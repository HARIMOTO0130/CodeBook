"""AI助手视图函数"""
import os
import time
import uuid
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from .models import AIInteractionRecord
# 使用官方推荐的导入方式
try:
    from volcenginesdkarkruntime import Ark
    SDK_AVAILABLE = True
except ImportError:
    # 如果导入失败，使用模拟实现但保持官方API结构
    print("豆包SDK未安装，使用模拟实现")
    class Ark:
        def __init__(self, **kwargs):
            self.api_key = kwargs.get('api_key', '')
            self.base_url = kwargs.get('base_url', '')
        
        @property
        def chat(self):
            return self.Chat()
    
    class Chat:
        def __init__(self):
            pass
        
        @property
        def completions(self):
            return self.Completions()
    
    class Completions:
        def create(self, model, messages, **kwargs):
            # 模拟回复
            class MockMessage:
                def __init__(self):
                    self.content = "这是模拟的AI回复。"
            
            class MockChoice:
                def __init__(self):
                    self.message = MockMessage()
            
            class MockResponse:
                def __init__(self):
                    self.choices = [MockChoice()]
            
            return MockResponse()
    
    SDK_AVAILABLE = False
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class AIAssistantView(views.APIView):
    """
    AI学习助手API视图
    使用豆包大模型提供智能问答功能
    支持用户认证和数据记录
    """
    # 允许匿名访问，但优先使用认证用户
    permission_classes = [AllowAny]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = self._init_ark_client()
    
    def _init_ark_client(self):
        """
        初始化豆包SDK客户端
        使用官方推荐的初始化方式
        """
        try:
            # 使用官方提供的API密钥
            api_key = "9511e57c-7838-415d-8225-fdf89678c631"
            
            # 创建客户端，包含官方推荐的base_url参数
            client = Ark(
                api_key=api_key,
                # 官方推荐的API调用基础URL
                base_url="https://ark.cn-beijing.volces.com/api/v3"
            )
            return client
        except Exception as e:
            print(f"初始化豆包客户端失败: {e}")
            return None
    
    def post(self, request):
        """
        处理AI助手请求
        接收用户问题，返回AI回复
        如果用户已认证，记录交互历史
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # 获取用户问题
        user_question = request.data.get('question', '')
        session_id = request.data.get('session_id', None)
        context = request.data.get('context', {})
        student_id = request.data.get('student_id', None)
        class_id = request.data.get('class_id', None)
        
        if not user_question.strip():
            return Response(
                {'error': '问题不能为空'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 如果没有session_id，生成一个新的
        if not session_id and request.user.is_authenticated:
            session_id = str(uuid.uuid4())
        
        start_time = time.time()
        
        try:
            # 增强数据集成：获取学生或班级相关数据作为上下文
            student_data = None
            class_data = None
            context_used = {
                'has_student_context': False,
                'has_class_context': False
            }
            
            # 验证权限并获取学生数据
            if student_id:
                if request.user.is_authenticated and request.user.role == 'teacher':
                    # 权限控制：确保教师只能访问自己负责的学生
                    try:
                        # 假设存在班级与教师的关联关系，以及学生与班级的关联关系
                        from apps.accounts.models import Class, Student
                        
                        # 检查学生是否属于教师负责的班级
                        student = Student.objects.filter(id=student_id).first()
                        if student:
                            teacher_classes = Class.objects.filter(teacher=request.user)
                            if student.class_id in [c.id for c in teacher_classes]:
                                # 获取学生相关数据
                                student_data = self._get_student_data(student_id)
                                context_used['has_student_context'] = True
                    except Exception as e:
                        logger.error(f"获取学生数据失败: {e}")
            
            # 验证权限并获取班级数据
            if class_id:
                if request.user.is_authenticated and request.user.role == 'teacher':
                    # 权限控制：确保教师只能访问自己负责的班级
                    try:
                        from apps.accounts.models import Class
                        
                        # 检查班级是否属于当前教师
                        if Class.objects.filter(id=class_id, teacher=request.user).exists():
                            # 获取班级相关数据
                            class_data = self._get_class_data(class_id)
                            context_used['has_class_context'] = True
                    except Exception as e:
                        logger.error(f"获取班级数据失败: {e}")
            
            # 生成AI回复，传递学生和班级数据作为上下文
            response_content = self.generate_response(user_question, student_data, class_data)
            response_time = time.time() - start_time
            
            # 如果用户已认证，记录交互历史
            if request.user.is_authenticated:
                try:
                    AIInteractionRecord.objects.create(
                        user=request.user,
                        interaction_type='question',
                        user_input=user_question,
                        ai_response=response_content,
                        session_id=session_id,
                        context={**context, 'student_id': student_id, 'class_id': class_id},
                        response_time=response_time,
                        tokens_used=0  # 可以根据实际API返回的token数更新
                    )
                except Exception as e:
                    logger.error(f"保存AI交互记录失败: {e}")
                    # 不影响主流程，继续返回结果
            
            # 返回AI回复
            return Response({
                'question': user_question,
                'answer': response_content,
                'session_id': session_id,
                'response_time': round(response_time, 2),
                'context_used': context_used
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"AI助手处理请求时出错: {e}", exc_info=True)
            return Response(
                {'error': f'处理请求时出错: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_student_data(self, student_id):
        """
        获取学生相关数据作为AI上下文
        """
        try:
            from apps.accounts.models import Student
            from .models import LearningRecord, PracticeRecord, KnowledgeMastery
            
            # 获取学生基本信息
            student = Student.objects.filter(id=student_id).first()
            if not student:
                return None
            
            student_data = {
                'name': student.student_name,
                'student_no': student.student_no,
                'class_id': student.class_id
            }
            
            # 获取学习记录
            learning_records = LearningRecord.objects.filter(user_id=student_id).select_related('book', 'chapter')
            student_data['learning_progress'] = []
            for record in learning_records:
                student_data['learning_progress'].append({
                    'book': record.book.title,
                    'chapter': record.chapter.title,
                    'progress': record.progress,
                    'last_learn_time': record.last_learn_time.isoformat()
                })
            
            # 获取练习记录
            practice_records = PracticeRecord.objects.filter(user_id=student_id).select_related('book', 'chapter')
            student_data['practice_records'] = []
            for record in practice_records:
                student_data['practice_records'].append({
                    'book': record.book.title,
                    'chapter': record.chapter.title,
                    'score': record.score,
                    'completed': record.completed,
                    'completed_time': record.completed_time.isoformat()
                })
            
            # 获取知识掌握度
            knowledge_mastery = KnowledgeMastery.objects.filter(user_id=student_id)
            student_data['knowledge_mastery'] = []
            for mastery in knowledge_mastery:
                student_data['knowledge_mastery'].append({
                    'knowledge_point': mastery.knowledge_point,
                    'mastery_level': mastery.mastery_level,
                    'assessed_at': mastery.assessed_at.isoformat()
                })
            
            return student_data
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取学生数据失败: {e}")
            return None
    
    def _get_class_data(self, class_id):
        """
        获取班级相关数据作为AI上下文
        """
        try:
            from apps.accounts.models import Class, Student
            from .models import LearningRecord, PracticeRecord
            
            # 获取班级基本信息
            class_obj = Class.objects.filter(id=class_id).first()
            if not class_obj:
                return None
            
            class_data = {
                'name': class_obj.name,
                'student_count': class_obj.student_set.count()
            }
            
            # 获取班级学生列表
            students = Student.objects.filter(class_id=class_id)
            class_data['students'] = [{
                'id': student.id,
                'name': student.student_name,
                'student_no': student.student_no
            } for student in students]
            
            # 获取班级整体学习情况
            class_learning_records = LearningRecord.objects.filter(user_id__in=[s.id for s in students]).select_related('book', 'chapter')
            
            # 计算班级平均进度
            if class_learning_records:
                total_progress = sum(record.progress for record in class_learning_records)
                class_data['average_progress'] = round(total_progress / len(class_learning_records), 2)
            else:
                class_data['average_progress'] = 0
            
            return class_data
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取班级数据失败: {e}")
            return None

    def generate_response(self, question, student_data=None, class_data=None):
        """
        使用豆包大模型生成回复，确保内容简洁清晰，无无关格式和符号，并在生成时就控制字数
        增强数据集成：根据学生或班级数据生成个性化回复
        """
        # 如果客户端初始化失败，返回备用回复
        if not self.client:
            return "很抱歉，AI助手服务暂时不可用，请稍后再试。"
        
        try:
            # 构建系统提示，强调在生成时就控制字数，确保内容完整且符合字数限制
            system_prompt = ("你是一个专业的编程学习助手，专门帮助用户解答编程相关问题。"  
                           "请用简洁明了的纯文本回答，避免使用任何特殊格式符号。"  
                           "如果需要代码示例，请直接提供代码内容，不要使用代码块标记。"  
                           "如果问题与编程无关，请礼貌地拒绝回答。"
                           "请在生成回复时就确保内容不超过300字，而不是生成过长内容后被截断。"  
                           "确保你的回答是完整的，包含所有必要信息，并且结尾自然。")
            
            # 构建用户提示，包含学生或班级数据作为上下文
            user_prompt = question
            
            # 添加学生数据上下文
            if student_data:
                user_prompt += f"\n\n以下是该学生的相关数据，供你参考：\n"
                user_prompt += f"学生姓名：{student_data['name']}\n"
                user_prompt += f"学号：{student_data['student_no']}\n"
                
                if student_data['learning_progress']:
                    user_prompt += "学习进度：\n"
                    for progress in student_data['learning_progress'][:3]:  # 只显示前3条
                        user_prompt += f"- {progress['book']} - {progress['chapter']}：{progress['progress']}%\n"
                
                if student_data['practice_records']:
                    user_prompt += "练习记录：\n"
                    for practice in student_data['practice_records'][:3]:  # 只显示前3条
                        user_prompt += f"- {practice['book']} - {practice['chapter']}：得分 {practice['score']}\n"
                
                if student_data['knowledge_mastery']:
                    user_prompt += "知识掌握度：\n"
                    for mastery in student_data['knowledge_mastery'][:3]:  # 只显示前3条
                        user_prompt += f"- {mastery['knowledge_point']}：{mastery['mastery_level']:.2f}\n"
            
            # 添加班级数据上下文
            if class_data:
                user_prompt += f"\n\n以下是该班级的相关数据，供你参考：\n"
                user_prompt += f"班级名称：{class_data['name']}\n"
                user_prompt += f"学生人数：{class_data['student_count']}\n"
                user_prompt += f"平均学习进度：{class_data['average_progress']}%\n"
            
            # 调用豆包API - 使用官方推荐的属性调用方式
            completion = self.client.chat.completions.create(
                # 使用官方推荐的模型ID
                model="doubao-seed-1-6-251015",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                # 降低max_tokens限制，间接帮助控制回复长度
                max_tokens=450
            )
            
            # 获取回复内容
            if completion and completion.choices:
                response_content = completion.choices[0].message.content
                # 清理可能的格式符号和杂乱内容
                # 移除常见的格式符号和标记
                response_content = response_content.replace('```', '').replace('\n\n', '\n')

                return response_content
            return "很抱歉，无法生成回复。"
        except Exception as e:
            print(f"生成AI回复时出错: {e}")
            return "很抱歉，AI助手服务暂时不可用，请稍后再试。"


class CodeCompletionView(views.APIView):
    """
    代码补全API视图
    接收代码内容、语言类型和上下文信息，返回智能代码补全建议
    """
    permission_classes = [AllowAny]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = self._init_ark_client()
    
    def _init_ark_client(self):
        """
        初始化豆包SDK客户端
        """
        try:
            # 使用与AI助手相同的API密钥
            api_key = "9511e57c-7838-415d-8225-fdf89678c631"
            
            # 创建客户端
            client = Ark(
                api_key=api_key,
                base_url="https://ark.cn-beijing.volces.com/api/v3"
            )
            return client
        except Exception as e:
            print(f"初始化豆包客户端失败: {e}")
            return None
    
    def post(self, request):
        """
        处理代码补全请求
        接收代码内容、语言类型、光标位置和上下文信息
        """
        try:
            # 获取请求参数
            code = request.data.get('code', '')
            language = request.data.get('language', '')
            cursor_line = request.data.get('cursor_line', 0)
            cursor_column = request.data.get('cursor_column', 0)
            context = request.data.get('context', '')
            
            # 验证必填参数
            if not code or not language:
                return Response(
                    {'error': '代码内容和语言类型不能为空'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # 生成代码补全建议
            completions = self.generate_code_completions(
                code=code,
                language=language,
                cursor_line=cursor_line,
                cursor_column=cursor_column,
                context=context
            )
            
            return Response({
                'completions': completions
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"处理代码补全请求时出错: {e}")
            # 返回基础补全建议作为回退
            fallback_completions = self._get_fallback_completions(language)
            return Response({
                'error': f'处理请求时出错: {str(e)}',
                'completions': fallback_completions
            }, status=status.HTTP_200_OK)
    
    def generate_code_completions(self, code, language, cursor_line, cursor_column, context):
        """
        使用豆包大模型生成代码补全建议
        """
        # 如果客户端初始化失败，返回备用补全
        if not self.client:
            return self._get_fallback_completions(language)
        
        try:
            # 构建系统提示，专注于代码补全任务
            system_prompt = ("你是一个专业的代码补全助手。请根据用户提供的代码上下文，" 
                           "在光标位置生成合适的代码补全建议。只返回纯代码补全内容，" 
                           "不要包含任何解释或格式标记。请生成2-5个可能的补全选项，" 
                           "每个选项使用|分隔。每个补全选项应简洁实用，并符合当前编程语言的语法规范。")
            
            # 构建用户提示
            user_prompt = f"""
编程语言: {language}
代码内容:
{code}
光标位置: 第{cursor_line}行，第{cursor_column}列
上下文信息:
{context}

请生成代码补全建议，用|分隔多个选项。
"""
            
            # 调用豆包API
            completion = self.client.chat.completions.create(
                model="doubao-seed-1-6-251015",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=200
            )
            
            # 解析回复
            if completion and completion.choices:
                response_content = completion.choices[0].message.content.strip()
                # 将回复分割为多个补全选项
                completion_options = [opt.strip() for opt in response_content.split('|')]
                # 转换为Monaco编辑器需要的格式
                return [
                    {
                        'label': option,
                        'insertText': option,
                        'kind': 3,  # Function
                        'detail': f'{language} 代码补全'
                    }
                    for option in completion_options[:5]  # 最多返回5个选项
                ]
            
            # 如果没有生成有效的补全，返回备用补全
            return self._get_fallback_completions(language)
            
        except Exception as e:
            print(f"生成代码补全时出错: {e}")
            return self._get_fallback_completions(language)
    
    def _get_fallback_completions(self, language):
        """
        获取语言特定的基础补全建议
        """
        # 为不同语言提供基础补全选项
        fallback_completions = {
            'python': [
                {'label': 'print()', 'insertText': 'print()', 'kind': 3, 'detail': '输出函数'},
                {'label': 'for item in items:', 'insertText': 'for item in items:', 'kind': 3, 'detail': 'for循环'},
                {'label': 'def function():', 'insertText': 'def function():', 'kind': 3, 'detail': '函数定义'},
                {'label': 'import ', 'insertText': 'import ', 'kind': 3, 'detail': '导入模块'},
                {'label': 'if condition:', 'insertText': 'if condition:', 'kind': 3, 'detail': '条件语句'}
            ],
            'javascript': [
                {'label': 'console.log()', 'insertText': 'console.log()', 'kind': 3, 'detail': '输出函数'},
                {'label': 'function name() {', 'insertText': 'function name() {', 'kind': 3, 'detail': '函数定义'},
                {'label': 'for (let i = 0; i < length; i++) {', 'insertText': 'for (let i = 0; i < length; i++) {', 'kind': 3, 'detail': 'for循环'},
                {'label': 'const variable = ', 'insertText': 'const variable = ', 'kind': 3, 'detail': '常量声明'},
                {'label': 'if (condition) {', 'insertText': 'if (condition) {', 'kind': 3, 'detail': '条件语句'}
            ],
            'java': [
                {'label': 'System.out.println();', 'insertText': 'System.out.println();', 'kind': 3, 'detail': '输出语句'},
                {'label': 'public static void main(String[] args) {', 'insertText': 'public static void main(String[] args) {', 'kind': 3, 'detail': '主方法'},
                {'label': 'for (int i = 0; i < length; i++) {', 'insertText': 'for (int i = 0; i < length; i++) {', 'kind': 3, 'detail': 'for循环'},
                {'label': 'public class Name {', 'insertText': 'public class Name {', 'kind': 3, 'detail': '类定义'},
                {'label': 'if (condition) {', 'insertText': 'if (condition) {', 'kind': 3, 'detail': '条件语句'}
            ]
        }
        
        # 返回对应语言的基础补全，默认为空列表
        return fallback_completions.get(language.lower(), [])
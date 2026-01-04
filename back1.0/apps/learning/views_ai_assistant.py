"""AI助手视图函数"""
import os
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
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
    """
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
        """
        # 获取用户问题
        user_question = request.data.get('question', '')
        
        if not user_question.strip():
            return Response(
                {'error': '问题不能为空'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # 生成AI回复
            response_content = self.generate_response(user_question)
            
            # 返回AI回复
            return Response({
                'question': user_question,
                'answer': response_content
            }, status=status.HTTP_200_OK)
        except Exception as e:
            print(f"AI助手处理请求时出错: {e}")
            return Response(
                {'error': f'处理请求时出错: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def generate_response(self, question):
        """
        使用豆包大模型生成回复，确保内容简洁清晰，无无关格式和符号，并在生成时就控制字数
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
            
            # 调用豆包API - 使用官方推荐的属性调用方式
            completion = self.client.chat.completions.create(
                # 使用官方推荐的模型ID
                model="doubao-seed-1-6-251015",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
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
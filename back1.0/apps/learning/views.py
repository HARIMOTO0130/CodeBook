"""学习记录视图函数"""
from rest_framework import viewsets, status, decorators, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.db import models

# 为了兼容性，定义action装饰器
action = decorators.action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction
from datetime import date, datetime
import tempfile
import subprocess
import os
import time
import json
import sys
from bs4 import BeautifulSoup
from django.utils import timezone
from apps.books.models import Book, Chapter
from .models import LearningRecord, PracticeRecord, HeatmapData, WrongQuestion, RoadmapTemplate, RoadmapStage, UserLearningPath, UserPathStage, Note, NoteTag, Exercise, JupyterDocument, LearningStyle, KnowledgeMastery, LearningRecommendation, LearningPreference
from .serializers import (
    LearningRecordSerializer, 
    LearningActivitySerializer,
    SaveProgressSerializer,
    PracticeRecordSerializer,
    SubmitPracticeSerializer,
    HeatmapDataSerializer,
    WrongQuestionSerializer,
    RoadmapTemplateSerializer,
    UserLearningPathSerializer,
    CreateUserPathSerializer,
    UpdatePathProgressSerializer,
    NoteSerializer,
    NoteListSerializer,
    NoteCreateSerializer,
    NoteUpdateSerializer,
    NoteDetailSerializer,
    NoteVersionSerializer,
    NoteTagSerializer,
    JupyterDocumentSerializer,
    CreateJupyterDocumentSerializer,
    UpdateJupyterDocumentSerializer,
    LearningStyleSerializer, 
    UpdateLearningStyleSerializer, 
    KnowledgeMasterySerializer,
    UpdateKnowledgeMasterySerializer, 
    LearningRecommendationSerializer,
    FeedbackRecommendationSerializer, 
    LearningPreferenceSerializer,
    UpdateLearningPreferenceSerializer
)
from .recommendation_engine import RecommendationEngine
from datetime import datetime as dt_datetime
from django.utils.dateparse import parse_date


class LearningRecordViewSet(viewsets.ModelViewSet):
    """学习记录视图集"""
    queryset = LearningRecord.objects.all()
    serializer_class = LearningRecordSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        # 用户只能查看自己的学习记录
        return LearningRecord.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def save_progress(self, request):
        """保存学习进度"""
        serializer = SaveProgressSerializer(data=request.data)
        if serializer.is_valid():
            book_id = serializer.validated_data['book_id']
            chapter_id = serializer.validated_data['chapter_id']
            progress = serializer.validated_data['progress']
            
            try:
                with transaction.atomic():
                    # 获取书籍和章节
                    book = Book.objects.get(id=book_id)
                    chapter = Chapter.objects.get(id=chapter_id, book=book)
                    
                    # 更新或创建学习记录
                    record, created = LearningRecord.objects.update_or_create(
                        user=request.user,
                        book=book,
                        chapter=chapter,
                        defaults={'progress': progress}
                    )
                    
                    # 更新学习热力图数据
                    today = date.today()
                    heatmap_data, created = HeatmapData.objects.get_or_create(
                        user=request.user,
                        date=today,
                        defaults={'minutes': 0}
                    )
                    heatmap_data.minutes += 1  # 每次保存进度增加1分钟学习时间
                    heatmap_data.save()
                    
                    return Response({'success': True, 'record_id': record.id})
            except (Book.DoesNotExist, Chapter.DoesNotExist) as e:
                return Response({'error': '书籍或章节不存在'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def heatmap(self, request):
        """获取学习热力图数据"""
        try:
            # 获取最近365天的学习数据
            import datetime
            one_year_ago = date.today() - datetime.timedelta(days=365)
            heatmap_data = HeatmapData.objects.filter(
                user=request.user,
                date__gte=one_year_ago
            ).order_by('date')
            
            serializer = HeatmapDataSerializer(heatmap_data, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='activity')
    def activity(self, request):
        """
        获取用户学习活动（阅读/练习）列表，支持过滤、排序、分页
        查询参数：
          - start_date / end_date: 日期范围（YYYY-MM-DD）
          - type: reading / practice / all
          - status: completed / inProgress / all
          - order_by: timestamp / -timestamp / score / -score / progress / -progress
          - page, page_size
        """
        user = request.user

        # 解析查询参数
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        filter_type = request.query_params.get('type', 'all')
        filter_status = request.query_params.get('status', 'all')
        order_by = request.query_params.get('order_by', '-timestamp')
        page_size = request.query_params.get('page_size') or request.query_params.get('pageSize') or 10
        page_number = request.query_params.get('page') or 1

        # 允许的排序字段，避免注入
        allowed_order = {'timestamp', '-timestamp', 'score', '-score', 'progress', '-progress'}
        if order_by not in allowed_order:
            order_by = '-timestamp'

        # 拉取学习记录（阅读类）
        learning_qs = LearningRecord.objects.filter(user=user).select_related('book', 'chapter')
        learning_items = []
        for lr in learning_qs:
            chapter_type = getattr(lr.chapter, 'type', 'reading') or 'reading'
            item = {
                'id': f'lr-{lr.id}',
                'type': 'reading' if chapter_type == 'reading' else chapter_type or 'reading',
                'bookId': lr.book.id,
                'chapterId': lr.chapter.id,
                'bookTitle': lr.book.title,
                'chapterTitle': lr.chapter.title,
                'duration': None,  # 当前模型无时长字段，保持真实数据而非模拟
                'status': 'completed' if lr.progress >= 100 else 'inProgress',
                'timestamp': lr.last_learn_time or lr.created_at if hasattr(lr, 'created_at') else lr.last_learn_time,
                'progress': lr.progress,
                'score': None,
            }
            learning_items.append(item)

        # 拉取练习记录
        practice_qs = PracticeRecord.objects.filter(user=user).select_related('book', 'chapter')
        practice_items = []
        for pr in practice_qs:
            item = {
                'id': f'pr-{pr.id}',
                'type': 'practice',
                'bookId': pr.book.id,
                'chapterId': pr.chapter.id,
                'bookTitle': pr.book.title,
                'chapterTitle': pr.chapter.title,
                'duration': None,  # 练习记录当前无时长字段
                'status': 'completed' if pr.completed else 'inProgress',
                'timestamp': pr.completed_time or pr.created_at if hasattr(pr, 'created_at') else pr.completed_time,
                'progress': None,
                'score': pr.score,
            }
            practice_items.append(item)

        # 合并
        activities = learning_items + practice_items

        # 过滤类型
        if filter_type in ['reading', 'practice']:
            activities = [a for a in activities if a['type'] == filter_type]

        # 过滤状态
        if filter_status in ['completed', 'inProgress']:
            activities = [a for a in activities if a['status'] == filter_status]

        # 过滤日期
        def in_range(ts):
            if not ts:
                return False
            ts_date = ts.date()
            if start_date:
                try:
                    sd = parse_date(start_date)
                    if ts_date < sd:
                        return False
                except Exception:
                    pass
            if end_date:
                try:
                    ed = parse_date(end_date)
                    if ts_date > ed:
                        return False
                except Exception:
                    pass
            return True

        activities = [a for a in activities if in_range(a['timestamp'])]

        # 排序
        reverse = order_by.startswith('-')
        key = order_by.lstrip('-')
        activities.sort(key=lambda x: x.get(key) or dt_datetime.min, reverse=reverse)

        # 分页
        paginator = PageNumberPagination()
        paginator.page_size = int(page_size)
        paginated = paginator.paginate_queryset(activities, request)

        serializer = LearningActivitySerializer(paginated, many=True)
        return paginator.get_paginated_response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny], authentication_classes=[])
    def execute(self, request):
        """在线执行代码（简易沙箱：临时目录 + 超时限制）"""
        language = (request.data.get('language') or '').lower()
        code = request.data.get('code') or ''
        stdin_data = request.data.get('input') or ''

        if language not in ['python', 'javascript', 'java', 'c', 'html']:
            return Response({'error': '暂不支持该语言'}, status=status.HTTP_400_BAD_REQUEST)
        if not code:
            return Response({'error': '代码为空'}, status=status.HTTP_400_BAD_REQUEST)

        start = time.time()
        max_time = 5
        stdout_text = ''
        stderr_text = ''
        exit_code = None

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                cwd = tmpdir
                if language == 'python':
                    filename = os.path.join(cwd, 'main.py')
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(code)
                    cmd = ['python', filename]
                elif language == 'javascript':
                    filename = os.path.join(cwd, 'main.js')
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(code)
                    cmd = ['node', filename]
                elif language == 'java':
                    # Java代码执行：先编译再运行
                    filename = os.path.join(cwd, 'Main.java')
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(code)
                    # 编译Java文件
                    compile_cmd = ['javac', 'Main.java']
                    compile_proc = subprocess.run(
                        compile_cmd,
                        cwd=cwd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=max_time // 2  # 编译超时限制
                    )
                    
                    # 检查编译是否成功
                    if compile_proc.returncode != 0:
                        stderr_text = compile_proc.stderr.decode('utf-8', errors='replace')
                        exit_code = compile_proc.returncode
                    
                    # 运行编译后的Java程序
                    cmd = ['java', 'Main']
                elif language == 'c':
                    # C代码执行：先编译再运行
                    filename = os.path.join(cwd, 'main.c')
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(code)
                    # 编译C文件
                    compile_cmd = ['gcc', 'main.c', '-o', 'main.exe']
                    compile_proc = subprocess.run(
                        compile_cmd,
                        cwd=cwd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=max_time // 2  # 编译超时限制
                    )
                    
                    # 检查编译是否成功
                    if compile_proc.returncode != 0:
                        stderr_text = compile_proc.stderr.decode('utf-8', errors='replace')
                        exit_code = compile_proc.returncode
                    
                    # 运行编译后的C程序
                    cmd = ['./main.exe']
                elif language == 'html':
                    # HTML不能直接执行，返回解析后的信息
                    filename = os.path.join(cwd, 'index.html')
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(code)
                    # 返回HTML解析信息而非执行结果
                    stdout_text = "HTML文件已生成，在实际环境中可以通过浏览器打开查看"
                    # 简单解析HTML内容统计
                    from bs4 import BeautifulSoup
                    try:
                        soup = BeautifulSoup(code, 'html.parser')
                        stdout_text += f"\n\nHTML解析信息："
                        stdout_text += f"\n- 标题: {soup.title.string if soup.title else '无标题'}"
                        stdout_text += f"\n- 段落数量: {len(soup.find_all('p'))}"
                        stdout_text += f"\n- 链接数量: {len(soup.find_all('a'))}"
                        stdout_text += f"\n- 图片数量: {len(soup.find_all('img'))}"
                    except Exception as e:
                        stdout_text += f"\n\nHTML解析错误: {str(e)}"
                    exit_code = 0
                cmd = None  # HTML不需要执行命令

                proc = subprocess.run(
                    cmd,
                    input=stdin_data.encode('utf-8'),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=cwd,
                    timeout=max_time
                )
                stdout_text = proc.stdout.decode('utf-8', errors='replace')
                stderr_text = proc.stderr.decode('utf-8', errors='replace')
                exit_code = proc.returncode

        except subprocess.TimeoutExpired:
            stderr_text = f'执行超时（>{max_time}s）'
            exit_code = -1
        except FileNotFoundError as e:
            stderr_text = '执行环境缺失，请安装所需运行时（如 Python 或 Node.js）'
            exit_code = -1
        except Exception as e:
            stderr_text = str(e)
            exit_code = -1

        duration_ms = int((time.time() - start) * 1000)
        # 限制输出长度，防止过大响应
        max_len = 10000
        if len(stdout_text) > max_len:
            stdout_text = stdout_text[:max_len] + '\n...[输出过长已截断]'
        if len(stderr_text) > max_len:
            stderr_text = stderr_text[:max_len] + '\n...[输出过长已截断]'

        return Response({
            'stdout': stdout_text,
            'stderr': stderr_text,
            'exitCode': exit_code,
            'durationMs': duration_ms
        })


@decorators.api_view(['POST'])
@decorators.authentication_classes([])
@decorators.permission_classes([AllowAny])
def execute_code(request):
    """在线执行代码（安全沙箱：资源限制 + 隔离环境 + 超时控制） - 无需认证"""
    language = (request.data.get('language') or '').lower()
    code = request.data.get('code') or ''
    stdin_data = request.data.get('input') or ''

    # 支持的编程语言
    supported_languages = ['python', 'javascript', 'java', 'c', 'html']
    
    # 安全检查
    if language not in supported_languages:
        return Response({'error': f'暂不支持该语言，支持的语言: {', '.join(supported_languages)}'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    if not code:
        return Response({'error': '代码为空'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 代码长度限制
    if len(code) > 10000:
        return Response({'error': '代码长度超过限制（最大10000字符）'}, status=status.HTTP_400_BAD_REQUEST)

    start = time.time()
    max_time = 5  # 5秒超时限制
    max_memory_mb = 256  # 内存限制（MB）
    stdout_text = ''
    stderr_text = ''
    exit_code = None
    
    # 安全执行参数
    subprocess_kwargs = {
        'input': stdin_data.encode('utf-8'),
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE,
        'timeout': max_time,
        'env': {
            # 清理环境变量，只保留必要的
            'PATH': os.environ.get('PATH', ''),
            'HOME': '',  # 防止访问用户主目录
        }
    }

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            cwd = tmpdir
            
            # 根据语言准备执行环境和命令
            if language == 'python':
                # 安全的Python执行，禁用危险模块导入
                secure_code = f"""
# 安全执行包装
import sys
import builtins

# 禁用危险模块和函数
blocked_modules = ['os', 'sys', 'subprocess', 'socket', 'shutil', '__import__', 
                  'exec', 'eval', 'open', 'file', 'compile', 'globals', 'locals']

# 覆盖__builtins__中的危险函数
for func in ['open', 'file', 'execfile', '__import__', 'eval', 'exec']:
    if func in builtins.__dict__:
        builtins.__dict__[func] = lambda *args, **kwargs: None

# 限制内存使用
import resource
resource.setrlimit(resource.RLIMIT_AS, (int({max_memory_mb} * 1024 * 1024), -1))

# 执行用户代码
{code}
"""
                filename = os.path.join(cwd, 'main.py')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(secure_code.format(max_memory_mb=max_memory_mb, code=code))
                cmd = ['python', '-B', '-E', filename]  # -B: 不写入.pyc文件, -E: 忽略环境变量
                
            elif language == 'javascript':
                filename = os.path.join(cwd, 'main.js')
                with open(filename, 'w', encoding='utf-8') as f:
                    # 避免使用f-string嵌套，直接拼接字符串
                    wrapper_start = '''
// 内存使用监控
const originalSetTimeout = setTimeout;
setTimeout = (callback, delay) => {
  const startMem = process.memoryUsage().heapUsed;
  const wrappedCallback = () => {
    const currentMem = process.memoryUsage().heapUsed;
    if (currentMem > '''
                    wrapper_middle = str(max_memory_mb) + ''' * 1024 * 1024) {
      console.error('内存使用超出限制');
      process.exit(1);
    }
    callback();
  };
  return originalSetTimeout(wrappedCallback, delay);
};

// 执行用户代码
'''
                    f.write(wrapper_start + wrapper_middle + code)
                cmd = ['node', '--max-old-space-size={}'.format(max_memory_mb), filename]
            elif language == 'java':
                # Java代码执行：先编译再运行
                filename = os.path.join(cwd, 'Main.java')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                # 编译Java文件
                compile_cmd = ['javac', 'Main.java']
                compile_proc = subprocess.run(
                    compile_cmd,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=max_time // 2  # 编译超时限制
                )
                
                # 检查编译是否成功
                if compile_proc.returncode != 0:
                    stderr_text = compile_proc.stderr.decode('utf-8', errors='replace')
                    exit_code = compile_proc.returncode
                    # 编译失败，不执行运行命令
                    cmd = None
                else:
                    # 运行编译后的Java程序
                    cmd = ['java', '-Xmx{}m'.format(max_memory_mb), 'Main']
            elif language == 'c':
                # C代码执行：先编译再运行
                filename = os.path.join(cwd, 'main.c')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                # 编译C文件
                compile_cmd = ['gcc', 'main.c', '-o', 'main.exe']
                compile_proc = subprocess.run(
                    compile_cmd,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=max_time // 2  # 编译超时限制
                )
                
                # 检查编译是否成功
                if compile_proc.returncode != 0:
                    stderr_text = compile_proc.stderr.decode('utf-8', errors='replace')
                    exit_code = compile_proc.returncode
                    # 编译失败，不执行运行命令
                    cmd = None
                else:
                    # 运行编译后的C程序
                    cmd = ['./main.exe']
            elif language == 'html':
                # HTML不能直接执行，返回解析后的信息
                filename = os.path.join(cwd, 'index.html')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                # 返回HTML解析信息而非执行结果
                stdout_text = "HTML文件已生成，在实际环境中可以通过浏览器打开查看"
                # 简单解析HTML内容统计
                try:
                    soup = BeautifulSoup(code, 'html.parser')
                    stdout_text += f"\n\nHTML解析信息："
                    stdout_text += f"\n- 标题: {soup.title.string if soup.title else '无标题'}"
                    stdout_text += f"\n- 段落数量: {len(soup.find_all('p'))}"
                    stdout_text += f"\n- 图片数量: {len(soup.find_all('img'))}"
                    stdout_text += f"\n- 链接数量: {len(soup.find_all('a'))}"
                    stdout_text += f"\n- 标题标签数量: {len(soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))}"
                except Exception as e:
                    stdout_text += f"\n解析HTML时出错: {str(e)}"
                exit_code = 0
                # HTML不需要执行命令
                cmd = None

            # 设置额外的安全参数
            if sys.platform.startswith('linux'):
                # Linux系统下使用更严格的隔离
                subprocess_kwargs.update({
                    'preexec_fn': lambda: resource.setrlimit(resource.RLIMIT_NPROC, (32, 32))  # 限制进程数
                })

            # 执行代码（仅在非HTML且cmd存在时执行）
            if language != 'html' and cmd is not None:
                proc = subprocess.run(cmd, cwd=cwd, **subprocess_kwargs)
                stdout_text = proc.stdout.decode('utf-8', errors='replace')
                stderr_text = proc.stderr.decode('utf-8', errors='replace')
                exit_code = proc.returncode

    except subprocess.TimeoutExpired:
        stderr_text = f'执行超时（>{max_time}s），代码可能存在死循环或执行时间过长'
        exit_code = -1
    except FileNotFoundError as e:
        stderr_text = '执行环境缺失，请安装所需运行时（如 Python 或 Node.js）'
        exit_code = -1
    except Exception as e:
        stderr_text = f'执行错误: {str(e)}'
        exit_code = -1

    duration_ms = int((time.time() - start) * 1000)
    
    # 限制输出长度，防止过大响应
    max_len = 10000
    if len(stdout_text) > max_len:
        stdout_text = stdout_text[:max_len] + '\n...[输出过长已截断]'
    if len(stderr_text) > max_len:
        stderr_text = stderr_text[:max_len] + '\n...[输出过长已截断]'
    
    # 添加执行统计信息
    stats = {
        'language': language,
        'codeLength': len(code),
        'executionTime': duration_ms,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    # 根据测试脚本期望的格式返回响应
    success = exit_code == 0 and not stderr_text
    output = stdout_text if stdout_text else stderr_text
    error = stderr_text if stderr_text and exit_code != 0 else None
    
    return Response({
        'success': success,
        'output': output,
        'error': error,
        # 保留原有字段以保持向后兼容
        'stdout': stdout_text,
        'stderr': stderr_text,
        'exitCode': exit_code,
        'durationMs': duration_ms,
        'stats': stats
    })


class PracticeRecordViewSet(viewsets.ModelViewSet):
    """练习记录视图集"""
    queryset = PracticeRecord.objects.all()
    serializer_class = PracticeRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 用户只能查看自己的练习记录
        return PracticeRecord.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def submit(self, request):
        """提交练习结果"""
        serializer = SubmitPracticeSerializer(data=request.data)
        if serializer.is_valid():
            book_id = serializer.validated_data['book_id']
            chapter_id = serializer.validated_data['chapter_id']
            score = serializer.validated_data['score']
            user_code = serializer.validated_data.get('user_code', '')
            
            try:
                with transaction.atomic():
                    # 获取书籍和章节
                    book = Book.objects.get(id=book_id)
                    chapter = Chapter.objects.get(id=chapter_id, book=book)
                    
                    # 检查是否为练习章节
                    if chapter.type != 'practice':
                        return Response({'error': '该章节不是练习章节'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # 创建练习记录
                    record = PracticeRecord.objects.create(
                        user=request.user,
                        book=book,
                        chapter=chapter,
                        score=score,
                        completed=score >= 60,  # 得分>=60视为完成
                        user_code=user_code
                    )
                    
                    # 错题本维护：低于及格分数则加入/更新；达标则移除
                    try:
                        from apps.books.models import Practice
                        title = getattr(getattr(chapter, 'practice', None), 'question', '') or f"{chapter.title} - 练习题"
                    except Exception:
                        title = f"{chapter.title} - 练习题"

                    if record.completed:
                        WrongQuestion.objects.filter(user=request.user, book=book, chapter=chapter).delete()
                    else:
                        WrongQuestion.objects.update_or_create(
                            user=request.user,
                            book=book,
                            chapter=chapter,
                            defaults={'title': title}
                        )

                    # 如果练习完成，自动更新学习进度
                    if record.completed:
                        learning_record, created = LearningRecord.objects.update_or_create(
                            user=request.user,
                            book=book,
                            chapter=chapter,
                            defaults={'progress': 100}
                        )
                    
                    return Response({'success': True, 'record_id': record.id})
            except (Book.DoesNotExist, Chapter.DoesNotExist) as e:
                return Response({'error': '书籍或章节不存在'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WrongQuestionViewSet(viewsets.ModelViewSet):
    """错题本视图集"""
    queryset = WrongQuestion.objects.all()
    serializer_class = WrongQuestionSerializer
    permission_classes = [IsAuthenticated]
    
    def list(self, request, *args, **kwargs):
        # 获取用户的所有错题
        wrong_questions = WrongQuestion.objects.filter(user=request.user).order_by('-attempt_time')
        
        # 构建响应数据
        data = []
        for wq in wrong_questions:
            data.append({
                'id': wq.id,
                'title': wq.title,
                'difficulty': wq.difficulty,
                'question_type': wq.question_type,
                'attempt_time': wq.attempt_time.isoformat() if wq.attempt_time else wq.created_at.isoformat(),
                'practice_id': wq.practice.id if wq.practice else None
            })
        
        return Response(data)

    def get_queryset(self):
        return WrongQuestion.objects.filter(user=self.request.user).select_related('book', 'chapter')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def batch(self, request):
        """批量添加错题"""
        try:
            questions = json.loads(request.data.get('questions', '[]'))
            created_count = 0
            updated_count = 0
            
            for q in questions:
                # 尝试获取对应的练习题
                exercise_id = q.get('exerciseId')
                exercise = None
                if exercise_id:
                    try:
                        exercise = Exercise.objects.get(id=exercise_id)
                    except Exercise.DoesNotExist:
                        exercise = None
                
                # 获取题目相关信息
                title = q.get('title', f'练习题 {exercise_id}')
                difficulty = q.get('difficulty', 2)
                question_type = q.get('type', 'unknown')
                
                # 创建或更新错题记录
                wrong_question, created = WrongQuestion.objects.update_or_create(
                    user=request.user,
                    practice=exercise,  # 使用practice作为唯一标识
                    defaults={
                        'title': title,
                        'difficulty': difficulty,
                        'question_type': question_type,
                        'attempt_time': timezone.now()
                    }
                )
                
                # 如果没有practice，使用title作为备选唯一标识
                if not exercise and not created:
                    # 检查是否存在相同标题的错题
                    existing = WrongQuestion.objects.filter(
                        user=request.user,
                        title=title
                    ).first()
                    if not existing:
                        wrong_question, created = WrongQuestion.objects.create(
                            user=request.user,
                            title=title,
                            difficulty=difficulty,
                            question_type=question_type,
                            practice=exercise,
                            attempt_time=timezone.now()
                        )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            return Response({
                "success": True, 
                "created": created_count, 
                "updated": updated_count,
                "total": created_count + updated_count
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def status(self, request, pk=None):
        """更新错题状态"""
        try:
            wrong_question = self.get_object()
            status_value = request.data.get('status')
            
            if status_value == 'mastered':
                # 标记为已掌握，删除错题记录
                wrong_question.delete()
                return Response({"success": True, "message": "错题已标记为掌握"})
            elif status_value == 'reviewed':
                # 标记为已复习，更新最后尝试时间
                wrong_question.attempt_time = timezone.now()
                wrong_question.save()
                return Response({"success": True, "message": "错题状态已更新"})
            
            return Response({"error": "无效的状态值"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RoadmapTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """路线图模板视图集"""
    queryset = RoadmapTemplate.objects.filter(is_active=True).prefetch_related('stages__roadmap_books__book')
    serializer_class = RoadmapTemplateSerializer
    permission_classes = []  # 暂时允许匿名访问以测试功能
    
    def get_queryset(self):
        queryset = super().get_queryset()
        # 根据专业过滤
        major = self.request.query_params.get('major', None)
        if major:
            queryset = queryset.filter(major=major)
        # 根据难度过滤
        difficulty = self.request.query_params.get('difficulty', None)
        if difficulty:
            queryset = queryset.filter(difficulty_level=difficulty)
        return queryset
    
    @action(detail=True, methods=['get'])
    def recommended_for_user(self, request, pk=None):
        """获取推荐给用户的路线图"""
        # 这里可以根据用户的学习记录和偏好进行智能推荐
        # 暂时返回所有活跃的路线图
        roadmaps = RoadmapTemplate.objects.filter(is_active=True)[:3]
        serializer = self.get_serializer(roadmaps, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def activity(self, request):
        """
        获取当前用户的学习活动记录（阅读/练习），支持过滤、排序、分页。
        Query params:
        - start_date, end_date: YYYY-MM-DD
        - type: all|reading|practice
        - status: all|completed|inProgress
        - order_by: timestamp|-timestamp (default -timestamp)
        - page, page_size
        """
        user = request.user
        params = request.query_params
        start_date = parse_date(params.get('start_date')) if params.get('start_date') else None
        end_date = parse_date(params.get('end_date')) if params.get('end_date') else None
        record_type = params.get('type', 'all')
        status_filter = params.get('status', 'all')
        order_by = params.get('order_by', '-timestamp')
        
        activities = []
        
        # 阅读/进度类记录
        if record_type in ['all', 'reading']:
            lr_qs = LearningRecord.objects.filter(user=user).select_related('book', 'chapter')
            if start_date:
                lr_qs = lr_qs.filter(last_learn_time__date__gte=start_date)
            if end_date:
                lr_qs = lr_qs.filter(last_learn_time__date__lte=end_date)
            for lr in lr_qs:
                completed = lr.progress >= 100
                if status_filter == 'completed' and not completed:
                    continue
                if status_filter == 'inProgress' and completed:
                    continue
                activities.append({
                    'id': f'lr-{lr.id}',
                    'source': 'learning_record',
                    'type': 'reading',
                    'bookId': lr.book.id,
                    'bookTitle': lr.book.title,
                    'chapterId': lr.chapter.id,
                    'chapterTitle': lr.chapter.title,
                    'progress': lr.progress,
                    'status': 'completed' if completed else 'inProgress',
                    'duration': 0,  # 暂无时长数据
                    'timestamp': lr.last_learn_time.isoformat(),
                })
        
        # 练习记录
        if record_type in ['all', 'practice']:
            pr_qs = PracticeRecord.objects.filter(user=user).select_related('book', 'chapter')
            if start_date:
                pr_qs = pr_qs.filter(completed_time__date__gte=start_date)
            if end_date:
                pr_qs = pr_qs.filter(completed_time__date__lte=end_date)
            for pr in pr_qs:
                completed = pr.completed
                if status_filter == 'completed' and not completed:
                    continue
                if status_filter == 'inProgress' and completed:
                    continue
                activities.append({
                    'id': f'pr-{pr.id}',
                    'source': 'practice_record',
                    'type': 'practice',
                    'bookId': pr.book.id,
                    'bookTitle': pr.book.title,
                    'chapterId': pr.chapter.id,
                    'chapterTitle': pr.chapter.title,
                    'score': pr.score,
                    'status': 'completed' if completed else 'inProgress',
                    'duration': 0,
                    'timestamp': pr.completed_time.isoformat(),
                })
        
        # 排序
        reverse = False
        key = 'timestamp'
        if order_by.startswith('-'):
            reverse = True
            key = order_by[1:]
        elif order_by:
            key = order_by
        activities.sort(key=lambda x: x.get(key, ''), reverse=reverse)
        
        # 分页
        page = int(params.get('page', 1))
        page_size = int(params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        total = len(activities)
        results = activities[start:end]
        
        return Response({
            'results': results,
            'page': page,
            'page_size': page_size,
            'total': total
        })


class UserLearningPathViewSet(viewsets.GenericViewSet, viewsets.mixins.ListModelMixin, viewsets.mixins.RetrieveModelMixin):
    """用户学习路径视图集"""
    queryset = UserLearningPath.objects.filter(is_active=True)
    serializer_class = UserLearningPathSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 用户只能查看自己的学习路径
        return super().get_queryset().filter(user=self.request.user).prefetch_related(
            'roadmap__stages__roadmap_books__book',
            'current_stage',
            'stage_progress__stage__roadmap_books__book'
        )
    
    @action(detail=False, methods=['post'])
    def create_path(self, request):
        """创建学习路径"""
        serializer = CreateUserPathSerializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    roadmap = RoadmapTemplate.objects.get(id=serializer.validated_data['roadmap_id'], is_active=True)
                    
                    # 检查用户是否已经有该路线图的学习路径
                    existing_path = UserLearningPath.objects.filter(
                        user=request.user,
                        roadmap=roadmap
                    ).first()
                    
                    if existing_path:
                        # 如果存在且已完成，可以重新开始
                        if existing_path.completed_at:
                            existing_path.progress = 0
                            existing_path.completed_at = None
                            existing_path.is_active = True
                            existing_path.custom_goals = serializer.validated_data.get('custom_goals', [])
                            existing_path.save()
                            
                            # 清除之前的进度记录
                            UserPathStage.objects.filter(user_path=existing_path).delete()
                            
                            # 创建新的阶段进度记录
                            self._create_stage_progress(existing_path, roadmap)
                            
                            # 设置第一个阶段为当前阶段
                            first_stage = roadmap.stages.order_by('stage_order').first()
                            if first_stage:
                                existing_path.current_stage = first_stage
                                existing_path.save()
                                
                            return Response(self.get_serializer(existing_path).data)
                        else:
                            return Response({'error': '您已经在学习这个路线图了'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # 创建新的学习路径
                    user_path = UserLearningPath.objects.create(
                        user=request.user,
                        roadmap=roadmap,
                        custom_goals=serializer.validated_data.get('custom_goals', [])
                    )
                    
                    # 创建阶段进度记录
                    self._create_stage_progress(user_path, roadmap)
                    
                    # 设置第一个阶段为当前阶段
                    first_stage = roadmap.stages.order_by('stage_order').first()
                    if first_stage:
                        user_path.current_stage = first_stage
                        user_path.save()
                    
                    return Response(self.get_serializer(user_path).data, status=status.HTTP_201_CREATED)
            except RoadmapTemplate.DoesNotExist:
                return Response({'error': '路线图不存在'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def update_progress(self, request, pk=None):
        """更新学习路径进度"""
        user_path = self.get_object()
        serializer = UpdatePathProgressSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    stage_id = serializer.validated_data['stage_id']
                    progress = serializer.validated_data['progress']
                    notes = serializer.validated_data.get('notes', '')
                    
                    # 获取阶段
                    stage = RoadmapStage.objects.get(id=stage_id, roadmap=user_path.roadmap)
                    
                    # 获取或创建阶段进度
                    stage_progress, created = UserPathStage.objects.get_or_create(
                        user_path=user_path,
                        stage=stage,
                        defaults={'progress': progress, 'notes': notes}
                    )
                    
                    # 更新进度
                    stage_progress.progress = progress
                    if notes:
                        stage_progress.notes = notes
                    
                    # 检查是否完成
                    if progress >= 100 and not stage_progress.is_completed:
                        stage_progress.is_completed = True
                        stage_progress.completed_at = datetime.now()
                    
                    stage_progress.save()
                    
                    # 更新总体进度
                    self._update_overall_progress(user_path)
                    
                    # 检查是否需要更新当前阶段
                    self._update_current_stage(user_path)
                    
                    # 检查是否完成整个路线图
                    if user_path.progress >= 100 and not user_path.completed_at:
                        user_path.completed_at = datetime.now()
                        user_path.save()
                    
                    return Response(self.get_serializer(user_path).data)
            except RoadmapStage.DoesNotExist:
                return Response({'error': '阶段不存在'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def pause(self, request, pk=None):
        """暂停学习路径"""
        user_path = self.get_object()
        user_path.is_active = False
        user_path.save()
        return Response({'success': True, 'message': '学习路径已暂停'})
    
    @action(detail=True, methods=['put'])
    def resume(self, request, pk=None):
        """恢复学习路径"""
        user_path = self.get_object()
        user_path.is_active = True
        user_path.save()
        return Response({'success': True, 'message': '学习路径已恢复'})
    
    def _create_stage_progress(self, user_path, roadmap):
        """为学习路径创建阶段进度记录"""
        for stage in roadmap.stages.order_by('stage_order'):
            UserPathStage.objects.create(
                user_path=user_path,
                stage=stage
            )
    
    def _update_overall_progress(self, user_path):
        """更新总体进度"""
        stage_progresses = UserPathStage.objects.filter(user_path=user_path)
        if stage_progresses.exists():
            total_progress = sum(sp.progress for sp in stage_progresses)
            avg_progress = total_progress // stage_progresses.count()
            user_path.progress = avg_progress
            user_path.save()
    
    def _update_current_stage(self, user_path):
        """更新当前阶段"""
        # 获取所有阶段
        stages = list(user_path.roadmap.stages.order_by('stage_order'))
        
        for i, stage in enumerate(stages):
            try:
                stage_progress = UserPathStage.objects.get(
                    user_path=user_path,
                    stage=stage
                )
                # 如果当前阶段未完成，则设置为当前阶段
                if not stage_progress.is_completed:
                    user_path.current_stage = stage
                    user_path.save()
                    return
            except UserPathStage.DoesNotExist:
                pass
        
        # 如果所有阶段都完成，保持最后一个阶段为当前阶段
        if stages and user_path.progress >= 100:
            user_path.current_stage = stages[-1]
            user_path.save()
    
    def _generate_recommendation_reason(self, roadmap, user_profile):
        """生成个性化推荐理由"""
        # 根据学习风格生成推荐理由
        learning_style = user_profile.get('learning_style', {})
        visual_score = learning_style.get('visual_score', 0)
        auditory_score = learning_style.get('auditory_score', 0)
        
        if visual_score > auditory_score:
            return f"此路线图包含丰富的视觉学习资源，非常适合您的视觉学习风格"
        elif auditory_score > visual_score:
            return f"此路线图提供多种听觉学习材料，与您的听觉学习风格高度匹配"
        else:
            return "此路线图提供多元化的学习资源，适合综合型学习风格"
    
    def _generate_personalized_features(self, roadmap, user_profile):
        """生成个性化特征标签"""
        features = []
        
        # 基于学习风格添加特征
        learning_style = user_profile.get('learning_style', {})
        if learning_style.get('visual_score', 0) > 0.7:
            features.append("视觉学习优化")
        if learning_style.get('auditory_score', 0) > 0.7:
            features.append("听觉学习优化")
        if learning_style.get('kinesthetic_score', 0) > 0.7:
            features.append("实践导向")
        
        # 基于难度偏好添加特征
        difficulty_preference = user_profile.get('difficulty_preference', 'medium')
        if difficulty_preference:
            features.append(f"{difficulty_preference}难度")
        
        # 基于路线图特征添加标签
        try:
            stages_count = roadmap.stages.count() if hasattr(roadmap, 'stages') else 0
            if stages_count <= 3:
                features.append("结构紧凑")
            elif stages_count >= 6:
                features.append("系统全面")
        except:
            pass
        
        return features


class NoteViewSet(viewsets.ModelViewSet):
    """笔记视图集"""
    queryset = Note.objects.all()
    permission_classes = [IsAuthenticated]
    filterset_fields = ['book', 'chapter', 'is_favorite', 'is_public']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at', 'view_count']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NoteListSerializer
        elif self.action == 'create':
            return NoteCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return NoteUpdateSerializer
        return NoteDetailSerializer
    
    def get_queryset(self):
        queryset = Note.objects.filter(user=self.request.user)
        
        # 支持按标签筛选
        tag_id = self.request.query_params.get('tag')
        if tag_id:
            queryset = queryset.filter(tag_relations__tag_id=tag_id)
        
        return queryset.select_related('book', 'chapter').prefetch_related('tag_relations__tag')
    
    def perform_create(self, serializer):
        # 创建时自动关联当前用户
        print(f"创建笔记 - 请求数据: {self.request.data}")
        print(f"创建笔记 - 验证后的数据: {serializer.validated_data}")
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        try:
            print(f"收到创建笔记请求 - 数据: {request.data}")
            response = super().create(request, *args, **kwargs)
            print(f"创建笔记成功 - 响应: {response.data}")
            return response
        except Exception as e:
            print(f"创建笔记失败 - 错误: {str(e)}")
            print(f"创建笔记失败 - 错误类型: {type(e).__name__}")
            if hasattr(e, 'detail'):
                print(f"创建笔记失败 - 详细信息: {e.detail}")
            raise
    
    def perform_update(self, serializer):
        # 更新时确保只能修改自己的笔记
        instance = self.get_object()
        if instance.user != self.request.user:
            from rest_framework import status
            raise status.HTTP_403_FORBIDDEN
        serializer.save()
    
    def perform_destroy(self, instance):
        # 删除时确保只能删除自己的笔记
        if instance.user != self.request.user:
            from rest_framework import status
            raise status.HTTP_403_FORBIDDEN
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """全文搜索笔记"""
        query = request.query_params.get('q', '')
        if not query:
            return Response({'error': '搜索关键词不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        results = self.get_queryset().filter(
            models.Q(title__icontains=query) | models.Q(content__icontains=query)
        )
        
        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(results, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """切换收藏状态"""
        note = self.get_object()
        note.is_favorite = not note.is_favorite
        note.save()
        return Response({'is_favorite': note.is_favorite})
    
    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """获取笔记版本历史"""
        print(f"获取版本历史 - 笔记ID: {pk}")
        print(f"获取版本历史 - 用户: {request.user}")
        note = self.get_object()
        print(f"获取版本历史 - 笔记对象: {note}")
        print(f"获取版本历史 - 笔记用户: {note.user}")
        versions = note.versions.all()[:10]  # 只返回最近10个版本
        print(f"获取版本历史 - 版本数量: {len(versions)}")
        serializer = NoteVersionSerializer(versions, many=True)
        print(f"获取版本历史 - 序列化数据: {serializer.data}")
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def restore_version(self, request, pk=None):
        """恢复到指定版本"""
        note = self.get_object()
        version_id = request.data.get('version_id')
        
        try:
            version = note.versions.get(id=version_id)
            # 创建当前版本的备份
            NoteVersion.objects.create(
                note=note,
                title=note.title,
                content=note.content,
                version_number=note.versions.count() + 1
            )
            # 恢复到指定版本
            note.title = version.title
            note.content = version.content
            note.save()
            
            return Response({'message': '版本恢复成功'})
        except NoteVersion.DoesNotExist:
            return Response({'error': '版本不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def share(self, request, pk=None):
        """分享笔记"""
        note = self.get_object()
        
        # 生成分享码
        import hashlib
        import time
        share_code = hashlib.md5(f"{note.id}-{time.time()}".encode()).hexdigest()
        expires_at = request.data.get('expires_at')
        
        share = NoteShare.objects.create(
            note=note,
            share_code=share_code,
            shared_by=request.user,
            expires_at=expires_at
        )
        
        return Response({
            'share_code': share_code,
            'share_url': f'/notes/shared/{share_code}',
            'expires_at': expires_at
        })
    
    @action(detail=False, methods=['get'])
    def review_reminders(self, request):
        """获取复习提醒"""
        from datetime import timedelta
        from django.utils import timezone
        
        # 根据艾宾浩斯遗忘曲线计算需要复习的笔记
        notes = self.get_queryset().filter(
            last_reviewed_at__lt=timezone.now() - timedelta(days=7)
        ).order_by('last_reviewed_at')
        
        serializer = NoteListSerializer(notes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_as_reviewed(self, request, pk=None):
        """标记为已复习"""
        note = self.get_object()
        note.last_reviewed_at = timezone.now()
        note.save()
        return Response({'message': '已标记为已复习'})
    
    @action(detail=True, methods=['post'])
    def add_attachment(self, request, pk=None):
        """添加附件"""
        note = self.get_object()
        files = request.FILES.getlist('files')
        
        attachments = []
        for file in files:
            attachment = NoteAttachment.objects.create(
                note=note,
                file=file,
                file_name=file.name,
                file_size=file.size,
                file_type=file.content_type
            )
            attachments.append(attachment)
        
        serializer = NoteAttachmentSerializer(attachments, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['delete'])
    def remove_attachment(self, request, pk=None):
        """删除附件"""
        note = self.get_object()
        attachment_id = request.data.get('attachment_id')
        
        try:
            attachment = note.attachments.get(id=attachment_id)
            attachment.delete()
            return Response({'message': '附件已删除'})
        except NoteAttachment.DoesNotExist:
            return Response({'error': '附件不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def tags(self, request):
        """获取用户的所有标签"""
        tags = NoteTag.objects.filter(user=request.user)
        serializer = NoteTagSerializer(tags, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def create_tag(self, request):
        """创建标签"""
        name = request.data.get('name')
        color = request.data.get('color', '#409EFF')
        
        tag, created = NoteTag.objects.get_or_create(
            user=request.user,
            name=name,
            defaults={'color': color}
        )
        
        serializer = NoteTagSerializer(tag)
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'])
    def add_tag(self, request, pk=None):
        """为笔记添加标签"""
        note = self.get_object()
        tag_id = request.data.get('tag_id')
        
        try:
            tag = NoteTag.objects.get(id=tag_id, user=request.user)
            NoteTagRelation.objects.get_or_create(note=note, tag=tag)
            return Response({'message': '标签已添加'})
        except NoteTag.DoesNotExist:
            return Response({'error': '标签不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def remove_tag(self, request, pk=None):
        """移除笔记的标签"""
        note = self.get_object()
        tag_id = request.data.get('tag_id')
        
        NoteTagRelation.objects.filter(note=note, tag_id=tag_id).delete()
        return Response({'message': '标签已移除'})


class LearningRecommendationViewSet(viewsets.ModelViewSet):
    """学习推荐视图集"""
    permission_classes = [IsAuthenticated]
    serializer_class = LearningRecommendationSerializer
    
    def get_queryset(self):
        # 只返回当前用户的推荐
        return LearningRecommendation.objects.filter(user=self.request.user).order_by('-created_at')
    
    @action(detail=False, methods=['post'])
    def update_preference(self, request):
        """更新学习偏好"""
        try:
            learning_preference = request.user.learning_preference
        except LearningPreference.DoesNotExist:
            learning_preference = LearningPreference(user=request.user)
        
        serializer = UpdateLearningPreferenceSerializer(learning_preference, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def preference(self, request):
        """获取学习偏好"""
        try:
            learning_preference = request.user.learning_preference
            serializer = LearningPreferenceSerializer(learning_preference)
            return Response(serializer.data)
        except LearningPreference.DoesNotExist:
            # 返回默认值
            default_data = {
                'learning_goals': [],
                'interest_areas': [],
                'difficulty_preference': 'medium',
                'daily_available_minutes': 60
            }
            return Response(default_data)
    
    @action(detail=False, methods=['post'])
    def update_style(self, request):
        """更新学习风格"""
        try:
            learning_style = request.user.learning_style
        except LearningStyle.DoesNotExist:
            learning_style = LearningStyle(user=request.user)
        
        serializer = UpdateLearningStyleSerializer(learning_style, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def style(self, request):
        """获取学习风格"""
        try:
            learning_style = request.user.learning_style
            serializer = LearningStyleSerializer(learning_style)
            return Response(serializer.data)
        except LearningStyle.DoesNotExist:
            # 返回默认值
            default_data = {
                'visual_score': 0.5,
                'auditory_score': 0.5,
                'reading_score': 0.5,
                'kinesthetic_score': 0.5,
                'pace_preference': 'balanced'
            }
            return Response(default_data)
    
    @action(detail=False, methods=['post'])
    def build_profile(self, request):
        """构建和更新用户画像"""
        engine = RecommendationEngine(request.user)
        profile_data = engine.build_user_profile()
        
        return Response({
            'learning_style': LearningStyleSerializer(profile_data['learning_style']).data,
            'learning_preference': LearningPreferenceSerializer(profile_data['learning_preference']).data,
            'total_learning_time': profile_data['total_learning_time'],
            'completed_chapters': profile_data['completed_chapters']
        }, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='roadmap')
    def recommend_roadmap(self, request):
        """推荐初始学习路线图，返回增强的推荐信息"""
        try:
            # 获取或构建用户画像
            engine = RecommendationEngine(request.user)
            user_profile = engine.build_user_profile()
            
            # 调用推荐引擎获取推荐路线图
            recommended_roadmaps = engine.recommend_roadmaps(limit=5)
            
            # 增强推荐结果，添加可视化所需的额外信息
            enhanced_roadmaps = []
            for idx, recommendation in enumerate(recommended_roadmaps):
                # 获取基础推荐数据
                roadmap = recommendation.roadmap if hasattr(recommendation, 'roadmap') else recommendation
                
                # 构建增强的路线图数据
                enhanced_roadmap = {
                    'id': roadmap.id if hasattr(roadmap, 'id') else f'recommended-{idx}',
                    'title': roadmap.title if hasattr(roadmap, 'title') else '智能推荐学习路线',
                    'description': roadmap.description if hasattr(roadmap, 'description') else '根据您的学习风格和偏好定制',
                    'difficulty_level': roadmap.difficulty_level if hasattr(roadmap, 'difficulty_level') else 'intermediate',
                    'estimated_hours': getattr(roadmap, 'estimated_hours', 80),
                    'stages': getattr(roadmap, 'stages', []),
                    'tags': getattr(roadmap, 'tags', []),
                    
                    # 添加个性化推荐信息
                    'is_recommended': True,
                    'matching_score': recommendation.score if hasattr(recommendation, 'score') else 85 + (idx * 5),  # 模拟匹配度分数
                    'recommendation_reason': '基于您的学习风格、知识掌握度和偏好生成的智能推荐',
                    'personalized_features': self._generate_personalized_features(roadmap, user_profile)
                }
                
                # 根据学习风格添加特定的推荐理由
                learning_style = user_profile.get('learning_style', {})
                if learning_style.get('visual_score', 0) > learning_style.get('auditory_score', 0):
                    enhanced_roadmap['recommendation_reason'] = f"此路线图包含丰富的视觉学习资源，非常适合您的{learning_style.get('dominant_style', '视觉')}学习风格"
                elif learning_style.get('auditory_score', 0) > learning_style.get('visual_score', 0):
                    enhanced_roadmap['recommendation_reason'] = f"此路线图提供多种听觉学习材料，与您的{learning_style.get('dominant_style', '听觉')}学习风格高度匹配"
                
                enhanced_roadmaps.append(enhanced_roadmap)
            
            # 返回增强的推荐结果
            return Response({
                'roadmaps': enhanced_roadmaps,
                'message': '智能推荐成功',
                'user_profile_summary': {
                    'learning_style': user_profile.get('learning_style', {}).get('dominant_style', '综合型'),
                    'knowledge_level': user_profile.get('knowledge_level', '中级'),
                    'interests': user_profile.get('interests', ['基础学习'])
                }
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def next_content(self, request):
        """推荐下一步学习内容"""
        path_id = request.query_params.get('path_id')
        
        engine = RecommendationEngine(request.user)
        # 先构建用户画像
        engine.build_user_profile()
        
        user_path = None
        if path_id:
            try:
                user_path = UserLearningPath.objects.get(id=path_id, user=request.user)
            except UserLearningPath.DoesNotExist:
                return Response({'error': '学习路径不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 获取推荐
        recommendations = engine.recommend_next_content(user_path)
        
        serializer = LearningRecommendationSerializer(recommendations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def learning_strategy(self, request):
        """获取学习策略建议"""
        path_id = request.query_params.get('path_id')
        
        if not path_id:
            return Response({'error': '必须提供学习路径ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user_path = UserLearningPath.objects.get(id=path_id, user=request.user)
        except UserLearningPath.DoesNotExist:
            return Response({'error': '学习路径不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        engine = RecommendationEngine(request.user)
        suggestions = engine.optimize_learning_strategy(user_path)
        
        return Response({'suggestions': suggestions})
    
    @action(detail=False, methods=['get'])
    def evaluate_effect(self, request):
        """评估学习效果"""
        engine = RecommendationEngine(request.user)
        evaluation = engine.evaluate_learning_effect()
        
        return Response(evaluation)
    
    @action(detail=True, methods=['post'])
    def feedback(self, request, pk):
        """反馈推荐内容"""
        try:
            recommendation = LearningRecommendation.objects.get(id=pk, user=request.user)
        except LearningRecommendation.DoesNotExist:
            return Response({'error': '推荐记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = FeedbackRecommendationSerializer(recommendation, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JupyterDocumentViewSet(viewsets.ModelViewSet):
    """Jupyter文档视图集"""
    queryset = JupyterDocument.objects.all()
    serializer_class = JupyterDocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取用户自己的文档和公开的文档"""
        # 获取请求参数
        book_id = self.request.query_params.get('book_id')
        chapter_id = self.request.query_params.get('chapter_id')
        is_public = self.request.query_params.get('is_public')
        
        # 基础查询：用户自己的文档或公开的文档
        queryset = JupyterDocument.objects.filter(
            (models.Q(user=self.request.user) | models.Q(is_public=True))
        )
        
        # 过滤条件
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        if chapter_id:
            queryset = queryset.filter(chapter_id=chapter_id)
        if is_public is not None:
            queryset = queryset.filter(is_public=is_public.lower() == 'true')
        
        # 按更新时间排序
        return queryset.order_by('-updated_at')
    
    def perform_create(self, serializer):
        """创建文档时自动关联当前用户"""
        serializer.save(user=self.request.user)
    
    def perform_update(self, serializer):
        """更新时确保只能修改自己的文档"""
        instance = self.get_object()
        if instance.user != self.request.user:
            return Response({'error': '无权修改此文档'}, status=status.HTTP_403_FORBIDDEN)
        serializer.save()
    
    def perform_destroy(self, instance):
        """删除时确保只能删除自己的文档"""
        if instance.user != self.request.user:
            return Response({'error': '无权删除此文档'}, status=status.HTTP_403_FORBIDDEN)
        instance.delete()


@decorators.api_view(['POST'])
@decorators.permission_classes([IsAuthenticated])
def create_jupyter_document(request):
    """创建Jupyter文档"""
    serializer = CreateJupyterDocumentSerializer(data=request.data)
    if serializer.is_valid():
        try:
            with transaction.atomic():
                # 准备文档数据
                document_data = {
                    'title': serializer.validated_data['title'],
                    'content': serializer.validated_data['content'],
                    'is_public': serializer.validated_data.get('is_public', False),
                    'user': request.user
                }
                
                # 关联书籍和章节
                book_id = serializer.validated_data.get('book_id')
                chapter_id = serializer.validated_data.get('chapter_id')
                
                if book_id:
                    try:
                        book = Book.objects.get(id=book_id)
                        document_data['book'] = book
                    except Book.DoesNotExist:
                        return Response({'error': '书籍不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                if chapter_id:
                    try:
                        chapter = Chapter.objects.get(id=chapter_id)
                        # 验证章节是否属于指定的书籍
                        if book_id and chapter.book.id != book_id:
                            return Response({'error': '章节不属于指定的书籍'}, status=status.HTTP_400_BAD_REQUEST)
                        document_data['chapter'] = chapter
                    except Chapter.DoesNotExist:
                        return Response({'error': '章节不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                # 创建文档
                document = JupyterDocument.objects.create(**document_data)
                
                # 序列化返回
                return Response(
                    JupyterDocumentSerializer(document).data,
                    status=status.HTTP_201_CREATED
                )
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@decorators.api_view(['POST'])
@decorators.permission_classes([IsAuthenticated])
def update_jupyter_document(request):
    """更新Jupyter文档"""
    # 获取文档ID
    document_id = request.data.get('id')
    if not document_id:
        return Response({'error': '文档ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 获取文档
        document = JupyterDocument.objects.get(id=document_id)
        
        # 验证权限
        if document.user != request.user:
            return Response({'error': '无权修改此文档'}, status=status.HTTP_403_FORBIDDEN)
        
        # 验证数据
        serializer = UpdateJupyterDocumentSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                # 更新文档字段
                if 'title' in serializer.validated_data:
                    document.title = serializer.validated_data['title']
                if 'content' in serializer.validated_data:
                    document.content = serializer.validated_data['content']
                if 'is_public' in serializer.validated_data:
                    document.is_public = serializer.validated_data['is_public']
                
                # 更新关联的书籍和章节
                if 'book_id' in serializer.validated_data:
                    if serializer.validated_data['book_id'] is None:
                        document.book = None
                    else:
                        try:
                            document.book = Book.objects.get(id=serializer.validated_data['book_id'])
                        except Book.DoesNotExist:
                            return Response({'error': '书籍不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                if 'chapter_id' in serializer.validated_data:
                    if serializer.validated_data['chapter_id'] is None:
                        document.chapter = None
                    else:
                        try:
                            chapter = Chapter.objects.get(id=serializer.validated_data['chapter_id'])
                            # 验证章节是否属于指定的书籍
                            if document.book and chapter.book.id != document.book.id:
                                return Response({'error': '章节不属于指定的书籍'}, status=status.HTTP_400_BAD_REQUEST)
                            document.chapter = chapter
                        except Chapter.DoesNotExist:
                            return Response({'error': '章节不存在'}, status=status.HTTP_404_NOT_FOUND)
                
                # 保存更新
                document.save()
                
                # 序列化返回
                return Response(
                    JupyterDocumentSerializer(document).data,
                    status=status.HTTP_200_OK
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except JupyterDocument.DoesNotExist:
        return Response({'error': '文档不存在'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

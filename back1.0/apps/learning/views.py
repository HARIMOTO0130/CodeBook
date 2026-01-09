"""学习记录视图函数"""
from rest_framework import viewsets, status, decorators, generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from django.db import models

# 为了兼容性，定义action装饰器
action = decorators.action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from django.db import transaction
from datetime import date, datetime
import tempfile
import subprocess
import os
import time
import json
import sys
import logging
import functools

# 配置日志记录器
logger = logging.getLogger(__name__)

# 权限验证装饰器
def note_permission_required(action_name):
    def decorator(view_func):
        @functools.wraps(view_func)
        def wrapped_view(self, request, *args, **kwargs):
            note = self.get_object()
            if note.user != request.user:
                logger.warning(f"用户 {request.user.username} (ID: {request.user.id}) 尝试越权{action_name}笔记 {note.id}，该笔记属于用户 {note.user.username} (ID: {note.user.id})")
                raise PermissionDenied(detail="您没有权限操作该笔记")
            return view_func(self, request, *args, **kwargs)
        return wrapped_view
    return decorator

from bs4 import BeautifulSoup
from django.utils import timezone
from apps.books.models import Book, Chapter
from .models import LearningRecord, PracticeRecord, HeatmapData, WrongQuestion, RoadmapTemplate, RoadmapStage, UserLearningPath, UserPathStage, Note, NoteTag, Exercise, JupyterDocument, LearningStyle, KnowledgeMastery, LearningRecommendation, LearningPreference, KnowledgeNode, KnowledgeRelation
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
    UpdateLearningPreferenceSerializer,
    KnowledgeNodeSerializer,
    KnowledgeRelationSerializer
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
    supported_languages = ['python', 'javascript', 'java', 'c', 'cpp', 'html', 'css']
    
    # 安全检查
    if language not in supported_languages:
        return Response({
            'success': False,
            'error': {
                'type': 'unsupported_language',
                'code': 'UNSUPPORTED_LANGUAGE',
                'message': f'暂不支持该语言',
                'details': f'支持的语言: {', '.join(supported_languages)}'
            },
            'stdout': '',
            'stderr': '',
            'exitCode': -1,
            'durationMs': 0,
            'stats': {
                'language': language,
                'codeLength': len(code),
                'executionTime': 0,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not code:
        return Response({
            'success': False,
            'error': {
                'type': 'empty_code',
                'code': 'EMPTY_CODE',
                'message': '代码为空',
                'details': '请输入要执行的代码'
            },
            'stdout': '',
            'stderr': '',
            'exitCode': -1,
            'durationMs': 0,
            'stats': {
                'language': language,
                'codeLength': 0,
                'executionTime': 0,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 代码长度限制
    max_code_length = 10000
    if len(code) > max_code_length:
        return Response({
            'success': False,
            'error': {
                'type': 'code_too_long',
                'code': 'CODE_TOO_LONG',
                'message': '代码长度超过限制',
                'details': f'最大允许长度: {max_code_length}字符，当前长度: {len(code)}字符'
            },
            'stdout': '',
            'stderr': '',
            'exitCode': -1,
            'durationMs': 0,
            'stats': {
                'language': language,
                'codeLength': len(code),
                'executionTime': 0,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
        }, status=status.HTTP_400_BAD_REQUEST)

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
        },
        'shell': False,  # 禁用shell，防止命令注入
    }

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            cwd = tmpdir
            
            # 根据语言准备执行环境和命令
            if language == 'python':
                # 安全的Python执行，禁用危险模块导入
                # 使用字符串拼接而不是f-string来避免转义问题
                secure_code = """
# 安全执行包装
import sys
import builtins

# 限制资源使用 - 只在支持resource模块的系统上执行
try:
    import resource
    # 限制内存使用
    resource.setrlimit(resource.RLIMIT_AS, (int(MAX_MEMORY * 1024 * 1024), -1))
    # 限制CPU时间
    resource.setrlimit(resource.RLIMIT_CPU, (MAX_TIME, MAX_TIME))
    # 限制进程数
    resource.setrlimit(resource.RLIMIT_NPROC, (16, 16))
except ImportError:
    # 在Windows系统上，resource模块不可用，跳过资源限制
    pass

# 禁用危险模块和函数
blocked_modules = ['os', 'sys', 'subprocess', 'socket', 'shutil', '__import__', \
                  'exec', 'eval', 'open', 'file', 'compile', 'globals', 'locals',\
                  'input', 'help', 'exit', 'quit', 'breakpoint']

# 覆盖__builtins__中的危险函数
for func_name in ['open', 'file', 'execfile', '__import__', 'eval', 'exec',\
             'input', 'help', 'exit', 'quit', 'breakpoint']:
    if func_name in builtins.__dict__:
        def create_blocked_func(f_name):
            def blocked_func(*args, **kwargs):
                print(f"Error: Disabled function '{f_name}'")
            return blocked_func
        builtins.__dict__[func_name] = create_blocked_func(func_name)

# 覆盖sys模块，禁用危险操作
sys.modules['sys'] = type('FakeSys', (), {
    'argv': ['python'],
    'version': '3.8.10',
    'platform': 'linux',
    'exit': lambda *args: print("错误：禁止使用sys.exit")
})()

# 执行用户代码
USER_CODE
"""
                # 使用字符串替换来插入变量
                secure_code = secure_code.replace('MAX_MEMORY', str(max_memory_mb))
                secure_code = secure_code.replace('MAX_TIME', str(max_time))
                secure_code = secure_code.replace('USER_CODE', code)
                filename = os.path.join(cwd, 'main.py')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(secure_code)
                cmd = ['python', '-B', '-E', '-S', filename]  # -B: 不写入.pyc文件, -E: 忽略环境变量, -S: 不导入site模块
                
            elif language == 'javascript':
                filename = os.path.join(cwd, 'main.js')
                with open(filename, 'w', encoding='utf-8') as f:
                    # 避免使用f-string嵌套，直接拼接字符串
                    wrapper_start = '''
// 安全执行包装
const originalSetTimeout = setTimeout;
const originalSetInterval = setInterval;

// 限制内存使用
function checkMemoryUsage() {
  const currentMem = process.memoryUsage().heapUsed;
  const maxMemory = '''
                    wrapper_middle = str(max_memory_mb) + ''' * 1024 * 1024;
  if (currentMem > maxMemory) {
    console.error('内存使用超出限制');
    process.exit(1);
  }
}

// 覆盖定时器，添加内存检查
setTimeout = (callback, delay) => {
  const wrappedCallback = () => {
    checkMemoryUsage();
    callback();
  };
  return originalSetTimeout(wrappedCallback, delay);
};

setInterval = (callback, delay) => {
  const wrappedCallback = () => {
    checkMemoryUsage();
    callback();
  };
  return originalSetInterval(wrappedCallback, delay);
};

// 禁用危险模块
const blockedModules = ['child_process', 'fs', 'net', 'http', 'https', 'os', 'path', 'process', 'url'];
for (const moduleName of blockedModules) {
  Object.defineProperty(require, 'cache', {
    __get: () => ({
      [moduleName]: { exports: {}} // 返回空对象
    })
  });
}

// 禁用危险全局对象
const originalRequire = require;
require = (moduleName) => {
  if (blockedModules.includes(moduleName)) {
    console.error(`错误：禁止导入${moduleName}模块`);
    return {};
  }
  return originalRequire(moduleName);
};

// 执行用户代码
'''
                    f.write(wrapper_start + wrapper_middle + code)
                cmd = ['node', '--max-old-space-size={}'.format(max_memory_mb), '--no-warnings', filename]
            elif language == 'java':
                # Java代码执行：先编译再运行
                filename = os.path.join(cwd, 'Main.java')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                # 编译Java文件
                compile_cmd = ['javac', '-Xlint:all', 'Main.java']
                try:
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
                        cmd = ['java', '-Xmx{}m'.format(max_memory_mb), '-Xms64m', '-Djava.security.manager', 'Main']
                except FileNotFoundError:
                    stderr_text = 'Java编译器未安装，请安装JDK以执行Java代码'
                    exit_code = -1
                    cmd = None
                except Exception as e:
                    stderr_text = f'Java编译失败：{str(e)}'
                    exit_code = -1
                    cmd = None
            elif language == 'c':
                # C代码执行：先编译再运行
                filename = os.path.join(cwd, 'main.c')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                # 编译C文件
                compile_cmd = ['gcc', '-Wall', '-Wextra', '-pedantic', '-O2', 'main.c', '-o', 'main.exe']
                try:
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
                except FileNotFoundError:
                    stderr_text = 'C编译器未安装，请安装GCC以执行C代码'
                    exit_code = -1
                    cmd = None
                except Exception as e:
                    stderr_text = f'C编译失败：{str(e)}'
                    exit_code = -1
                    cmd = None
            elif language == 'cpp':
                # C++代码执行：先编译再运行
                filename = os.path.join(cwd, 'main.cpp')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                # 编译C++文件
                compile_cmd = ['g++', '-Wall', '-Wextra', '-pedantic', '-O2', 'main.cpp', '-o', 'main.exe']
                try:
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
                        # 运行编译后的C++程序
                        cmd = ['./main.exe']
                except FileNotFoundError:
                    stderr_text = 'C++编译器未安装，请安装GCC以执行C++代码'
                    exit_code = -1
                    cmd = None
                except Exception as e:
                    stderr_text = f'C++编译失败：{str(e)}'
                    exit_code = -1
                    cmd = None
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
                    stdout_text += f"\n- 脚本数量: {len(soup.find_all('script'))}"
                    stdout_text += f"\n- 样式数量: {len(soup.find_all('style'))}"
                    stdout_text += f"\n- div容器数量: {len(soup.find_all('div'))}"
                    stdout_text += f"\n- 表单元素数量: {len(soup.find_all(['form', 'input', 'button', 'select', 'textarea']))}"
                except Exception as e:
                    stdout_text += f"\n解析HTML时出错: {str(e)}"
                exit_code = 0
                # HTML不需要执行命令
                cmd = None
            elif language == 'css':
                # CSS不能直接执行，返回解析后的信息
                filename = os.path.join(cwd, 'style.css')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                # 返回CSS解析信息而非执行结果
                stdout_text = "CSS文件已生成，在实际环境中可以应用到HTML文件"
                # 简单解析CSS内容统计
                try:
                    # 统计CSS规则数量
                    rules_count = len(code.split('}')) - 1
                    # 统计选择器数量
                    selectors_count = len(code.split('{')) - 1
                    # 统计属性数量
                    properties_count = len(code.split(';')) - code.count('/*')
                    
                    stdout_text += f"\n\nCSS解析信息："
                    stdout_text += f"\n- 规则数量: {rules_count}"
                    stdout_text += f"\n- 选择器数量: {selectors_count}"
                    stdout_text += f"\n- 属性数量: {properties_count}"
                    stdout_text += f"\n- 文件大小: {len(code)} 字符"
                except Exception as e:
                    stdout_text += f"\n解析CSS时出错: {str(e)}"
                exit_code = 0
                # CSS不需要执行命令
                cmd = None

            # 设置额外的安全参数
            if sys.platform.startswith('linux'):
                # Linux系统下使用更严格的隔离
                subprocess_kwargs.update({
                    'preexec_fn': lambda: (
                        # 限制进程数
                        resource.setrlimit(resource.RLIMIT_NPROC, (16, 16)),
                        # 限制CPU时间
                        resource.setrlimit(resource.RLIMIT_CPU, (max_time, max_time)),
                        # 限制文件大小
                        resource.setrlimit(resource.RLIMIT_FSIZE, (1024 * 1024, 1024 * 1024)),
                        # 限制打开文件数
                        resource.setrlimit(resource.RLIMIT_NOFILE, (128, 128))
                    )
                })
            elif sys.platform.startswith('win'):
                # Windows系统下的安全设置
                subprocess_kwargs.update({
                    'creationflags': subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NO_WINDOW
                })

            # 执行代码（仅在非HTML且cmd存在时执行）
            if language != 'html' and cmd is not None:
                proc = subprocess.run(cmd, cwd=cwd, **subprocess_kwargs)
                
                # 智能解码输出，优先使用utf-8，失败时尝试gbk（Windows系统常见编码）
                def decode_output(output_bytes):
                    try:
                        # 优先尝试UTF-8
                        return output_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        try:
                            # 尝试GBK编码（Windows系统常见）
                            return output_bytes.decode('gbk')
                        except UnicodeDecodeError:
                            # 最后使用replace模式，确保不会崩溃
                            return output_bytes.decode('utf-8', errors='replace')
                
                stdout_text = decode_output(proc.stdout)
                stderr_text = decode_output(proc.stderr)
                exit_code = proc.returncode

    except subprocess.TimeoutExpired:
        stderr_text = f'执行超时（>{max_time}s），代码可能存在死循环或执行时间过长'
        exit_code = -1
    except FileNotFoundError as e:
        stderr_text = '执行环境缺失，请安装所需运行时（如 Python 或 Node.js）'
        exit_code = -1
    except PermissionError as e:
        stderr_text = f'权限错误：{str(e)}'
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
    
    # 构建错误信息
    error = None
    if stderr_text and exit_code != 0:
        error_type = 'execution_error'
        error_code = 'EXECUTION_ERROR'
        error_message = '代码执行失败'
        
        if '超时' in stderr_text:
            error_type = 'timeout_error'
            error_code = 'TIMEOUT_ERROR'
            error_message = '执行超时'
        elif '环境缺失' in stderr_text:
            error_type = 'environment_error'
            error_code = 'ENVIRONMENT_ERROR'
            error_message = '执行环境缺失'
        elif '权限错误' in stderr_text:
            error_type = 'permission_error'
            error_code = 'PERMISSION_ERROR'
            error_message = '权限错误'
        elif language in ['java', 'c', 'cpp'] and any(term in stderr_text for term in ['error:', 'warning:', 'undefined reference']):
            error_type = 'compile_error'
            error_code = 'COMPILE_ERROR'
            error_message = '编译失败'
        
        error = {
            'type': error_type,
            'code': error_code,
            'message': error_message,
            'details': stderr_text
        }
    
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
        wrong_questions = WrongQuestion.objects.filter(user=request.user).select_related('book', 'chapter', 'practice').order_by('-attempt_time')
        
        # 构建响应数据
        data = []
        for wq in wrong_questions:
            data.append({
                'id': wq.id,
                'title': wq.title,
                'difficulty': wq.difficulty,
                'question_type': wq.question_type,
                'attempt_time': wq.attempt_time.isoformat() if wq.attempt_time else wq.created_at.isoformat(),
                'practice_id': wq.practice.id if wq.practice else None,
                'book': wq.book.id if wq.book else None,
                'book_id': wq.book.id if wq.book else None,  # 添加book_id字段
                'chapter': wq.chapter.id if wq.chapter else None,
                'chapter_id': wq.chapter.id if wq.chapter else None,  # 添加chapter_id字段
                'book_title': wq.book.title if wq.book else None,
                'chapter_title': wq.chapter.title if wq.chapter else None,
                'status': 'unresolved'  # 默认状态为未解决
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
    
    @action(detail=False, methods=['post'])
    def add_from_exercise(self, request):
        """从练习题添加错题"""
        try:
            from apps.books.models import Practice as BookPractice
            
            data = request.data
            user = request.user
            
            # 获取练习题或练习记录
            practice_id = data.get('practice_id')
            exercise_id = data.get('exercise_id')
            question_type = data.get('question_type', 'unknown')
            
            if not practice_id and not exercise_id:
                return Response({"error": "必须提供practice_id或exercise_id"}, status=status.HTTP_400_BAD_REQUEST)
            
            # 初始化错题数据
            wrong_question_data = {
                'title': '',
                'difficulty': 2,
                'question_type': question_type,
                'book': None,
                'chapter': None,
                'practice': None  # 添加practice字段用于唯一标识
            }
            
            # 处理BookPractice模型（教材练习题集）
            if practice_id:
                try:
                    # 首先尝试从BookPractice模型查询
                    book_practice = BookPractice.objects.get(id=practice_id)
                    wrong_question_data['title'] = book_practice.title
                    wrong_question_data['difficulty'] = book_practice.difficulty
                    wrong_question_data['book'] = book_practice.chapter.book if hasattr(book_practice, 'chapter') and hasattr(book_practice.chapter, 'book') else None
                    wrong_question_data['chapter'] = book_practice.chapter if hasattr(book_practice, 'chapter') else None
                except BookPractice.DoesNotExist:
                    # 如果BookPractice不存在，再尝试从Exercise模型查询
                    try:
                        exercise = Exercise.objects.get(id=practice_id)
                        wrong_question_data['title'] = exercise.title
                        wrong_question_data['difficulty'] = exercise.difficulty
                        wrong_question_data['practice'] = exercise  # 设置practice字段
                    except Exercise.DoesNotExist:
                        return Response({"error": "练习题不存在"}, status=status.HTTP_404_NOT_FOUND)
            elif exercise_id:
                # 处理Exercise模型（独立练习题）
                try:
                    exercise = Exercise.objects.get(id=exercise_id)
                    wrong_question_data['title'] = exercise.title
                    wrong_question_data['difficulty'] = exercise.difficulty
                    wrong_question_data['practice'] = exercise  # 设置practice字段
                except Exercise.DoesNotExist:
                    return Response({"error": "练习题不存在"}, status=status.HTTP_404_NOT_FOUND)
            
            # 创建或更新错题记录
            if wrong_question_data['practice']:
                # 如果有practice对象，使用practice作为唯一标识
                wrong_question, created = WrongQuestion.objects.update_or_create(
                    user=user,
                    practice=wrong_question_data['practice'],
                    defaults={
                        'title': wrong_question_data['title'],
                        'difficulty': wrong_question_data['difficulty'],
                        'question_type': wrong_question_data['question_type'],
                        'book': wrong_question_data['book'],
                        'chapter': wrong_question_data['chapter'],
                        'attempt_time': timezone.now()
                    }
                )
            else:
                # 如果没有practice对象（即BookPractice），使用title + book + chapter作为唯一标识
                wrong_question, created = WrongQuestion.objects.update_or_create(
                    user=user,
                    title=wrong_question_data['title'],
                    book=wrong_question_data['book'],
                    chapter=wrong_question_data['chapter'],
                    defaults={
                        'difficulty': wrong_question_data['difficulty'],
                        'question_type': wrong_question_data['question_type'],
                        'attempt_time': timezone.now()
                    }
                )
            
            return Response({
                "success": True,
                "id": wrong_question.id,
                "created": created
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def status(self, request, pk=None):
        """更新错题状态"""
        try:
            wrong_question = self.get_object()
            status_value = request.data.get('status')
            
            if status_value == 'resolved' or status_value == 'mastered':
                # 标记为已解决或已掌握，删除错题记录
                wrong_question.delete()
                return Response({"success": True, "message": "错题已标记为掌握"})
            elif status_value == 'redoing' or status_value == 'reviewed':
                # 标记为重做中或已复习，更新最后尝试时间
                wrong_question.attempt_time = timezone.now()
                wrong_question.save()
                return Response({"success": True, "message": "错题状态已更新"})
            elif status_value == 'unresolved':
                # 标记为未解决，仅更新最后尝试时间
                wrong_question.attempt_time = timezone.now()
                wrong_question.save()
                return Response({"success": True, "message": "错题状态已更新"})
            
            return Response({"error": "无效的状态值"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 个性化学习路径相关视图
class PersonalizedLearningPathAPIView(APIView):
    """个性化学习路径API"""
    permission_classes = [IsAuthenticated]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化个性化学习路径生成器
        from .personalized_learning_path import PersonalizedLearningPathGenerator
        self.path_generator = PersonalizedLearningPathGenerator()
    
    @decorators.api_view(['POST'])
    @decorators.permission_classes([IsAuthenticated])
    def generate_path(request):
        """生成个性化学习路径
        
        请求参数：
        - learning_goal: 学习目标
        - max_nodes: 最大节点数量（可选，默认10）
        
        返回：
        - path: 学习路径节点列表
        - explanation: 学习路径解释
        - suggestions: 个性化学习建议
        - user_profile: 用户画像
        """
        from .personalized_learning_path import PersonalizedLearningPathGenerator
        path_generator = PersonalizedLearningPathGenerator()
        
        learning_goal = request.data.get('learning_goal', '')
        max_nodes = request.data.get('max_nodes', 10)
        
        if not learning_goal:
            return Response({'error': '学习目标不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = path_generator.generate_learning_path(request.user, learning_goal, max_nodes)
            # 如果生成结果中只包含错误信息，回退到简化路径而不是返回500
            if isinstance(result, dict) and result.get('error'):
                raise Exception(result.get('error'))
            return Response(result)
        except Exception as e:
            # 避免前端直接收到500，这里提供一个简化的兜底学习路径
            print(f"[PersonalizedLearningPathAPIView] generate_path 出错，使用回退方案: {e}")
            fallback_path = [
                {
                    "id": 1,
                    "title": "明确学习目标",
                    "type": "concept",
                    "level": 1,
                    "difficulty": 1.0,
                    "description": f"根据您的目标「{learning_goal}」梳理核心知识点。"
                },
                {
                    "id": 2,
                    "title": "打牢基础知识",
                    "type": "concept",
                    "level": 1,
                    "difficulty": 1.5,
                    "description": "通过基础教材和示例练习，建立对关键概念的初步理解。"
                },
                {
                    "id": 3,
                    "title": "结合案例进行实践",
                    "type": "skill",
                    "level": 2,
                    "difficulty": 2.0,
                    "description": "选择1-2个与目标相关的小项目，将知识应用到实际问题中。"
                }
            ][: max_nodes]
            
            fallback_suggestions = [
                "建议先用 1-2 天时间明确学习目标，并拆解为可执行的小任务。",
                "建议每天保持至少 30 分钟的学习时间，形成稳定节奏。",
                "建议在实践过程中主动记录问题，并及时查阅资料或向老师/同学请教。"
            ]
            
            return Response(
                {
                    "path": fallback_path,
                    "explanation": "由于智能路径生成服务暂时不可用，系统为您生成了一条基础学习路径，帮助您循序渐进地开展学习。",
                    "suggestions": fallback_suggestions,
                    "user_profile": {}
                },
                status=status.HTTP_200_OK,
            )
    
    @decorators.api_view(['POST'])
    @decorators.permission_classes([IsAuthenticated])
    def update_path(request):
        """更新学习路径
        
        请求参数：
        - path: 当前学习路径
        - performance: 学习表现数据
        
        返回：
        - updated_path: 更新后的学习路径
        """
        from .personalized_learning_path import PersonalizedLearningPathGenerator
        path_generator = PersonalizedLearningPathGenerator()
        
        path = request.data.get('path', [])
        performance = request.data.get('performance', {})
        
        if not path:
            return Response({'error': '学习路径不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            updated_path = path_generator.update_learning_path(request.user, path, performance)
            return Response({'updated_path': updated_path})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @decorators.api_view(['POST'])
    @decorators.permission_classes([IsAuthenticated])
    def generate_feedback(request):
        """生成学习反馈
        
        请求参数：
        - performance: 学习表现数据
        
        返回：
        - feedback: 学习反馈
        - improvement_suggestions: 改进建议
        """
        from .personalized_learning_path import PersonalizedLearningPathGenerator
        path_generator = PersonalizedLearningPathGenerator()
        
        performance = request.data.get('performance', {})
        
        try:
            result = path_generator.generate_learning_feedback(request.user, performance)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @decorators.api_view(['POST'])
    @decorators.permission_classes([IsAuthenticated])
    def generate_smart_path(request):
        """生成智能推荐学习路径图（类似mo平台）
        
        请求参数：
        - learning_goal: 学习目标（可选，默认为"AI学习"）
        - max_nodes: 最大节点数量（可选，默认10）
        
        返回：
        - nodes: 路径节点列表，包含节点信息和位置坐标
        - edges: 节点之间的连接关系
        - explanation: 路径解释
        - suggestions: 个性化学习建议
        """
        from .personalized_learning_path import PersonalizedLearningPathGenerator
        path_generator = PersonalizedLearningPathGenerator()
        
        learning_goal = request.data.get('learning_goal', 'AI学习')
        max_nodes = request.data.get('max_nodes', 10)
        
        try:
            # 生成个性化学习路径
            result = path_generator.generate_learning_path(request.user, learning_goal, max_nodes)
            path_nodes = result.get('path', [])
            
            if not path_nodes:
                return Response({
                    'nodes': [],
                    'edges': [],
                    'explanation': '暂时无法生成学习路径，请稍后重试',
                    'suggestions': []
                }, status=status.HTTP_200_OK)
            
            # 构建节点数据（包含位置信息，用于可视化）
            nodes = []
            for i, node in enumerate(path_nodes):
                # 计算节点位置（类似mo平台的布局）
                # 使用层级布局：节点按顺序排列，每层可以有多个节点
                level = node.get('level', i + 1)
                nodes_in_level = sum(1 for n in path_nodes if n.get('level', 0) == level)
                node_index_in_level = sum(1 for n in path_nodes[:i] if n.get('level', 0) == level)
                
                # 计算x坐标（水平位置）
                x = 150 + level * 250  # 每层间隔250px
                # 计算y坐标（垂直位置，同一层的节点垂直排列）
                y = 200 + node_index_in_level * 120  # 每个节点间隔120px
                
                nodes.append({
                    'id': node.get('id', i + 1),
                    'title': node.get('title', f'节点{i+1}'),
                    'type': node.get('type', 'concept'),
                    'level': level,
                    'difficulty': node.get('difficulty', 1.0),
                    'importance': node.get('importance', 5.0),
                    'description': node.get('description', ''),
                    'professional_group': node.get('professional_group', 'science'),
                    'tags': node.get('tags', []),
                    'x': x,
                    'y': y,
                    'status': 'pending'  # pending, current, completed
                })
            
            # 构建边数据（节点之间的连接）
            edges = []
            for i in range(len(nodes) - 1):
                edges.append({
                    'source': nodes[i]['id'],
                    'target': nodes[i + 1]['id'],
                    'type': 'next',  # next, prerequisite, related
                    'strength': 1.0
                })
            
            return Response({
                'nodes': nodes,
                'edges': edges,
                'explanation': result.get('explanation', '为您生成了个性化学习路径'),
                'suggestions': result.get('suggestions', []),
                'user_profile': result.get('user_profile', {})
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"生成智能推荐路径失败: {e}")
            # 返回一个简化的回退路径
            fallback_nodes = [
                {
                    'id': 1,
                    'title': 'Python基础',
                    'type': 'concept',
                    'level': 1,
                    'difficulty': 1.0,
                    'importance': 5.0,
                    'description': '掌握Python编程基础',
                    'x': 150,
                    'y': 200,
                    'status': 'pending'
                },
                {
                    'id': 2,
                    'title': '机器学习算法',
                    'type': 'concept',
                    'level': 2,
                    'difficulty': 2.0,
                    'importance': 4.5,
                    'description': '学习经典机器学习算法',
                    'x': 400,
                    'y': 200,
                    'status': 'pending'
                },
                {
                    'id': 3,
                    'title': '深度学习',
                    'type': 'concept',
                    'level': 3,
                    'difficulty': 3.0,
                    'importance': 4.0,
                    'description': '深入学习神经网络和深度学习',
                    'x': 650,
                    'y': 200,
                    'status': 'pending'
                }
            ]
            fallback_edges = [
                {'source': 1, 'target': 2, 'type': 'next', 'strength': 1.0},
                {'source': 2, 'target': 3, 'type': 'next', 'strength': 1.0}
            ]
            
            return Response({
                'nodes': fallback_nodes,
                'edges': fallback_edges,
                'explanation': '由于智能路径生成服务暂时不可用，系统为您生成了一条基础学习路径',
                'suggestions': [
                    '建议按照从基础到高级的顺序学习',
                    '定期复习已学内容，加深理解',
                    '多做实践练习，巩固所学知识'
                ],
                'user_profile': {}
            }, status=status.HTTP_200_OK)


# 知识图谱相关视图
class KnowledgeGraphAPIView(APIView):
    """知识图谱API"""
    permission_classes = [IsAuthenticated]
    
    @decorators.api_view(['GET'])
    @decorators.permission_classes([IsAuthenticated])
    def get_nodes(request):
        """获取知识节点列表
        
        查询参数：
        - graph_id: 知识图谱ID（可选）
        - type: 节点类型（可选）
        - level: 节点层级（可选）
        - professional_group: 专业组（可选）
        
        返回：
        - nodes: 知识节点列表
        """
        from .models import KnowledgeNode
        
        graph_id = request.query_params.get('graph_id')
        node_type = request.query_params.get('type')
        level = request.query_params.get('level')
        professional_group = request.query_params.get('professional_group')
        
        queryset = KnowledgeNode.objects.all()
        
        if graph_id:
            queryset = queryset.filter(graph_id=graph_id)
        if node_type:
            queryset = queryset.filter(type=node_type)
        if level:
            queryset = queryset.filter(level=level)
        if professional_group:
            queryset = queryset.filter(professional_group=professional_group)
        
        nodes = []
        for node in queryset:
            nodes.append({
                "id": node.id,
                "title": node.title,
                "type": node.type,
                "level": node.level,
                "difficulty": node.difficulty,
                "importance": node.importance,
                "description": node.description,
                "professional_group": node.professional_group,
                "tags": node.tags
            })
        
        return Response({'nodes': nodes})
    
    @decorators.api_view(['GET'])
    @decorators.permission_classes([IsAuthenticated])
    def get_relations(request):
        """获取知识关系列表
        
        查询参数：
        - graph_id: 知识图谱ID（可选）
        - relation_type: 关系类型（可选）
        
        返回：
        - relations: 知识关系列表
        """
        from .models import KnowledgeRelation
        
        graph_id = request.query_params.get('graph_id')
        relation_type = request.query_params.get('relation_type')
        
        queryset = KnowledgeRelation.objects.all()
        
        if graph_id:
            queryset = queryset.filter(graph_id=graph_id)
        if relation_type:
            queryset = queryset.filter(relation_type=relation_type)
        
        relations = []
        for relation in queryset:
            relations.append({
                "id": relation.id,
                "source": relation.source.id,
                "target": relation.target.id,
                "relation_type": relation.relation_type,
                "strength": relation.strength,
                "source_title": relation.source.title,
                "target_title": relation.target.title
            })
        
        return Response({'relations': relations})
    
    @decorators.api_view(['POST'])
    @decorators.permission_classes([IsAuthenticated])
    def add_node(request):
        """添加知识节点
        
        请求参数：
        - title: 节点标题
        - type: 节点类型
        - level: 节点层级
        - difficulty: 难度系数
        - importance: 重要程度
        - description: 节点描述
        - professional_group: 专业组
        - tags: 节点标签
        - graph_id: 知识图谱ID
        
        返回：
        - node: 添加的知识节点
        """
        from .models import KnowledgeNode, KnowledgeGraph
        
        graph_id = request.data.get('graph_id')
        title = request.data.get('title')
        node_type = request.data.get('type')
        level = request.data.get('level', 1)
        difficulty = request.data.get('difficulty', 3.0)
        importance = request.data.get('importance', 3.0)
        description = request.data.get('description', '')
        professional_group = request.data.get('professional_group', 'science')
        tags = request.data.get('tags', [])
        
        if not graph_id or not title or not node_type:
            return Response({'error': 'graph_id、title和type不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            graph = KnowledgeGraph.objects.get(id=graph_id)
            node = KnowledgeNode.objects.create(
                graph=graph,
                title=title,
                type=node_type,
                level=level,
                difficulty=difficulty,
                importance=importance,
                description=description,
                professional_group=professional_group,
                tags=tags
            )
            
            return Response({
                "id": node.id,
                "title": node.title,
                "type": node.type,
                "level": node.level,
                "difficulty": node.difficulty,
                "importance": node.importance,
                "description": node.description,
                "professional_group": node.professional_group,
                "tags": node.tags
            })
        except KnowledgeGraph.DoesNotExist:
            return Response({'error': '知识图谱不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @decorators.api_view(['POST'])
    @decorators.permission_classes([IsAuthenticated])
    def add_relation(request):
        """添加知识关系
        
        请求参数：
        - graph_id: 知识图谱ID
        - source_id: 源节点ID
        - target_id: 目标节点ID
        - relation_type: 关系类型
        - strength: 关系强度（可选，默认1.0）
        
        返回：
        - relation: 添加的知识关系
        """
        from .models import KnowledgeRelation, KnowledgeGraph, KnowledgeNode
        
        graph_id = request.data.get('graph_id')
        source_id = request.data.get('source_id')
        target_id = request.data.get('target_id')
        relation_type = request.data.get('relation_type')
        strength = request.data.get('strength', 1.0)
        
        if not graph_id or not source_id or not target_id or not relation_type:
            return Response({'error': 'graph_id、source_id、target_id和relation_type不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            graph = KnowledgeGraph.objects.get(id=graph_id)
            source = KnowledgeNode.objects.get(id=source_id)
            target = KnowledgeNode.objects.get(id=target_id)
            
            relation = KnowledgeRelation.objects.create(
                graph=graph,
                source=source,
                target=target,
                relation_type=relation_type,
                strength=strength
            )
            
            return Response({
                "id": relation.id,
                "source": relation.source.id,
                "target": relation.target.id,
                "relation_type": relation.relation_type,
                "strength": relation.strength,
                "source_title": relation.source.title,
                "target_title": relation.target.title
            })
        except KnowledgeGraph.DoesNotExist:
            return Response({'error': '知识图谱不存在'}, status=status.HTTP_404_NOT_FOUND)
        except KnowledgeNode.DoesNotExist:
            return Response({'error': '源节点或目标节点不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @decorators.api_view(['POST'])
    @decorators.permission_classes([IsAuthenticated])
    def auto_build(request):
        """自动构建知识图谱
        
        请求参数：
        - documents: 文档列表，每个文档包含 title 和 content
        - graph_name: 知识图谱名称（可选）
        - merge_existing: 是否与现有图谱合并（可选，默认True）
        - use_llm: 是否使用大模型辅助（可选，默认True）
        
        返回：
        - graph_id: 新建或更新的知识图谱ID
        - stats: 构建统计信息
        """
        from .knowledge_graph_auto_builder import KnowledgeGraphAutoBuilder
        
        documents = request.data.get('documents', [])
        graph_name = request.data.get('graph_name')
        merge_existing = request.data.get('merge_existing', True)
        use_llm = request.data.get('use_llm', True)
        
        if not documents:
            return Response({'error': '文档列表不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 初始化自动构建器
            builder = KnowledgeGraphAutoBuilder(use_llm=use_llm)
            
            # 执行构建
            stats = builder.build_from_documents(
                documents=documents,
                graph_name=graph_name,
                merge_existing=merge_existing
            )
            
            return Response({
                'graph_id': builder.graph_id,
                'stats': stats,
                'message': '知识图谱自动构建完成'
            })
        except Exception as e:
            logger.error(f"自动构建知识图谱失败: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @decorators.api_view(['POST'])
    @decorators.permission_classes([IsAuthenticated])
    def incremental_build(request):
        """增量构建知识图谱
        
        请求参数：
        - graph_id: 知识图谱ID
        - new_documents: 新增文档列表
        
        返回：
        - stats: 构建统计信息
        """
        from .knowledge_graph_auto_builder import KnowledgeGraphAutoBuilder
        
        graph_id = request.data.get('graph_id')
        new_documents = request.data.get('new_documents', [])
        
        if not graph_id:
            return Response({'error': 'graph_id不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not new_documents:
            return Response({'error': '新增文档列表不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 初始化自动构建器
            builder = KnowledgeGraphAutoBuilder(graph_id=graph_id, use_llm=True)
            
            # 执行增量构建
            stats = builder.build_from_documents(
                documents=new_documents,
                merge_existing=True
            )
            
            return Response({
                'stats': stats,
                'message': '知识图谱增量构建完成'
            })
        except Exception as e:
            logger.error(f"增量构建知识图谱失败: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @decorators.api_view(['GET'])
    @decorators.permission_classes([IsAuthenticated])
    def check_quality(request):
        """检查知识图谱质量
        
        查询参数：
        - graph_id: 知识图谱ID
        
        返回：
        - quality_report: 质量报告
        """
        from .knowledge_graph_auto_builder import KnowledgeGraphQualityChecker
        
        graph_id = request.query_params.get('graph_id')
        
        if not graph_id:
            # 使用默认图谱
            graph = KnowledgeGraph.objects.filter(is_active=True).first()
            if graph:
                graph_id = graph.id
            else:
                return Response({'error': '没有可用的知识图谱'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            checker = KnowledgeGraphQualityChecker(int(graph_id))
            report = checker.generate_quality_report()
            return Response(report)
        except Exception as e:
            logger.error(f"检查知识图谱质量失败: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @decorators.api_view(['POST'])
    @decorators.permission_classes([IsAuthenticated])
    def build_from_texts(request):
        """从文本语料库构建知识图谱（简化接口）
        
        请求参数：
        - texts: 文本列表
        - graph_name: 知识图谱名称（可选）
        
        返回：
        - graph_id: 新建知识图谱ID
        - stats: 构建统计信息
        """
        from .knowledge_graph_auto_builder import build_knowledge_graph_from_texts
        
        texts = request.data.get('texts', [])
        graph_name = request.data.get('graph_name')
        
        if not texts:
            return Response({'error': '文本列表不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            stats = build_knowledge_graph_from_texts(texts, graph_name)
            return Response({
                'stats': stats,
                'message': '知识图谱构建完成'
            })
        except Exception as e:
            logger.error(f"从文本构建知识图谱失败: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 大模型相关视图
class LLMAPIView(APIView):
    """大模型API"""
    permission_classes = [IsAuthenticated]
    
    @decorators.api_view(['POST'])
    @decorators.permission_classes([IsAuthenticated])
    def generate_response(request):
        """调用大模型生成响应
        
        请求参数：
        - prompt: 提示词
        - temperature: 温度参数（可选，默认0.7）
        - max_tokens: 最大tokens数（可选，默认1000）
        - context: 上下文信息（可选）
        
        返回：
        - response: 大模型生成的响应
        """
        from .llm_integration import LLMService
        
        prompt = request.data.get('prompt', '')
        temperature = request.data.get('temperature', 0.7)
        max_tokens = request.data.get('max_tokens', 1000)
        context = request.data.get('context', {})
        
        if not prompt:
            return Response({'error': '提示词不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            llm_service = LLMService()
            response = llm_service.generate_response(prompt, temperature, max_tokens, context)
            return Response({'response': response})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @decorators.api_view(['POST'])
    @decorators.permission_classes([IsAuthenticated])
    def extract_knowledge(request):
        """从文本中提取知识节点
        
        请求参数：
        - text: 输入文本
        
        返回：
        - nodes: 提取的知识节点列表
        - relations: 提取的知识关系列表
        """
        from .llm_integration import LLMService
        
        text = request.data.get('text', '')
        
        if not text:
            return Response({'error': '文本不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            llm_service = LLMService()
            result = llm_service.extract_knowledge_nodes(text)
            return Response(result)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
        
        # 检查learning_style是对象还是字典
        visual_score = 0
        auditory_score = 0
        
        if hasattr(learning_style, 'visual_score'):  # 如果是LearningStyle对象
            visual_score = getattr(learning_style, 'visual_score', 0)
            auditory_score = getattr(learning_style, 'auditory_score', 0)
        else:  # 如果是字典
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
        
        # 检查learning_style是对象还是字典
        visual_score = 0
        auditory_score = 0
        kinesthetic_score = 0
        
        if hasattr(learning_style, 'visual_score'):  # 如果是LearningStyle对象
            visual_score = getattr(learning_style, 'visual_score', 0)
            auditory_score = getattr(learning_style, 'auditory_score', 0)
            kinesthetic_score = getattr(learning_style, 'kinesthetic_score', 0)
        else:  # 如果是字典
            visual_score = learning_style.get('visual_score', 0)
            auditory_score = learning_style.get('auditory_score', 0)
            kinesthetic_score = learning_style.get('kinesthetic_score', 0)
        
        if visual_score > 0.7:
            features.append("视觉学习优化")
        if auditory_score > 0.7:
            features.append("听觉学习优化")
        if kinesthetic_score > 0.7:
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
            logger.warning(f"用户 {self.request.user.username} (ID: {self.request.user.id}) 尝试越权修改笔记 {instance.id}，该笔记属于用户 {instance.user.username} (ID: {instance.user.id})")
            raise PermissionDenied(detail="您没有权限修改该笔记")
        serializer.save()
    
    def perform_destroy(self, instance):
        # 删除时确保只能删除自己的笔记
        if instance.user != self.request.user:
            logger.warning(f"用户 {self.request.user.username} (ID: {self.request.user.id}) 尝试越权删除笔记 {instance.id}，该笔记属于用户 {instance.user.username} (ID: {instance.user.id})")
            raise PermissionDenied(detail="您没有权限删除该笔记")
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
    @note_permission_required("操作")
    def toggle_favorite(self, request, pk=None):
        """切换收藏状态"""
        note = self.get_object()
        note.is_favorite = not note.is_favorite
        note.save()
        return Response({'is_favorite': note.is_favorite})
    
    @action(detail=True, methods=['get'])
    @note_permission_required("查看")
    def versions(self, request, pk=None):
        """获取笔记版本历史"""
        note = self.get_object()
        versions = note.versions.all()[:10]  # 只返回最近10个版本
        serializer = NoteVersionSerializer(versions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    @note_permission_required("恢复")
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
    @note_permission_required("分享")
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
    @note_permission_required("标记")
    def mark_as_reviewed(self, request, pk=None):
        """标记为已复习"""
        note = self.get_object()
        note.last_reviewed_at = timezone.now()
        note.save()
        return Response({'message': '已标记为已复习'})
    
    @action(detail=True, methods=['post'])
    @note_permission_required("添加")
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
    @note_permission_required("删除")
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
    @note_permission_required("添加")
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
    @note_permission_required("移除")
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
        # 使用模型中实际存在的排序字段，避免无效字段导致的错误
        return LearningRecommendation.objects.filter(user=self.request.user).order_by('-recommended_at')
    
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
    
    @action(detail=False, methods=['post'])
    def generate_personalized_suggestions(self, request):
        """生成基于知识图谱和豆包的个性化学习建议
        
        请求参数：
        - knowledge_node_ids: 相关知识节点ID列表（可选）
        - learning_goal: 学习目标（可选）
        - context: 上下文信息（可选）
        
        返回：
        - suggestions: 个性化学习建议列表
        - explanation: 建议生成说明
        """
        from .llm_integration import LLMService
        from .personalized_learning_path import PersonalizedLearningPathGenerator
        
        try:
            # 获取请求参数
            knowledge_node_ids = request.data.get('knowledge_node_ids', [])
            learning_goal = request.data.get('learning_goal', '')
            context = request.data.get('context', {})
            
            # 初始化服务
            path_generator = PersonalizedLearningPathGenerator()
            llm_service = LLMService()
            
            # 获取用户画像
            user_profile = path_generator._get_user_profile(request.user)
            
            # 获取相关知识节点信息
            knowledge_nodes = []
            if knowledge_node_ids:
                from .models import KnowledgeNode
                knowledge_nodes = KnowledgeNode.objects.filter(id__in=knowledge_node_ids)
            
            # 构建上下文信息
            context_info = {
                'user_profile': user_profile,
                'knowledge_nodes': [{
                    'id': node.id,
                    'title': node.title,
                    'type': node.type,
                    'difficulty': node.difficulty,
                    'description': node.description
                } for node in knowledge_nodes],
                'learning_goal': learning_goal
            }
            
            # 构建知识图谱
            professional_group = user_profile.get('professional_group', 'science')
            path_generator.kg_engine.build_knowledge_graph(professional_group=professional_group)
            
            # 生成学习路径
            max_nodes = 10
            learning_path = path_generator.kg_engine.get_recommended_path(user_profile, learning_goal, max_nodes)
            
            # 如果没有生成路径，使用默认路径
            if not learning_path:
                learning_path = path_generator._create_default_path(learning_goal, max_nodes)
            
            # 生成个性化建议
            suggestions = path_generator._generate_personalized_suggestions(learning_path, user_profile)
            
            # 确保建议数量足够
            if len(suggestions) < 5:
                # 构建详细的提示词
                prompt = f"""你是一位专业的教育顾问，请根据用户的学习情况生成个性化学习建议：
                
                用户画像：
                - 专业：{user_profile.get('professional_group', '未指定')}
                - 知识水平：{user_profile.get('knowledge_level', '中级')}
                - 学习风格：{user_profile.get('learning_style', {})}
                - 兴趣领域：{user_profile.get('interest_areas', [])}
                - 当前知识：{user_profile.get('current_knowledge', [])}
                - 薄弱知识点：{user_profile.get('weak_knowledge', [])}
                
                学习路径：
                {chr(10).join([f"{i+1}. {node['title']}（{node['type']}，难度：{node['difficulty']}）：{node['description']}" for i, node in enumerate(learning_path)])}
                
                学习目标：{learning_goal}
                
                请生成8条具体、可操作的个性化学习建议，每条建议以"建议"开头，涵盖不同方面（学习方法、资源选择、时间管理等）。
                """
                
                # 调用豆包大模型
                llm_suggestions = llm_service.generate_response(prompt, temperature=0.7, max_tokens=1500)
                
                # 解析建议
                llm_suggestions_list = []
                for line in llm_suggestions.strip().split('\n'):
                    if line.startswith('建议'):
                        llm_suggestions_list.append(line.strip())
                
                # 合并建议
                suggestions = list(set(suggestions + llm_suggestions_list))[:8]
            
            return Response({
                'suggestions': suggestions,
                'explanation': '基于您的知识图谱和学习情况，结合AI生成的个性化学习建议',
                'user_profile': user_profile
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            print(f"生成个性化建议失败: {e}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_personalized_features(self, roadmap, user_profile):
        """获取路线图的个性化特征"""
        features = []
        
        # 基于学习风格推荐特征
        learning_style = user_profile.get('learning_style', {})
        
        # 检查learning_style是对象还是字典
        visual_score = 0
        auditory_score = 0
        reading_score = 0
        kinesthetic_score = 0
        
        if hasattr(learning_style, 'visual_score'):  # 如果是LearningStyle对象
            visual_score = getattr(learning_style, 'visual_score', 0)
            auditory_score = getattr(learning_style, 'auditory_score', 0)
            reading_score = getattr(learning_style, 'reading_score', 0)
            kinesthetic_score = getattr(learning_style, 'kinesthetic_score', 0)
        else:  # 如果是字典
            visual_score = learning_style.get('visual_score', 0)
            auditory_score = learning_style.get('auditory_score', 0)
            reading_score = learning_style.get('reading_score', 0)
            kinesthetic_score = learning_style.get('kinesthetic_score', 0)
        
        if visual_score > 0.7:
            features.append('视觉化学习资源')
        if auditory_score > 0.7:
            features.append('音频讲解材料')
        if reading_score > 0.7:
            features.append('详细文字教程')
        if kinesthetic_score > 0.7:
            features.append('动手实践项目')
        
        # 基于专业推荐特征
        professional_group = user_profile.get('professional_group', 'science')
        if professional_group == 'business':
            features.append('商业案例分析')
        elif professional_group == 'humanities':
            features.append('人文素养拓展')
        elif professional_group == 'arts':
            features.append('创意实践结合')
        elif professional_group == 'science':
            features.append('科学实验验证')
        
        # 基于难度推荐特征
        knowledge_level = user_profile.get('knowledge_level', '中级')
        if knowledge_level == '初级':
            features.append('入门基础课程')
        elif knowledge_level == '中级':
            features.append('进阶提升课程')
        elif knowledge_level == '高级':
            features.append('高级挑战课程')
        
        return features if features else ['个性化推荐', '适合您当前水平']
    
    @action(detail=False, methods=['get'], url_path='roadmap')
    def recommend_roadmap(self, request):
        """推荐初始学习路线图，返回增强的推荐信息"""
        try:
            # 获取或构建用户画像
            try:
                engine = RecommendationEngine(request.user)
                user_profile = engine.build_user_profile()
                # 调用推荐引擎获取推荐路线图
                recommended_roadmaps = engine.recommend_roadmaps(limit=5)
            except Exception as e:
                # 如果智能推荐引擎出错，则回退到简单的基于模板的推荐，避免直接返回500
                print(f"[LearningRecommendationViewSet] 推荐引擎出错，使用回退方案: {e}")
                # 确保user_profile是一个字典，其中learning_style也是字典格式
                user_profile = {
                    "learning_style": {
                        "dominant_style": "综合型"
                    },
                    "knowledge_level": "中级",
                    "interest_areas": [],
                    "dominant_style": "综合型"
                }
                from .models import RoadmapTemplate
                roadmaps_qs = RoadmapTemplate.objects.filter(is_active=True)[:5]
                # 用路线路径本身作为“推荐结果”进行后续增强处理
                recommended_roadmaps = list(roadmaps_qs)
            
            # 增强推荐结果，添加可视化所需的额外信息
            enhanced_roadmaps = []
            for idx, recommendation in enumerate(recommended_roadmaps):
                # 获取基础推荐数据
                roadmap = getattr(recommendation, 'roadmap', None) or recommendation
                
                # 构建增强的路线图数据
                enhanced_roadmap = {
                    'id': getattr(roadmap, 'id', f'recommended-{idx}'),
                    'title': getattr(roadmap, 'title', '智能推荐学习路线'),
                    'description': getattr(roadmap, 'description', '根据您的学习风格和偏好定制'),
                    'difficulty_level': getattr(roadmap, 'difficulty_level', 'intermediate'),
                    'estimated_hours': getattr(roadmap, 'estimated_hours', 80),
                    'stages': getattr(roadmap, 'stages', []),
                    'tags': getattr(roadmap, 'tags', []),
                    
                    # 添加个性化推荐信息
                    'is_recommended': True,
                    # 如果有score字段则使用，否则给一个递减/递增的模拟匹配度
                    'matching_score': getattr(recommendation, 'score', 90 - idx * 3),
                    'recommendation_reason': '基于您的学习风格、知识掌握度和偏好生成的智能推荐',
                    'personalized_features': self._get_personalized_features(roadmap, user_profile)
                }
                
                # 根据学习风格添加特定的推荐理由
                learning_style = user_profile.get('learning_style', {})
                
                # 检查learning_style是对象还是字典
                visual_score = 0
                auditory_score = 0
                dominant_style = '综合型'
                
                if hasattr(learning_style, 'visual_score'):  # 如果是LearningStyle对象
                    visual_score = getattr(learning_style, 'visual_score', 0)
                    auditory_score = getattr(learning_style, 'auditory_score', 0)
                    dominant_style = getattr(learning_style, 'dominant_style', '综合型')
                else:  # 如果是字典
                    visual_score = learning_style.get('visual_score', 0)
                    auditory_score = learning_style.get('auditory_score', 0)
                    dominant_style = learning_style.get('dominant_style', '综合型')
                
                if visual_score > auditory_score:
                    enhanced_roadmap['recommendation_reason'] = f"此路线图包含丰富的视觉学习资源，非常适合您的{dominant_style}学习风格"
                elif auditory_score > visual_score:
                    enhanced_roadmap['recommendation_reason'] = f"此路线图提供多种听觉学习材料，与您的{dominant_style}学习风格高度匹配"
                
                enhanced_roadmaps.append(enhanced_roadmap)
            
            # 准备用户画像摘要
            user_learning_style = user_profile.get('learning_style', {})
            summary_dominant_style = '综合型'
            
            if hasattr(user_learning_style, 'dominant_style'):  # 如果是LearningStyle对象
                summary_dominant_style = getattr(user_learning_style, 'dominant_style', '综合型')
            else:  # 如果是字典
                summary_dominant_style = user_learning_style.get('dominant_style', '综合型')
            
            # 返回增强的推荐结果
            return Response({
                'roadmaps': enhanced_roadmaps,
                'message': '智能推荐成功',
                'user_profile_summary': {
                    'learning_style': summary_dominant_style,
                    'knowledge_level': user_profile.get('knowledge_level', '中级'),
                    'interests': user_profile.get('interest_areas', ['基础学习'])
                }
            })
        except Exception as e:
            # 最终兜底：如果仍然出错，则返回空列表，让前端走静态数据回退逻辑，而不是500
            print(f"[LearningRecommendationViewSet] recommend_roadmap 最终兜底错误: {e}")
            return Response(
                {
                    'roadmaps': [],
                    'message': '暂时无法生成智能推荐，已返回空结果',
                    'error': str(e),
                    'user_profile_summary': {
                        'learning_style': '综合型',
                        'knowledge_level': '中级',
                        'interests': ['基础学习']
                    }
                },
                status=status.HTTP_200_OK,
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


class KnowledgeNodeViewSet(viewsets.ModelViewSet):
    """知识节点视图集"""
    queryset = KnowledgeNode.objects.all()
    serializer_class = KnowledgeNodeSerializer
    permission_classes = [AllowAny]  # 允许匿名访问，便于开发和测试
    
    def list(self, request, *args, **kwargs):
        """获取知识节点列表"""
        queryset = self.get_queryset()
        
        # 根据查询参数过滤
        professional_group = request.query_params.get('professional_group')
        if professional_group:
            queryset = queryset.filter(professional_group=professional_group)
        
        type = request.query_params.get('type')
        if type:
            queryset = queryset.filter(type=type)
        
        serializer = self.get_serializer(queryset, many=True)
        # 返回前端期望的格式
        return Response({'nodes': serializer.data})


class KnowledgeRelationViewSet(viewsets.ModelViewSet):
    """知识关系视图集"""
    queryset = KnowledgeRelation.objects.all()
    serializer_class = KnowledgeRelationSerializer
    permission_classes = [AllowAny]  # 允许匿名访问，便于开发和测试
    
    def list(self, request, *args, **kwargs):
        """获取知识关系列表"""
        queryset = self.get_queryset()
        
        serializer = self.get_serializer(queryset, many=True)
        # 返回前端期望的格式
        return Response({'relations': serializer.data})

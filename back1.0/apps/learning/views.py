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
from .models import LearningRecord, PracticeRecord, HeatmapData, WrongQuestion, RoadmapTemplate, RoadmapStage, UserLearningPath, UserPathStage, Note, NoteTag, Exercise, JupyterDocument, LearningStyle, KnowledgeMastery, LearningRecommendation, LearningPreference, KnowledgeNode, KnowledgeRelation, AIInteractionRecord
from apps.teacher.models import Class, Student, Homework, StudentHomework, Notice, StudentNoticeRead, ClassResource
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
    KnowledgeRelationSerializer,
    AIInteractionRecordSerializer,
    AIInteractionRecordCreateSerializer
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
    
    @action(detail=False, methods=['get'])
    def heatmap(self, request):
        """获取学习热力图数据"""
        try:
            user = request.user
            
            # 获取热力图数据
            heatmap_data = HeatmapData.objects.filter(user=user).order_by('date')
            
            # 使用序列化器序列化数据
            serializer = HeatmapDataSerializer(heatmap_data, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"获取学习热力图数据失败: {str(e)}")
            return Response({'error': f'获取学习热力图数据失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_queryset(self):
        # 用户只能查看自己的学习记录
        return LearningRecord.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def activity(self, request):
        """获取统一的学习活动记录（合并阅读和练习记录）"""
        try:
            # 获取当前用户
            user = request.user
            
            # 获取学习记录
            learning_records = LearningRecord.objects.filter(user=user).select_related('book', 'chapter')
            
            # 获取练习记录
            practice_records = PracticeRecord.objects.filter(user=user).select_related('book', 'chapter')
            
            # 合并活动记录
            activities = []
            
            # 添加学习记录
            for record in learning_records:
                if not record.book or not record.chapter:
                    continue
                    
                activity = {
                    'id': f'reading-{record.id}',
                    'type': 'reading',
                    'bookId': record.book.id,
                    'chapterId': record.chapter.id,
                    'bookTitle': record.book.title,
                    'chapterTitle': record.chapter.title,
                    'duration': None,
                    'status': 'completed' if record.progress >= 100 else 'inProgress',
                    'timestamp': record.last_learn_time,
                    'progress': record.progress,
                    'score': None
                }
                activities.append(activity)
            
            # 添加练习记录
            for record in practice_records:
                if not record.book or not record.chapter:
                    continue
                    
                activity = {
                    'id': f'practice-{record.id}',
                    'type': 'practice',
                    'bookId': record.book.id,
                    'chapterId': record.chapter.id,
                    'bookTitle': record.book.title,
                    'chapterTitle': record.chapter.title,
                    'duration': None,
                    'status': 'completed' if record.completed else 'inProgress',
                    'timestamp': record.completed_time or record.created_at,
                    'progress': None,
                    'score': record.score
                }
                activities.append(activity)
            
            # 按时间戳排序
            order_by = request.query_params.get('order_by', '-timestamp')
            reverse = order_by.startswith('-')
            field = order_by.lstrip('-')
            
            if field == 'timestamp':
                activities.sort(key=lambda x: x['timestamp'], reverse=reverse)
            elif field == 'bookId':
                activities.sort(key=lambda x: x['bookId'], reverse=reverse)
            elif field == 'chapterId':
                activities.sort(key=lambda x: x['chapterId'], reverse=reverse)
            elif field == 'score':
                activities.sort(key=lambda x: x['score'] or 0, reverse=reverse)
            elif field == 'progress':
                activities.sort(key=lambda x: x['progress'] or 0, reverse=reverse)
            
            # 分页
            page = self.paginate_queryset(activities)
            if page is not None:
                serializer = LearningActivitySerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = LearningActivitySerializer(activities, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"获取学习活动记录失败: {str(e)}")
            return Response({'error': f'获取学习活动记录失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # 定义为普通方法而不是action，以便直接在urls.py中使用
    def execute(self, request):
        """在线执行代码（简易沙箱：临时目录 + 超时限制）"""
        language = (request.data.get('language') or '').lower()
        code = request.data.get('code') or ''
        stdin_data = request.data.get('input') or ''
        
        if language not in ['python', 'javascript', 'java', 'c', 'html']:
            return Response({'error': '暂不支持该语言'}, status=status.HTTP_400_BAD_REQUEST)
        if not code:
            return Response({'error': '代码为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 定义decode_output函数在方法顶部
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
        
        start = time.time()
        max_time = 5
        stdout_text = ''
        stderr_text = ''
        exit_code = None
        
        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                cwd = tmpdir
                cmd = None
                
                if language == 'python':
                    filename = os.path.join(cwd, 'main.py')
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(code)
                    cmd = ['python', '-B', filename]
                elif language == 'javascript':
                    filename = os.path.join(cwd, 'main.js')
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(code)
                    cmd = ['node', filename]
                elif language == 'java':
                    filename = os.path.join(cwd, 'Main.java')
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(code)
                    compile_cmd = ['javac', 'Main.java']
                    compile_proc = subprocess.run(
                        compile_cmd,
                        cwd=cwd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=max_time // 2
                    )
                    if compile_proc.returncode != 0:
                        stderr_text = decode_output(compile_proc.stderr)
                        exit_code = compile_proc.returncode
                    else:
                        cmd = ['java', 'Main']
                elif language == 'c':
                    filename = os.path.join(cwd, 'main.c')
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(code)
                    compile_cmd = ['gcc', 'main.c', '-o', 'main.exe']
                    compile_proc = subprocess.run(
                        compile_cmd,
                        cwd=cwd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        timeout=max_time // 2
                    )
                    if compile_proc.returncode != 0:
                        stderr_text = decode_output(compile_proc.stderr)
                        exit_code = compile_proc.returncode
                    else:
                        cmd = ['./main.exe']
                elif language == 'html':
                    filename = os.path.join(cwd, 'index.html')
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(code)
                    stdout_text = 'HTML文件已生成，在实际环境中可以通过浏览器打开查看'
                    exit_code = 0
                    cmd = None
                
                if cmd:
                    # 设置环境变量，确保Python使用UTF-8编码输出
                    env = os.environ.copy()
                    env['PYTHONIOENCODING'] = 'utf-8'
                    proc = subprocess.run(
                        cmd,
                        input=stdin_data.encode('utf-8'),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=cwd,
                        timeout=max_time,
                        env=env  # 使用修改后的环境变量
                    )
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
            elif language == 'python' and any(term in stderr_text for term in ['SyntaxError:', 'IndentationError:', 'NameError: name']):
                error_type = 'compile_error'
                error_code = 'COMPILE_ERROR'
                error_message = '语法错误'
            
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


# 独立的代码执行视图函数，允许匿名访问
from rest_framework.decorators import api_view, permission_classes, authentication_classes
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def execute_code(request):
    """在线执行代码（简易沙箱：临时目录 + 超时限制）"""
    language = (request.data.get('language') or '').lower()
    code = request.data.get('code') or ''
    stdin_data = request.data.get('input') or ''
    
    if language not in ['python', 'javascript', 'java', 'c', 'html']:
        return Response({'error': '暂不支持该语言'}, status=status.HTTP_400_BAD_REQUEST)
    if not code:
        return Response({'error': '代码为空'}, status=status.HTTP_400_BAD_REQUEST)
    
    # 定义decode_output函数在方法顶部
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
    
    start = time.time()
    max_time = 5
    stdout_text = ''
    stderr_text = ''
    exit_code = None
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            cwd = tmpdir
            cmd = None
            
            if language == 'python':
                filename = os.path.join(cwd, 'main.py')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                cmd = ['python', '-B', filename]
            elif language == 'javascript':
                filename = os.path.join(cwd, 'main.js')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                cmd = ['node', filename]
            elif language == 'java':
                filename = os.path.join(cwd, 'Main.java')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                compile_cmd = ['javac', 'Main.java']
                compile_proc = subprocess.run(
                    compile_cmd,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=max_time // 2
                )
                if compile_proc.returncode != 0:
                    stderr_text = decode_output(compile_proc.stderr)
                    exit_code = compile_proc.returncode
                else:
                    cmd = ['java', 'Main']
            elif language == 'c':
                filename = os.path.join(cwd, 'main.c')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                compile_cmd = ['gcc', 'main.c', '-o', 'main.exe']
                compile_proc = subprocess.run(
                    compile_cmd,
                    cwd=cwd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=max_time // 2
                )
                if compile_proc.returncode != 0:
                    stderr_text = decode_output(compile_proc.stderr)
                    exit_code = compile_proc.returncode
                else:
                    cmd = ['./main.exe']
            elif language == 'html':
                filename = os.path.join(cwd, 'index.html')
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(code)
                stdout_text = 'HTML文件已生成，在实际环境中可以通过浏览器打开查看'
                exit_code = 0
                cmd = None
            
            if cmd:
                # 设置环境变量，确保Python使用UTF-8编码输出
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                proc = subprocess.run(
                    cmd,
                    input=stdin_data.encode('utf-8'),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=cwd,
                    timeout=max_time,
                    env=env  # 使用修改后的环境变量
                )
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
        elif language == 'python' and any(term in stderr_text for term in ['SyntaxError:', 'IndentationError:', 'NameError: name']):
            error_type = 'compile_error'
            error_code = 'COMPILE_ERROR'
            error_message = '语法错误'
        
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
    permission_classes = [AllowAny]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 初始化个性化学习路径生成器
        from .personalized_learning_path import PersonalizedLearningPathGenerator
        self.path_generator = PersonalizedLearningPathGenerator()
    
    @decorators.api_view(['POST'])
    @decorators.permission_classes([AllowAny])
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
        """
        from .models import KnowledgeNode
        
        data = request.data
        try:
            node = KnowledgeNode.objects.create(
                title=data.get('title'),
                type=data.get('type', 'concept'),
                level=data.get('level', 1),
                difficulty=data.get('difficulty', 1.0),
                importance=data.get('importance', 5.0),
                description=data.get('description', ''),
                professional_group=data.get('professional_group', 'science'),
                tags=data.get('tags', []),
                graph_id=data.get('graph_id')
            )
            return Response({
                'id': node.id,
                'title': node.title,
                'type': node.type,
                'level': node.level,
                'difficulty': node.difficulty,
                'importance': node.importance,
                'description': node.description,
                'professional_group': node.professional_group,
                'tags': node.tags,
                'graph_id': node.graph_id
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class NoteViewSet(viewsets.ModelViewSet):
    """笔记视图集"""
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        # 用户只能查看自己的笔记
        return Note.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'list':
            return NoteListSerializer
        elif self.action == 'retrieve':
            return NoteDetailSerializer
        elif self.action == 'create':
            return NoteCreateSerializer
        elif self.action == 'update':
            return NoteUpdateSerializer
        return NoteSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @note_permission_required('更新')
    def perform_update(self, serializer):
        serializer.save(updated_at=timezone.now())
    
    @note_permission_required('删除')
    def perform_destroy(self, instance):
        instance.delete()
    
    @action(detail=False, methods=['get'])
    def search(self, request):
        """搜索笔记"""
        keyword = request.query_params.get('keyword', '')
        if not keyword:
            return Response([], status=status.HTTP_200_OK)
        
        # 搜索标题和内容包含关键字的笔记
        notes = Note.objects.filter(
            models.Q(user=request.user) & (models.Q(title__icontains=keyword) | models.Q(content__icontains=keyword))
        ).order_by('-updated_at')
        
        serializer = NoteListSerializer(notes, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """获取最近更新的笔记"""
        notes = Note.objects.filter(user=request.user).order_by('-updated_at')[:10]
        serializer = NoteListSerializer(notes, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_tag(self, request, pk=None):
        """为笔记添加标签"""
        note = self.get_object()
        tag_name = request.data.get('tag_name')
        
        if not tag_name:
            return Response({'error': '标签名称不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取或创建标签
        tag, created = NoteTag.objects.get_or_create(user=request.user, name=tag_name)
        
        # 将标签添加到笔记
        note.tags.add(tag)
        
        return Response({'success': True, 'tag_id': tag.id})
    
    @action(detail=True, methods=['post'])
    def remove_tag(self, request, pk=None):
        """从笔记移除标签"""
        note = self.get_object()
        tag_id = request.data.get('tag_id')
        
        if not tag_id:
            return Response({'error': '标签ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            tag = NoteTag.objects.get(id=tag_id, user=request.user)
            note.tags.remove(tag)
            return Response({'success': True})
        except NoteTag.DoesNotExist:
            return Response({'error': '标签不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def tags(self, request):
        """获取用户的所有标签"""
        tags = NoteTag.objects.filter(user=request.user).order_by('name')
        serializer = NoteTagSerializer(tags, many=True)
        return Response(serializer.data)


class JupyterDocumentViewSet(viewsets.ModelViewSet):
    """Jupyter文档视图集"""
    queryset = JupyterDocument.objects.all()
    serializer_class = JupyterDocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 用户只能查看自己的Jupyter文档
        return JupyterDocument.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_document(self, request):
        """创建Jupyter文档"""
        serializer = CreateJupyterDocumentSerializer(data=request.data)
        if serializer.is_valid():
            document = serializer.save(user=request.user)
            return Response({
                'id': document.id,
                'title': document.title,
                'content': document.content,
                'created_at': document.created_at,
                'updated_at': document.updated_at
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'])
    def update_document(self, request, pk=None):
        """更新Jupyter文档"""
        document = self.get_object()
        serializer = UpdateJupyterDocumentSerializer(document, data=request.data)
        if serializer.is_valid():
            updated_document = serializer.save()
            return Response({
                'id': updated_document.id,
                'title': updated_document.title,
                'content': updated_document.content,
                'updated_at': updated_document.updated_at
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LearningStyleViewSet(viewsets.ModelViewSet):
    """学习风格视图集"""
    queryset = LearningStyle.objects.all()
    serializer_class = LearningStyleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 用户只能查看自己的学习风格
        return LearningStyle.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['put'])
    def update_style(self, request):
        """更新学习风格"""
        user = request.user
        serializer = UpdateLearningStyleSerializer(data=request.data)
        
        if serializer.is_valid():
            # 获取或创建学习风格记录
            learning_style, created = LearningStyle.objects.get_or_create(user=user)
            
            # 更新学习风格
            learning_style.visual = serializer.validated_data.get('visual', learning_style.visual)
            learning_style.auditory = serializer.validated_data.get('auditory', learning_style.auditory)
            learning_style.kinesthetic = serializer.validated_data.get('kinesthetic', learning_style.kinesthetic)
            learning_style.read_write = serializer.validated_data.get('read_write', learning_style.read_write)
            learning_style.social = serializer.validated_data.get('social', learning_style.social)
            learning_style.solitary = serializer.validated_data.get('solitary', learning_style.solitary)
            learning_style.save()
            
            return Response({
                'success': True,
                'learning_style': LearningStyleSerializer(learning_style).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class KnowledgeMasteryViewSet(viewsets.ModelViewSet):
    """知识掌握度视图集"""
    queryset = KnowledgeMastery.objects.all()
    serializer_class = KnowledgeMasterySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 用户只能查看自己的知识掌握度
        return KnowledgeMastery.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['put'])
    def update_mastery(self, request):
        """更新知识掌握度"""
        user = request.user
        serializer = UpdateKnowledgeMasterySerializer(data=request.data)
        
        if serializer.is_valid():
            knowledge_id = serializer.validated_data['knowledge_id']
            mastery_level = serializer.validated_data['mastery_level']
            
            # 获取或创建知识掌握度记录
            knowledge_mastery, created = KnowledgeMastery.objects.update_or_create(
                user=user,
                knowledge_id=knowledge_id,
                defaults={'mastery_level': mastery_level}
            )
            
            return Response({
                'success': True,
                'knowledge_mastery': KnowledgeMasterySerializer(knowledge_mastery).data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LearningRecommendationViewSet(viewsets.ModelViewSet):
    """学习推荐视图集"""
    queryset = LearningRecommendation.objects.all()
    serializer_class = LearningRecommendationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 用户只能查看自己的学习推荐
        return LearningRecommendation.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def feedback(self, request):
        """反馈学习推荐"""
        serializer = FeedbackRecommendationSerializer(data=request.data)
        if serializer.is_valid():
            recommendation_id = serializer.validated_data['recommendation_id']
            feedback = serializer.validated_data['feedback']
            
            try:
                recommendation = LearningRecommendation.objects.get(id=recommendation_id, user=request.user)
                recommendation.feedback = feedback
                recommendation.save()
                return Response({'success': True})
            except LearningRecommendation.DoesNotExist:
                return Response({'error': '学习推荐不存在'}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LearningPreferenceViewSet(viewsets.ModelViewSet):
    """学习偏好视图集"""
    queryset = LearningPreference.objects.all()
    serializer_class = LearningPreferenceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 用户只能查看自己的学习偏好
        return LearningPreference.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['put'])
    def update_preference(self, request):
        """更新学习偏好"""
        user = request.user
        data = request.data
        
        # 获取或创建学习偏好记录
        learning_preference, created = LearningPreference.objects.get_or_create(user=user)
        
        # 更新学习偏好
        if 'preferred_language' in data:
            learning_preference.preferred_language = data['preferred_language']
        if 'preferred_difficulty' in data:
            learning_preference.preferred_difficulty = data['preferred_difficulty']
        if 'learning_goal' in data:
            learning_preference.learning_goal = data['learning_goal']
        if 'preferred_content_type' in data:
            learning_preference.preferred_content_type = data['preferred_content_type']
        
        learning_preference.save()
        
        return Response({
            'success': True,
            'learning_preference': LearningPreferenceSerializer(learning_preference).data
        })


class KnowledgeNodeViewSet(viewsets.ModelViewSet):
    """知识节点视图集"""
    queryset = KnowledgeNode.objects.all()
    serializer_class = KnowledgeNodeSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 用户只能查看公开的或自己创建的知识节点
        return KnowledgeNode.objects.filter(models.Q(is_public=True) | models.Q(creator=self.request.user))
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class KnowledgeRelationViewSet(viewsets.ModelViewSet):
    """知识关系视图集"""
    queryset = KnowledgeRelation.objects.all()
    serializer_class = KnowledgeRelationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 用户只能查看公开的或自己创建的知识关系
        return KnowledgeRelation.objects.filter(models.Q(is_public=True) | models.Q(creator=self.request.user))
    
    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

@decorators.api_view(['GET'])
@decorators.permission_classes([IsAuthenticated])
def get_recommended_roadmaps(request):
    """获取推荐的学习路线图
    
    返回：
    - roadmaps: 推荐路线图列表
    """
    from .recommendation_engine import RecommendationEngine
    
    # 创建推荐引擎实例
    recommendation_engine = RecommendationEngine(request.user)
    
    # 获取推荐路线图
    recommended_roadmaps = recommendation_engine.recommend_roadmaps(limit=5)
    
    # 序列化结果
    serialized_roadmaps = []
    for recommendation in recommended_roadmaps:
        roadmap_data = {
            'id': recommendation.roadmap.id if hasattr(recommendation, 'roadmap') else recommendation.id,
            'title': recommendation.roadmap.title if hasattr(recommendation, 'roadmap') else recommendation.title,
            'description': recommendation.roadmap.description if hasattr(recommendation, 'roadmap') else recommendation.description,
            'difficulty_level': recommendation.roadmap.difficulty_level if hasattr(recommendation, 'roadmap') else recommendation.difficulty_level,
            'estimated_hours': recommendation.roadmap.estimated_hours if hasattr(recommendation, 'roadmap') else recommendation.estimated_hours,
            'tags': recommendation.roadmap.tags if hasattr(recommendation, 'roadmap') else recommendation.tags,
            'is_recommended': True,
            'recommendation_reason': recommendation.reason if hasattr(recommendation, 'reason') else '智能推荐路线图',
            'matching_score': recommendation.score if hasattr(recommendation, 'score') else 90
        }
        serialized_roadmaps.append(roadmap_data)
    
    return Response({'roadmaps': serialized_roadmaps})


class AIInteractionRecordViewSet(viewsets.ModelViewSet):
    """AI交互记录视图集"""
    queryset = AIInteractionRecord.objects.all()
    serializer_class = AIInteractionRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # 用户只能查看自己的AI交互记录
        return AIInteractionRecord.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def create_interaction(self, request):
        """创建AI交互记录"""
        serializer = AIInteractionRecordCreateSerializer(data=request.data)
        if serializer.is_valid():
            interaction = serializer.save(user=request.user)
            return Response({
                'id': interaction.id,
                'user_query': interaction.user_query,
                'ai_response': interaction.ai_response,
                'created_at': interaction.created_at
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

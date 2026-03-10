# -*- coding: utf-8 -*-
"""审核模块视图"""
import logging
from django.utils import timezone
from django.db.models import Count, Q
from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import ReviewTask, ManualReviewRecord, AIReviewRecord, WorkflowLog, ReviewRuleConfig, BookEditHistory, TeacherProfile
from .permissions import IsReviewer, ReviewTaskAccessControl, CanAccessContent
from .serializers import (
    ReviewTaskListSerializer, ReviewTaskDetailSerializer,
    ManualReviewRecordListSerializer, ManualReviewRecordDetailSerializer,
    ManualReviewCreateSerializer, AIReviewRecordSerializer,
    WorkflowLogSerializer, ReviewRuleConfigSerializer, TaskStatsSerializer,
    BookEditHistorySerializer, TeacherProfileSerializer,
    BookListSerializer, BookDetailSerializer, BookVersionSerializer
)
from .ai_review import run_ai_review
from apps.books.models import Book, BookVersion

logger = logging.getLogger(__name__)


class ReviewTaskViewSet(viewsets.ModelViewSet):
    """审核任务视图集"""
    permission_classes = [IsAuthenticated, ReviewTaskAccessControl]
    
    def get_queryset(self):
        queryset = ReviewTask.objects.all()
        
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        task_type = self.request.query_params.get('task_type')
        if task_type:
            queryset = queryset.filter(task_type=task_type)
        
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=int(priority))
        
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(book_title__icontains=search) | 
                Q(book_author__icontains=search)
            )
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ReviewTaskDetailSerializer
        return ReviewTaskListSerializer
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取任务统计"""
        user = request.user
        
        total = ReviewTask.objects.count()
        pending = ReviewTask.objects.filter(status='pending').count()
        in_review = ReviewTask.objects.filter(status='in_review').count()
        approved = ReviewTask.objects.filter(status='approved').count()
        rejected = ReviewTask.objects.filter(status='rejected').count()
        
        today = timezone.now().date()
        today_reviewed = ManualReviewRecord.objects.filter(
            reviewer=user,
            completed_at__date=today
        ).count()
        
        my_pending = ReviewTask.objects.filter(
            assigned_reviewer=user,
            status__in=['pending', 'in_review']
        ).count()
        
        my_completed = ManualReviewRecord.objects.filter(reviewer=user).count()
        
        stats = {
            'total': total,
            'pending': pending,
            'in_review': in_review,
            'approved': approved,
            'rejected': rejected,
            'today_reviewed': today_reviewed,
            'my_pending': my_pending,
            'my_completed': my_completed,
        }
        
        serializer = TaskStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def claim(self, request, pk=None):
        """认领任务"""
        task = self.get_object()
        
        if task.status != 'pending':
            return Response({'error': '该任务已被处理'}, status=status.HTTP_400_BAD_REQUEST)
        
        if task.assigned_reviewer and task.assigned_reviewer != request.user:
            return Response({'error': '该任务已被其他人认领'}, status=status.HTTP_400_BAD_REQUEST)
        
        task.assigned_reviewer = request.user
        task.status = 'in_review'
        task.save()
        
        WorkflowLog.objects.create(
            task=task,
            action='claimed',
            actor=request.user,
            actor_type='reviewer',
            from_status='pending',
            to_status='in_review',
            comment=f'{request.user.username}认领了任务'
        )
        
        return Response({'message': '认领成功', 'task_id': task.id})
    
    @action(detail=True, methods=['post'])
    def release(self, request, pk=None):
        """释放任务"""
        task = self.get_object()
        
        if task.assigned_reviewer != request.user:
            return Response({'error': '您没有权限释放此任务'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = task.status
        task.assigned_reviewer = None
        task.status = 'pending'
        task.save()
        
        WorkflowLog.objects.create(
            task=task,
            action='released',
            actor=request.user,
            actor_type='reviewer',
            from_status=old_status,
            to_status='pending',
            comment=f'{request.user.username}释放了任务'
        )
        
        return Response({'message': '释放成功'})
    
    @action(detail=True, methods=['post'])
    def trigger_ai_review(self, request, pk=None):
        """触发AI审核"""
        task = self.get_object()
        
        try:
            book_data = {
                'title': task.book_title,
                'author': task.book_author,
                'description': task.description or '',
            }
            
            chapters_data = []
            
            ai_record = run_ai_review(task, book_data, chapters_data)
            
            return Response({
                'message': 'AI审核完成',
                'ai_record': AIReviewRecordSerializer(ai_record).data
            })
        except Exception as e:
            logger.error(f'AI审核失败: {str(e)}')
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """获取任务日志"""
        task = self.get_object()
        logs = task.workflow_logs.all()[:50]
        serializer = WorkflowLogSerializer(logs, many=True)
        return Response(serializer.data)


class ManualReviewViewSet(viewsets.ModelViewSet):
    """人工审核记录视图集"""
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = ManualReviewRecord.objects.all()
        
        task_id = self.request.query_params.get('task')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ManualReviewCreateSerializer
        if self.action == 'retrieve':
            return ManualReviewRecordDetailSerializer
        return ManualReviewRecordListSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        task_id = request.data.get('task_id')
        if not task_id:
            return Response({'error': '缺少task_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            task = ReviewTask.objects.get(pk=task_id)
        except ReviewTask.DoesNotExist:
            return Response({'error': '任务不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        if task.assigned_reviewer != request.user:
            return Response({'error': '您没有权限审核此任务'}, status=status.HTTP_403_FORBIDDEN)
        
        existing_record = ManualReviewRecord.objects.filter(
            task=task,
            reviewer=request.user
        ).first()
        
        if existing_record:
            return Response({'error': '您已经审核过此任务'}, status=status.HTTP_400_BAD_REQUEST)
        
        record = ManualReviewRecord.objects.create(
            task=task,
            reviewer=request.user,
            started_at=task.updated_at,
            completed_at=timezone.now(),
            **serializer.validated_data
        )
        
        duration = (record.completed_at - record.started_at).total_seconds() / 60
        record.review_duration = int(duration)
        record.save()
        
        decision = serializer.validated_data['decision']
        old_status = task.status
        
        if decision == 'approved':
            task.status = 'approved'
        elif decision == 'rejected':
            task.status = 'rejected'
        else:
            task.status = 'pending'
        
        task.save()
        
        WorkflowLog.objects.create(
            task=task,
            action='approved' if decision == 'approved' else 'rejected',
            actor=request.user,
            actor_type='reviewer',
            from_status=old_status,
            to_status=task.status,
            comment=serializer.validated_data.get('overall_comment', '')
        )
        
        return Response(
            ManualReviewRecordDetailSerializer(record).data,
            status=status.HTTP_201_CREATED
        )


class AIReviewViewSet(viewsets.ReadOnlyModelViewSet):
    """AI审核记录视图集"""
    queryset = AIReviewRecord.objects.all()
    serializer_class = AIReviewRecordSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = AIReviewRecord.objects.all()
        
        task_id = self.request.query_params.get('task')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        
        return queryset


class WorkflowLogViewSet(viewsets.ReadOnlyModelViewSet):
    """审核流程日志视图集"""
    queryset = WorkflowLog.objects.all()
    serializer_class = WorkflowLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = WorkflowLog.objects.all()
        
        task_id = self.request.query_params.get('task')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        return queryset


class ReviewRuleConfigViewSet(viewsets.ModelViewSet):
    """审核规则配置视图集"""
    queryset = ReviewRuleConfig.objects.all()
    serializer_class = ReviewRuleConfigSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = ReviewRuleConfig.objects.all()
        
        rule_type = self.request.query_params.get('rule_type')
        if rule_type:
            queryset = queryset.filter(rule_type=rule_type)
        
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset


# 认证相关视图函数
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from apps.users.models import User


@api_view(['POST'])
@permission_classes([AllowAny])
def review_login(request):
    """审核端用户登录"""
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': '请提供用户名和密码'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': '用户名或密码错误'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # 检查用户角色是否为审核员
    if user.role != 'reviewer':
        return Response(
            {'error': '您没有审核员权限'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # 获取或创建token
    token, created = Token.objects.get_or_create(user=user)
    
    return Response({
        'token': token.key,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'name': getattr(user, 'name', user.username),
        }
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def review_register(request):
    """审核端用户注册"""
    data = request.data
    
    # 验证必填字段
    required_fields = ['username', 'password', 'email']
    for field in required_fields:
        if not data.get(field):
            return Response(
                {field: f'{field}为必填项'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # 检查用户名是否已存在
    if User.objects.filter(username=data['username']).exists():
        return Response(
            {'username': '该用户名已被注册'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # 检查邮箱是否已存在
    if User.objects.filter(email=data['email']).exists():
        return Response(
            {'email': '该邮箱已被注册'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # 创建用户
        user = User.objects.create_user(
            username=data['username'],
            password=data['password'],
            email=data['email'],
            role='reviewer'
        )
        
        # 设置可选字段
        if 'name' in data:
            user.name = data['name']
            user.save()
        
        # 创建token
        token = Token.objects.create(user=user)
        
        return Response({
            'message': '注册成功',
            'token': token.key,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'name': getattr(user, 'name', user.username),
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': f'注册失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def review_logout(request):
    """审核端用户登出"""
    try:
        # 删除用户的token
        request.user.auth_token.delete()
        return Response({'message': '登出成功'})
    except:
        return Response({'message': '登出成功'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_review_profile(request):
    """获取审核端用户信息"""
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
        'name': getattr(user, 'name', user.username),
    })


class BookEditHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """教材修改历史视图集"""
    serializer_class = BookEditHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = BookEditHistory.objects.all()
        
        # 按教材ID筛选
        book_id = self.request.query_params.get('book_id')
        if book_id:
            queryset = queryset.filter(book_id=book_id)
        
        # 按任务ID筛选
        task_id = self.request.query_params.get('task_id')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        
        # 按操作类型筛选
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        # 按操作人筛选
        actor_id = self.request.query_params.get('actor_id')
        if actor_id:
            queryset = queryset.filter(actor_id=actor_id)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_book(self, request):
        """获取指定教材的修改历史"""
        book_id = request.query_params.get('book_id')
        if not book_id:
            return Response({'error': '请提供book_id参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        history = BookEditHistory.objects.filter(book_id=book_id)[:50]
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)


class TeacherProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """教师档案视图集"""
    queryset = TeacherProfile.objects.all()
    serializer_class = TeacherProfileSerializer
    permission_classes = [IsAuthenticated, CanAccessContent]
    
    def get_queryset(self):
        queryset = TeacherProfile.objects.all()
        
        # 按部门筛选
        department = self.request.query_params.get('department')
        if department:
            queryset = queryset.filter(department__icontains=department)
        
        # 按姓名筛选
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__icontains=name)
        
        # 按工号筛选
        employee_id = self.request.query_params.get('employee_id')
        if employee_id:
            queryset = queryset.filter(employee_id__icontains=employee_id)
        
        # 只显示在职教师
        if self.request.query_params.get('active_only') == 'true':
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """获取教师教材统计信息"""
        teacher = self.get_object()
        return Response({
            'teacher_id': teacher.id,
            'name': teacher.name,
            'employee_id': teacher.employee_id,
            'stats': {
                'total_uploaded': teacher.total_uploaded_books,
                'total_modified': teacher.total_modified_books,
                'approved': teacher.approved_books,
                'rejected': teacher.rejected_books,
                'approval_rate': round(
                    teacher.approved_books / (teacher.approved_books + teacher.rejected_books) * 100, 2
                ) if (teacher.approved_books + teacher.rejected_books) > 0 else 0
            }
        })
    
    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        """获取教师相关的教材列表"""
        teacher = self.get_object()
        
        # 获取该教师上传或修改的教材审核任务
        tasks = ReviewTask.objects.filter(
            Q(submitted_by_id=teacher.user_id) |
            Q(modified_by_id=teacher.user_id) |
            Q(original_uploader_id=teacher.user_id)
        ).order_by('-created_at')[:20]
        
        serializer = ReviewTaskListSerializer(tasks, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, CanAccessContent])
def get_book_metadata(request, book_id):
    """
    获取教材元数据（审核员可访问）
    
    返回教材的基本信息和元数据，不包含敏感内容
    """
    try:
        # 这里应该从教材提供者端获取教材信息
        # 暂时返回模拟数据
        return Response({
            'book_id': book_id,
            'access_level': 'metadata_only',
            'message': '审核员只能访问教材元数据，无法查看正文内容',
            'accessible_fields': [
                'title', 'author', 'version', 'word_count', 
                'chapter_count', 'description', 'category', 'tags'
            ],
            'restricted_fields': [
                'content', 'chapter_content', 'code_examples', 
                'attachments', 'full_text'
            ]
        })
    except Exception as e:
        return Response(
            {'error': f'获取教材信息失败: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    """教材视图集（审核端 - 只读）"""
    permission_classes = [IsAuthenticated, CanAccessContent]
    pagination_class = PageNumberPagination
    
    def get_queryset(self):
        queryset = Book.objects.all()
        
        # 搜索功能
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(author__icontains=search) |
                Q(description__icontains=search)
            )
        
        # 状态筛选
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # 分类筛选
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(categories__name=category)
        
        # 排序
        ordering = self.request.query_params.get('ordering', '-created_at')
        queryset = queryset.order_by(ordering)
        
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BookDetailSerializer
        return BookListSerializer
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """获取教材修改历史"""
        book = self.get_object()
        
        # 获取审核端的修改历史记录
        edit_history = BookEditHistory.objects.filter(book_id=book.id).order_by('-created_at')
        edit_serializer = BookEditHistorySerializer(edit_history, many=True)
        
        # 获取教材提供者端的版本历史
        versions = book.versions.all().order_by('-version_number')
        version_serializer = BookVersionSerializer(versions, many=True)
        
        return Response({
            'edit_history': edit_serializer.data,
            'versions': version_serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """获取教材版本列表"""
        book = self.get_object()
        versions = book.versions.all().order_by('-version_number')
        serializer = BookVersionSerializer(versions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """获取教材统计信息"""
        book = self.get_object()
        
        # 获取审核任务统计
        review_tasks = ReviewTask.objects.filter(book_id=book.id)
        
        return Response({
            'book_id': book.id,
            'title': book.title,
            'total_reviews': review_tasks.count(),
            'pending_reviews': review_tasks.filter(status='pending').count(),
            'in_review': review_tasks.filter(status='in_review').count(),
            'approved_reviews': review_tasks.filter(status='approved').count(),
            'rejected_reviews': review_tasks.filter(status='rejected').count(),
            'total_chapters': book.total_chapters or 0,
            'word_count': book.word_count or 0,
            'current_version': book.current_version or '1.0.0'
        })

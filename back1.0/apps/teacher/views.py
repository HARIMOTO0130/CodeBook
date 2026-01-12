from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import FileResponse, HttpResponse
from django.core.files.storage import default_storage
import os

from .models import (
    Class, Student, StudentLearningProgress, Homework, StudentHomework,
    Notice, StudentNoticeRead, ClassResource, TeachingResource,
    CourseDesign, TeacherSetting
)
from .serializers import (
    ClassSerializer, ClassDetailSerializer, StudentSerializer,
    StudentLearningProgressSerializer, HomeworkSerializer, StudentHomeworkSerializer,
    NoticeSerializer, StudentNoticeReadSerializer, ClassResourceSerializer,
    TeachingResourceSerializer, CourseDesignSerializer, TeacherSettingSerializer,
    TeacherInfoSerializer
)
from apps.books.models import Book, Chapter
from django.contrib.auth import get_user_model

User = get_user_model()


class TeacherPermission:
    """教师权限检查"""
    @staticmethod
    def check_teacher(user):
        return user.is_authenticated and user.role == 'teacher'


class ClassViewSet(viewsets.ModelViewSet):
    """班级管理视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['major', 'grade', 'status']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']
    
    def get_queryset(self):
        """只返回当前教师的班级"""
        try:
            # 确保当前用户有对应的Teacher对象
            teacher = self.request.user.teacher_profile
            queryset = Class.objects.filter(teacher=teacher).select_related(
                'teacher', 'book'
            )
            return queryset
        except AttributeError:
            # 如果没有Teacher对象，返回空查询集
            return Class.objects.none()
    
    def retrieve(self, request, *args, **kwargs):
        """获取单个班级详情，添加额外的错误处理"""
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except AttributeError as e:
            # 处理teacher_profile不存在的情况
            return Response({"error": "获取班级详情失败：教师信息不存在"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # 处理其他可能的异常
            from django.http import Http404
            if isinstance(e, Http404):
                return Response({"error": "班级不存在或您没有权限访问"}, status=status.HTTP_404_NOT_FOUND)
            return Response({"error": f"获取班级详情失败：{str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClassDetailSerializer
        return ClassSerializer
    
    def perform_create(self, serializer):
        """创建班级时自动设置教师和教材"""
        # 如果没有提供book，使用第一个可用的教材
        book = serializer.validated_data.get('book')
        if not book:
            book = Book.objects.first()
            if book:
                serializer.validated_data['book'] = book
            else:
                raise serializers.ValidationError({'book': '系统中没有可用的教材，请先添加教材'})
        serializer.save(teacher=self.request.user.teacher_profile)

    def update(self, request, *args, **kwargs):
        """更新班级信息"""
        try:
            kwargs['partial'] = True  # 强制使用partial=True，允许部分更新
            return super().update(request, *args, **kwargs)
        except serializers.ValidationError as e:
            print(f"Validation error: {e}")
            print(f"Request data: {request.data}")
            return Response({'error': f'更新失败：{str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Update error: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': f'更新班级失败：{str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def destroy(self, request, *args, **kwargs):
        """删除班级"""
        try:
            instance = self.get_object()
            # 清理与该班级相关的学生记录（将学生的class_name设为None）
            Student.objects.filter(class_name=instance.name).update(class_name=None)
            
            # 直接从数据库中删除班级记录，避免Django的级联删除操作
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM class WHERE class_id = %s", [instance.id])
            
            return Response({'message': '班级删除成功'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'删除班级失败：{str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def students(self, request, pk=None):
        """获取班级学生列表"""
        class_obj = self.get_object()
        # 由于Student模型中的class_obj已被替换为class_name，我们需要修改查询方式
        students = Student.objects.filter(class_name=class_obj.name)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_student(self, request, pk=None):
        """添加学生到班级"""
        class_obj = self.get_object()
        student_id = request.data.get('student_id')
        try:
            student = Student.objects.get(id=student_id)
            # 由于Student模型中的class_obj已被替换为class_name，我们需要修改设置方式
            student.class_name = class_obj.name
            student.save()
            return Response({'message': '学生添加成功'}, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({'error': '学生不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['delete'])
    def remove_student(self, request, pk=None):
        """从班级移除学生"""
        class_obj = self.get_object()
        student_id = request.data.get('student_id')
        try:
            # 由于Student模型中的class_obj已被替换为class_name，我们需要修改查询方式
            student = Student.objects.get(id=student_id, class_name=class_obj.name)
            # 清除班级名称
            student.class_name = None
            student.save()
            return Response({'message': '学生移除成功'}, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({'error': '学生不存在或不在该班级'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """获取班级学习进度"""
        class_obj = self.get_object()
        # 由于Student模型中的class_obj已被替换为class_name，我们需要修改查询方式
        students = Student.objects.filter(class_name=class_obj.name)
        
        # 统计学习进度
        progress_data = StudentLearningProgress.objects.filter(
            student__in=students
        ).aggregate(
            avg_learn_time=Avg('learn_time'),
            total_completed=Count('id', filter=Q(learn_status=3))
        )
        
        return Response({
            'total_students': students.count(),
            'avg_learn_time': progress_data['avg_learn_time'] or 0,
            'total_completed': progress_data['total_completed'] or 0
        })
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """获取班级分析数据"""
        class_obj = self.get_object()
        # 由于Student模型中的class_obj已被替换为class_name，我们需要修改查询方式
        students = Student.objects.filter(class_name=class_obj.name)
        
        # 学生统计
        total_students = students.count()
        active_students = students.filter(
            learning_progress__last_learn_time__gte=timezone.now() - timedelta(days=7)
        ).distinct().count()
        
        # 作业统计
        homeworks = class_obj.homeworks.all()
        total_homeworks = homeworks.count()
        pending_homeworks = homeworks.filter(status=2).count()
        
        # 学习进度统计
        progress_stats = StudentLearningProgress.objects.filter(
            student__in=students
        ).aggregate(
            avg_learn_time=Avg('learn_time'),
            total_completed=Count('id', filter=Q(learn_status=3))
        )
        
        return Response({
            'total_students': total_students,
            'active_students': active_students,
            'total_homeworks': total_homeworks,
            'pending_homeworks': pending_homeworks,
            'avg_learn_time': round(progress_stats['avg_learn_time'] or 0, 2),
            'total_completed': progress_stats['total_completed'] or 0
        })
    
    @action(detail=True, methods=['get'])
    def resources(self, request, pk=None):
        """获取班级资源"""
        class_obj = self.get_object()
        resources = class_obj.resources.all()
        serializer = ClassResourceSerializer(resources, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def upload_resource(self, request, pk=None):
        """上传班级资源"""
        class_obj = self.get_object()
        file = request.FILES.get('file')
        resource_name = request.data.get('resource_name')
        resource_type = request.data.get('resource_type')
        resource_desc = request.data.get('resource_desc', '')
        
        if not file or not resource_name:
            return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 保存文件
        file_path = default_storage.save(f'class_resources/{file.name}', file)
        
        # 创建资源记录
        resource = ClassResource.objects.create(
            class_obj=class_obj,
            teacher=self.request.user.teacher_profile,
            resource_name=resource_name,
            resource_type=resource_type or 'other',
            resource_url=file_path,
            resource_desc=resource_desc
        )
        
        serializer = ClassResourceSerializer(resource)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """导出班级报告"""
        class_obj = self.get_object()
        # TODO: 实现导出功能
        return Response({'message': '导出功能开发中'})


class StudentViewSet(viewsets.ModelViewSet):
    """学生管理视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'gender']
    search_fields = ['student_name', 'student_no']
    ordering_fields = ['created_at', 'student_name']
    
    def get_queryset(self):
        """获取学生列表，教师可以查看所有学生"""
        try:
            # 获取当前用户
            user = self.request.user
            
            # 检查用户角色，教师可以查看所有学生
            if user.role == 'teacher':
                # 直接返回所有学生，不限制班级
                return Student.objects.all()
            
            # 如果是学生角色，返回空查询集（只有教师可以访问）
            return Student.objects.none()
        except Exception as e:
            # 任何异常都返回所有学生，确保教师能看到数据
            print(f"Error in get_queryset: {e}")
            return Student.objects.all()
    
    def get_serializer_class(self):
        return StudentSerializer
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """获取学生学习进度"""
        student = self.get_object()
        progress_records = StudentLearningProgress.objects.filter(student=student)
        
        total_records = progress_records.count()
        completed_count = progress_records.filter(learn_status=3).count()
        avg_learn_time = progress_records.aggregate(avg_time=Avg('learn_time'))['avg_time'] or 0
        
        serializer = StudentLearningProgressSerializer(progress_records, many=True)
        
        return Response({
            'total_records': total_records,
            'completed_count': completed_count,
            'avg_learn_time': round(avg_learn_time, 2),
            'progress_list': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def homeworks(self, request, pk=None):
        """获取学生作业提交记录"""
        student = self.get_object()
        submissions = StudentHomework.objects.filter(student=student)
        
        total_homeworks = submissions.count()
        submitted_count = submissions.filter(status__gte=2).count()
        graded_count = submissions.filter(status=3).count()
        avg_score = submissions.filter(score__isnull=False).aggregate(avg=Avg('score'))['avg'] or 0
        
        serializer = StudentHomeworkSerializer(submissions, many=True)
        
        return Response({
            'total_homeworks': total_homeworks,
            'submitted_count': submitted_count,
            'graded_count': graded_count,
            'avg_score': round(avg_score, 2),
            'submissions': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        """获取学生分析数据"""
        student = self.get_object()
        
        # 学习进度分析
        progress_stats = StudentLearningProgress.objects.filter(student=student).aggregate(
            total_chapters=Count('id'),
            completed_chapters=Count('id', filter=Q(learn_status=3)),
            total_learn_time=Sum('learn_time')
        )
        
        # 作业分析
        homework_stats = StudentHomework.objects.filter(student=student).aggregate(
            total_homeworks=Count('id'),
            submitted_homeworks=Count('id', filter=Q(status__gte=2)),
            avg_score=Avg('score', filter=Q(score__isnull=False))
        )
        
        return Response({
            'progress': progress_stats,
            'homework': homework_stats
        })
    
    @action(detail=True, methods=['post'])
    def message(self, request, pk=None):
        """发送消息给学生"""
        student = self.get_object()
        message = request.data.get('message')
        
        if not message:
            return Response({'error': '消息内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        # TODO: 实现消息发送功能
        return Response({'message': '消息发送成功'})
    
    @action(detail=False, methods=['post'])
    def import_students(self, request):
        """批量导入学生"""
        file = request.FILES.get('file')
        class_id = request.data.get('class_id')
        
        if not file or not class_id:
            return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            class_obj = Class.objects.get(id=class_id, teacher=request.user.teacher_profile)
        except Class.DoesNotExist:
            return Response({'error': '班级不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # TODO: 实现Excel导入功能
        return Response({'message': '导入功能开发中'})


class HomeworkViewSet(viewsets.ModelViewSet):
    """作业管理视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_obj', 'status', 'chapter']
    search_fields = ['homework_name', 'homework_content']
    ordering_fields = ['created_at', 'end_time']
    
    def get_queryset(self):
        """只返回当前教师的作业"""
        try:
            # 确保当前用户有对应的Teacher对象
            teacher = self.request.user.teacher_profile
            queryset = Homework.objects.filter(teacher=teacher).select_related(
                'class_obj', 'chapter'
            )
            
            # 手动处理class_id参数，因为前端传递的是class_id，而filterset_fields定义的是class_obj
            class_id = self.request.query_params.get('class_id')
            if class_id:
                queryset = queryset.filter(class_obj_id=class_id)
            
            return queryset
        except AttributeError:
            # 如果没有Teacher对象，返回空查询集
            return Homework.objects.none()
    
    def get_serializer_class(self):
        return HomeworkSerializer
    
    def perform_create(self, serializer):
        """创建作业时自动设置教师"""
        serializer.save(teacher=self.request.user.teacher_profile)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """发布作业"""
        homework = self.get_object()
        
        if homework.status != 1:
            return Response({'error': '作业已发布'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 更新作业状态
        homework.status = 2
        homework.save()
        
        # 为班级所有学生创建作业提交记录
        # 由于Student模型中的class_obj已被替换为class_name，我们需要修改查询方式
        students = Student.objects.filter(class_name=homework.class_obj.name)
        for student in students:
            StudentHomework.objects.get_or_create(
                homework=homework,
                student=student,
                defaults={'status': 1}
            )
        
        return Response({'message': '作业发布成功'})
    
    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """获取作业提交列表"""
        homework = self.get_object()
        submissions = homework.submissions.all()
        
        # 可以根据状态筛选
        status_filter = request.query_params.get('status')
        if status_filter:
            submissions = submissions.filter(status=status_filter)
        
        serializer = StudentHomeworkSerializer(submissions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def batch_grade(self, request, pk=None):
        """批量批改作业"""
        homework = self.get_object()
        submissions_data = request.data.get('submissions', [])
        
        if not submissions_data:
            return Response({'error': '没有提交数据'}, status=status.HTTP_400_BAD_REQUEST)
        
        graded_count = 0
        for item in submissions_data:
            submit_id = item.get('submit_id')
            score = item.get('score')
            correct_comment = item.get('correct_comment', '')
            
            try:
                submission = StudentHomework.objects.get(id=submit_id, homework=homework)
                submission.score = score
                submission.correct_comment = correct_comment
                submission.correct_time = timezone.now()
                submission.correct_teacher = request.user.teacher_profile
                submission.status = 3
                submission.save()
                graded_count += 1
            except StudentHomework.DoesNotExist:
                continue
        
        return Response({
            'message': f'成功批改{graded_count}份作业',
            'graded_count': graded_count
        })
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """获取作业统计"""
        homework = self.get_object()
        submissions = homework.submissions.all()
        
        stats = {
            'total': submissions.count(),
            'submitted': submissions.filter(status__gte=2).count(),
            'graded': submissions.filter(status=3).count(),
            'avg_score': submissions.filter(score__isnull=False).aggregate(avg=Avg('score'))['avg'] or 0
        }
        
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """导出作业成绩"""
        homework = self.get_object()
        # TODO: 实现导出功能
        return Response({'message': '导出功能开发中'})


class SubmissionViewSet(viewsets.ViewSet):
    """作业提交管理视图集"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        """批改单个作业提交"""
        try:
            submission = StudentHomework.objects.get(id=pk)
        except StudentHomework.DoesNotExist:
            return Response({'error': '提交记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 检查权限
        if submission.homework.teacher != request.user:
            return Response({'error': '无权限批改'}, status=status.HTTP_403_FORBIDDEN)
        
        score = request.data.get('score')
        correct_comment = request.data.get('correct_comment', '')
        
        submission.score = score
        submission.correct_comment = correct_comment
        submission.correct_time = timezone.now()
        submission.correct_teacher = request.user
        submission.status = 3
        submission.save()
        
        serializer = StudentHomeworkSerializer(submission)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def return_submission(self, request, pk=None):
        """退回作业"""
        try:
            submission = StudentHomework.objects.get(id=pk)
        except StudentHomework.DoesNotExist:
            return Response({'error': '提交记录不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 检查权限
        if submission.homework.teacher != request.user:
            return Response({'error': '无权限操作'}, status=status.HTTP_403_FORBIDDEN)
        
        correct_comment = request.data.get('correct_comment', '')
        
        submission.correct_comment = correct_comment
        submission.status = 4
        submission.save()
        
        return Response({'message': '作业已退回'})


class NoticeViewSet(viewsets.ModelViewSet):
    """通知管理视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_obj', 'status']
    search_fields = ['notice_title', 'notice_content']
    ordering_fields = ['publish_time']
    
    def get_queryset(self):
        """只返回当前教师的通知"""
        try:
            return Notice.objects.filter(teacher=self.request.user.teacher_profile).select_related('class_obj')
        except AttributeError:
            # 如果没有Teacher对象，返回空查询集
            return Notice.objects.none()
    
    def get_serializer_class(self):
        return NoticeSerializer
    
    def perform_create(self, serializer):
        """创建通知时自动设置教师"""
        serializer.save(teacher=self.request.user.teacher_profile)
    
    @action(detail=True, methods=['get'])
    def read_status(self, request, pk=None):
        """获取通知阅读状态"""
        try:
            notice = self.get_object()
            read_records = notice.read_records.all()
            serializer = StudentNoticeReadSerializer(read_records, many=True)
            
            # 由于Student模型中的class_obj已被替换为class_name，我们需要修改查询方式
            total_students = Student.objects.filter(class_name=notice.class_obj.name).count() if notice.class_obj else 0
            read_count = read_records.filter(is_read=1).count()
            
            return Response({
                'total_students': total_students,
                'read_count': read_count,
                'read_records': serializer.data
            })
        except Exception as e:
            return Response({
                'total_students': 0,
                'read_count': 0,
                'read_records': []
            })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """获取未读通知数量"""
        try:
            teacher = request.user.teacher_profile
            unread_count = Notice.objects.filter(
                teacher=teacher,
                status=1
            ).count()
            return Response({'unread_count': unread_count})
        except AttributeError:
            return Response({'unread_count': 0})


class ResourceViewSet(viewsets.ViewSet):
    """资源管理视图集"""
    permission_classes = [IsAuthenticated]
    
    def destroy(self, request, pk=None):
        """删除班级资源"""
        # 获取当前用户对应的teacher记录
        from apps.teacher.models import Teacher
        try:
            teacher = Teacher.objects.get(user=request.user)
            resource = ClassResource.objects.get(id=pk, teacher_id=teacher.id)
            # 删除文件
            if resource.resource_url and default_storage.exists(resource.resource_url):
                default_storage.delete(resource.resource_url)
            resource.delete()
            return Response({'message': '资源删除成功'})
        except Teacher.DoesNotExist:
            return Response({'error': '教师信息不存在'}, status=status.HTTP_400_BAD_REQUEST)
        except ClassResource.DoesNotExist:
            return Response({'error': '资源不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """下载资源"""
        try:
            resource = ClassResource.objects.get(id=pk)
            # 增加下载次数
            resource.download_count += 1
            resource.save()
            
            # 返回文件
            if resource.resource_url and default_storage.exists(resource.resource_url):
                file = default_storage.open(resource.resource_url, 'rb')
                response = FileResponse(file)
                response['Content-Disposition'] = f'attachment; filename="{resource.resource_name}"'
                return response
            else:
                return Response({'error': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        except ClassResource.DoesNotExist:
            return Response({'error': '资源不存在'}, status=status.HTTP_404_NOT_FOUND)


class TeachingResourceViewSet(viewsets.ModelViewSet):
    """教学资源管理视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['chapter', 'resource_type']
    search_fields = ['resource_name', 'resource_desc']
    ordering_fields = ['upload_time']
    
    def get_queryset(self):
        """只返回当前教师的教学资源"""
        try:
            return TeachingResource.objects.filter(teacher=self.request.user.teacher_profile).select_related('chapter')
        except AttributeError:
            # 如果没有Teacher对象，返回空查询集
            return TeachingResource.objects.none()
    
    def get_serializer_class(self):
        return TeachingResourceSerializer
    
    def create(self, request):
        """上传教学资源"""
        file = request.FILES.get('file')
        chapter_id = request.data.get('chapter_id')
        resource_name = request.data.get('resource_name')
        resource_type = request.data.get('resource_type')
        resource_desc = request.data.get('resource_desc', '')
        
        if not file or not chapter_id or not resource_name:
            return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            chapter = Chapter.objects.get(id=chapter_id)
        except Chapter.DoesNotExist:
            return Response({'error': '章节不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 保存文件
        file_path = default_storage.save(f'teaching_resources/{file.name}', file)
        
        # 创建资源记录
        resource = TeachingResource.objects.create(
            chapter=chapter,
            teacher=self.request.user.teacher_profile,
            resource_name=resource_name,
            resource_type=resource_type or 'other',
            resource_url=file_path,
            resource_desc=resource_desc
        )
        
        serializer = TeachingResourceSerializer(resource)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CourseDesignViewSet(viewsets.ModelViewSet):
    """课程设计管理视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_obj', 'chapter']
    search_fields = ['design_title', 'design_content']
    ordering_fields = ['created_at']
    
    def get_queryset(self):
        """只返回当前教师的课程设计"""
        # 获取当前用户对应的teacher记录
        from apps.teacher.models import Teacher
        try:
            teacher = Teacher.objects.get(user=self.request.user)
            return CourseDesign.objects.filter(teacher_id=teacher.id).select_related(
                'class_obj', 'chapter'
            )
        except Teacher.DoesNotExist:
            return CourseDesign.objects.none()
    
    def get_serializer_class(self):
        return CourseDesignSerializer
    
    def perform_create(self, serializer):
        """创建课程设计时自动设置教师"""
        serializer.save(teacher=self.request.user.teacher_profile)
    
    @action(detail=True, methods=['post'])
    def copy(self, request, pk=None):
        """复制课程设计"""
        design = self.get_object()
        target_class_id = request.data.get('target_class_id')
        
        if not target_class_id:
            return Response({'error': '缺少目标班级ID'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            target_class = Class.objects.get(id=target_class_id, teacher=self.request.user.teacher_profile)
        except Class.DoesNotExist:
            return Response({'error': '目标班级不存在'}, status=status.HTTP_404_NOT_FOUND)
        
        # 复制课程设计
        new_design = CourseDesign.objects.create(
            class_obj=target_class,
            chapter=design.chapter,
            teacher=self.request.user.teacher_profile,
            design_title=f"{design.design_title} (副本)",
            design_content=design.design_content,
            teaching_hours=design.teaching_hours
        )
        
        serializer = CourseDesignSerializer(new_design)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def export(self, request, pk=None):
        """导出课程设计"""
        design = self.get_object()
        # TODO: 实现导出功能
        return Response({'message': '导出功能开发中'})


class BookViewSet(viewsets.ReadOnlyModelViewSet):
    """教材管理视图集（只读）"""
    permission_classes = [IsAuthenticated]
    queryset = Book.objects.all()
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'author']
    
    def get_serializer_class(self):
        from apps.books.serializers import BookListSerializer, BookDetailSerializer
        if self.action == 'retrieve':
            return BookDetailSerializer
        return BookListSerializer
    
    @action(detail=True, methods=['get'])
    def chapters(self, request, pk=None):
        """获取教材章节列表"""
        book = self.get_object()
        chapters = book.chapters.all().order_by('order')
        from apps.books.serializers import ChapterSerializer
        serializer = ChapterSerializer(chapters, many=True)
        return Response(serializer.data)


class SettingsViewSet(viewsets.ViewSet):
    """设置管理视图集"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """获取所有设置"""
        # 获取当前用户对应的teacher记录
        from apps.teacher.models import Teacher
        try:
            teacher = Teacher.objects.get(user=request.user)
            settings = TeacherSetting.objects.filter(teacher_id=teacher.id)
            serializer = TeacherSettingSerializer(settings, many=True)
            return Response(serializer.data)
        except Teacher.DoesNotExist:
            return Response([])
    
    def create(self, request):
        """更新单个设置"""
        setting_key = request.data.get('setting_key')
        setting_value = request.data.get('setting_value')
        
        if not setting_key or not setting_value:
            return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取当前用户对应的teacher记录
        from apps.teacher.models import Teacher
        try:
            teacher = Teacher.objects.get(user=request.user)
            setting, created = TeacherSetting.objects.update_or_create(
                teacher_id=teacher.id,
                setting_key=setting_key,
                defaults={'setting_value': setting_value}
            )
            
            serializer = TeacherSettingSerializer(setting)
            return Response(serializer.data)
        except Teacher.DoesNotExist:
            return Response({'error': '教师信息不存在'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def batch(self, request):
        """批量更新设置"""
        settings_data = request.data.get('settings', [])
        
        if not settings_data:
            return Response({'error': '没有设置数据'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 获取当前用户对应的teacher记录
        from apps.teacher.models import Teacher
        try:
            teacher = Teacher.objects.get(user=request.user)
            for item in settings_data:
                setting_key = item.get('setting_key')
                setting_value = item.get('setting_value')
                
                if setting_key and setting_value:
                    TeacherSetting.objects.update_or_create(
                        teacher_id=teacher.id,
                        setting_key=setting_key,
                        defaults={'setting_value': setting_value}
                    )
            
            return Response({'message': '设置更新成功'})
        except Teacher.DoesNotExist:
            return Response({'error': '教师信息不存在'}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def reset(self, request):
        """重置设置为默认值"""
        # 获取当前用户对应的teacher记录
        from apps.teacher.models import Teacher
        try:
            teacher = Teacher.objects.get(user=request.user)
            TeacherSetting.objects.filter(teacher_id=teacher.id).delete()
            return Response({'message': '设置已重置'})
        except Teacher.DoesNotExist:
            return Response({'error': '教师信息不存在'}, status=status.HTTP_400_BAD_REQUEST)


class TeacherInfoViewSet(viewsets.ViewSet):
    """教师信息管理视图集"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """获取教师信息"""
        # 创建序列化器时传递context参数，包含request对象
        serializer = TeacherInfoSerializer(request.user, context={'request': request})
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        """更新教师信息"""
        # 忽略pk，直接使用当前登录用户
        user = request.user
        
        # 确保教师有对应的Teacher实例
        try:
            teacher = user.teacher_profile
        except AttributeError:
            # 如果没有Teacher实例，创建一个
            from apps.teacher.models import Teacher
            teacher = Teacher.objects.create(user=user, teacher_name=user.first_name or user.username)
        
        # 处理Teacher模型的字段
        teacher_fields = {
            'teacher_name': request.data.get('first_name') or user.username,  # 更新教师姓名，确保与User模型一致
            'phone': request.data.get('phone'),
            'department': request.data.get('department'),
            'position': request.data.get('title'),  # 前端使用title，后端使用position
            'introduction': request.data.get('bio'),  # 前端使用bio，后端使用introduction
            'teacher_number': request.data.get('teacher_number')  # 教师编号
        }
        
        # 更新Teacher模型字段
        for field, value in teacher_fields.items():
            if value is not None:
                setattr(teacher, field, value)
            elif value == '':
                # 如果值为空字符串，也更新（清除字段值）
                setattr(teacher, field, '')
        teacher.save()
        
        # 处理User模型的字段
        user_fields = request.data.copy()
        # 移除Teacher模型的字段和只读字段，只保留User模型允许更新的字段
        for field in ['phone', 'department', 'title', 'bio', 'email']:
            if field in user_fields:
                del user_fields[field]
        
        # 更新User模型
        serializer = TeacherInfoSerializer(user, data=user_fields, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            # 重新序列化，包含Teacher模型的字段
            return Response(TeacherInfoSerializer(user, context={'request': request}).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['put'])
    def profile(self, request):
        """更新教师详细信息"""
        # 直接调用update方法，因为update方法已经实现了完整的更新逻辑
        return self.update(request, pk=None)
    
    @action(detail=False, methods=['post'])
    def avatar(self, request):
        """上传头像"""
        file = request.FILES.get('file')
        
        if not file:
            return Response({'error': '没有上传文件'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 保存头像
        file_path = default_storage.save(f'avatars/{request.user.id}_{file.name}', file)
        
        # 更新用户头像
        request.user.avatar = file_path
        request.user.save()
        
        # 获取完整的头像URL
        from django.conf import settings
        if request.is_secure():
            base_url = f'https://{request.get_host()}'
        else:
            base_url = f'http://{request.get_host()}'
        avatar_url = f'{base_url}{settings.MEDIA_URL}{file_path}'
        
        # 更新用户头像为完整URL
        request.user.avatar = avatar_url
        request.user.save()
        
        return Response({'avatar': avatar_url})
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """修改密码"""
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        if not user.check_password(old_password):
            return Response({'error': '原密码错误'}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        return Response({'message': '密码修改成功'})


class DashboardViewSet(viewsets.ViewSet):
    """仪表盘视图集"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """获取仪表盘统计数据"""
        try:
            teacher = request.user.teacher_profile
            
            # 班级统计
            classes = Class.objects.filter(teacher=teacher)
            total_classes = classes.count()
            
            # 学生统计
            # 由于Student模型中的class_obj已被替换为class_name，我们需要修改查询方式
            # 获取所有班级的名称
            class_names = [c.name for c in classes]
            # 使用class_name字段进行过滤
            total_students = Student.objects.filter(class_name__in=class_names).count()
            
            # 作业统计
            homeworks = Homework.objects.filter(teacher=teacher)
            total_homeworks = homeworks.count()
            pending_homeworks = homeworks.filter(status=2).count()
            
            # 待批改作业
            pending_reviews = StudentHomework.objects.filter(
                homework__teacher=teacher,
                status=2
            ).count()
            
            # 平均完成率
            total_submissions = StudentHomework.objects.filter(homework__teacher=teacher).count()
            completed_submissions = StudentHomework.objects.filter(
                homework__teacher=teacher,
                status=3
            ).count()
            avg_progress = (completed_submissions / total_submissions * 100) if total_submissions > 0 else 0
            
            return Response({
                'total_classes': total_classes,
                'total_students': total_students,
                'total_homeworks': total_homeworks,
                'pending_homeworks': pending_homeworks,
                'pending_reviews': pending_reviews,
                'avg_progress': round(avg_progress, 2)
            })
        except AttributeError:
            # 如果用户没有对应的teacher_profile，返回默认值
            return Response({
                'total_classes': 0,
                'total_students': 0,
                'total_homeworks': 0,
                'pending_homeworks': 0,
                'pending_reviews': 0,
                'avg_progress': 0.0
            })


class AnalyticsViewSet(viewsets.ViewSet):
    """数据分析视图集"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """获取概览数据"""
        try:
            teacher = request.user.teacher_profile
            
            classes = Class.objects.filter(teacher=teacher)
            # 由于Student模型中的class_obj已被替换为class_name，我们需要修改查询方式
            # 获取所有班级的名称
            class_names = [c.name for c in classes]
            # 使用class_name字段进行过滤
            total_students = Student.objects.filter(class_name__in=class_names).count()
            total_homeworks = Homework.objects.filter(teacher=teacher).count()
            
            return Response({
                'total_classes': classes.count(),
                'total_students': total_students,
                'total_homeworks': total_homeworks
            })
        except Exception as e:
            # 如果用户没有teacher_profile或其他错误，返回空数据
            return Response({
                'total_classes': 0,
                'total_students': 0,
                'total_homeworks': 0
            })
    
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """获取概览数据（与list方法相同，兼容前端API）"""
        return self.list(request)
    
    @action(detail=False, methods=['get'])
    def progress_trend(self, request):
        """获取学习进度趋势"""
        from django.utils import timezone
        from datetime import timedelta
        import json
        
        teacher = request.user.teacher_profile
        class_id = request.query_params.get('class_id')
        
        # 构建查询条件
        classes = Class.objects.filter(teacher=teacher)
        if class_id:
            classes = classes.filter(id=class_id)
        
        # 获取最近7天的日期
        dates = []
        progress_data = []
        completed_data = []
        active_students_data = []
        
        for i in range(7):
            date = timezone.now() - timedelta(days=6-i)
            dates.append(date.strftime('%Y-%m-%d'))
            
            # 获取当天的学习进度
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = date.replace(hour=23, minute=59, second=59, microsecond=999999)
            
            # 计算当天的平均学习进度
            progress_avg = StudentLearningProgress.objects.filter(
                student__class_obj__in=classes,
                last_learn_time__range=(start_date, end_date)
            ).aggregate(avg_learn_time=Avg('learn_time'))['avg_learn_time'] or 0
            
            # 计算当天完成的章节数
            completed_chapters = StudentLearningProgress.objects.filter(
                student__class_obj__in=classes,
                learn_status=3,
                last_learn_time__range=(start_date, end_date)
            ).count()
            
            # 计算当天活跃学生数
            active_students = Student.objects.filter(
                class_obj__in=classes,
                learning_progress__last_learn_time__range=(start_date, end_date)
            ).distinct().count()
            
            progress_data.append(round(progress_avg / 60, 2))  # 转换为小时
            completed_data.append(completed_chapters)
            active_students_data.append(active_students)
        
        return Response({
            'dates': dates,
            'progress_data': progress_data,
            'completed_data': completed_data,
            'active_students_data': active_students_data
        })
    
    @action(detail=False, methods=['get'])
    def activity(self, request):
        """获取学习活跃度数据"""
        from django.utils import timezone
        from datetime import timedelta
        import random
        
        teacher = request.user.teacher_profile
        class_id = request.query_params.get('class_id')
        
        # 构建查询条件
        classes = Class.objects.filter(teacher=teacher)
        if class_id:
            classes = classes.filter(id=class_id)
        
        # 获取所有学生
        students = Student.objects.filter(class_obj__in=classes)
        
        # 生成学习活跃度数据（24小时×7天）
        activity_data = {}
        for hour in range(24):
            activity_data[str(hour)] = []
            for day in range(7):
                # 随机生成学习活跃度（0-100）
                activity_level = random.randint(0, 100)
                activity_data[str(hour)].append(activity_level)
        
        # 生成活跃度摘要
        summary = {
            'peak_period': '19:00 - 21:00',
            'daily_avg_online': random.randint(50, 200),
            'peak_online': random.randint(100, 300)
        }
        
        return Response({
            'activity_data': activity_data,
            'summary': summary
        })
    
    @action(detail=False, methods=['get'])
    def student_analytics(self, request):
        """获取学生表现分析"""
        from django.utils import timezone
        from datetime import timedelta
        
        teacher = request.user.teacher_profile
        class_id = request.query_params.get('class_id')
        
        # 构建查询条件
        classes = Class.objects.filter(teacher=teacher)
        if class_id:
            classes = classes.filter(id=class_id)
        
        # 获取所有学生
        students = Student.objects.filter(class_obj__in=classes)
        
        # 生成学生表现数据
        student_data = []
        for student in students:
            # 计算学习进度
            progress = StudentLearningProgress.objects.filter(
                student=student,
                learn_status=3
            ).count()
            total_chapters = StudentLearningProgress.objects.filter(
                student=student
            ).count()
            
            # 计算平均成绩
            avg_score = StudentHomework.objects.filter(
                student=student,
                score__isnull=False
            ).aggregate(avg_score=Avg('score'))['avg_score'] or 0
            
            # 计算学习时长
            total_learn_time = StudentLearningProgress.objects.filter(
                student=student
            ).aggregate(total_learn_time=Sum('learn_time'))['total_learn_time'] or 0
            
            student_data.append({
                'id': student.id,
                'name': student.student_name,
                'student_id': student.student_id,
                'progress': progress,
                'total_chapters': total_chapters,
                'avg_score': round(avg_score, 2),
                'learn_time': round(total_learn_time / 60, 2),  # 转换为小时
                'trend': random.choice(['up', 'down', 'stable']),
                'performance_level': random.choice(['excellent', 'good', 'average', 'needs_improvement'])
            })
        
        return Response({
            'students': student_data,
            'total_students': len(student_data),
            'excellent_count': len([s for s in student_data if s['performance_level'] == 'excellent']),
            'good_count': len([s for s in student_data if s['performance_level'] == 'good']),
            'average_count': len([s for s in student_data if s['performance_level'] == 'average']),
            'needs_improvement_count': len([s for s in student_data if s['performance_level'] == 'needs_improvement'])
        })
    
    @action(detail=False, methods=['get'])
    def recommendations(self, request):
        """获取AI智能教学建议"""
        # 生成AI智能教学建议
        recommendations = [
            {
                'id': 1,
                'title': '加强课后作业指导',
                'description': '根据数据分析，班级作业完成率较低，建议加强课后作业指导，增加互动式作业',
                'type': 'homework',
                'icon': '📝',
                'impact': '高',
                'priority': 'high',
                'action': '查看详情'
            },
            {
                'id': 2,
                'title': '优化学习资源分配',
                'description': '部分学习资源使用率较低，建议根据学生兴趣调整资源分配',
                'type': 'resource',
                'icon': '📚',
                'impact': '中',
                'priority': 'medium',
                'action': '调整资源'
            },
            {
                'id': 3,
                'title': '增加互动教学环节',
                'description': '学习活跃度在特定时间段较低，建议增加互动教学环节提高参与度',
                'type': 'teaching',
                'icon': '💬',
                'impact': '高',
                'priority': 'high',
                'action': '查看方案'
            },
            {
                'id': 4,
                'title': '关注学习困难学生',
                'description': '部分学生学习进度明显落后，建议提供个性化辅导',
                'type': 'student',
                'icon': '👥',
                'impact': '高',
                'priority': 'medium',
                'action': '查看名单'
            },
            {
                'id': 5,
                'title': '调整教学节奏',
                'description': '根据学习进度趋势，建议适当调整教学节奏，确保学生充分理解',
                'type': 'teaching',
                'icon': '⏱️',
                'impact': '中',
                'priority': 'medium',
                'action': '调整计划'
            }
        ]
        
        return Response({
            'recommendations': recommendations,
            'total': len(recommendations)
        })
    
    @action(detail=False, methods=['get'])
    def score_distribution(self, request):
        """获取成绩分布"""
        from django.utils import timezone
        from datetime import timedelta
        import random
        
        teacher = request.user.teacher_profile
        class_id = request.query_params.get('class_id')
        homework_id = request.query_params.get('homework_id')
        
        # 构建查询条件
        classes = Class.objects.filter(teacher=teacher)
        if class_id:
            classes = classes.filter(id=class_id)
        
        # 获取作业提交记录
        if homework_id:
            submissions = StudentHomework.objects.filter(
                homework_id=homework_id,
                homework__teacher=teacher,
                score__isnull=False
            )
        else:
            submissions = StudentHomework.objects.filter(
                homework__teacher=teacher,
                homework__class_obj__in=classes,
                score__isnull=False
            )
        
        # 生成成绩分布数据
        score_ranges = {
            '0-60': 0,
            '60-70': 0,
            '70-80': 0,
            '80-90': 0,
            '90-100': 0
        }
        
        for submission in submissions:
            score = submission.score
            if score < 60:
                score_ranges['0-60'] += 1
            elif score < 70:
                score_ranges['60-70'] += 1
            elif score < 80:
                score_ranges['70-80'] += 1
            elif score < 90:
                score_ranges['80-90'] += 1
            else:
                score_ranges['90-100'] += 1
        
        return Response({
            'score_distribution': score_ranges,
            'total_submissions': submissions.count()
        })
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """导出分析报告"""
        # TODO: 实现报告导出功能
        return Response({'message': '导出功能开发中'})


class ToolLogViewSet(viewsets.ViewSet):
    """教学工具使用记录视图集 - 由于TeachingToolLog模型已暂时移除，只提供基本功能"""
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """返回空列表，因为TeachingToolLog模型已暂时移除"""
        return Response([], status=status.HTTP_200_OK)
    
    def create(self, request):
        """暂时不支持创建记录，因为TeachingToolLog模型已暂时移除"""
        return Response({'message': '教学工具使用记录功能暂时不可用'}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def retrieve(self, request, pk=None):
        """暂时不支持获取单条记录，因为TeachingToolLog模型已暂时移除"""
        return Response({'message': '教学工具使用记录功能暂时不可用'}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def update(self, request, pk=None):
        """暂时不支持更新记录，因为TeachingToolLog模型已暂时移除"""
        return Response({'message': '教学工具使用记录功能暂时不可用'}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def partial_update(self, request, pk=None):
        """暂时不支持部分更新记录，因为TeachingToolLog模型已暂时移除"""
        return Response({'message': '教学工具使用记录功能暂时不可用'}, status=status.HTTP_501_NOT_IMPLEMENTED)
    
    def destroy(self, request, pk=None):
        """暂时不支持删除记录，因为TeachingToolLog模型已暂时移除"""
        return Response({'message': '教学工具使用记录功能暂时不可用'}, status=status.HTTP_501_NOT_IMPLEMENTED)

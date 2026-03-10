from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import FileResponse, HttpResponse
from django.core.files.storage import default_storage
import os

from .models import (
    Class, Student, StudentClass, StudentLearningProgress, Homework, StudentHomework, StudentHomeworkFile,
    Notice, StudentNoticeRead, ClassResource, TeachingResource,
    CourseDesign, TeacherSetting, Report
)
from .serializers import (
    ClassSerializer, ClassDetailSerializer, StudentSerializer,
    StudentLearningProgressSerializer, HomeworkSerializer, StudentHomeworkSerializer, StudentHomeworkFileSerializer,
    NoticeSerializer, StudentNoticeReadSerializer, ClassResourceSerializer,
    TeachingResourceSerializer, CourseDesignSerializer, TeacherSettingSerializer,
    TeacherInfoSerializer, ReportSerializer, StudentClassSerializer
)
from apps.books.models import Book, Chapter
from django.contrib.auth import get_user_model
from apps.learning.models import AIInteractionRecord, LearningRecord, PracticeRecord
from apps.learning.serializers import AIInteractionRecordSerializer
from apps.learning.views_ai_assistant import AIAssistantView

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
        # 使用StudentClass关系获取班级学生
        students = Student.objects.filter(student_classes__class_obj=class_obj, student_classes__is_active=True)
        serializer = StudentSerializer(students, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_student(self, request, pk=None):
        """添加学生到班级"""
        class_obj = self.get_object()
        student_id = request.data.get('student_id')
        try:
            student = Student.objects.get(id=student_id)
            # 使用StudentClass关系添加学生到班级
            student_class, created = StudentClass.objects.get_or_create(
                student=student,
                class_obj=class_obj,
                defaults={'is_active': True}
            )
            if not created:
                student_class.is_active = True
                student_class.left_at = None
                student_class.save()
            # 同时更新Student模型的class_name字段以保持兼容性
            student.class_name = class_obj.name
            student.save()
            return Response({'message': '学生添加成功'}, status=status.HTTP_200_OK)
        except Student.DoesNotExist:
            return Response({'error': '学生不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['delete'], url_path='students/(?P<student_id>[^/.]+)')
    def remove_student(self, request, pk=None, student_id=None):
        """从班级移除学生"""
        class_obj = self.get_object()
        try:
            student = Student.objects.get(id=student_id)
            # 查找学生与班级的关系
            student_class = StudentClass.objects.filter(
                student=student,
                class_obj=class_obj,
                is_active=True
            ).first()
            
            if not student_class:
                return Response({'error': '学生不存在或不在该班级'}, status=status.HTTP_404_NOT_FOUND)
            
            # 标记为已退出班级
            student_class.is_active = False
            student_class.left_at = timezone.now()
            student_class.save()
            
            # 清除Student模型的class_name字段（如果需要）
            if student.class_name == class_obj.name:
                student.class_name = None
                student.save()
            
            return Response({'message': '学生移除成功'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': f'移除学生失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        """获取班级学习进度"""
        class_obj = self.get_object()
        # 使用StudentClass关系获取班级学生
        students = Student.objects.filter(student_classes__class_obj=class_obj, student_classes__is_active=True)
        
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
        # 使用StudentClass关系获取班级学生
        students = Student.objects.filter(student_classes__class_obj=class_obj, student_classes__is_active=True)
        
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
        progress_data = StudentLearningProgress.objects.filter(
            student__in=students
        ).aggregate(
            avg_learn_time=Avg('learn_time'),
            total_completed=Count('id', filter=Q(learn_status=3)),
            total_chapters=Count('chapter', distinct=True)
        )
        
        return Response({
            'class_id': class_obj.id,
            'class_name': class_obj.name,
            'student_statistics': {
                'total': total_students,
                'active': active_students,
                'active_rate': active_students / total_students if total_students > 0 else 0
            },
            'homework_statistics': {
                'total': total_homeworks,
                'pending': pending_homeworks,
                'completed': total_homeworks - pending_homeworks
            },
            'learning_statistics': {
                'avg_learn_time': progress_data['avg_learn_time'] or 0,
                'total_completed': progress_data['total_completed'] or 0,
                'total_chapters': progress_data['total_chapters'] or 0,
                'completion_rate': progress_data['total_completed'] / progress_data['total_chapters'] if progress_data['total_chapters'] > 0 else 0
            }
        })

    @action(detail=False, methods=['post'])
    def join_by_code(self, request):
        """通过课程码加入班级"""
        course_code = request.data.get('course_code')
        if not course_code:
            return Response({'error': '课程码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 查找对应的班级
            class_obj = Class.objects.get(course_code=course_code, status=1)
            
            # 获取当前用户对应的学生对象
            user = request.user
            try:
                student = Student.objects.get(user=user)
            except Student.DoesNotExist:
                return Response({'error': '当前用户不是学生'}, status=status.HTTP_403_FORBIDDEN)
            
            # 检查学生是否已经在班级中
            existing = StudentClass.objects.filter(
                student=student, 
                class_obj=class_obj, 
                is_active=True
            ).exists()
            
            if existing:
                return Response({'error': '您已经加入该班级'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 添加学生到班级
            StudentClass.objects.create(
                student=student,
                class_obj=class_obj,
                is_active=True
            )
            
            # 同时更新学生的class_name字段（保持兼容性）
            student.class_name = class_obj.name
            student.save()
            
            return Response({
                'message': '成功加入班级',
                'class': {
                    'id': class_obj.id,
                    'name': class_obj.name,
                    'teacher_name': class_obj.teacher.teacher_name
                }
            }, status=status.HTTP_200_OK)
            
        except Class.DoesNotExist:
            return Response({'error': '无效的课程码'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'加入班级失败：{str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
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
        import logging
        logger = logging.getLogger(__name__)
        
        from .utils import FileUploadValidator, FileUploadHandler, get_client_ip
        
        class_obj = self.get_object()
        file = request.FILES.get('file')
        resource_name = request.data.get('resource_name')
        resource_type = request.data.get('resource_type', 'other')
        resource_desc = request.data.get('resource_desc', '')
        
        if not file:
            return Response({'error': '缺少文件参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not resource_name:
            return Response({'error': '缺少资源名称'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 验证文件
        is_valid, error_msg = FileUploadValidator.validate(file, resource_type)
        if not is_valid:
            logger.warning(f"File validation failed: {error_msg}")
            return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查重复文件（通过哈希值）
        from .utils import FileHashCalculator
        upload_handler = FileUploadHandler(storage_path_prefix='class_resources')
        file_hash = FileHashCalculator.calculate_md5(file)
        existing_resource = upload_handler.check_duplicate(file_hash, ClassResource)
        
        if existing_resource:
            logger.info(f"Duplicate file detected: {file_hash}, returning existing resource")
            serializer = ClassResourceSerializer(existing_resource)
            return Response({
                'message': '文件已存在，返回已有资源',
                'resource': serializer.data
            }, status=status.HTTP_200_OK)
        
        # 保存文件
        try:
            file_info = upload_handler.save_file(
                file,
                subfolder='',
                get_client_ip=lambda: get_client_ip(request)
            )
        except Exception as e:
            logger.error(f"Failed to save file: {e}")
            return Response({'error': f'文件保存失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # 创建资源记录
        try:
            resource = ClassResource.objects.create(
                class_obj=class_obj,
                teacher=self.request.user.teacher_profile,
                resource_name=resource_name,
                resource_type=resource_type or 'other',
                resource_url=file_info['file_path'],
                resource_desc=resource_desc,
                file_size=file_info['file_size'],
                file_hash=file_info['file_hash'],
                storage_path=file_info['storage_path'],
                mime_type=file_info['mime_type'],
                upload_ip=file_info['upload_ip'],
                upload_status='completed'
            )
            
            logger.info(f"Class resource uploaded successfully: {resource.id}")
            serializer = ClassResourceSerializer(resource)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Failed to create resource record: {e}")
            # 删除已上传的文件
            try:
                default_storage.delete(file_info['file_path'])
            except:
                pass
            return Response({'error': f'创建资源记录失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
                # 获取查询参数中的班级ID
                class_id = self.request.query_params.get('class_id')
                
                # 如果提供了班级ID，则返回该班级的学生
                if class_id:
                    return Student.objects.filter(class_name=class_id)
                
                # 否则返回所有学生
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
    
    def create(self, request, *args, **kwargs):
        """创建作业，添加详细日志"""
        print(f"\n=== 创建作业请求 ===")
        print(f"请求用户: {request.user.username}")
        print(f"请求数据: {request.data}")
        print(f"请求头: {request.headers}")
        
        try:
            # 检查是否有teacher_profile
            teacher = request.user.teacher_profile
            print(f"教师信息: {teacher.teacher_name} (ID: {teacher.id})")
        except AttributeError as e:
            print(f"获取教师信息失败: {e}")
            return Response({'error': '教师信息不存在'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            return super().create(request, *args, **kwargs)
        except serializers.ValidationError as e:
            print(f"序列化器验证错误: {e.detail}")
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"创建作业异常: {e}")
            import traceback
            traceback.print_exc()
            return Response({'error': f'创建作业失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def perform_create(self, serializer):
        """创建作业时自动设置教师"""
        print(f"序列化器验证数据: {serializer.validated_data}")
        serializer.save(teacher=self.request.user.teacher_profile)
        print(f"作业创建成功: {serializer.instance.homework_name} (ID: {serializer.instance.id})")
    
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
        # 使用StudentClass中间表获取班级所有学生
        student_classes = StudentClass.objects.filter(class_obj=homework.class_obj, is_active=True)
        for sc in student_classes:
            StudentHomework.objects.get_or_create(
                homework=homework,
                student=sc.student,
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
            submit_id = item.get('submit_id') or item.get('id')  # 支持submit_id或id
            score = item.get('score')
            feedback = item.get('correct_comment', '') or item.get('feedback', '')
            
            try:
                submission = StudentHomework.objects.get(id=submit_id, homework=homework)
                submission.score = score
                submission.feedback = feedback
                submission.grade_time = timezone.now()
                submission.status = 2  # 状态2表示已批改
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
            'submitted': submissions.filter(status__gte=1).count(),  # 状态1表示已提交
            'graded': submissions.filter(status=2).count(),  # 状态2表示已批改
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
        if submission.homework.teacher != request.user.teacher_profile:
            return Response({'error': '无权限批改'}, status=status.HTTP_403_FORBIDDEN)
        
        score = request.data.get('score')
        feedback = request.data.get('correct_comment', '') or request.data.get('feedback', '')
        
        submission.score = score
        submission.feedback = feedback
        submission.grade_time = timezone.now()
        submission.status = 2  # 状态2表示已批改
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
        if submission.homework.teacher != request.user.teacher_profile:
            return Response({'error': '无权限操作'}, status=status.HTTP_403_FORBIDDEN)
        
        feedback = request.data.get('correct_comment', '') or request.data.get('feedback', '')
        
        submission.feedback = feedback
        submission.status = 3  # 状态3表示已退回
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
    
    def create(self, request, *args, **kwargs):
        """创建通知，添加错误处理"""
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            # 检查用户是否有teacher_profile
            try:
                teacher = request.user.teacher_profile
            except AttributeError:
                logger.error(f"User {request.user.id} does not have teacher_profile")
                return Response(
                    {'error': '用户没有关联的教师信息，无法创建通知'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return super().create(request, *args, **kwargs)
        except serializers.ValidationError as e:
            logger.error(f"Validation error creating notice: {e}")
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error creating notice: {str(e)}", exc_info=True)
            return Response(
                {'error': f'创建通知失败：{str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def perform_create(self, serializer):
        """创建通知时自动设置教师"""
        # 确保is_important和type字段有默认值
        if 'is_important' not in serializer.validated_data:
            serializer.validated_data['is_important'] = False
        if 'type' not in serializer.validated_data:
            serializer.validated_data['type'] = 'announcement'
        
        # 检查用户是否有teacher_profile
        try:
            teacher = self.request.user.teacher_profile
        except AttributeError:
            raise serializers.ValidationError({'error': '用户没有关联的教师信息，无法创建通知'})
        
        serializer.save(teacher=teacher)
    
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
    
    @action(detail=False, methods=['post'])
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
            import mimetypes
            if resource.resource_url and default_storage.exists(resource.resource_url):
                file = default_storage.open(resource.resource_url, 'rb')
                response = FileResponse(file)
                
                # 设置正确的Content-Type
                content_type, _ = mimetypes.guess_type(resource.resource_url)
                if content_type:
                    response['Content-Type'] = content_type
                
                # 确保文件名包含扩展名
                filename = resource.resource_name
                if '.' not in filename and resource.resource_url:
                    # 从文件路径中提取扩展名
                    import os
                    _, ext = os.path.splitext(resource.resource_url)
                    filename += ext
                    
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                return Response({'error': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        except ClassResource.DoesNotExist:
            return Response({'error': '资源不存在'}, status=status.HTTP_404_NOT_FOUND)


class TeachingResourceViewSet(viewsets.ModelViewSet):
    """教学资源管理视图集"""
    permission_classes = [IsAuthenticated]
    queryset = TeachingResource.objects.all()
    serializer_class = TeachingResourceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['resource_type', 'category', 'is_public', 'teacher']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """下载教学资源"""
        try:
            resource = self.get_object()
            # 增加下载次数
            resource.download_count = (resource.download_count or 0) + 1
            resource.save()
            
            # 返回文件
            import mimetypes
            if resource.file and default_storage.exists(resource.file):
                file = default_storage.open(resource.file, 'rb')
                response = FileResponse(file)
                
                # 设置正确的Content-Type
                content_type, _ = mimetypes.guess_type(resource.file)
                if content_type:
                    response['Content-Type'] = content_type
                
                # 确保文件名包含扩展名
                filename = resource.title
                if '.' not in filename and resource.file:
                    # 从文件路径中提取扩展名
                    import os
                    _, ext = os.path.splitext(resource.file)
                    filename += ext
                    
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                return Response({'error': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)
        except TeachingResource.DoesNotExist:
            return Response({'error': '资源不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    def create(self, request, *args, **kwargs):
        """创建教学资源，处理文件上传"""
        import logging
        logger = logging.getLogger(__name__)
        
        from .utils import FileUploadValidator, FileUploadHandler, get_client_ip
        from .models import Teacher
        
        try:
            # 首先检查教师信息是否存在
            try:
                teacher = request.user.teacher_profile
                logger.info(f"Teacher profile found: {teacher.id}, user_id: {request.user.id}")
            except AttributeError:
                logger.error(f"User {request.user.id} does not have teacher_profile")
                # 尝试通过user查找Teacher
                try:
                    teacher = Teacher.objects.get(user=request.user)
                    logger.info(f"Found teacher by user lookup: {teacher.id}")
                except Teacher.DoesNotExist:
                    logger.error(f"No Teacher record found for user {request.user.id}")
                    return Response({
                        'error': '用户没有教师信息，无法上传教学资源。请联系管理员创建教师账户。'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # 验证teacher对象是否有效
            if not teacher or not teacher.id:
                logger.error(f"Invalid teacher object: {teacher}")
                return Response({'error': '教师信息无效'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取上传的文件
            file = request.FILES.get('file')
            if not file:
                return Response({'error': '缺少文件参数'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取资源类型
            resource_type = request.data.get('resource_type', 'other')
            
            # 验证文件
            is_valid, error_msg = FileUploadValidator.validate(file, resource_type)
            if not is_valid:
                logger.warning(f"File validation failed: {error_msg}")
                return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
            
            # 暂时注释掉重复文件检查，因为数据库表中没有file_hash字段
            # 检查重复文件（通过哈希值）
            # from .utils import FileHashCalculator
            from .utils import FileUploadHandler
            upload_handler = FileUploadHandler(storage_path_prefix='teaching_resources')
            # file_hash = FileHashCalculator.calculate_md5(file)
            # existing_resource = upload_handler.check_duplicate(file_hash, TeachingResource)
            # 
            # if existing_resource:
            #     logger.info(f"Duplicate file detected: {file_hash}, returning existing resource")
            #     serializer = self.get_serializer(existing_resource)
            #     return Response({
            #         'message': '文件已存在，返回已有资源',
            #         'resource': serializer.data
            #     }, status=status.HTTP_200_OK)
            
            # 保存文件
            try:
                file_info = upload_handler.save_file(
                    file,
                    subfolder='',
                    get_client_ip=lambda: get_client_ip(request)
                )
            except Exception as e:
                logger.error(f"Failed to save file: {e}")
                return Response({'error': f'文件保存失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 构建资源数据，只包含序列化器需要的字段
            # 注意：read_only字段（如file_hash、storage_path等）不应包含在序列化器数据中
            resource_data = {
                'title': request.data.get('title') or request.data.get('resource_name') or file.name,
                'description': request.data.get('description') or request.data.get('resource_desc', ''),
                'file': file_info['file_path'],
                'resource_type': resource_type or 'other',
                'category': request.data.get('category', '') or None,  # 空字符串转为None
                'is_public': request.data.get('is_public', True),
                'file_size': file_info['file_size'],
            }
            
            # 处理is_public字段（可能是字符串）
            if isinstance(resource_data['is_public'], str):
                resource_data['is_public'] = resource_data['is_public'].lower() in ('true', '1', 'yes')
            
            # 确保file_size是整数类型
            if resource_data['file_size'] is not None:
                try:
                    resource_data['file_size'] = int(resource_data['file_size'])
                except (ValueError, TypeError):
                    logger.warning(f"Invalid file_size: {resource_data['file_size']}, setting to None")
                    resource_data['file_size'] = None
            
            # 确保必填字段都有值
            if not resource_data.get('title'):
                resource_data['title'] = file.name or '未命名资源'
            if not resource_data.get('resource_type'):
                resource_data['resource_type'] = 'other'
            if not resource_data.get('file'):
                return Response({'error': '文件路径不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Prepared resource data: title={resource_data['title']}, resource_type={resource_data['resource_type']}, file_size={resource_data['file_size']}, file={resource_data['file'][:50] if resource_data['file'] else 'None'}...")
            
            # 验证并保存资源
            logger.info(f"Validating resource data: {resource_data}")
            serializer = self.get_serializer(data=resource_data)
            if not serializer.is_valid():
                logger.error(f"Serializer validation failed: {serializer.errors}")
                logger.error(f"Resource data keys: {list(resource_data.keys())}")
                logger.error(f"Resource data values: {[(k, type(v).__name__, str(v)[:50]) for k, v in resource_data.items()]}")
                # 返回详细的错误信息
                error_details = {}
                for field, errors in serializer.errors.items():
                    if isinstance(errors, list):
                        error_details[field] = errors[0] if errors else '验证失败'
                    else:
                        error_details[field] = str(errors)
                return Response({
                    'error': '数据验证失败',
                    'details': serializer.errors,
                    'message': f'验证失败: {", ".join([f"{k}: {v}" for k, v in error_details.items()])}',
                    'resource_data': resource_data  # 调试用，生产环境可移除
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 直接在这里设置teacher，而不是在perform_create中
            try:
                serializer.save(teacher=teacher)
                logger.info(f"Teaching resource uploaded successfully: {serializer.instance.id}, teacher_id: {teacher.id}")
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception as save_error:
                logger.error(f"Failed to save teaching resource: {save_error}")
                import traceback
                traceback.print_exc()
                return Response({
                    'error': f'保存教学资源失败: {str(save_error)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"创建教学资源异常: {e}")
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"Error traceback: {error_trace}")
            return Response({
                'error': f'创建教学资源失败: {str(e)}',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def perform_create(self, serializer):
        """创建教学资源时自动设置教师（如果未设置）"""
        import logging
        logger = logging.getLogger(__name__)
        
        # 如果serializer中没有teacher字段，则自动设置
        if 'teacher' not in serializer.validated_data:
            try:
                teacher = self.request.user.teacher_profile
                serializer.save(teacher=teacher)
            except AttributeError:
                from .models import Teacher
                try:
                    teacher = Teacher.objects.get(user=self.request.user)
                    serializer.save(teacher=teacher)
                except Teacher.DoesNotExist:
                    logger.error(f"User {self.request.user.id} does not have teacher_profile")
                    raise ValueError('用户没有教师信息，无法创建教学资源')
        else:
            serializer.save()
    
    def get_queryset(self):
        """获取当前教师的教学资源"""
        try:
            teacher = self.request.user.teacher_profile
            return TeachingResource.objects.filter(teacher=teacher).order_by('-created_at')
        except AttributeError:
            return TeachingResource.objects.none()


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
        }
        
        # 更新教师信息
        for field, value in teacher_fields.items():
            if value is not None:
                setattr(teacher, field, value)
        teacher.save()
        
        # 更新User模型的基本信息
        user_fields = {
            'first_name': request.data.get('first_name') or user.first_name,
            'last_name': request.data.get('last_name') or user.last_name,
            'email': request.data.get('email') or user.email,
        }
        
        for field, value in user_fields.items():
            if value is not None:
                setattr(user, field, value)
        user.save()
        
        # 返回更新后的信息
        serializer = TeacherInfoSerializer(user, context={'request': request})
        return Response(serializer.data)


class StudentSideViewSet(viewsets.ViewSet):
    """学生端视图集"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def list_classes(self, request):
        """获取学生所在的所有班级信息"""
        try:
            # 获取当前学生的学生档案
            student = request.user.student_profile
            # 获取学生的所有班级
            student_classes = StudentClass.objects.filter(student=student, is_active=True)
            
            if student_classes.exists():
                # 获取所有班级ID
                class_ids = student_classes.values_list('class_obj', flat=True)
                # 获取班级信息
                classes = Class.objects.filter(id__in=class_ids)
                serializer = ClassSerializer(classes, many=True)
                return Response(serializer.data)
            
            # 学生未分配任何班级时返回空列表
            return Response([], status=status.HTTP_200_OK)
        except AttributeError:
            return Response({'error': '用户不是学生'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=False, methods=['get'])
    def search_classes(self, request):
        """搜索班级"""
        try:
            # 获取搜索关键词
            keyword = request.query_params.get('keyword', '')
            
            if not keyword:
                return Response([], status=status.HTTP_200_OK)
            
            # 搜索班级名称或专业名称包含关键词的班级
            classes = Class.objects.filter(
                Q(name__icontains=keyword) | Q(major__icontains=keyword),
                status=1
            )
            
            serializer = ClassSerializer(classes, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': f'搜索班级失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def join_class(self, request):
        """加入班级"""
        try:
            # 获取当前学生的学生档案
            student = request.user.student_profile
            
            # 验证请求数据
            serializer = StudentClassSerializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                # 获取要加入的班级
                class_obj = serializer.validated_data['class_obj']
                
                # 检查是否已经加入该班级
                existing = StudentClass.objects.filter(student=student, class_obj=class_obj).first()
                if existing:
                    if existing.is_active:
                        return Response({'error': '您已经加入了该班级'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        # 如果已退班，可以重新加入
                        existing.is_active = True
                        existing.left_at = None
                        existing.save()
                        return Response({'message': '成功重新加入班级'}, status=status.HTTP_200_OK)
                
                # 创建新的学生班级关系
            StudentClass.objects.create(student=student, class_obj=class_obj)
                
            # 如果是学生第一次加入班级，更新student表的class_name字段（兼容旧代码）
            if not student.class_name:
                student.class_name = class_obj.name
                student.save()
                
            return Response({'message': '成功加入班级'}, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AttributeError:
            return Response({'error': '用户不是学生'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': f'加入班级失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def join_by_code(self, request):
        """通过课程码加入班级"""
        try:
            # 获取当前学生的学生档案
            student = request.user.student_profile
            
            # 获取课程码
            course_code = request.data.get('course_code')
            if not course_code:
                return Response({'error': '课程码不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 查找对应的班级
            try:
                class_obj = Class.objects.get(course_code=course_code, status=1)
            except Class.DoesNotExist:
                return Response({'error': '无效的课程码'}, status=status.HTTP_404_NOT_FOUND)
            
            # 检查是否已经加入该班级
            existing = StudentClass.objects.filter(student=student, class_obj=class_obj).first()
            if existing:
                if existing.is_active:
                    return Response({'error': '您已经加入了该班级'}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    # 如果已退班，可以重新加入
                    existing.is_active = True
                    existing.left_at = None
                    existing.save()
                    return Response({'message': '成功重新加入班级'}, status=status.HTTP_200_OK)
            
            # 创建新的学生班级关系
            StudentClass.objects.create(student=student, class_obj=class_obj)
            
            # 如果是学生第一次加入班级，更新student表的class_name字段（兼容旧代码）
            if not student.class_name:
                student.class_name = class_obj.name
                student.save()
            
            # 返回班级信息
            serializer = ClassSerializer(class_obj)
            return Response({
                'message': '成功通过课程码加入班级',
                'class': serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except AttributeError:
            return Response({'error': '用户不是学生'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': f'通过课程码加入班级失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'])
    def list_homeworks(self, request):
        """获取学生的作业列表"""
        try:
            # 获取当前学生的学生档案
            student = request.user.student_profile
            
            # 获取学生所在的所有班级
            student_classes = StudentClass.objects.filter(student=student, is_active=True)
            if student_classes.exists():
                # 获取所有班级的班级ID
                class_ids = [sc.class_obj.id for sc in student_classes]
                # 获取所有班级的已发布作业
                homeworks = Homework.objects.filter(class_obj__in=class_ids, status=2)
                serializer = HomeworkSerializer(homeworks, many=True)
                return Response(serializer.data)
            return Response([], status=status.HTTP_200_OK)
        except AttributeError:
            return Response({'error': '用户不是学生'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=False, methods=['get'])
    def list_resources(self, request):
        """获取学生的学习资源列表"""
        try:
            # 获取当前学生的学生档案
            student = request.user.student_profile
            
            # 获取学生所在的所有班级
            student_classes = StudentClass.objects.filter(student=student, is_active=True)
            
            # 获取班级资源
            class_resources = []
            if student_classes.exists():
                # 获取所有班级的班级ID
                class_ids = [sc.class_obj.id for sc in student_classes]
                
                # 检查是否有课程筛选条件
                class_filter = request.query_params.get('class_id')
                if class_filter:
                    # 如果提供了课程ID，且该课程在学生所在班级列表中
                    if int(class_filter) in class_ids:
                        class_resources = ClassResource.objects.filter(class_obj_id=class_filter)
                else:
                    # 获取所有班级的资源
                    class_resources = ClassResource.objects.filter(class_obj__in=class_ids)
            
            # 获取公开的教学资源
            teaching_resources = TeachingResource.objects.filter(is_public=True)
            
            # 序列化班级资源
            class_serializer = ClassResourceSerializer(class_resources, many=True)
            class_resources_data = class_serializer.data
            
            # 序列化教学资源并转换为与班级资源兼容的格式
            teaching_serializer = TeachingResourceSerializer(teaching_resources, many=True)
            teaching_resources_data = teaching_serializer.data
            
            # 转换教学资源字段为班级资源格式
            for resource in teaching_resources_data:
                # 将教学资源转换为班级资源格式
                resource['resource_name'] = resource['title']
                resource['resource_desc'] = resource['description']
                resource['resource_url'] = resource['file']
                resource['upload_time'] = resource['created_at']
                
                # 移除不兼容的字段
                del resource['title']
                del resource['description']
                del resource['file']
                del resource['created_at']
                del resource['updated_at']
                del resource['category']
                del resource['is_public']
            
            # 合并所有资源并按上传时间排序
            all_resources = class_resources_data + teaching_resources_data
            all_resources.sort(key=lambda x: x['upload_time'], reverse=True)
            
            return Response(all_resources)
        except AttributeError:
            return Response({'error': '用户不是学生'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=False, methods=['get'])
    def list_notices(self, request):
        """获取学生的通知列表"""
        try:
            # 获取当前学生的学生档案
            student = request.user.student_profile
            
            # 获取学生所在的所有班级
            student_classes = StudentClass.objects.filter(student=student, is_active=True)
            if student_classes.exists():
                # 获取所有班级的班级ID
                class_ids = [sc.class_obj.id for sc in student_classes]
                # 获取所有班级的通知和全局通知
                notices = Notice.objects.filter(Q(class_obj__in=class_ids) | Q(class_obj__isnull=True), status=1)
                serializer = NoticeSerializer(notices, many=True)
                return Response(serializer.data)
            return Response([], status=status.HTTP_200_OK)
        except AttributeError:
            return Response({'error': '用户不是学生'}, status=status.HTTP_403_FORBIDDEN)
    
    @action(detail=True, methods=['get'])
    def get_homework_detail(self, request, pk=None):
        """获取作业详情"""
        try:
            # 获取当前学生的学生档案
            student = request.user.student_profile
            # 获取作业详情
            homework = Homework.objects.get(id=pk, status=2)
            
            # 检查作业是否属于学生所在的任何一个班级
            is_in_class = StudentClass.objects.filter(
                student=student, 
                class_obj=homework.class_obj, 
                is_active=True
            ).exists()
            
            if is_in_class:
                serializer = HomeworkSerializer(homework)
                return Response(serializer.data)
            return Response({'error': '无权限访问该作业'}, status=status.HTTP_403_FORBIDDEN)
        except AttributeError:
            return Response({'error': '用户不是学生'}, status=status.HTTP_403_FORBIDDEN)
        except Homework.DoesNotExist:
            return Response({'error': '作业不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def submit_homework(self, request, pk=None):
        """提交作业"""
        try:
            # 获取当前学生的学生档案
            student = request.user.student_profile
            # 获取作业
            homework = Homework.objects.get(id=pk, status=2)
            # 检查作业是否属于学生所在的任何一个班级
            is_in_class = StudentClass.objects.filter(
                student=student.id, 
                class_obj=homework.class_obj.id, 
                is_active=True
            ).exists()
            if is_in_class:
                # 检查是否已提交
                submission, created = StudentHomework.objects.get_or_create(
                    homework=homework,
                    student=student,
                    defaults={'status': 1}
                )
                # 更新提交内容
                submission.submit_content = request.data.get('content')
                submission.submit_time = timezone.now()
                submission.status = 2  # 已提交
                submission.save()
                serializer = StudentHomeworkSerializer(submission)
                return Response(serializer.data)
            return Response({'error': '无权限访问该作业'}, status=status.HTTP_403_FORBIDDEN)
        except AttributeError:
            return Response({'error': '用户不是学生'}, status=status.HTTP_403_FORBIDDEN)
        except Homework.DoesNotExist:
            return Response({'error': '作业不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def download(self, request, pk=None):
        """记录资源下载并提供下载"""
        try:
            # 获取当前学生的学生档案
            student = request.user.student_profile
            
            # 尝试从班级资源中查找
            try:
                resource = ClassResource.objects.get(id=pk)
                resource_type = 'class'
                file_path = resource.resource_url
                filename = resource.resource_name
            except ClassResource.DoesNotExist:
                # 尝试从教学资源中查找
                try:
                    resource = TeachingResource.objects.get(id=pk)
                    resource_type = 'teaching'
                    file_path = resource.file
                    filename = resource.title
                except TeachingResource.DoesNotExist:
                    return Response({'error': '资源不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 检查学生是否有权限访问该资源
            if resource_type == 'class':
                # 对于班级资源，检查学生是否在该班级中
                is_in_class = StudentClass.objects.filter(
                student=student, 
                class_obj=resource.class_obj, 
                is_active=True
            ).exists()
                if not is_in_class:
                    return Response({'error': '无权限访问该资源'}, status=status.HTTP_403_FORBIDDEN)
            
            # 增加下载次数
            resource.download_count = (resource.download_count or 0) + 1
            resource.save()
            
            # 返回文件
            import mimetypes
            if file_path and default_storage.exists(file_path):
                file = default_storage.open(file_path, 'rb')
                response = FileResponse(file)
                
                # 设置正确的Content-Type
                content_type, _ = mimetypes.guess_type(file_path)
                if content_type:
                    response['Content-Type'] = content_type
                
                # 确保文件名包含扩展名
                if '.' not in filename and file_path:
                    # 从文件路径中提取扩展名
                    import os
                    _, ext = os.path.splitext(file_path)
                    filename += ext
                    
                response['Content-Disposition'] = f'attachment; filename="{filename}"'
                return response
            else:
                return Response({'error': '文件不存在'}, status=status.HTTP_404_NOT_FOUND)
            
        except AttributeError:
            return Response({'error': '用户不是学生'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': f'下载失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def draft(self, request, pk=None):
        """保存作业草稿"""
        try:
            # 获取当前学生的学生档案
            student = request.user.student_profile
            # 获取作业
            homework = Homework.objects.get(id=pk, status=2)
            # 检查作业是否属于学生所在的任何一个班级
            is_in_class = StudentClass.objects.filter(
                student=student.id, 
                class_obj=homework.class_obj.id, 
                is_active=True
            ).exists()
            if is_in_class:
                # 检查是否已存在草稿或提交
                submission, created = StudentHomework.objects.get_or_create(
                    homework=homework,
                    student=student,
                    defaults={'status': 1}
                )
                # 更新草稿内容
                submission.submit_content = request.data.get('content')
                submission.status = 1  # 草稿状态
                submission.save()
                serializer = StudentHomeworkSerializer(submission)
                return Response(serializer.data)
            return Response({'error': '无权限访问该作业'}, status=status.HTTP_403_FORBIDDEN)
        except AttributeError:
            return Response({'error': '用户不是学生'}, status=status.HTTP_403_FORBIDDEN)
        except Homework.DoesNotExist:
            return Response({'error': '作业不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        """获取作业提交历史"""
        try:
            # 获取当前学生的学生档案
            student = request.user.student_profile
            # 获取作业
            homework = Homework.objects.get(id=pk, status=2)
            # 检查作业是否属于学生所在的任何一个班级
            is_in_class = StudentClass.objects.filter(
                student=student.id, 
                class_obj=homework.class_obj.id, 
                is_active=True
            ).exists()
            if is_in_class:
                # 获取该学生的所有作业提交历史
                submissions = StudentHomework.objects.filter(
                    homework=homework,
                    student=student
                ).order_by('-submit_time')
                serializer = StudentHomeworkSerializer(submissions, many=True)
                return Response(serializer.data)
            return Response({'error': '无权限访问该作业'}, status=status.HTTP_403_FORBIDDEN)
        except AttributeError:
            return Response({'error': '用户不是学生'}, status=status.HTTP_403_FORBIDDEN)
        except Homework.DoesNotExist:
            return Response({'error': '作业不存在'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def upload_file(self, request, pk=None):
        """上传作业文件"""
        import logging
        logger = logging.getLogger(__name__)
        
        from .utils import FileUploadValidator, FileUploadHandler, get_client_ip
        
        try:
            # 获取当前学生的学生档案
            student = request.user.student_profile
            # 获取作业
            homework = Homework.objects.get(id=pk, status=2)
            # 检查作业是否属于学生所在的任何一个班级
            is_in_class = StudentClass.objects.filter(
                student=student.id, 
                class_obj=homework.class_obj.id, 
                is_active=True
            ).exists()
            if is_in_class:
                # 获取上传的文件
                file = request.FILES.get('file')
                if not file:
                    return Response({'error': '缺少文件参数'}, status=status.HTTP_400_BAD_REQUEST)
                
                # 验证文件
                is_valid, error_msg = FileUploadValidator.validate(file)
                if not is_valid:
                    logger.warning(f"File validation failed: {error_msg}")
                    return Response({'error': error_msg}, status=status.HTTP_400_BAD_REQUEST)
                
                # 获取或创建作业提交记录
                submission, created = StudentHomework.objects.get_or_create(
                    homework=homework,
                    student=student,
                    defaults={'status': 1, 'submit_time': timezone.now()}
                )
                
                # 上传文件
                upload_handler = FileUploadHandler(storage_path_prefix='homework_files')
                file_info = upload_handler.save_file(
                    file, 
                    subfolder=f'{student.id}/{homework.id}',
                    get_client_ip=lambda: get_client_ip(request)
                )
                
                # 创建文件记录
                file_record = StudentHomeworkFile.objects.create(
                    student_homework=submission,
                    file_name=file.name,
                    file_path=file_info['file_path'],
                    storage_path=file_info['storage_path'],
                    file_size=file_info['file_size'],
                    file_hash=file_info['file_hash'],
                    mime_type=file_info['mime_type'],
                    upload_ip=file_info['upload_ip']
                )
                
                serializer = StudentHomeworkFileSerializer(file_record)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({'error': '无权限访问该作业'}, status=status.HTTP_403_FORBIDDEN)
        except AttributeError:
            return Response({'error': '用户不是学生'}, status=status.HTTP_403_FORBIDDEN)
        except Homework.DoesNotExist:
            return Response({'error': '作业不存在'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Failed to upload homework file: {e}")
            return Response({'error': f'文件上传失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'])
    def mark_notice_as_read(self, request, pk=None):
        """标记通知为已读"""
        try:
            # 获取当前学生的学生档案
            student = request.user.student_profile
            # 获取通知
            notice = Notice.objects.get(id=pk, status=1)
            # 检查通知是否属于学生所在班级或全体通知
            class_obj = Class.objects.filter(name=student.class_name).first()
            if class_obj and (notice.class_obj == class_obj or notice.class_obj is None):
                # 标记为已读
                read_record, created = StudentNoticeRead.objects.get_or_create(
                    notice=notice,
                    student=student,
                    defaults={'is_read': 1, 'read_time': timezone.now()}
                )
                if not created:
                    read_record.is_read = 1
                    read_record.read_time = timezone.now()
                    read_record.save()
                # 更新通知的阅读计数
                notice.read_count += 1
                notice.save()
                return Response({'message': '通知已标记为已读'})
            return Response({'error': '无权限访问该通知'}, status=status.HTTP_403_FORBIDDEN)
        except AttributeError:
            return Response({'error': '用户不是学生'}, status=status.HTTP_403_FORBIDDEN)
        except Notice.DoesNotExist:
            return Response({'error': '通知不存在'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def leave_class(self, request):
        """学生退出班级"""
        try:
            # 获取当前学生的学生档案
            student = request.user.student_profile
            
            # 获取要退出的班级ID
            class_id = request.data.get('class_id')
            if not class_id:
                return Response({'error': '班级ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 查找学生与班级的关系
            student_class = StudentClass.objects.filter(
                student=student,
                class_obj=class_id,
                is_active=True
            ).first()
            
            if not student_class:
                return Response({'error': '您未加入该班级或已退出'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 标记为已退出班级
            student_class.is_active = False
            student_class.left_at = timezone.now()
            student_class.save()
            
            return Response({'message': '成功退出班级'}, status=status.HTTP_200_OK)
        except AttributeError:
            return Response({'error': '用户不是学生'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({'error': f'退出班级失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


class ReportViewSet(viewsets.ModelViewSet):
    """报告管理视图集"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['class_obj', 'report_type', 'status']
    search_fields = ['title']
    ordering_fields = ['generated_at', 'title']
    
    def get_queryset(self):
        """只返回当前教师的报告"""
        try:
            # 确保当前用户有对应的Teacher对象
            teacher = self.request.user.teacher_profile
            queryset = Report.objects.filter(teacher=teacher).select_related(
                'class_obj', 'student'
            )
            return queryset
        except AttributeError:
            # 如果没有Teacher对象，返回空查询集
            return Report.objects.none()
    
    def get_serializer_class(self):
        return ReportSerializer
    
    def generate_report_data(self, report_type, class_obj, student, start_date, end_date):
        """生成报告数据"""
        report_data = {
            'title': f"{class_obj.name}学习报告",
            'generated_at': timezone.now().strftime('%Y-%m-%d %H:%M:%S'),
            'report_type': report_type,
        }
        
        # 学生个人报告
        if report_type == 'student':
            report_data['title'] = f"{student.student_name}学习报告"
            
            # 学习进度
            progress_stats = StudentLearningProgress.objects.filter(
                student=student,
                created_at__range=[start_date, end_date]
            ).aggregate(
                total_chapters=Count('id'),
                completed_chapters=Count('id', filter=Q(learn_status=3)),
                total_learn_time=Sum('learn_time')
            )
            
            completion_rate = 0
            if progress_stats['total_chapters'] > 0:
                completion_rate = round((progress_stats['completed_chapters'] / progress_stats['total_chapters']) * 100)
            
            report_data['progress'] = {
                'totalChapters': progress_stats['total_chapters'] or 0,
                'completedChapters': progress_stats['completed_chapters'] or 0,
                'completionRate': completion_rate,
                'totalTime': round((progress_stats['total_learn_time'] or 0) / 60, 1)  # 转换为小时
            }
            
            # 作业完成情况
            homework_stats = StudentHomework.objects.filter(
                student=student,
                homework__end_time__range=[start_date, end_date]
            ).aggregate(
                total=Count('id'),
                submitted=Count('id', filter=Q(status__gte=1)),
                avgScore=Avg('score', filter=Q(score__isnull=False))
            )
            
            submission_rate = 0
            if homework_stats['total'] > 0:
                submission_rate = round((homework_stats['submitted'] / homework_stats['total']) * 100)
            
            report_data['homework'] = {
                'total': homework_stats['total'] or 0,
                'submitted': homework_stats['submitted'] or 0,
                'avgScore': round(homework_stats['avgScore'] or 0),
                'submissionRate': submission_rate
            }
        
        # 班级整体报告
        elif report_type == 'class':
            # 获取班级学生
            students = Student.objects.filter(student_classes__class_obj=class_obj, student_classes__is_active=True)
            total_students = students.count()
            
            # 班级学习进度
            class_progress = StudentLearningProgress.objects.filter(
                student__in=students,
                created_at__range=[start_date, end_date]
            ).aggregate(
                total_chapters=Count('id'),
                completed_chapters=Count('id', filter=Q(learn_status=3)),
                total_learn_time=Sum('learn_time')
            )
            
            avg_completion_rate = 0
            if class_progress['total_chapters'] > 0:
                avg_completion_rate = round((class_progress['completed_chapters'] / class_progress['total_chapters']) * 100)
            
            avg_learn_time = 0
            if total_students > 0:
                avg_learn_time = round((class_progress['total_learn_time'] or 0) / total_students / 60, 1)  # 人均小时数
            
            report_data['progress'] = {
                'totalChapters': class_progress['total_chapters'] or 0,
                'completedChapters': class_progress['completed_chapters'] or 0,
                'completionRate': avg_completion_rate,
                'totalTime': round((class_progress['total_learn_time'] or 0) / 60, 1),  # 总小时数
                'avgLearnTime': avg_learn_time
            }
            
            # 班级作业统计
            class_homework = StudentHomework.objects.filter(
                student__in=students,
                homework__end_time__range=[start_date, end_date]
            ).aggregate(
                total=Count('id'),
                submitted=Count('id', filter=Q(status__gte=1)),
                avgScore=Avg('score', filter=Q(score__isnull=False))
            )
            
            avg_submission_rate = 0
            if class_homework['total'] > 0:
                avg_submission_rate = round((class_homework['submitted'] / class_homework['total']) * 100)
            
            report_data['homework'] = {
                'total': class_homework['total'] or 0,
                'submitted': class_homework['submitted'] or 0,
                'avgScore': round(class_homework['avgScore'] or 0),
                'submissionRate': avg_submission_rate
            }
            
            # 学生表现排名
            student_performances = []
            for student in students:
                student_progress = StudentLearningProgress.objects.filter(
                    student=student,
                    created_at__range=[start_date, end_date]
                ).aggregate(
                    completed_chapters=Count('id', filter=Q(learn_status=3)),
                    total_learn_time=Sum('learn_time')
                )
                
                student_homework = StudentHomework.objects.filter(
                    student=student,
                    homework__end_time__range=[start_date, end_date]
                ).aggregate(
                    avgScore=Avg('score', filter=Q(score__isnull=False))
                )
                
                student_performances.append({
                    'student_name': student.student_name,
                    'student_no': student.student_no,
                    'completed_chapters': student_progress['completed_chapters'] or 0,
                    'total_learn_time': student_progress['total_learn_time'] or 0,
                    'avg_score': round(student_homework['avgScore'] or 0)
                })
            
            # 按平均成绩排序
            student_performances.sort(key=lambda x: x['avg_score'], reverse=True)
            report_data['student_performances'] = student_performances
        
        # 对比分析报告
        elif report_type == 'comparison':
            # 这里可以实现对比分析逻辑，例如不同班级或不同时间段的对比
            report_data['comparison'] = {
                'message': '对比分析报告数据生成中'
            }
        
        return report_data
    
    def create(self, request, *args, **kwargs):
        """生成报告"""
        try:
            # 获取报告参数
            report_type = request.data.get('report_type')
            class_id = request.data.get('class_id')
            student_id = request.data.get('student_id')
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')
            include_progress = request.data.get('include_progress', True)
            include_homework = request.data.get('include_homework', True)
            include_attendance = request.data.get('include_attendance', False)
            include_performance = request.data.get('include_performance', True)
            export_format = request.data.get('export_format', 'pdf')
            
            # 验证参数
            if not all([report_type, class_id, start_date, end_date]):
                return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 验证报告类型
            if report_type not in ['student', 'class', 'comparison']:
                return Response({'error': '无效的报告类型'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取班级对象
            try:
                class_obj = Class.objects.get(id=class_id, teacher=request.user.teacher_profile)
            except Class.DoesNotExist:
                return Response({'error': '班级不存在'}, status=status.HTTP_404_NOT_FOUND)
            
            # 获取学生对象（如果是学生报告）
            student = None
            if report_type == 'student':
                if not student_id:
                    return Response({'error': '学生个人报告必须指定学生'}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    student = Student.objects.get(id=student_id, student_classes__class_obj=class_obj, student_classes__is_active=True)
                except Student.DoesNotExist:
                    return Response({'error': '学生不存在或不在该班级'}, status=status.HTTP_404_NOT_FOUND)
            
            # 转换日期格式
            try:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': '日期格式无效，应为YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
            
            # 生成报告标题
            title = f"{class_obj.name}学习报告"
            if report_type == 'student':
                title = f"{student.student_name}学习报告"
            
            # 创建报告记录
            report = Report.objects.create(
                teacher=request.user.teacher_profile,
                class_obj=class_obj,
                student=student,
                report_type=report_type,
                title=title,
                start_date=start_date,
                end_date=end_date,
                include_progress=include_progress,
                include_homework=include_homework,
                include_attendance=include_attendance,
                include_performance=include_performance,
                export_format=export_format,
                status=1  # 生成中
            )
            
            # 生成报告数据
            report_data = self.generate_report_data(report_type, class_obj, student, start_date, end_date)
            
            # 更新报告数据
            report.report_data = report_data
            report.status = 2  # 已完成
            report.save()
            
            # 返回报告信息
            serializer = self.get_serializer(report)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({'error': f'生成报告失败: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """下载报告"""
        report = self.get_object()
        
        # 这里可以实现报告文件生成和下载逻辑
        # 目前返回模拟数据
        response = HttpResponse("报告内容", content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{report.title}.pdf"'
        return response
    
    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """预览报告"""
        report = self.get_object()
        serializer = self.get_serializer(report)
        return Response(serializer.data['report_data'])


class StudentDataViewSet(viewsets.ViewSet):
    """教师端学生数据交互接口 - 确保教师只能访问其班级的学生数据"""
    permission_classes = [IsAuthenticated]
    
    def _get_teacher(self, request):
        """获取当前教师的Teacher对象"""
        try:
            return request.user.teacher_profile
        except AttributeError:
            raise serializers.ValidationError({'error': '用户没有关联的教师信息'})
    
    def _check_student_access(self, request, student_id):
        """检查教师是否有权限访问该学生的数据"""
        teacher = self._get_teacher(request)
        
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            raise serializers.ValidationError({'error': '学生不存在'})
        
        # 检查学生是否属于该教师的班级
        if student.class_name:
            teacher_classes = Class.objects.filter(teacher=teacher, name=student.class_name)
            if not teacher_classes.exists():
                raise PermissionDenied('您没有权限访问该学生的数据')
        
        return student
    
    @action(detail=False, methods=['get'])
    def ai_interactions(self, request):
        """获取指定学生的AI交互记录"""
        import logging
        logger = logging.getLogger(__name__)
        
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response(
                {'error': 'student_id参数是必需的'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            student = self._check_student_access(request, student_id)
            
            # 获取学生的用户对象
            if not student.user:
                return Response(
                    {'error': '该学生未关联用户账号'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 获取AI交互记录
            interactions = AIInteractionRecord.objects.filter(
                user=student.user
            ).order_by('-created_at')
            
            # 支持分页
            page = self.paginate_queryset(interactions)
            if page is not None:
                serializer = AIInteractionRecordSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = AIInteractionRecordSerializer(interactions, many=True)
            return Response(serializer.data)
            
        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.error(f"获取学生AI交互记录失败: {e}", exc_info=True)
            return Response(
                {'error': f'获取数据失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def learning_progress(self, request):
        """获取指定学生的学习进度"""
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response(
                {'error': 'student_id参数是必需的'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            student = self._check_student_access(request, student_id)
            
            if not student.user:
                return Response(
                    {'error': '该学生未关联用户账号'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 获取学习记录
            learning_records = LearningRecord.objects.filter(
                user=student.user
            ).select_related('book', 'chapter').order_by('-last_learn_time')
            
            # 计算统计信息
            total_progress = learning_records.aggregate(
                avg_progress=Avg('progress'),
                total_chapters=Count('id')
            )
            
            # 获取最近的学习记录
            recent_records = learning_records[:10]
            
            from apps.learning.serializers import LearningRecordSerializer
            serializer = LearningRecordSerializer(recent_records, many=True)
            
            return Response({
                'student_id': student.id,
                'student_name': student.student_name,
                'statistics': total_progress,
                'recent_records': serializer.data
            })
            
        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response(
                {'error': f'获取数据失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def practice_records(self, request):
        """获取指定学生的练习记录"""
        student_id = request.query_params.get('student_id')
        if not student_id:
            return Response(
                {'error': 'student_id参数是必需的'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            student = self._check_student_access(request, student_id)
            
            if not student.user:
                return Response(
                    {'error': '该学生未关联用户账号'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # 获取练习记录
            practice_records = PracticeRecord.objects.filter(
                user=student.user
            ).select_related('book', 'chapter').order_by('-completed_time')
            
            # 支持分页
            page = self.paginate_queryset(practice_records)
            if page is not None:
                from apps.learning.serializers import PracticeRecordSerializer
                serializer = PracticeRecordSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            from apps.learning.serializers import PracticeRecordSerializer
            serializer = PracticeRecordSerializer(practice_records, many=True)
            return Response(serializer.data)
            
        except PermissionDenied as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            return Response(
                {'error': f'获取数据失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def class_students_summary(self, request):
        """获取班级所有学生的数据摘要（用于教师端概览）"""
        class_id = request.query_params.get('class_id')
        if not class_id:
            return Response(
                {'error': 'class_id参数是必需的'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            teacher = self._get_teacher(request)
            
            # 验证班级是否属于该教师
            try:
                class_obj = Class.objects.get(id=class_id, teacher=teacher)
            except Class.DoesNotExist:
                return Response(
                    {'error': '班级不存在或您没有权限访问'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # 获取该班级的所有学生
            students = Student.objects.filter(class_name=class_obj.name)
            
            summary = []
            for student in students:
                if not student.user:
                    continue
                
                # 获取学生的AI交互统计
                ai_count = AIInteractionRecord.objects.filter(user=student.user).count()
                
                # 获取学习进度统计
                learning_stats = LearningRecord.objects.filter(
                    user=student.user
                ).aggregate(
                    avg_progress=Avg('progress'),
                    total_chapters=Count('id')
                )
                
                # 获取练习记录统计
                practice_stats = PracticeRecord.objects.filter(
                    user=student.user
                ).aggregate(
                    avg_score=Avg('score'),
                    completed_count=Count('id', filter=Q(completed=True))
                )
                
                summary.append({
                    'student_id': student.id,
                    'student_name': student.student_name,
                    'student_no': student.student_no,
                    'ai_interaction_count': ai_count,
                    'learning_progress': learning_stats['avg_progress'] or 0,
                    'total_chapters': learning_stats['total_chapters'] or 0,
                    'avg_practice_score': practice_stats['avg_score'] or 0,
                    'completed_practices': practice_stats['completed_count'] or 0
                })
            
            return Response({
                'class_id': class_obj.id,
                'class_name': class_obj.name,
                'student_count': len(summary),
                'students': summary
            })
            
        except Exception as e:
            return Response(
                {'error': f'获取数据失败: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def paginate_queryset(self, queryset):
        """分页支持"""
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        return paginator.paginate_queryset(queryset, self.request)
    
    def get_paginated_response(self, data):
        """返回分页响应"""
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        return paginator.get_paginated_response(data)


class TeacherAIAssistantView(AIAssistantView):
    """
    教师端AI助手视图
    继承基础AI助手功能，增加学生数据查询和上下文理解能力
    """
    permission_classes = [IsAuthenticated]
    
    def _get_teacher(self, request):
        """获取当前教师的Teacher对象"""
        try:
            return request.user.teacher_profile
        except AttributeError:
            raise serializers.ValidationError({'error': '用户没有关联的教师信息'})
    
    def _get_student_context(self, request, student_id=None, class_id=None):
        """
        获取学生相关的上下文数据
        用于增强AI回答的准确性和相关性
        """
        context_data = {
            'student_info': None,
            'learning_progress': None,
            'practice_records': None,
            'ai_interactions': None,
            'class_info': None
        }
        
        try:
            teacher = self._get_teacher(request)
            
            # 如果提供了学生ID，获取该学生的详细信息
            if student_id:
                try:
                    student = Student.objects.get(id=student_id)
                    # 验证权限
                    if student.class_name:
                        teacher_classes = Class.objects.filter(teacher=teacher, name=student.class_name)
                        if teacher_classes.exists() and student.user:
                            # 获取学生学习进度
                            learning_records = LearningRecord.objects.filter(
                                user=student.user
                            ).select_related('book', 'chapter')[:5]
                            
                            # 获取练习记录
                            practice_records = PracticeRecord.objects.filter(
                                user=student.user
                            ).select_related('book', 'chapter')[:5]
                            
                            # 获取AI交互记录统计
                            ai_count = AIInteractionRecord.objects.filter(user=student.user).count()
                            
                            context_data['student_info'] = {
                                'id': student.id,
                                'name': student.student_name,
                                'student_no': student.student_no,
                                'class_name': student.class_name
                            }
                            context_data['learning_progress'] = [
                                {
                                    'book': record.book.title if record.book else '',
                                    'chapter': record.chapter.title if record.chapter else '',
                                    'progress': record.progress
                                }
                                for record in learning_records
                            ]
                            context_data['practice_records'] = [
                                {
                                    'book': record.book.title if record.book else '',
                                    'chapter': record.chapter.title if record.chapter else '',
                                    'score': record.score,
                                    'completed': record.completed
                                }
                                for record in practice_records
                            ]
                            context_data['ai_interactions'] = {
                                'total_count': ai_count
                            }
                except Student.DoesNotExist:
                    pass
            
            # 如果提供了班级ID，获取班级信息
            if class_id:
                try:
                    class_obj = Class.objects.get(id=class_id, teacher=teacher)
                    students = Student.objects.filter(class_name=class_obj.name)
                    
                    context_data['class_info'] = {
                        'id': class_obj.id,
                        'name': class_obj.name,
                        'student_count': students.count(),
                        'book': class_obj.book.title if class_obj.book else ''
                    }
                except Class.DoesNotExist:
                    pass
                    
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"获取学生上下文数据失败: {e}")
        
        return context_data
    
    def _build_enhanced_prompt(self, question, context_data):
        """
        构建增强的提示词，包含学生数据上下文
        """
        base_prompt = "你是一个专业的教学助手，专门帮助教师分析学生学习情况、提供教学建议和解答教学相关问题。"
        
        context_parts = []
        
        if context_data.get('student_info'):
            student = context_data['student_info']
            context_parts.append(f"\n当前关注的学生信息：")
            context_parts.append(f"- 姓名：{student['name']}")
            context_parts.append(f"- 学号：{student['student_no']}")
            context_parts.append(f"- 班级：{student['class_name']}")
        
        if context_data.get('learning_progress'):
            context_parts.append(f"\n学生学习进度：")
            for progress in context_data['learning_progress'][:3]:
                context_parts.append(f"- {progress['book']} - {progress['chapter']}: {progress['progress']}%")
        
        if context_data.get('practice_records'):
            context_parts.append(f"\n学生练习记录：")
            for practice in context_data['practice_records'][:3]:
                status = "已完成" if practice['completed'] else "未完成"
                context_parts.append(f"- {practice['book']} - {practice['chapter']}: 得分{practice['score']}, {status}")
        
        if context_data.get('ai_interactions'):
            ai_info = context_data['ai_interactions']
            context_parts.append(f"\n学生AI交互次数：{ai_info['total_count']}次")
        
        if context_data.get('class_info'):
            class_info = context_data['class_info']
            context_parts.append(f"\n班级信息：")
            context_parts.append(f"- 班级名称：{class_info['name']}")
            context_parts.append(f"- 学生人数：{class_info['student_count']}")
            context_parts.append(f"- 使用教材：{class_info['book']}")
        
        if context_parts:
            context_text = "\n".join(context_parts)
            enhanced_prompt = f"{base_prompt}\n\n{context_text}\n\n请基于以上信息，为教师提供专业、有针对性的回答。"
        else:
            enhanced_prompt = base_prompt
        
        return enhanced_prompt
    
    def post(self, request):
        """
        处理教师端AI助手请求
        支持基于学生数据的智能问答
        """
        import logging
        import time
        import uuid
        logger = logging.getLogger(__name__)
        
        # 获取用户问题
        user_question = request.data.get('question', '')
        session_id = request.data.get('session_id', None)
        student_id = request.data.get('student_id', None)
        class_id = request.data.get('class_id', None)
        context = request.data.get('context', {})
        
        if not user_question.strip():
            return Response(
                {'error': '问题不能为空'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 如果没有session_id，生成一个新的
        if not session_id:
            session_id = str(uuid.uuid4())
        
        start_time = time.time()
        
        try:
            # 获取学生数据上下文
            student_context = self._get_student_context(request, student_id, class_id)
            
            # 构建增强的提示词
            enhanced_prompt = self._build_enhanced_prompt(user_question, student_context)
            
            # 生成AI回复
            response_content = self._generate_with_context(user_question, enhanced_prompt)
            response_time = time.time() - start_time
            
            # 记录交互历史
            try:
                AIInteractionRecord.objects.create(
                    user=request.user,
                    interaction_type='question',
                    user_input=user_question,
                    ai_response=response_content,
                    session_id=session_id,
                    context={
                        **context,
                        'student_id': student_id,
                        'class_id': class_id,
                        'student_context': student_context,
                        'is_teacher_query': True
                    },
                    response_time=response_time,
                    tokens_used=0
                )
            except Exception as e:
                logger.error(f"保存教师AI交互记录失败: {e}")
            
            # 返回AI回复
            return Response({
                'question': user_question,
                'answer': response_content,
                'session_id': session_id,
                'response_time': round(response_time, 2),
                'context_used': {
                    'has_student_context': bool(student_context.get('student_info')),
                    'has_class_context': bool(student_context.get('class_info'))
                }
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"教师AI助手处理请求时出错: {e}", exc_info=True)
            return Response(
                {'error': f'处理请求时出错: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _generate_with_context(self, question, enhanced_prompt):
        """
        使用增强的提示词生成AI回复
        """
        if not self.client:
            return "很抱歉，AI助手服务暂时不可用，请稍后再试。"
        
        try:
            completion = self.client.chat.completions.create(
                model="doubao-seed-1-6-251015",
                messages=[
                    {"role": "system", "content": enhanced_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.7,
                max_tokens=600  # 教师端可以返回更详细的回答
            )
            
            if completion and completion.choices:
                response_content = completion.choices[0].message.content
                response_content = response_content.replace('```', '').replace('\n\n', '\n')
                return response_content
            return "很抱歉，无法生成回复。"
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"生成教师AI回复时出错: {e}")
            return "很抱歉，AI助手服务暂时不可用，请稍后再试。"

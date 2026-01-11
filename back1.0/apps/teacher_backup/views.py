from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg, Q
from .models import Class, Assignment, AssignmentSubmission, Notification, TeachingResource, TeacherProfile, StudentProfile
from .serializers import (
    ClassSerializer, ClassDetailSerializer, AssignmentSerializer,
    AssignmentSubmissionSerializer, NotificationSerializer,
    TeachingResourceSerializer, TeacherProfileSerializer,
    StudentProfileSerializer, UserSerializer
)
from django.contrib.auth import get_user_model
from apps.learning.models import LearningRecord, PracticeRecord, HeatmapData

User = get_user_model()


class ClassViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['major', 'grade']
    search_fields = ['name', 'description']
    ordering_fields = ['created_at', 'name']

    def get_queryset(self):
        queryset = Class.objects.filter(teacher=self.request.user)
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ClassDetailSerializer
        return ClassSerializer

    @action(detail=True, methods=['post'])
    def add_student(self, request, pk=None):
        class_obj = self.get_object()
        student_id = request.data.get('student_id')
        try:
            student = User.objects.get(id=student_id, role='student')
            class_obj.students.add(student)
            return Response({'message': '学生添加成功'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': '学生不存在'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def remove_student(self, request, pk=None):
        class_obj = self.get_object()
        student_id = request.data.get('student_id')
        try:
            student = User.objects.get(id=student_id)
            class_obj.students.remove(student)
            return Response({'message': '学生移除成功'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': '学生不存在'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def analytics(self, request, pk=None):
        class_obj = self.get_object()
        students = class_obj.students.all()

        total_students = students.count()
        active_students = students.filter(learning_records__isnull=False).distinct().count()
        avg_learning_time = HeatmapData.objects.filter(user__in=students).aggregate(
            avg_time=Avg('minutes')
        )['avg_time'] or 0

        return Response({
            'total_students': total_students,
            'active_students': active_students,
            'avg_learning_time': round(avg_learning_time, 2)
        })


class AssignmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['classes']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'due_date']

    def get_queryset(self):
        queryset = Assignment.objects.filter(teacher=self.request.user)
        return queryset

    def get_serializer_class(self):
        return AssignmentSerializer

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        assignment = self.get_object()
        submissions = assignment.submissions.all()
        serializer = AssignmentSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def grade(self, request, pk=None):
        assignment = self.get_object()
        submission_id = request.data.get('submission_id')
        score = request.data.get('score')
        feedback = request.data.get('feedback', '')

        try:
            submission = AssignmentSubmission.objects.get(id=submission_id, assignment=assignment)
            submission.score = score
            submission.feedback = feedback
            submission.graded_at = timezone.now()
            submission.graded_by = request.user
            submission.save()

            return Response({'message': '批改成功'}, status=status.HTTP_200_OK)
        except AssignmentSubmission.DoesNotExist:
            return Response({'error': '提交记录不存在'}, status=status.HTTP_404_NOT_FOUND)


class NotificationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['type', 'is_read']
    ordering_fields = ['created_at']

    def get_queryset(self):
        queryset = Notification.objects.filter(receiver=self.request.user)
        return queryset

    def get_serializer_class(self):
        return NotificationSerializer

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        Notification.objects.filter(receiver=request.user, is_read=False).update(is_read=True)
        return Response({'message': '全部标记为已读'}, status=status.HTTP_200_OK)


class TeachingResourceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['resource_type', 'category', 'is_public']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title']

    def get_queryset(self):
        queryset = TeachingResource.objects.filter(teacher=self.request.user)
        return queryset

    def get_serializer_class(self):
        return TeachingResourceSerializer

    def perform_create(self, serializer):
        file = self.request.FILES.get('file')
        if file:
            serializer.save(teacher=self.request.user, file_size=file.size)
        else:
            serializer.save(teacher=self.request.user)


class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'student_profile__student_id']
    ordering_fields = ['username', 'created_at']

    def get_queryset(self):
        queryset = User.objects.filter(role='student')
        class_id = self.request.query_params.get('class_id')
        if class_id:
            queryset = queryset.filter(student_classes__id=class_id)
        return queryset

    def get_serializer_class(self):
        return UserSerializer

    @action(detail=True, methods=['get'])
    def profile(self, request, pk=None):
        student = self.get_object()
        try:
            profile = student.student_profile
            serializer = StudentProfileSerializer(profile)
            return Response(serializer.data)
        except StudentProfile.DoesNotExist:
            return Response({'error': '学生档案不存在'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def learning_progress(self, request, pk=None):
        student = self.get_object()
        learning_records = LearningRecord.objects.filter(user=student)
        
        total_records = learning_records.count()
        avg_progress = learning_records.aggregate(avg_progress=Avg('progress'))['avg_progress'] or 0
        
        return Response({
            'total_records': total_records,
            'avg_progress': round(avg_progress, 2)
        })

    @action(detail=True, methods=['get'])
    def practice_records(self, request, pk=None):
        student = self.get_object()
        practice_records = PracticeRecord.objects.filter(user=student)
        
        total_practices = practice_records.count()
        avg_score = practice_records.aggregate(avg_score=Avg('score'))['avg_score'] or 0
        completed_count = practice_records.filter(completed=True).count()
        
        return Response({
            'total_practices': total_practices,
            'avg_score': round(avg_score, 2),
            'completed_count': completed_count
        })


class AnalyticsViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = request.user
        
        if user.role != 'teacher':
            return Response({'error': '权限不足'}, status=status.HTTP_403_FORBIDDEN)
        
        classes = user.classes.all()
        total_students = sum(c.students.count() for c in classes)
        total_assignments = user.assignments.count()
        
        return Response({
            'total_classes': classes.count(),
            'total_students': total_students,
            'total_assignments': total_assignments
        })

from rest_framework import serializers
from .models import Class, Assignment, AssignmentSubmission, Notification, TeachingResource, TeacherProfile, StudentProfile
from django.contrib.auth import get_user_model
from apps.books.serializers import BookListSerializer as BookSerializer, ChapterSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'avatar']


class TeacherProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = TeacherProfile
        fields = '__all__'


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    class_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = '__all__'

    def get_class_name(self, obj):
        classes = obj.user.student_classes.all()
        return [c.name for c in classes]


class ClassSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)
    student_count = serializers.SerializerMethodField()

    class Meta:
        model = Class
        fields = '__all__'

    def get_student_count(self, obj):
        return obj.students.count()


class ClassDetailSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)
    students = StudentProfileSerializer(source='student_profile', many=True, read_only=True)

    class Meta:
        model = Class
        fields = '__all__'


class AssignmentSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)
    books = BookSerializer(many=True, read_only=True)
    chapters = ChapterSerializer(many=True, read_only=True)
    classes = ClassSerializer(many=True, read_only=True)
    submission_count = serializers.SerializerMethodField()
    graded_count = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = '__all__'

    def get_submission_count(self, obj):
        return obj.submissions.count()

    def get_graded_count(self, obj):
        return obj.submissions.filter(graded_at__isnull=False).count()


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    assignment = AssignmentSerializer(read_only=True)
    student = UserSerializer(read_only=True)
    graded_by = UserSerializer(read_only=True)

    class Meta:
        model = AssignmentSubmission
        fields = '__all__'


class NotificationSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    receiver = UserSerializer(read_only=True)

    class Meta:
        model = Notification
        fields = '__all__'


class TeachingResourceSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)

    class Meta:
        model = TeachingResource
        fields = '__all__'

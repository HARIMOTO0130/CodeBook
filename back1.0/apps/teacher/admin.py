from django.contrib import admin
from .models import Class, Assignment, AssignmentSubmission, Notification, TeachingResource, TeacherProfile, StudentProfile


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'major', 'grade', 'created_at']
    list_filter = ['major', 'grade', 'created_at']
    search_fields = ['name', 'description', 'teacher__username']
    filter_horizontal = ['students']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'due_date', 'total_score', 'created_at']
    list_filter = ['created_at', 'due_date']
    search_fields = ['title', 'description', 'teacher__username']
    filter_horizontal = ['books', 'chapters', 'classes']


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'student', 'score', 'is_late', 'submitted_at', 'graded_at']
    list_filter = ['is_late', 'submitted_at', 'graded_at']
    search_fields = ['assignment__title', 'student__username']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'sender', 'receiver', 'type', 'is_read', 'created_at']
    list_filter = ['type', 'is_read', 'created_at']
    search_fields = ['title', 'content', 'sender__username', 'receiver__username']


@admin.register(TeachingResource)
class TeachingResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'resource_type', 'category', 'is_public', 'created_at']
    list_filter = ['resource_type', 'category', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'teacher__username']


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'title', 'office']
    list_filter = ['department', 'title']
    search_fields = ['user__username', 'department', 'title']


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'student_id', 'major', 'grade', 'enrollment_date']
    list_filter = ['major', 'grade', 'enrollment_date']
    search_fields = ['user__username', 'student_id', 'major', 'grade']

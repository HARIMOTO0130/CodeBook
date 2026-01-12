from django.contrib import admin
from .models import (
    Class, Teacher, Student, Homework, StudentHomework, Notice,
    ClassResource, TeachingResource, CourseDesign, StudentLearningProgress
)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'teacher', 'major', 'grade', 'created_at']
    list_filter = ['major', 'grade', 'created_at']
    search_fields = ['name', 'description', 'teacher__username']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['teacher_name', 'user', 'department', 'position', 'created_at']
    list_filter = ['department', 'position', 'created_at']
    search_fields = ['teacher_name', 'user__username', 'department', 'position']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    def display_classes(self, obj):
        """显示学生所属班级"""
        return ', '.join([cls.name for cls in obj.class_obj.all()])
    
    display_classes.short_description = '班级'
    
    list_display = ['student_name', 'student_no', 'display_classes', 'gender', 'phone', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['student_name', 'student_no', 'phone']


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ['homework_name', 'teacher', 'class_obj', 'chapter', 'end_time', 'total_score', 'created_at']
    list_filter = ['class_obj', 'chapter', 'created_at', 'end_time']
    search_fields = ['homework_name', 'homework_content', 'teacher__username']


@admin.register(StudentHomework)
class StudentHomeworkAdmin(admin.ModelAdmin):
    list_display = ['homework', 'student', 'score', 'status', 'submit_time', 'grade_time']
    list_filter = ['status', 'submit_time', 'grade_time']
    search_fields = ['homework__homework_name', 'student__student_name']


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ['notice_title', 'teacher', 'class_obj', 'publish_time', 'status']
    list_filter = ['class_obj', 'status', 'publish_time']
    search_fields = ['notice_title', 'notice_content', 'teacher__username']


@admin.register(TeachingResource)
class TeachingResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'teacher', 'resource_type', 'category', 'created_at']
    list_filter = ['resource_type', 'category', 'is_public', 'created_at']
    search_fields = ['title', 'description', 'teacher__username']


@admin.register(ClassResource)
class ClassResourceAdmin(admin.ModelAdmin):
    list_display = ['resource_name', 'class_obj', 'teacher', 'resource_type', 'upload_time']
    list_filter = ['class_obj', 'resource_type', 'upload_time']
    search_fields = ['resource_name', 'resource_desc', 'teacher__username']


@admin.register(CourseDesign)
class CourseDesignAdmin(admin.ModelAdmin):
    list_display = ['design_title', 'class_obj', 'chapter', 'teacher', 'teaching_hours', 'created_at']
    list_filter = ['class_obj', 'chapter', 'created_at']
    search_fields = ['design_title', 'design_content', 'teacher__username']


@admin.register(StudentLearningProgress)
class StudentLearningProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'chapter', 'learn_time', 'learn_status', 'last_learn_time']
    list_filter = ['learn_status', 'last_learn_time']
    search_fields = ['student__student_name', 'chapter__title']

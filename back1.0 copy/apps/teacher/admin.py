from django.contrib import admin
from .models import (
    Class, Student, StudentLearningProgress, Homework, StudentHomework,
    Notice, StudentNoticeRead, ClassResource, TeachingResource, CourseDesign,
    TeacherSetting, TeachingToolLog
)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    """班级管理"""
    list_display = ['id', 'name', 'teacher', 'book', 'major', 'grade', 'status', 'created_at']
    list_filter = ['major', 'grade', 'status', 'created_at']
    search_fields = ['name', 'major', 'description']
    list_per_page = 20
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """学生管理"""
    list_display = ['id', 'student_no', 'student_name', 'gender', 'phone', 'class_obj', 'status', 'created_at']
    list_filter = ['gender', 'status', 'class_obj', 'created_at']
    search_fields = ['student_no', 'student_name', 'phone']
    list_per_page = 50
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(StudentLearningProgress)
class StudentLearningProgressAdmin(admin.ModelAdmin):
    """学生学习进度管理"""
    list_display = ['id', 'student', 'chapter', 'teacher', 'learn_time', 'learn_status', 'last_learn_time']
    list_filter = ['learn_status', 'teacher', 'created_at']
    search_fields = ['student__student_name', 'chapter__title']
    list_per_page = 50
    date_hierarchy = 'created_at'
    ordering = ['-last_learn_time']


@admin.register(Homework)
class HomeworkAdmin(admin.ModelAdmin):
    """作业管理"""
    list_display = ['id', 'homework_name', 'teacher', 'class_obj', 'chapter', 'start_time', 'end_time', 'total_score', 'status']
    list_filter = ['status', 'teacher', 'class_obj', 'created_at']
    search_fields = ['homework_name', 'homework_content']
    list_per_page = 20
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(StudentHomework)
class StudentHomeworkAdmin(admin.ModelAdmin):
    """学生作业提交管理"""
    list_display = ['id', 'homework', 'student', 'submit_time', 'correct_time', 'score', 'status']
    list_filter = ['status', 'submit_time', 'correct_time']
    search_fields = ['homework__homework_name', 'student__student_name']
    list_per_page = 50
    ordering = ['-submit_time']


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    """通知管理"""
    list_display = ['id', 'notice_title', 'teacher', 'class_obj', 'publish_time', 'expire_time', 'read_count', 'status']
    list_filter = ['status', 'teacher', 'class_obj', 'publish_time']
    search_fields = ['notice_title', 'notice_content']
    list_per_page = 20
    date_hierarchy = 'publish_time'
    ordering = ['-publish_time']


@admin.register(StudentNoticeRead)
class StudentNoticeReadAdmin(admin.ModelAdmin):
    """学生通知阅读记录管理"""
    list_display = ['id', 'notice', 'student', 'is_read', 'read_time']
    list_filter = ['is_read', 'read_time']
    search_fields = ['notice__notice_title', 'student__student_name']
    list_per_page = 50
    ordering = ['-read_time']


@admin.register(ClassResource)
class ClassResourceAdmin(admin.ModelAdmin):
    """班级资源管理"""
    list_display = ['id', 'resource_name', 'class_obj', 'teacher', 'resource_type', 'upload_time', 'download_count']
    list_filter = ['resource_type', 'class_obj', 'upload_time']
    search_fields = ['resource_name', 'resource_desc']
    list_per_page = 20
    date_hierarchy = 'upload_time'
    ordering = ['-upload_time']


@admin.register(TeachingResource)
class TeachingResourceAdmin(admin.ModelAdmin):
    """教学资源管理"""
    list_display = ['id', 'resource_name', 'chapter', 'teacher', 'resource_type', 'upload_time']
    list_filter = ['resource_type', 'teacher', 'upload_time']
    search_fields = ['resource_name', 'resource_desc']
    list_per_page = 20
    date_hierarchy = 'upload_time'
    ordering = ['-upload_time']


@admin.register(CourseDesign)
class CourseDesignAdmin(admin.ModelAdmin):
    """课程设计管理"""
    list_display = ['id', 'design_title', 'class_obj', 'chapter', 'teacher', 'teaching_hours', 'created_at']
    list_filter = ['teacher', 'class_obj', 'created_at']
    search_fields = ['design_title', 'design_content']
    list_per_page = 20
    date_hierarchy = 'created_at'
    ordering = ['-created_at']


@admin.register(TeacherSetting)
class TeacherSettingAdmin(admin.ModelAdmin):
    """教师个人设置管理"""
    list_display = ['id', 'teacher', 'setting_key', 'setting_value', 'updated_at']
    list_filter = ['setting_key', 'updated_at']
    search_fields = ['teacher__username', 'setting_key']
    list_per_page = 50
    ordering = ['-updated_at']


@admin.register(TeachingToolLog)
class TeachingToolLogAdmin(admin.ModelAdmin):
    """教学工具使用记录管理"""
    list_display = ['id', 'teacher', 'tool_name', 'use_time', 'class_obj', 'use_duration']
    list_filter = ['tool_name', 'teacher', 'use_time']
    search_fields = ['teacher__username', 'tool_name']
    list_per_page = 50
    date_hierarchy = 'use_time'
    ordering = ['-use_time']

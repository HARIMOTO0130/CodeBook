from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    ClassViewSet, StudentViewSet, HomeworkViewSet, SubmissionViewSet,
    NoticeViewSet, ResourceViewSet, CourseDesignViewSet,
    TeachingResourceViewSet,
    BookViewSet, SettingsViewSet, TeacherInfoViewSet, 
    DashboardViewSet, AnalyticsViewSet, ToolLogViewSet, ReportViewSet,
    StudentDataViewSet, TeacherAIAssistantView, StudentSideViewSet
)

# 使用传统方式配置URL
urlpatterns = [
    # 学生端班级信息
    path('student-side/classes/', StudentSideViewSet.as_view({'get': 'list_classes'}), name='student-classes'),
    # 学生端班级搜索
    path('student-side/classes/search/', StudentSideViewSet.as_view({'get': 'search_classes'}), name='student-classes-search'),
    # 学生端加入班级
    path('student-side/classes/join/', StudentSideViewSet.as_view({'post': 'join_class'}), name='student-classes-join'),
    # 学生端通过课程码加入班级
    path('student-side/classes/join-by-code/', StudentSideViewSet.as_view({'post': 'join_by_code'}), name='student-classes-join-by-code'),
    # 学生端退出班级
    path('student-side/classes/leave/', StudentSideViewSet.as_view({'post': 'leave_class'}), name='student-classes-leave'),
    
    # 学生端作业列表
    path('student-side/homeworks/', StudentSideViewSet.as_view({'get': 'list_homeworks'}), name='student-homeworks'),
    
    # 学生端作业详情
    path('student-side/homeworks/<int:pk>/', StudentSideViewSet.as_view({'get': 'get_homework_detail'}), name='student-homework-detail'),
    
    # 学生端作业提交
    path('student-side/homeworks/<int:pk>/submit/', StudentSideViewSet.as_view({'post': 'submit_homework'}), name='student-homework-submit'),
    
    # 学生端作业草稿保存
    path('student-side/homeworks/<int:pk>/draft/', StudentSideViewSet.as_view({'post': 'draft'}), name='student-homework-draft'),
    
    # 学生端作业提交历史
    path('student-side/homeworks/<int:pk>/history/', StudentSideViewSet.as_view({'get': 'history'}), name='student-homework-history'),
    
    # 学生端作业文件上传
    path('student-side/homeworks/<int:pk>/upload-file/', StudentSideViewSet.as_view({'post': 'upload_file'}), name='student-homework-upload-file'),
    
    # 学生端学习资源
    path('student-side/resources/', StudentSideViewSet.as_view({'get': 'list_resources'}), name='student-resources'),
    # 学生端资源下载
    path('student-side/resources/<int:pk>/download/', StudentSideViewSet.as_view({'post': 'download'}), name='student-resource-download'),
    
    # 学生端通知列表
    path('student-side/notices/', StudentSideViewSet.as_view({'get': 'list_notices'}), name='student-notices'),
    
    # 学生端通知标记已读
    path('student-side/notices/<int:pk>/read/', StudentSideViewSet.as_view({'post': 'mark_notice_as_read'}), name='student-notice-read'),
    
    # 教师端AI助手
    path('ai-assistant/', TeacherAIAssistantView.as_view(), name='teacher-ai-assistant'),
]

# 使用router注册其他视图集
router = DefaultRouter()
router.register(r'classes', ClassViewSet, basename='class')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'homeworks', HomeworkViewSet, basename='homework')
router.register(r'submissions', SubmissionViewSet, basename='submission')
router.register(r'notices', NoticeViewSet, basename='notice')
router.register(r'resources', ResourceViewSet, basename='resource')
router.register(r'teaching_resources', TeachingResourceViewSet, basename='teaching_resource')
router.register(r'course_designs', CourseDesignViewSet, basename='course_design')
router.register(r'books', BookViewSet, basename='book')
router.register(r'settings', SettingsViewSet, basename='setting')
router.register(r'info', TeacherInfoViewSet, basename='info')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')
router.register(r'tool_logs', ToolLogViewSet, basename='tool_log')
router.register(r'reports', ReportViewSet, basename='report')
router.register(r'student-data', StudentDataViewSet, basename='student-data')

# 将router生成的URL添加到urlpatterns列表
urlpatterns += router.urls

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ClassViewSet, StudentViewSet, HomeworkViewSet, SubmissionViewSet,
    NoticeViewSet, ResourceViewSet, TeachingResourceViewSet,
    CourseDesignViewSet, BookViewSet, SettingsViewSet,
    TeacherInfoViewSet, DashboardViewSet, AnalyticsViewSet, ToolLogViewSet
)

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

urlpatterns = [
    path('', include(router.urls)),
]

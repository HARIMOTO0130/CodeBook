from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ClassViewSet, AssignmentViewSet, NotificationViewSet, TeachingResourceViewSet, StudentViewSet, AnalyticsViewSet

router = DefaultRouter()
router.register(r'classes', ClassViewSet, basename='class')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'resources', TeachingResourceViewSet, basename='resource')
router.register(r'students', StudentViewSet, basename='student')
router.register(r'analytics', AnalyticsViewSet, basename='analytics', basename='analytics')

urlpatterns = [
    path('', include(router.urls)),
]

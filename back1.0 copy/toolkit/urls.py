from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ToolViewSet, ToolCategoryViewSet, ExecutionHistoryViewSet

router = DefaultRouter()
router.register(r'tools', ToolViewSet, basename='tool')
router.register(r'categories', ToolCategoryViewSet, basename='tool-category')
router.register(r'history', ExecutionHistoryViewSet, basename='execution-history')

urlpatterns = [
    path('', include(router.urls)),
]
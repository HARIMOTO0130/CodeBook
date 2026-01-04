"""用户URL配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, TestAPIView
from rest_framework.permissions import AllowAny

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    # 添加测试端点，允许匿名访问
    path('test/', TestAPIView.as_view(), name='test-api'),
    # 直接使用UserViewSet，在views.py中已设置相应权限
    path('register/', UserViewSet.as_view({'post': 'register'}), name='register'),
    path('login/', UserViewSet.as_view({'post': 'login'}), name='login'),
    path('logout/', UserViewSet.as_view({'post': 'logout'}), name='logout'),
    path('me/', UserViewSet.as_view({'get': 'me'}), name='me'),
    path('preferences/', UserViewSet.as_view({'get': 'preferences', 'put': 'preferences'}), name='preferences'),
]
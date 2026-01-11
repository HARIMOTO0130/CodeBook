"""URL configuration for CodeBook+ project."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django管理后台
    path('admin/', admin.site.urls),
    
    # 学生端API（包含工具箱）
    path('api/student/books/', include('apps.books.urls')),      # 学生端书籍浏览
    path('api/student/learning/', include('apps.learning.urls')),  # 学习记录、练习等
    path('api/student/users/', include('apps.users.urls')),      # 用户相关（登录、注册等）
    path('api/student/toolkit/', include('toolkit.urls')),       # 学生端工具箱
    
    # 教师端API
    path('api/teacher/', include('apps.teacher.urls')),  # 班级、作业、学生管理等
    
    # 教材提供者端API（仅教材相关的核心功能）
    path('api/provider/books/', include('apps.books.urls')),  # 书籍 / 章节 / 版本 / 状态等管理
    
    # 兼容旧版API路径（保持向后兼容）
    path('api/books/', include('apps.books.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/learning/', include('apps.learning.urls')),
    path('api/toolkit/', include('toolkit.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
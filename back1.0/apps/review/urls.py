# -*- coding: utf-8 -*-
"""审核模块URL配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReviewTaskViewSet, ManualReviewViewSet, AIReviewViewSet,
    WorkflowLogViewSet, ReviewRuleConfigViewSet,
    BookEditHistoryViewSet, TeacherProfileViewSet, BookViewSet,
    review_login, review_register, review_logout, get_review_profile,
    get_book_metadata
)

router = DefaultRouter()
router.register(r'tasks', ReviewTaskViewSet, basename='review-task')
router.register(r'manual-reviews', ManualReviewViewSet, basename='manual-review')
router.register(r'ai-reviews', AIReviewViewSet, basename='ai-review')
router.register(r'logs', WorkflowLogViewSet, basename='workflow-log')
router.register(r'rules', ReviewRuleConfigViewSet, basename='review-rule')
router.register(r'edit-history', BookEditHistoryViewSet, basename='edit-history')
router.register(r'teachers', TeacherProfileViewSet, basename='teacher-profile')
router.register(r'books', BookViewSet, basename='book')

urlpatterns = [
    path('', include(router.urls)),
    # 认证相关接口
    path('auth/login/', review_login, name='review-login'),
    path('auth/register/', review_register, name='review-register'),
    path('auth/logout/', review_logout, name='review-logout'),
    path('auth/profile/', get_review_profile, name='review-profile'),
    # 内容访问控制接口
    path('books/<int:book_id>/metadata/', get_book_metadata, name='book-metadata'),
]

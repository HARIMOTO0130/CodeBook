"""书籍URL配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookViewSet,
    ChapterViewSet,
    BookCategoryViewSet,
    BookTagViewSet,
    BookVersionViewSet,
    ChapterVersionViewSet,
    ChapterMediaViewSet,
    BookReviewViewSet,
)

router = DefaultRouter()

# 学生端/公共接口
router.register(r'', BookViewSet, basename='book')
router.register(r'chapters', ChapterViewSet, basename='chapter')

# 教材提供者端接口（通过 /api/provider/books/* 访问）
router.register(r'categories', BookCategoryViewSet, basename='book-category')
router.register(r'tags', BookTagViewSet, basename='book-tag')
router.register(r'versions', BookVersionViewSet, basename='book-version')
router.register(r'chapter-versions', ChapterVersionViewSet, basename='chapter-version')
router.register(r'media', ChapterMediaViewSet, basename='chapter-media')
router.register(r'reviews', BookReviewViewSet, basename='book-review')

urlpatterns = [
    path('', include(router.urls)),
    path('chapters/book/<int:book_id>/', ChapterViewSet.as_view({'get': 'by_book'})),
]
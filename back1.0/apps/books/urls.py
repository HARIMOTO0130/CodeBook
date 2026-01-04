"""书籍URL配置"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, ChapterViewSet

router = DefaultRouter()
router.register(r'', BookViewSet, basename='book')
router.register(r'chapters', ChapterViewSet, basename='chapter')

urlpatterns = [
    path('', include(router.urls)),
    path('chapters/book/<int:book_id>/', ChapterViewSet.as_view({'get': 'by_book'})),
]
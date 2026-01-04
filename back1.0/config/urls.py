"""URL configuration for CodeBook+ project."""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/books/', include('apps.books.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/learning/', include('apps.learning.urls')),
    path('api/toolkit/', include('toolkit.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
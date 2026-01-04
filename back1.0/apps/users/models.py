"""用户模型定义"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """自定义用户模型"""
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    email = models.EmailField(unique=True, verbose_name='邮箱')
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
    
    def __str__(self):
        return self.username


class UserPreferences(models.Model):
    """用户偏好设置"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences', verbose_name='用户')
    default_language = models.CharField(max_length=50, default='python', verbose_name='默认编程语言')
    code_theme = models.CharField(max_length=50, default='vs-dark', verbose_name='代码编辑器主题')
    auto_play_video = models.BooleanField(default=False, verbose_name='自动播放视频')
    keyboard_shortcuts = models.BooleanField(default=True, verbose_name='启用键盘快捷键')
    
    class Meta:
        verbose_name = '用户偏好设置'
        verbose_name_plural = '用户偏好设置'
    
    def __str__(self):
        return f"{self.user.username}的偏好设置"
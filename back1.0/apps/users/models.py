"""用户模型定义"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """自定义用户管理器，支持role参数"""
    def create_user(self, username, email=None, password=None, role='student', **extra_fields):
        """创建普通用户"""
        if not username:
            raise ValueError('用户名是必需的')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """创建超级用户"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('超级用户必须设置 is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('超级用户必须设置 is_superuser=True')
        
        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """自定义用户模型"""
    ROLE_CHOICES = [
        ('student', '学生'),
        ('teacher', '教师'),
        ('provider', '教材提供者'),
        ('admin', '管理员'),
    ]
    
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name='头像')
    email = models.EmailField(unique=True, verbose_name='邮箱')
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='student',
        verbose_name='用户角色'
    )
    
    objects = UserManager()
    
    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'
    
    def __str__(self):
        return self.username
    
    def is_student(self):
        """判断是否为学生"""
        return self.role == 'student'
    
    def is_teacher(self):
        """判断是否为教师"""
        return self.role == 'teacher'
    
    def is_provider(self):
        """判断是否为教材提供者"""
        return self.role == 'provider'
    
    def is_admin(self):
        """判断是否为管理员"""
        return self.role == 'admin' or self.is_staff


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
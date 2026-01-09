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
    
    # 新增基本信息字段
    nickname = models.CharField(max_length=50, blank=True, null=True, verbose_name='昵称')
    bio = models.TextField(blank=True, null=True, verbose_name='个性签名')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')
    
    # 新增隐私设置字段
    profile_visibility = models.CharField(
        max_length=20, 
        choices=[('public', '公开'), ('friends', '好友可见'), ('private', '私密')],
        default='public',
        verbose_name='资料可见性'
    )
    learning_records_visibility = models.CharField(
        max_length=20, 
        choices=[('public', '公开'), ('friends', '好友可见'), ('private', '私密')],
        default='private',
        verbose_name='学习记录可见性'
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
    show_line_numbers = models.BooleanField(default=True, verbose_name='显示代码行号')
    use_vim_mode = models.BooleanField(default=False, verbose_name='使用Vim模式')
    
    # 新增学习信息字段
    learning_goals = models.JSONField(default=list, verbose_name='学习目标')
    major_category = models.CharField(
        max_length=50, 
        choices=[('business', '经管类'), ('humanities', '文史类'), ('arts', '艺术类'), ('science', '理工科')],
        blank=True, null=True,
        verbose_name='专业类别'
    )
    major = models.CharField(max_length=100, blank=True, null=True, verbose_name='专业方向')
    learning_stage = models.CharField(
        max_length=20, 
        choices=[('beginner', '初学者'), ('intermediate', '进阶者'), ('advanced', '高级学习者')],
        default='beginner',
        verbose_name='学习阶段'
    )
    interests = models.JSONField(default=list, verbose_name='兴趣领域')
    
    # 新增学习提醒设置
    enable_learning_reminders = models.BooleanField(default=True, verbose_name='启用学习提醒')
    reminder_time = models.TimeField(default='09:00', verbose_name='提醒时间')
    daily_reminder = models.BooleanField(default=True, verbose_name='每日学习提醒')
    deadline_reminder = models.BooleanField(default=True, verbose_name='截止日期提醒')
    
    class Meta:
        verbose_name = '用户偏好设置'
        verbose_name_plural = '用户偏好设置'
    
    def __str__(self):
        return f"{self.user.username}的偏好设置"
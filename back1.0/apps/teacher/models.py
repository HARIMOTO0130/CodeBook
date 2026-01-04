from django.db import models
from django.contrib.auth import get_user_model
from apps.books.models import Book, Chapter

User = get_user_model()


class Class(models.Model):
    """班级模型"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='班级名称')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='classes', verbose_name='班主任')
    students = models.ManyToManyField(User, related_name='student_classes', verbose_name='学生', blank=True)
    major = models.CharField(max_length=100, blank=True, null=True, verbose_name='专业')
    grade = models.CharField(max_length=50, blank=True, null=True, verbose_name='年级')
    description = models.TextField(blank=True, null=True, verbose_name='班级描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '班级'
        verbose_name_plural = '班级'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Assignment(models.Model):
    """作业模型"""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name='作业标题')
    description = models.TextField(blank=True, null=True, verbose_name='作业说明')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignments', verbose_name='教师')
    books = models.ManyToManyField(Book, related_name='assignments', verbose_name='关联教材', blank=True)
    chapters = models.ManyToManyField(Chapter, related_name='assignments', verbose_name='关联章节', blank=True)
    classes = models.ManyToManyField(Class, related_name='assignments', verbose_name='分配班级')
    due_date = models.DateTimeField(verbose_name='截止时间')
    total_score = models.IntegerField(default=100, verbose_name='总分')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '作业'
        verbose_name_plural = '作业'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class AssignmentSubmission(models.Model):
    """作业提交模型"""
    id = models.AutoField(primary_key=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions', verbose_name='作业')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_submissions', verbose_name='学生')
    score = models.IntegerField(blank=True, null=True, verbose_name='得分')
    feedback = models.TextField(blank=True, null=True, verbose_name='教师反馈')
    submitted_at = models.DateTimeField(auto_now=True, verbose_name='提交时间')
    is_late = models.BooleanField(default=False, verbose_name='是否迟交')
    graded_at = models.DateTimeField(blank=True, null=True, verbose_name='批改时间')
    graded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_submissions', verbose_name='批改教师')

    class Meta:
        verbose_name = '作业提交'
        verbose_name_plural = '作业提交'
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.assignment.title} - {self.student.username}"


class Notification(models.Model):
    """通知模型"""
    id = models.AutoField(primary_key=True)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications', verbose_name='发送者')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_notifications', verbose_name='接收者')
    title = models.CharField(max_length=200, verbose_name='通知标题')
    content = models.TextField(verbose_name='通知内容')
    type = models.CharField(max_length=20, choices=[
        ('assignment', '作业通知'),
        ('reminder', '提醒通知'),
        ('feedback', '反馈通知'),
        ('system', '系统通知')
    ], default='system', verbose_name='通知类型')
    is_read = models.BooleanField(default=False, verbose_name='是否已读')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.receiver.username}"


class TeachingResource(models.Model):
    """教学资源模型"""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name='资源标题')
    description = models.TextField(blank=True, null=True, verbose_name='资源描述')
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_resources', verbose_name='上传教师')
    file = models.FileField(upload_to='teaching_resources/', verbose_name='资源文件')
    resource_type = models.CharField(max_length=20, choices=[
        ('ppt', 'PPT'),
        ('video', '视频'),
        ('document', '文档'),
        ('other', '其他')
    ], default='other', verbose_name='资源类型')
    category = models.CharField(max_length=100, blank=True, null=True, verbose_name='分类')
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    file_size = models.IntegerField(blank=True, null=True, verbose_name='文件大小(字节)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '教学资源'
        verbose_name_plural = '教学资源'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class TeacherProfile(models.Model):
    """教师档案模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile', verbose_name='用户')
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name='所属院系')
    title = models.CharField(max_length=50, blank=True, null=True, verbose_name='职称')
    office = models.CharField(max_length=100, blank=True, null=True, verbose_name='办公室')
    office_hours = models.CharField(max_length=200, blank=True, null=True, verbose_name='办公时间')
    bio = models.TextField(blank=True, null=True, verbose_name='个人简介')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '教师档案'
        verbose_name_plural = '教师档案'

    def __str__(self):
        return f"{self.user.username}的档案"


class StudentProfile(models.Model):
    """学生档案模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', verbose_name='用户')
    student_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='学号')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='手机号')
    major = models.CharField(max_length=100, blank=True, null=True, verbose_name='专业')
    grade = models.CharField(max_length=50, blank=True, null=True, verbose_name='年级')
    enrollment_date = models.DateField(blank=True, null=True, verbose_name='入学日期')
    notes = models.TextField(blank=True, null=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '学生档案'
        verbose_name_plural = '学生档案'

    def __str__(self):
        return f"{self.user.username}的档案"

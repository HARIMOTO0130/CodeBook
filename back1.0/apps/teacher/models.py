from django.db import models
from django.contrib.auth import get_user_model
from apps.books.models import Book, Chapter

User = get_user_model()


class Teacher(models.Model):
    """教师模型 - 对应数据库teacher表"""
    id = models.AutoField(primary_key=True, db_column='teacher_id')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile', verbose_name='关联用户', db_column='user_id')
    teacher_number = models.CharField(max_length=50, unique=True, verbose_name='教师编号', null=True, blank=True)
    teacher_name = models.CharField(max_length=100, verbose_name='教师姓名')
    department = models.CharField(max_length=100, verbose_name='所属部门', null=True, blank=True)
    position = models.CharField(max_length=50, verbose_name='职位', null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name='联系电话', null=True, blank=True)
    email = models.CharField(max_length=100, verbose_name='邮箱', null=True, blank=True)
    avatar = models.CharField(max_length=255, verbose_name='头像', null=True, blank=True)
    introduction = models.TextField(verbose_name='教师简介', null=True, blank=True)
    status = models.IntegerField(default=1, verbose_name='状态', help_text='1-正常，0-禁用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_column='create_time')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间', db_column='update_time')

    class Meta:
        db_table = 'teacher'
        verbose_name = '教师'
        verbose_name_plural = '教师'
        ordering = ['-created_at']

    def __str__(self):
        return self.teacher_name


class Class(models.Model):
    """班级模型 - 对应数据库class表"""
    id = models.AutoField(primary_key=True, db_column='class_id')
    name = models.CharField(max_length=100, verbose_name='班级名称', db_column='class_name')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_classes', verbose_name='教师', db_column='teacher_id')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='classes', verbose_name='关联教材', db_column='book_id', null=True, blank=True)
    major = models.CharField(max_length=100, verbose_name='专业名称', default='计算机科学')
    grade = models.CharField(max_length=50, verbose_name='年级', default='2024', null=True, blank=True)
    academic_year = models.CharField(max_length=20, verbose_name='学年', default='2024-2025')
    semester = models.CharField(max_length=10, verbose_name='学期', default='1')
    description = models.TextField(blank=True, null=True, verbose_name='班级描述', db_column='class_desc')
    status = models.IntegerField(default=1, verbose_name='状态', help_text='1-正常，0-解散')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_column='create_time')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间', db_column='update_time')

    class Meta:
        db_table = 'class'
        verbose_name = '班级'
        verbose_name_plural = '班级'
        ordering = ['-created_at']
        unique_together = [['teacher', 'book']]  # 一个教师下一个班级对应一本教材

    def __str__(self):
        return self.name

    @property
    def student_count(self):
        """获取班级学生数量"""
        return self.students.count()


class Student(models.Model):
    """学生模型 - 对应数据库student表"""
    id = models.AutoField(primary_key=True, db_column='student_id')
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', verbose_name='关联用户', db_column='user_id', null=True, blank=True)
    student_no = models.CharField(max_length=50, unique=True, verbose_name='学生学号', db_column='student_number')
    student_name = models.CharField(max_length=100, verbose_name='学生姓名')
    gender = models.IntegerField(blank=True, null=True, verbose_name='性别', help_text='1-男，2-女，0-未知')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='联系电话')
    # 暂时使用CharField来避免数据库错误
    class_name = models.CharField(max_length=100, verbose_name='所属班级', null=True, blank=True)
    status = models.IntegerField(default=1, verbose_name='状态', help_text='1-正常，0-离校/退班')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_column='create_time')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间', db_column='update_time')

    class Meta:
        db_table = 'student'
        verbose_name = '学生'
        verbose_name_plural = '学生'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['student_name']),
        ]

    def __str__(self):
        return f"{self.student_name} ({self.student_no})"


class StudentLearningProgress(models.Model):
    """学生学习进度模型 - 对应数据库student_learning_progress表"""
    id = models.AutoField(primary_key=True, db_column='progress_id')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='learning_progress', verbose_name='学生', db_column='student_id')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='student_progress', verbose_name='章节', db_column='chapter_id')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='student_progress', verbose_name='教师', db_column='teacher_id')
    learn_time = models.IntegerField(default=0, verbose_name='学习时长（分钟）')
    learn_status = models.IntegerField(default=1, verbose_name='学习状态', help_text='1-未学习，2-学习中，3-已完成')
    last_learn_time = models.DateTimeField(blank=True, null=True, verbose_name='最后学习时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_column='create_time')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间', db_column='update_time')

    class Meta:
        db_table = 'student_learning_progress'
        verbose_name = '学生学习进度'
        verbose_name_plural = '学生学习进度'
        unique_together = [['student', 'chapter']]
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['learn_status']),
        ]

    def __str__(self):
        return f"{self.student.student_name} - {self.chapter.title}"


class Homework(models.Model):
    """作业模型 - 对应数据库homework表"""
    id = models.AutoField(primary_key=True, db_column='homework_id')
    homework_name = models.CharField(max_length=200, verbose_name='作业名称')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='homeworks', verbose_name='创建教师', db_column='teacher_id')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='homeworks', verbose_name='所属班级', db_column='class_id')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='homeworks', verbose_name='关联章节', db_column='chapter_id')
    homework_content = models.TextField(verbose_name='作业内容')
    start_time = models.DateTimeField(verbose_name='作业发布时间')
    end_time = models.DateTimeField(verbose_name='作业截止时间')
    total_score = models.IntegerField(default=100, verbose_name='作业总分')
    status = models.IntegerField(default=1, verbose_name='状态', help_text='1-未发布，2-已发布，3-已截止')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_column='create_time')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间', db_column='update_time')

    class Meta:
        db_table = 'homework'
        verbose_name = '作业'
        verbose_name_plural = '作业'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['class_obj']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.homework_name


class StudentHomework(models.Model):
    """学生作业提交模型 - 对应数据库student_homework表"""
    id = models.AutoField(primary_key=True, db_column='submit_id')
    homework = models.ForeignKey(Homework, on_delete=models.CASCADE, related_name='submissions', verbose_name='作业', db_column='homework_id')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='homework_submissions', verbose_name='学生', db_column='student_id')
    submit_content = models.TextField(blank=True, null=True, verbose_name='提交内容')
    submit_file_url = models.CharField(max_length=255, blank=True, null=True, verbose_name='提交文件地址')
    submit_time = models.DateTimeField(blank=True, null=True, verbose_name='提交时间')
    correct_time = models.DateTimeField(blank=True, null=True, verbose_name='批改时间')
    score = models.IntegerField(blank=True, null=True, verbose_name='得分')
    correct_comment = models.TextField(blank=True, null=True, verbose_name='批改评语')
    correct_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='corrected_homeworks', verbose_name='批改教师', db_column='correct_teacher_id')
    status = models.IntegerField(default=1, verbose_name='状态', help_text='1-未提交，2-已提交，3-已批改，4-已退回')

    class Meta:
        db_table = 'student_homework'
        verbose_name = '学生作业提交'
        verbose_name_plural = '学生作业提交'
        unique_together = [['homework', 'student']]
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.homework.homework_name} - {self.student.student_name}"


class Notice(models.Model):
    """通知模型 - 对应数据库notice表"""
    id = models.AutoField(primary_key=True, db_column='notice_id')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='sent_notices', verbose_name='发布教师', db_column='teacher_id')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True, related_name='notices', verbose_name='所属班级', db_column='class_id', help_text='NULL表示全体学生')
    notice_title = models.CharField(max_length=200, verbose_name='通知标题')
    notice_content = models.TextField(verbose_name='通知内容')
    publish_time = models.DateTimeField(auto_now_add=True, verbose_name='发布时间')
    expire_time = models.DateTimeField(blank=True, null=True, verbose_name='过期时间')
    read_count = models.IntegerField(default=0, verbose_name='已读次数')
    status = models.IntegerField(default=1, verbose_name='状态', help_text='1-有效，0-已删除')

    class Meta:
        db_table = 'notice'
        verbose_name = '通知'
        verbose_name_plural = '通知'
        ordering = ['-publish_time']
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['class_obj']),
        ]

    def __str__(self):
        return self.notice_title


class StudentNoticeRead(models.Model):
    """学生通知阅读记录模型 - 对应数据库student_notice_read表"""
    id = models.AutoField(primary_key=True, db_column='read_id')
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE, related_name='read_records', verbose_name='通知', db_column='notice_id')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='notice_reads', verbose_name='学生', db_column='student_id')
    read_time = models.DateTimeField(blank=True, null=True, verbose_name='阅读时间')
    is_read = models.IntegerField(default=0, verbose_name='是否已读', help_text='0-未读，1-已读')

    class Meta:
        db_table = 'student_notice_read'
        verbose_name = '学生通知阅读记录'
        verbose_name_plural = '学生通知阅读记录'
        unique_together = [['notice', 'student']]
        indexes = [
            models.Index(fields=['student']),
        ]

    def __str__(self):
        return f"{self.notice.notice_title} - {self.student.student_name}"


class ClassResource(models.Model):
    """班级资源模型 - 对应数据库class_resource表"""
    id = models.AutoField(primary_key=True, db_column='resource_id')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='resources', verbose_name='所属班级', db_column='class_id')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='class_resources', verbose_name='所属教师', db_column='teacher_id')
    resource_name = models.CharField(max_length=200, verbose_name='资源名称')
    resource_type = models.CharField(max_length=50, verbose_name='资源类型', help_text='文档、视频、音频、图片等')
    resource_url = models.CharField(max_length=255, verbose_name='资源存储地址')
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    download_count = models.IntegerField(default=0, verbose_name='下载次数')
    resource_desc = models.CharField(max_length=500, blank=True, null=True, verbose_name='资源描述')

    class Meta:
        db_table = 'class_resource'
        verbose_name = '班级资源'
        verbose_name_plural = '班级资源'
        ordering = ['-upload_time']
        indexes = [
            models.Index(fields=['class_obj']),
            models.Index(fields=['teacher']),
        ]

    def __str__(self):
        return self.resource_name


class TeachingResource(models.Model):
    """教学资源模型 - 对应数据库teaching_resource表"""
    id = models.AutoField(primary_key=True, db_column='resource_id')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='teaching_resources', verbose_name='所属章节', db_column='chapter_id', null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teaching_resources', verbose_name='上传教师', db_column='teacher_id', null=True, blank=True)
    resource_name = models.CharField(max_length=200, verbose_name='资源名称', blank=True, null=True)
    resource_type = models.CharField(max_length=50, verbose_name='资源类型', help_text='课件、教案、习题等', blank=True, null=True)
    resource_url = models.CharField(max_length=255, verbose_name='资源存储地址', blank=True, null=True)
    upload_time = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    resource_desc = models.CharField(max_length=500, blank=True, null=True, verbose_name='资源描述')

    class Meta:
        db_table = 'teaching_resource'
        verbose_name = '教学资源'
        verbose_name_plural = '教学资源'
        ordering = ['-upload_time']
        indexes = [
            models.Index(fields=['chapter']),
            models.Index(fields=['teacher']),
        ]

    def __str__(self):
        return self.resource_name


class CourseDesign(models.Model):
    """课程设计模型 - 对应数据库course_design表"""
    id = models.AutoField(primary_key=True, db_column='design_id')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='course_designs', verbose_name='所属班级', db_column='class_id')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='course_designs', verbose_name='关联章节', db_column='chapter_id')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='course_designs', verbose_name='设计教师', db_column='teacher_id')
    design_title = models.CharField(max_length=200, verbose_name='设计标题')
    design_content = models.TextField(blank=True, null=True, verbose_name='设计内容')
    teaching_hours = models.IntegerField(blank=True, null=True, verbose_name='预计课时')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_column='create_time')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间', db_column='update_time')

    class Meta:
        db_table = 'course_design'
        verbose_name = '课程设计'
        verbose_name_plural = '课程设计'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['class_obj']),
            models.Index(fields=['chapter']),
        ]

    def __str__(self):
        return self.design_title


class TeacherSetting(models.Model):
    """教师个人设置模型 - 对应数据库teacher_setting表"""
    id = models.AutoField(primary_key=True, db_column='setting_id')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='settings', verbose_name='教师', db_column='teacher_id')
    setting_key = models.CharField(max_length=50, verbose_name='设置项key', help_text='theme、notify_type等')
    setting_value = models.CharField(max_length=255, verbose_name='设置项值')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', db_column='create_time')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间', db_column='update_time')

    class Meta:
        db_table = 'teacher_setting'
        verbose_name = '教师个人设置'
        verbose_name_plural = '教师个人设置'
        unique_together = [['teacher', 'setting_key']]

    def __str__(self):
        return f"{self.teacher.teacher_name} - {self.setting_key}"


class TeachingToolLog(models.Model):
    """教学工具使用记录模型 - 对应数据库teaching_tool_log表"""
    id = models.AutoField(primary_key=True, db_column='log_id')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='tool_logs', verbose_name='教师', db_column='teacher_id')
    tool_name = models.CharField(max_length=100, verbose_name='工具名称', help_text='计时器、随机点名、答题卡等')
    use_time = models.DateTimeField(auto_now_add=True, verbose_name='使用时间')
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, null=True, blank=True, related_name='tool_logs', verbose_name='使用的班级', db_column='class_id')
    use_duration = models.IntegerField(default=0, verbose_name='使用时长（秒）')

    class Meta:
        db_table = 'teaching_tool_log'
        verbose_name = '教学工具使用记录'
        verbose_name_plural = '教学工具使用记录'
        ordering = ['-use_time']
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['tool_name']),
            models.Index(fields=['class_obj']),
        ]

    def __str__(self):
        return f"{self.teacher.teacher_name} - {self.tool_name}"

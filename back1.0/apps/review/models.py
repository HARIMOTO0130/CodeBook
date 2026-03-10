# -*- coding: utf-8 -*-
"""审核模块模型定义"""
from django.db import models
from django.conf import settings
from django.utils import timezone


class ReviewTask(models.Model):
    """审核任务表"""
    TASK_TYPE_CHOICES = [
        ('new_submission', '新提交'),
        ('edit_review', '修改审核'),
    ]
    
    STATUS_CHOICES = [
        ('pending', '待审核'),
        ('in_review', '审核中'),
        ('approved', '已通过'),
        ('rejected', '已驳回'),
    ]
    
    PRIORITY_CHOICES = [
        (0, '普通'),
        (1, '优先'),
        (2, '紧急'),
        (3, '特急'),
    ]
    
    # 教材基本信息
    book_id = models.IntegerField(verbose_name='教材ID')
    book_title = models.CharField(max_length=200, verbose_name='教材标题')
    book_subtitle = models.CharField(max_length=200, blank=True, null=True, verbose_name='副标题')
    book_author = models.CharField(max_length=100, verbose_name='教材作者')
    book_isbn = models.CharField(max_length=20, blank=True, null=True, verbose_name='ISBN')
    book_language = models.CharField(max_length=50, default='zh-CN', verbose_name='语言')
    book_word_count = models.IntegerField(default=0, verbose_name='字数')
    
    # 任务信息
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default='new_submission', verbose_name='任务类型')
    priority = models.IntegerField(default=0, choices=PRIORITY_CHOICES, verbose_name='优先级')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='状态')
    
    # 审核员信息
    assigned_reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='指派审核员'
    )
    
    # 提交人信息（教师/上传者）
    submitted_by_id = models.IntegerField(null=True, blank=True, verbose_name='提交人ID')
    submitted_by_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='提交人姓名')
    submitted_by_username = models.CharField(max_length=150, blank=True, null=True, verbose_name='提交人用户名')
    submitted_by_employee_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='提交人工号')
    submitted_by_department = models.CharField(max_length=100, blank=True, null=True, verbose_name='提交人部门')
    submitted_by_email = models.EmailField(blank=True, null=True, verbose_name='提交人邮箱')
    submitted_by_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='提交人电话')
    
    # 修改者信息（如果是修改审核）
    modified_by_id = models.IntegerField(null=True, blank=True, verbose_name='修改人ID')
    modified_by_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='修改人姓名')
    modified_by_username = models.CharField(max_length=150, blank=True, null=True, verbose_name='修改人用户名')
    modified_by_employee_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='修改人工号')
    modified_by_department = models.CharField(max_length=100, blank=True, null=True, verbose_name='修改人部门')
    
    # 原始上传者信息
    original_uploader_id = models.IntegerField(null=True, blank=True, verbose_name='原始上传者ID')
    original_uploader_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='原始上传者姓名')
    original_uploader_username = models.CharField(max_length=150, blank=True, null=True, verbose_name='原始上传者用户名')
    original_uploader_employee_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='原始上传者工号')
    original_uploader_department = models.CharField(max_length=100, blank=True, null=True, verbose_name='原始上传者部门')
    
    # 时间记录
    submitted_at = models.DateTimeField(null=True, blank=True, verbose_name='提交时间')
    original_uploaded_at = models.DateTimeField(null=True, blank=True, verbose_name='原始上传时间')
    last_modified_at = models.DateTimeField(null=True, blank=True, verbose_name='最后修改时间')
    deadline = models.DateTimeField(null=True, blank=True, verbose_name='审核截止时间')
    
    # 版本信息
    version_number = models.CharField(max_length=20, default='1.0.0', verbose_name='版本号')
    previous_version = models.CharField(max_length=20, blank=True, null=True, verbose_name='上一版本号')
    chapter_count = models.IntegerField(default=0, verbose_name='章节数')
    description = models.TextField(blank=True, null=True, verbose_name='教材描述')
    change_summary = models.TextField(blank=True, null=True, verbose_name='变更说明')
    
    # 分类和标签
    category_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='分类名称')
    tags = models.JSONField(default=list, verbose_name='标签列表')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '审核任务'
        verbose_name_plural = '审核任务'
        db_table = 'review_task'
        ordering = ['-priority', 'created_at']
    
    def __str__(self):
        return f"{self.book_title} - {self.get_status_display()}"


class ManualReviewRecord(models.Model):
    """人工审核记录表"""
    DECISION_CHOICES = [
        ('approved', '通过'),
        ('rejected', '驳回'),
        ('needs_revision', '需修改'),
    ]
    
    task = models.ForeignKey(ReviewTask, on_delete=models.CASCADE, related_name='manual_records', verbose_name='审核任务')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='review_records', verbose_name='审核员')
    
    decision = models.CharField(max_length=20, choices=DECISION_CHOICES, verbose_name='审核决定')
    overall_comment = models.TextField(blank=True, verbose_name='总体审核意见')
    
    content_quality_score = models.IntegerField(null=True, blank=True, verbose_name='内容质量评分')
    accuracy_score = models.IntegerField(null=True, blank=True, verbose_name='准确性评分')
    completeness_score = models.IntegerField(null=True, blank=True, verbose_name='完整性评分')
    formatting_score = models.IntegerField(null=True, blank=True, verbose_name='格式规范评分')
    language_score = models.IntegerField(null=True, blank=True, verbose_name='语言表达评分')
    
    content_issues = models.JSONField(default=list, verbose_name='内容问题列表')
    format_issues = models.JSONField(default=list, verbose_name='格式问题列表')
    suggestions = models.TextField(blank=True, verbose_name='修改建议')
    
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始审核时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成审核时间')
    review_duration = models.IntegerField(null=True, blank=True, verbose_name='审核耗时(分钟)')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '人工审核记录'
        verbose_name_plural = '人工审核记录'
        db_table = 'review_manual_record'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.task.book_title} - {self.reviewer.username} - {self.get_decision_display()}"
    
    @property
    def average_score(self):
        scores = [self.content_quality_score, self.accuracy_score, self.completeness_score, 
                  self.formatting_score, self.language_score]
        valid_scores = [s for s in scores if s is not None]
        return sum(valid_scores) / len(valid_scores) if valid_scores else None


class AIReviewRecord(models.Model):
    """AI审核记录表"""
    RISK_LEVEL_CHOICES = [
        ('low', '低风险'),
        ('medium', '中等风险'),
        ('high', '高风险'),
        ('critical', '严重风险'),
    ]
    
    task = models.OneToOneField(ReviewTask, on_delete=models.CASCADE, related_name='ai_record', verbose_name='审核任务')
    
    overall_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='总体评分')
    risk_level = models.CharField(max_length=20, choices=RISK_LEVEL_CHOICES, null=True, blank=True, verbose_name='风险等级')
    
    content_compliance_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='内容合规性评分')
    accuracy_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='准确性评分')
    completeness_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='完整性评分')
    readability_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='可读性评分')
    
    detected_issues = models.JSONField(default=list, verbose_name='检测到的问题')
    risk_items = models.JSONField(default=list, verbose_name='风险项')
    suggestions = models.JSONField(default=list, verbose_name='AI建议')
    
    raw_response = models.TextField(blank=True, verbose_name='AI原始响应')
    model_version = models.CharField(max_length=50, blank=True, verbose_name='模型版本')
    processing_time = models.IntegerField(null=True, blank=True, verbose_name='处理耗时(毫秒)')
    
    status = models.CharField(max_length=20, default='pending', verbose_name='审核状态')
    error_message = models.TextField(blank=True, null=True, verbose_name='错误信息')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'AI审核记录'
        verbose_name_plural = 'AI审核记录'
        db_table = 'review_ai_record'
    
    def __str__(self):
        return f"{self.task.book_title} - AI审核"


class WorkflowLog(models.Model):
    """审核流程日志表"""
    ACTION_CHOICES = [
        ('created', '任务创建'),
        ('assigned', '任务分配'),
        ('claimed', '任务认领'),
        ('released', '任务释放'),
        ('ai_reviewed', 'AI审核完成'),
        ('manual_reviewed', '人工审核完成'),
        ('approved', '审核通过'),
        ('rejected', '审核驳回'),
        ('returned', '退回修改'),
    ]
    
    ACTOR_TYPE_CHOICES = [
        ('system', '系统'),
        ('reviewer', '审核员'),
        ('provider', '教材提供者'),
    ]
    
    task = models.ForeignKey(ReviewTask, on_delete=models.CASCADE, related_name='workflow_logs', verbose_name='审核任务')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES, verbose_name='操作类型')
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='操作人')
    actor_type = models.CharField(max_length=20, choices=ACTOR_TYPE_CHOICES, default='system', verbose_name='操作人类型')
    from_status = models.CharField(max_length=20, blank=True, null=True, verbose_name='原状态')
    to_status = models.CharField(max_length=20, blank=True, null=True, verbose_name='新状态')
    comment = models.TextField(blank=True, verbose_name='备注')
    extra_data = models.JSONField(default=dict, blank=True, verbose_name='额外数据')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '审核流程日志'
        verbose_name_plural = '审核流程日志'
        db_table = 'review_workflow_log'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.task.book_title} - {self.get_action_display()}"


class ReviewRuleConfig(models.Model):
    """审核规则配置表"""
    RULE_TYPE_CHOICES = [
        ('content', '内容规则'),
        ('format', '格式规则'),
        ('ai', 'AI规则'),
    ]
    
    rule_name = models.CharField(max_length=100, verbose_name='规则名称')
    rule_type = models.CharField(max_length=20, choices=RULE_TYPE_CHOICES, verbose_name='规则类型')
    description = models.TextField(blank=True, verbose_name='规则描述')
    rule_config = models.JSONField(default=dict, verbose_name='规则配置')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    priority = models.IntegerField(default=0, verbose_name='优先级')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '审核规则配置'
        verbose_name_plural = '审核规则配置'
        db_table = 'review_rule_config'
        ordering = ['-priority', 'rule_name']
    
    def __str__(self):
        return self.rule_name


class BookEditHistory(models.Model):
    """教材修改历史记录"""
    ACTION_CHOICES = [
        ('created', '创建'),
        ('updated', '更新'),
        ('submitted', '提交审核'),
        ('approved', '审核通过'),
        ('rejected', '审核驳回'),
        ('published', '发布'),
        ('archived', '归档'),
    ]
    
    # 关联信息
    book_id = models.IntegerField(verbose_name='教材ID')
    book_title = models.CharField(max_length=200, verbose_name='教材标题')
    task = models.ForeignKey(
        ReviewTask,
        on_delete=models.CASCADE,
        related_name='edit_history',
        null=True,
        blank=True,
        verbose_name='审核任务'
    )
    
    # 操作信息
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name='操作类型')
    action_display = models.CharField(max_length=100, blank=True, verbose_name='操作描述')
    
    # 操作人信息
    actor_id = models.IntegerField(verbose_name='操作人ID')
    actor_name = models.CharField(max_length=100, verbose_name='操作人姓名')
    actor_username = models.CharField(max_length=150, verbose_name='操作人用户名')
    actor_employee_id = models.CharField(max_length=50, blank=True, null=True, verbose_name='操作人工号')
    actor_department = models.CharField(max_length=100, blank=True, null=True, verbose_name='操作人部门')
    actor_role = models.CharField(max_length=20, verbose_name='操作人角色')
    
    # 版本信息
    version_number = models.CharField(max_length=20, verbose_name='版本号')
    previous_version = models.CharField(max_length=20, blank=True, null=True, verbose_name='上一版本号')
    
    # 变更内容摘要
    changes_summary = models.TextField(blank=True, verbose_name='变更摘要')
    changes_detail = models.JSONField(default=dict, verbose_name='变更详情')
    
    # 元数据
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP地址')
    user_agent = models.TextField(blank=True, verbose_name='用户代理')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='操作时间')
    
    class Meta:
        verbose_name = '教材修改历史'
        verbose_name_plural = '教材修改历史'
        db_table = 'review_book_edit_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['book_id', '-created_at']),
            models.Index(fields=['task_id', '-created_at']),
            models.Index(fields=['actor_id', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.book_title} - {self.get_action_display()} - {self.actor_name}"


class TeacherProfile(models.Model):
    """教师档案（用于审核端展示教师信息）"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='review_teacher_profile',
        verbose_name='关联用户'
    )
    
    # 基本信息
    employee_id = models.CharField(max_length=50, unique=True, verbose_name='工号')
    name = models.CharField(max_length=100, verbose_name='姓名')
    department = models.CharField(max_length=100, verbose_name='所属部门')
    title = models.CharField(max_length=50, blank=True, null=True, verbose_name='职称')
    
    # 联系信息
    email = models.EmailField(verbose_name='邮箱')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='电话')
    office_location = models.CharField(max_length=100, blank=True, null=True, verbose_name='办公地点')
    
    # 教学信息
    teaching_subjects = models.JSONField(default=list, verbose_name='教授科目')
    research_areas = models.JSONField(default=list, verbose_name='研究领域')
    
    # 教材统计
    total_uploaded_books = models.IntegerField(default=0, verbose_name='上传教材总数')
    total_modified_books = models.IntegerField(default=0, verbose_name='修改教材总数')
    approved_books = models.IntegerField(default=0, verbose_name='已通过教材数')
    rejected_books = models.IntegerField(default=0, verbose_name='被驳回教材数')
    
    # 状态
    is_active = models.BooleanField(default=True, verbose_name='是否在职')
    
    # 时间戳
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '教师档案'
        verbose_name_plural = '教师档案'
        db_table = 'review_teacher_profile'
    
    def __str__(self):
        return f"{self.name} ({self.employee_id}) - {self.department}"

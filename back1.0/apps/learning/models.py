"""学习记录相关模型定义"""
from django.db import models
from django.contrib.auth import get_user_model
from apps.books.models import Book, Chapter

User = get_user_model()


class LearningRecord(models.Model):
    """学习记录模型"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_records', verbose_name='用户')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='learning_records', verbose_name='教材')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='learning_records', verbose_name='章节')
    progress = models.IntegerField(default=0, verbose_name='学习进度(%)')
    last_learn_time = models.DateTimeField(auto_now=True, verbose_name='最后学习时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '学习记录'
        verbose_name_plural = '学习记录'
        unique_together = ('user', 'book', 'chapter')
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} - {self.chapter.title}"


class PracticeRecord(models.Model):
    """练习记录模型"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='practice_records', verbose_name='用户')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='practice_records', verbose_name='教材')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='practice_records', verbose_name='章节')
    score = models.IntegerField(default=0, verbose_name='得分')
    completed = models.BooleanField(default=False, verbose_name='是否完成')
    user_code = models.TextField(blank=True, null=True, verbose_name='用户提交的代码')
    completed_time = models.DateTimeField(auto_now=True, verbose_name='完成时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '练习记录'
        verbose_name_plural = '练习记录'
    
    def __str__(self):
        return f"{self.user.username} - {self.book.title} - {self.chapter.title} - 得分:{self.score}"


class HeatmapData(models.Model):
    """学习热力图数据模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='heatmap_data', verbose_name='用户')
    date = models.DateField(verbose_name='日期')
    minutes = models.IntegerField(default=0, verbose_name='学习时长(分钟)')
    
    class Meta:
        verbose_name = '学习热力图数据'
        verbose_name_plural = '学习热力图数据'
        unique_together = ('user', 'date')
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.minutes}分钟"


class WrongQuestion(models.Model):
    """错题本模型"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wrong_questions', verbose_name='用户')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='wrong_questions', verbose_name='教材', null=True, blank=True)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='wrong_questions', verbose_name='章节', null=True, blank=True)
    title = models.CharField(max_length=255, verbose_name='题目')
    difficulty = models.IntegerField(default=2, verbose_name='难度(1-5)')
    question_type = models.CharField(max_length=20, default='unknown', verbose_name='题目类型')
    practice = models.ForeignKey('Exercise', on_delete=models.CASCADE, related_name='wrong_questions', null=True, blank=True, verbose_name='练习题')
    attempt_time = models.DateTimeField(auto_now=True, verbose_name='最后尝试时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='记录时间')

    class Meta:
        verbose_name = '错题'
        verbose_name_plural = '错题'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.book.title} - {self.title}"


class Exercise(models.Model):
    """独立练习题模型"""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name='题目名称')
    description = models.TextField(verbose_name='题目描述')
    question = models.TextField(verbose_name='问题内容')
    code_template = models.TextField(blank=True, null=True, verbose_name='代码模板')
    language = models.CharField(max_length=50, default='python', verbose_name='编程语言')
    difficulty = models.IntegerField(default=2, choices=[
        (1, '简单'), (2, '中等'), (3, '困难')
    ], verbose_name='难度')
    category = models.CharField(max_length=50, choices=[
        ('python_basic', 'Python基础'),
        ('javascript_basic', 'JavaScript基础'),
        ('algorithm', '算法基础'),
        ('logic', '编程思维')
    ], verbose_name='题目分类')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '练习题'
        verbose_name_plural = '练习题'
        ordering = ['category', 'difficulty', 'created_at']

    def __str__(self):
        return self.title


class ExerciseTestCase(models.Model):
    """练习题测试用例模型"""
    id = models.AutoField(primary_key=True)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='test_cases', verbose_name='练习题')
    input_data = models.JSONField(verbose_name='输入数据')
    expected_output = models.JSONField(verbose_name='期望输出')
    order = models.IntegerField(default=0, verbose_name='测试用例顺序')

    class Meta:
        verbose_name = '练习题测试用例'
        verbose_name_plural = '练习题测试用例'
        ordering = ['order']

    def __str__(self):
        return f"{self.exercise.title} - 测试用例 {self.order + 1}"


class ExerciseRecord(models.Model):
    """练习记录模型"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercise_records', verbose_name='用户')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='user_records', verbose_name='练习题')
    user_code = models.TextField(blank=True, null=True, verbose_name='用户提交的代码')
    passed = models.BooleanField(default=False, verbose_name='是否通过')
    score = models.IntegerField(default=0, verbose_name='得分')
    submitted_at = models.DateTimeField(auto_now=True, verbose_name='提交时间')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '练习题记录'
        verbose_name_plural = '练习题记录'

    def __str__(self):
        return f"{self.user.username} - {self.exercise.title} - {'通过' if self.passed else '未通过'}"


class RoadmapTemplate(models.Model):
    """路线图模板模型"""
    id = models.AutoField(primary_key=True)
    major = models.CharField(max_length=50, choices=[
        ('business', '经管类'), ('humanities', '文史类'),
        ('arts', '艺术类'), ('science', '理工科')
    ], verbose_name='专业类别')
    title = models.CharField(max_length=200, verbose_name='路线图标题')
    description = models.TextField(verbose_name='路线图描述')
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', '入门'), ('intermediate', '进阶'), ('advanced', '高级')
    ], verbose_name='难度级别')
    estimated_hours = models.IntegerField(default=40, verbose_name='预计学习时长(小时)')
    tags = models.JSONField(default=list, verbose_name='技能标签')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '路线图模板'
        verbose_name_plural = '路线图模板'

    def __str__(self):
        return f"{self.title} - {self.get_major_display()}"


class RoadmapStage(models.Model):
    """路线图阶段模型"""
    roadmap = models.ForeignKey(RoadmapTemplate, on_delete=models.CASCADE, related_name='stages', verbose_name='所属路线图')
    stage_order = models.IntegerField(verbose_name='阶段顺序')
    title = models.CharField(max_length=200, verbose_name='阶段标题')
    description = models.TextField(verbose_name='阶段描述')
    learning_goals = models.JSONField(default=list, verbose_name='学习目标列表')
    required_skills = models.JSONField(default=list, verbose_name='前置技能要求')
    estimated_duration = models.IntegerField(verbose_name='预计学习时长(小时)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '路线图阶段'
        verbose_name_plural = '路线图阶段'
        ordering = ['roadmap', 'stage_order']

    def __str__(self):
        return f"{self.roadmap.title} - {self.stage_order}. {self.title}"


class RoadmapBook(models.Model):
    """路线图与书籍的关联模型"""
    stage = models.ForeignKey(RoadmapStage, on_delete=models.CASCADE, related_name='roadmap_books', verbose_name='所属阶段')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='roadmap_books', verbose_name='教材')
    recommended_order = models.IntegerField(default=0, verbose_name='推荐阅读顺序')
    importance = models.IntegerField(default=3, choices=[
        (1, '了解'), (2, '熟悉'), (3, '重点'), (4, '核心')
    ], verbose_name='重要程度')
    notes = models.TextField(blank=True, null=True, verbose_name='学习建议')

    class Meta:
        verbose_name = '路线图书籍'
        verbose_name_plural = '路线图书籍'
        ordering = ['stage', 'recommended_order']

    def __str__(self):
        return f"{self.stage.title} - {self.book.title}"


class UserLearningPath(models.Model):
    """用户学习路径模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='learning_paths', verbose_name='用户')
    roadmap = models.ForeignKey(RoadmapTemplate, on_delete=models.CASCADE, related_name='user_paths', verbose_name='路线图模板')
    current_stage = models.ForeignKey(RoadmapStage, on_delete=models.SET_NULL, null=True, related_name='current_user_paths', verbose_name='当前阶段')
    progress = models.IntegerField(default=0, verbose_name='总体进度百分比')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始学习时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    custom_goals = models.JSONField(default=list, verbose_name='用户自定义目标')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '用户学习路径'
        verbose_name_plural = '用户学习路径'
        unique_together = ('user', 'roadmap')

    def __str__(self):
        return f"{self.user.username} - {self.roadmap.title}"


class UserPathStage(models.Model):
    """用户路径阶段进度模型"""
    user_path = models.ForeignKey(UserLearningPath, on_delete=models.CASCADE, related_name='stage_progress', verbose_name='用户学习路径')
    stage = models.ForeignKey(RoadmapStage, on_delete=models.CASCADE, related_name='user_progress', verbose_name='路线图阶段')
    progress = models.IntegerField(default=0, verbose_name='阶段进度百分比')
    is_completed = models.BooleanField(default=False, verbose_name='是否完成')
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    notes = models.TextField(blank=True, null=True, verbose_name='学习笔记')

    class Meta:
        verbose_name = '用户路径阶段'
        verbose_name_plural = '用户路径阶段'
        unique_together = ('user_path', 'stage')

    def __str__(self):
        return f"{self.user_path} - {self.stage.title} - {self.progress}%"


class Note(models.Model):
    """笔记模型"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes', verbose_name='用户')
    title = models.CharField(max_length=255, verbose_name='笔记标题')
    content = models.TextField(verbose_name='笔记内容')
    
    # 关联字段
    book = models.ForeignKey('books.Book', on_delete=models.SET_NULL, null=True, blank=True, related_name='notes', verbose_name='关联教材')
    chapter = models.ForeignKey('books.Chapter', on_delete=models.SET_NULL, null=True, blank=True, related_name='notes', verbose_name='关联章节')
    position = models.TextField(blank=True, null=True, verbose_name='位置信息（JSON格式）')
    
    # 状态字段
    is_favorite = models.BooleanField(default=False, verbose_name='是否收藏')
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    view_count = models.IntegerField(default=0, verbose_name='查看次数')
    
    # 时间字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    last_reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name='最后复习时间')
    
    class Meta:
        verbose_name = '笔记'
        verbose_name_plural = '笔记'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['book', 'chapter']),
            models.Index(fields=['is_favorite']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class NoteTag(models.Model):
    """笔记标签"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, verbose_name='标签名称')
    color = models.CharField(max_length=7, default='#409EFF', verbose_name='标签颜色')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='note_tags', verbose_name='创建用户')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '笔记标签'
        verbose_name_plural = '笔记标签'
        unique_together = ('user', 'name')
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class NoteTagRelation(models.Model):
    """笔记标签关联"""
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='tag_relations')
    tag = models.ForeignKey(NoteTag, on_delete=models.CASCADE, related_name='note_relations')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '笔记标签关联'
        verbose_name_plural = '笔记标签关联'
        unique_together = ('note', 'tag')
    
    def __str__(self):
        return f"{self.note.title} - {self.tag.name}"


class NoteAttachment(models.Model):
    """笔记附件"""
    id = models.AutoField(primary_key=True)
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='attachments', verbose_name='笔记')
    file = models.FileField(upload_to='note_attachments/%Y/%m/', verbose_name='附件文件')
    file_name = models.CharField(max_length=255, verbose_name='文件名')
    file_size = models.IntegerField(verbose_name='文件大小（字节）')
    file_type = models.CharField(max_length=50, verbose_name='文件类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='上传时间')
    
    class Meta:
        verbose_name = '笔记附件'
        verbose_name_plural = '笔记附件'
    
    def __str__(self):
        return f"{self.note.title} - {self.file_name}"


class NoteVersion(models.Model):
    """笔记版本历史"""
    id = models.AutoField(primary_key=True)
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='versions', verbose_name='笔记')
    title = models.CharField(max_length=255, verbose_name='标题')
    content = models.TextField(verbose_name='内容')
    version_number = models.IntegerField(verbose_name='版本号')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '笔记版本历史'
        verbose_name_plural = '笔记版本历史'
        ordering = ['-version_number']
    
    def __str__(self):
        return f"{self.note.title} - v{self.version_number}"


class NoteShare(models.Model):
    """笔记分享"""
    id = models.AutoField(primary_key=True)
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='shares', verbose_name='笔记')
    share_code = models.CharField(max_length=32, unique=True, verbose_name='分享码')
    shared_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shared_notes', verbose_name='分享者')
    shared_to = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='received_notes', verbose_name='接收者')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='过期时间')
    view_count = models.IntegerField(default=0, verbose_name='查看次数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '笔记分享'
        verbose_name_plural = '笔记分享'
    
    def __str__(self):
        return f"{self.note.title} - {self.share_code}"


class JupyterDocument(models.Model):
    """Jupyter风格交互式文档模型"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='jupyter_documents', verbose_name='用户')
    title = models.CharField(max_length=255, verbose_name='文档标题')
    content = models.TextField(verbose_name='文档内容（Markdown格式）')
    book = models.ForeignKey('books.Book', on_delete=models.SET_NULL, null=True, blank=True, related_name='jupyter_documents', verbose_name='关联书籍')
    chapter = models.ForeignKey('books.Chapter', on_delete=models.SET_NULL, null=True, blank=True, related_name='jupyter_documents', verbose_name='关联章节')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_public = models.BooleanField(default=False, verbose_name='是否公开')
    
    class Meta:
        verbose_name = 'Jupyter文档'
        verbose_name_plural = 'Jupyter文档'
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"


class LearningStyle(models.Model):
    """用户学习风格模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learning_style', verbose_name='用户')
    # 视觉学习者、听觉学习者、读写学习者、动手实践学习者
    visual_score = models.FloatField(default=0.5, verbose_name='视觉学习偏好度')
    auditory_score = models.FloatField(default=0.5, verbose_name='听觉学习偏好度')
    reading_score = models.FloatField(default=0.5, verbose_name='读写学习偏好度')
    kinesthetic_score = models.FloatField(default=0.5, verbose_name='动手实践偏好度')
    
    # 学习节奏偏好：快速学习、深入学习
    pace_preference = models.CharField(max_length=20, choices=[
        ('fast', '快速学习'), ('deep', '深入学习'), ('balanced', '平衡型')
    ], default='balanced', verbose_name='学习节奏偏好')
    
    # 学习环境偏好
    environment_preference = models.CharField(max_length=50, choices=[
        ('quiet', '安静环境'), ('moderate_noise', '适度噪音'), ('collaborative', '协作环境')
    ], default='quiet', verbose_name='学习环境偏好')
    
    # 偏好的学习资源类型
    preferred_resource_types = models.JSONField(default=list, verbose_name='偏好的学习资源类型')
    
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '学习风格'
        verbose_name_plural = '学习风格'
    
    def __str__(self):
        return f"{self.user.username}的学习风格"


class KnowledgeMastery(models.Model):
    """知识点掌握度模型"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='knowledge_mastery', verbose_name='用户')
    
    # 知识点可以与书籍和章节关联
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True, related_name='knowledge_mastery', verbose_name='关联书籍')
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True, related_name='knowledge_mastery', verbose_name='关联章节')
    
    # 知识点名称或标识
    knowledge_point = models.CharField(max_length=255, verbose_name='知识点名称')
    
    # 掌握度评分（0-1之间）
    mastery_level = models.FloatField(default=0.0, verbose_name='掌握度评分')
    
    # 最近评估时间
    assessed_at = models.DateTimeField(auto_now=True, verbose_name='最近评估时间')
    
    # 评估次数
    assessment_count = models.IntegerField(default=0, verbose_name='评估次数')
    
    # 相关标签
    tags = models.JSONField(default=list, verbose_name='知识点标签')
    
    class Meta:
        verbose_name = '知识掌握度'
        verbose_name_plural = '知识掌握度'
        unique_together = ('user', 'knowledge_point', 'book', 'chapter')
    
    def __str__(self):
        return f"{self.user.username} - {self.knowledge_point} - {self.mastery_level:.2f}"


class LearningRecommendation(models.Model):
    """学习推荐记录模型"""
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recommendations', verbose_name='用户')
    
    # 关联的学习路径
    user_path = models.ForeignKey(UserLearningPath, on_delete=models.SET_NULL, null=True, blank=True, related_name='recommendations', verbose_name='用户学习路径')
    
    # 推荐的内容类型和关联
    recommendation_type = models.CharField(max_length=50, choices=[
        ('roadmap', '路线图'), ('stage', '学习阶段'), ('book', '书籍'),
        ('chapter', '章节'), ('exercise', '练习题'), ('resource', '其他资源')
    ], verbose_name='推荐类型')
    
    # 关联的具体内容
    roadmap = models.ForeignKey(RoadmapTemplate, on_delete=models.SET_NULL, null=True, blank=True, related_name='recommendations', verbose_name='推荐路线图')
    stage = models.ForeignKey(RoadmapStage, on_delete=models.SET_NULL, null=True, blank=True, related_name='recommendations', verbose_name='推荐阶段')
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True, related_name='recommendations', verbose_name='推荐书籍')
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True, related_name='recommendations', verbose_name='推荐章节')
    exercise = models.ForeignKey(Exercise, on_delete=models.SET_NULL, null=True, blank=True, related_name='recommendations', verbose_name='推荐练习题')
    
    # 推荐原因
    reason = models.TextField(blank=True, null=True, verbose_name='推荐原因')
    
    # 推荐分数（0-1之间）
    score = models.FloatField(default=0.0, verbose_name='推荐分数')
    
    # 推荐时间
    recommended_at = models.DateTimeField(auto_now_add=True, verbose_name='推荐时间')
    
    # 用户反馈
    user_feedback = models.CharField(max_length=20, choices=[
        ('none', '未反馈'), ('accepted', '已接受'), ('rejected', '已拒绝')
    ], default='none', verbose_name='用户反馈')
    
    # 反馈时间
    feedback_at = models.DateTimeField(null=True, blank=True, verbose_name='反馈时间')
    
    class Meta:
        verbose_name = '学习推荐'
        verbose_name_plural = '学习推荐'
        ordering = ['-score', '-recommended_at']
    
    def __str__(self):
        return f"{self.user.username}的推荐 - {self.get_recommendation_type_display()}"


class LearningPreference(models.Model):
    """学习偏好设置模型"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='learning_preference', verbose_name='用户')
    
    # 学习目标
    learning_goals = models.JSONField(default=list, verbose_name='学习目标')
    
    # 兴趣领域
    interest_areas = models.JSONField(default=list, verbose_name='兴趣领域')
    
    # 每天可用学习时间（分钟）
    daily_available_minutes = models.IntegerField(default=60, verbose_name='每天可用学习时间')
    
    # 学习提醒设置
    reminder_enabled = models.BooleanField(default=False, verbose_name='是否启用学习提醒')
    reminder_time = models.TimeField(null=True, blank=True, verbose_name='学习提醒时间')
    
    # 难度偏好
    difficulty_preference = models.CharField(max_length=20, choices=[
        ('easy', '偏简单'), ('medium', '适中'), ('challenging', '偏难'), ('mixed', '混合')
    ], default='medium', verbose_name='难度偏好')
    
    # 更新时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '学习偏好'
        verbose_name_plural = '学习偏好'
    
    def __str__(self):
        return f"{self.user.username}的学习偏好"


# 知识图谱相关模型
class KnowledgeGraph(models.Model):
    """知识图谱模型"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='图谱名称')
    description = models.TextField(verbose_name='图谱描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    
    class Meta:
        verbose_name = '知识图谱'
        verbose_name_plural = '知识图谱'
    
    def __str__(self):
        return self.name


class KnowledgeNode(models.Model):
    """知识节点模型"""
    id = models.AutoField(primary_key=True)
    graph = models.ForeignKey(KnowledgeGraph, on_delete=models.CASCADE, related_name='nodes', verbose_name='所属图谱')
    title = models.CharField(max_length=200, verbose_name='节点标题')
    type = models.CharField(max_length=50, choices=[
        ('concept', '概念层'),
        ('professional_integration', '专业融合层'),
        ('skill', '技能层'),
        ('resource', '资源层')
    ], verbose_name='节点类型')
    level = models.IntegerField(default=1, verbose_name='节点层级')
    difficulty = models.FloatField(default=3.0, verbose_name='难度系数')
    importance = models.FloatField(default=3.0, verbose_name='重要程度')
    description = models.TextField(verbose_name='节点描述')
    professional_group = models.CharField(max_length=50, choices=[
        ('business', '经管类'),
        ('humanities', '文史类'),
        ('arts', '艺术类'),
        ('science', '理工科')
    ], verbose_name='专业组')
    tags = models.JSONField(default=list, verbose_name='节点标签')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '知识节点'
        verbose_name_plural = '知识节点'
        ordering = ['level', 'importance', 'difficulty']
    
    def __str__(self):
        return f"{self.title} ({self.get_type_display()})"


class KnowledgeRelation(models.Model):
    """知识关系模型"""
    id = models.AutoField(primary_key=True)
    graph = models.ForeignKey(KnowledgeGraph, on_delete=models.CASCADE, related_name='relations', verbose_name='所属图谱')
    source = models.ForeignKey(KnowledgeNode, on_delete=models.CASCADE, related_name='outgoing_relations', verbose_name='源节点')
    target = models.ForeignKey(KnowledgeNode, on_delete=models.CASCADE, related_name='incoming_relations', verbose_name='目标节点')
    relation_type = models.CharField(max_length=50, choices=[
        ('prerequisite', '前置依赖'),
        ('related', '相关知识'),
        ('application', '应用场景'),
        ('advanced', '进阶知识'),
        ('professional', '专业关联')
    ], verbose_name='关系类型')
    strength = models.FloatField(default=1.0, verbose_name='关系强度')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '知识关系'
        verbose_name_plural = '知识关系'
        unique_together = ('source', 'target', 'relation_type')
    
    def __str__(self):
        return f"{self.source.title} - {self.get_relation_type_display()} - {self.target.title}"


# 大模型相关模型
class LLMIntegration(models.Model):
    """大模型集成配置"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='配置名称')
    provider = models.CharField(max_length=50, choices=[
        ('openai', 'OpenAI'),
        ('anthropic', 'Anthropic'),
        ('baidu', '百度文心一言'),
        ('alibaba', '阿里云通义千问'),
        ('doubao', '豆包(Doubao)')
    ], verbose_name='大模型提供商')
    api_key = models.CharField(max_length=255, verbose_name='API密钥')
    model_name = models.CharField(max_length=100, verbose_name='模型名称')
    is_active = models.BooleanField(default=True, verbose_name='是否激活')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '大模型配置'
        verbose_name_plural = '大模型配置'
    
    def __str__(self):
        return self.name


class PromptTemplate(models.Model):
    """大模型Prompt模板"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name='模板名称')
    template = models.TextField(verbose_name='模板内容')
    type = models.CharField(max_length=50, choices=[
        ('knowledge_extraction', '知识提取'),
        ('path_generation', '路径生成'),
        ('content_explanation', '内容解释'),
        ('feedback_generation', '反馈生成'),
        ('question_answering', '问答')
    ], verbose_name='模板类型')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'Prompt模板'
        verbose_name_plural = 'Prompt模板'
    
    def __str__(self):
        return self.name

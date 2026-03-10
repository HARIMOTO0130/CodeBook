"""StrategyKG 四层知识图谱模型

基于认知科学中的"抽象阶梯"理论，将知识分为四个层次：
- Level 0: 概念层 - 基础理论知识
- Level 1: 分类层 - 技术领域知识
- Level 2: 实体层 - 具体技能知识
- Level 3: 动态层 - 实时数据流
"""

from django.db import models
from django.contrib.auth import get_user_model
from apps.books.models import Book, Chapter

User = get_user_model()


class StrategyKnowledgeNode(models.Model):
    """StrategyKG 知识节点模型 - 支持四层抽象结构"""
    
    LEVEL_CHOICES = [
        (0, 'Level 0 - 概念层'),
        (1, 'Level 1 - 分类层'),
        (2, 'Level 2 - 实体层'),
        (3, 'Level 3 - 动态层'),
    ]
    
    NODE_TYPE_CHOICES = [
        ('concept', '概念'),
        ('skill', '技能'),
        ('resource', '资源'),
        ('path', '路径'),
        ('application', '应用'),
    ]
    
    TEMPORAL_CHOICES = [
        ('atemporal', '无时间性'),
        ('long_term', '长期趋势'),
        ('historical', '历史时态'),
        ('realtime', '实时流'),
    ]
    
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name='节点标题')
    description = models.TextField(verbose_name='节点描述')
    
    level = models.IntegerField(choices=LEVEL_CHOICES, verbose_name='知识层级', db_index=True)
    node_type = models.CharField(max_length=50, choices=NODE_TYPE_CHOICES, verbose_name='节点类型')
    temporal = models.CharField(max_length=20, choices=TEMPORAL_CHOICES, default='atemporal', verbose_name='时间属性')
    
    difficulty = models.FloatField(default=1.0, verbose_name='难度系数')
    importance = models.FloatField(default=3.0, verbose_name='重要性')
    
    tags = models.JSONField(default=list, verbose_name='标签列表')
    metadata = models.JSONField(default=dict, verbose_name='元数据')
    
    professional_group = models.CharField(max_length=50, verbose_name='专业组', db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'StrategyKG知识节点'
        verbose_name_plural = 'StrategyKG知识节点'
        indexes = [
            models.Index(fields=['level', 'professional_group']),
            models.Index(fields=['node_type']),
            models.Index(fields=['difficulty']),
        ]
    
    def __str__(self):
        return f"L{self.level} - {self.title}"


class StrategyRelation(models.Model):
    """StrategyKG 知识关系模型"""
    
    RELATION_TYPE_CHOICES = [
        ('requires', '前置依赖'),
        ('belongs_to', '属于'),
        ('includes', '包含'),
        ('recommends', '推荐'),
        ('leads_to', '导向'),
        ('applies_to', '应用于'),
        ('similar_to', '相似于'),
    ]
    
    id = models.AutoField(primary_key=True)
    source = models.ForeignKey(
        StrategyKnowledgeNode, 
        on_delete=models.CASCADE, 
        related_name='outgoing_relations',
        verbose_name='源节点'
    )
    target = models.ForeignKey(
        StrategyKnowledgeNode, 
        on_delete=models.CASCADE, 
        related_name='incoming_relations',
        verbose_name='目标节点'
    )
    relation_type = models.CharField(max_length=50, choices=RELATION_TYPE_CHOICES, verbose_name='关系类型')
    
    strength = models.FloatField(default=1.0, verbose_name='关系强度')
    confidence = models.FloatField(default=1.0, verbose_name='置信度')
    
    metadata = models.JSONField(default=dict, verbose_name='关系元数据')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'StrategyKG知识关系'
        verbose_name_plural = 'StrategyKG知识关系'
        unique_together = ('source', 'target', 'relation_type')
        indexes = [
            models.Index(fields=['relation_type']),
            models.Index(fields=['strength']),
        ]
    
    def __str__(self):
        return f"{self.source.title} - {self.get_relation_type_display()} - {self.target.title}"


class StrategyLearningPath(models.Model):
    """StrategyKG 学习路径模型"""
    
    STATUS_CHOICES = [
        ('draft', '草稿'),
        ('active', '激活'),
        ('archived', '归档'),
    ]
    
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name='路径标题')
    description = models.TextField(verbose_name='路径描述')
    
    professional_group = models.CharField(max_length=50, verbose_name='专业组')
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', '入门'),
        ('intermediate', '进阶'),
        ('advanced', '高级'),
    ], verbose_name='难度级别')
    
    estimated_hours = models.IntegerField(default=40, verbose_name='预计学习时长(小时)')
    
    tags = models.JSONField(default=list, verbose_name='技能标签')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='状态')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'StrategyKG学习路径'
        verbose_name_plural = 'StrategyKG学习路径'
    
    def __str__(self):
        return self.title


class StrategyPathNode(models.Model):
    """StrategyKG 路径节点关联模型"""
    
    id = models.AutoField(primary_key=True)
    path = models.ForeignKey(
        StrategyLearningPath, 
        on_delete=models.CASCADE, 
        related_name='path_nodes',
        verbose_name='所属路径'
    )
    node = models.ForeignKey(
        StrategyKnowledgeNode, 
        on_delete=models.CASCADE, 
        related_name='path_associations',
        verbose_name='知识节点'
    )
    order = models.IntegerField(verbose_name='节点顺序')
    is_required = models.BooleanField(default=True, verbose_name='是否必修')
    estimated_hours = models.IntegerField(default=0, verbose_name='预计学习时长(小时)')
    
    class Meta:
        verbose_name = 'StrategyKG路径节点'
        verbose_name_plural = 'StrategyKG路径节点'
        unique_together = ('path', 'node')
        ordering = ['path', 'order']
    
    def __str__(self):
        return f"{self.path.title} - {self.order}. {self.node.title}"


class UserStrategyPath(models.Model):
    """用户 StrategyKG 学习路径关联模型"""
    
    STATUS_CHOICES = [
        ('not_started', '未开始'),
        ('active', '学习中'),
        ('paused', '暂停'),
        ('completed', '已完成'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='strategy_paths', verbose_name='用户')
    path = models.ForeignKey(StrategyLearningPath, on_delete=models.CASCADE, related_name='user_paths', verbose_name='学习路径')
    
    current_node = models.ForeignKey(
        StrategyPathNode, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='current_users',
        verbose_name='当前节点'
    )
    
    progress = models.IntegerField(default=0, verbose_name='总体进度百分比')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started', verbose_name='状态')
    
    custom_goals = models.JSONField(default=list, verbose_name='用户自定义目标')
    notes = models.TextField(blank=True, null=True, verbose_name='学习笔记')
    
    started_at = models.DateTimeField(auto_now_add=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户StrategyKG路径'
        verbose_name_plural = '用户StrategyKG路径'
        unique_together = ('user', 'path')
    
    def __str__(self):
        return f"{self.user.username} - {self.path.title}"


class UserNodeProgress(models.Model):
    """用户节点学习进度模型"""
    
    MASTERY_LEVEL_CHOICES = [
        (0, '未学习'),
        (1, '了解'),
        (2, '熟悉'),
        (3, '掌握'),
        (4, '精通'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='node_progress', verbose_name='用户')
    user_path = models.ForeignKey(
        UserStrategyPath, 
        on_delete=models.CASCADE, 
        related_name='node_progresses',
        verbose_name='用户路径'
    )
    node = models.ForeignKey(
        StrategyKnowledgeNode, 
        on_delete=models.CASCADE, 
        related_name='user_progress',
        verbose_name='知识节点'
    )
    
    mastery_level = models.IntegerField(choices=MASTERY_LEVEL_CHOICES, default=0, verbose_name='掌握程度')
    learning_hours = models.FloatField(default=0, verbose_name='学习时长(小时)')
    
    notes = models.TextField(blank=True, null=True, verbose_name='学习笔记')
    
    started_at = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='完成时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户节点进度'
        verbose_name_plural = '用户节点进度'
        unique_together = ('user', 'node')
    
    def __str__(self):
        return f"{self.user.username} - {self.node.title} - {self.get_mastery_level_display()}"


class StrategyRecommendation(models.Model):
    """StrategyKG 个性化推荐模型"""
    
    RECOMMENDATION_TYPE_CHOICES = [
        ('path', '学习路径'),
        ('node', '知识点'),
        ('resource', '学习资源'),
        ('practice', '练习题'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='strategy_recommendations', verbose_name='用户')
    
    recommendation_type = models.CharField(max_length=20, choices=RECOMMENDATION_TYPE_CHOICES, verbose_name='推荐类型')
    
    recommended_path = models.ForeignKey(
        StrategyLearningPath, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='recommendations',
        verbose_name='推荐路径'
    )
    recommended_node = models.ForeignKey(
        StrategyKnowledgeNode, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='recommendations',
        verbose_name='推荐节点'
    )
    
    matching_score = models.FloatField(default=0, verbose_name='匹配度分数')
    recommendation_reason = models.TextField(verbose_name='推荐理由')
    
    is_accepted = models.BooleanField(null=True, blank=True, verbose_name='是否接受')
    user_feedback = models.TextField(blank=True, null=True, verbose_name='用户反馈')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = 'StrategyKG推荐'
        verbose_name_plural = 'StrategyKG推荐'
        ordering = ['-matching_score', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_recommendation_type_display()}"


class StrategyUserProfile(models.Model):
    """StrategyKG 用户画像模型"""
    
    LEARNING_STYLE_CHOICES = [
        ('visual', '视觉学习者'),
        ('auditory', '听觉学习者'),
        ('reading', '读写学习者'),
        ('kinesthetic', '动手实践学习者'),
    ]
    
    PACING_CHOICES = [
        ('fast', '快速学习'),
        ('deep', '深入学习'),
        ('balanced', '平衡型'),
    ]
    
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='strategy_profile', verbose_name='用户')
    
    professional_group = models.CharField(max_length=50, verbose_name='专业组')
    
    knowledge_level = models.CharField(max_length=20, choices=[
        ('beginner', '初学者'),
        ('intermediate', '中级'),
        ('advanced', '高级'),
    ], verbose_name='知识水平')
    
    learning_style = models.CharField(max_length=20, choices=LEARNING_STYLE_CHOICES, verbose_name='学习风格')
    pacing_preference = models.CharField(max_length=20, choices=PACING_CHOICES, default='balanced', verbose_name='学习节奏偏好')
    
    interests = models.JSONField(default=list, verbose_name='兴趣领域')
    learning_goals = models.JSONField(default=list, verbose_name='学习目标')
    
    total_learning_minutes = models.IntegerField(default=0, verbose_name='总学习时长(分钟)')
    completed_practices = models.IntegerField(default=0, verbose_name='完成练习数')
    avg_practice_score = models.FloatField(default=0, verbose_name='平均练习得分')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'StrategyKG用户画像'
        verbose_name_plural = 'StrategyKG用户画像'
    
    def __str__(self):
        return f"{self.user.username} - {self.professional_group}"


class StrategyResource(models.Model):
    """StrategyKG 学习资源模型"""
    
    RESOURCE_TYPE_CHOICES = [
        ('book', '教材'),
        ('video', '视频'),
        ('article', '文章'),
        ('practice', '练习'),
        ('project', '项目'),
    ]
    
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, verbose_name='资源标题')
    description = models.TextField(verbose_name='资源描述')
    
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES, verbose_name='资源类型')
    url = models.URLField(blank=True, null=True, verbose_name='资源链接')
    
    node = models.ForeignKey(
        StrategyKnowledgeNode, 
        on_delete=models.CASCADE, 
        related_name='resources',
        verbose_name='关联知识点'
    )
    
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, blank=True, related_name='strategy_resources', verbose_name='关联教材')
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True, related_name='strategy_resources', verbose_name='关联章节')
    
    difficulty = models.FloatField(default=1.0, verbose_name='难度')
    quality_score = models.FloatField(default=3.0, verbose_name='质量评分')
    
    tags = models.JSONField(default=list, verbose_name='标签')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = 'StrategyKG学习资源'
        verbose_name_plural = 'StrategyKG学习资源'
    
    def __str__(self):
        return self.title
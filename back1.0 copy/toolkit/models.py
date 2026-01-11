from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class ToolCategory(models.Model):
    """工具分类"""
    name = models.CharField(max_length=50, unique=True, verbose_name="分类名称", default='未分类')
    slug = models.SlugField(max_length=50, unique=True, verbose_name="分类标识", default='default-category')
    description = models.TextField(blank=True, verbose_name="分类描述", default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "工具分类"
        verbose_name_plural = "工具分类"
        app_label = 'toolkit'
    
    def __str__(self):
        return self.name


class Tool(models.Model):
    """工具定义"""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="工具名称", default='未命名工具')
    slug = models.SlugField(max_length=100, unique=True, verbose_name="工具标识", default='default-tool')
    description = models.TextField(verbose_name="工具描述", default='')
    icon = models.CharField(max_length=20, default="🔧", verbose_name="工具图标")
    category = models.ForeignKey(ToolCategory, on_delete=models.CASCADE, related_name="tools", verbose_name="所属分类")
    book_id = models.IntegerField(null=True, blank=True, verbose_name="关联教材ID")
    book_title = models.CharField(max_length=100, blank=True, verbose_name="关联教材名称")
    chapter_number = models.IntegerField(null=True, blank=True, verbose_name="关联章节号")
    first_section_id = models.IntegerField(null=True, blank=True, verbose_name="首个相关章节ID")
    implementation_class = models.CharField(max_length=100, verbose_name="实现类名", default='')
    is_active = models.BooleanField(default=True, verbose_name="是否启用")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "工具"
        verbose_name_plural = "工具"
        app_label = 'toolkit'
    
    def __str__(self):
        return self.name


class ToolParameter(models.Model):
    """工具参数定义"""
    PARAM_TYPES = [
        ('text', '文本'),
        ('number', '数字'),
        ('select', '下拉选择'),
        ('textarea', '多行文本'),
        ('file', '文件上传')
    ]
    
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name="parameters", verbose_name="所属工具")
    name = models.CharField(max_length=50, verbose_name="参数名")
    label = models.CharField(max_length=100, verbose_name="参数标签")
    type = models.CharField(max_length=20, choices=PARAM_TYPES, verbose_name="参数类型")
    placeholder = models.CharField(max_length=200, blank=True, verbose_name="占位提示")
    default_value = models.CharField(max_length=500, blank=True, verbose_name="默认值")
    is_required = models.BooleanField(default=True, verbose_name="是否必填")
    options = models.JSONField(default=list, blank=True, verbose_name="选项列表")
    order = models.IntegerField(default=0, verbose_name="排序")
    
    class Meta:
        verbose_name = "工具参数"
        verbose_name_plural = "工具参数"
        ordering = ['order']
        app_label = 'toolkit'
    
    def __str__(self):
        return f"{self.tool.name} - {self.label}"


class ExecutionHistory(models.Model):
    """工具执行历史"""
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tool_executions", verbose_name="执行用户")
    tool = models.ForeignKey(Tool, on_delete=models.CASCADE, related_name="executions", verbose_name="执行工具")
    parameters = models.JSONField(verbose_name="执行参数")
    result = models.TextField(blank=True, verbose_name="执行结果")
    status = models.CharField(max_length=20, choices=[
        ('success', '成功'),
        ('failed', '失败'),
        ('running', '运行中')
    ], verbose_name="执行状态")
    error_message = models.TextField(blank=True, verbose_name="错误信息")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="执行时间")
    
    class Meta:
        verbose_name = "执行历史"
        verbose_name_plural = "执行历史"
        app_label = 'toolkit'
    
    def __str__(self):
        return f"{self.user} - {self.tool.name} - {self.created_at}"
"""书籍相关模型定义"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
import json
import os
import logging

logger = logging.getLogger(__name__)

# 导入Jupyter Notebook相关模型
from .jupyter_models import JupyterNotebook, JupyterCell, JupyterOutput


class BookCategory(models.Model):
    """教材分类（支持层级结构）"""
    name = models.CharField(max_length=100, verbose_name='分类名称')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='分类标识')
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='父分类'
    )
    description = models.TextField(blank=True, verbose_name='分类描述')
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '书籍分类'
        verbose_name_plural = '书籍分类'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class BookTag(models.Model):
    """教材标签（结构化管理）"""
    name = models.CharField(max_length=50, unique=True, verbose_name='标签名')
    description = models.TextField(blank=True, verbose_name='标签描述')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '书籍标签'
        verbose_name_plural = '书籍标签'

    def __str__(self):
        return self.name


class Book(models.Model):
    """教材书籍模型（面向学生端 + 教材提供者端）"""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name='书名')
    author = models.CharField(max_length=100, verbose_name='作者')
    cover = models.ImageField(upload_to='book_covers/', null=True, blank=True, verbose_name='封面')
    pdf_file = models.FileField(upload_to='book_pdfs/', null=True, blank=True, verbose_name='PDF文件')
    description = models.TextField(verbose_name='描述')

    # 旧版字符串标签（JSON数组），保留用于兼容
    tags = models.TextField(blank=True, default='[]', verbose_name='标签(JSON)')

    # 新版结构化分类 / 标签，多对多关系
    categories = models.ManyToManyField(
        BookCategory,
        blank=True,
        related_name='books',
        verbose_name='所属分类'
    )
    tag_objects = models.ManyToManyField(
        BookTag,
        blank=True,
        related_name='books',
        verbose_name='标签对象'
    )

    owner = models.ForeignKey(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_books',
        verbose_name='上传者'
    )

    # 归档标记（代替物理删除，用于教材提供者端的“归档/下架”）
    is_archived = models.BooleanField(default=False, verbose_name='是否归档')

    chapter_count = models.IntegerField(default=0, verbose_name='章节数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    current_version = models.CharField(max_length=20, default='1.0', verbose_name='当前版本')

    @property
    def tag_list(self):
        """
        兼容旧版的标签JSON字段，仍然对前端暴露为列表。
        教材提供者端后续可以渐进迁移到 BookTag 多对多关系。
        """
        try:
            return json.loads(self.tags) if self.tags else []
        except json.JSONDecodeError:
            return []

    @tag_list.setter
    def tag_list(self, value):
        """设置旧版标签JSON字段（保持兼容）"""
        self.tags = json.dumps(value) if isinstance(value, list) else '[]'

    class Meta:
        verbose_name = '教材'
        verbose_name_plural = '教材'

    def __str__(self):
        return self.title

    def delete(self, *args, **kwargs):
        """
        删除书籍时同时删除相关的PDF文件。
        教材提供者端一般不建议直接物理删除，可以通过 is_archived 做软删除。
        """
        # 先保存文件路径以便后续删除
        pdf_path = None
        if self.pdf_file and hasattr(self.pdf_file, 'path'):
            pdf_path = self.pdf_file.path

        # 调用父类的delete方法删除数据库记录
        super().delete(*args, **kwargs)

        # 如果文件存在，则删除物理文件
        if pdf_path and os.path.exists(pdf_path):
            try:
                os.remove(pdf_path)
                logger.info(f"成功删除PDF文件: {pdf_path}")
            except Exception as e:
                logger.error(f"删除PDF文件失败 {pdf_path}: {str(e)}")

    def save(self, *args, **kwargs):
        # 计算章节数
        if self.pk:
            # 已经有主键的情况，计算非练习类型的章节数
            self.chapter_count = self.chapters.filter(type__in=['reading', 'video']).count()
        else:
            # 新建记录时，章节数默认为0
            self.chapter_count = 0

        # 保存实例
        super().save(*args, **kwargs)


class BookVersion(models.Model):
    """教材版本信息（支持版本历史与回滚）"""
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name='原始书籍'
    )
    version_number = models.IntegerField(verbose_name='版本号')
    title = models.CharField(max_length=200, verbose_name='标题')
    author = models.CharField(max_length=100, verbose_name='作者')
    description = models.TextField(verbose_name='描述')
    pdf_file = models.FileField(
        upload_to='book_versions/',
        null=True,
        blank=True,
        verbose_name='版本PDF文件'
    )
    tags = models.TextField(blank=True, default='[]', verbose_name='标签(JSON)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    created_by = models.ForeignKey(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='版本创建人'
    )
    comment = models.TextField(blank=True, verbose_name='版本说明')
    is_branch = models.BooleanField(default=False, verbose_name='是否分支版本')
    parent_version = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='child_versions',
        verbose_name='父版本'
    )

    class Meta:
        verbose_name = '教材版本'
        verbose_name_plural = '教材版本'
        ordering = ['book_id', '-version_number']

    def __str__(self):
        return f"{self.book.title} - v{self.version_number}"


class Chapter(models.Model):
    """章节模型"""
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chapters', verbose_name='所属书籍')
    title = models.CharField(max_length=200, verbose_name='章节标题')
    type = models.CharField(
        max_length=20, 
        choices=[('reading', '阅读'), ('video', '视频'), ('practice', '练习')],
        default='reading',
        verbose_name='章节类型'
    )
    duration = models.IntegerField(default=30, verbose_name='预计时长(分钟)')
    description = models.TextField(verbose_name='章节描述')
    content = models.TextField(blank=True, null=True, verbose_name='章节内容')
    code = models.TextField(blank=True, null=True, verbose_name='示例代码')
    jupyter_content = models.TextField(blank=True, null=True, verbose_name='Jupyter文档内容')
    # 添加合并内容字段，用于存储所有内容的统一表示
    merged_content = models.TextField(blank=True, null=True, verbose_name='合并内容')
    language = models.CharField(max_length=50, default='python', verbose_name='编程语言')
    content_type = models.CharField(
        max_length=20, 
        choices=[('markdown', 'Markdown'), ('jupyter', 'Jupyter')],
        default='markdown',
        verbose_name='内容类型'
    )
    video_url = models.URLField(blank=True, null=True, verbose_name='视频URL')
    order = models.IntegerField(default=0, verbose_name='排序')
    level = models.IntegerField(default=1, verbose_name='章节级别')
    is_main_chapter = models.BooleanField(default=True, verbose_name='是否为主章节')
    parent_chapter = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True, related_name='sub_chapters', verbose_name='父章节')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    def save(self, *args, **kwargs):
        """保存前合并所有内容"""
        import json
        
        # 创建合并内容的Jupyter格式
        merged_cells = []
        
        # 尝试解析已有的jupyter_content
        if self.jupyter_content:
            try:
                jupyter_data = json.loads(self.jupyter_content)
                if isinstance(jupyter_data, dict) and 'cells' in jupyter_data:
                    # 保留已有的Jupyter单元格
                    merged_cells.extend(jupyter_data['cells'])
                elif isinstance(jupyter_data, list):
                    # 如果是直接的cells数组
                    merged_cells.extend(jupyter_data)
            except json.JSONDecodeError:
                # 如果解析失败，将其作为普通文本处理
                if self.jupyter_content.strip():
                    merged_cells.append({
                        'cell_type': 'markdown',
                        'source': [self.jupyter_content],
                        'metadata': {}
                    })
        
        # 添加content字段内容作为Markdown单元格
        if self.content and self.content.strip():
            # 检查是否已经包含在jupyter_content中
            content_exists = False
            for cell in merged_cells:
                if cell.get('cell_type') == 'markdown' and cell.get('source'):
                    cell_content = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
                    if self.content in cell_content:
                        content_exists = True
                        break
            
            if not content_exists:
                merged_cells.append({
                    'cell_type': 'markdown',
                    'source': [self.content],
                    'metadata': {}
                })
        
        # 添加code字段内容作为代码单元格
        if self.code and self.code.strip():
            # 检查是否已经包含在jupyter_content中
            code_exists = False
            for cell in merged_cells:
                if cell.get('cell_type') == 'code' and cell.get('source'):
                    cell_content = ''.join(cell['source']) if isinstance(cell['source'], list) else cell['source']
                    if self.code in cell_content:
                        code_exists = True
                        break
            
            if not code_exists:
                merged_cells.append({
                    'cell_type': 'code',
                    'source': [self.code],
                    'metadata': {},
                    'outputs': [],
                    'language': self.language
                })
        
        # 如果没有任何内容，创建一个默认的Markdown单元格
        if not merged_cells:
            merged_cells.append({
                'cell_type': 'markdown',
                'source': [f"# {self.title}\n\n{self.description}"],
                'metadata': {}
            })
        
        # 创建完整的Jupyter Notebook格式
        merged_jupyter = {
            'cells': merged_cells,
            'metadata': {
                'kernelspec': {
                    'display_name': self.language.capitalize() if self.language else 'Python',
                    'language': self.language if self.language else 'python',
                    'name': self.language if self.language else 'python'
                },
                'language_info': {
                    'name': self.language if self.language else 'python',
                    'version': '3.9.0'
                }
            },
            'nbformat': 4,
            'nbformat_minor': 4
        }
        
        # 保存合并内容
        self.merged_content = json.dumps(merged_jupyter)
        
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = '章节'
        verbose_name_plural = '章节'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.book.title} - {self.title}"


class ChapterVersion(models.Model):
    """章节版本信息"""
    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name='原始章节'
    )
    version_number = models.IntegerField(verbose_name='版本号')
    title = models.CharField(max_length=200, verbose_name='标题')
    description = models.TextField(verbose_name='描述')
    content = models.TextField(blank=True, null=True, verbose_name='章节内容')
    code = models.TextField(blank=True, null=True, verbose_name='示例代码')
    jupyter_content = models.TextField(blank=True, null=True, verbose_name='Jupyter文档内容')
    merged_content = models.TextField(blank=True, null=True, verbose_name='合并内容')
    language = models.CharField(max_length=50, default='python', verbose_name='编程语言')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    created_by = models.ForeignKey(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='版本创建人'
    )
    comment = models.TextField(blank=True, verbose_name='版本说明')

    class Meta:
        verbose_name = '章节版本'
        verbose_name_plural = '章节版本'
        ordering = ['chapter_id', '-version_number']

    def __str__(self):
        return f"{self.chapter.title} - v{self.version_number}"


# 信号处理函数：自动更新书籍的章节数
@receiver([post_save, post_delete], sender=Chapter)
def update_book_chapter_count(sender, instance, **kwargs):
    """
    当章节被保存或删除时，自动更新所属书籍的章节数
    只计算非练习类型的章节（reading、video）
    """
    # 获取章节所属的书籍
    book = instance.book
    
    # 计算非练习类型的章节数
    book.chapter_count = Chapter.objects.filter(
        book=book, 
        type__in=['reading', 'video']
    ).count()
    
    # 保存书籍实例
    book.save()


class ChapterMedia(models.Model):
    """章节多媒体资源（视频/图片/音频/附件）"""
    MEDIA_TYPES = [
        ('video', '视频'),
        ('image', '图片'),
        ('audio', '音频'),
        ('attachment', '附件'),
    ]

    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='media',
        verbose_name='所属章节'
    )
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPES, verbose_name='资源类型')
    url = models.URLField(blank=True, null=True, verbose_name='资源URL')
    file = models.FileField(
        upload_to='chapter_media/%Y/%m/',
        blank=True,
        null=True,
        verbose_name='资源文件'
    )
    title = models.CharField(max_length=200, blank=True, verbose_name='标题')
    description = models.TextField(blank=True, verbose_name='描述')
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = '章节多媒体资源'
        verbose_name_plural = '章节多媒体资源'
        ordering = ['chapter_id', 'order']

    def __str__(self):
        return f"{self.chapter.title} - {self.title or self.get_media_type_display()}"


class BookReview(models.Model):
    """教材审核记录（用于教材提供者端审核流程）"""
    REVIEW_STATUS = [
        ('pending', '待审核'),
        ('approved', '通过'),
        ('rejected', '驳回'),
    ]

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='教材'
    )
    reviewer = models.ForeignKey(
        getattr(settings, 'AUTH_USER_MODEL', 'auth.User'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='book_reviews',
        verbose_name='审核人'
    )
    status = models.CharField(max_length=20, choices=REVIEW_STATUS, verbose_name='审核结果')
    comment = models.TextField(blank=True, verbose_name='审核意见')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='审核时间')

    class Meta:
        verbose_name = '教材审核记录'
        verbose_name_plural = '教材审核记录'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.book.title} - {self.get_status_display()}"


class Practice(models.Model):
    """练习题模型"""
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='practices', verbose_name='所属章节')
    
    title = models.CharField(max_length=255, verbose_name='练习题集名称')
    description = models.TextField(blank=True, null=True, verbose_name='练习题集描述')
    
    questions = models.JSONField(verbose_name='问题列表', default=list, help_text='存储多个问题的JSON数组')
    
    language = models.CharField(max_length=50, default='python', verbose_name='编程语言')
    difficulty = models.IntegerField(default=2, choices=[
        (1, '简单'), (2, '中等'), (3, '困难')
    ], verbose_name='难度')
    
    order = models.IntegerField(default=0, verbose_name='排序')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '练习题'
        verbose_name_plural = '练习题'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.chapter.title} - {self.title}"


class PracticeChoiceOption(models.Model):
    """选择题选项模型"""
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE, related_name='choice_options', verbose_name='所属练习题')
    content = models.TextField(verbose_name='选项内容')
    is_correct = models.BooleanField(default=False, verbose_name='是否正确答案')
    order = models.IntegerField(default=0, verbose_name='选项顺序')
    
    class Meta:
        verbose_name = '选择题选项'
        verbose_name_plural = '选择题选项'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.practice.title} - 选项 {self.order + 1}"


class PracticeFillBlank(models.Model):
    """填空题空位模型"""
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE, related_name='fill_blanks', verbose_name='所属练习题')
    prompt = models.CharField(max_length=255, verbose_name='提示文本')
    placeholder = models.CharField(max_length=100, blank=True, null=True, verbose_name='占位符')
    correct_answer = models.CharField(max_length=255, verbose_name='正确答案')
    order = models.IntegerField(default=0, verbose_name='空位顺序')
    
    class Meta:
        verbose_name = '填空题空位'
        verbose_name_plural = '填空题空位'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.practice.title} - 空位 {self.order + 1}"


class TestCase(models.Model):
    """测试用例模型"""
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE, related_name='test_cases', verbose_name='所属练习')
    input_data = models.JSONField(verbose_name='输入数据')
    expected_output = models.JSONField(verbose_name='期望输出')
    order = models.IntegerField(default=0, verbose_name='测试用例顺序')
    
    class Meta:
        verbose_name = '测试用例'
        verbose_name_plural = '测试用例'
        ordering = ['order']
    
    def __str__(self):
        return f"{self.practice.title} - 测试用例 {self.order + 1}"
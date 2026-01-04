"""书籍相关模型定义"""
from django.db import models
from django.conf import settings
import json
import os
import logging

logger = logging.getLogger(__name__)

# 导入Jupyter Notebook相关模型
from .jupyter_models import JupyterNotebook, JupyterCell, JupyterOutput


class Book(models.Model):
    """教材书籍模型"""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, verbose_name='书名')
    author = models.CharField(max_length=100, verbose_name='作者')
    cover = models.ImageField(upload_to='book_covers/', null=True, blank=True, verbose_name='封面')
    pdf_file = models.FileField(upload_to='book_pdfs/', null=True, blank=True, verbose_name='PDF文件')
    description = models.TextField(verbose_name='描述')
    tags = models.TextField(blank=True, default='[]', verbose_name='标签')
    owner = models.ForeignKey(getattr(settings, 'AUTH_USER_MODEL', 'auth.User'), on_delete=models.SET_NULL, null=True, blank=True, related_name='uploaded_books', verbose_name='上传者')
    
    @property
    def tag_list(self):
        """获取标签列表"""
        try:
            return json.loads(self.tags) if self.tags else []
        except json.JSONDecodeError:
            return []
    
    @tag_list.setter
    def tag_list(self, value):
        """设置标签列表"""
        self.tags = json.dumps(value) if isinstance(value, list) else '[]'
    chapter_count = models.IntegerField(default=0, verbose_name='章节数')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '教材'
        verbose_name_plural = '教材'
    
    def __str__(self):
        return self.title
    
    def delete(self, *args, **kwargs):
        """删除书籍时同时删除相关的PDF文件"""
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
            # 已经有主键的情况，直接计算章节数
            self.chapter_count = self.chapters.count()
        else:
            # 新建记录时，章节数默认为0
            self.chapter_count = 0
        
        # 保存实例
        super().save(*args, **kwargs)


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


class Practice(models.Model):
    """练习题模型"""
    chapter = models.OneToOneField(Chapter, on_delete=models.CASCADE, related_name='practice', verbose_name='所属章节')
    question = models.TextField(verbose_name='问题描述')
    code_template = models.TextField(blank=True, null=True, verbose_name='代码模板')
    
    class Meta:
        verbose_name = '练习题'
        verbose_name_plural = '练习题'
    
    def __str__(self):
        return f"{self.chapter.title} - 练习题"


class TestCase(models.Model):
    """测试用例模型"""
    practice = models.ForeignKey(Practice, on_delete=models.CASCADE, related_name='test_cases', verbose_name='所属练习')
    input_data = models.JSONField(verbose_name='输入数据')
    expected_output = models.JSONField(verbose_name='期望输出')
    
    class Meta:
        verbose_name = '测试用例'
        verbose_name_plural = '测试用例'
    
    def __str__(self):
        return f"{self.practice} - 测试用例"
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自定义管理命令：导入docx文件到系统中
"""

import os
import sys
import tempfile
import json
import re
from django.core.management.base import BaseCommand
from django.conf import settings

# 导入docx处理器
from apps.books.docx_processor import process_docx
from apps.books.models import Book, Chapter

class Command(BaseCommand):
    """导入docx文件到系统"""
    
    help = '导入docx文件到系统中'
    
    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='docx文件路径')
        parser.add_argument('--title', type=str, default='导入的教材', help='教材标题')
        parser.add_argument('--description', type=str, default='', help='教材描述')
        parser.add_argument('--author', type=str, default='系统导入', help='作者')
        
    def handle(self, *args, **options):
        file_path = options['file_path']
        title = options['title']
        description = options['description']
        author = options['author']
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"文件不存在: {file_path}"))
            return
        
        self.stdout.write(f"开始导入文件: {file_path}")
        
        try:
            # 创建临时目录用于保存图片
            with tempfile.TemporaryDirectory() as image_temp_dir:
                # 处理docx文件
                docx_result = process_docx(file_path, image_output_dir=image_temp_dir)
                
                self.stdout.write(f"\n处理结果摘要:")
                self.stdout.write(f"提取的章节数: {len(docx_result['chapters'])}")
                self.stdout.write(f"提取的图片数: {len(docx_result['images'])}")
                
                # 创建教材
                book = Book.objects.create(
                    title=title,
                    description=description,
                    author=author,
                    chapter_count=len(docx_result['chapters']),
                    total_chapters=len(docx_result['chapters']),
                    status='published'
                )
                
                self.stdout.write(f"\n创建教材成功: {book.title} (ID: {book.id})")
                
                # 处理图片
                if docx_result['images']:
                    import shutil
                    import uuid
                    
                    # 创建图片ID到新路径的映射
                    image_mapping = {}
                    
                    for image_info in docx_result['images']:
                        # 生成唯一文件名
                        unique_filename = f"{uuid.uuid4()}_{image_info['filename']}"
                        image_path = os.path.join('book_images', str(book.id), unique_filename)
                        
                        # 创建目标目录
                        media_image_dir = os.path.join(settings.MEDIA_ROOT, 'book_images', str(book.id))
                        if not os.path.exists(media_image_dir):
                            os.makedirs(media_image_dir)
                        
                        # 复制图片到media目录
                        source_path = image_info['path']
                        dest_path = os.path.join(media_image_dir, unique_filename)
                        shutil.copy2(source_path, dest_path)
                        
                        # 获取图片的完整URL路径
                        image_url = os.path.join(settings.MEDIA_URL, image_path)
                        
                        # 保存映射关系
                        image_mapping[image_info['filename']] = image_url
                    
                    self.stdout.write(f"\n处理图片成功: {len(docx_result['images'])}张图片")
                
                # 创建章节
                for i, chapter in enumerate(docx_result['chapters']):
                    # 检查内容中是否包含代码块
                    import re
                    content = chapter['content']
                    code_blocks = re.findall(r'```python.*?```', content, re.DOTALL)
                    
                    # 创建章节对象
                    chapter_obj = Chapter.objects.create(
                        book=book,
                        title=chapter['title'],
                        content=content,
                        order=i + 1
                    )
                    
                    # 如果有代码块，转换为Jupyter格式
                    if code_blocks:
                        from apps.books.content_converter import ContentConverter
                        converter = ContentConverter()
                        
                        # 将Markdown内容转换为Jupyter格式
                        jupyter_data = converter.markdown_to_jupyter(content)
                        
                        # 更新章节的Jupyter相关字段
                        chapter_obj.jupyter_content = json.dumps(jupyter_data)
                        chapter_obj.content_type = 'jupyter'
                        chapter_obj.save()
                    
                    # 更新章节内容中的图片引用
                    if 'image_mapping' in locals() and 'image_markers' in chapter:
                        content = chapter_obj.content
                        
                        # 为每个图片标记分配一个图片URL
                        markers = chapter['image_markers']
                        for j, marker in enumerate(markers):
                            if j < len(docx_result['images']):
                                # 找到对应的图片信息
                                image_info = docx_result['images'][j]
                                # 获取图片的新URL
                                new_url = None
                                for filename, url in image_mapping.items():
                                    if image_info['filename'] in filename:
                                        new_url = url
                                        break
                                
                                if new_url:
                                    # 替换图片标记
                                    marker_ref = f"[{marker}]"
                                    new_ref = f"![图片]({new_url})"
                                    content = content.replace(marker_ref, new_ref)
                        
                        # 如果还有剩余的图片没有对应的标记，添加到章节末尾
                        if len(docx_result['images']) > len(markers):
                            content += "\n\n## 本章图片\n"
                            for j in range(len(markers), len(docx_result['images'])):
                                image_info = docx_result['images'][j]
                                for filename, url in image_mapping.items():
                                    if image_info['filename'] in filename:
                                        new_url = url
                                        content += f"![图片 {j+1}]({new_url})\n"
                                        break
                        
                        chapter_obj.content = content
                        chapter_obj.save()
                    
                    self.stdout.write(f"\n创建章节成功: {chapter['title']} (ID: {chapter_obj.id})")
                
                # 更新教材章节数
                book.chapter_count = len(docx_result['chapters'])
                book.save()
                
                self.stdout.write(f"\n{self.style.SUCCESS('导入成功！')}")
                self.stdout.write(f"教材ID: {book.id}")
                self.stdout.write(f"教材标题: {book.title}")
                self.stdout.write(f"导入章节数: {book.chapter_count}")
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"导入失败: {str(e)}"))
            import traceback
            traceback.print_exc()

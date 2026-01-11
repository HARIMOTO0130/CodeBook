#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复所有章节的jupyter_content字段，确保它们包含有效的JSON格式数据
"""
from django.core.management.base import BaseCommand
from apps.books.models import Chapter
import json
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '修复所有章节的jupyter_content字段，确保它们包含有效的JSON格式数据'
    
    def handle(self, *args, **options):
        self.stdout.write('开始修复章节的jupyter_content字段...')
        
        # 获取所有章节
        chapters = Chapter.objects.all()
        total_chapters = chapters.count()
        self.stdout.write(f'找到 {total_chapters} 个章节')
        
        fixed_count = 0
        error_count = 0
        
        for chapter in chapters:
            try:
                # 检查jupyter_content字段
                if chapter.jupyter_content:
                    # 尝试解析为JSON
                    if isinstance(chapter.jupyter_content, str):
                        try:
                            # 尝试解析字符串为JSON
                            parsed = json.loads(chapter.jupyter_content)
                            # 如果解析成功，确保是字典格式
                            if not isinstance(parsed, dict):
                                # 如果不是字典，设置为默认格式
                                chapter.jupyter_content = {}
                                fixed_count += 1
                                self.stdout.write(f'  修复章节 {chapter.id}: {chapter.title} - 转换为默认JSON格式')
                        except json.JSONDecodeError:
                            # 解析失败，设置为空字典
                            chapter.jupyter_content = {}
                            fixed_count += 1
                            self.stdout.write(f'  修复章节 {chapter.id}: {chapter.title} - 修复无效JSON')
                    elif not isinstance(chapter.jupyter_content, dict):
                        # 如果不是字符串也不是字典，设置为空字典
                        chapter.jupyter_content = {}
                        fixed_count += 1
                        self.stdout.write(f'  修复章节 {chapter.id}: {chapter.title} - 转换为默认JSON格式')
                else:
                    # 如果字段为空，设置为空字典
                    chapter.jupyter_content = {}
                    fixed_count += 1
                    self.stdout.write(f'  修复章节 {chapter.id}: {chapter.title} - 设置默认空JSON对象')
                
                # 保存修复后的章节
                chapter.save()
                
            except Exception as e:
                error_count += 1
                self.stderr.write(f'  处理章节 {chapter.id}: {chapter.title} 时出错: {str(e)}')
        
        self.stdout.write(self.style.SUCCESS(f'修复完成!'))
        self.stdout.write(f'- 总共处理: {total_chapters} 章节')
        self.stdout.write(f'- 成功修复: {fixed_count} 章节')
        self.stdout.write(f'- 处理错误: {error_count} 章节')
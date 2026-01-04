#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修复所有章节的content字段，确保它们包含有效的JSON格式数据
"""
from django.core.management.base import BaseCommand
from apps.books.models import Chapter
import json
import logging
import re

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = '修复所有章节的content字段，确保它们包含有效的JSON格式数据'
    
    def handle(self, *args, **options):
        self.stdout.write('开始修复章节的content字段...')
        
        # 获取所有章节
        chapters = Chapter.objects.all()
        total_chapters = chapters.count()
        self.stdout.write(f'找到 {total_chapters} 个章节')
        
        fixed_count = 0
        error_count = 0
        
        for chapter in chapters:
            try:
                # 只处理content_type为'jupyter'的章节或有潜在JSON内容的章节
                if chapter.content_type == 'jupyter' or (chapter.content and self._looks_like_json(chapter.content)):
                    if chapter.content:
                        # 尝试清理和修复content字段
                        cleaned_content = self._clean_json_content(chapter.content)
                        
                        if cleaned_content != chapter.content:
                            chapter.content = cleaned_content
                            fixed_count += 1
                            self.stdout.write(f'  修复章节 {chapter.id}: {chapter.title} - 清理content字段')
                    
                    # 确保content_type正确设置
                    if chapter.content_type not in ['markdown', 'jupyter']:
                        chapter.content_type = 'markdown'
                        self.stdout.write(f'  修复章节 {chapter.id}: {chapter.title} - 重置content_type')
                
                # 保存修复后的章节
                chapter.save()
                
            except Exception as e:
                error_count += 1
                self.stderr.write(f'  处理章节 {chapter.id}: {chapter.title} 时出错: {str(e)}')
        
        self.stdout.write(self.style.SUCCESS(f'修复完成!'))
        self.stdout.write(f'- 总共处理: {total_chapters} 章节')
        self.stdout.write(f'- 成功修复: {fixed_count} 章节')
        self.stdout.write(f'- 处理错误: {error_count} 章节')
    
    def _looks_like_json(self, content):
        """检查字符串是否可能是JSON格式"""
        if not content or not isinstance(content, str):
            return False
        
        # 简单检查是否以{或[开头和以}或]结尾
        content = content.strip()
        return (content.startswith('{') and content.endswith('}')) or \
               (content.startswith('[') and content.endswith(']'))
    
    def _clean_json_content(self, content):
        """清理JSON内容中的常见问题"""
        if not content or not isinstance(content, str):
            return content
        
        # 移除多余的空白字符
        content = content.strip()
        
        try:
            # 尝试直接解析
            parsed = json.loads(content)
            # 如果解析成功，返回格式化后的JSON
            return json.dumps(parsed, ensure_ascii=False)
        except json.JSONDecodeError:
            # 尝试修复一些常见问题
            # 1. 移除可能的HTML标签
            content = re.sub(r'<[^>]+>', '', content)
            
            # 2. 修复不规范的引号（只保留双引号）
            # 注意：这是一个简单的修复，可能不适合所有情况
            content = re.sub(r"'(.*?)'", '"\\1"', content)
            
            # 3. 移除尾部多余的逗号
            content = re.sub(r',\s*([}\]])', '\1', content)
            
            # 4. 尝试再次解析
            try:
                parsed = json.loads(content)
                return json.dumps(parsed, ensure_ascii=False)
            except json.JSONDecodeError:
                # 如果仍然解析失败，返回一个安全的空JSON对象
                return '{}'
        
        return content
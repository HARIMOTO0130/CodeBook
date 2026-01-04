#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
从JSON文件导入书籍数据到数据库
"""

import os
import json
import django
from django.core.management import execute_from_command_line

# 导入书籍数据的JSON文件路径
JSON_FILE_PATH = 'simple_books_data.json'

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.books.models import Book, Chapter

def import_books_from_json(json_file_path):
    """
    从JSON文件导入书籍数据到数据库
    """
    try:
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        books_data = data.get('books', [])
        
        if not books_data:
            print("没有找到书籍数据")
            return
        
        imported_count = 0
        skipped_count = 0
        
        for book_data in books_data:
            # 检查书籍是否已存在
            title = book_data.get('title')
            author = book_data.get('author')
            
            if not title:
                print("跳过没有标题的书籍")
                skipped_count += 1
                continue
            
            # 查找或创建书籍
            book, created = Book.objects.get_or_create(
                title=title,
                defaults={
                    'author': author,
                    'description': book_data.get('description', ''),
                    'tags': book_data.get('tags', []),
                }
            )
            
            if created:
                print(f"创建书籍: {title} - {author}")
                
                # 导入章节
                chapters_data = book_data.get('chapters', [])
                for i, chapter_data in enumerate(chapters_data):
                    chapter = Chapter.objects.create(
                        book=book,
                        title=chapter_data.get('title', f'第{i+1}章'),
                        type=chapter_data.get('type', 'reading'),
                        duration=chapter_data.get('duration', 45),
                        description=chapter_data.get('description', ''),
                        content=chapter_data.get('content', ''),
                        code=chapter_data.get('code', ''),
                        language=chapter_data.get('language', ''),
                        order=i+1
                    )
                    print(f"  创建章节: {chapter.title}")
                
                imported_count += 1
            else:
                print(f"跳过已存在的书籍: {title}")
                skipped_count += 1
        
        print(f"\n导入完成！")
        print(f"成功导入: {imported_count} 本书")
        print(f"跳过: {skipped_count} 本书")
        
    except FileNotFoundError:
        print(f"错误: 找不到文件 {json_file_path}")
    except json.JSONDecodeError:
        print(f"错误: JSON文件格式不正确")
    except Exception as e:
        print(f"导入过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # 确保数据库迁移已应用
    execute_from_command_line(["manage.py", "migrate"])
    
    # 导入书籍数据
    json_file_path = "simple_books_data.json"
    import_books_from_json(json_file_path)
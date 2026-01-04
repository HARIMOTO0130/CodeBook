#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新所有书籍的章节数脚本
"""

import os
import sys

# 添加Django项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django环境变量
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# 导入Django并初始化
import django
django.setup()

# 导入模型
from apps.books.models import Book

def update_all_books_chapter_count():
    """更新所有书籍的章节数"""
    print("开始更新所有书籍的章节数...")
    
    # 获取所有书籍
    books = Book.objects.all()
    total_books = books.count()
    updated_count = 0
    
    print(f"找到 {total_books} 本书籍")
    
    for book in books:
        # 计算章节数
        actual_chapter_count = book.chapters.count()
        
        # 如果章节数有变化，更新书籍
        if book.chapter_count != actual_chapter_count:
            old_count = book.chapter_count
            book.chapter_count = actual_chapter_count
            book.save(update_fields=['chapter_count'])
            updated_count += 1
            print(f"更新书籍: {book.title} - 章节数从 {old_count} 更新为 {actual_chapter_count}")
        else:
            print(f"书籍: {book.title} - 章节数已是最新 ({actual_chapter_count})")
    
    print(f"更新完成！总共更新了 {updated_count} 本书籍的章节数")

if __name__ == "__main__":
    try:
        update_all_books_chapter_count()
    except Exception as e:
        print(f"更新失败: {str(e)}")
        sys.exit(1)
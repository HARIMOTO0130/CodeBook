#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库中章节的类型分布
"""

import os
import sys

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.books.models import Book, Chapter

def check_chapter_types():
    """
    检查数据库中章节的类型分布
    """
    print("=== 检查数据库中章节的类型分布 ===")
    
    # 获取所有书籍
    books = Book.objects.all()
    print(f"\n总共有 {books.count()} 本书籍")
    
    for book in books:
        print(f"\n=== 书籍: {book.title} (ID: {book.id}) ===")
        
        # 获取该书籍的所有章节
        chapters = book.chapters.all()
        print(f"总共有 {chapters.count()} 个章节")
        
        # 检查章节类型分布
        chapter_types = chapters.values('type').annotate(count=Count('type')).order_by('-count')
        print("章节类型分布:")
        for chapter_type in chapter_types:
            print(f"  - {chapter_type['type']}: {chapter_type['count']} 个")
        
        # 列出所有章节的详细信息
        print("\n所有章节详细信息:")
        for chapter in chapters:
            print(f"  - 章节: {chapter.title} (ID: {chapter.id}), 类型: {chapter.type}, 顺序: {chapter.order}")

if __name__ == "__main__":
    from django.db.models import Count
    check_chapter_types()

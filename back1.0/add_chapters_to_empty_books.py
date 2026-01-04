#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为没有章节的书籍添加基础章节内容
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()
from apps.books.models import Book, Chapter

def add_basic_chapters_to_empty_books():
    """为没有章节的书籍添加基础章节"""
    print("=== 为没有章节的书籍添加基础章节 ===")
    
    # 获取所有没有章节的书籍
    books_without_chapters = []
    for book in Book.objects.all():
        if book.chapters.count() == 0:
            books_without_chapters.append(book)
    
    print(f"发现 {len(books_without_chapters)} 本书籍没有章节")
    
    # 为每本书添加3个基础章节
    added_chapters_count = 0
    
    for book in books_without_chapters:
        print(f"\n为书籍 '{book.title}' 添加章节...")
        
        # 根据书籍标题生成章节内容
        book_type = book.title.split(' ')[0] if ' ' in book.title else book.title
        
        # 章节模板
        chapters_template = [
            {
                'title': f'第1章：{book_type}概述',
                'content': f'本章介绍{book.title}的基础知识和学习路径。\n\n**学习目标：**\n- 了解{book_type}的基本概念\n- 掌握{book_type}的应用场景\n- 熟悉{book_type}的发展历程\n\n{book_type}是一个广泛应用的领域，具有重要的理论和实践意义。通过本章学习，您将对{book_type}有一个初步的认识。',
                'order': 1,
                'type': 'text',
                'duration': 30
            },
            {
                'title': f'第2章：{book_type}核心原理',
                'content': f'本章详细讲解{book_type}的核心原理和关键技术。\n\n**主要内容：**\n- {book_type}的基本原理\n- 关键技术点分析\n- 实际应用案例\n\n理解这些核心原理对于掌握{book_type}至关重要，也是后续学习的基础。',
                'order': 2,
                'type': 'text',
                'duration': 45
            },
            {
                'title': f'第3章：{book_type}实践与应用',
                'content': f'本章通过实际案例展示{book_type}的应用方法。\n\n**实践内容：**\n- 项目设置与配置\n- 核心功能实现\n- 常见问题解决\n\n通过本章的实践练习，您将能够独立应用{book_type}解决实际问题。',
                'order': 3,
                'type': 'text',
                'duration': 60
            }
        ]
        
        # 创建章节
        for chapter_data in chapters_template:
            chapter = Chapter.objects.create(
                book=book,
                title=chapter_data['title'],
                content=chapter_data['content'],
                order=chapter_data['order'],
                type=chapter_data['type'],
                duration=chapter_data['duration'],
                description=f'{chapter_data["title"]} - {chapter_data["content"].split("\n\n")[0]}'
            )
            print(f"  - 添加章节: {chapter.title}")
            added_chapters_count += 1
    
    # 修复空内容章节
    print("\n=== 修复空内容章节 ===")
    empty_content_chapters = Chapter.objects.filter(content__isnull=True) | Chapter.objects.filter(content='')
    
    for chapter in empty_content_chapters:
        print(f"修复章节: {chapter.book.title} - {chapter.title}")
        # 设置默认内容
        chapter.content = f"这是{chapter.book.title}中{chapter.title}的内容。\n\n本章详细讲解相关知识点和实践方法，帮助您深入理解和掌握相关技能。"
        chapter.description = f"{chapter.title} - 详细内容讲解"
        chapter.save()
        print(f"  - 已更新章节内容")
    
    print(f"\n=== 完成 ===")
    print(f"成功添加 {added_chapters_count} 个章节到 {len(books_without_chapters)} 本书籍")
    print(f"修复了 {empty_content_chapters.count()} 个空内容章节")

if __name__ == "__main__":
    add_basic_chapters_to_empty_books()
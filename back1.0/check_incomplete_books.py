#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库中所有书籍的章节完整性
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django设置模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()
from apps.books.models import Book, Chapter

def check_books_completeness():
    """检查所有书籍的章节完整性"""
    print("=== 检查书籍章节完整性 ===")
    print(f"总书籍数量: {Book.objects.count()}")
    print()
    
    # 找出没有章节的书籍
    books_without_chapters = []
    books_with_chapters = []
    
    for book in Book.objects.all():
        chapter_count = book.chapters.count()
        
        if chapter_count == 0:
            books_without_chapters.append(book)
        else:
            books_with_chapters.append((book, chapter_count))
    
    # 打印没有章节的书籍
    if books_without_chapters:
        print("\n1. 没有章节的书籍:")
        print("-" * 80)
        for book in books_without_chapters:
            print(f"ID: {book.id}, 标题: {book.title}, 作者: {book.author}")
    else:
        print("\n1. 没有发现没有章节的书籍")
    
    # 打印有章节的书籍及其章节数
    print(f"\n2. 有章节的书籍 ({len(books_with_chapters)}本):")
    print("-" * 80)
    for book, chapter_count in books_with_chapters:
        print(f"ID: {book.id}, 标题: {book.title}, 章节数: {chapter_count}")
    
    # 检查章节内容是否完整
    print("\n3. 检查章节内容完整性:")
    print("-" * 80)
    chapters_with_missing_content = []
    
    for chapter in Chapter.objects.all():
        # 检查章节内容是否为空
        if not chapter.content or len(chapter.content.strip()) == 0:
            chapters_with_missing_content.append(chapter)
    
    if chapters_with_missing_content:
        print(f"发现 {len(chapters_with_missing_content)} 个章节内容为空:")
        for chapter in chapters_with_missing_content:
            print(f"书籍: {chapter.book.title}, 章节: {chapter.title} (ID: {chapter.id})")
    else:
        print("所有章节都包含内容")

if __name__ == "__main__":
    check_books_completeness()
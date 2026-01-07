#!/usr/bin/env python
"""
重新计算所有书籍的章节数脚本
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 导入Django
import django
django.setup()

# 导入模型
from apps.books.models import Book, Chapter

def update_all_chapter_counts():
    """重新计算所有书籍的章节数"""
    print("开始重新计算所有书籍的章节数...")
    
    # 获取所有书籍
    books = Book.objects.all()
    
    updated_count = 0
    
    for book in books:
        # 计算非练习类型的章节数
        chapter_count = Chapter.objects.filter(
            book=book, 
            type__in=['reading', 'video']
        ).count()
        
        # 如果章节数有变化，更新书籍
        if book.chapter_count != chapter_count:
            book.chapter_count = chapter_count
            book.save()
            updated_count += 1
            print(f"更新了书籍 {book.title} 的章节数: {chapter_count}")
        else:
            print(f"书籍 {book.title} 的章节数已经正确: {chapter_count}")
    
    print(f"\n章节数更新完成！共更新了 {updated_count} 本书籍")

if __name__ == "__main__":
    update_all_chapter_counts()

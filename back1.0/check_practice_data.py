#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库中练习题数据的存储情况
"""

import os
import sys
import django
import json

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.books.models import Book, Chapter, Practice

def check_practice_data():
    """
    检查数据库中练习题数据的存储情况
    """
    print("=== 检查数据库中练习题数据 ===")
    
    # 获取所有书籍
    books = Book.objects.all()
    print(f"\n总共有 {books.count()} 本书籍")
    
    for book in books:
        print(f"\n=== 书籍: {book.title} (ID: {book.id}) ===")
        
        # 获取该书籍的所有章节
        chapters = book.chapters.all()
        print(f"总共有 {chapters.count()} 个章节")
        
        # 检查练习章节
        practice_chapters = chapters.filter(type='practice')
        print(f"练习章节数量: {practice_chapters.count()}")
        
        if practice_chapters.count() == 0:
            print("该书籍没有练习章节")
            continue
        
        for practice_chapter in practice_chapters:
            print(f"\n--- 练习章节: {practice_chapter.title} (ID: {practice_chapter.id}) ---")
            
            # 检查该章节的练习题
            practices = practice_chapter.practices.all()
            print(f"练习题集数量: {practices.count()}")
            
            if practices.count() == 0:
                print("该练习章节没有练习题")
                continue
            
            for practice in practices:
                print(f"\n练习题集: {practice.title} (ID: {practice.id})")
                print(f"问题数量: {len(practice.questions)}")
                
                # 检查每个问题的完整性
                if len(practice.questions) > 0:
                    print("问题列表:")
                    for i, question in enumerate(practice.questions, 1):
                        print(f"  问题 {i}:")
                        print(f"    类型: {question.get('type', '未知')}")
                        print(f"    题干: {question.get('question', '无')}")
                        
                        # 检查判断题是否有选项
                        if question.get('type') in ['judgment', 'Judgment']:
                            options = question.get('options', [])
                            if len(options) > 0:
                                print(f"    选项: {json.dumps(options, ensure_ascii=False)}")
                            else:
                                print(f"    选项: 无")
                        
                        # 检查填空题是否有空位
                        if question.get('type') in ['fill', 'Fill']:
                            blanks = question.get('blanks', [])
                            if len(blanks) > 0:
                                print(f"    空位数量: {len(blanks)}")
                            else:
                                print(f"    空位: 无")
                else:
                    print("问题列表为空")

if __name__ == "__main__":
    check_practice_data()

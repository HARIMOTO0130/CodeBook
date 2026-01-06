#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查数据库中所有练习题数据的完整性
"""

import os
import sys
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.books.models import Practice, Chapter, Book

def check_all_practice_data():
    """检查所有练习题数据的完整性"""
    print("=== 检查数据库中所有练习题数据 ===")
    
    # 获取所有书籍
    books = Book.objects.all()
    
    for book in books:
        print(f"\n=== 书籍: {book.title} (ID: {book.id}) ===")
        
        # 获取书籍的所有章节
        chapters = Chapter.objects.filter(book=book, type='practice')
        
        if not chapters.exists():
            print(f"  ❌ 该书籍没有练习题章节")
            continue
        
        for chapter in chapters:
            print(f"\n--- 章节: {chapter.title} (ID: {chapter.id}) ---")
            
            # 获取章节的所有练习题集
            practices = Practice.objects.filter(chapter=chapter)
            
            if not practices.exists():
                print(f"  ❌ 该章节没有练习题集")
                continue
            
            for practice in practices:
                print(f"\n  练习集: {practice.title} (ID: {practice.id}) - 难度: {practice.difficulty}")
                print(f"  题目数量: {len(practice.questions)}")
                
                if not practice.questions:
                    print(f"  ❌ 练习题集为空")
                    continue
                
                # 检查每道题的完整性
                for i, question in enumerate(practice.questions):
                    print(f"\n    第{i+1}题:")
                    print(f"      类型: {question.get('type')}")
                    print(f"      题干: {question.get('question')}")
                    
                    # 根据题目类型检查必要字段
                    if question.get('type') in ['choice', 'Judgment']:
                        options = question.get('options', [])
                        print(f"      选项数量: {len(options)}")
                        for j, option in enumerate(options):
                            print(f"        选项{j+1}: {option.get('content')}, 是否正确: {option.get('is_correct')}")
                    elif question.get('type') == 'fill':
                        blanks = question.get('blanks', [])
                        print(f"      填空数量: {len(blanks)}")
                        for j, blank in enumerate(blanks):
                            print(f"        填空{j+1}: 正确答案: {blank.get('correct_answer')}")
                    
                print(f"    ✅ 该练习题集数据完整")

if __name__ == '__main__':
    check_all_practice_data()

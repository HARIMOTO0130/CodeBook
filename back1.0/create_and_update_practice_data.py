#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为每本书籍的每个阅读章节创建对应的练习章节和练习题集，并更新练习题内容
"""

import os
import sys
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from apps.books.models import Practice, Chapter, Book

# 从update_all_practice_questions.py导入题目生成函数
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from update_all_practice_questions import (
    get_choice_question,
    get_choice_option,
    get_fill_question,
    get_fill_answer,
    get_true_false_question,
    get_true_false_answer,
    get_code_completion_question,
    get_programming_question,
    get_code_template,
    get_test_cases
)

def create_and_update_practice_data():
    """
    为每本书籍的每个阅读章节创建对应的练习章节和练习题集，并更新练习题内容
    """
    print("=== 创建并更新练习题数据 ===")
    
    # 获取所有书籍
    books = Book.objects.all()
    print(f"找到 {books.count()} 本书籍")
    
    for book in books:
        print(f"\n=== 处理书籍: {book.title} (ID: {book.id}) ===")
        
        # 获取该书籍的所有阅读章节
        reading_chapters = book.chapters.filter(type='reading')
        print(f"找到 {reading_chapters.count()} 个阅读章节")
        
        for reading_chapter in reading_chapters:
            print(f"\n--- 处理阅读章节: {reading_chapter.title} (ID: {reading_chapter.id}, 顺序: {reading_chapter.order}) ---")
            
            # 检查是否已经存在对应的练习章节
            practice_chapter_name = f"{reading_chapter.title} - 练习题"
            existing_practice_chapter = book.chapters.filter(
                title=practice_chapter_name,
                type='practice'
            ).first()
            
            if existing_practice_chapter:
                print(f"✓ 练习章节 '{practice_chapter_name}' 已存在 (ID: {existing_practice_chapter.id})")
                practice_chapter = existing_practice_chapter
            else:
                # 创建新的练习章节
                practice_chapter = Chapter(
                    book=book,
                    title=practice_chapter_name,
                    type='practice',
                    duration=60,
                    description=f"{reading_chapter.title}的练习题",
                    content="",
                    language='python',
                    order=reading_chapter.order,
                    level=reading_chapter.level,
                    is_main_chapter=False,
                    parent_chapter=reading_chapter,
                    content_type='markdown'
                )
                practice_chapter.save()
                print(f"✓ 已创建练习章节 '{practice_chapter_name}' (ID: {practice_chapter.id})")
            
            # 检查该练习章节是否已经有练习题集
            practice_title = f"{practice_chapter.title} - 练习题集"
            existing_practice = practice_chapter.practices.filter(title=practice_title).first()
            
            if existing_practice:
                print(f"✓ 练习题集 '{practice_title}' 已存在 (ID: {existing_practice.id})")
                practice = existing_practice
            else:
                # 创建新的练习题集
                practice = Practice(
                    chapter=practice_chapter,
                    title=practice_title,
                    description=f"{practice_chapter.title}的练习题集",
                    questions=[],
                    language='python',
                    difficulty=2,
                    order=1
                )
                practice.save()
                print(f"✓ 已创建练习题集 '{practice_title}' (ID: {practice.id})")
            
            # 更新练习题集的内容
            print("\n正在更新练习题集内容...")
            
            # 使用章节顺序而不是章节ID来匹配题目内容
            chapter_num = reading_chapter.order
            
            try:
                # 生成完整的练习题
                questions = []
                
                # 1. 选择题
                choice_question = {
                    "id": 1,
                    "type": "choice",
                    "title": "选择题",
                    "question": get_choice_question(book, chapter_num),
                    "options": [
                        {"id": 1, "content": get_choice_option(book, chapter_num, 1), "is_correct": False},
                        {"id": 2, "content": get_choice_option(book, chapter_num, 2), "is_correct": True},
                        {"id": 3, "content": get_choice_option(book, chapter_num, 3), "is_correct": False},
                        {"id": 4, "content": get_choice_option(book, chapter_num, 4), "is_correct": False}
                    ],
                    "difficulty": 1,
                    "order": 1
                }
                questions.append(choice_question)
                
                # 2. 填空题
                fill_question = {
                    "id": 2,
                    "type": "fill",
                    "title": "填空题",
                    "question": get_fill_question(book, chapter_num),
                    "blanks": [
                        {"id": 1, "correct_answer": get_fill_answer(book, chapter_num, 1), "placeholder": "第一空"},
                        {"id": 2, "correct_answer": get_fill_answer(book, chapter_num, 2), "placeholder": "第二空"}
                    ],
                    "difficulty": 2,
                    "order": 2
                }
                questions.append(fill_question)
                
                # 3. 判断题 - 注意：这里将type从true_false改为Judgment以匹配前端期望
                true_false_question = {
                    "id": 3,
                    "type": "Judgment",
                    "title": "判断题",
                    "question": get_true_false_question(book, chapter_num),
                    "options": [
                        {"id": 1, "content": "正确", "is_correct": get_true_false_answer(book, chapter_num)},
                        {"id": 2, "content": "错误", "is_correct": not get_true_false_answer(book, chapter_num)}
                    ],
                    "correct_answer": 0 if get_true_false_answer(book, chapter_num) else 1,
                    "difficulty": 1,
                    "order": 3
                }
                questions.append(true_false_question)
                
                # 4. 代码补全题
                code_completion_question = {
                    "id": 4,
                    "type": "code_completion",
                    "title": "代码补全题",
                    "question": get_code_completion_question(book, chapter_num),
                    "code_template": get_code_template(book, chapter_num, "completion"),
                    "test_cases": get_test_cases(book, chapter_num, "completion"),
                    "difficulty": 2,
                    "order": 4
                }
                questions.append(code_completion_question)
                
                # 5. 编程题
                programming_question = {
                    "id": 5,
                    "type": "programming",
                    "title": "编程题",
                    "question": get_programming_question(book, chapter_num),
                    "code_template": get_code_template(book, chapter_num, "programming"),
                    "test_cases": get_test_cases(book, chapter_num, "programming"),
                    "difficulty": 3,
                    "order": 5
                }
                questions.append(programming_question)
                
                # 更新练习题集的questions字段
                practice.questions = questions
                practice.save()
                
                print(f"✅ 已成功更新练习题集 '{practice.title}'，添加了 {len(questions)} 道完整题目")
                
            except Exception as e:
                print(f"❌ 更新练习题集时出错: {str(e)}")
                import traceback
                traceback.print_exc()
    
    print("\n=== 所有练习题数据的创建和更新完成！ ===")

if __name__ == "__main__":
    create_and_update_practice_data()

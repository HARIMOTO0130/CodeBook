import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from apps.books.models import Practice, Chapter, Book

def verify_practice_data():
    """验证练习题数据是否正确插入"""
    
    # 获取所有Practice对象
    practices = Practice.objects.all()
    
    if not practices.exists():
        print("没有找到练习题集")
        return
    
    print(f"找到 {practices.count()} 个练习题集\n")
    
    total_questions = 0
    
    for practice in practices:
        chapter = practice.chapter
        book = chapter.book
        
        questions = practice.questions
        question_count = len(questions)
        total_questions += question_count
        
        print(f"练习题集: {practice.title}")
        print(f"所属书籍: {book.title}, 章节: {chapter.title}")
        print(f"题目数量: {question_count} 道")
        
        # 检查题目类型
        if question_count > 0:
            question_types = set(q['type'] for q in questions)
            print(f"题目类型: {', '.join(question_types)}")
        
        print("-" * 50)
    
    print(f"\n总题目数量: {total_questions} 道")
    print(f"平均每个练习题集: {total_questions / practices.count():.1f} 道题目")
    
    # 检查是否每个练习题集都至少有5道题目
    insufficient_practices = [p for p in practices if len(p.questions) < 5]
    if insufficient_practices:
        print(f"\n警告: 以下 {len(insufficient_practices)} 个练习题集题目数量不足5道:")
        for p in insufficient_practices:
            print(f"- {p.title}: {len(p.questions)} 道题目")
    else:
        print("\n✅ 所有练习题集都至少包含5道题目！")

if __name__ == "__main__":
    verify_practice_data()

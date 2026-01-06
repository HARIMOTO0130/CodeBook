import os
import sys
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.books.models import Practice

def view_practice_structure():
    """查看练习题的数据结构"""
    # 获取第一个练习题集
    practice = Practice.objects.first()
    
    if not practice:
        print("没有找到练习题集")
        return
    
    print(f"练习集ID: {practice.id}")
    print(f"练习集标题: {practice.title}")
    print(f"练习集描述: {practice.description}")
    print(f"所属章节: {practice.chapter.title}")
    print(f"书籍: {practice.chapter.book.title}")
    print(f"\nQuestions字段类型: {type(practice.questions)}")
    print(f"Questions字段内容:")
    
    # 打印完整的questions数据
    if practice.questions:
        print(json.dumps(practice.questions, indent=2, ensure_ascii=False))
        
        # 查看第一题的结构
        first_question = practice.questions[0]
        print(f"\n第一题结构:")
        print(f"键: {list(first_question.keys())}")
    else:
        print("空")

if __name__ == "__main__":
    view_practice_structure()

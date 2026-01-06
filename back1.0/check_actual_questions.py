import os
import sys
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.books.models import Practice

def check_actual_questions():
    """直接查看数据库中练习题的实际内容"""
    # 获取第一个练习题集
    practice = Practice.objects.filter(chapter__book__id=2, chapter__id=4).first()
    
    if practice:
        print(f"练习题集: {practice.title}")
        print(f"实际题目内容:")
        for i, question in enumerate(practice.questions):
            print(f"\n第{i+1}题:")
            print(f"  ID: {question.get('id')}")
            print(f"  类型: {question.get('type')}")
            print(f"  题干: {question.get('question')}")
            
            # 显示选择题选项
            if question.get('type') == 'choice' and 'options' in question:
                print(f"  选项:")
                for option in question['options']:
                    print(f"    {option['id']}. {option['content']} {'(正确)' if option['is_correct'] else ''}")
            
            # 显示判断题答案
            if question.get('type') in ['true_false', 'Judgment'] and 'correct_answer' in question:
                print(f"  正确答案: {question['correct_answer']}")

if __name__ == "__main__":
    check_actual_questions()

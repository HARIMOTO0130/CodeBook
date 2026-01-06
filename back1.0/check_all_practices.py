import os
import sys
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.books.models import Practice, Chapter, Book

def check_all_practices():
    """检查所有练习题集的数据完整性"""
    print("正在检查所有练习题集的数据完整性...")
    
    # 获取所有书籍
    books = Book.objects.all().order_by('id')
    
    for book in books:
        print(f"\n=== 书籍: {book.title} (ID: {book.id}) ===")
        
        # 获取书籍的所有章节
        chapters = Chapter.objects.filter(book=book).order_by('order')
        
        for chapter in chapters:
            print(f"\n--- 章节: {chapter.title} (ID: {chapter.id}) ---")
            
            # 获取章节的所有练习题集
            practices = Practice.objects.filter(chapter=chapter).order_by('order')
            
            if not practices:
                print(f"  该章节没有练习题集")
                continue
            
            for practice in practices:
                print(f"  \n练习集: {practice.title} (ID: {practice.id}) - 难度: {practice.difficulty}")
                
                # 检查questions字段
                if not practice.questions or len(practice.questions) == 0:
                    print(f"    ❌ 练习题集没有任何题目")
                    continue
                
                print(f"    题目数量: {len(practice.questions)}")
                
                # 检查每一道题
                has_issues = False
                for i, question in enumerate(practice.questions):
                    print(f"    \n    第{i+1}题:")
                    print(f"      类型: {question.get('type', '未知')}")
                    print(f"      题干: {question.get('question', '缺失')[:50]}{'...' if len(question.get('question', '')) > 50 else ''}")
                    
                    # 检查是否有基本字段
                    required_fields = ['id', 'type', 'question']
                    for field in required_fields:
                        if field not in question or not question[field]:
                            print(f"      ❌ 缺失必要字段: {field}")
                            has_issues = True
                    
                    # 根据题型检查特定字段
                    q_type = question.get('type', '')
                    
                    if q_type == 'choice':
                        if 'options' not in question or len(question['options']) == 0:
                            print(f"      ❌ 选择题缺少选项")
                            has_issues = True
                        else:
                            # 检查是否有正确选项
                            has_correct = any(option.get('is_correct', False) for option in question['options'])
                            if not has_correct:
                                print(f"      ❌ 选择题没有正确选项")
                                has_issues = True
                    
                    elif q_type in ['true_false', 'Judgment']:
                        if 'correct_answer' not in question:
                            print(f"      ❌ 判断题缺少正确答案")
                            has_issues = True
                    
                    elif q_type == 'fill':
                        if 'blanks' not in question or len(question['blanks']) == 0:
                            print(f"      ❌ 填空题缺少空白设置")
                            has_issues = True
                        else:
                            # 检查每个空白是否有答案
                            for j, blank in enumerate(question['blanks']):
                                if 'correct_answer' not in blank or not blank['correct_answer']:
                                    print(f"      ❌ 填空题第{j+1}个空白缺少答案")
                                    has_issues = True
                    
                    elif q_type in ['code_completion', 'programming']:
                        if 'code_template' not in question or not question['code_template']:
                            print(f"      ❌ 代码题缺少代码模板")
                            has_issues = True
                        if 'test_cases' not in question or len(question['test_cases']) == 0:
                            print(f"      ❌ 代码题缺少测试用例")
                            has_issues = True
                
                if not has_issues:
                    print(f"    ✅ 该练习题集数据完整")
                else:
                    print(f"    ❌ 该练习题集存在数据问题")

if __name__ == "__main__":
    check_all_practices()

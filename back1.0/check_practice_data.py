import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.books.models import Practice, Book, Chapter

def check_practice_data():
    print("正在检查练习题数据...")
    
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
                for i, question in enumerate(practice.questions):
                    print(f"    \n    第{i+1}题:")
                    
                    # 检查题干
                    if 'question' not in question or not question['question']:
                        print(f"      ❌ 题干缺失")
                    else:
                        print(f"      题干: {question['question']}")
                    
                    # 检查类型
                    if 'type' not in question:
                        print(f"      ❌ 题型缺失")
                    else:
                        print(f"      类型: {question['type']}")
                    
                    # 根据题型检查不同字段
                    q_type = question.get('type', '')
                    
                    if q_type == 'choice':
                        # 选择题检查选项
                        if 'options' not in question or not question['options']:
                            print(f"      ❌ 选项缺失")
                        else:
                            print(f"      选项数量: {len(question['options'])}")
                            for j, option in enumerate(question['options']):
                                if 'content' not in option or not option['content']:
                                    print(f"        ❌ 选项{j+1}内容缺失")
                                else:
                                    print(f"        选项{j+1}: {option['content']}")
                    
                    elif q_type == 'fill':
                        # 填空题检查答案
                        if 'answers' not in question or not question['answers']:
                            print(f"      ❌ 答案缺失")
                        else:
                            print(f"      答案数量: {len(question['answers'])}")
                    
                    elif q_type == 'Judgment':
                        # 判断题检查选项
                        if 'options' not in question or not question['options']:
                            print(f"      ❌ 选项缺失")
                        else:
                            print(f"      选项数量: {len(question['options'])}")
                    
                    elif q_type == 'code':
                        # 代码题检查代码内容
                        if 'code' not in question or not question['code']:
                            print(f"      ❌ 代码内容缺失")
                        else:
                            print(f"      代码内容: 存在")
                    
                    elif q_type == 'programming':
                        # 编程题检查题目和测试用例
                        if 'description' not in question or not question['description']:
                            print(f"      ❌ 编程题描述缺失")
                        else:
                            print(f"      描述: {question['description'][:50]}...")
                    
                    # 检查答案是否存在
                    if 'correct_answer' not in question:
                        print(f"      ❌ 正确答案缺失")
                    else:
                        print(f"      正确答案: {question['correct_answer']}")

if __name__ == "__main__":
    check_practice_data()

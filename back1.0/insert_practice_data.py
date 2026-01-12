# -*- coding: utf-8 -*-
"""
为练习题插入示例数据
使用 Django ORM 避免字符编码问题
将选项和空位直接放在 questions 数组中的问题对象里
"""
import os
import sys
import django

# 设置 Django 环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.books.models import Practice, PracticeChoiceOption, PracticeFillBlank, TestCase, Chapter
import json

def create_questions_for_practice(practice_id, chapter_title):
    """为指定练习题创建题目数据"""
    try:
        # 获取练习题
        practice = Practice.objects.get(id=practice_id)
        print(f"\n{'='*60}")
        print(f"处理练习题 ID {practice_id}: {practice.title}")
        print(f"所属章节: {chapter_title}")
        print(f"{'='*60}")
        
        # 1. 创建 questions 数组，将选项和空位直接放在问题对象中
        questions = [
            {
                "id": 1,
                "type": "choice",
                "title": "选择题1",
                "question": f"关于{chapter_title}，以下哪个描述是正确的？",
                "stem": f"关于{chapter_title}，以下哪个描述是正确的？",
                "content": f"关于{chapter_title}，以下哪个描述是正确的？",
                "description": "请选择正确的答案",
                "language": "python",
                "difficulty": 1,
                "order": 1,
                # 将选项直接放在问题对象中
                "options": [
                    {"id": 1, "content": "这是本章的核心概念，涵盖了主要内容", "is_correct": True},
                    {"id": 2, "content": "这是一个错误的描述，与本章内容无关", "is_correct": False},
                    {"id": 3, "content": "这是一个不完整的描述，缺少关键信息", "is_correct": False},
                    {"id": 4, "content": "这是一个过时的描述，已被更新", "is_correct": False}
                ],
                "choice_options": [
                    {"id": 1, "content": "这是本章的核心概念，涵盖了主要内容", "is_correct": True},
                    {"id": 2, "content": "这是一个错误的描述，与本章内容无关", "is_correct": False},
                    {"id": 3, "content": "这是一个不完整的描述，缺少关键信息", "is_correct": False},
                    {"id": 4, "content": "这是一个过时的描述，已被更新", "is_correct": False}
                ]
            },
            {
                "id": 2,
                "type": "true_false",
                "title": "判断题1",
                "question": f"在{chapter_title}中，本章内容是计算机科学的基础知识。",
                "stem": f"在{chapter_title}中，本章内容是计算机科学的基础知识。",
                "content": f"在{chapter_title}中，本章内容是计算机科学的基础知识。",
                "description": "请判断正误",
                "correct_answer": True,
                "language": "python",
                "difficulty": 1,
                "order": 2
            },
            {
                "id": 3,
                "type": "fill_blank",
                "title": "填空题1",
                "question": f"请填写：在{chapter_title}中，____是____的基础。",
                "stem": f"请填写：在{chapter_title}中，____是____的基础。",
                "content": f"请填写：在{chapter_title}中，____是____的基础。",
                "description": "请填写正确答案",
                "language": "python",
                "difficulty": 2,
                "order": 3,
                # 将空位直接放在问题对象中
                "blanks": [
                    {"id": 1, "prompt": "第一个空", "placeholder": "请输入答案", "correct_answer": "数据结构", "correctAnswer": "数据结构"},
                    {"id": 2, "prompt": "第二个空", "placeholder": "请输入答案", "correct_answer": "算法设计", "correctAnswer": "算法设计"}
                ],
                "fill_blanks": [
                    {"id": 1, "prompt": "第一个空", "placeholder": "请输入答案", "correct_answer": "数据结构", "correctAnswer": "数据结构"},
                    {"id": 2, "prompt": "第二个空", "placeholder": "请输入答案", "correct_answer": "算法设计", "correctAnswer": "算法设计"}
                ]
            },
            {
                "id": 4,
                "type": "programming",
                "title": "编程题1",
                "question": f"编写一个Python函数，实现{chapter_title}中提到的功能。",
                "stem": f"编写一个Python函数，实现{chapter_title}中提到的功能。",
                "content": f"编写一个Python函数，实现{chapter_title}中提到的功能。函数名为 calculate，接受两个参数 a 和 b，返回它们的和。",
                "description": "请完成以下编程练习",
                "code_template": "def calculate(a, b):\n    # 在这里编写你的代码\n    return a + b",
                "language": "python",
                "difficulty": 2,
                "order": 4
            }
        ]
        
        practice.questions = questions
        practice.save()
        print(f"✓ 已更新 questions 字段，包含 {len(questions)} 道题目")
        
        # 2. 删除旧的关联数据（如果存在）
        PracticeChoiceOption.objects.filter(practice=practice).delete()
        PracticeFillBlank.objects.filter(practice=practice).delete()
        TestCase.objects.filter(practice=practice).delete()
        print("✓ 已清除旧的关联数据")
        
        # 3. 插入测试用例（用于编程题）
        test_cases = [
            {'input_data': {'a': 2, 'b': 3}, 'expected_output': 5, 'order': 0},
            {'input_data': {'a': 10, 'b': 20}, 'expected_output': 30, 'order': 1},
            {'input_data': {'a': -5, 'b': 5}, 'expected_output': 0, 'order': 2},
        ]
        
        for tc_data in test_cases:
            TestCase.objects.create(
                practice=practice,
                **tc_data
            )
        print(f"✓ 已插入 {len(test_cases)} 个测试用例")
        
        # 验证数据
        print("\n=== 数据验证 ===")
        print(f"练习题 ID: {practice.id}")
        print(f"题目数量: {len(practice.questions)}")
        print(f"测试用例数量: {TestCase.objects.filter(practice=practice).count()}")
        
        # 检查第一道选择题的选项
        if len(practice.questions) > 0 and practice.questions[0].get('options'):
            print(f"第一道选择题选项数量: {len(practice.questions[0]['options'])}")
        
        # 检查第三道填空题的空位
        if len(practice.questions) > 2 and practice.questions[2].get('blanks'):
            print(f"第三道填空题空位数量: {len(practice.questions[2]['blanks'])}")
        
        print("✓ 数据插入成功！")
        return True
        
    except Practice.DoesNotExist:
        print(f"错误：找不到 ID 为 {practice_id} 的练习题")
        return False
    except Exception as e:
        print(f"错误：{str(e)}")
        import traceback
        traceback.print_exc()
        return False

def insert_all_practices():
    """为所有练习题插入数据"""
    # 获取所有有练习题的章节
    chapters = Chapter.objects.filter(practices__isnull=False).distinct()
    
    print(f"\n找到 {chapters.count()} 个有练习题的章节")
    
    # 为每个章节的练习题插入数据
    for chapter in chapters:
        practices = chapter.practices.all()
        for practice in practices:
            create_questions_for_practice(practice.id, chapter.title)
    
    print(f"\n{'='*60}")
    print("所有练习题数据插入完成！")
    print(f"{'='*60}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # 如果提供了练习ID，只为该练习插入数据
        practice_id = int(sys.argv[1])
        practice = Practice.objects.get(id=practice_id)
        create_questions_for_practice(practice_id, practice.chapter.title)
    else:
        # 否则为所有练习题插入数据
        insert_all_practices()


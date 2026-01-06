import os
import sys
import json

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from apps.books.models import Practice

def check_practice_questions():
    """检查所有练习题集的题目完整性"""
    
    # 获取所有Practice对象
    practices = Practice.objects.all()
    
    print(f"总共有 {practices.count()} 个练习题集")
    
    incomplete_practices = []
    
    for practice in practices:
        if not practice.questions:
            print(f"❌ {practice.title}: 没有题目数据")
            incomplete_practices.append(practice)
            continue
            
        print(f"\n✅ {practice.title}: {len(practice.questions)}道题")
        
        for i, question in enumerate(practice.questions, 1):
            question_type = question.get('type', '未知类型')
            question_text = question.get('question', '')
            
            if not question_text:
                print(f"  ❌ 第{i}题（{question_type}）: 题干为空")
                incomplete_practices.append(practice)
            elif question_text in ['填空题', '判断题', '选择题', '代码补全题', '编程题']:
                print(f"  ⚠️  第{i}题（{question_type}）: 题干不完整 - {question_text}")
                incomplete_practices.append(practice)
            else:
                print(f"  ✅ 第{i}题（{question_type}）: 题干完整")
                
            # 检查判断题选项
            if question_type == 'Judgment' or question_type == 'judgment':
                options = question.get('options', [])
                if len(options) < 2:
                    print(f"  ⚠️  第{i}题（{question_type}）: 缺少选项")
    
    if not incomplete_practices:
        print("\n🎉 所有练习题集的题目都完整！")
    else:
        print(f"\n⚠️  发现 {len(set(incomplete_practices))} 个练习题集存在不完整的题目")

if __name__ == "__main__":
    check_practice_questions()

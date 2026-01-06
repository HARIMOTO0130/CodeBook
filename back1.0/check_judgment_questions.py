import os
import django
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# 导入模型
from apps.books.models import Practice

def check_judgment_questions():
    print('开始检查所有练习的第三题（判断题）选项完整性...')
    
    # 获取所有练习
    practices = Practice.objects.all()
    total_practices = practices.count()
    print(f'共找到 {total_practices} 个练习')
    
    # 统计问题
    completed_practices = 0
    missing_options_count = 0
    has_options_count = 0
    
    for practice in practices:
        if practice.questions and isinstance(practice.questions, list):
            # 获取第三题（索引为2，因为从0开始）
            if len(practice.questions) >= 3:
                third_question = practice.questions[2]
                question_id = third_question.get('id', 3)
                question_type = third_question.get('type', 'unknown')
                
                # 检查是否为判断题
                if question_type in ['Judgment', 'judgment', 'true_false']:
                    # 检查是否有options字段
                    if 'options' in third_question and isinstance(third_question['options'], list):
                        if len(third_question['options']) >= 2:
                            has_options_count += 1
                            print(f'✓ 练习 {practice.id} - 第三题（ID: {question_id}）有完整选项')
                        else:
                            missing_options_count += 1
                            print(f'✗ 练习 {practice.id} - 第三题（ID: {question_id}）选项数量不足: {len(third_question["options"])} 个')
                    else:
                        missing_options_count += 1
                        print(f'✗ 练习 {practice.id} - 第三题（ID: {question_id}）缺少options字段')
                    
                    completed_practices += 1
    
    print(f'\n检查完成:')
    print(f'共检查 {completed_practices} 个练习的第三题')
    print(f'✅ 有完整选项的判断题: {has_options_count} 个')
    print(f'❌ 缺少选项的判断题: {missing_options_count} 个')
    
    if missing_options_count > 0:
        print('\n建议运行 update_all_practice_questions.py 脚本修复这些问题')
    else:
        print('\n所有判断题都有完整选项！')

if __name__ == '__main__':
    check_judgment_questions()
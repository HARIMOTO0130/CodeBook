#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""测试个性化建议生成功能"""

import os
import sys

# 添加Django项目根目录到Python路径 - 调整为正确的路径
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

# 设置Django环境变量 - 使用正确的设置模块名称
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back1.0.settings')

# 导入Django设置
import django
django.setup()

from apps.learning.personalized_learning_path import PersonalizedLearningPathGenerator


def test_generate_suggestions():
    """测试生成个性化建议"""
    print("开始测试生成个性化建议...")
    
    # 创建生成器实例
    generator = PersonalizedLearningPathGenerator()
    
    # 定义测试数据
    user_profile = {
        'professional_group': 'science',
        'learning_style': {
            'visual_score': 0.8,
            'auditory_score': 0.5,
            'reading_score': 0.7,
            'kinesthetic_score': 0.6,
            'pace_preference': 'balanced',
            'difficulty_preference': 'medium'
        },
        'knowledge_level': '中级',
        'interest_areas': ['人工智能', '机器学习'],
        'current_knowledge': ['Python编程', '线性代数'],
        'weak_knowledge': ['深度学习', '神经网络']
    }
    
    path = [
        {
            'id': 1,
            'title': 'Python基础',
            'type': 'concept',
            'level': 1,
            'difficulty': 1.0,
            'importance': 5.0,
            'description': 'Python编程语言的基础知识，包括语法、数据类型、控制流等。',
            'professional_group': 'science',
            'tags': ['Python', '编程基础']
        },
        {
            'id': 2,
            'title': '线性代数',
            'type': 'concept',
            'level': 2,
            'difficulty': 2.0,
            'importance': 4.5,
            'description': '线性代数的基本概念和运算，包括向量、矩阵、行列式等。',
            'professional_group': 'science',
            'tags': ['线性代数', '数学基础']
        },
        {
            'id': 3,
            'title': '机器学习基础',
            'type': 'concept',
            'level': 3,
            'difficulty': 3.0,
            'importance': 4.0,
            'description': '机器学习的基本概念和算法，包括监督学习、无监督学习等。',
            'professional_group': 'science',
            'tags': ['机器学习', '人工智能']
        }
    ]
    
    # 测试生成个性化建议
    try:
        suggestions = generator._generate_personalized_suggestions(path, user_profile)
        
        # 输出结果
        print('\n生成的个性化建议：')
        for i, suggestion in enumerate(suggestions, 1):
            print(f'{i}. {suggestion}')
        
        print(f'\n共生成 {len(suggestions)} 条建议')
        
        # 验证结果
        if suggestions:
            print('\n✅ 测试通过：成功生成个性化建议')
            return True
        else:
            print('\n❌ 测试失败：未生成任何建议')
            return False
            
    except Exception as e:
        print(f'\n❌ 测试失败：生成建议时发生错误 - {e}')
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    test_generate_suggestions()

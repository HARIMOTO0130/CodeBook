#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
查询数据库中判断题的详细结构，验证选项字段是否正确
"""

import os
import sys
import json

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.books.models import Practice

def check_judgment_options():
    """检查所有判断题的选项字段"""
    print("=== 检查判断题选项字段 ===")
    
    # 获取所有练习集
    practices = Practice.objects.all()
    
    for practice in practices:
        # 解析JSON数据
        try:
            practice_data = practice.questions
            
            # 查找第3题（判断题）
            if len(practice_data) >= 3:
                judgment_question = practice_data[2]
                
                print(f"\n练习集: {practice.title}")
                print(f"章节: {practice.chapter.title}")
                print(f"判断题类型: {judgment_question.get('type')}")
                print(f"判断题题干: {judgment_question.get('question')}")
                print(f"是否包含options字段: {'options' in judgment_question}")
                
                if 'options' in judgment_question:
                    options = judgment_question['options']
                    print(f"选项数量: {len(options)}")
                    for i, option in enumerate(options):
                        print(f"  选项{i+1}: {option.get('content')}, 是否正确: {option.get('is_correct')}")
                else:
                    print("  ❌ 缺少options字段")
                    
        except Exception as e:
            print(f"\n❌ 处理练习集 {practice.title} 时出错: {e}")

if __name__ == '__main__':
    check_judgment_options()

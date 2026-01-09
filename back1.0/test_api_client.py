#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试个性化学习路径API
"""

import os
import sys
import django

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from apps.learning.models import User

# 创建测试客户端
client = Client()

# 使用现有的学生用户
try:
    user = User.objects.get(username='student')
    print(f"找到现有用户: {user.username}")
    
    # 登录用户
    client.force_login(user)
    print("用户登录成功")
except User.DoesNotExist:
    print("学生用户不存在")
    sys.exit(1)

# 测试个性化学习路径生成
try:
    print("\n开始测试个性化学习路径生成API...")
    
    # 发送POST请求
    response = client.post(
        '/api/learning/personalized-path/generate/',
        {
            'learning_goal': 'Python编程',
            'max_nodes': 10
        },
        content_type='application/json'
    )
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    # 检查响应
    if response.status_code == 200:
        data = response.json()
        if 'path' in data and 'explanation' in data:
            print("\n测试成功！个性化学习路径生成API正常工作")
            
            # 检查是否生成了智能路径而不是回退路径
            if "智能路径生成服务暂时不可用" not in data['explanation']:
                print("✓ 成功生成了智能学习路径")
            else:
                print("✗ 仍在使用回退路径，请检查系统配置")
        else:
            print("\n测试失败：响应中缺少必要字段")
    else:
        print(f"\n测试失败：状态码 {response.status_code}")
        
except Exception as e:
    print(f"\n测试失败: {e}")
    import traceback
    traceback.print_exc()

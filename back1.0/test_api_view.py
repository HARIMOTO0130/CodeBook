#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试个性化学习路径API视图
"""

import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth.models import User

# 设置Django环境
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.learning.views import PersonalizedLearningPathAPIView

# 创建测试用户
test_user, created = User.objects.get_or_create(
    username='student',
    defaults={
        'email': 'student@example.com',
        'password': '123456'
    }
)

# 创建请求工厂
factory = RequestFactory()

# 测试generate_path方法
try:
    print("开始测试PersonalizedLearningPathAPIView.generate_path...")
    
    # 创建POST请求
    request = factory.post(
        '/api/learning/path/generate/',
        {
            'learning_goal': 'Python编程',
            'max_nodes': 10
        },
        content_type='application/json'
    )
    
    # 设置用户
    request.user = test_user
    
    # 调用视图方法
    response = PersonalizedLearningPathAPIView.generate_path(request)
    print(f"响应状态码: {response.status_code}")
    print(f"响应内容: {response.data}")
    
    # 检查响应
    if response.status_code == 200:
        if 'path' in response.data and 'explanation' in response.data:
            print("测试成功！")
        else:
            print("测试失败：响应中缺少必要字段")
    else:
        print(f"测试失败：状态码 {response.status_code}")
        
except Exception as e:
    print(f"测试失败: {e}")
    import traceback
    traceback.print_exc()

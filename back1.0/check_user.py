#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查并创建测试用户脚本
"""

import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.users.models import User
from apps.users.models import UserPreferences

def check_and_create_user(username, password, is_staff=False):
    """检查用户是否存在，不存在则创建"""
    print(f"\n检查用户: {username}")
    
    # 查找用户
    user = User.objects.filter(username=username).first()
    
    if user:
        print(f"✓ 用户 {username} 已存在")
        print(f"  - 激活状态: {user.is_active}")
        print(f"  - 管理员权限: {user.is_staff}")
        print(f"  - 密码是否匹配: {'✓' if user.check_password(password) else '✗'}")
        
        # 如果密码不匹配，更新密码
        if not user.check_password(password):
            print(f"  ! 更新密码为: {password}")
            user.set_password(password)
            user.save()
            print(f"  ✓ 密码更新成功")
            
        # 确保用户处于激活状态
        if not user.is_active:
            print(f"  ! 激活用户 {username}")
            user.is_active = True
            user.save()
            print(f"  ✓ 用户已激活")
            
        # 确保用户有偏好设置
        preferences, created = UserPreferences.objects.get_or_create(user=user)
        if created:
            print(f"  ✓ 创建了用户偏好设置")
            
    else:
        # 创建新用户
        print(f"✗ 用户 {username} 不存在，正在创建...")
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password=password,
            is_staff=is_staff,
            is_active=True
        )
        print(f"  ✓ 用户 {username} 创建成功")
        
        # 创建用户偏好设置
        UserPreferences.objects.create(user=user)
        print(f"  ✓ 创建了用户偏好设置")
    
    return user

if __name__ == "__main__":
    print("=" * 60)
    print("用户检查与创建工具")
    print("=" * 60)
    
    # 检查并创建管理员用户
    admin_user = check_and_create_user('admin', 'admin123', is_staff=True)
    
    # 检查并创建普通用户
    student_user = check_and_create_user('student', 'student123', is_staff=False)
    
    print("\n" + "=" * 60)
    print("所有用户检查完成!")
    print(f"管理员账号: admin / admin123")
    print(f"普通用户账号: student / student123")
    print("=" * 60)
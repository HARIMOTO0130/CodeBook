#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""检查数据库表结构"""
import os
import sys
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.db import connection

def check_tables():
    with connection.cursor() as cursor:
        # 检查所有表
        cursor.execute("SHOW TABLES")
        all_tables = [t[0] for t in cursor.fetchall()]
        
        print("=" * 60)
        print("数据库表检查报告")
        print("=" * 60)
        
        # 审核端相关表
        print("\n【审核端相关表】")
        review_tables = [t for t in all_tables if 'review' in t]
        if review_tables:
            for table in review_tables:
                print(f"  ✓ {table}")
        else:
            print("  ✗ 未找到审核端相关表")
        
        # 用户相关表
        print("\n【用户相关表】")
        user_tables = [t for t in all_tables if 'user' in t or 'auth' in t or 'token' in t]
        for table in user_tables:
            print(f"  ✓ {table}")
        
        # 检查users_user表结构
        print("\n【users_user表字段】")
        try:
            cursor.execute("DESCRIBE users_user")
            columns = cursor.fetchall()
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
        except Exception as e:
            print(f"  ✗ 无法获取表结构: {e}")
        
        # 检查是否有reviewer角色的用户
        print("\n【审核员角色用户】")
        try:
            cursor.execute("SELECT COUNT(*) FROM users_user WHERE role = 'reviewer'")
            count = cursor.fetchone()[0]
            print(f"  当前有 {count} 个审核员用户")
            
            if count > 0:
                cursor.execute("SELECT id, username, email, role FROM users_user WHERE role = 'reviewer' LIMIT 5")
                users = cursor.fetchall()
                print("  审核员列表:")
                for user in users:
                    print(f"    - ID:{user[0]} {user[1]} ({user[2]})")
        except Exception as e:
            print(f"  ✗ 无法查询: {e}")
        
        print("\n" + "=" * 60)
        print("检查完成")
        print("=" * 60)

if __name__ == '__main__':
    check_tables()

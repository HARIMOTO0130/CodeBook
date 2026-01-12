#!/usr/bin/env python
"""
临时脚本，用于检查数据库表结构
"""
import os
import django
from django.db import connection

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

def check_table_structure(table_name):
    """检查指定表的结构"""
    with connection.cursor() as cursor:
        # 获取表结构
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        
        print(f"表 {table_name} 的结构:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} (Null: {col[2]}, Key: {col[3]}, Default: {col[4]}, Extra: {col[5]})")
        print()

if __name__ == "__main__":
    # 检查student_learning_progress表
    check_table_structure('student_learning_progress')
    # 也可以检查其他相关表
    check_table_structure('student')
    check_table_structure('class')

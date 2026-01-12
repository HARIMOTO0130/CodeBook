#!/usr/bin/env python
"""
检查 student_learning_progress 表的结构
"""
import os
import django
from django.db import connection

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def check_progress_table():
    """检查 student_learning_progress 表的结构"""
    with connection.cursor() as cursor:
        print("检查 student_learning_progress 表结构...")
        # 获取表结构
        cursor.execute("DESCRIBE student_learning_progress")
        columns = cursor.fetchall()
        
        print(f"表 student_learning_progress 的结构:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} (Null: {col[2]}, Key: {col[3]}, Default: {col[4]}, Extra: {col[5]})")
        print()
        
        # 检查是否有数据
        cursor.execute("SELECT COUNT(*) FROM student_learning_progress")
        count = cursor.fetchone()[0]
        print(f"表 student_learning_progress 中有 {count} 条数据")

if __name__ == "__main__":
    check_progress_table()

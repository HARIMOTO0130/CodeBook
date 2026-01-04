#!/usr/bin/env python
"""
查询并显示Django项目数据库中的所有表及其内容
"""

import os
import sys
import django
from django.db import connection

# 设置Django环境
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def get_all_tables():
    """获取数据库中所有表的名称"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' AND name NOT LIKE 'django_%';")
        return [table[0] for table in cursor.fetchall()]

def get_table_content(table_name):
    """获取指定表的内容"""
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT * FROM {table_name}")
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        return columns, rows

def get_table_count(table_name):
    """获取指定表的记录数"""
    with connection.cursor() as cursor:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        return cursor.fetchone()[0]

def main():
    """主函数"""
    print("=" * 80)
    print("数据库表内容检查")
    print("=" * 80)
    
    # 获取所有表名
    tables = get_all_tables()
    print(f"发现 {len(tables)} 个自定义表:")
    
    for i, table_name in enumerate(tables, 1):
        print(f"\n{"=" * 80}")
        print(f"表 {i}/{len(tables)}: {table_name}")
        print(f"{"=" * 80}")
        
        # 获取表记录数
        count = get_table_count(table_name)
        print(f"记录数: {count}")
        
        # 如果表有记录，显示内容
        if count > 0:
            columns, rows = get_table_content(table_name)
            print(f"列名: {', '.join(columns)}")
            print("-" * 80)
            
            # 显示前10条记录（如果记录数超过10）
            display_rows = rows[:10]
            for row in display_rows:
                print(row)
            
            if count > 10:
                print(f"\n... 还有 {count - 10} 条记录未显示")
        else:
            print("该表为空")
    
    print(f"\n{"=" * 80}")
    print("数据库表检查完成")
    print(f"{"=" * 80}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n发生错误: {e}")
        sys.exit(1)
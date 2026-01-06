import os
import sys

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db import connection

def get_table_create_statement(table_name):
    """获取指定表的创建语句"""
    with connection.cursor() as cursor:
        cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
        create_statement = cursor.fetchone()[1]
        return create_statement

if __name__ == "__main__":
    tables_to_check = ['books_book', 'books_jupytercell']
    
    for table in tables_to_check:
        print(f"\n=== 表 {table} 的创建语句 ===")
        create_stmt = get_table_create_statement(table)
        print(create_stmt)
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "CodeBook.settings")
django.setup()

from django.db import connection

def check_practice_table():
    print("检查books_practice表结构：")
    with connection.cursor() as cursor:
        cursor.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = 'codebook' AND TABLE_NAME LIKE 'books_practice' 
        ORDER BY ORDINAL_POSITION;
        """)
        columns = cursor.fetchall()
        for column in columns:
            print(f"表名: {column[0]}, 字段名: {column[1]}, 数据类型: {column[2]}, 可空: {column[3]}, 默认值: {column[4]}")

if __name__ == "__main__":
    check_practice_table()

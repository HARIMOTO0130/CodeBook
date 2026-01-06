import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.db import connection

def view_practice_table():
    with connection.cursor() as cursor:
        # 查看表结构
        cursor.execute("DESCRIBE books_practice")
        columns = cursor.fetchall()
        print("Books_practice表结构：")
        for column in columns:
            print(f"字段名: {column[0]}, 类型: {column[1]}, 空值: {column[2]}, 键: {column[3]}, 默认值: {column[4]}, 额外: {column[5]}")
        
        # 查看当前数据
        cursor.execute("SELECT id, chapter_id, title, description, questions FROM books_practice LIMIT 5")
        rows = cursor.fetchall()
        print("\n当前数据（前5条）：")
        for row in rows:
            print(f"ID: {row[0]}, 章节ID: {row[1]}, 标题: {row[2]}, 描述: {row[3]}, 问题数: {len(row[4]) if row[4] else 0}")

if __name__ == "__main__":
    view_practice_table()

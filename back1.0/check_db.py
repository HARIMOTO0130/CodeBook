import os
import sys

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db import connection

def check_database_tables():
    print("检查数据库连接状态...")
    try:
        # 尝试连接数据库
        with connection.cursor() as cursor:
            # 获取所有表名
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            
        print(f"数据库连接成功！")
        print(f"当前数据库中有 {len(tables)} 个表：")
        for table in sorted(tables):
            print(f"  - {table}")
        
        return tables
    except Exception as e:
        print(f"数据库连接失败：{e}")
        return None

if __name__ == "__main__":
    check_database_tables()

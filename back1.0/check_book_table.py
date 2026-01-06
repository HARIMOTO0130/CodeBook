import mysql.connector
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 获取数据库连接信息
db_config = {
    'user': os.getenv('DB_USER', 'admin'),
    'password': os.getenv('DB_PASSWORD', 'Admin@123456'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '3306'),
    'database': os.getenv('DB_NAME', 'codebook')
}

# 连接数据库
try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    
    # 检查books_book表结构
    print("=== books_book 表结构 ===")
    cursor.execute("DESCRIBE books_book")
    columns = cursor.fetchall()
    
    print(f"\n列数: {len(columns)}")
    print("\n字段列表:")
    for column in columns:
        print(f"  {column[0]} ({column[1]}) - {column[2]}")
    
    cursor.close()
    conn.close()
    print("\n数据库连接已关闭")
    
except mysql.connector.Error as err:
    print(f"数据库连接错误: {err}")
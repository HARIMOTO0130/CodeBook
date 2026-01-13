#!/usr/bin/env python3
"""
脚本用于修复teacher_teachingresource表中所有缺失的字段
确保数据库表结构与模型定义一致
"""

import os
import sys
import django
from django.db import connection

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载Django设置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()


def add_missing_column(table_name, column_name, column_definition):
    """检查并添加缺失的列"""
    try:
        with connection.cursor() as cursor:
            # 检查字段是否已存在
            cursor.execute("""
                SELECT COLUMN_NAME 
                FROM INFORMATION_SCHEMA.COLUMNS 
                WHERE TABLE_NAME = %s 
                AND COLUMN_NAME = %s
            """, [table_name, column_name])
            
            if cursor.fetchone():
                print(f"✅ 字段 '{column_name}' 已存在")
                return True
            
            # 尝试添加字段
            try:
                cursor.execute(f"""
                    ALTER TABLE {table_name} 
                    ADD COLUMN {column_name} {column_definition}
                """)
                print(f"✅ 成功添加字段 '{column_name}'")
                return True
            except Exception as e:
                print(f"❌ 添加字段 '{column_name}' 时出错: {str(e)}")
                return False
                
    except Exception as e:
        print(f"❌ 检查字段 '{column_name}' 时出错: {str(e)}")
        return False


def main():
    """主函数"""
    table_name = 'teacher_teachingresource'
    
    print(f"开始修复 {table_name} 表中的缺失字段...")
    
    # 定义需要添加的字段
    fields = [
        # 字段名: (字段定义)
        ('file_hash', 'VARCHAR(64) NULL COMMENT "文件哈希值"'),
        ('upload_status', 'VARCHAR(20) DEFAULT "completed" COMMENT "上传状态"'),
        ('storage_path', 'TEXT NULL COMMENT "完整存储路径"'),
        ('mime_type', 'VARCHAR(100) NULL COMMENT "文件MIME类型"'),
        ('upload_ip', 'VARCHAR(45) NULL COMMENT "上传IP地址"'),
        ('retry_count', 'INT DEFAULT 0 COMMENT "重试次数"'),
        ('download_count', 'INT DEFAULT 0 COMMENT "下载次数"'),
    ]
    
    # 逐个添加字段
    for field_name, field_definition in fields:
        add_missing_column(table_name, field_name, field_definition)
    
    print("\n修复完成！")


if __name__ == "__main__":
    main()
import mysql.connector
import json

# 数据库配置
config = {
    'user': 'admin',
    'password': 'Admin@123456',
    'host': 'localhost',
    'port': 3306,
    'database': 'codebook',
    'charset': 'utf8mb4'
}

def get_table_structure(table_name):
    """获取指定表的结构信息"""
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        
        # 获取表的字段信息
        cursor.execute(f"DESCRIBE {table_name}")
        columns = cursor.fetchall()
        
        # 获取表的主键信息
        cursor.execute(f"SHOW INDEX FROM {table_name} WHERE Key_name = 'PRIMARY'")
        primary_keys = [row[4] for row in cursor.fetchall()]
        
        # 获取自增字段信息
        auto_increment = None
        for col in columns:
            if 'auto_increment' in col[5]:
                auto_increment = col[0]
                break
        
        # 获取外键信息
        cursor.execute(f"SHOW CREATE TABLE {table_name}")
        create_table = cursor.fetchone()[1]
        
        cursor.close()
        cnx.close()
        
        # 格式化字段信息
        formatted_columns = []
        for col in columns:
            formatted_columns.append({
                'name': col[0],
                'type': col[1],
                'null': col[2] == 'YES',
                'key': col[3],
                'default': col[4],
                'extra': col[5]
            })
        
        return {
            'columns': formatted_columns,
            'primary_keys': primary_keys,
            'auto_increment': auto_increment,
            'create_table': create_table
        }
        
    except Exception as e:
        print(f"获取表 {table_name} 结构失败: {str(e)}")
        return None

if __name__ == "__main__":
    # 获取需要修复的表结构
    tables_to_check = ['toolkit_executionhistory', 'toolkit_toolparameter']
    table_structures = {}
    
    for table in tables_to_check:
        structure = get_table_structure(table)
        if structure:
            table_structures[table] = structure
    
    # 保存表结构到文件
    with open('toolkit_table_structures.json', 'w', encoding='utf-8') as f:
        json.dump(table_structures, f, ensure_ascii=False, indent=2)
    
    print("表结构信息已保存到 toolkit_table_structures.json")
    
    # 打印表结构摘要
    for table, structure in table_structures.items():
        print(f"\n{table} 表结构:")
        print(f"  字段数: {len(structure['columns'])}")
        print(f"  字段列表:")
        for col in structure['columns']:
            print(f"    - {col['name']} ({col['type']}) {'NULL' if col['null'] else 'NOT NULL'}")

import os
import sys

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.db import connection
import json

def get_table_structure():
    """获取数据库中所有表的详细结构信息"""
    print("正在获取数据库表结构...")
    
    table_structures = {}
    
    with connection.cursor() as cursor:
        # 获取所有表名
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        print(f"共找到 {len(tables)} 个表")
        
        for table_name in tables:
            print(f"  分析表: {table_name}")
            
            # 获取表的字段信息
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            
            table_info = {
                'columns': [],
                'primary_keys': [],
                'auto_increment': None
            }
            
            for column in columns:
                field_name = column[0]
                field_type = column[1]
                is_null = column[2] == 'YES'
                key = column[3]
                default = column[4]
                extra = column[5]
                
                column_info = {
                    'name': field_name,
                    'type': field_type,
                    'null': is_null,
                    'key': key,
                    'default': default,
                    'extra': extra
                }
                
                table_info['columns'].append(column_info)
                
                if key == 'PRI':
                    table_info['primary_keys'].append(field_name)
                
                if 'auto_increment' in extra:
                    table_info['auto_increment'] = field_name
            
            # 获取表的外键信息
            cursor.execute(f"SHOW CREATE TABLE `{table_name}`")
            create_table_sql = cursor.fetchone()[1]
            
            # 解析外键信息（简化版）
            foreign_keys = []
            if 'FOREIGN KEY' in create_table_sql:
                lines = create_table_sql.split('\n')
                for line in lines:
                    if 'FOREIGN KEY' in line:
                        # 简化的外键解析
                        foreign_key_info = line.strip()
                        foreign_keys.append(foreign_key_info)
            
            table_info['foreign_keys'] = foreign_keys
            table_structures[table_name] = table_info
    
    # 保存表结构信息到文件
    with open('table_structures.json', 'w', encoding='utf-8') as f:
        json.dump(table_structures, f, ensure_ascii=False, indent=2)
    
    print("\n表结构信息已保存到 table_structures.json 文件")
    return table_structures

def analyze_sql_insert_compatibility(sql_file_path, table_structures):
    """分析SQL文件中的插入语句与表结构的兼容性"""
    print(f"\n正在分析SQL文件: {sql_file_path}")
    
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 查找所有INSERT语句
    import re
    insert_pattern = re.compile(r'INSERT INTO\s+`?([^`\s]+)`?\s+VALUES\s+\((.+)\);', re.IGNORECASE | re.DOTALL)
    insert_matches = insert_pattern.findall(sql_content)
    
    print(f"找到 {len(insert_matches)} 条INSERT语句")
    
    compatibility_issues = []
    
    for i, (table_name, values_str) in enumerate(insert_matches, 1):
        print(f"  分析第 {i} 条INSERT语句 (表: {table_name})")
        
        if table_name not in table_structures:
            compatibility_issues.append({
                'insert_index': i,
                'table_name': table_name,
                'issue_type': 'table_not_exists',
                'message': f'表 {table_name} 在当前数据库中不存在'
            })
            continue
        
        # 解析插入的值（简化版，假设没有嵌套的括号）
        values_list = []
        current_value = []
        in_string = False
        string_char = ''
        
        for char in values_str:
            if char in ['"', "'", '`'] and (not current_value or current_value[-1] != '\\'):
                if in_string and char == string_char:
                    in_string = False
                    string_char = ''
                elif not in_string:
                    in_string = True
                    string_char = char
            
            current_value.append(char)
            
            if char == ',' and not in_string:
                values_list.append(''.join(current_value[:-1]).strip())
                current_value = []
        
        # 添加最后一个值
        if current_value:
            values_list.append(''.join(current_value).strip())
        
        table_columns = table_structures[table_name]['columns']
        num_columns = len(table_columns)
        num_values = len(values_list)
        
        if num_columns != num_values:
            compatibility_issues.append({
                'insert_index': i,
                'table_name': table_name,
                'issue_type': 'column_count_mismatch',
                'message': f'列数不匹配: 表有 {num_columns} 列，但插入了 {num_values} 个值'
            })
            continue
        
        # 检查字段类型兼容性（简化版）
        type_issues = []
        for j, (column, value) in enumerate(zip(table_columns, values_list)):
            column_name = column['name']
            column_type = column['type']
            
            # 简化的类型检查
            if 'int' in column_type.lower() or 'bigint' in column_type.lower():
                # 整数类型
                stripped_value = value.strip("'`")
                if stripped_value and not stripped_value.replace('-', '').isdigit() and stripped_value != 'NULL':
                    type_issues.append(f"字段 {column_name} (类型 {column_type}) 可能与值 {value} 不兼容")
            elif 'varchar' in column_type.lower() or 'text' in column_type.lower():
                # 字符串类型
                if not value.startswith("'") and not value.startswith('"') and not value.startswith('`') and value != 'NULL':
                    type_issues.append(f"字段 {column_name} (类型 {column_type}) 可能需要字符串值，但当前值为 {value}")
            elif 'datetime' in column_type.lower() or 'date' in column_type.lower():
                # 日期时间类型
                if value != 'NULL' and not (value.startswith("'") or value.startswith('"')):
                    type_issues.append(f"字段 {column_name} (类型 {column_type}) 可能需要日期时间字符串，但当前值为 {value}")
        
        if type_issues:
            compatibility_issues.append({
                'insert_index': i,
                'table_name': table_name,
                'issue_type': 'type_compatibility',
                'message': f'类型兼容性问题: {"，".join(type_issues)}'
            })
    
    # 保存兼容性问题到文件
    with open('compatibility_issues.json', 'w', encoding='utf-8') as f:
        json.dump(compatibility_issues, f, ensure_ascii=False, indent=2)
    
    print(f"\n分析完成，共发现 {len(compatibility_issues)} 个兼容性问题")
    print("兼容性问题已保存到 compatibility_issues.json 文件")
    
    return compatibility_issues

if __name__ == "__main__":
    # 获取表结构
    table_structures = get_table_structure()
    
    # 分析SQL文件兼容性
    sql_file = "d:\halimotodata\数字教材\lfy1.0\CodeBook\codebook.sql"
    analyze_sql_insert_compatibility(sql_file, table_structures)

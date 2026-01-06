import json
import re

def load_table_structures():
    """加载表结构信息"""
    with open('table_structures.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_sql_inserts(sql_file_path):
    """解析SQL文件中的所有INSERT语句"""
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 正确解析INSERT语句的正则表达式
    insert_pattern = re.compile(r'INSERT\s+INTO\s+`?([^`\s]+)`?\s+VALUES\s+\(([\s\S]*?)\);', re.IGNORECASE)
    return insert_pattern.findall(sql_content)

def parse_insert_values(values_str):
    """解析INSERT语句中的值列表"""
    values = []
    current_value = []
    in_string = False
    string_char = ''
    paren_count = 0
    
    for char in values_str:
        # 处理字符串边界
        if char in ['"', "'", '`'] and (not current_value or current_value[-1] != '\\'):
            if in_string and char == string_char:
                in_string = False
                string_char = ''
            elif not in_string:
                in_string = True
                string_char = char
        
        # 处理括号嵌套
        if char == '(' and not in_string:
            paren_count += 1
        elif char == ')' and not in_string:
            paren_count -= 1
        
        # 添加字符到当前值
        current_value.append(char)
        
        # 当遇到逗号且不在字符串中且括号匹配时，添加当前值
        if char == ',' and not in_string and paren_count == 0:
            values.append(''.join(current_value[:-1]).strip())
            current_value = []
    
    # 添加最后一个值
    if current_value:
        values.append(''.join(current_value).strip())
    
    return values

def check_type_compatibility(column, value):
    """检查字段类型与值的兼容性"""
    column_name = column['name']
    column_type = column['type'].lower()
    value_str = value.strip()
    
    # 处理NULL值
    if value_str.upper() == 'NULL':
        if not column['null']:
            return False, f"字段 {column_name} 不允许为NULL，但值为NULL"
        return True, None
    
    # 处理整数类型
    if 'int' in column_type or 'bigint' in column_type:
        stripped_value = value_str.strip("'`")
        if not stripped_value.replace('-', '').isdigit():
            return False, f"字段 {column_name} (类型 {column['type']}) 需要整数值，但值为 {value}"
    
    # 处理字符串类型
    elif 'varchar' in column_type or 'text' in column_type or 'char' in column_type:
        if not value_str.startswith("'") and not value_str.startswith('"') and not value_str.startswith('`'):
            return False, f"字段 {column_name} (类型 {column['type']}) 需要字符串值，但值为 {value}"
    
    # 处理日期时间类型
    elif 'datetime' in column_type or 'date' in column_type or 'time' in column_type:
        if not value_str.startswith("'") and not value_str.startswith('"'):
            return False, f"字段 {column_name} (类型 {column['type']}) 需要日期时间字符串，但值为 {value}"
    
    # 处理布尔类型
    elif 'boolean' in column_type or 'tinyint(1)' in column_type:
        stripped_value = value_str.strip("'`")
        if stripped_value not in ['0', '1', 'true', 'false', 'True', 'False']:
            return False, f"字段 {column_name} (类型 {column['type']}) 需要布尔值，但值为 {value}"
    
    return True, None

def analyze_compatibility():
    """分析所有INSERT语句与本地表结构的兼容性"""
    sql_file = "d:\\halimotodata\\数字教材\\lfy1.0\\CodeBook\\codebook.sql"
    
    # 加载表结构
    table_structures = load_table_structures()
    print(f"已加载 {len(table_structures)} 个表的结构信息")
    
    # 解析INSERT语句
    insert_matches = parse_sql_inserts(sql_file)
    print(f"已解析 {len(insert_matches)} 条INSERT语句")
    
    # 分析兼容性
    compatibility_issues = []
    
    for i, (table_name, values_str) in enumerate(insert_matches, 1):
        if i % 50 == 0:
            print(f"  正在分析第 {i} 条INSERT语句...")
        
        # 检查表是否存在
        if table_name not in table_structures:
            compatibility_issues.append({
                'insert_index': i,
                'table_name': table_name,
                'issue_type': 'table_not_exists',
                'message': f'表 {table_name} 在当前数据库中不存在'
            })
            continue
        
        # 解析值
        table_columns = table_structures[table_name]['columns']
        try:
            values = parse_insert_values(values_str)
        except Exception as e:
            compatibility_issues.append({
                'insert_index': i,
                'table_name': table_name,
                'issue_type': 'parse_error',
                'message': f'解析值时出错: {str(e)}'
            })
            continue
        
        # 检查列数匹配
        num_columns = len(table_columns)
        num_values = len(values)
        
        if num_columns != num_values:
            compatibility_issues.append({
                'insert_index': i,
                'table_name': table_name,
                'issue_type': 'column_count_mismatch',
                'message': f'列数不匹配: 表有 {num_columns} 列，但插入了 {num_values} 个值'
            })
            continue
        
        # 检查类型兼容性
        for j, (column, value) in enumerate(zip(table_columns, values)):
            is_compatible, error_msg = check_type_compatibility(column, value)
            if not is_compatible:
                compatibility_issues.append({
                    'insert_index': i,
                    'table_name': table_name,
                    'issue_type': 'type_compatibility',
                    'message': error_msg
                })
    
    # 保存兼容性问题
    with open('compatibility_issues_detailed.json', 'w', encoding='utf-8') as f:
        json.dump(compatibility_issues, f, ensure_ascii=False, indent=2)
    
    print(f"\n兼容性分析完成")
    print(f"找到 {len(compatibility_issues)} 个兼容性问题")
    print("详细信息已保存到 compatibility_issues_detailed.json 文件")
    
    # 打印问题类型统计
    issue_types = {}
    for issue in compatibility_issues:
        issue_type = issue['issue_type']
        issue_types[issue_type] = issue_types.get(issue_type, 0) + 1
    
    print(f"\n问题类型统计:")
    for issue_type, count in issue_types.items():
        print(f"  {issue_type}: {count} 个")

if __name__ == "__main__":
    analyze_compatibility()
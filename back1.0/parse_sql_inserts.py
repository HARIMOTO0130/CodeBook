import re
import os

def parse_sql_inserts(sql_file_path):
    """正确解析SQL文件中的所有INSERT语句"""
    print(f"正在解析SQL文件: {sql_file_path}")
    
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 使用更可靠的正则表达式来匹配INSERT语句
    # 不使用re.DOTALL，这样它只会匹配单行或多行但不包含分号的INSERT语句
    insert_pattern = re.compile(r'INSERT\s+INTO\s+`?([^`\s]+)`?\s+VALUES\s+\(([\s\S]*?)\);', re.IGNORECASE)
    
    insert_matches = insert_pattern.findall(sql_content)
    
    print(f"找到 {len(insert_matches)} 条INSERT语句")
    
    # 打印前几条INSERT语句的信息
    for i, (table_name, values_str) in enumerate(insert_matches[:5], 1):
        print(f"  第 {i} 条: 表 {table_name}, 值长度: {len(values_str)} 字符")
        
        # 尝试解析值
        values = []
        current_value = []
        in_string = False
        string_char = ''
        paren_count = 0
        
        for char in values_str:
            if char in ['"', "'", '`'] and (not current_value or current_value[-1] != '\\'):
                if in_string and char == string_char:
                    in_string = False
                    string_char = ''
                elif not in_string:
                    in_string = True
                    string_char = char
            
            if char == '(' and not in_string:
                paren_count += 1
            elif char == ')' and not in_string:
                paren_count -= 1
            
            current_value.append(char)
            
            if char == ',' and not in_string and paren_count == 0:
                values.append(''.join(current_value[:-1]).strip())
                current_value = []
        
        # 添加最后一个值
        if current_value:
            values.append(''.join(current_value).strip())
        
        print(f"    解析到 {len(values)} 个值")
    
    return insert_matches

if __name__ == "__main__":
    sql_file = "d:\\halimotodata\\数字教材\\lfy1.0\\CodeBook\\codebook.sql"
    parse_sql_inserts(sql_file)
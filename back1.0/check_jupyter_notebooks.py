import re

def get_jupyter_notebook_inserts(sql_file_path):
    """获取books_jupyternotebook表的INSERT语句"""
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    pattern = re.compile(r'INSERT\s+INTO\s+books_jupyternotebook\s+VALUES\s+\(([\s\S]*?)\);', re.IGNORECASE)
    return pattern.findall(sql_content)

def parse_values(values_str):
    """解析值列表"""
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
    
    if current_value:
        values.append(''.join(current_value).strip())
    
    return values

def main():
    sql_file = "d:\\halimotodata\\数字教材\\lfy1.0\\CodeBook\\codebook.sql"
    
    notebook_inserts = get_jupyter_notebook_inserts(sql_file)
    print(f"找到 {len(notebook_inserts)} 条books_jupyternotebook表的INSERT语句")
    
    for i, insert in enumerate(notebook_inserts, 1):
        values = parse_values(insert)
        print(f"\n第 {i} 条INSERT语句值:")
        for j, val in enumerate(values, 1):
            print(f"  {j}. {val}")

if __name__ == "__main__":
    main()
import json
import re

def load_table_structures():
    """加载表结构信息"""
    with open('table_structures.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def get_table_insert_statements(sql_file_path, table_name):
    """获取指定表的INSERT语句"""
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    pattern = re.compile(rf'INSERT\s+INTO\s+`?{table_name}`?\s+VALUES\s+\(([\s\S]*?)\);', re.IGNORECASE)
    return pattern.findall(sql_content)

def parse_insert_values(values_str):
    """解析INSERT语句中的值列表"""
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
    table_structures = load_table_structures()
    
    # 分析books_book表
    print("=== 分析 books_book 表 ===")
    book_table = table_structures.get('books_book', {})
    if book_table:
        print(f"表结构: {len(book_table['columns'])} 列")
        print("字段列表:")
        for i, col in enumerate(book_table['columns'], 1):
            print(f"  {i}. {col['name']} ({col['type']}, NULL: {col['null']}, KEY: {col['key']})")
        
        # 获取INSERT语句
        book_inserts = get_table_insert_statements(sql_file, 'books_book')
        print(f"\n找到 {len(book_inserts)} 条INSERT语句")
        
        if book_inserts:
            # 解析第一个INSERT语句
            values = parse_insert_values(book_inserts[0])
            print(f"第一个INSERT语句有 {len(values)} 个值:")
            for i, val in enumerate(values, 1):
                print(f"  {i}. {val}")
    
    print("\n" + "="*50 + "\n")
    
    # 分析books_jupytercell表
    print("=== 分析 books_jupytercell 表 ===")
    jupyter_table = table_structures.get('books_jupytercell', {})
    if jupyter_table:
        print(f"表结构: {len(jupyter_table['columns'])} 列")
        print("字段列表:")
        for i, col in enumerate(jupyter_table['columns'], 1):
            print(f"  {i}. {col['name']} ({col['type']}, NULL: {col['null']}, KEY: {col['key']})")
        
        # 获取INSERT语句
        jupyter_inserts = get_table_insert_statements(sql_file, 'books_jupytercell')
        print(f"\n找到 {len(jupyter_inserts)} 条INSERT语句")
        
        if jupyter_inserts:
            # 解析第一个INSERT语句
            values = parse_insert_values(jupyter_inserts[0])
            print(f"第一个INSERT语句有 {len(values)} 个值:")
            for i, val in enumerate(values, 1):
                print(f"  {i}. {val}")

if __name__ == "__main__":
    main()
import re
import os

def fix_sql_inserts(sql_file_path):
    """修复SQL文件中的INSERT语句，使其与本地表结构兼容"""
    print(f"正在修复SQL文件: {sql_file_path}")
    
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # books_book表的INSERT语句已经与表结构兼容，无需修复
    print("1. books_book表的INSERT语句已与表结构兼容，无需修复")
    
    # 修复books_jupytercell表的INSERT语句
    print("2. 修复books_jupytercell表的INSERT语句...")
    jupyter_pattern = re.compile(r'(INSERT\s+INTO\s+books_jupytercell\s+VALUES\s+\()([\s\S]*?)(\);)', re.IGNORECASE)
    
    # 统计修复的数量，用于分配notebook_id
    jupyter_matches = jupyter_pattern.findall(sql_content)
    print(f"   找到 {len(jupyter_matches)} 条books_jupytercell表的INSERT语句")
    
    # 简单的notebook_id分配策略：平均分配到可用的notebook_id
    # 根据之前的分析，notebook_id有1-9可用
    notebooks = list(range(1, 10))
    notebooks_per_id = len(jupyter_matches) // len(notebooks) + 1
    
    def fix_jupyter_insert(match, counter=[0]):
        prefix = match.group(1)
        values_str = match.group(2)
        suffix = match.group(3)
        
        # 根据计数器分配notebook_id
        notebook_id = notebooks[counter[0] // notebooks_per_id]
        if notebook_id > 9:
            notebook_id = 9  # 确保不超过最大可用ID
        
        # 在值列表末尾添加notebook_id
        fixed_values = values_str + f', {notebook_id}'
        
        counter[0] += 1
        return prefix + fixed_values + suffix
    
    sql_content = jupyter_pattern.sub(fix_jupyter_insert, sql_content)
    print("   完成")
    
    # 修复toolkit_executionhistory表的INSERT语句
    print("3. 修复toolkit_executionhistory表的INSERT语句...")
    execution_pattern = re.compile(r'(INSERT\s+INTO\s+toolkit_executionhistory\s+VALUES\s+\()([\s\S]*?)(\);)', re.IGNORECASE)
    
    # 统计修复的数量
    execution_matches = execution_pattern.findall(sql_content)
    print(f"   找到 {len(execution_matches)} 条toolkit_executionhistory表的INSERT语句")
    
    def count_values(values_str):
        """统计值的数量，考虑字符串内的逗号"""
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
        
        return len(values)
    
    def fix_execution_insert(match):
        prefix = match.group(1)
        values_str = match.group(2)
        suffix = match.group(3)
        
        # 统计当前值的数量
        value_count = count_values(values_str)
        
        # 根据值的数量添加相应的字段
        if value_count == 6:
            # 缺少tool_id和user_id
            fixed_values = values_str + ', 1, NULL'
        elif value_count == 7:
            # 缺少user_id
            fixed_values = values_str + ', NULL'
        else:
            # 值的数量正确
            fixed_values = values_str
        
        return prefix + fixed_values + suffix
    
    sql_content = execution_pattern.sub(fix_execution_insert, sql_content)
    print("   完成")
    
    # 修复toolkit_toolparameter表的INSERT语句
    print("4. 修复toolkit_toolparameter表的INSERT语句...")
    parameter_pattern = re.compile(r'(INSERT\s+INTO\s+toolkit_toolparameter\s+VALUES\s+\()([\s\S]*?)(\);)', re.IGNORECASE)
    
    # 统计修复的数量
    parameter_matches = parameter_pattern.findall(sql_content)
    print(f"   找到 {len(parameter_matches)} 条toolkit_toolparameter表的INSERT语句")
    
    def fix_parameter_insert(match):
        prefix = match.group(1)
        values_str = match.group(2)
        suffix = match.group(3)
        
        # 添加tool_id字段值
        # 根据错误信息，该表有10个字段，但INSERT语句只有9个值
        fixed_values = values_str + ', 1'
        return prefix + fixed_values + suffix
    
    sql_content = parameter_pattern.sub(fix_parameter_insert, sql_content)
    print("   完成")
    
    # 修复books_practice表的INSERT语句
    print("5. 修复books_practice表的INSERT语句...")
    practice_pattern = re.compile(r'(INSERT\s+INTO\s+books_practice\s+VALUES\s+\()([\s\S]*?)(\);)', re.IGNORECASE)
    
    # 统计修复的数量
    practice_matches = practice_pattern.findall(sql_content)
    print(f"   找到 {len(practice_matches)} 条books_practice表的INSERT语句")
    
    def fix_practice_insert(match):
        prefix = match.group(1)
        values_str = match.group(2)
        suffix = match.group(3)
        
        # 添加questions字段值（JSON类型）
        # 根据表结构，该表有10个字段，但INSERT语句只有9个值
        fixed_values = values_str + ", '{}'"
        return prefix + fixed_values + suffix
    
    sql_content = practice_pattern.sub(fix_practice_insert, sql_content)
    print("   完成")
    
    # 修复books_jupyternotebook表的INSERT语句
    print("6. 修复books_jupyternotebook表的INSERT语句...")
    jupyternotebook_pattern = re.compile(r'(INSERT\s+INTO\s+books_jupyternotebook\s+VALUES\s+\()([\s\S]*?)(\);)', re.IGNORECASE)
    
    # 统计修复的数量
    jupyternotebook_matches = jupyternotebook_pattern.findall(sql_content)
    print(f"   找到 {len(jupyternotebook_matches)} 条books_jupyternotebook表的INSERT语句")
    
    def fix_jupyternotebook_insert(match, counter=[1]):
        prefix = match.group(1)
        values_str = match.group(2)
        suffix = match.group(3)
        
        # 添加chapter_id字段值
        # 根据表结构，该表有7个字段，但INSERT语句只有6个值
        # 由于chapter_id有唯一约束，使用递增的counter作为chapter_id
        fixed_values = values_str + f', {counter[0]}'
        counter[0] += 1
        return prefix + fixed_values + suffix
    
    sql_content = jupyternotebook_pattern.sub(fix_jupyternotebook_insert, sql_content)
    print("   完成")
    
    # 保存修复后的SQL文件
    fixed_file_path = sql_file_path.replace('.sql', '_fixed.sql')
    with open(fixed_file_path, 'w', encoding='utf-8') as f:
        f.write(sql_content)
    
    print(f"\n修复完成！")
    print(f"原始文件: {sql_file_path}")
    print(f"修复后的文件: {fixed_file_path}")
    
    return fixed_file_path

def verify_fixes(fixed_file_path):
    """验证修复后的SQL文件"""
    print(f"\n验证修复后的SQL文件: {fixed_file_path}")
    
    with open(fixed_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # 检查books_book表的INSERT语句
    book_pattern = re.compile(r'INSERT\s+INTO\s+books_book\s+VALUES\s+\(([\s\S]*?)\);', re.IGNORECASE)
    book_matches = book_pattern.findall(sql_content)
    print(f"\n1. books_book表: 共 {len(book_matches)} 条INSERT语句")
    
    if book_matches:
        # 检查第一个INSERT语句的列数
        values = []
        current_value = []
        in_string = False
        string_char = ''
        paren_count = 0
        
        for char in book_matches[0]:
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
        
        print(f"   第一个INSERT语句有 {len(values)} 个值 (预期: 11)")
    
    # 检查books_jupytercell表的INSERT语句
    jupyter_pattern = re.compile(r'INSERT\s+INTO\s+books_jupytercell\s+VALUES\s+\(([\s\S]*?)\);', re.IGNORECASE)
    jupyter_matches = jupyter_pattern.findall(sql_content)
    print(f"\n2. books_jupytercell表: 共 {len(jupyter_matches)} 条INSERT语句")
    
    if jupyter_matches:
        # 检查第一个INSERT语句的列数
        values = []
        current_value = []
        in_string = False
        string_char = ''
        paren_count = 0
        
        for char in jupyter_matches[0]:
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
        
        print(f"   第一个INSERT语句有 {len(values)} 个值 (预期: 9)")
        print(f"   最后一个值 (notebook_id): {values[-1] if values else 'N/A'}")

if __name__ == "__main__":
    sql_file = "d:\\halimotodata\\数字教材\\lfy1.0\\CodeBook\\codebook.sql"
    fixed_file = fix_sql_inserts(sql_file)
    verify_fixes(fixed_file)
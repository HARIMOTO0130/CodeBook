import mysql.connector
import os

# 数据库配置
config = {
    'user': 'admin',
    'password': 'Admin@123456',
    'host': 'localhost',
    'port': 3306,
    'database': 'codebook',
    'charset': 'utf8mb4'
}

def import_sql_file(file_path):
    """导入SQL文件到MySQL数据库"""
    print(f"正在导入SQL文件: {file_path}")
    
    try:
        # 连接数据库
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        
        # 读取SQL文件
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 分割SQL语句（以分号+换行符为分隔符）
        sql_statements = []
        current_statement = []
        in_string = False
        string_char = ''
        
        for line in sql_content.splitlines():
            for char in line:
                # 处理字符串边界
                if char in ['"', "'", '`'] and (not current_statement or current_statement[-1] != '\\'):
                    if in_string and char == string_char:
                        in_string = False
                        string_char = ''
                    elif not in_string:
                        in_string = True
                        string_char = char
                
                current_statement.append(char)
                
                # 如果遇到分号且不在字符串中，执行当前语句
                if char == ';' and not in_string:
                    sql_statement = ''.join(current_statement).strip()
                    if sql_statement:
                        sql_statements.append(sql_statement)
                    current_statement = []
                    break
            
            # 处理行末
            if current_statement:
                current_statement.append('\n')
        
        # 执行所有SQL语句
        success_count = 0
        error_count = 0
        
        for i, statement in enumerate(sql_statements):
            try:
                cursor.execute(statement)
                success_count += 1
                if i % 50 == 0:
                    print(f"   已执行 {i+1}/{len(sql_statements)} 条语句...")
            except Exception as e:
                error_count += 1
                print(f"\n   执行语句 {i+1} 时出错:")
                print(f"   语句: {statement[:100]}...")
                print(f"   错误: {str(e)}")
                
        # 提交事务
        cnx.commit()
        
        # 关闭连接
        cursor.close()
        cnx.close()
        
        print(f"\n导入完成！")
        print(f"总语句数: {len(sql_statements)}")
        print(f"成功: {success_count}")
        print(f"失败: {error_count}")
        
        return success_count, error_count
        
    except Exception as e:
        print(f"\n导入失败！")
        print(f"错误: {str(e)}")
        return 0, 1

if __name__ == "__main__":
    sql_file = "d:\halimotodata\数字教材\lfy1.0\CodeBook\codebook_fixed.sql"
    import_sql_file(sql_file)

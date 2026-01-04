#!/usr/bin/env python
"""
检查关键业务表的详细内容
"""

import os
import sys
import json
import django
from django.db import connection
from datetime import datetime

# 设置Django环境
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# 导入模型以便获取更结构化的数据
from apps.books.models import Book, Chapter, Practice, TestCase
from apps.books.jupyter_models import JupyterNotebook, JupyterCell, JupyterOutput

def format_json_data(data):
    """格式化JSON数据以便更好地显示"""
    if data:
        try:
            # 如果是字符串形式的JSON，尝试解析
            if isinstance(data, str):
                parsed = json.loads(data)
                return json.dumps(parsed, ensure_ascii=False, indent=2)
            # 如果已经是字典或列表
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception:
            return str(data)
    return "None"

def format_datetime(dt):
    """格式化日期时间"""
    if isinstance(dt, datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)

def print_separator(title):
    """打印分隔符"""
    print(f"\n{"=" * 80}")
    print(f"{title}")
    print(f"{"=" * 80}")

def check_books_table():
    """检查书籍表"""
    print_separator("检查 books_book 表")
    books = Book.objects.all()
    print(f"总共有 {books.count()} 本书籍")
    
    for i, book in enumerate(books, 1):
        print(f"\n书籍 {i}/{books.count()}:")
        print(f"  ID: {book.id}")
        print(f"  标题: {book.title}")
        print(f"  作者: {book.author}")
        print(f"  描述: {book.description}")
        print(f"  章节数量: {book.chapter_count}")
        print(f"  创建时间: {format_datetime(book.created_at)}")
        print(f"  更新时间: {format_datetime(book.updated_at)}")

def check_chapters_table():
    """检查章节表"""
    print_separator("检查 books_chapter 表")
    chapters = Chapter.objects.all()
    print(f"总共有 {chapters.count()} 个章节")
    
    # 按书籍分组显示章节
    book_ids = Chapter.objects.values_list('book_id', flat=True).distinct()
    for book_id in book_ids:
        book = Book.objects.get(id=book_id)
        book_chapters = Chapter.objects.filter(book_id=book_id).order_by('order')
        print(f"\n书籍 '{book.title}' 的章节:")
        
        for chapter in book_chapters:
            print(f"  章节 {chapter.order}: {chapter.title}")
            print(f"    类型: {chapter.type}")
            print(f"    时长: {chapter.duration} 分钟")
            print(f"    语言: {chapter.language}")
            
            # 检查是否有Jupyter关联
            has_jupyter = hasattr(chapter, 'jupyter_notebook') and chapter.jupyter_notebook is not None
            print(f"    Jupyter关联: {'是' if has_jupyter else '否'}")
            
            # 简要显示merged_content是否存在
            has_content = chapter.merged_content is not None
            print(f"    合并内容: {'是' if has_content else '否'}")

def check_jupyter_tables():
    """检查Jupyter相关表"""
    print_separator("检查 Jupyter 相关表")
    
    # 检查JupyterNotebook表
    notebooks = JupyterNotebook.objects.all()
    print(f"\n总共有 {notebooks.count()} 个Jupyter笔记本")
    
    for i, notebook in enumerate(notebooks, 1):
        chapter = notebook.chapter
        print(f"\n笔记本 {i}/{notebooks.count()}:")
        print(f"  关联章节: {chapter.title} (书籍: {chapter.book.title})")
        print(f"  nbformat: {notebook.nbformat}")
        print(f"  nbformat_minor: {notebook.nbformat_minor}")
        
        # 检查关联的单元格数量
        cell_count = JupyterCell.objects.filter(notebook=notebook).count()
        print(f"  包含 {cell_count} 个单元格")

def check_practice_tables():
    """检查练习题相关表"""
    print_separator("检查 练习题 相关表")
    
    # 检查Practice表
    practices = Practice.objects.all()
    print(f"\n总共有 {practices.count()} 个练习题")
    
    if practices:
        for practice in practices:
            print(f"\n练习题 ID: {practice.id}")
            print(f"  关联章节: {practice.chapter.title}")
            
            # 获取所有字段名和值
            fields = [(field.name, getattr(practice, field.name)) for field in practice._meta.fields]
            for field_name, field_value in fields:
                if field_name not in ['id', 'chapter']:
                    print(f"  {field_name}: {field_value}")
            
            # 检查测试用例数量
            test_cases = TestCase.objects.filter(practice=practice)
            print(f"  包含 {test_cases.count()} 个测试用例")

def check_all_tables_summary():
    """获取所有表的基本信息（仅表名和记录数）"""
    print_separator("数据库所有表概览")
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name;")
        tables = [table[0] for table in cursor.fetchall()]
        
        print(f"数据库中共有 {len(tables)} 个表:\n")
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count} 条记录")

def main():
    """主函数"""
    print("数据库关键表内容检查")
    print("=" * 80)
    
    try:
        # 先显示所有表的概览
        check_all_tables_summary()
        
        # 然后详细检查关键业务表
        check_books_table()
        check_chapters_table()
        check_jupyter_tables()
        check_practice_tables()
        
        print(f"\n{"=" * 80}")
        print("数据库检查完成")
        print(f"{"=" * 80}")
        
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
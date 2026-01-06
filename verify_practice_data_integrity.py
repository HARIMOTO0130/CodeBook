#!/usr/bin/env python3
"""
验证练习题数据完整性脚本
- 检查数据库中的练习题数据
- 调用API获取练习题数据
- 比较两者是否一致
- 确保所有数据都能在前端正常展示
"""

import os
import sys
import json
import requests
import pymysql
from pymysql.cursors import DictCursor

# 配置信息
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'admin',
    'password': 'Admin@123456',
    'database': 'codebook',
    'charset': 'utf8mb4'
}

api_config = {
    'base_url': 'http://localhost:8000/api/student',
    'token': ''  # 如果需要认证，请填写token
}


def get_db_practices():
    """从数据库获取所有练习题数据"""
    print("从数据库获取练习题数据...")
    conn = None
    try:
        conn = pymysql.connect(**db_config)
        with conn.cursor(DictCursor) as cursor:
            # 查询所有章节的练习题
            sql = """
            SELECT p.id, p.chapter_id, p.title, p.description, p.language, p.difficulty, p.questions,
                   b.id as book_id, b.title as book_title,
                   c.title as chapter_title
            FROM books_practice p
            JOIN books_chapter c ON p.chapter_id = c.id
            JOIN books_book b ON c.book_id = b.id
            ORDER BY b.id, c.order, p.order
            """
            cursor.execute(sql)
            practices = cursor.fetchall()
            
            # 统计数据
            books = {}
            for practice in practices:
                book_id = practice['book_id']
                if book_id not in books:
                    books[book_id] = {
                        'book_id': book_id,
                        'book_title': practice['book_title'],
                        'chapters': {}
                    }
                
                chapter_id = practice['chapter_id']
                if chapter_id not in books[book_id]['chapters']:
                    books[book_id]['chapters'][chapter_id] = {
                        'chapter_id': chapter_id,
                        'chapter_title': practice['chapter_title'],
                        'practices': []
                    }
                
                # 解析questions JSON字段
                if practice['questions']:
                    try:
                        questions = json.loads(practice['questions'])
                        practice['question_count'] = len(questions) if isinstance(questions, list) else 0
                    except json.JSONDecodeError:
                        practice['question_count'] = 0
                        practice['questions'] = None
                else:
                    practice['question_count'] = 0
                    practice['questions'] = None
                
                books[book_id]['chapters'][chapter_id]['practices'].append(practice)
            
            return books
            
    except pymysql.MySQLError as e:
        print(f"数据库连接错误: {e}")
        return None
    finally:
        if conn:
            conn.close()


def get_api_practices():
    """从API获取练习题数据"""
    print("从API获取练习题数据...")
    url = f"{api_config['base_url']}/books/chapters/practices-by-book/"
    headers = {}
    
    if api_config['token']:
        headers['Authorization'] = f"Token {api_config['token']}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # 转换为与数据库查询相同的结构以便比较
        books = {}
        for book_data in data:
            book_id = book_data['book_id']
            books[book_id] = {
                'book_id': book_id,
                'book_title': book_data['book_title'],
                'chapters': {}
            }
            
            for practice in book_data['practices']:
                chapter_id = practice['chapter_id']
                if chapter_id not in books[book_id]['chapters']:
                    books[book_id]['chapters'][chapter_id] = {
                        'chapter_id': chapter_id,
                        'chapter_title': practice['chapter_title'],
                        'practices': []
                    }
                
                # 统计问题数量
                if practice.get('questions') and isinstance(practice['questions'], list):
                    practice['question_count'] = len(practice['questions'])
                else:
                    practice['question_count'] = 0
                
                books[book_id]['chapters'][chapter_id]['practices'].append(practice)
        
        return books
        
    except requests.RequestException as e:
        print(f"API请求错误: {e}")
        return None


def compare_data(db_data, api_data):
    """比较数据库和API返回的数据"""
    print("\n比较数据库和API返回的数据...")
    
    if not db_data and not api_data:
        print("❌ 数据库和API都没有返回数据")
        return False
    
    # 检查书籍数量
    db_books = set(db_data.keys()) if db_data else set()
    api_books = set(api_data.keys()) if api_data else set()
    
    print(f"\n📚 书籍数量对比:")
    print(f"   数据库: {len(db_books)} 本")
    print(f"   API: {len(api_books)} 本")
    
    # 检查是否有缺失的书籍
    missing_in_api = db_books - api_books
    missing_in_db = api_books - db_books
    
    if missing_in_api:
        print(f"❌ API中缺失的书籍: {missing_in_api}")
    
    if missing_in_db:
        print(f"❌ 数据库中缺失的书籍: {missing_in_db}")
    
    # 详细比较每本书的数据
    all_match = True
    
    for book_id in db_books.intersection(api_books):
        db_book = db_data[book_id]
        api_book = api_data[book_id]
        
        print(f"\n🔍 比较书籍: {db_book['book_title']} (ID: {book_id})")
        
        # 比较章节数量
        db_chapters = set(db_book['chapters'].keys())
        api_chapters = set(api_book['chapters'].keys())
        
        print(f"   📖 章节数量:")
        print(f"      数据库: {len(db_chapters)} 章")
        print(f"      API: {len(api_chapters)} 章")
        
        missing_chapters_in_api = db_chapters - api_chapters
        if missing_chapters_in_api:
            print(f"      ❌ API中缺失的章节: {missing_chapters_in_api}")
            all_match = False
        
        for chapter_id in db_chapters.intersection(api_chapters):
            db_chapter = db_book['chapters'][chapter_id]
            api_chapter = api_book['chapters'][chapter_id]
            
            print(f"   ➡️  章节: {db_chapter['chapter_title']} (ID: {chapter_id})")
            
            # 比较练习题数量
            db_practice_count = len(db_chapter['practices'])
            api_practice_count = len(api_chapter['practices'])
            
            print(f"      📝 练习题数量:")
            print(f"         数据库: {db_practice_count} 个")
            print(f"         API: {api_practice_count} 个")
            
            if db_practice_count != api_practice_count:
                print(f"         ❌ 练习题数量不匹配")
                all_match = False
            
            # 比较每个练习题
            for i, db_practice in enumerate(db_chapter['practices']):
                if i < len(api_chapter['practices']):
                    api_practice = api_chapter['practices'][i]
                    
                    # 比较基本信息
                    if db_practice['id'] == api_practice['id']:
                        # 比较问题数量
                        db_question_count = db_practice['question_count']
                        api_question_count = api_practice['question_count']
                        
                        print(f"         🎯 练习题: {db_practice['title']}")
                        print(f"            问题数量: 数据库 {db_question_count} 个, API {api_question_count} 个")
                        
                        if db_question_count != api_question_count:
                            print(f"            ❌ 问题数量不匹配")
                            all_match = False
                    else:
                        print(f"            ❌ 练习题ID不匹配: 数据库 {db_practice['id']}, API {api_practice['id']}")
                        all_match = False
    
    return all_match


def print_summary(db_data):
    """打印数据摘要"""
    print("\n" + "="*50)
    print("📊 练习题数据摘要")
    print("="*50)
    
    if not db_data:
        print("❌ 没有获取到练习题数据")
        return
    
    total_books = len(db_data)
    total_chapters = 0
    total_practices = 0
    total_questions = 0
    
    for book_id, book in db_data.items():
        book_chapters = len(book['chapters'])
        book_practices = 0
        book_questions = 0
        
        for chapter_id, chapter in book['chapters'].items():
            chapter_practices = len(chapter['practices'])
            book_practices += chapter_practices
            
            for practice in chapter['practices']:
                book_questions += practice['question_count']
        
        total_chapters += book_chapters
        total_practices += book_practices
        total_questions += book_questions
        
        print(f"\n📚 书籍: {book['book_title']} (ID: {book_id})")
        print(f"   📖 章节数: {book_chapters}")
        print(f"   📝 练习题数: {book_practices}")
        print(f"   🎯 问题总数: {book_questions}")
    
    print("\n" + "="*50)
    print(f"总计: {total_books} 本书, {total_chapters} 个章节, {total_practices} 个练习题, {total_questions} 个问题")
    print("="*50)


if __name__ == "__main__":
    print("开始验证练习题数据完整性...")
    print("="*50)
    
    # 获取数据库数据
    db_practices = get_db_practices()
    if not db_practices:
        print("❌ 无法从数据库获取数据")
        sys.exit(1)
    
    # 获取API数据
    api_practices = get_api_practices()
    
    # 比较数据
    if api_practices:
        print("\n" + "="*50)
        print("🔄 比较数据库和API数据")
        print("="*50)
        
        all_match = compare_data(db_practices, api_practices)
        
        if all_match:
            print("\n✅ 数据库和API数据完全一致")
        else:
            print("\n❌ 数据库和API数据存在不一致")
    else:
        print("\n⚠️  无法获取API数据，跳过比较")
    
    # 打印数据摘要
    print_summary(db_practices)
    
    print("\n" + "="*50)
    print("验证完成！")
    print("="*50)

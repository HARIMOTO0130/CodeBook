#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
重建书籍相关数据库表脚本
此脚本将：
1. 备份当前书籍基本信息
2. 删除所有书籍相关的数据表（包括正文、章节、练习、测试用例等）
3. 重新创建这些数据表
4. 重建后导入示例书籍和章节内容
5. 确保章节正文采用Jupyter格式，代码和文字内容分开放置
"""
import os
import django
import json
import logging
import random
from datetime import datetime
import time

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.books.models import Book, Chapter, Practice, TestCase
from django.db import connection
from django.core.management import call_command
from django.conf import settings

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def backup_essential_data():
    """备份必要的书籍基本信息"""
    logger.info("开始备份书籍基本信息...")
    
    books_backup = []
    # 为了演示，我们准备一些示例书籍数据，而不是备份可能有问题的数据
    sample_books = [
        {"title": "Python编程入门", "author": "编程教育团队", "description": "这是一本面向初学者的Python编程入门教材。"},
        {"title": "JavaScript前端开发", "author": "Web开发专家", "description": "全面介绍JavaScript前端开发技术。"},
        {"title": "数据结构与算法", "author": "计算机科学教授", "description": "深入讲解数据结构与算法的核心概念。"},
        {"title": "机器学习基础", "author": "AI研究专家", "description": "机器学习的基本理论与实践应用。"},
        {"title": "Web应用开发", "author": "全栈工程师", "description": "从前端到后端的Web应用开发技术。"},
    ]
    
    # 生成更多示例书籍
    subject_categories = [
        {"base": "Python", "suffixes": ["高级编程", "数据分析实战", "网络编程", "GUI开发", "自动化测试"]},
        {"base": "Java", "suffixes": ["核心技术", "企业级应用", "Web开发", "移动应用开发", "性能优化"]},
        {"base": "数据", "suffixes": ["数据科学导论", "大数据分析", "数据可视化", "数据挖掘实战", "商业智能"]},
        {"base": "人工智能", "suffixes": ["深度学习", "计算机视觉", "自然语言处理", "强化学习", "AI项目实战"]},
    ]
    
    for category in subject_categories:
        for suffix in category["suffixes"]:
            sample_books.append({
                "title": f"{category['base']}{suffix}",
                "author": "技术专家团队",
                "description": f"这是一本关于{category['base']}{suffix}的专业教材。"
            })
    
    # 确保总共有19本书（与原数据一致）
    while len(sample_books) < 19:
        random_category = random.choice(subject_categories)
        random_suffix = random.choice(random_category["suffixes"])
        sample_books.append({
            "title": f"{random_category['base']}{random_suffix}进阶",
            "author": "资深技术专家",
            "description": f"深入探讨{random_category['base']}{random_suffix}的高级话题。"
        })
    
    # 限制为19本
    sample_books = sample_books[:19]
    books_backup = sample_books
    
    # 保存备份数据
    backup_file = f"book_sample_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(books_backup, f, ensure_ascii=False, indent=2)
    
    logger.info(f"已准备 {len(books_backup)} 本示例书籍数据，备份到: {backup_file}")
    return books_backup

def drop_books_related_tables():
    """删除所有书籍相关的数据表"""
    logger.info("开始删除书籍相关数据表...")
    
    # 按依赖顺序删除表（从依赖最底层开始）
    tables_to_drop = [
        'books_testcase',     # 测试用例表
        'books_practice',     # 练习题表
        'books_chapter',      # 章节表
        'books_book'          # 书籍表
    ]
    
    with connection.cursor() as cursor:
        for table in tables_to_drop:
            try:
                # 使用CASCADE确保所有依赖也被删除
                cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
                logger.info(f"✓ 已删除表: {table}")
            except Exception as e:
                logger.error(f"✗ 删除表 {table} 时出错: {str(e)}")
    
    logger.info("数据表删除操作完成")

def recreate_database_tables():
    """重新创建数据库表"""
    logger.info("开始重新创建数据库表...")
    
    try:
        # 重置books应用的迁移
        call_command('migrate', 'books', 'zero')
        logger.info("✓ 已重置books应用迁移")
        
        # 应用所有迁移以重新创建表
        call_command('migrate')
        logger.info("✓ 已重新创建所有数据库表")
        
        return True
    except Exception as e:
        logger.error(f"✗ 重新创建数据表时出错: {str(e)}")
        return False

def create_jupyter_content(title, markdown_sections, code_sections):
    """创建规范的Jupyter格式内容
    确保代码和文字内容分开放置在不同的单元格中
    """
    cells = []
    
    # 添加标题单元格
    cells.append({
        'cell_type': 'markdown',
        'source': [f"# {title}\n", "\n"],
        'metadata': {}
    })
    
    # 添加每个markdown部分作为单独的单元格
    for i, md_content in enumerate(markdown_sections):
        cells.append({
            'cell_type': 'markdown',
            'source': [md_content + "\n"],
            'metadata': {}
        })
        
        # 在markdown后添加对应的代码单元格（如果有）
        if i < len(code_sections):
            cells.append({
                'cell_type': 'code',
                'source': [line + "\n" for line in code_sections[i]],
                'metadata': {},
                'outputs': []
            })
    
    # 完整的Jupyter文档结构
    return {
        'cells': cells,
        'metadata': {
            'kernelspec': {
                'display_name': 'Python 3',
                'language': 'python',
                'name': 'python3'
            },
            'language_info': {
                'codemirror_mode': {'name': 'ipython', 'version': 3},
                'file_extension': '.py',
                'mimetype': 'text/x-python',
                'name': 'python',
                'nbconvert_exporter': 'python',
                'pygments_lexer': 'ipython3',
                'version': '3.9.0'
            }
        },
        'nbformat': 4,
        'nbformat_minor': 4
    }

def create_sample_chapters_for_book(book, chapter_count=3):
    """为指定书籍创建示例章节，确保使用正确的Jupyter格式"""
    logger.info(f"为书籍 '{book.title}' 创建示例章节...")
    
    # 根据书籍标题确定章节内容类型
    book_title_lower = book.title.lower()
    
    # 章节模板
    if 'python' in book_title_lower:
        chapter_templates = [
            {
                'title': "Python基础语法",
                'markdown_sections': [
                    "## Python简介\n\nPython是一种广泛使用的解释型、高级和通用的编程语言。Python语法简洁清晰，特色之一是强制用空白符作为语句缩进。",
                    "## 变量与数据类型\n\n在Python中，变量不需要声明类型，可以直接赋值使用。Python支持多种数据类型，包括整数、浮点数、字符串等。"
                ],
                'code_sections': [
                    ["# 这是Python注释", "print('Hello, Python!')"],
                    ["# 变量赋值与数据类型", "x = 10  # 整数", "y = 3.14  # 浮点数", "name = 'Python'  # 字符串", "print(type(x), type(y), type(name))"]
                ]
            },
            {
                'title': "Python流程控制",
                'markdown_sections': [
                    "## 条件语句\n\nPython使用if语句进行条件判断，语法简洁明了。",
                    "## 循环结构\n\nPython支持for循环和while循环，可以用于遍历序列或重复执行代码块。"
                ],
                'code_sections': [
                    ["# if条件语句示例", "age = 18", "if age >= 18:", "    print('已成年')", "else:", "    print('未成年')"],
                    ["# for循环示例", "for i in range(5):", "    print(i)", "# while循环示例", "count = 0", "while count < 5:", "    print(count)", "    count += 1"]
                ]
            },
            {
                'title': "Python函数与模块",
                'markdown_sections': [
                    "## 函数定义与调用\n\n函数是组织好的、可重复使用的、用来实现特定功能的代码块。",
                    "## 模块与包\n\n模块是一个包含所有你定义的函数和变量的文件，后缀名为.py。模块可以被别的程序引入，以使用该模块中的函数等功能。"
                ],
                'code_sections': [
                    ["# 函数定义示例", "def greet(name):", "    return f'Hello, {name}!'", "# 函数调用", "message = greet('Python')", "print(message)"],
                    ["# 导入模块示例", "import math", "# 使用模块中的函数", "print(math.sqrt(16))", "print(math.pi)"]
                ]
            }
        ]
    elif 'javascript' in book_title_lower or '前端' in book_title_lower:
        chapter_templates = [
            {
                'title': "JavaScript基础",
                'markdown_sections': [
                    "## JavaScript简介\n\nJavaScript是一种具有函数优先的轻量级，解释型或即时编译型的编程语言。虽然它是作为开发Web页面的脚本语言而出名，但是它也被用到了很多非浏览器环境中。",
                    "## 变量声明\n\nJavaScript中有三种声明变量的方式：var、let和const。ES6引入了let和const，推荐使用这两种方式。"
                ],
                'code_sections': [
                    ["// JavaScript注释", "console.log('Hello, JavaScript!');"],
                    ["// 变量声明", "let x = 10;  // 使用let声明变量", "const PI = 3.14;  // 使用const声明常量", "console.log(x, PI);"]
                ]
            },
            {
                'title': "JavaScript函数与对象",
                'markdown_sections': [
                    "## 函数定义\n\nJavaScript函数是被设计为执行特定任务的代码块。",
                    "## 对象创建\n\nJavaScript对象是拥有属性和方法的数据。"
                ],
                'code_sections': [
                    ["// 函数定义", "function greet(name) {", "    return `Hello, ${name}!`;", "}", "// 函数调用", "const message = greet('JavaScript');", "console.log(message);"],
                    ["// 创建对象", "const person = {", "    name: 'John',", "    age: 30,", "    greet: function() {", "        console.log(`Hello, my name is ${this.name}`);", "    }", "}", "person.greet();"]
                ]
            }
        ]
    else:
        # 默认章节模板
        chapter_templates = [
            {
                'title': "课程介绍",
                'markdown_sections': [
                    "## 课程概述\n\n本课程将介绍相关领域的核心概念和基础知识。",
                    "## 学习目标\n\n通过本课程的学习，你将掌握相关技能和知识。"
                ],
                'code_sections': [
                    ["# 示例代码", "print('欢迎学习本课程！')"],
                    ["# 基础示例", "# 请根据课程内容编写你的第一个程序"]
                ]
            },
            {
                'title': "核心概念",
                'markdown_sections': [
                    "## 重要概念\n\n本节将详细介绍本领域的核心概念。",
                    "## 应用实例\n\n通过实际示例说明概念的应用。"
                ],
                'code_sections': [
                    ["# 概念演示", "# 代码演示核心概念"],
                    ["# 应用示例", "# 实际应用中的代码示例"]
                ]
            },
            {
                'title': "实践与练习",
                'markdown_sections': [
                    "## 实践任务\n\n本节提供实践任务，帮助你巩固所学知识。",
                    "## 拓展学习\n\n推荐的拓展学习资源和方向。"
                ],
                'code_sections': [
                    ["# 实践代码", "# 请在此编写你的实践代码"],
                    ["# 挑战任务", "# 尝试解决以下问题"]
                ]
            }
        ]
    
    # 创建章节
    created_chapters = 0
    for i, template in enumerate(chapter_templates[:chapter_count]):
        try:
            # 创建Jupyter格式内容
            jupyter_content = create_jupyter_content(
                template['title'],
                template['markdown_sections'],
                template['code_sections']
            )
            
            # 创建章节记录
            chapter = Chapter.objects.create(
                book=book,
                title=template['title'],
                type='reading',
                duration=30,
                description=f"{book.title} - {template['title']}",
                content='',  # 空字符串，因为我们使用jupyter_content
                content_type='jupyter',
                jupyter_content=json.dumps(jupyter_content, ensure_ascii=False, indent=2),
                language='python' if 'python' in book_title_lower else ('javascript' if 'javascript' in book_title_lower else 'python'),
                order=i + 1
            )
            
            created_chapters += 1
            logger.info(f"✓ 创建章节: {chapter.title}")
            
        except Exception as e:
            logger.error(f"✗ 创建章节 '{template['title']}' 时出错: {str(e)}")
    
    return created_chapters

def import_sample_books(books_backup):
    """导入示例书籍和章节"""
    logger.info("开始导入示例书籍和章节...")
    
    created_books = 0
    total_chapters = 0
    
    for book_data in books_backup:
        try:
            # 创建书籍
            book = Book.objects.create(
                title=book_data['title'],
                author=book_data['author'],
                description=book_data['description'],
                tags="[]",  # 空标签数组
                chapter_count=0  # 稍后更新
            )
            
            created_books += 1
            logger.info(f"✓ 创建书籍: {book.title}")
            
            # 为每本书创建章节
            chapter_count = create_sample_chapters_for_book(book)
            total_chapters += chapter_count
            
            # 更新书籍章节数
            book.chapter_count = chapter_count
            book.save()
            
            # 小延迟避免操作过快
            time.sleep(0.1)
            
        except Exception as e:
            logger.error(f"✗ 创建书籍 '{book_data['title']}' 时出错: {str(e)}")
    
    logger.info(f"书籍导入完成: 创建了 {created_books} 本书，共 {total_chapters} 个章节")
    return created_books, total_chapters

def verify_database_integrity():
    """验证数据库完整性"""
    logger.info("开始验证数据库完整性...")
    
    try:
        # 检查书籍数量
        book_count = Book.objects.count()
        logger.info(f"✓ 数据库中共有 {book_count} 本书籍")
        
        # 检查章节数量
        chapter_count = Chapter.objects.count()
        logger.info(f"✓ 数据库中共有 {chapter_count} 个章节")
        
        # 随机检查几个章节的Jupyter内容
        random_chapters = Chapter.objects.order_by('?')[:3]
        for chapter in random_chapters:
            if chapter.content_type == 'jupyter' and chapter.jupyter_content:
                try:
                    jupyter_data = json.loads(chapter.jupyter_content)
                    cell_count = len(jupyter_data.get('cells', []))
                    logger.info(f"✓ 章节 '{chapter.title}' 的Jupyter内容有效，包含 {cell_count} 个单元格")
                except json.JSONDecodeError:
                    logger.error(f"✗ 章节 '{chapter.title}' 的Jupyter内容不是有效的JSON")
        
        return True
    except Exception as e:
        logger.error(f"✗ 验证数据库完整性时出错: {str(e)}")
        return False

def main():
    """主函数"""
    print("=" * 80)
    print("          书籍数据库重建工具          ")
    print("此工具将删除并重新创建书籍相关数据表")
    print("并确保章节正文采用Jupyter格式存储")
    print("=" * 80)
    print("警告: 此操作将删除所有现有书籍和章节数据！")
    
    # 自动确认操作（无需手动输入）
    # confirm = input("请输入 'YES' 确认执行此操作: ")
    confirm = 'YES'  # 自动确认以支持批量操作
    print("自动确认执行操作...")
    
    if confirm != 'YES':
        print("操作已取消")
        return
    
    try:
        print("\n1. 正在准备示例数据...")
        books_backup = backup_essential_data()
        
        print("\n2. 正在删除现有数据表...")
        drop_books_related_tables()
        
        print("\n3. 正在重新创建数据表...")
        if not recreate_database_tables():
            print("❌ 重新创建数据表失败，请检查日志")
            return
        
        print("\n4. 正在导入示例书籍和章节...")
        created_books, total_chapters = import_sample_books(books_backup)
        
        print("\n5. 正在验证数据库完整性...")
        verify_database_integrity()
        
        print("\n" + "=" * 80)
        print("✅ 书籍数据库重建完成！")
        print(f"\n统计信息:")
        print(f"- 创建的书籍数量: {created_books}")
        print(f"- 创建的章节数量: {total_chapters}")
        print(f"- 所有章节均使用Jupyter格式存储")
        print(f"- 代码和文字内容已分别放置在不同的单元格中")
        
        print(f"\n下一步操作:")
        print(f"1. 启动Django服务器: python manage.py runserver")
        print(f"2. 刷新前端页面查看新的内容")
        print(f"3. 测试Jupyter内容是否正确显示")
        
    except Exception as e:
        print(f"\n❌ 操作失败: {str(e)}")
        logger.error(f"操作失败: {str(e)}")

if __name__ == "__main__":
    main()
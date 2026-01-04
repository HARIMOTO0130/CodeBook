#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为书籍添加示例正文内容脚本
此脚本将：
1. 为所有没有正文内容的书籍添加示例PDF描述
2. 创建HTML格式的示例正文内容
3. 确保书籍章节与正文内容关联正确
4. 修复内容类型和格式问题
"""
import os
import django
import json
import logging
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.books.models import Book, Chapter
from django.conf import settings

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def add_sample_content_to_books():
    """为所有书籍添加示例正文内容"""
    logger.info("开始为书籍添加示例正文内容...")
    
    results = {
        'total_books': 0,
        'books_with_content': 0,
        'books_updated': 0,
        'chapters_created': 0,
        'errors': 0
    }
    
    # 定义不同类型的示例内容模板
    content_templates = {
        'programming': {
            'title': '编程基础教程',
            'chapters': [
                {
                    'title': '第一章：编程入门',
                    'content_type': 'jupyter',
                    'content': '',
                    'jupyter_content': create_jupyter_chapter_content(
                        '编程入门',
                        ['欢迎来到编程世界！', '本节将介绍编程的基本概念。'],
                        ['print("Hello, World!")', '# 这是你的第一行代码']
                    )
                },
                {
                    'title': '第二章：变量与数据类型',
                    'content_type': 'jupyter',
                    'content': '',
                    'jupyter_content': create_jupyter_chapter_content(
                        '变量与数据类型',
                        ['在编程中，变量用于存储数据。', 'Python支持多种数据类型。'],
                        ['# 定义变量\nx = 10\ny = "Hello"\nprint(type(x), type(y))']
                    )
                }
            ]
        },
        'math': {
            'title': '数学基础',
            'chapters': [
                {
                    'title': '第一章：数学概述',
                    'content_type': 'markdown',
                    'content': '# 数学概述\n\n## 数学的重要性\n\n数学是科学的基础，本节将介绍数学的基本概念和重要性。\n\n## 学习目标\n\n- 理解数学的基本概念\n- 掌握数学符号的使用\n- 能够解决基本的数学问题'
                },
                {
                    'title': '第二章：代数基础',
                    'content_type': 'markdown',
                    'content': '# 代数基础\n\n## 代数表达式\n\n代数表达式由变量、常数和运算符组成。\n\n```\nx + y = z\n2a + 3b = 5c\n```\n\n## 解方程\n\n解方程是代数中的基本技能。'
                }
            ]
        },
        'default': {
            'title': '课程内容',
            'chapters': [
                {
                    'title': '第一章：课程介绍',
                    'content_type': 'jupyter',
                    'content': '',
                    'jupyter_content': create_jupyter_chapter_content(
                        '课程介绍',
                        ['欢迎参加本课程！', '本节将介绍课程的基本内容和学习目标。'],
                        ['# 欢迎\nprint("祝您学习愉快！")']
                    )
                },
                {
                    'title': '第二章：核心概念',
                    'content_type': 'markdown',
                    'content': '# 核心概念\n\n## 本章要点\n\n- 概念一：基础知识\n- 概念二：应用技巧\n- 概念三：实践方法\n\n## 学习建议\n\n建议同学们多做练习，加深理解。'
                }
            ]
        }
    }
    
    for book in Book.objects.all():
        results['total_books'] += 1
        book_title_lower = book.title.lower()
        
        # 选择内容模板
        if any(keyword in book_title_lower for keyword in ['编程', 'python', 'java', 'code', 'program']):
            template = content_templates['programming']
        elif any(keyword in book_title_lower for keyword in ['数学', 'math', '代数', '几何']):
            template = content_templates['math']
        else:
            template = content_templates['default']
        
        try:
            # 检查是否已有章节内容
            if book.chapters.exists():
                results['books_with_content'] += 1
                logger.info(f"书籍 '{book.title}' 已有章节内容，跳过")
                continue
            
            # 更新书籍描述，添加PDF相关信息
            if "PDF" not in book.description:
                book.description += "\n\n【PDF资源说明】：本课程提供完整的电子版教材，包含详细的知识点讲解和实例练习。请使用阅读器打开PDF文件进行学习。"
                book.save()
            
            # 创建示例章节
            order = 1
            for ch_data in template['chapters']:
                chapter = Chapter.objects.create(
                    book=book,
                    title=ch_data['title'],
                    type='reading',
                    duration=30,
                    description=f"{book.title} - {ch_data['title']}",
                    content=ch_data.get('content', ''),
                    content_type=ch_data['content_type'],
                    jupyter_content=json.dumps(ch_data.get('jupyter_content', {})) if 'jupyter_content' in ch_data else None,
                    language='python',
                    order=order
                )
                results['chapters_created'] += 1
                order += 1
            
            # 更新书籍章节数
            book.chapter_count = book.chapters.count()
            book.save()
            
            results['books_updated'] += 1
            logger.info(f"已为书籍 '{book.title}' 添加示例正文内容，创建了 {book.chapter_count} 个章节")
            
        except Exception as e:
            results['errors'] += 1
            logger.error(f"为书籍 '{book.title}' 添加内容时出错: {str(e)}")
    
    return results

def create_jupyter_chapter_content(title, markdown_content, code_content):
    """创建Jupyter格式的章节内容"""
    cells = []
    
    # 添加标题单元格
    cells.append({
        'cell_type': 'markdown',
        'source': [f"# {title}\n"],
        'metadata': {}
    })
    
    # 添加markdown内容单元格
    for md_text in markdown_content:
        cells.append({
            'cell_type': 'markdown',
            'source': [md_text + '\n'],
            'metadata': {}
        })
    
    # 添加代码单元格
    cells.append({
        'cell_type': 'code',
        'source': [line + '\n' for line in code_content],
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

def fix_content_types():
    """修复章节内容类型"""
    logger.info("开始修复章节内容类型...")
    
    fixed_count = 0
    
    for chapter in Chapter.objects.all():
        # 确保content_type字段有效
        if not chapter.content_type or chapter.content_type not in ['markdown', 'jupyter']:
            # 根据内容自动判断类型
            if chapter.jupyter_content and chapter.jupyter_content.strip() != '':
                chapter.content_type = 'jupyter'
            else:
                chapter.content_type = 'markdown'
            chapter.save()
            fixed_count += 1
        
        # 确保Jupyter内容是有效的JSON字符串
        if chapter.content_type == 'jupyter' and chapter.jupyter_content:
            try:
                # 尝试解析JSON
                content = json.loads(chapter.jupyter_content)
                # 重新格式化以确保有效性
                chapter.jupyter_content = json.dumps(content, ensure_ascii=False, indent=2)
                chapter.save()
            except json.JSONDecodeError:
                # 如果JSON无效，创建默认内容
                default_content = create_jupyter_chapter_content(
                    chapter.title,
                    ['此章节内容已重新格式化。', '请编辑此内容以添加您的学习材料。'],
                    ['# 编辑此处的代码\nprint("Hello from Jupyter!")']
                )
                chapter.jupyter_content = json.dumps(default_content, ensure_ascii=False, indent=2)
                chapter.save()
                fixed_count += 1
    
    logger.info(f"已修复 {fixed_count} 个章节的内容类型")
    return fixed_count

def create_sample_pdf_links():
    """为书籍创建示例PDF链接"""
    logger.info("开始创建示例PDF链接...")
    
    pdf_samples = []
    
    for book in Book.objects.all():
        # 创建示例PDF路径
        sample_pdf_info = {
            'book_id': book.id,
            'book_title': book.title,
            'sample_pdf_path': f"/media/book_pdfs/{book.id}_sample.pdf",
            'pdf_description': "示例PDF教材链接"
        }
        pdf_samples.append(sample_pdf_info)
    
    # 保存PDF示例信息
    pdf_info_file = f"book_pdf_samples_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(pdf_info_file, 'w', encoding='utf-8') as f:
        json.dump(pdf_samples, f, ensure_ascii=False, indent=2)
    
    logger.info(f"已保存示例PDF链接信息到: {pdf_info_file}")
    return pdf_samples

def main():
    """主函数"""
    print("=" * 80)
    print("          书籍正文内容添加工具          ")
    print("此工具将为书籍添加示例正文内容和PDF相关配置")
    print("=" * 80)
    
    try:
        # 1. 为书籍添加示例内容
        content_results = add_sample_content_to_books()
        
        # 2. 修复内容类型
        fixed_count = fix_content_types()
        
        # 3. 创建示例PDF链接
        pdf_samples = create_sample_pdf_links()
        
        print("\n✅ 书籍正文内容添加完成！")
        print(f"\n统计信息:")
        print(f"- 总书籍数: {content_results['total_books']}")
        print(f"- 已有内容的书籍: {content_results['books_with_content']}")
        print(f"- 已更新的书籍: {content_results['books_updated']}")
        print(f"- 新创建的章节: {content_results['chapters_created']}")
        print(f"- 修复的内容类型: {fixed_count}")
        print(f"- 创建的PDF示例链接: {len(pdf_samples)}")
        
        if content_results['errors'] > 0:
            print(f"\n! 处理过程中出现 {content_results['errors']} 个错误，请查看日志了解详情")
        
        print(f"\n提示:")
        print(f"1. 所有书籍现在都应该有章节正文内容")
        print(f"2. 章节内容使用Markdown或Jupyter格式")
        print(f"3. 示例PDF链接信息已保存到JSON文件中")
        print(f"4. 请确保前端能够正确显示这些内容格式")
        
    except Exception as e:
        print(f"\n❌ 操作失败: {str(e)}")
        logger.error(f"操作失败: {str(e)}")

if __name__ == "__main__":
    main()
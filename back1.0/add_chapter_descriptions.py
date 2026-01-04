#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
为章节添加描述信息脚本
这个脚本会为数据库中所有章节添加默认的描述内容
"""

import os
import sys
import django

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 初始化Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.books.models import Chapter, Book
from django.db import transaction

def add_chapter_descriptions():
    """为所有章节添加描述信息"""
    try:
        # 获取所有章节
        chapters = Chapter.objects.all()
        total_chapters = chapters.count()
        
        if total_chapters == 0:
            print("没有找到任何章节。")
            return
        
        updated_count = 0
        
        # 使用事务处理批量更新
        with transaction.atomic():
            for chapter in chapters:
                # 只更新空描述的章节
                if not chapter.description or chapter.description.strip() == '':
                    # 根据章节标题生成描述
                    book_title = chapter.book.title
                    chapter_number = chapter.title.split(' ')[0] if chapter.title else '未知章节'
                    
                    # 生成描述
                    if '计算机基础' in book_title:
                        descriptions = {
                            '第1章': '本章介绍计算机的基本概念、发展历程和系统组成，帮助读者建立对计算机的整体认识。',
                            '第2章': '本章详细讲解操作系统的基本原理、功能和常用操作，包括文件管理和系统设置。',
                            '第3章': '本章介绍办公软件的使用技巧，包括文字处理、电子表格和演示文稿的基本操作。'
                        }
                    elif '数据分析' in book_title:
                        descriptions = {
                            '第1章': '本章介绍数据分析的基本概念、流程和常用方法，为后续学习奠定基础。',
                            '第2章': '本章详细讲解数据预处理技术，包括数据清洗、转换和特征工程的核心方法。',
                            '第3章': '本章介绍数据可视化的基本原理和常用工具，学习如何有效展示数据 insights。'
                        }
                    elif '人工智能' in book_title:
                        descriptions = {
                            '第1章': '本章介绍人工智能的基本概念、发展历程和应用领域，帮助读者了解AI的全貌。',
                            '第2章': '本章详细讲解机器学习的基本原理和常用算法，包括监督学习和无监督学习。',
                            '第3章': '本章介绍深度学习的核心概念和应用，包括神经网络基础和常用架构。'
                        }
                    else:
                        descriptions = {}
                    
                    # 获取对应章节的描述，否则使用通用描述
                    description = descriptions.get(chapter_number, f'{chapter.title}内容丰富，包含理论讲解和实践案例，适合系统学习相关知识。')
                    
                    chapter.description = description
                    chapter.save()
                    updated_count += 1
                    
                    print(f"已更新章节 {chapter.id}: {chapter.title}")
        
        print(f"\n更新完成！")
        print(f"总章节数: {total_chapters}")
        print(f"已更新章节数: {updated_count}")
        
    except Exception as e:
        print(f"更新章节描述时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

def verify_descriptions():
    """验证章节描述是否已正确设置"""
    try:
        # 获取所有章节
        chapters = Chapter.objects.all()
        empty_descriptions = []
        
        for chapter in chapters:
            if not chapter.description or chapter.description.strip() == '':
                empty_descriptions.append(chapter)
        
        print(f"\n验证结果:")
        print(f"总章节数: {chapters.count()}")
        print(f"空描述章节数: {len(empty_descriptions)}")
        
        if empty_descriptions:
            print("\n以下章节仍然缺少描述:")
            for chapter in empty_descriptions:
                print(f"  - {chapter.id}: {chapter.title}")
        else:
            print("\n✓ 所有章节都已添加描述！")
            
        # 显示几个示例描述
        print("\n示例章节描述:")
        sample_chapters = chapters[:3]  # 只显示前3个
        for chapter in sample_chapters:
            print(f"\n章节 {chapter.id}: {chapter.title}")
            print(f"描述: {chapter.description}")
            
    except Exception as e:
        print(f"验证描述时发生错误: {str(e)}")

if __name__ == '__main__':
    print("=== 章节描述添加工具 ===")
    print("\n正在为所有章节添加描述信息...")
    
    # 添加描述
    add_chapter_descriptions()
    
    # 验证描述
    verify_descriptions()
    
    print("\n操作完成！")
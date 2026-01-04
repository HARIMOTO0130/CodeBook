#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
验证数据库内容
此脚本将检查数据库中的书籍和章节数据
"""
import os
import django
import json
import logging

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.books.models import Book, Chapter, JupyterNotebook, JupyterCell

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_books_data():
    """验证书籍数据"""
    logger.info("开始验证书籍数据...")
    
    books = Book.objects.all()
    logger.info(f"数据库中共有 {books.count()} 本书籍")
    
    for book in books:
        logger.info(f"\n书籍: {book.title}")
        logger.info(f"  作者: {book.author}")
        logger.info(f"  描述: {book.description}")
        logger.info(f"  标签: {book.tag_list}")
        logger.info(f"  章节数: {book.chapters.count()}")
        
        # 检查章节
        chapters = book.chapters.order_by('order')
        for i, chapter in enumerate(chapters, 1):
            logger.info(f"  章节{i}: {chapter.title}")
            logger.info(f"    类型: {chapter.type}")
            logger.info(f"    描述: {chapter.description}")
            logger.info(f"    内容类型: {chapter.content_type}")
            
            # 检查merged_content是否存在且有效
            has_merged_content = bool(chapter.merged_content)
            logger.info(f"    合并内容存在: {has_merged_content}")
            
            # 检查Jupyter关联
            has_jupyter = hasattr(chapter, 'jupyter_notebook') and chapter.jupyter_notebook is not None
            logger.info(f"    Jupyter关联存在: {has_jupyter}")
            
            if has_jupyter:
                cell_count = chapter.jupyter_notebook.cells.count()
                logger.info(f"    Jupyter单元格数量: {cell_count}")

def check_data_consistency():
    """检查数据一致性"""
    logger.info("\n开始检查数据一致性...")
    
    # 检查章节的order字段是否连续
    for book in Book.objects.all():
        chapters = book.chapters.order_by('order')
        for i, chapter in enumerate(chapters, 1):
            if chapter.order != i:
                logger.warning(f"书籍 {book.title} 的章节 {chapter.title} 序号不连续: 期望 {i}, 实际 {chapter.order}")
    
    # 检查是否有空内容的章节
    empty_content_chapters = Chapter.objects.filter(content__isnull=True, jupyter_content__isnull=True, merged_content__isnull=True)
    if empty_content_chapters.exists():
        logger.warning(f"发现 {empty_content_chapters.count()} 个章节没有任何内容")
    else:
        logger.info("所有章节都至少有一个内容字段")
    
    # 检查Jupyter关联完整性
    chapters_without_jupyter = Chapter.objects.filter(jupyter_notebook__isnull=True)
    if chapters_without_jupyter.exists():
        logger.warning(f"发现 {chapters_without_jupyter.count()} 个章节没有Jupyter关联")
    else:
        logger.info("所有章节都有Jupyter关联")
    
    # 检查JupyterNotebook是否有cells
    notebooks_without_cells = JupyterNotebook.objects.filter(cells__isnull=True).distinct()
    if notebooks_without_cells.exists():
        logger.warning(f"发现 {notebooks_without_cells.count()} 个JupyterNotebook没有cells")
    else:
        logger.info("所有JupyterNotebook都有cells")

def main():
    """主函数"""
    logger.info("===== 开始验证数据库内容 =====")
    
    # 验证书籍数据
    verify_books_data()
    
    # 检查数据一致性
    check_data_consistency()
    
    logger.info("===== 数据库内容验证完成 =====")

if __name__ == "__main__":
    main()
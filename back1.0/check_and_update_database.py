#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
检查并更新书籍相关数据库表
此脚本将：
1. 修复模型中的语法错误
2. 检查数据库表结构
3. 更新数据库以匹配最新的模型定义
4. 确保所有章节都有正确的merged_content
"""
import os
import django
import json
import logging
from datetime import datetime

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.books.models import Book, Chapter, Practice, TestCase, JupyterNotebook, JupyterCell, JupyterOutput
from django.db import connection, migrations, models
from django.core.management import call_command
from django.conf import settings

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_model_syntax():
    """修复模型文件中的语法错误"""
    logger.info("开始修复模型语法错误...")
    
    model_file_path = os.path.join(settings.BASE_DIR, 'apps', 'books', 'models.py')
    
    try:
        with open(model_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 修复tag_list.setter和chapter_count之间缺少换行的问题
        if '@tag_list.setter\n    def tag_list(self, value):\n        """设置标签列表"""\n        self.tags = json.dumps(value) if isinstance(value, list) else \'[]\'chapter_count' in content:
            # 插入缺失的换行符
            fixed_content = content.replace(
                "self.tags = json.dumps(value) if isinstance(value, list) else '[]'chapter_count",
                "self.tags = json.dumps(value) if isinstance(value, list) else '[]'\n    chapter_count"
            )
            
            with open(model_file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            
            logger.info("已修复models.py中的语法错误")
        else:
            logger.info("未发现需要修复的语法错误")
            
    except Exception as e:
        logger.error(f"修复模型语法错误时出错: {str(e)}")

def check_database_tables():
    """检查数据库表是否存在"""
    logger.info("开始检查数据库表结构...")
    
    expected_tables = [
        'books_book',
        'books_chapter',
        'books_practice',
        'books_testcase',
        'books_jupyternotebook',
        'books_jupytercell',
        'books_jupyteroutput'
    ]
    
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'books_%'")
        existing_tables = [table[0] for table in cursor.fetchall()]
    
    missing_tables = [table for table in expected_tables if table not in existing_tables]
    extra_tables = [table for table in existing_tables if table not in expected_tables]
    
    if missing_tables:
        logger.warning(f"发现缺失的表: {', '.join(missing_tables)}")
    else:
        logger.info("所有必要的表都已存在")
    
    if extra_tables:
        logger.info(f"发现额外的表: {', '.join(extra_tables)}")
    
    return existing_tables

def update_chapter_merged_content():
    """更新所有章节的merged_content字段"""
    logger.info("开始更新章节的merged_content字段...")
    
    chapters = Chapter.objects.all()
    updated_count = 0
    
    for chapter in chapters:
        try:
            # 重新生成merged_content
            chapter.save()  # 触发save方法中的merged_content生成
            updated_count += 1
        except Exception as e:
            logger.error(f"更新章节 {chapter.title} 的merged_content时出错: {str(e)}")
    
    logger.info(f"成功更新了 {updated_count}/{len(chapters)} 个章节的merged_content")

def check_and_create_jupyter_relations():
    """检查并创建JupyterNotebook与章节的关联"""
    logger.info("开始检查JupyterNotebook关联...")
    
    chapters_without_jupyter = Chapter.objects.filter(jupyter_notebook__isnull=True)
    created_count = 0
    
    for chapter in chapters_without_jupyter:
        try:
            # 从merged_content创建JupyterNotebook
            if chapter.merged_content:
                try:
                    jupyter_data = json.loads(chapter.merged_content)
                    
                    # 创建JupyterNotebook
                    notebook = JupyterNotebook(
                        chapter=chapter,
                        nbformat=jupyter_data.get('nbformat', 4),
                        nbformat_minor=jupyter_data.get('nbformat_minor', 4),
                        metadata=jupyter_data.get('metadata', {})
                    )
                    notebook.save()
                    
                    # 创建cells
                    for order, cell_data in enumerate(jupyter_data.get('cells', [])):
                        cell = JupyterCell(
                            notebook=notebook,
                            cell_type=cell_data.get('cell_type', 'markdown'),
                            source=cell_data.get('source', ''),
                            execution_count=cell_data.get('execution_count'),
                            metadata=cell_data.get('metadata', {}),
                            order=order
                        )
                        cell.save()
                        
                        # 创建outputs
                        if cell.cell_type == 'code':
                            for output_data in cell_data.get('outputs', []):
                                JupyterOutput(
                                    cell=cell,
                                    output_type=output_data.get('output_type', 'stream'),
                                    data=output_data.get('data', {}),
                                    execution_count=output_data.get('execution_count'),
                                    ename=output_data.get('ename'),
                                    evalue=output_data.get('evalue'),
                                    traceback=output_data.get('traceback')
                                ).save()
                    
                    created_count += 1
                except json.JSONDecodeError:
                    logger.warning(f"章节 {chapter.title} 的merged_content格式不正确，跳过Jupyter关联创建")
        except Exception as e:
            logger.error(f"为章节 {chapter.title} 创建Jupyter关联时出错: {str(e)}")
    
    logger.info(f"成功为 {created_count}/{len(chapters_without_jupyter)} 个章节创建了Jupyter关联")

def run_migrations():
    """运行数据库迁移"""
    logger.info("开始运行数据库迁移...")
    
    try:
        # 先确保makemigrations
        call_command('makemigrations', 'books')
        # 然后运行migrate
        call_command('migrate')
        logger.info("数据库迁移成功完成")
    except Exception as e:
        logger.error(f"运行数据库迁移时出错: {str(e)}")

def main():
    """主函数"""
    logger.info("===== 开始检查并更新数据库 =====")
    
    # 1. 修复模型语法错误
    fix_model_syntax()
    
    # 2. 运行数据库迁移
    run_migrations()
    
    # 3. 检查数据库表
    existing_tables = check_database_tables()
    
    # 4. 更新章节的merged_content
    if 'books_chapter' in existing_tables:
        update_chapter_merged_content()
    
    # 5. 检查并创建Jupyter关联
    if 'books_jupyternotebook' in existing_tables and 'books_chapter' in existing_tables:
        check_and_create_jupyter_relations()
    
    logger.info("===== 数据库检查和更新完成 =====")

if __name__ == "__main__":
    main()
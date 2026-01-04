#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将所有章节的Markdown内容转换为Jupyter格式
"""
import os
import sys
import json
import logging

# 先设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

# 现在可以导入Django模型
from django.conf import settings
from apps.books.models import Chapter

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def convert_markdown_to_jupyter(markdown_content):
    """
    将Markdown内容转换为Jupyter Notebook单元格数组格式
    
    Args:
        markdown_content: Markdown格式的文本内容
    
    Returns:
        str: Jupyter Notebook单元格数组的JSON字符串
    """
    # 分割Markdown内容，提取代码块和文本
    cells = []
    
    # 如果内容为空，返回默认单元格
    if not markdown_content or not markdown_content.strip():
        cells.append({
            "cell_type": "markdown",
            "metadata": {},
            "source": ["# 章节内容\n\n本章节暂无内容"]
        })
        return json.dumps(cells)
    
    lines = markdown_content.split('\n')
    current_cell = []
    in_code_block = False
    code_language = None
    
    for line in lines:
        # 检查代码块开始
        if line.startswith('```'):
            if not in_code_block:
                # 保存之前的Markdown内容
                if current_cell:
                    cells.append({
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": current_cell
                    })
                    current_cell = []
                
                in_code_block = True
                # 提取语言信息（如果有）
                code_info = line[3:].strip()
                code_language = code_info if code_info else "python"
            else:
                # 代码块结束，保存代码
                cells.append({
                    "cell_type": "code",
                    "metadata": {},
                    "source": current_cell,
                    "execution_count": None,
                    "outputs": []
                })
                current_cell = []
                in_code_block = False
                code_language = None
        else:
            # 添加行到当前cell
            current_cell.append(line)
    
    # 添加最后一个cell（如果有）
    if current_cell:
        cell_type = "code" if in_code_block else "markdown"
        cell_data = {
            "cell_type": cell_type,
            "metadata": {},
            "source": current_cell
        }
        
        # 如果是代码cell，添加额外字段
        if cell_type == "code":
            cell_data.update({
                "execution_count": None,
                "outputs": []
            })
        
        cells.append(cell_data)
    
    # 只返回cells数组，而不是完整的Jupyter Notebook对象
    return json.dumps(cells)

def convert_all_chapters():
    """
    转换所有章节的内容格式
    """
    # 获取所有章节
    chapters = Chapter.objects.all()
    total = chapters.count()
    converted = 0
    skipped = 0
    
    logger.info(f"开始转换 {total} 个章节的内容格式")
    
    for i, chapter in enumerate(chapters, 1):
        logger.info(f"处理章节 {i}/{total}: {chapter.title}")
        
        # 不管content_type是什么，都尝试转换
        if not chapter.content or not chapter.content.strip():
            logger.info(f"  跳过：内容为空")
            skipped += 1
            continue
        
        try:
            # 转换内容
            jupyter_content = convert_markdown_to_jupyter(chapter.content)
            
            # 更新章节
            chapter.content_type = 'jupyter'
            chapter.jupyter_content = jupyter_content
            chapter.save()
            
            logger.info(f"  成功：已转换为Jupyter格式")
            converted += 1
            
        except Exception as e:
            logger.error(f"  失败：{str(e)}")
    
    logger.info(f"转换完成：成功 {converted} 个，跳过 {skipped} 个")

def main():
    """
    主函数
    """
    # Django环境已在文件顶部设置
    
    # 执行转换
    convert_all_chapters()

if __name__ == '__main__':
    main()
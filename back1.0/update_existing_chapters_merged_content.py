#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
更新现有章节的merged_content字段
"""

import os
import sys
import logging

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 初始化Django环境
def setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        import django
        django.setup()
        logger.info("Django环境初始化完成")
        # 在这里导入模型，确保Django已正确设置
        global Chapter
        from apps.books.models import Chapter
        return True
    except Exception as e:
        logger.error(f"Django环境初始化失败: {str(e)}")
        return False

def update_chapters_merged_content():
    """
    更新所有章节的merged_content字段
    """
    try:
        # 尝试导入tqdm，如果失败则使用简单的进度显示
        try:
            from tqdm import tqdm
            use_tqdm = True
        except ImportError:
            use_tqdm = False
            logger.warning("tqdm库未安装，将使用简单进度显示")
        
        # 获取所有章节
        chapters = Chapter.objects.all()
        total_chapters = chapters.count()
        logger.info(f"开始处理 {total_chapters} 个章节")
        
        updated_count = 0
        skipped_count = 0
        error_count = 0
        
        # 使用tqdm或简单循环显示进度
        if use_tqdm:
            chapter_iterator = tqdm(chapters, desc="处理章节")
        else:
            chapter_iterator = chapters
        
        for chapter in chapter_iterator:
            try:
                # 调用save方法会自动生成merged_content
                chapter.save(update_fields=['merged_content'])
                updated_count += 1
                
                # 每处理100个章节记录一次进度
                if updated_count % 100 == 0:
                    logger.info(f"已处理 {updated_count}/{total_chapters} 个章节")
                    
            except Exception as e:
                logger.error(f"处理章节 {chapter.id} - {chapter.title} 时出错: {str(e)}")
                error_count += 1
        
        logger.info(f"处理完成!")
        logger.info(f"成功更新: {updated_count} 个章节")
        logger.info(f"跳过: {skipped_count} 个章节")
        logger.info(f"错误: {error_count} 个章节")
        
    except Exception as e:
        logger.error(f"更新章节内容时发生错误: {str(e)}")

if __name__ == "__main__":
    logger.info("开始执行章节内容更新脚本")
    if setup_django():
        update_chapters_merged_content()
    else:
        logger.error("无法初始化Django环境，脚本终止")
        sys.exit(1)
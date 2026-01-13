#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json

# 添加项目根目录和apps目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apps'))

from books.docx_processor import DocxProcessor

def test_table_extraction():
    """测试表格提取和嵌入功能"""
    # 测试文件路径
    test_file_path = r"d:\liufyData\CodeBook_max\《人工智能基础》讲义——中.docx"
    
    if not os.path.exists(test_file_path):
        print(f"测试文件不存在: {test_file_path}")
        return
    
    print(f"测试文件: {test_file_path}")
    
    processor = DocxProcessor()
    if processor.open_document(test_file_path):
        try:
            # 提取章节内容（包含表格）
            chapters = processor.extract_content_by_headings()
            print(f"\n=== 提取到的章节数量: {len(chapters)} ===")
            
            # 查找包含表格的章节
            print(f"\n=== 包含表格的章节 ===")
            for i, chapter in enumerate(chapters):
                title = chapter['title']
                content = chapter['content']
                
                # 检查内容中是否包含表格标记
                if '|' in content and '---' in content:  # 简单的Markdown表格检测
                    print(f"章节 {i+1}: {title} 包含表格")
                    
                    # 打印章节内容的前500个字符
                    print(f"内容前500个字符:")
                    print(content[:500])
                    print("...")
                    print()
                    break  # 只打印第一个包含表格的章节
                    
        finally:
            processor.close_document()
    else:
        print("无法打开文档")

if __name__ == "__main__":
    test_table_extraction()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json

# 添加项目根目录和apps目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'apps'))

from books.docx_processor import DocxProcessor

def test_content_extraction():
    """测试DOCX内容提取是否正确"""
    # 测试文件路径
    test_file_path = r"d:\liufyData\CodeBook_max\《人工智能基础》讲义——中.docx"
    
    if not os.path.exists(test_file_path):
        print(f"测试文件不存在: {test_file_path}")
        return
    
    print(f"测试文件: {test_file_path}")
    
    processor = DocxProcessor()
    if processor.open_document(test_file_path):
        try:
            # 提取所有文本
            all_text = processor.extract_all_text()
            print(f"\n=== 文档总字数: {len(all_text)} ===")
            print(f"前1000个字符: {all_text[:1000]}...")
            
            # 提取章节内容
            chapters = processor.extract_content_by_headings()
            print(f"\n=== 提取到的章节数量: {len(chapters)} ===")
            
            # 打印每个章节的标题和内容长度
            for i, chapter in enumerate(chapters[:10]):  # 只打印前10个章节
                title = chapter['title']
                content = chapter['content']
                print(f"\n章节 {i+1}: {title}")
                print(f"内容长度: {len(content)} 字符")
                print(f"开始段落: {chapter['start_paragraph']}")
                
                # 打印前200个字符的内容
                if content:
                    print(f"内容前200个字符: {content[:200]}...")
                else:
                    print("内容为空！")
                    
        finally:
            processor.close_document()
    else:
        print("无法打开文档")

if __name__ == "__main__":
    test_content_extraction()
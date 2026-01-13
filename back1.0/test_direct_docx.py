#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
直接测试docx_processor.py的process_docx函数
绕过Django服务器，直接调用函数测试图片和表格处理功能
"""

import os
import tempfile
from apps.books.docx_processor import process_docx

# 测试文件路径
TEST_FILE_PATH = r"d:\liufyData\CodeBook_max\《人工智能基础》讲义——中.docx"

def test_direct_docx_processing():
    """直接测试docx处理功能"""
    print("=== 直接测试.docx处理功能 ===")
    
    # 检查测试文件是否存在
    if not os.path.exists(TEST_FILE_PATH):
        print(f"测试文件不存在: {TEST_FILE_PATH}")
        return False
    
    # 创建临时图片目录
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"临时图片目录: {temp_dir}")
        
        try:
            # 直接调用process_docx函数
            print("开始处理.docx文件...")
            result = process_docx(TEST_FILE_PATH, image_output_dir=temp_dir)
            
            # 打印处理结果摘要
            print("\n=== 处理结果摘要 ===")
            print(f"章节数量: {len(result['chapters'])}")
            print(f"图片数量: {len(result['images'])}")
            print(f"匹配章节数量: {len(result['matched_chapters'])}")
            
            # 打印前3个章节的标题和内容预览
            print("\n=== 章节内容预览 ===")
            for i, chapter in enumerate(result['chapters'][:3]):
                print(f"\n章节 {i+1}: {chapter['title']}")
                print(f"级别: {chapter['level']}")
                print(f"内容长度: {len(chapter['content'])} 字符")
                
                # 检查内容中是否包含表格
                if '| --- |' in chapter['content'] and '|' in chapter['content']:
                    print("✅ 内容包含Markdown表格")
                    # 打印表格部分
                    lines = chapter['content'].split('\n')
                    table_start = None
                    table_end = None
                    for j, line in enumerate(lines):
                        if '|' in line and table_start is None:
                            table_start = j
                        if table_start is not None and '|' not in line and j > table_start + 1:
                            table_end = j
                            break
                    if table_start is not None:
                        table_lines = lines[table_start:table_end]
                        print("表格预览:")
                        for line in table_lines[:5]:  # 只打印前5行
                            print(line)
                        if len(table_lines) > 5:
                            print("...")
                else:
                    print("❌ 内容不包含Markdown表格")
                
                # 检查内容中是否包含图片引用
                if "![图片" in chapter['content']:
                    print("✅ 内容包含图片引用")
                    # 打印图片引用部分
                    lines = chapter['content'].split('\n')
                    for line in lines:
                        if "![图片" in line:
                            print(f"图片引用: {line.strip()}")
                            break
                else:
                    print("❌ 内容不包含图片引用")
                
                # 打印内容前100个字符
                print(f"内容预览: {chapter['content'][:100]}...")
            
            # 打印图片信息
            print("\n=== 图片信息 ===")
            for i, image in enumerate(result['images'][:5]):  # 只打印前5张图片
                print(f"图片 {i+1}: {image['filename']}")
                print(f"  路径: {image['path']}")
                print(f"  尺寸: {image['width']}x{image['height']}")
                print(f"  ID: {image['id']}")
            
            if len(result['images']) > 5:
                print(f"... 还有 {len(result['images']) - 5} 张图片")
            
            print("\n✅ 测试完成！")
            return True
            
        except Exception as e:
            print(f"\n❌ 处理过程中发生错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    test_direct_docx_processing()

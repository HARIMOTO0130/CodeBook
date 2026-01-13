#!/usr/bin/env python3
import os
import json
from apps.books.docx_processor import process_docx, DocxProcessor

# 测试文件路径
test_file = r'd:\liufyData\CodeBook_max\《人工智能基础》讲义——中.docx'

print(f"测试文件: {test_file}")
print(f"文件存在: {os.path.exists(test_file)}")

# 创建处理器实例
processor = DocxProcessor()

# 打开文档
if processor.open_document(test_file):
    print("\n=== 文档打开成功 ===")
    
    # 提取所有段落
    print("\n=== 所有段落（前20个）===")
    paragraphs = processor.document.paragraphs
    for i, para in enumerate(paragraphs[:20]):
        text = para.text.strip()
        if text:
            print(f"段落 {i+1}: {text}")
    
    # 提取标题
    print("\n=== 提取的标题 ===")
    headings = processor._extract_headings()
    for heading in headings[:10]:
        print(f"级别 {heading['level']}: {heading['text']}")
    
    # 提取章节内容
    print("\n=== 提取的章节内容 ===")
    chapters = processor.extract_content_by_headings()
    for i, chapter in enumerate(chapters[:5]):
        print(f"\n章节 {i+1}: {chapter['title']} (级别: {chapter['level']})")
        print(f"开始段落: {chapter.get('start_paragraph', 'N/A')}")
        if 'end_paragraph' in chapter:
            print(f"结束段落: {chapter['end_paragraph']}")
        print(f"内容长度: {len(chapter['content'])} 字符")
        print(f"内容预览: {chapter['content'][:200]}...")
    
    # 关闭文档
    processor.close_document()
else:
    print("文档打开失败")

# 使用process_docx函数处理
print("\n=== 使用process_docx函数处理 ===")
result = process_docx(test_file)

print(f"\n目录项数: {len(result['toc'])}")
print(f"原始章节数: {len(result['chapters'])}")
print(f"匹配后的章节数: {len(result['matched_chapters'])}")

# 打印章节内容
print("\n=== 最终章节内容 ===")
for i, chapter in enumerate(result['chapters']):
    print(f"\n章节 {i+1}: {chapter['title']} (级别: {chapter['level']})")
    print(f"内容长度: {len(chapter['content'])} 字符")
    print(f"内容预览: {chapter['content'][:300]}...")

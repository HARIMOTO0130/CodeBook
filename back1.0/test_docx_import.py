#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试.docx导入功能的脚本
"""

import requests
import os
import sys
import json

# API端点
API_URL = "http://localhost:8000/api/books/import_docx/"
# 测试文件路径
TEST_FILE_PATH = r"d:\liufyData\CodeBook_max\《人工智能基础》讲义——中.docx"
# 测试用户信息（需要根据实际情况修改）
TEST_USERNAME = "admin"
TEST_PASSWORD = "admin123"

def get_token():
    """获取认证令牌"""
    token_url = "http://localhost:8000/api/token/"
    
    try:
        response = requests.post(token_url, data={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            return response.json().get("access", "")
        else:
            print(f"获取令牌失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return ""
    except Exception as e:
        print(f"获取令牌时发生错误: {str(e)}")
        return ""

def test_docx_import():
    """测试.docx导入功能"""
    # 检查测试文件是否存在
    if not os.path.exists(TEST_FILE_PATH):
        print(f"测试文件不存在: {TEST_FILE_PATH}")
        return False
    
    # 获取认证令牌
    token = get_token()
    if not token:
        return False
    
    # 设置请求头
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # 准备请求数据
    files = {
        "docx_file": open(TEST_FILE_PATH, "rb")
    }
    
    data = {
        "title": "人工智能基础讲义",
        "description": "测试导入的人工智能基础讲义",
        "author": "测试作者"
    }
    
    print(f"开始测试.docx导入功能...")
    print(f"测试文件: {TEST_FILE_PATH}")
    
    try:
        # 发送请求
        response = requests.post(API_URL, headers=headers, files=files, data=data)
        
        # 打印响应
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
        
        if response.status_code == 201:
            print("\n✓ 导入成功！")
            return True
        else:
            print("\n✗ 导入失败！")
            return False
            
    except Exception as e:
        print(f"\n✗ 测试过程中发生错误: {str(e)}")
        return False
    finally:
        # 关闭文件
        files["docx_file"].close()

if __name__ == "__main__":
    print("=== .docx导入功能测试 ===")
    print()
    
    success = test_docx_import()
    
    print()
    print("=== 测试结束 ===")
    
    # 根据测试结果设置退出码
    sys.exit(0 if success else 1)

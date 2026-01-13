#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import os
import json

## API端点
API_URL = "http://localhost:8000/api/books/import_docx/"
# 测试文件路径
TEST_FILE_PATH = r"d:\liufyData\CodeBook_max\test.docx"
# 测试配置
TEST_USERNAME = "provider"
TEST_PASSWORD = "123456"

def get_auth_token():
    """获取认证令牌"""
    token_url = "http://localhost:8000/api/users/login/"
    
    try:
        response = requests.post(token_url, data={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD
        })
        
        if response.status_code == 200:
            return response.json().get("token", "")
        else:
            print(f"获取令牌失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return ""
    except Exception as e:
        print(f"获取令牌时发生错误: {str(e)}")
        return ""

def test_docx_import():
    """测试.docx导入API"""
    # 检查测试文件是否存在
    if not os.path.exists(TEST_FILE_PATH):
        print(f"测试文件不存在: {TEST_FILE_PATH}")
        return False
    
    # 设置请求头（不需要认证）
    headers = {}
    # 为了兼容，仍然保留headers变量
    
    # 准备请求数据
    files = {
        "docx_file": open(TEST_FILE_PATH, "rb")
    }
    
    data = {
        "title": "人工智能基础讲义",
        "description": "测试API导入的人工智能基础讲义",
        "author": "测试作者",
        "chapter_count": "0"  # 导入所有章节
    }
    
    print(f"开始调用.docx导入API...")
    print(f"API地址: {API_URL}")
    print(f"测试文件: {TEST_FILE_PATH}")
    print(f"请求参数: {data}")
    
    try:
        # 发送请求
        response = requests.post(API_URL, headers=headers, files=files, data=data)
        
        # 打印响应
        print(f"\n响应状态码: {response.status_code}")
        try:
            response_json = response.json()
            print(f"响应内容: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
        except json.JSONDecodeError:
            print(f"响应内容: {response.text}")
        
        if response.status_code == 201:
            print("\n✅ 导入成功！")
            return True
        else:
            print("\n❌ 导入失败！")
            return False
            
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 关闭文件
        for file in files.values():
            file.close()

if __name__ == "__main__":
    print("=== .docx文档导入API测试 ===")
    print()
    
    success = test_docx_import()
    
    print()
    print("=== 测试结束 ===")
    exit(0 if success else 1)

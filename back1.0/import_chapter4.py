#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试导入.docx文档中的第四章内容
"""

import requests
import os
import json

# API端点
API_URL = "http://127.0.0.1:8000/api/books/import_docx/"
# 测试文件路径
TEST_FILE_PATH = "d:/liufyData/CodeBook_max/《人工智能基础》讲义——中.docx"

# 登录信息
LOGIN_URL = "http://127.0.0.1:8000/api/users/login/"
LOGIN_DATA = {
    "username": "provider",
    "password": "provider123"
}

def get_auth_token():
    """获取认证令牌"""
    try:
        response = requests.post(LOGIN_URL, json=LOGIN_DATA)
        if response.status_code == 200:
            return response.json().get("token", "")
        else:
            print(f"登录失败: {response.status_code}")
            print(f"错误信息: {response.text}")
            return ""
    except Exception as e:
        print(f"登录时发生错误: {str(e)}")
        return ""

def import_chapter4():
    """导入第四章内容"""
    # 检查测试文件是否存在
    if not os.path.exists(TEST_FILE_PATH):
        print(f"测试文件不存在: {TEST_FILE_PATH}")
        return False
    
    # 获取认证令牌
    token = get_auth_token()
    if not token:
        return False
    
    # 设置请求头
    headers = {
        "Authorization": f"Token {token}"
    }
    
    # 准备请求数据
    files = {
        "docx_file": open(TEST_FILE_PATH, "rb")
    }
    
    # 只导入第四章相关内容
    # 这里我们通过章节计数来控制，实际应用中可能需要更精确的过滤
    data = {
        "title": "人工智能基础讲义-第四章",
        "description": "仅包含第四章内容的人工智能基础讲义",
        "author": "测试作者",
        "chapter_count": "0"  # 0表示导入所有章节，然后我们可以在后台过滤
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
    print("=== 测试导入第四章内容 ===")
    import_chapter4()

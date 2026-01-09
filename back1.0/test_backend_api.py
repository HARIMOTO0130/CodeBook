#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试后端API集成
"""

import requests
import json

def test_intelligent_recommendation():
    """测试智能推荐API"""
    print("开始测试智能推荐API...")
    
    # API端点 - 使用正确的路径
    url = "http://localhost:8000/api/learning/recommendations/personalized-suggestions/"
    
    # 请求数据
    payload = {
        "user_id": 1,
        "limit": 5
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # 发送请求
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        print(f"\nAPI响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text}")
        
        try:
            response_json = response.json()
            print(f"\nAPI响应JSON: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
        except Exception as json_err:
            print(f"\n响应不是有效的JSON: {json_err}")
        
        if response.status_code == 200:
            print("\n智能推荐API测试成功!")
        else:
            print(f"\n智能推荐API测试失败: {response.status_code}")
    
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_personalized_path():
    """测试个性化学习路径API"""
    print("\n" + "=" * 50)
    print("开始测试个性化学习路径API...")
    
    # API端点 - 使用正确的路径
    url = "http://localhost:8000/api/learning/personalized-path/generate/"
    
    # 请求数据
    payload = {
        "user_id": 1,
        "learning_goal": "掌握Python数据分析",
        "knowledge_level": "beginner"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        # 发送请求
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        print(f"\nAPI响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text}")
        
        try:
            response_json = response.json()
            print(f"\nAPI响应JSON: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
        except Exception as json_err:
            print(f"\n响应不是有效的JSON: {json_err}")
        
        if response.status_code == 200:
            print("\n个性化学习路径API测试成功!")
        else:
            print(f"\n个性化学习路径API测试失败: {response.status_code}")
    
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_intelligent_recommendation()
    test_personalized_path()

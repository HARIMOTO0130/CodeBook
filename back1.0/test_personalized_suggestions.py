#!/usr/bin/env python
"""测试个性化学习建议生成功能"""

import requests
import json

def test_personalized_suggestions():
    """测试生成个性化学习建议API"""
    print("=== 测试个性化学习建议生成功能 ===")
    
    # API端点
    api_url = "http://127.0.0.1:8000/api/student/learning/recommendations/personalized-suggestions/"
    
    # 请求参数
    payload = {
        "learning_goal": "Java",
        "knowledge_node_ids": []
    }
    
    # 请求头
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Token 0c8f15d22a7b3c3d4e5f6a7b8c9d0e1f2a3b4c5d"  # 替换为有效的token
    }
    
    try:
        # 发送请求
        print(f"1. 发送请求到API端点: {api_url}")
        print(f"1. 请求参数: {payload}")
        response = requests.post(api_url, json=payload, headers=headers)
        
        # 检查响应状态
        print(f"2. 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            # 解析响应内容
            result = response.json()
            print(f"3. 响应内容: {json.dumps(result, ensure_ascii=False, indent=2)}")
            
            # 检查建议数量
            suggestions = result.get("suggestions", [])
            print(f"4. 生成的建议数量: {len(suggestions)}")
            
            if suggestions:
                print("5. 建议列表:")
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"   {i}. {suggestion}")
            else:
                print("5. ❌ 测试失败: 未生成任何建议")
            
            return len(suggestions) > 0
        else:
            print(f"5. ❌ 测试失败: API返回错误状态码 {response.status_code}")
            print(f"5. 错误信息: {response.text}")
            return False
    except Exception as e:
        print(f"5. ❌ 测试失败: {str(e)}")
        return False

if __name__ == "__main__":
    test_personalized_suggestions()

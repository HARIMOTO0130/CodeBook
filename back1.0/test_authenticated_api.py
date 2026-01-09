#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试需要认证的API端点
"""

import requests
import json

def login(username, password):
    """登录获取认证token"""
    print(f"尝试使用账号 {username} 登录...")
    
    url = "http://localhost:8000/api/users/login/"
    payload = {
        "username": username,
        "password": password
    }
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        print(f"登录响应状态码: {response.status_code}")
        print(f"登录响应内容: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            token = response_data.get('token')
            if token:
                print(f"登录成功，获取到token: {token[:10]}...")
                return token
            else:
                print("登录成功，但未获取到token")
                return None
        else:
            print(f"登录失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"登录异常: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_intelligent_recommendation(token):
    """测试智能推荐API"""
    print("\n开始测试智能推荐API...")
    
    # 测试多个智能推荐相关端点
    test_endpoints = [
        ("GET", "http://localhost:8000/api/learning/recommendations/roadmap/"),
        ("GET", "http://localhost:8000/api/learning/recommendations/next-content/"),
        ("GET", "http://localhost:8000/api/learning/recommendations/user-profile/"),
    ]
    
    headers = {
        "Authorization": f"Token {token}"
    }
    
    for method, url in test_endpoints:
        print(f"\n尝试 {method} {url}")
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            else:
                continue
            
            print(f"响应状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            
            try:
                response_json = response.json()
                print(f"响应JSON: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
            except Exception as json_err:
                print(f"响应不是有效的JSON: {json_err}")
            
            if response.status_code == 200:
                print(f"✅ {method} {url} 测试成功!")
                return True
        
        except Exception as e:
            print(f"❌ {method} {url} 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 尝试使用POST方法测试generate_personalized_suggestions端点
    print("\n最后尝试测试generate_personalized_suggestions端点...")
    url = "http://localhost:8000/api/learning/recommendations/personalized-suggestions/"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps({"user_id": 1, "limit": 5}))
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            print("✅ 智能推荐API测试成功!")
            return True
        else:
            print(f"❌ 智能推荐API测试失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 智能推荐API测试失败: {e}")
        return False

def test_personalized_path(token):
    """测试个性化学习路径API"""
    print("\n" + "=" * 50)
    print("开始测试个性化学习路径API...")
    
    url = "http://localhost:8000/api/learning/personalized-path/generate/"
    payload = {
        "user_id": 1,
        "learning_goal": "掌握Python数据分析",
        "knowledge_level": "beginner"
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        print(f"\nAPI响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text}")
        
        try:
            response_json = response.json()
            print(f"\nAPI响应JSON: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
            if response.status_code == 200:
                print("\n个性化学习路径API测试成功!")
                return True
            else:
                print(f"\n个性化学习路径API测试失败: {response.status_code}")
                return False
        except Exception as json_err:
            print(f"\n响应不是有效的JSON: {json_err}")
            return False
    
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_api(token):
    """测试LLM API"""
    print("\n" + "=" * 50)
    print("开始测试LLM API...")
    
    url = "http://localhost:8000/api/learning/llm/generate/"
    payload = {
        "prompt": "请解释一下知识图谱的概念",
        "temperature": 0.7,
        "max_tokens": 500
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        print(f"\nAPI响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text}")
        
        try:
            response_json = response.json()
            print(f"\nAPI响应JSON: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
            if response.status_code == 200:
                print("\nLLM API测试成功!")
                return True
            else:
                print(f"\nLLM API测试失败: {response.status_code}")
                return False
        except Exception as json_err:
            print(f"\n响应不是有效的JSON: {json_err}")
            return False
    
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_knowledge_graph(token):
    """测试知识图谱API"""
    print("\n" + "=" * 50)
    print("开始测试知识图谱API...")
    
    # 测试获取知识节点
    url = "http://localhost:8000/api/learning/knowledge-graph/nodes/"
    headers = {
        "Authorization": f"Token {token}"
    }
    
    try:
        response = requests.get(url, headers=headers)
        
        print(f"\n知识节点API响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("\n知识图谱API测试成功!")
            return True
        else:
            print(f"\n知识图谱API测试失败: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_llm_knowledge_extraction(token):
    """测试LLM知识提取功能"""
    print("\n" + "=" * 50)
    print("开始测试LLM知识提取功能...")
    
    url = "http://localhost:8000/api/learning/llm/extract-knowledge/"
    payload = {
        "text": "Python是一种高级编程语言，它具有简洁的语法和强大的功能。Python可以用于Web开发、数据分析、人工智能等领域。Python的主要特点包括：1. 易于学习；2. 开源；3. 跨平台；4. 丰富的库生态系统。"
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        print(f"\nAPI响应状态码: {response.status_code}")
        print(f"API响应内容: {response.text}")
        
        try:
            response_json = response.json()
            print(f"\nAPI响应JSON: {json.dumps(response_json, ensure_ascii=False, indent=2)}")
            if response.status_code == 200:
                nodes = response_json.get('nodes', [])
                relations = response_json.get('relations', [])
                print(f"\n成功提取知识节点，节点数：{len(nodes)}, 关系数：{len(relations)}")
                print("LLM知识提取功能测试成功!")
                return True
            else:
                print(f"\nLLM知识提取功能测试失败: {response.status_code}")
                return False
        except Exception as json_err:
            print(f"\n响应不是有效的JSON: {json_err}")
            return False
    
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("开始测试API认证和功能...")
    
    # 登录获取token
    token = login("student", "123456")
    if not token:
        print("\n无法获取认证token，测试结束")
        return
    
    # 测试各个API端点
    results = []
    results.append(test_intelligent_recommendation(token))
    results.append(test_personalized_path(token))
    results.append(test_llm_api(token))
    results.append(test_knowledge_graph(token))
    results.append(test_llm_knowledge_extraction(token))
    
    # 输出测试结果汇总
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print(f"总测试数: {len(results)}")
    print(f"通过测试数: {sum(results)}")
    print(f"失败测试数: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 所有测试通过!")
    else:
        print(f"\n⚠️  有 {len(results) - sum(results)} 个测试失败")

if __name__ == "__main__":
    main()

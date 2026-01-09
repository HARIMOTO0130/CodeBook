#!/usr/bin/env python3
"""
测试大模型集成功能
"""

import os
import sys
from dotenv import load_dotenv

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 加载.env文件
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

# 设置环境变量，加载Django配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.learning.llm_integration import LLMService

# 测试豆包API调用
def test_doubao_api():
    print("测试豆包API调用...")
    
    # 从Django设置中获取API密钥
    from django.conf import settings
    api_key = settings.DOUBao_API_KEY
    
    if not api_key:
        print("错误：DOUBao_API_KEY环境变量未设置")
        return False
    
    # 创建LLM服务实例
    llm_service = LLMService(provider='doubao', api_key=api_key)
    
    # 测试生成响应
    try:
        prompt = "请简要介绍一下Python的主要特点"
        response = llm_service.generate_response(prompt)
        print(f"成功调用豆包API，响应：{response[:100]}...")
        return True
    except Exception as e:
        print(f"调用豆包API失败：{e}")
        return False

# 测试知识提取
def test_knowledge_extraction():
    print("\n测试知识提取功能...")
    
    llm_service = LLMService(provider='doubao')
    
    text = "Python是一种高级编程语言，具有简单易学、可读性强、支持多种编程范式等特点。它广泛应用于Web开发、数据分析、人工智能等领域。Python的主要版本包括Python 2和Python 3，目前主流是Python 3。"
    
    try:
        result = llm_service.extract_knowledge_nodes(text)
        print(f"成功提取知识节点，节点数：{len(result['nodes'])}, 关系数：{len(result['relations'])}")
        return True
    except Exception as e:
        print(f"知识提取失败：{e}")
        return False

if __name__ == "__main__":
    print("开始测试大模型集成功能...")
    
    # 测试豆包API调用
    doubao_result = test_doubao_api()
    
    # 测试知识提取
    extraction_result = test_knowledge_extraction()
    
    print("\n测试完成")
    print(f"豆包API调用：{'成功' if doubao_result else '失败'}")
    print(f"知识提取功能：{'成功' if extraction_result else '失败'}")

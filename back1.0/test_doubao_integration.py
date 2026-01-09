#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试豆包API集成
"""

import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.learning.llm_integration import LLMService

def test_doubao_integration():
    """测试豆包API集成"""
    print("开始测试豆包API集成...")
    
    try:
        # 初始化LLM服务
        llm_service = LLMService(provider='doubao')
        print(f"初始化成功，提供商: {llm_service.provider}")
        print(f"模型名称: {llm_service.model_name}")
        print(f"API密钥: {llm_service.api_key[:10]}...")
        
        # 测试简单对话
        test_prompt = "你好，能帮我生成一个学习计划吗？"
        print(f"\n测试提示词: {test_prompt}")
        
        response = llm_service.generate_response(test_prompt, temperature=0.7, max_tokens=500)
        print(f"\n豆包API响应:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        
        # 测试知识提取功能
        print("\n测试知识提取功能...")
        test_text = "Python是一种高级编程语言，它具有简洁的语法和强大的功能。Python可以用于Web开发、数据分析、人工智能等领域。Python的主要特点包括：1. 易于学习；2. 开源；3. 跨平台；4. 丰富的库生态系统。"
        knowledge_nodes = llm_service.extract_knowledge_nodes(test_text)
        print(f"成功提取知识节点，节点数：{len(knowledge_nodes['nodes'])}, 关系数：{len(knowledge_nodes['relations'])}")
        
        print("\n测试完成，豆包API集成成功！")
        return True
    
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_doubao_integration()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试代码沙盒支持的所有编程语言功能
"""
import requests
import json
import sys
import time

BASE_URL = "http://127.0.0.1:8000/api/learning/execute/"

def test_language(language, code, description):
    """测试特定语言的代码执行"""
    print(f"\n{'=' * 60}")
    print(f"测试 {language.upper()}: {description}")
    print(f"{'=' * 60}")
    
    try:
        # 构建请求数据
        data = {
            'language': language,
            'code': code
        }
        
        # 发送请求
        print(f"发送代码到沙盒执行...")
        response = requests.post(BASE_URL, json=data)
        
        # 检查响应
        if response.status_code == 200:
            result = response.json()
            print(f"执行状态: {'成功' if result.get('success') else '失败'}")
            print(f"输出结果:")
            print(f"{'-' * 40}")
            print(result.get('output', '无输出'))
            print(f"{'-' * 40}")
            
            if not result.get('success'):
                print(f"错误信息: {result.get('error', '未知错误')}")
            
            return result.get('success', False)
        else:
            print(f"请求失败，状态码: {response.status_code}")
            print(f"响应内容: {response.text}")
            return False
            
    except Exception as e:
        print(f"测试过程中发生异常: {str(e)}")
        return False

def test_all_languages():
    """测试所有支持的编程语言"""
    # 测试配置
    tests = [
        {
            'language': 'python',
            'code': 'print("Hello from Python!")\nfor i in range(3):\n    print(f"Python test - iteration {i+1}")\nprint("Python test completed successfully!")',
            'description': '基础打印和循环'
        },
        {
            'language': 'javascript',
            'code': 'console.log("Hello from JavaScript!");\nfor (let i = 0; i < 3; i++) {\n    console.log(`JavaScript test - iteration ${i+1}`);\n}\nconsole.log("JavaScript test completed successfully!");',
            'description': '基础打印和循环'
        },
        {
            'language': 'java',
            'code': 'public class TestJava {\n    public static void main(String[] args) {\n        System.out.println("Hello from Java!");\n        for (int i = 0; i < 3; i++) {\n            System.out.println("Java test - iteration " + (i+1));\n        }\n        System.out.println("Java test completed successfully!");\n    }\n}',
            'description': '基础打印和循环'
        },
        {
            'language': 'c',
            'code': '#include <stdio.h>\n\nint main() {\n    printf("Hello from C!\n");\n    for (int i = 0; i < 3; i++) {\n        printf("C test - iteration %d\n", i+1);\n    }\n    printf("C test completed successfully!\n");\n    return 0;\n}',
            'description': '基础打印和循环'
        },
        {
            'language': 'html',
            'code': '<!DOCTYPE html>\n<html>\n<head>\n    <title>HTML Test</title>\n</head>\n<body>\n    <h1>Hello from HTML!</h1>\n    <p>This is a test paragraph.</p>\n    <div>HTML test completed successfully!</div>\n</body>\n</html>',
            'description': '基本HTML结构'
        }
    ]
    
    # 执行所有测试
    success_count = 0
    total_count = len(tests)
    
    for test in tests:
        if test_language(test['language'], test['code'], test['description']):
            success_count += 1
        
        # 添加短暂延迟避免请求过于密集
        time.sleep(1)
    
    # 打印测试总结
    print(f"\n{'=' * 60}")
    print(f"测试总结: {success_count}/{total_count} 种语言测试成功")
    print(f"{'=' * 60}")
    
    return success_count == total_count

if __name__ == "__main__":
    print("开始测试代码沙盒多语言支持...")
    print(f"测试API地址: {BASE_URL}")
    print("直接执行测试，跳过服务检查")
    
    # 执行测试
    all_passed = test_all_languages()
    
    if all_passed:
        print("\n所有测试通过！代码沙盒多语言支持功能正常工作。")
        sys.exit(0)
    else:
        print("\n部分测试失败，请检查代码沙盒的实现。")
        sys.exit(1)
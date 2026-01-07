#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
代码沙盒功能测试脚本
"""

import requests
import json

BASE_URL = 'http://localhost:8000/api'

# 测试用例
test_cases = [
    {
        "name": "Python 基础测试",
        "language": "python",
        "code": "print('Hello, World!')\nx = 10\ny = 20\nprint(f'x + y = {x + y}')",
        "expected_success": True
    },
    {
        "name": "JavaScript 基础测试",
        "language": "javascript",
        "code": "console.log('Hello, World!');\nlet x = 10;\nlet y = 20;\nconsole.log(`x + y = ${x + y}`);",
        "expected_success": True
    },
    {
        "name": "Java 基础测试",
        "language": "java",
        "code": "public class Main {\n    public static void main(String[] args) {\n        System.out.println(\"Hello, World!\");\n        int x = 10;\n        int y = 20;\n        System.out.println(\"x + y = \" + (x + y));\n    }\n}",
        "expected_success": False
    },
    {
        "name": "C 基础测试",
        "language": "c",
        "code": "#include <stdio.h>\n\nint main() {\n    printf(\"Hello, World!\\n\");\n    int x = 10;\n    int y = 20;\n    printf(\"x + y = %d\\n\", x + y);\n    return 0;\n}",
        "expected_success": False
    },
    {
        "name": "C++ 基础测试",
        "language": "cpp",
        "code": "#include <iostream>\n\nint main() {\n    std::cout << \"Hello, World!\" << std::endl;\n    int x = 10;\n    int y = 20;\n    std::cout << \"x + y = \" << (x + y) << std::endl;\n    return 0;\n}",
        "expected_success": False
    },
    {
        "name": "HTML 基础测试",
        "language": "html",
        "code": "<!DOCTYPE html>\n<html>\n<head>\n    <title>Test</title>\n</head>\n<body>\n    <h1>Hello, World!</h1>\n    <p>This is a test.</p>\n</body>\n</html>",
        "expected_success": True
    },
    {
        "name": "CSS 基础测试",
        "language": "css",
        "code": "/* CSS 测试代码 */\nbody {\n    background-color: lightblue;\n    font-family: Arial, sans-serif;\n}\n\nh1 {\n    color: darkblue;\n    text-align: center;\n}\n\n.container {\n    width: 80%;\n    margin: 0 auto;\n    padding: 20px;\n    background-color: white;\n    box-shadow: 0 0 10px rgba(0,0,0,0.1);\n}",
        "expected_success": True
    },
    {
        "name": "Python 安全测试（禁用危险函数）",
        "language": "python",
        "code": "import os\nos.system('ls -la')",
        "expected_success": False
    },
    {
        "name": "Python 超时测试",
        "language": "python",
        "code": "while True: pass",
        "expected_success": False
    }
]

def test_execute_code():
    """测试代码执行功能"""
    print("=== 测试代码执行功能 ===")
    success_count = 0
    total_count = len(test_cases)
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print(f"语言: {test_case['language']}")
        print(f"代码:\n{test_case['code']}")
        
        try:
            response = requests.post(
                f'{BASE_URL}/learning/execute/',
                json={
                    'language': test_case['language'],
                    'code': test_case['code']
                }
            )
            
            result = response.json()
            print(f"响应状态码: {response.status_code}")
            print(f"执行结果: {'成功' if result['success'] else '失败'}")
            
            if 'output' in result and result['output']:
                print(f"输出: {result['output']}")
            
            if 'error' in result and result['error']:
                print(f"错误: {result['error']}")
            
            # 验证结果
            if result['success'] == test_case['expected_success']:
                print("✅ 测试通过")
                success_count += 1
            else:
                print("❌ 测试失败")
                print(f"  预期: {'成功' if test_case['expected_success'] else '失败'}")
                print(f"  实际: {'成功' if result['success'] else '失败'}")
                
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {success_count}/{total_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    return success_count == total_count

def test_get_languages():
    """测试获取支持的编程语言列表"""
    print("\n=== 测试获取支持的编程语言列表 ===")
    
    try:
        response = requests.get(f'{BASE_URL}/learning/code-sandbox/languages/')
        result = response.json()
        print(f"响应状态码: {response.status_code}")
        print(f"支持的语言: {result['languages']}")
        print(f"默认语言: {result['default']}")
        
        # 验证C++是否在支持列表中
        if 'cpp' in result['languages']:
            print("✅ C++语言已成功添加到支持列表")
            return True
        else:
            print("❌ C++语言未添加到支持列表")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("代码沙盒功能测试")
    print(f"测试API地址: {BASE_URL}")
    
    # 测试获取支持的编程语言列表
    languages_test = test_get_languages()
    
    # 测试代码执行功能
    execute_test = test_execute_code()
    
    # 综合结果
    print("\n=== 综合测试结果 ===")
    if languages_test and execute_test:
        print("✅ 所有测试通过")
        return 0
    else:
        print("❌ 部分测试失败")
        return 1

if __name__ == "__main__":
    exit(main())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建独立练习题数据脚本
用于生成与教材无关的独立练习题
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import django
django.setup()

from apps.learning.models import Exercise, ExerciseTestCase

def create_python_basic_exercises():
    """创建Python基础练习题"""
    exercises = [
        {
            'title': 'Hello World',
            'description': '输出Hello World',
            'question': '编写代码输出Hello World',
            'code_template': '# 请在此处编写代码\n',
            'language': 'python',
            'difficulty': 1,
            'category': 'python_basic',
            'test_cases': [
                {'input_data': {}, 'expected_output': 'Hello World'}
            ]
        },
        {
            'title': '求和函数',
            'description': '计算两个数的和',
            'question': '编写一个函数add(a, b)，返回a和b的和。',
            'code_template': 'def add(a, b):\n    # 请在此处编写代码\n    pass',
            'language': 'python',
            'difficulty': 1,
            'category': 'python_basic',
            'test_cases': [
                {'input_data': {'a': 5, 'b': 3}, 'expected_output': 8},
                {'input_data': {'a': -2, 'b': 7}, 'expected_output': 5},
                {'input_data': {'a': 0, 'b': 0}, 'expected_output': 0}
            ]
        },
        {
            'title': '判断素数',
            'description': '判断一个数是否为素数',
            'question': '编写一个函数is_prime(n)，判断n是否为素数。',
            'code_template': 'def is_prime(n):\n    # 请在此处编写代码\n    pass',
            'language': 'python',
            'difficulty': 2,
            'category': 'python_basic',
            'test_cases': [
                {'input_data': {'n': 7}, 'expected_output': True},
                {'input_data': {'n': 10}, 'expected_output': False},
                {'input_data': {'n': 2}, 'expected_output': True}
            ]
        },
        {
            'title': '统计字符出现次数',
            'description': '统计字符串中每个字符出现的次数',
            'question': '编写一个函数count_chars(s)，返回字符串s中每个字符出现的次数字典。',
            'code_template': 'def count_chars(s):\n    # 请在此处编写代码\n    pass',
            'language': 'python',
            'difficulty': 2,
            'category': 'python_basic',
            'test_cases': [
                {'input_data': {'s': 'hello'}, 'expected_output': {'h': 1, 'e': 1, 'l': 2, 'o': 1}},
                {'input_data': {'s': 'Python'}, 'expected_output': {'P': 1, 'y': 1, 't': 1, 'h': 1, 'o': 1, 'n': 1}},
                {'input_data': {'s': ''}, 'expected_output': {}}
            ]
        },
        {
            'title': '合并两个有序列表',
            'description': '合并两个已排序的列表',
            'question': '编写一个函数merge_sorted_lists(list1, list2)，合并两个已排序的列表并返回排序后的结果。',
            'code_template': 'def merge_sorted_lists(list1, list2):\n    # 请在此处编写代码\n    pass',
            'language': 'python',
            'difficulty': 3,
            'category': 'python_basic',
            'test_cases': [
                {'input_data': {'list1': [1, 3, 5], 'list2': [2, 4, 6]}, 'expected_output': [1, 2, 3, 4, 5, 6]},
                {'input_data': {'list1': [10, 20], 'list2': [5, 15, 25]}, 'expected_output': [5, 10, 15, 20, 25]},
                {'input_data': {'list1': [], 'list2': [1, 2, 3]}, 'expected_output': [1, 2, 3]}
            ]
        }
    ]
    return exercises

def create_javascript_basic_exercises():
    """创建JavaScript基础练习题"""
    exercises = [
        {
            'title': 'JavaScript Hello World',
            'description': '输出Hello World',
            'question': '编写JavaScript代码输出Hello World',
            'code_template': '// 请在此处编写代码\n',
            'language': 'javascript',
            'difficulty': 1,
            'category': 'javascript_basic',
            'test_cases': [
                {'input_data': {}, 'expected_output': 'Hello World'}
            ]
        },
        {
            'title': 'JavaScript求和函数',
            'description': '计算两个数的和',
            'question': '编写一个函数add(a, b)，返回a和b的和。',
            'code_template': 'function add(a, b) {\n    // 请在此处编写代码\n}',
            'language': 'javascript',
            'difficulty': 1,
            'category': 'javascript_basic',
            'test_cases': [
                {'input_data': {'a': 5, 'b': 3}, 'expected_output': 8},
                {'input_data': {'a': -2, 'b': 7}, 'expected_output': 5},
                {'input_data': {'a': 0, 'b': 0}, 'expected_output': 0}
            ]
        },
        {
            'title': '数组去重',
            'description': '去除数组中的重复元素',
            'question': '编写一个函数unique(arr)，返回一个去重后的新数组。',
            'code_template': 'function unique(arr) {\n    // 请在此处编写代码\n}',
            'language': 'javascript',
            'difficulty': 2,
            'category': 'javascript_basic',
            'test_cases': [
                {'input_data': {'arr': [1, 2, 2, 3, 4, 4]}, 'expected_output': [1, 2, 3, 4]},
                {'input_data': {'arr': ['a', 'b', 'a', 'c']}, 'expected_output': ['a', 'b', 'c']},
                {'input_data': {'arr': []}, 'expected_output': []}
            ]
        },
        {
            'title': '对象属性遍历',
            'description': '遍历对象的所有属性',
            'question': '编写一个函数getObjectKeys(obj)，返回对象所有属性名的数组。',
            'code_template': 'function getObjectKeys(obj) {\n    // 请在此处编写代码\n}',
            'language': 'javascript',
            'difficulty': 2,
            'category': 'javascript_basic',
            'test_cases': [
                {'input_data': {'obj': {name: 'Alice', age: 25}}, 'expected_output': ['name', 'age']},
                {'input_data': {'obj': {}}, 'expected_output': []}
            ]
        },
        {
            'title': 'DOM元素创建',
            'description': '创建并返回DOM元素',
            'question': '编写一个函数createElement(tag, content, className)，创建一个指定标签、内容和类名的DOM元素。',
            'code_template': 'function createElement(tag, content, className) {\n    // 请在此处编写代码\n}',
            'language': 'javascript',
            'difficulty': 3,
            'category': 'javascript_basic',
            'test_cases': [
                {'input_data': {'tag': 'div', 'content': 'Hello', 'className': 'greeting'}, 'expected_output': '<div class="greeting">Hello</div>'},
                {'input_data': {'tag': 'p', 'content': 'Test', 'className': 'test-class'}, 'expected_output': '<p class="test-class">Test</p>'}
            ]
        }
    ]
    return exercises

def create_algorithm_exercises():
    """创建算法基础练习题"""
    exercises = [
        {
            'title': '二分查找',
            'description': '实现二分查找算法',
            'question': '编写一个函数binary_search(arr, target)，在已排序的数组arr中查找target，如果找到返回索引，否则返回-1。',
            'code_template': 'def binary_search(arr, target):\n    # 请在此处编写代码\n    pass',
            'language': 'python',
            'difficulty': 2,
            'category': 'algorithm',
            'test_cases': [
                {'input_data': {'arr': [1, 2, 3, 4, 5], 'target': 3}, 'expected_output': 2},
                {'input_data': {'arr': [10, 20, 30, 40], 'target': 25}, 'expected_output': -1},
                {'input_data': {'arr': [5, 10, 15, 20, 25], 'target': 25}, 'expected_output': 4}
            ]
        },
        {
            'title': '快速排序',
            'description': '实现快速排序算法',
            'question': '编写一个函数quick_sort(arr)，使用快速排序算法对列表进行排序。',
            'code_template': 'def quick_sort(arr):\n    # 请在此处编写代码\n    pass',
            'language': 'python',
            'difficulty': 3,
            'category': 'algorithm',
            'test_cases': [
                {'input_data': {'arr': [3, 1, 4, 1, 5, 9, 2, 6]}, 'expected_output': [1, 1, 2, 3, 4, 5, 6, 9]},
                {'input_data': {'arr': [10, 5, 3, 8, 2]}, 'expected_output': [2, 3, 5, 8, 10]},
                {'input_data': {'arr': [1, 2, 3, 4, 5]}, 'expected_output': [1, 2, 3, 4, 5]}
            ]
        },
        {
            'title': '斐波那契数列',
            'description': '计算斐波那契数列的第n项',
            'question': '编写一个函数fibonacci(n)，返回斐波那契数列的第n项。',
            'code_template': 'def fibonacci(n):\n    # 请在此处编写代码\n    pass',
            'language': 'python',
            'difficulty': 2,
            'category': 'algorithm',
            'test_cases': [
                {'input_data': {'n': 5}, 'expected_output': 5},
                {'input_data': {'n': 10}, 'expected_output': 55},
                {'input_data': {'n': 1}, 'expected_output': 1}
            ]
        },
        {
            'title': '括号匹配',
            'description': '检查括号是否正确匹配',
            'question': '编写一个函数is_valid_parentheses(s)，检查字符串中的括号是否正确匹配。',
            'code_template': 'def is_valid_parentheses(s):\n    # 请在此处编写代码\n    pass',
            'language': 'python',
            'difficulty': 2,
            'category': 'algorithm',
            'test_cases': [
                {'input_data': {'s': '()'}, 'expected_output': True},
                {'input_data': {'s': '()[]{}'}, 'expected_output': True},
                {'input_data': {'s': '(]'}, 'expected_output': False}
            ]
        },
        {
            'title': '最大子数组和',
            'description': '找出最大子数组和',
            'question': '编写一个函数max_subarray(nums)，找出数组中具有最大和的连续子数组。',
            'code_template': 'def max_subarray(nums):\n    # 请在此处编写代码\n    pass',
            'language': 'python',
            'difficulty': 3,
            'category': 'algorithm',
            'test_cases': [
                {'input_data': {'nums': [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, 'expected_output': 6},
                {'input_data': {'nums': [1]}, 'expected_output': 1},
                {'input_data': {'nums': [5, 4, -1, 7, 8]}, 'expected_output': 23}
            ]
        }
    ]
    return exercises

def create_logic_exercises():
    """创建编程思维练习题"""
    exercises = [
        {
            'title': 'FizzBuzz问题',
            'description': '经典的FizzBuzz编程问题',
            'question': '编写一个函数fizz_buzz(n)，返回一个列表，包含从1到n的字符串表示。',
            'code_template': 'def fizz_buzz(n):\n    # 请在此处编写代码\n    pass',
            'language': 'python',
            'difficulty': 1,
            'category': 'logic',
            'test_cases': [
                {'input_data': {'n': 5}, 'expected_output': ['1', '2', 'Fizz', '4', 'Buzz']},
                {'input_data': {'n': 15}, 'expected_output': ['1', '2', 'Fizz', '4', 'Buzz', 'Fizz', '7', '8', 'Fizz', 'Buzz', '11', 'Fizz', '13', '14', 'FizzBuzz']},
                {'input_data': {'n': 3}, 'expected_output': ['1', '2', 'Fizz']}
            ]
        },
        {
            'title': '回文数',
            'description': '判断一个整数是否为回文数',
            'question': '编写一个函数is_palindrome_number(x)，判断整数x是否为回文数。',
            'code_template': 'def is_palindrome_number(x):\n    # 请在此处编写代码\n    pass',
            'language': 'python',
            'difficulty': 2,
            'category': 'logic',
            'test_cases': [
                {'input_data': {'x': 121}, 'expected_output': True},
                {'input_data': {'x': -121}, 'expected_output': False},
                {'input_data': {'x': 10}, 'expected_output': False}
            ]
        },
        {
            'title': '罗马数字转整数',
            'description': '将罗马数字转换为整数',
            'question': '编写一个函数roman_to_int(s)，将罗马数字字符串转换为整数。',
            'code_template': 'def roman_to_int(s):\n    # 请在此处编写代码\n    pass',
            'language': 'python',
            'difficulty': 2,
            'category': 'logic',
            'test_cases': [
                {'input_data': {'s': 'III'}, 'expected_output': 3},
                {'input_data': {'s': 'IV'}, 'expected_output': 4},
                {'input_data': {'s': 'IX'}, 'expected_output': 9}
            ]
        },
        {
            'title': '最长公共前缀',
            'description': '找出字符串数组的最长公共前缀',
            'question': '编写一个函数longest_common_prefix(strs)，找出字符串数组的最长公共前缀。',
            'code_template': 'def longest_common_prefix(strs):\n    # 请在此处编写代码\n    pass',
            'language': 'python',
            'difficulty': 2,
            'category': 'logic',
            'test_cases': [
                {'input_data': {'strs': ['flower', 'flow', 'flight']}, 'expected_output': 'fl'},
                {'input_data': {'strs': ['dog', 'racecar', 'car']}, 'expected_output': ''},
                {'input_data': {'strs': ['apple', 'app', 'application']}, 'expected_output': 'app'}
            ]
        },
        {
            'title': '反转整数',
            'description': '反转一个整数',
            'question': '编写一个函数reverse_integer(x)，反转整数x。',
            'code_template': 'def reverse_integer(x):\n    # 请在此处编写代码\n    pass',
            'language': 'python',
            'difficulty': 2,
            'category': 'logic',
            'test_cases': [
                {'input_data': {'x': 123}, 'expected_output': 321},
                {'input_data': {'x': -123}, 'expected_output': -321},
                {'input_data': {'x': 120}, 'expected_output': 21}
            ]
        }
    ]
    return exercises

def create_all_exercises():
    """创建所有练习题"""
    all_exercises = []
    
    # 收集所有类别的练习题
    all_exercises.extend(create_python_basic_exercises())
    all_exercises.extend(create_javascript_basic_exercises())
    all_exercises.extend(create_algorithm_exercises())
    all_exercises.extend(create_logic_exercises())
    
    # 创建练习题及其测试用例
    created_count = 0
    for exercise_data in all_exercises:
        # 检查是否已存在同名练习题
        existing = Exercise.objects.filter(title=exercise_data['title']).first()
        if not existing:
            # 创建练习题
            test_cases_data = exercise_data.pop('test_cases')
            exercise = Exercise.objects.create(**exercise_data)
            
            # 创建测试用例
            for i, test_case_data in enumerate(test_cases_data):
                test_case_data['exercise'] = exercise
                test_case_data['order'] = i
                ExerciseTestCase.objects.create(**test_case_data)
            
            created_count += 1
            print(f"已创建练习题: {exercise.title}")
        else:
            print(f"练习题已存在: {exercise_data['title']}")
    
    print(f"\n创建完成！共创建了 {created_count} 个练习题。")

if __name__ == '__main__':
    print("开始创建独立练习题数据...")
    create_all_exercises()
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建练习题页面三个板块的习题数据
"""
import os
import sys
import django
from django.utils import timezone
import json

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.books.models import Book, Chapter, Practice, TestCase

def create_practice_books_and_chapters():
    """创建练习题相关的书籍和章节"""
    print("开始创建练习题数据...")
    
    # 创建3个练习板块对应的书籍
    practice_books_data = [
        {
            'title': 'Python基础练习题',
            'author': '系统',
            'description': 'Python编程语言基础知识练习题集合',
            'tags': json.dumps(['Python', '编程', '基础', '练习'])
        },
        {
            'title': '算法与数据结构练习题',
            'author': '系统',
            'description': '常见算法和数据结构练习题',
            'tags': json.dumps(['算法', '数据结构', '编程', '练习'])
        },
        {
            'title': '编程思维拓展练习题',
            'author': '系统',
            'description': '培养编程思维和解决问题能力的练习题',
            'tags': json.dumps(['编程思维', '逻辑', '问题解决', '练习'])
        }
    ]
    
    created_books = []
    for book_data in practice_books_data:
        book, created = Book.objects.get_or_create(
            title=book_data['title'],
            defaults={
                'author': book_data['author'],
                'description': book_data['description'],
                'tags': book_data['tags']
            }
        )
        if created:
            print(f"创建书籍: {book.title}")
        else:
            print(f"书籍已存在: {book.title}")
        created_books.append(book)
    
    # 为每本书创建10个练习章节
    for book in created_books:
        create_practice_chapters_for_book(book)
    
    print("练习题数据创建完成！")

def create_practice_chapters_for_book(book):
    """为指定书籍创建练习章节"""
    book_title = book.title
    language = 'python'  # 默认使用Python语言
    
    # 根据书籍类型定义不同的练习题
    if 'Python' in book_title:
        chapter_data_list = get_python_exercises()
    elif '算法' in book_title:
        chapter_data_list = get_algorithm_exercises()
    else:
        chapter_data_list = get_logic_exercises()
    
    for i, chapter_data in enumerate(chapter_data_list, 1):
        # 检查章节是否已存在
        existing_chapter = Chapter.objects.filter(
            book=book,
            title=chapter_data['title']
        ).first()
        
        if existing_chapter:
            print(f"章节已存在: {book.title} - {chapter_data['title']}")
            continue
        
        # 创建章节
        chapter = Chapter.objects.create(
            book=book,
            title=chapter_data['title'],
            type='practice',
            duration=chapter_data.get('duration', 20),
            description=chapter_data['description'],
            language=language,
            order=i
        )
        
        # 创建练习题
        practice = Practice.objects.create(
            chapter=chapter,
            question=chapter_data['question'],
            code_template=chapter_data['code_template']
        )
        
        # 创建测试用例
        for test_case_data in chapter_data['test_cases']:
            TestCase.objects.create(
                practice=practice,
                input_data=test_case_data['input_data'],
                expected_output=test_case_data['expected_output']
            )
        
        print(f"创建章节和练习题: {book.title} - {chapter.title}")

def get_python_exercises():
    """Python基础练习题"""
    return [
        {
            'title': '两数之和',
            'description': '编写一个函数，计算两个数的和',
            'question': '编写一个函数add(a, b)，接收两个数字参数，返回它们的和。',
            'code_template': 'def add(a, b):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'a': 1, 'b': 2}, 'expected_output': 3},
                {'input_data': {'a': 5, 'b': 10}, 'expected_output': 15},
                {'input_data': {'a': -3, 'b': 7}, 'expected_output': 4}
            ]
        },
        {
            'title': '判断回文字符串',
            'description': '编写函数判断一个字符串是否为回文',
            'question': '编写一个函数is_palindrome(s)，判断字符串s是否为回文（正读倒读都一样）。',
            'code_template': 'def is_palindrome(s):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'s': 'level'}, 'expected_output': True},
                {'input_data': {'s': 'hello'}, 'expected_output': False},
                {'input_data': {'s': 'radar'}, 'expected_output': True}
            ]
        },
        {
            'title': '计算阶乘',
            'description': '编写函数计算一个数的阶乘',
            'question': '编写一个函数factorial(n)，计算并返回n的阶乘。',
            'code_template': 'def factorial(n):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'n': 5}, 'expected_output': 120},
                {'input_data': {'n': 0}, 'expected_output': 1},
                {'input_data': {'n': 3}, 'expected_output': 6}
            ]
        },
        {
            'title': '列表求和',
            'description': '计算列表中所有元素的和',
            'question': '编写一个函数sum_list(numbers)，计算并返回列表中所有元素的和。',
            'code_template': 'def sum_list(numbers):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'numbers': [1, 2, 3, 4, 5]}, 'expected_output': 15},
                {'input_data': {'numbers': [10, 20, 30]}, 'expected_output': 60},
                {'input_data': {'numbers': []}, 'expected_output': 0}
            ]
        },
        {
            'title': '找出最大值',
            'description': '找出列表中的最大值',
            'question': '编写一个函数find_max(numbers)，返回列表中的最大值。',
            'code_template': 'def find_max(numbers):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'numbers': [1, 5, 3, 9, 2]}, 'expected_output': 9},
                {'input_data': {'numbers': [-10, -5, -20]}, 'expected_output': -5},
                {'input_data': {'numbers': [42]}, 'expected_output': 42}
            ]
        },
        {
            'title': '字符串反转',
            'description': '反转输入的字符串',
            'question': '编写一个函数reverse_string(s)，返回反转后的字符串。',
            'code_template': 'def reverse_string(s):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'s': 'hello'}, 'expected_output': 'olleh'},
                {'input_data': {'s': 'Python'}, 'expected_output': 'nohtyP'},
                {'input_data': {'s': ''}, 'expected_output': ''}
            ]
        },
        {
            'title': '计算平均数',
            'description': '计算列表中所有元素的平均值',
            'question': '编写一个函数average(numbers)，返回列表中所有元素的平均值。',
            'code_template': 'def average(numbers):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'numbers': [1, 2, 3, 4, 5]}, 'expected_output': 3.0},
                {'input_data': {'numbers': [10, 20, 30]}, 'expected_output': 20.0},
                {'input_data': {'numbers': [5]}, 'expected_output': 5.0}
            ]
        },
        {
            'title': '判断素数',
            'description': '判断一个数是否为素数',
            'question': '编写一个函数is_prime(n)，判断n是否为素数。',
            'code_template': 'def is_prime(n):\n    # 请在此处编写代码\n    pass',
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
            'test_cases': [
                {'input_data': {'list1': [1, 3, 5], 'list2': [2, 4, 6]}, 'expected_output': [1, 2, 3, 4, 5, 6]},
                {'input_data': {'list1': [10, 20], 'list2': [5, 15, 25]}, 'expected_output': [5, 10, 15, 20, 25]},
                {'input_data': {'list1': [], 'list2': [1, 2, 3]}, 'expected_output': [1, 2, 3]}
            ]
        }
    ]

def get_algorithm_exercises():
    """算法与数据结构练习题"""
    return [
        {
            'title': '二分查找',
            'description': '实现二分查找算法',
            'question': '编写一个函数binary_search(arr, target)，在已排序的数组arr中查找target，如果找到返回索引，否则返回-1。',
            'code_template': 'def binary_search(arr, target):\n    # 请在此处编写代码\n    pass',
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
            'test_cases': [
                {'input_data': {'arr': [3, 1, 4, 1, 5, 9, 2, 6]}, 'expected_output': [1, 1, 2, 3, 4, 5, 6, 9]},
                {'input_data': {'arr': [10, 5, 3, 8, 2]}, 'expected_output': [2, 3, 5, 8, 10]},
                {'input_data': {'arr': [1, 2, 3, 4, 5]}, 'expected_output': [1, 2, 3, 4, 5]}
            ]
        },
        {
            'title': '链表节点反转',
            'description': '反转链表的节点',
            'question': '实现一个函数reverse_linked_list(head)，反转链表的节点顺序。',
            'code_template': 'class ListNode:\n    def __init__(self, val=0, next=None):\n        self.val = val\n        self.next = next\n\ndef reverse_linked_list(head):\n    # 请在此处编写代码\n    pass\n\n# 辅助函数：将列表转换为链表\ndef list_to_linked_list(lst):\n    dummy = ListNode(0)\n    current = dummy\n    for val in lst:\n        current.next = ListNode(val)\n        current = current.next\n    return dummy.next\n\n# 辅助函数：将链表转换为列表\ndef linked_list_to_list(head):\n    result = []\n    current = head\n    while current:\n        result.append(current.val)\n        current = current.next\n    return result',
            'test_cases': [
                {'input_data': {'head': [1, 2, 3, 4, 5]}, 'expected_output': [5, 4, 3, 2, 1]},
                {'input_data': {'head': [10, 20, 30]}, 'expected_output': [30, 20, 10]},
                {'input_data': {'head': []}, 'expected_output': []}
            ]
        },
        {
            'title': '斐波那契数列',
            'description': '计算斐波那契数列的第n项',
            'question': '编写一个函数fibonacci(n)，返回斐波那契数列的第n项。',
            'code_template': 'def fibonacci(n):\n    # 请在此处编写代码\n    pass',
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
            'test_cases': [
                {'input_data': {'nums': [-2, 1, -3, 4, -1, 2, 1, -5, 4]}, 'expected_output': 6},
                {'input_data': {'nums': [1]}, 'expected_output': 1},
                {'input_data': {'nums': [5, 4, -1, 7, 8]}, 'expected_output': 23}
            ]
        },
        {
            'title': '有效的回文',
            'description': '判断字符串是否为有效的回文',
            'question': '编写一个函数is_valid_palindrome(s)，判断字符串是否为有效的回文（只考虑字母和数字，忽略大小写）。',
            'code_template': 'def is_valid_palindrome(s):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'s': 'A man, a plan, a canal: Panama'}, 'expected_output': True},
                {'input_data': {'s': 'race a car'}, 'expected_output': False},
                {'input_data': {'s': ' '}, 'expected_output': True}
            ]
        },
        {
            'title': '两数之和II',
            'description': '在有序数组中找出和为目标值的两个数的索引',
            'question': '编写一个函数two_sum(numbers, target)，在已排序的数组中找出和为目标值的两个数的索引。',
            'code_template': 'def two_sum(numbers, target):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'numbers': [2, 7, 11, 15], 'target': 9}, 'expected_output': [1, 2]},
                {'input_data': {'numbers': [2, 3, 4], 'target': 6}, 'expected_output': [1, 3]},
                {'input_data': {'numbers': [-1, 0], 'target': -1}, 'expected_output': [1, 2]}
            ]
        },
        {
            'title': '爬楼梯',
            'description': '计算爬楼梯的方法数',
            'question': '编写一个函数climb_stairs(n)，计算爬到第n阶楼梯的方法数。',
            'code_template': 'def climb_stairs(n):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'n': 2}, 'expected_output': 2},
                {'input_data': {'n': 3}, 'expected_output': 3},
                {'input_data': {'n': 4}, 'expected_output': 5}
            ]
        },
        {
            'title': '合并区间',
            'description': '合并重叠的区间',
            'question': '编写一个函数merge_intervals(intervals)，合并所有重叠的区间。',
            'code_template': 'def merge_intervals(intervals):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'intervals': [[1, 3], [2, 6], [8, 10], [15, 18]]}, 'expected_output': [[1, 6], [8, 10], [15, 18]]},
                {'input_data': {'intervals': [[1, 4], [4, 5]]}, 'expected_output': [[1, 5]]},
                {'input_data': {'intervals': [[1, 4], [0, 2], [3, 5]]}, 'expected_output': [[0, 5]]}
            ]
        }
    ]

def get_logic_exercises():
    """编程思维拓展练习题"""
    return [
        {
            'title': 'FizzBuzz问题',
            'description': '经典的FizzBuzz编程问题',
            'question': '编写一个函数fizz_buzz(n)，返回一个列表，包含从1到n的字符串表示。',
            'code_template': 'def fizz_buzz(n):\n    # 请在此处编写代码\n    pass',
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
            'test_cases': [
                {'input_data': {'strs': ['flower', 'flow', 'flight']}, 'expected_output': 'fl'},
                {'input_data': {'strs': ['dog', 'racecar', 'car']}, 'expected_output': ''},
                {'input_data': {'strs': ['apple', 'app', 'application']}, 'expected_output': 'app'}
            ]
        },
        {
            'title': '有效的括号字符串',
            'description': '检查括号字符串是否有效',
            'question': '编写一个函数check_valid_string(s)，检查包含(、)和*的字符串是否有效。',
            'code_template': 'def check_valid_string(s):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'s': '()'}, 'expected_output': True},
                {'input_data': {'s': '(*)'}, 'expected_output': True},
                {'input_data': {'s': '(*))'}, 'expected_output': True}
            ]
        },
        {
            'title': '多数元素',
            'description': '找出数组中的多数元素',
            'question': '编写一个函数majority_element(nums)，找出数组中出现次数超过一半的元素。',
            'code_template': 'def majority_element(nums):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'nums': [3, 2, 3]}, 'expected_output': 3},
                {'input_data': {'nums': [2, 2, 1, 1, 1, 2, 2]}, 'expected_output': 2},
                {'input_data': {'nums': [1]}, 'expected_output': 1}
            ]
        },
        {
            'title': '求众数II',
            'description': '找出数组中出现次数超过n/3的元素',
            'question': '编写一个函数majority_element_ii(nums)，找出数组中出现次数超过n/3的所有元素。',
            'code_template': 'def majority_element_ii(nums):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'nums': [3, 2, 3]}, 'expected_output': [3]},
                {'input_data': {'nums': [1]}, 'expected_output': [1]},
                {'input_data': {'nums': [1, 1, 1, 3, 3, 2, 2, 2]}, 'expected_output': [1, 2]}
            ]
        },
        {
            'title': '反转整数',
            'description': '反转一个整数',
            'question': '编写一个函数reverse_integer(x)，反转整数x。',
            'code_template': 'def reverse_integer(x):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'x': 123}, 'expected_output': 321},
                {'input_data': {'x': -123}, 'expected_output': -321},
                {'input_data': {'x': 120}, 'expected_output': 21}
            ]
        },
        {
            'title': '移除元素',
            'description': '移除数组中指定值的所有元素',
            'question': '编写一个函数remove_element(nums, val)，移除数组中所有等于val的元素。',
            'code_template': 'def remove_element(nums, val):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'nums': [3, 2, 2, 3], 'val': 3}, 'expected_output': 2},
                {'input_data': {'nums': [0, 1, 2, 2, 3, 0, 4, 2], 'val': 2}, 'expected_output': 5},
                {'input_data': {'nums': [], 'val': 0}, 'expected_output': 0}
            ]
        },
        {
            'title': '加一',
            'description': '对数组表示的数字加一',
            'question': '编写一个函数plus_one(digits)，对数组表示的非负整数加一。',
            'code_template': 'def plus_one(digits):\n    # 请在此处编写代码\n    pass',
            'test_cases': [
                {'input_data': {'digits': [1, 2, 3]}, 'expected_output': [1, 2, 4]},
                {'input_data': {'digits': [4, 3, 2, 1]}, 'expected_output': [4, 3, 2, 2]},
                {'input_data': {'digits': [9]}, 'expected_output': [1, 0]}
            ]
        }
    ]

if __name__ == '__main__':
    create_practice_books_and_chapters()
"""初始化数据脚本"""
import os
import sys
import django

# 设置Django环境
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.users.models import User, UserPreferences
from apps.books.models import Book, Chapter, Practice, TestCase
from django.contrib.auth.hashers import make_password

def create_users():
    """创建示例用户"""
    print("创建示例用户...")
    
    # 创建管理员用户
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'password': make_password('admin123'),
            'is_staff': True,
            'is_superuser': True
        }
    )
    
    # 创建普通用户
    student_user, created = User.objects.get_or_create(
        username='student',
        defaults={
            'email': 'student@example.com',
            'password': make_password('student123')
        }
    )
    
    # 创建用户偏好设置
    UserPreferences.objects.get_or_create(user=admin_user)
    UserPreferences.objects.get_or_create(
        user=student_user,
        defaults={
            'default_language': 'python',
            'code_theme': 'vs-dark',
            'auto_play_video': False,
            'keyboard_shortcuts': True
        }
    )
    
    print("用户创建完成")

def create_books():
    """创建更真实的多教材、多章节示例数据（不同语言/不同正文/不同代码）"""
    print("创建示例教材...")

    # 1) Python 编程入门
    python_book, _ = Book.objects.get_or_create(
        id=1,
        defaults={
            'title': 'Python编程入门',
            'author': '张三',
            'description': '从零开始掌握Python：基础语法、数据结构、控制流与实践',
        }
    )
    python_book.tag_list = ['Python', '基础', '编程入门']
    python_book.save()

    Chapter.objects.update_or_create(
        id=101,
        defaults={
            'book': python_book,
            'title': '第1章：Python与开发环境',
            'type': 'reading',
            'duration': 25,
            'description': '安装解释器、认识REPL与脚本模式、基本IO',
            'content': '# Python与开发环境\n\n本章介绍如何安装Python、如何在交互式解释器(REPL)与脚本模式下运行代码。\n\n示例：输出一行文本。\n\n```python\nprint("Hello, Python!")\n```',
            'code': 'print("Hello, Python from Chapter 1!")',
            'language': 'python',
            'order': 1
        }
    )

    Chapter.objects.update_or_create(
        id=102,
        defaults={
            'book': python_book,
            'title': '第2章：数据结构与循环',
            'type': 'reading',
            'duration': 40,
            'description': '列表/字典/集合/元组与for/while循环',
            'content': '# 数据结构与循环\n\n列表与字典是Python最常用的数据结构。\n\n```python\nnums = [1,2,3,4]\nfor n in nums:\n    print(n*n)\n```',
            'code': 'nums = [1, 2, 3, 4]\nfor n in nums:\n    print(n*n)',
            'language': 'python',
            'order': 2
        }
    )

    Chapter.objects.update_or_create(
        id=103,
        defaults={
            'book': python_book,
            'title': '第3章：文件与异常（视频）',
            'type': 'video',
            'duration': 35,
            'description': '读写文本文件与异常捕获',
            'content': '# 文件与异常\n\ntry/except 可以优雅地处理异常。',
            'code': 'try:\n    with open("README.md", "r", encoding="utf-8") as f:\n        print(f.readline())\nexcept FileNotFoundError:\n    print("文件不存在")',
            'language': 'python',
            'video_url': 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4',
            'order': 3
        }
    )

    # 练习章节
    py_practice_ch, _ = Chapter.objects.update_or_create(
        id=104,
        defaults={
            'book': python_book,
            'title': '第4章：条件与函数（练习）',
            'type': 'practice',
            'duration': 45,
            'description': '综合练习：判断与函数封装',
            'language': 'python',
            'order': 4
        }
    )

    practice, _ = Practice.objects.get_or_create(
        chapter=py_practice_ch,
        defaults={
            'question': '实现一个函数 is_even(n) 返回字符串“偶数”或“奇数”',
            'code_template': 'def is_even(n):\n    # 请在此处实现\n    pass\n\nprint(is_even(42))\nprint(is_even(7))\n'
        }
    )
    TestCase.objects.get_or_create(practice=practice, defaults={'input_data': 42, 'expected_output': '偶数'})
    TestCase.objects.get_or_create(practice=practice, defaults={'input_data': 7, 'expected_output': '奇数'})
    python_book.save()

    # 2) JavaScript 基础（不同语言、不同代码与内容）
    js_book, _ = Book.objects.get_or_create(
        id=2,
        defaults={
            'title': 'JavaScript基础',
            'author': '李四',
            'description': '浏览器与Node.js双环境下的JavaScript基础语法与实践',
        }
    )
    js_book.tag_list = ['JavaScript', '前端', 'Node.js']
    js_book.save()

    Chapter.objects.update_or_create(
        id=201,
        defaults={
            'book': js_book,
            'title': '第1章：JS快速上手',
            'type': 'reading',
            'duration': 20,
            'description': '变量、控制台输出、基本数据类型',
            'content': '# JS快速上手\n\n使用 console.log 输出文本。\n\n```javascript\nconsole.log("Hello, JS!")\n```',
            'code': 'console.log("Hello, JS from Chapter 1!")',
            'language': 'javascript',
            'order': 1
        }
    )

    Chapter.objects.update_or_create(
        id=202,
        defaults={
            'book': js_book,
            'title': '第2章：数组与循环',
            'type': 'reading',
            'duration': 30,
            'description': 'Array与for/forEach的使用',
            'content': '# 数组与循环\n\n使用 forEach 遍历数组：\n\n```javascript\n[1,2,3].forEach(n => console.log(n*n))\n```',
            'code': '[1,2,3,4].forEach(n => console.log(n*n))',
            'language': 'javascript',
            'order': 2
        }
    )

    Chapter.objects.update_or_create(
        id=203,
        defaults={
            'book': js_book,
            'title': '第3章：异步与Promise（视频）',
            'type': 'video',
            'duration': 35,
            'description': '理解事件循环、Promise与async/await',
            'content': '# 异步基础\n\n使用Promise封装异步：',
            'code': 'async function main(){\n  const v = await Promise.resolve(42)\n  console.log(v)\n}\nmain()',
            'language': 'javascript',
            'video_url': 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4',
            'order': 3
        }
    )

    js_book.save()

    print("教材创建完成：Python与JavaScript两套不同内容与语言的示例数据已准备")

def main():
    """主函数"""
    print("开始初始化数据...")
    create_users()
    create_books()
    print("数据初始化完成！")

if __name__ == '__main__':
    main()
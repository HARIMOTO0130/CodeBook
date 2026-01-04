import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 导入Django
import django
django.setup()

# 导入模型
from apps.books.models import Book, Chapter, Practice, TestCase

def add_new_book():
    """向数据库添加新的计算机相关书籍"""
    print("开始添加新书籍...")
    
    # 创建新书籍 - 计算机网络基础
    new_book, created = Book.objects.get_or_create(
        id=2,  # 使用不同于第一本书的ID
        defaults={
            'title': '计算机网络基础',
            'author': '李四',
            'description': '系统介绍计算机网络的基本概念、原理和应用'
        }
    )
    
    if created:
        print(f"成功创建新书籍: {new_book.title}")
        
        # 设置标签
        new_book.tag_list = ['计算机网络', '网络基础', 'TCP/IP']
        new_book.save()
        
        # 创建章节1：网络概述
        chapter1, _ = Chapter.objects.get_or_create(
            id=201,
            defaults={
                'book': new_book,
                'title': '第1章：网络概述',
                'type': 'reading',
                'duration': 35,
                'description': '了解计算机网络的基本概念和发展历程',
                'content': '# 计算机网络概述\n\n计算机网络是指将分散的计算机通过通信设备连接起来，实现信息共享和资源共享的系统。\n\n```python\n# 简单的网络连接示例\nimport socket\n\ndef simple_client():\n    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n    client.connect((\"127.0.0.1\", 8080))\n    client.send(b\"Hello, Network!\")\n    response = client.recv(1024)\n    print(f\"收到响应: {response.decode()}\")\n    client.close()\n```',
                'code': 'import socket\n\ndef simple_client():\n    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n    client.connect((\"127.0.0.1\", 8080))\n    client.send(b\"Hello, Network!\")\n    response = client.recv(1024)\n    print(f\"收到响应: {response.decode()}\")\n    client.close()',
                'language': 'python',
                'order': 1
            }
        )
        
        # 创建章节2：OSI七层模型
        chapter2, _ = Chapter.objects.get_or_create(
            id=202,
            defaults={
                'book': new_book,
                'title': '第2章：OSI七层模型',
                'type': 'video',
                'duration': 50,
                'description': '学习OSI参考模型的七层结构和各层功能',
                'content': '# OSI七层模型\n\nOSI参考模型将网络通信分为七层，每一层都有特定的功能。\n\n```python\n# 模拟OSI模型的简单示例\ndef application_layer():\n    return "应用层数据"\n\ndef presentation_layer(data):\n    return f"{data} (已编码)"\n\ndef session_layer(data):\n    return f"{data} (会话已建立)"\n\ndef transport_layer(data):\n    return f"{data} (添加了端口信息)"\n\ndef network_layer(data):\n    return f"{data} (添加了IP地址)"\n\ndef data_link_layer(data):\n    return f"{data} (添加了MAC地址)"\n\ndef physical_layer(data):\n    return f"{data} (已转换为比特流)"\n```',
                'code': '# OSI模型数据传输模拟\ndef process_data_through_layers():\n    data = application_layer()\n    data = presentation_layer(data)\n    data = session_layer(data)\n    data = transport_layer(data)\n    data = network_layer(data)\n    data = data_link_layer(data)\n    data = physical_layer(data)\n    print(f"最终传输的数据: {data}")\n\n# 尝试实现各个层的函数',
                'language': 'python',
                'video_url': 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4',
                'order': 2
            }
        )
        
        # 创建章节3：TCP/IP协议（练习章节）
        chapter3, _ = Chapter.objects.get_or_create(
            id=203,
            defaults={
                'book': new_book,
                'title': '第3章：TCP/IP协议',
                'type': 'practice',
                'duration': 65,
                'description': '掌握TCP/IP协议的基本概念和应用',
                'language': 'python',
                'order': 3
            }
        )
        
        # 创建练习
        practice, _ = Practice.objects.get_or_create(
            chapter=chapter3,
            defaults={
                'question': '编写一个简单的TCP服务器程序',
                'code_template': 'import socket\n\ndef create_tcp_server(host, port):\n    # 创建socket\n    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n    \n    # 绑定地址和端口\n    ??\n    \n    # 开始监听\n    ??\n    \n    print(f"服务器正在 {host}:{port} 上运行...")\n    \n    # 接受连接\n    conn, addr = server.accept()\n    print(f"客户端已连接: {addr}")\n    \n    # 接收数据\n    data = conn.recv(1024)\n    print(f"收到数据: {data.decode()}")\n    \n    # 发送响应\n    conn.send(b"Hello from server!")\n    \n    # 关闭连接\n    conn.close()\n    server.close()\n\n# 调用函数\ncreate_tcp_server(\"127.0.0.1\", 8080)'  
            }
        )
        
        # 创建测试用例
        TestCase.objects.get_or_create(
            practice=practice,
            defaults={
                'input_data': 'Hello, Server!',
                'expected_output': 'Hello from server!'
            }
        )
        
        TestCase.objects.get_or_create(
            practice=practice,
            defaults={
                'input_data': 'Test Connection',
                'expected_output': 'Hello from server!'
            }
        )
        
        print(f"成功为 {new_book.title} 创建了3个章节和相关练习")
    else:
        print(f"书籍 '{new_book.title}' 已经存在")
    
    print("\n更新后的书籍列表：")
    all_books = Book.objects.all()
    for book in all_books:
        print(f"- {book.title} (作者: {book.author})")
    print(f"\n数据库中现在共有 {all_books.count()} 本书籍")

if __name__ == "__main__":
    add_new_book()
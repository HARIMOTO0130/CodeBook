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

def add_unique_book():
    """添加一本全新的、内容独特的计算机相关书籍"""
    print("开始添加全新书籍...")
    
    # 首先删除之前添加的书籍（ID=2）
    try:
        old_book = Book.objects.get(id=2)
        old_book.delete()
        print("已删除之前添加的书籍")
    except Book.DoesNotExist:
        print("之前的书籍不存在，继续添加新书籍")
    
    # 创建新书籍 - JavaScript编程入门
    new_book, created = Book.objects.get_or_create(
        id=2,  # 使用不同于第一本书的ID
        defaults={
            'title': 'JavaScript编程入门',
            'author': '王五',
            'description': '全面介绍JavaScript编程语言的核心概念、语法特性和实际应用场景，从基础到进阶的系统学习指南'
        }
    )
    
    if created:
        print(f"成功创建新书籍: {new_book.title}")
        
        # 设置标签
        new_book.tag_list = ['JavaScript', '前端开发', '编程语言', 'Web开发']
        new_book.save()
        
        # 创建章节1：JavaScript简介（使用JavaScript代码示例）
        chapter1, _ = Chapter.objects.get_or_create(
            id=201,
            defaults={
                'book': new_book,
                'title': '第1章：JavaScript简介与环境搭建',
                'type': 'reading',
                'duration': 45,
                'description': '了解JavaScript的历史起源、特点优势，以及如何搭建开发环境',
                'content': '# JavaScript简介与环境搭建\n\nJavaScript是一种具有函数优先特性的轻量级解释型或即时编译型的编程语言。虽然它是作为开发Web页面的脚本语言而出名，但是它也被用到了很多非浏览器环境中。\n\n## JavaScript的历史与发展\n\nJavaScript诞生于1995年，由Netscape公司的Brendan Eich在仅仅10天内设计完成。最初名为LiveScript，后来为了蹭Java的热度而改名为JavaScript，但两者实际上没有任何关系。\n\n## JavaScript的特点\n\n- **解释型语言**：不需要编译，浏览器可以直接执行\n- **弱类型语言**：变量类型可以动态改变\n- **基于原型的面向对象**：不同于传统的基于类的面向对象语言\n- **单线程执行**：通过事件循环实现异步操作\n\n## 开发环境搭建\n\n最简单的JavaScript开发环境只需要一个文本编辑器和一个浏览器。\n\n```javascript\n// 第一个JavaScript程序\nconsole.log("Hello, JavaScript!");\n\n// 创建一个简单的HTML页面\n/*\n<!DOCTYPE html>\n<html>\n<head>\n    <title>JavaScript示例</title>\n</head>\n<body>\n    <h1>我的第一个JavaScript程序</h1>\n    <script>\n        document.write("Hello, JavaScript世界!");\n        console.log("这行代码将在控制台显示");\n    </script>\n</body>\n</html>\n*/\n\n// JavaScript中的变量声明\nlet name = "JavaScript";\nconst version = 2023;\nvar isFun = true;\n\n// 输出变量信息\nconsole.log(`语言: ${name}`);\nconsole.log(`版本年份: ${version}`);\nconsole.log(`是否有趣: ${isFun}`);\n```',
                'code': '// JavaScript基础示例代码\n\n// 1. 变量声明和数据类型\nlet message = "Hello, JavaScript!";\nconst PI = 3.14159;\nlet count = 100;\nlet isActive = true;\n\n// 2. 函数定义和调用\nfunction greet(name) {\n    return `Hello, ${name}! Welcome to JavaScript world.`;\n}\n\n// 3. 数组操作\nconst languages = ["JavaScript", "HTML", "CSS", "Node.js"];\n\n// 4. 输出结果\nconsole.log(message);\nconsole.log(PI);\nconsole.log(greet("学习者"));\nconsole.log(`Web开发需要学习: ${languages.join(", ")}`);',
                'language': 'javascript',
                'order': 1
            }
        )
        
        # 创建章节2：JavaScriptDOM编程（使用JavaScript代码示例）
        chapter2, _ = Chapter.objects.get_or_create(
            id=202,
            defaults={
                'book': new_book,
                'title': '第2章：DOM操作与事件处理',
                'type': 'video',
                'duration': 60,
                'description': '学习如何使用JavaScript操作HTML文档，处理用户交互事件',
                'content': '# DOM操作与事件处理\n\n文档对象模型（DOM）是HTML和XML文档的编程接口。它提供了对文档的结构化表述，并定义了一种方式可以使程序对该结构进行访问，从而改变文档的结构、样式和内容。\n\n## DOM树结构\n\n当网页被加载时，浏览器会创建页面的文档对象模型（Document Object Model）。HTML DOM模型被构造为对象的树。\n\n## DOM选择器\n\nJavaScript提供了多种方式来选择DOM元素：\n\n```javascript\n// DOM选择器示例\n\n// 通过ID选择元素\nconst headerElement = document.getElementById("main-header");\n\n// 通过类名选择元素\nconst items = document.getElementsByClassName("list-item");\n\n// 通过标签名选择元素\nconst paragraphs = document.getElementsByTagName("p");\n\n// 通过CSS选择器选择元素\nconst firstItem = document.querySelector(".list-item:first-child");\nconst allItems = document.querySelectorAll(".list-item");\n\n// 改变元素样式\nheaderElement.style.color = "blue";\nheaderElement.style.backgroundColor = "lightgray";\nheaderElement.style.padding = "10px";\n\n// 修改元素内容\nheaderElement.textContent = "更新后的标题";\n\n// 添加新元素\nfunction addNewElement() {\n    // 创建新元素\n    const newParagraph = document.createElement("p");\n    \n    // 设置元素内容\n    newParagraph.textContent = "这是一个新添加的段落。";\n    newParagraph.className = "dynamic-content";\n    \n    // 添加到文档中\n    document.body.appendChild(newParagraph);\n    \n    console.log("新元素已添加到页面中");\n}\n```\n\n## 事件处理\n\nJavaScript可以监听和响应用户的交互事件，如点击、悬停、键盘输入等。\n\n```javascript\n// 事件处理示例\n\n// 方法1: 使用属性绑定\nconst button1 = document.getElementById("button1");\nbutton1.onclick = function() {\n    alert("按钮1被点击了!");\n};\n\n// 方法2: 使用addEventListener\nconst button2 = document.getElementById("button2");\nbutton2.addEventListener("click", function() {\n    console.log("按钮2被点击了!");\n    this.style.backgroundColor = "green";\n});\n\n// 方法3: 使用命名函数\nfunction handleMouseOver(event) {\n    console.log("鼠标悬停在元素上!");\n    event.target.style.color = "red";\n}\n\nconst hoverElement = document.getElementById("hover-element");\nhoverElement.addEventListener("mouseover", handleMouseOver);\n\n// 移除事件监听器\nfunction cleanup() {\n    hoverElement.removeEventListener("mouseover", handleMouseOver);\n    console.log("事件监听器已移除");\n}\n```',
                'code': '// DOM操作综合示例\n\n// 等待DOM加载完成\ndocument.addEventListener("DOMContentLoaded", function() {\n    // 创建一个待办事项管理器\n    const todoApp = {\n        init: function() {\n            this.todoInput = document.getElementById("todo-input");\n            this.addButton = document.getElementById("add-todo");\n            this.todoList = document.getElementById("todo-list");\n            \n            // 添加事件监听器\n            this.addButton.addEventListener("click", this.addTodo.bind(this));\n            this.todoInput.addEventListener("keypress", (e) => {\n                if (e.key === "Enter") {\n                    this.addTodo();\n                }\n            });\n            \n            console.log("待办事项应用已初始化");\n        },\n        \n        addTodo: function() {\n            const text = this.todoInput.value.trim();\n            if (text !== "") {\n                const li = document.createElement("li");\n                li.className = "todo-item";",\n                li.innerHTML = `\n                    <span>${text}</span>\n                    <button class="delete-btn">删除</button>\n                `;\n                \n                // 添加删除功能\n                const deleteBtn = li.querySelector(".delete-btn");\n                deleteBtn.addEventListener("click", () => {\n                    li.remove();\n                    console.log("待办事项已删除");\n                });\n                \n                // 添加到列表\n                this.todoList.appendChild(li);\n                \n                // 清空输入框\n                this.todoInput.value = "";",\n                \n                console.log(`已添加待办事项: ${text}`);\n            }\n        }\n    };\n    \n    // 初始化应用\n    todoApp.init();\n});',
                'language': 'javascript',
                'video_url': 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4',
                'order': 2
            }
        )
        
        # 创建章节3：JavaScript异步编程（使用JavaScript代码示例）
        chapter3, _ = Chapter.objects.get_or_create(
            id=203,
            defaults={
                'book': new_book,
                'title': '第3章：异步编程与Promise',
                'type': 'practice',
                'duration': 75,
                'description': '深入理解JavaScript的异步编程模型，掌握Promise、async/await等现代异步编程技术',
                'language': 'javascript',
                'order': 3
            }
        )
        
        # 创建练习
        practice, _ = Practice.objects.get_or_create(
            chapter=chapter3,
            defaults={
                'question': '编写一个使用Promise和async/await实现的模拟数据获取程序',
                'code_template': '// JavaScript异步编程练习\n\n// 模拟API请求函数\nfunction fetchUserData(userId) {\n    return new Promise((resolve, reject) => {\n        setTimeout(() => {\n            if (userId > 0) {\n                resolve({\n                    id: userId,\n                    name: "用户" + userId,\n                    email: "user" + userId + "@example.com",\n                    posts: [1, 2, 3]\n                });\n            } else {\n                reject(new Error("无效的用户ID"));\n            }\n        }, 1000);\n    });\n}\n\n// 模拟获取用户文章函数\nfunction fetchUserPosts(userId) {\n    return new Promise((resolve, reject) => {\n        setTimeout(() => {\n            resolve([\n                { id: 1, title: "第一篇文章", content: "这是用户" + userId + "的第一篇文章" },\n                { id: 2, title: "第二篇文章", content: "这是用户" + userId + "的第二篇文章" }\n            ]);\n        }, 1500);\n    });\n}\n\n// TODO: 使用Promise链式调用获取用户数据和文章\nfunction getUserWithPostsPromise(userId) {\n    ??\n}\n\n// TODO: 使用async/await重写上述函数\nasync function getUserWithPostsAsync(userId) {\n    ??\n}\n\n// 测试函数\nfunction runTests() {\n    console.log("使用Promise测试:");\n    getUserWithPostsPromise(1)\n        .then(result => console.log("Promise结果:", result))\n        .catch(error => console.error("Promise错误:", error));\n    \n    console.log("使用async/await测试:");\n    (async () => {\n        try {\n            const result = await getUserWithPostsAsync(1);\n            console.log("Async结果:", result);\n        } catch (error) {\n            console.error("Async错误:", error);\n        }\n    })();\n}\n\n// 运行测试\nrunTests();'
            }
        )
        
        # 创建测试用例
        TestCase.objects.get_or_create(
            practice=practice,
            defaults={
                'input_data': 1,
                'expected_output': '{"id":1,"name":"用户1","posts":[{"id":1,"title":"第一篇文章"},{"id":2,"title":"第二篇文章"}]}'
            }
        )
        
        TestCase.objects.get_or_create(
            practice=practice,
            defaults={
                'input_data': -1,
                'expected_output': 'Error: 无效的用户ID'
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
    add_unique_book()
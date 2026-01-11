from django.core.management.base import BaseCommand
from apps.books.models import Book, Chapter, Practice
import json


class Command(BaseCommand):
    help = '修复《大学计算机基础与应用》第1章的练习题'

    def handle(self, *args, **options):
        """修复第1章的练习题"""
        
        try:
            book = Book.objects.get(title="大学计算机基础与应用")
            self.stdout.write(f"找到书籍: {book.title} (ID: {book.id})")
            
            # 查询第1章（按order=1查询）
            chapter1 = Chapter.objects.filter(book=book, order=1).first()
            
            if not chapter1:
                self.stdout.write(self.style.ERROR("错误：找不到第1章！"))
                return
            
            self.stdout.write(f"第1章信息:")
            self.stdout.write(f"  ID: {chapter1.id}")
            self.stdout.write(f"  标题: {chapter1.title}")
            self.stdout.write(f"  序号: {chapter1.order}")
            
            # 检查是否已有练习题
            existing_practices = Practice.objects.filter(chapter=chapter1)
            self.stdout.write(f"现有练习题数量: {existing_practices.count()}")
            
            if existing_practices.exists():
                self.stdout.write(self.style.WARNING("发现已存在的练习题，将删除后重新创建..."))
                existing_practices.delete()
            
            # 创建练习题数据
            questions = [
                {
                    "id": 1,
                    "type": "choice",
                    "title": "计算机系统组成",
                    "question": "计算机系统由哪两大部分组成？",
                    "options": [
                        {"id": "A", "text": "硬件系统和软件系统"},
                        {"id": "B", "text": "输入系统和输出系统"},
                        {"id": "C", "text": "存储系统和处理系统"},
                        {"id": "D", "text": "操作系统和应用系统"}
                    ],
                    "correct_answer": "A",
                    "difficulty": 1,
                    "order": 1
                },
                {
                    "id": 2,
                    "type": "true_false",
                    "title": "CPU功能判断",
                    "question": "CPU是计算机的核心部件，负责执行指令和处理数据。",
                    "correct_answer": True,
                    "difficulty": 1,
                    "order": 2
                },
                {
                    "id": 3,
                    "type": "fill",
                    "title": "内存填空",
                    "question": "计算机的内存分为____和____两种。",
                    "blanks": [
                        {"id": 1, "correct_answer": "RAM", "placeholder": "请输入答案"},
                        {"id": 2, "correct_answer": "ROM", "placeholder": "请输入答案"}
                    ],
                    "difficulty": 2,
                    "order": 3
                },
                {
                    "id": 4,
                    "type": "code_completion",
                    "title": "Python基础",
                    "question": "补全以下代码，输出'Hello, World!'",
                    "code_template": "print('Hello, ___)",
                    "language": "python",
                    "correct_answer": "World!'",
                    "difficulty": 2,
                    "order": 4
                },
                {
                    "id": 5,
                    "type": "programming",
                    "title": "简单计算",
                    "question": "编写一个Python程序，计算并输出1到10的和。",
                    "code_template": "# 在这里编写你的代码\n",
                    "language": "python",
                    "test_cases": [
                        {"input": "", "output": "55", "description": "计算1到10的和"}
                    ],
                    "difficulty": 2,
                    "order": 5
                },
                {
                    "id": 6,
                    "type": "choice",
                    "title": "存储设备",
                    "question": "下列哪个不是计算机的存储设备？",
                    "options": [
                        {"id": "A", "text": "硬盘"},
                        {"id": "B", "text": "内存"},
                        {"id": "C", "text": "CPU"},
                        {"id": "D", "text": "U盘"}
                    ],
                    "correct_answer": "C",
                    "difficulty": 1,
                    "order": 6
                }
            ]
            
            # 创建练习题
            practice = Practice.objects.create(
                chapter=chapter1,
                title=f"{chapter1.title} - 练习题集",
                description=f"《{book.title}》{chapter1.title}的练习题，包含6道不同类型的题目",
                questions=questions,
                language="python",
                difficulty=2,
                order=1
            )
            
            self.stdout.write(self.style.SUCCESS(f"\n成功创建练习题:"))
            self.stdout.write(f"  练习题ID: {practice.id}")
            self.stdout.write(f"  练习题标题: {practice.title}")
            self.stdout.write(f"  题目数量: {len(questions)}")
            
            # 验证创建结果
            self.stdout.write("\n=== 验证练习题 ===")
            practices = Practice.objects.filter(chapter=chapter1)
            self.stdout.write(f"练习题数量: {practices.count()}")
            for p in practices:
                self.stdout.write(f"  - {p.title} (ID: {p.id})")
                if p.questions:
                    if isinstance(p.questions, list):
                        self.stdout.write(f"    题目数量: {len(p.questions)}")
                    elif isinstance(p.questions, str):
                        try:
                            q = json.loads(p.questions)
                            self.stdout.write(f"    题目数量: {len(q) if isinstance(q, list) else 1}")
                        except:
                            self.stdout.write(f"    题目数量: 无法解析")
                    else:
                        self.stdout.write(f"    题目数量: {len(p.questions) if hasattr(p.questions, '__len__') else '未知'}")
            
            self.stdout.write(self.style.SUCCESS("\n修复完成！"))
            
        except Book.DoesNotExist:
            self.stdout.write(self.style.ERROR("错误：找不到《大学计算机基础与应用》这本书!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"发生错误: {e}"))
            import traceback
            traceback.print_exc()


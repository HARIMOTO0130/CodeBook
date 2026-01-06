import os
import sys

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from apps.books.models import Book, Chapter, Practice

def view_books_chapters():
    books = Book.objects.all()
    print(f"找到 {books.count()} 本书籍")
    print("=" * 60)
    
    for book in books:
        print(f"书籍: {book.title} (ID: {book.id})")
        print(f"作者: {book.author}, 章节数: {book.chapters.count()}")
        
        chapters = Chapter.objects.filter(book=book).order_by('order')
        for chapter in chapters:
            practice_count = Practice.objects.filter(chapter=chapter).count()
            print(f"  - 章节: {chapter.title} (ID: {chapter.id})")
            print(f"    类型: {chapter.type}, 顺序: {chapter.order}")
            print(f"    练习题集数: {practice_count}")
            
            # 查看每个练习题集的问题数量
            practices = Practice.objects.filter(chapter=chapter).order_by('order')
            for practice in practices:
                questions_count = len(practice.questions) if practice.questions else 0
                print(f"      * 练习题集: {practice.title} (ID: {practice.id})")
                print(f"        问题数: {questions_count}, 难度: {practice.difficulty}, 语言: {practice.language}")
        
        print("-" * 60)

if __name__ == "__main__":
    view_books_chapters()

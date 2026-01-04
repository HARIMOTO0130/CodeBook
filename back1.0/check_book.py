import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.books.models import Book, Chapter

# 检查《Python编程入门》是否存在
book_exists = Book.objects.filter(title='Python编程入门').exists()
print(f"《Python编程入门》是否存在: {book_exists}")

# 如果存在，显示书籍详情和章节信息
if book_exists:
    book = Book.objects.get(title='Python编程入门')
    print(f"\n书籍详情:")
    print(f"ID: {book.id}")
    print(f"标题: {book.title}")
    print(f"作者: {book.author}")
    print(f"描述: {book.description}")
    print(f"章节数: {book.chapter_count}")
    
    # 显示章节列表
    chapters = Chapter.objects.filter(book=book).order_by('order')
    print(f"\n章节列表 ({chapters.count()}个):")
    for chapter in chapters:
        print(f"- {chapter.order}. {chapter.title} (类型: {chapter.type})")

# 获取所有书籍的概览
all_books = Book.objects.all()
print(f"\n数据库中共有 {all_books.count()} 本书籍")
for b in all_books[:5]:  # 只显示前5本
    print(f"- {b.title} by {b.author}")
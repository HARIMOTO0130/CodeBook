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
from apps.books.models import Book

def check_all_books():
    """检查数据库中所有的书籍记录"""
    # 获取所有书籍
    all_books = Book.objects.all()
    book_count = all_books.count()
    
    print(f"数据库中共有 {book_count} 本书籍")
    
    # 打印每本书的详细信息
    if book_count > 0:
        print("\n书籍列表：")
        for i, book in enumerate(all_books, 1):
            print(f"\n{i}. 标题: {book.title}")
            print(f"   作者: {book.author}")
            print(f"   描述: {book.description}")
            print(f"   标签: {book.tags}")
            print(f"   创建时间: {book.created_at}")
            print(f"   ID: {book.id}")
    else:
        print("数据库中没有书籍记录")

if __name__ == "__main__":
    check_all_books()
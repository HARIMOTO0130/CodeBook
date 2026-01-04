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
from apps.books.models import Book, Chapter

def check_all_chapters():
    """检查数据库中所有书籍的章节内容"""
    print("开始检查所有章节内容...")
    
    # 获取所有书籍
    books = Book.objects.all()
    
    for book in books:
        print(f"\n{'='*50}")
        print(f"书籍: {book.title} (ID: {book.id})")
        print(f"{'='*50}")
        
        # 获取该书籍的所有章节
        chapters = Chapter.objects.filter(book=book).order_by('order')
        
        if chapters.count() > 0:
            print(f"该书籍共有 {chapters.count()} 个章节：\n")
            
            for chapter in chapters:
                print(f"{'-'*40}")
                print(f"章节 {chapter.order}: {chapter.title} (ID: {chapter.id})")
                print(f"类型: {chapter.type}")
                print(f"语言: {chapter.language}")
                print(f"描述: {chapter.description}")
                
                # 只显示content的前100个字符（太长会影响阅读）
                if chapter.content:
                    content_preview = chapter.content[:100] + ('...' if len(chapter.content) > 100 else '')
                    print(f"内容预览: {content_preview}")
                else:
                    print("内容: None")
                
                # 只显示code的前100个字符
                if chapter.code:
                    code_preview = chapter.code[:100] + ('...' if len(chapter.code) > 100 else '')
                    print(f"代码预览: {code_preview}")
                else:
                    print("代码: None")
                
                print(f"{'-'*40}\n")
        else:
            print("该书籍没有章节")
    
    print(f"\n{'='*50}")
    print(f"检查完成！")
    print(f"{'='*50}")

if __name__ == "__main__":
    check_all_chapters()
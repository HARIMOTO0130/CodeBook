import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# 导入模型
from apps.books.models import Practice, Chapter

# 查询所有Practice数据
practices = Practice.objects.all().values('id', 'title', 'language')

print('练习题语言分布：')
for p in practices:
    print(f'ID: {p["id"]}, 标题: {p["title"]}, 语言: {p["language"]}')

# 查询Practice关联的Chapter和Book信息
print('\n练习题详细信息（含章节和书籍）：')
practices_with_related = Practice.objects.select_related('chapter', 'chapter__book')
for practice in practices_with_related:
    book_title = practice.chapter.book.title if practice.chapter and practice.chapter.book else '未知书籍'
    chapter_title = practice.chapter.title if practice.chapter else '未知章节'
    print(f'练习ID: {practice.id}, 标题: {practice.title}, 语言: {practice.language}, 章节: {chapter_title}, 书籍: {book_title}')

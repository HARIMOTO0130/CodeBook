# -*- coding: utf-8 -*-
"""检查数据库中的编码问题"""
from django.core.management.base import BaseCommand
from apps.books.models import Book, Chapter, Practice
from django.db import connection


class Command(BaseCommand):
    help = '检查数据库中的中文编码问题'

    def handle(self, *args, **options):
        self.stdout.write('正在检查数据库编码...')
        
        # 检查数据库连接字符集
        with connection.cursor() as cursor:
            cursor.execute("SHOW VARIABLES LIKE 'character_set%'")
            for row in cursor.fetchall():
                self.stdout.write(f'{row[0]}: {row[1]}')
        
        # 检查书籍数据
        self.stdout.write('\n检查书籍数据:')
        books = Book.objects.all()
        for book in books:
            title = book.title
            author = book.author
            # 尝试检测是否是乱码
            try:
                # 如果字符串包含很多乱码字符，可能是编码问题
                title_encoded = title.encode('utf-8')
                author_encoded = author.encode('utf-8')
                self.stdout.write(f'  书籍 ID {book.id}:')
                self.stdout.write(f'    标题: {title}')
                self.stdout.write(f'    作者: {author}')
                self.stdout.write(f'    标题 UTF-8 字节: {title_encoded}')
                self.stdout.write(f'    作者 UTF-8 字节: {author_encoded}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'  书籍 ID {book.id} 编码错误: {e}'))
        
        self.stdout.write('\n检查完成！')



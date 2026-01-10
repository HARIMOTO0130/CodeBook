from django.core.management.base import BaseCommand
from apps.books.models import Book, Chapter, Practice


class Command(BaseCommand):
    help = '验证所有章节都有练习题'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== 书籍列表 ==='))
        books = Book.objects.all()
        for i, book in enumerate(books):
            self.stdout.write(f'{i+1}. {book.title} - {book.chapter_count}章')

        self.stdout.write('\n=== 练习题统计 ===')
        total_practices = Practice.objects.count()
        self.stdout.write(f'总练习题数量: {total_practices}')

        self.stdout.write('\n=== 各章节练习题情况 ===')
        total_chapters = 0
        chapters_with_practice = 0
        chapters_without_practice = []

        for book in books:
            chapters = Chapter.objects.filter(book=book)
            self.stdout.write(f'\n书籍: {book.title}')
            for chapter in chapters:
                total_chapters += 1
                has_practice = chapter.practices.exists()
                if has_practice:
                    chapters_with_practice += 1
                    self.stdout.write(self.style.SUCCESS(f'  [OK] {chapter.title}'))
                else:
                    chapters_without_practice.append(f'{book.title} - {chapter.title}')
                    self.stdout.write(self.style.ERROR(f'  [MISSING] {chapter.title}'))

        self.stdout.write('\n=== 总结 ===')
        self.stdout.write(f'总章节数: {total_chapters}')
        self.stdout.write(self.style.SUCCESS(f'有练习题的章节: {chapters_with_practice}'))
        self.stdout.write(self.style.ERROR(f'缺少练习题的章节: {len(chapters_without_practice)}'))

        if chapters_without_practice:
            self.stdout.write('\n缺少练习题的章节列表:')
            for chapter in chapters_without_practice:
                self.stdout.write(self.style.ERROR(f'  - {chapter}'))
        else:
            self.stdout.write(self.style.SUCCESS('\n所有章节都有练习题！'))

import json
from django.core.management.base import BaseCommand, CommandError
from apps.books.models import Book, Chapter


class Command(BaseCommand):
    help = 'Import books and chapters from a JSON file.'

    def add_arguments(self, parser):
        parser.add_argument('json_path', type=str, help='Path to JSON file describing books and chapters')
        parser.add_argument('--update', action='store_true', help='Update existing books matched by title+author')

    def handle(self, *args, **options):
        json_path = options['json_path']
        allow_update = options['update']

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise CommandError(f'File not found: {json_path}')
        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON: {e}')

        books = data if isinstance(data, list) else data.get('books', [])
        if not isinstance(books, list) or not books:
            raise CommandError('JSON must contain a non-empty list under key "books" or be a list of book objects')

        created_books = 0
        updated_books = 0
        created_chapters = 0

        for b in books:
            title = (b.get('title') or '').strip()
            author = (b.get('author') or '').strip() or '未知作者'
            description = b.get('description') or ''
            tags = b.get('tags') or []
            chapters = b.get('chapters') or []

            if not title:
                self.stdout.write(self.style.WARNING('Skip a book with empty title'))
                continue

            book = None
            if allow_update:
                book = Book.objects.filter(title=title, author=author).first()

            if book is None:
                book = Book.objects.create(
                    title=title,
                    author=author,
                    description=description,
                )
                try:
                    book.tag_list = list(tags) if isinstance(tags, list) else []
                    book.save()
                except Exception:
                    # ignore invalid tag formats
                    pass
                created_books += 1
                self.stdout.write(self.style.SUCCESS(f'Created book: {book.title}'))
            else:
                # update basic fields
                book.description = description
                try:
                    book.tag_list = list(tags) if isinstance(tags, list) else []
                except Exception:
                    pass
                book.save()
                updated_books += 1
                self.stdout.write(self.style.SUCCESS(f'Updated book: {book.title}'))

            # Import chapters
            order_counter = 1
            for ch in chapters:
                ch_title = (ch.get('title') or '').strip()
                if not ch_title:
                    self.stdout.write(self.style.WARNING('  - Skip a chapter with empty title'))
                    continue

                ch_type = (ch.get('type') or 'reading').lower()
                if ch_type not in ('reading', 'video', 'practice'):
                    ch_type = 'reading'

                chapter, _created = Chapter.objects.get_or_create(
                    book=book,
                    title=ch_title,
                    defaults={
                        'type': ch_type,
                        'duration': int(ch.get('duration') or 30),
                        'description': ch.get('description') or '',
                        'content': ch.get('content') or '',
                        'code': ch.get('code') or '',
                        'language': (ch.get('language') or 'python').lower(),
                        'video_url': ch.get('video_url') or ch.get('videoUrl') or None,
                        'order': int(ch.get('order') or order_counter),
                    }
                )

                if not _created and allow_update:
                    # update fields when --update
                    chapter.type = ch_type
                    chapter.duration = int(ch.get('duration') or chapter.duration or 30)
                    chapter.description = ch.get('description') or chapter.description
                    chapter.content = ch.get('content') or chapter.content
                    chapter.code = ch.get('code') or chapter.code
                    chapter.language = (ch.get('language') or chapter.language or 'python').lower()
                    chapter.video_url = ch.get('video_url') or ch.get('videoUrl') or chapter.video_url
                    chapter.order = int(ch.get('order') or chapter.order or order_counter)
                    chapter.save()

                if _created:
                    created_chapters += 1
                    self.stdout.write(self.style.NOTICE(f'  - Added chapter: {chapter.title}'))

                order_counter += 1

            # refresh chapter_count
            book.save()

        self.stdout.write(self.style.SUCCESS(
            f'Import done. Books created: {created_books}, updated: {updated_books}, chapters created: {created_chapters}'
        ))



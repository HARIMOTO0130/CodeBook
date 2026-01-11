from django.core.management.base import BaseCommand
from apps.books.models import Practice
from django.db.models import Count


class Command(BaseCommand):
    help = 'Check practice questions per chapter'

    def handle(self, *args, **options):
        chapter_practices = Practice.objects.values('chapter_id').annotate(count=Count('id')).order_by('chapter_id')
        self.stdout.write('Chapter practices:')
        for cp in chapter_practices:
            self.stdout.write(f'Chapter {cp["chapter_id"]}: {cp["count"]} practices')

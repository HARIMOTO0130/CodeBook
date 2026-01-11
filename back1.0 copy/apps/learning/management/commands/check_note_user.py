from django.core.management.base import BaseCommand
from apps.learning.models import Note, NoteVersion
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = '检查笔记用户信息'

    def handle(self, *args, **options):
        note = Note.objects.get(id=14)
        self.stdout.write(f'笔记ID: {note.id}')
        self.stdout.write(f'笔记标题: {note.title}')
        self.stdout.write(f'笔记用户ID: {note.user_id}')
        self.stdout.write(f'笔记用户名: {note.user.username}')
        self.stdout.write(f'所有用户:')
        for user in User.objects.all():
            self.stdout.write(f'  - ID: {user.id}, 用户名: {user.username}')

from django.core.management.base import BaseCommand
from apps.learning.models import Note, NoteVersion
from apps.learning.serializers import NoteVersionSerializer

class Command(BaseCommand):
    help = '检查笔记版本数据'

    def handle(self, *args, **options):
        note = Note.objects.get(id=14)
        self.stdout.write(f'笔记ID: {note.id}')
        self.stdout.write(f'笔记标题: {note.title}')
        self.stdout.write(f'笔记版本数: {note.versions.count()}')
        self.stdout.write('所有版本:')
        for v in note.versions.all():
            self.stdout.write(f'  - ID: {v.id}, 版本号: {v.version_number}, 标题: {v.title}, 创建时间: {v.created_at}')
            self.stdout.write(f'    内容长度: {len(v.content) if v.content else 0}')
            self.stdout.write(f'    内容预览: {v.content[:100] if v.content else "None"}')
            try:
                serializer = NoteVersionSerializer(v)
                self.stdout.write(f'    序列化测试: 成功')
                self.stdout.write(f'    序列化数据: {serializer.data}')
            except Exception as e:
                self.stdout.write(f'    序列化测试: 失败 - {e}')

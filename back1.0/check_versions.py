from apps.learning.models import Note, NoteVersion
from apps.learning.serializers import NoteVersionSerializer

note = Note.objects.get(id=14)
print('笔记ID:', note.id)
print('笔记标题:', note.title)
print('笔记版本数:', note.versions.count())
print('所有版本:')
for v in note.versions.all():
    print(f'  - ID: {v.id}, 版本号: {v.version_number}, 标题: {v.title}, 创建时间: {v.created_at}')
    print(f'    内容长度: {len(v.content) if v.content else 0}')
    print(f'    内容预览: {v.content[:100] if v.content else "None"}')
    try:
        serializer = NoteVersionSerializer(v)
        print(f'    序列化测试: 成功')
        print(f'    序列化数据: {serializer.data}')
    except Exception as e:
        print(f'    序列化测试: 失败 - {e}')

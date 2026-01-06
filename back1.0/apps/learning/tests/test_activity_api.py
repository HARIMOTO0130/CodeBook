from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from apps.books.models import Book, Chapter
from apps.learning.models import LearningRecord, PracticeRecord
from datetime import datetime, timedelta


class LearningActivityAPITestCase(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='student1', password='pass1234')
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

        # 创建书籍与章节
        self.book = Book.objects.create(title='测试书籍', author='Author', description='desc')
        self.chapter_reading = Chapter.objects.create(
            book=self.book,
            title='阅读章节',
            type='reading',
            description='desc',
            content='',
            code='',
            language='python'
        )
        self.chapter_practice = Chapter.objects.create(
            book=self.book,
            title='练习章节',
            type='practice',
            description='desc',
            content='',
            code='',
            language='python'
        )

        # 创建学习记录
        LearningRecord.objects.create(
            user=self.user,
            book=self.book,
            chapter=self.chapter_reading,
            progress=80
        )

        # 创建练习记录
        PracticeRecord.objects.create(
            user=self.user,
            book=self.book,
            chapter=self.chapter_practice,
            score=90,
            completed=True,
            user_code='print("hi")'
        )

    def test_activity_list(self):
        url = reverse('learning-record-activity')
        res = self.client.get(url)
        self.assertEqual(res.status_code, 200)
        self.assertIn('results', res.data)
        self.assertGreaterEqual(res.data.get('count', 0), 2)
        types = {item['type'] for item in res.data['results']}
        self.assertTrue({'reading', 'practice'}.issubset(types))

    def test_filter_type(self):
        url = reverse('learning-record-activity')
        res = self.client.get(url, {'type': 'practice'})
        self.assertEqual(res.status_code, 200)
        results = res.data['results']
        self.assertTrue(all(r['type'] == 'practice' for r in results))

    def test_date_filter(self):
        url = reverse('learning-record-activity')
        today = datetime.utcnow().date().isoformat()
        res = self.client.get(url, {'start_date': today, 'end_date': today})
        self.assertEqual(res.status_code, 200)
        self.assertGreaterEqual(res.data.get('count', 0), 0)



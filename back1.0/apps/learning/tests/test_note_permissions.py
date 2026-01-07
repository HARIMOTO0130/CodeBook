from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from apps.learning.models import Note


class NotePermissionTestCase(APITestCase):
    def setUp(self):
        User = get_user_model()
        
        # 清除所有现有笔记和用户，确保测试环境干净
        Note.objects.all().delete()
        User.objects.all().delete()
        
        # 创建两个测试用户
        self.user1 = User.objects.create_user(username='student1', email='student1@example.com', password='pass1234')
        self.user2 = User.objects.create_user(username='student2', email='student2@example.com', password='pass1234')
        
        # 创建两个测试客户端，分别认证为不同用户
        self.client1 = APIClient()
        self.client1.force_authenticate(user=self.user1)
        
        self.client2 = APIClient()
        self.client2.force_authenticate(user=self.user2)
        
        # 创建测试笔记
        self.note1 = Note.objects.create(
            title='用户1的笔记',
            content='这是用户1的笔记内容',
            user=self.user1
        )
        
        self.note2 = Note.objects.create(
            title='用户2的笔记',
            content='这是用户2的笔记内容',
            user=self.user2
        )
    
    def test_get_queryset_filters_user_notes(self):
        """测试get_queryset方法仅返回当前用户的笔记"""
        # 验证用户1只能看到自己的笔记
        response = self.client1.get(reverse('note-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 简单验证：响应中应该包含用户1的笔记
        self.assertIn(self.note1.title, str(response.data))
        # 简单验证：响应中不应该包含用户2的笔记
        self.assertNotIn(self.note2.title, str(response.data))
        
        # 验证用户2只能看到自己的笔记
        response = self.client2.get(reverse('note-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 简单验证：响应中应该包含用户2的笔记
        self.assertIn(self.note2.title, str(response.data))
        # 简单验证：响应中不应该包含用户1的笔记
        self.assertNotIn(self.note1.title, str(response.data))
    
    def test_retrieve_own_note_permitted(self):
        """测试用户可以查看自己的笔记"""
        response = self.client1.get(reverse('note-detail', kwargs={'pk': self.note1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], self.note1.id)
    
    def test_retrieve_other_user_note_forbidden(self):
        """测试用户无法查看其他用户的笔记"""
        response = self.client1.get(reverse('note-detail', kwargs={'pk': self.note2.id}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_update_own_note_permitted(self):
        """测试用户可以更新自己的笔记"""
        data = {'title': '更新后的标题', 'content': '更新后的内容'}
        response = self.client1.put(reverse('note-detail', kwargs={'pk': self.note1.id}), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], '更新后的标题')
    
    def test_update_other_user_note_forbidden(self):
        """测试用户无法更新其他用户的笔记"""
        data = {'title': '非法更新', 'content': '非法内容'}
        response = self.client1.put(reverse('note-detail', kwargs={'pk': self.note2.id}), data)
        # 由于get_queryset的过滤，其他用户的笔记会返回404而不是403，这是更安全的做法
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_delete_own_note_permitted(self):
        """测试用户可以删除自己的笔记"""
        response = self.client1.delete(reverse('note-detail', kwargs={'pk': self.note1.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # 验证笔记已被删除
        self.assertFalse(Note.objects.filter(id=self.note1.id).exists())
    
    def test_delete_other_user_note_forbidden(self):
        """测试用户无法删除其他用户的笔记"""
        response = self.client1.delete(reverse('note-detail', kwargs={'pk': self.note2.id}))
        # 由于get_queryset的过滤，其他用户的笔记会返回404而不是403，这是更安全的做法
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_versions_action_permission(self):
        """测试versions操作的权限控制"""
        # 用户1可以查看自己笔记的版本
        response = self.client1.get(reverse('note-versions', kwargs={'pk': self.note1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 用户1无法查看用户2笔记的版本
        response = self.client1.get(reverse('note-versions', kwargs={'pk': self.note2.id}))
        # 由于get_queryset的过滤，其他用户的笔记会返回404而不是403，这是更安全的做法
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    


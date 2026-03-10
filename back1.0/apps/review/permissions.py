# -*- coding: utf-8 -*-
"""审核模块权限控制"""
from rest_framework import permissions


class IsReviewer(permissions.BasePermission):
    """检查用户是否为审核员"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'reviewer'


class CanAccessContent(permissions.BasePermission):
    """
    内容访问控制权限
    
    审核人员可以访问：
    - 教材基本信息（标题、作者、版本等）
    - 教材元数据（字数、章节数等）
    - 教材描述和摘要
    - 修改历史和教师信息
    
    审核人员不能访问：
    - 教材正文内容（章节详细内容）
    - 代码示例
    - 教材附件文件
    """
    
    ALLOWED_FIELDS = {
        'book': [
            'id', 'title', 'subtitle', 'author', 'isbn', 'language',
            'word_count', 'chapter_count', 'version_number', 'description',
            'category', 'tags', 'status', 'created_at', 'updated_at'
        ],
        'chapter': [
            'id', 'title', 'order', 'word_count', 'created_at', 'updated_at'
        ]
    }
    
    RESTRICTED_FIELDS = {
        'book': ['content', 'file_url', 'attachment'],
        'chapter': ['content', 'code_examples', 'file_url']
    }
    
    def has_permission(self, request, view):
        """检查基本权限"""
        if not request.user.is_authenticated:
            return False
        
        # 审核员有基本访问权限
        if request.user.role == 'reviewer':
            return True
        
        # 其他角色需要检查具体权限
        return request.user.is_staff or request.user.is_superuser
    
    def has_object_permission(self, request, view, obj):
        """检查对象级别权限"""
        if not request.user.is_authenticated:
            return False
        
        # 超级管理员有完全访问权限
        if request.user.is_superuser:
            return True
        
        # 审核员有受限访问权限
        if request.user.role == 'reviewer':
            return self._check_reviewer_access(request, view, obj)
        
        # 其他角色
        return request.user.is_staff
    
    def _check_reviewer_access(self, request, view, obj):
        """检查审核员的访问权限"""
        # 只允许GET、HEAD、OPTIONS请求
        if request.method not in permissions.SAFE_METHODS:
            return False
        
        # 检查是否在审核任务中
        from .models import ReviewTask
        task_exists = ReviewTask.objects.filter(
            book_id=getattr(obj, 'id', None),
            assigned_reviewer=request.user
        ).exists()
        
        if not task_exists:
            # 如果没有被指派，只能访问基本信息
            return True
        
        return True


class ContentAccessMixin:
    """内容访问控制混入类"""
    
    def get_serializer_context(self):
        """添加用户角色信息到序列化器上下文"""
        context = super().get_serializer_context()
        context['user_role'] = self.request.user.role if self.request.user.is_authenticated else None
        context['is_reviewer'] = self.request.user.role == 'reviewer' if self.request.user.is_authenticated else False
        return context
    
    def get_serializer(self, *args, **kwargs):
        """根据用户角色返回不同的序列化器"""
        serializer_class = self.get_serializer_class()
        
        # 如果是审核员，使用受限序列化器
        if hasattr(self.request.user, 'role') and self.request.user.role == 'reviewer':
            kwargs['context'] = self.get_serializer_context()
        
        return serializer_class(*args, **kwargs)


class ReviewTaskAccessControl(permissions.BasePermission):
    """审核任务访问控制"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        # 审核员可以访问任务列表和详情
        if request.user.role == 'reviewer':
            return True
        
        # 管理员有完全权限
        return request.user.is_staff or request.user.is_superuser
    
    def has_object_permission(self, request, view, obj):
        """对象级别权限控制"""
        if not request.user.is_authenticated:
            return False
        
        # 超级管理员有完全权限
        if request.user.is_superuser:
            return True
        
        # 审核员只能操作自己被指派的任务
        if request.user.role == 'reviewer':
            # 查看权限：所有审核员都可以查看
            if request.method in permissions.SAFE_METHODS:
                return True
            
            # 修改权限：只能修改自己被指派的任务
            if obj.assigned_reviewer == request.user:
                return True
            
            # 认领权限：待审核状态的任务
            if view.action == 'claim' and obj.status == 'pending':
                return True
            
            return False
        
        return request.user.is_staff


def filter_content_for_reviewer(data, content_type='book'):
    """
    过滤内容，移除审核员不应访问的敏感字段
    
    Args:
        data: 原始数据字典
        content_type: 内容类型 ('book' 或 'chapter')
    
    Returns:
        过滤后的数据字典
    """
    if not isinstance(data, dict):
        return data
    
    restricted_fields = {
        'book': ['content', 'file_url', 'attachment', 'full_text', 'raw_content'],
        'chapter': ['content', 'code_examples', 'file_url', 'full_text', 'raw_content', 'code']
    }
    
    fields_to_remove = restricted_fields.get(content_type, [])
    
    filtered_data = data.copy()
    for field in fields_to_remove:
        if field in filtered_data:
            filtered_data[field] = '[内容已隐藏 - 审核员无访问权限]'
    
    return filtered_data

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建测试Jupyter文档的脚本
"""

import os
django_settings = 'config.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', django_settings)

import django
django.setup()

from apps.learning.models import JupyterDocument
from apps.users.models import User

# 获取或创建用户
user = User.objects.first()
if not user:
    user = User.objects.create_user('testuser', 'test@example.com', 'password')
    print("创建了测试用户: testuser")
else:
    print(f"使用现有用户: {user.username}")

# 创建测试文档
content = '''[
    {
        "id": "1",
        "type": "markdown",
        "content": "# 欢迎使用Jupyter笔记本\n\n这是一个测试文档"
    },
    {
        "id": "2", 
        "type": "code",
        "content": "print(\"Hello, World!\")",
        "language": "python"
    }
]'''

doc = JupyterDocument.objects.create(
    user=user,
    title='测试Jupyter文档',
    content=content,
    is_public=True
)

print(f"创建了测试文档，ID: {doc.id}，标题: {doc.title}")
print(f"现在可以通过 /learning/jupyter-documents/{doc.id}/ 访问此文档")

# 列出所有文档
print("\n当前所有Jupyter文档:")
for d in JupyterDocument.objects.all():
    print(f"- ID: {d.id}, 标题: {d.title}, 用户: {d.user.username}")
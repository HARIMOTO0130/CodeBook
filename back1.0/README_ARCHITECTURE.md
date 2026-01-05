# CodeBook+ 后端架构说明

## 项目架构

本项目采用多端架构设计，支持三个不同的用户角色：
- **学生端（Student）**：学习中心、教材学习、练习与实战等
- **教师端（Teacher）**：班级管理、教学管理、作业管理等
- **教材提供者端（Provider）**：工具箱、书籍管理、内容编辑等

## API路径结构

### 学生端API (`/api/student/`)
- `/api/student/books/` - 书籍浏览（只读）
- `/api/student/learning/` - 学习记录、练习、笔记等
- `/api/student/users/` - 用户相关（登录、注册、个人信息）

### 教师端API (`/api/teacher/`)
- `/api/teacher/classes/` - 班级管理
- `/api/teacher/assignments/` - 作业管理
- `/api/teacher/students/` - 学生管理
- `/api/teacher/analytics/` - 数据分析
- `/api/teacher/resources/` - 教学资源
- `/api/teacher/notifications/` - 消息通知

### 教材提供者端API (`/api/provider/`)
- `/api/provider/books/` - 书籍管理（创建、编辑、删除）
- `/api/provider/toolkit/` - 工具箱管理

### 兼容性
为了保持向后兼容，旧版API路径仍然可用：
- `/api/books/` → 等同于 `/api/student/books/`
- `/api/learning/` → 等同于 `/api/student/learning/`
- `/api/users/` → 等同于 `/api/student/users/`
- `/api/toolkit/` → 等同于 `/api/provider/toolkit/`

## 应用结构

```
apps/
├── users/          # 用户管理（所有端共用）
├── books/          # 书籍管理（学生端浏览，提供者端管理）
├── learning/       # 学习相关（学生端）
├── teacher/        # 教师端功能
└── toolkit/        # 工具箱（教材提供者端）
```

## 权限控制

各端API应通过以下方式控制权限：
1. 用户角色验证（role字段）
2. Django权限系统
3. 视图级别的权限检查

## 开发指南

### 添加新的API端点
1. 在对应的app下创建或更新views
2. 在对应的urls.py中添加路由
3. 确保路径前缀正确（`/api/student/`, `/api/teacher/`, `/api/provider/`）

### 权限检查示例
```python
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes

@permission_classes([IsAuthenticated])
def your_view(request):
    # 检查用户角色
    if request.user.role != 'student':
        return Response({'error': '权限不足'}, status=403)
    # ...
```


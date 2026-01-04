# CodeBook+ 后端项目

这是CodeBook+交互式计算机教育数字教材平台的后端服务，使用Django和Django REST Framework构建。

## 技术栈

- Python 3.8+
- Django 4.2.7
- Django REST Framework 3.14.0
- SQLite (开发环境) / PostgreSQL (生产环境推荐)
- JWT认证
- CORS支持

## 项目结构

```
back1.0/
├── config/               # Django配置目录
│   ├── __init__.py
│   ├── settings.py       # 项目配置
│   ├── urls.py           # URL路由配置
│   └── wsgi.py           # WSGI应用
├── apps/                 # 应用目录
│   ├── __init__.py
│   ├── users/            # 用户管理应用
│   ├── books/            # 教材管理应用
│   └── learning/         # 学习记录应用
├── .env                  # 环境变量配置
├── .gitignore            # Git忽略文件
├── initial_data.py       # 初始数据脚本
├── manage.py             # Django管理脚本
└── requirements.txt      # 项目依赖
```

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置环境变量

复制并编辑`.env`文件，修改必要的配置：

```
SECRET_KEY='your-secret-key-please-change-in-production'
DEBUG=True
ALLOWED_HOSTS=*
```

### 3. 数据库迁移

```bash
# 创建数据库迁移
python manage.py makemigrations

# 应用数据库迁移
python manage.py migrate
```

### 4. 创建超级用户

```bash
python manage.py createsuperuser
```

### 5. 导入初始数据（可选）

```bash
python initial_data.py
```

这将创建测试用户和示例教材数据。

### 6. 运行开发服务器

```bash
python manage.py runserver
```

服务器将在 http://127.0.0.1:8000/ 启动

## API 端点

### 用户相关
- `POST /api/auth/register/` - 用户注册
- `POST /api/auth/login/` - 用户登录
- `POST /api/auth/logout/` - 用户登出
- `GET /api/auth/me/` - 获取当前用户信息
- `PUT /api/auth/preferences/` - 更新用户偏好设置

### 教材相关
- `GET /api/books/books/` - 获取书籍列表
- `GET /api/books/books/<id>/` - 获取书籍详情
- `GET /api/books/chapters/<id>/` - 获取章节详情
- `GET /api/books/chapters/book/<book_id>/` - 获取指定书籍的所有章节

### 学习记录相关
- `GET /api/learning/records/` - 获取学习记录
- `POST /api/learning/save-progress/` - 保存学习进度
- `POST /api/learning/practice-submit/` - 提交练习结果
- `GET /api/learning/heatmap/` - 获取学习热力图数据

## 前后端连接说明

要将前端Vue项目与本后端连接，需要进行以下配置：

### 前端配置

1. 修改前端项目中的API基础URL，指向Django后端：

```javascript
// 在前端项目的api.js文件中
const API_BASE_URL = 'http://localhost:8000/api';

// 然后将所有API调用改为使用这个基础URL
```

2. 处理认证：前端需要在请求头中包含认证信息

```javascript
// 登录后保存token
localStorage.setItem('token', response.data.token);

// 在API请求中添加认证头
const headers = {
  'Authorization': `Token ${localStorage.getItem('token')}`
};
```

### 后端配置

确保在`settings.py`中正确配置了CORS，允许前端域名访问：

```python
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',  # Vite默认端口
    # 添加其他需要允许的域名
]
```

## 开发说明

1. 添加新功能时，请按照Django应用的标准结构创建相应的模型、视图和URL
2. 遵循RESTful API设计原则
3. 为所有API端点添加适当的权限控制
4. 使用Django的ORM进行数据库操作，避免直接编写SQL

## 部署说明

生产环境部署时，建议：

1. 使用PostgreSQL或MySQL替代SQLite
2. 设置`DEBUG=False`
3. 配置适当的`ALLOWED_HOSTS`
4. 使用Gunicorn/uWSGI作为WSGI服务器
5. 使用Nginx作为反向代理
6. 设置HTTPS
7. 配置适当的日志记录
8. 使用环境变量管理敏感配置
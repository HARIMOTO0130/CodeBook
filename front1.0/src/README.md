# CodeBook+ 前端项目结构说明

## 项目架构

本项目采用多端架构设计，支持三个不同的用户角色：
- **学生端（Student）**：学习中心、教材学习、练习与实战等
- **教师端（Teacher）**：班级管理、教学管理、作业管理等
- **教材提供者端（Provider）**：工具箱、书籍管理、内容编辑等

## 目录结构

```
src/
├── student/              # 学生端模块
│   ├── api/             # 学生端API接口
│   ├── components/      # 学生端组件
│   ├── views/           # 学生端页面视图
│   └── router/          # 学生端路由配置
│
├── teacher/             # 教师端模块
│   ├── api/             # 教师端API接口
│   ├── components/      # 教师端组件
│   ├── views/           # 教师端页面视图
│   ├── router/          # 教师端路由配置
│   ├── constants/       # 常量定义
│   └── utils/           # 工具函数
│
├── provider/            # 教材提供者端模块
│   ├── api/             # 教材提供者端API接口
│   ├── components/      # 教材提供者端组件
│   ├── views/           # 教材提供者端页面视图
│   └── router/          # 教材提供者端路由配置
│
├── api/                 # 共享API接口（兼容旧版）
├── components/          # 共享组件（兼容旧版）
├── views/               # 共享视图（404等）
├── router/              # 主路由配置（整合所有端）
├── styles/              # 全局样式
└── utils/               # 共享工具函数
```

## 路由说明

### 路由前缀
- 学生端：`/student/*`
- 教师端：`/teacher/*`
- 教材提供者端：`/provider/*`

### 默认入口
访问根路径 `/` 会自动重定向到 `/student/books`

## 开发指南

### 添加新页面
1. 在对应端的 `views/` 目录下创建Vue组件
2. 在对应端的 `router/index.js` 中添加路由配置
3. 确保路由meta中包含正确的 `role` 字段

### 添加新组件
1. 在对应端的 `components/` 目录下创建组件
2. 如果是共享组件，放在根目录的 `components/` 下

### API调用
- 学生端API：`/api/student/*`
- 教师端API：`/api/teacher/*`
- 教材提供者端API：`/api/provider/*`

## 权限控制

路由守卫会自动检查：
1. 用户是否已登录（`requiresAuth`）
2. 用户角色是否匹配（`role`）

用户角色存储在 `localStorage` 的 `userRole` 字段中。


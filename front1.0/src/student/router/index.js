import { createRouter, createWebHistory } from 'vue-router'

// 导入学生端视图组件
const BooksView = () => import('../views/BooksView.vue')
const BookOutlineView = () => import('../views/BookOutlineView.vue')
const LearnView = () => import('../views/LearnView.vue')
const FullCodeView = () => import('../../views/FullCodeView.vue')
const RecordsView = () => import('../views/RecordsView.vue')
const SettingsView = () => import('../views/SettingsView.vue')
const ToolKitView = () => import('../../views/ToolKitView.vue')
const LearningPathView = () => import('../views/LearningPathView.vue')
const PracticeView = () => import('../views/PracticeView.vue')
const JupyterNotebookView = () => import('../views/JupyterNotebookView.vue')
const JupyterDocumentsListView = () => import('../views/JupyterDocumentsListView.vue')

// 新增视图组件导入
const ClassView = () => import('../views/ClassView.vue')
const HomeworksView = () => import('../views/HomeworksView.vue')
const HomeworkDetailView = () => import('../views/HomeworkDetailView.vue')
const ResourcesView = () => import('../views/ResourcesView.vue')
const NoticesView = () => import('../views/NoticesView.vue')

// 学生端路由配置
const studentRoutes = [
  {
    path: '/student',
    redirect: '/student/books'
  },
  {
    path: '/student/books',
    name: 'StudentBooks',
    component: BooksView,
    meta: { title: '教材书架', role: 'student' }
  },
  {
    path: '/student/books/:bookId',
    name: 'StudentBookOutline',
    component: BookOutlineView,
    meta: { title: '章节大纲', role: 'student' },
    props: true
  },
  {
    path: '/student/books/:bookId/chapter/:chapterId',
    name: 'StudentLearning',
    component: LearnView,
    meta: { title: '学习页', role: 'student' },
    props: true
  },
  {
    path: '/student/fullcode',
    name: 'StudentFullCode',
    component: FullCodeView,
    meta: { title: '代码全屏', role: 'student' }
  },
  {
    path: '/student/profile/records',
    name: 'StudentRecords',
    component: RecordsView,
    meta: { title: '学习记录', requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/profile/settings',
    name: 'StudentSettings',
    component: SettingsView,
    meta: { title: '设置', requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/toolkit',
    name: 'StudentToolKit',
    component: ToolKitView,
    meta: { title: '轻量化工具包', role: 'student' }
  },
  {
    path: '/student/learning-paths',
    name: 'StudentLearningPath',
    component: LearningPathView,
    meta: { title: '学习路线图', role: 'student' }
  },
  {
    path: '/student/practice',
    name: 'StudentPractice',
    component: PracticeView,
    meta: { title: '练习题', role: 'student' },
    // 兼容从章节页或书籍页进入练习的多种路径，避免因路径不同触发404
    alias: [
      '/student/practice/',
      '/student/books/:bookId/practice',
      '/student/books/:bookId/chapter/:chapterId/practice'
    ]
  },
  {
    path: '/student/jupyter',
    name: 'StudentJupyterDocumentsList',
    component: JupyterDocumentsListView,
    meta: { title: 'Jupyter文档列表', requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/jupyter/new',
    name: 'StudentJupyterNotebookNew',
    component: JupyterNotebookView,
    meta: { title: '新建Jupyter文档', requiresAuth: true, role: 'student' },
    props: { documentId: null }
  },
  {
    path: '/student/jupyter/:documentId',
    name: 'StudentJupyterNotebook',
    component: JupyterNotebookView,
    meta: { title: '编辑Jupyter文档', requiresAuth: true, role: 'student' },
    props: true
  },
  // 新增班级相关路由
  {
    path: '/student/class',
    name: 'StudentClass',
    component: ClassView,
    meta: { title: '我的班级', requiresAuth: true, role: 'student' }
  },
  // 新增作业相关路由
  {
    path: '/student/homeworks',
    name: 'StudentHomeworks',
    component: HomeworksView,
    meta: { title: '我的作业', requiresAuth: true, role: 'student' }
  },
  {
    path: '/student/homeworks/:homeworkId',
    name: 'StudentHomeworkDetail',
    component: HomeworkDetailView,
    meta: { title: '作业详情', requiresAuth: true, role: 'student' },
    props: true
  },
  // 新增资源相关路由
  {
    path: '/student/resources',
    name: 'StudentResources',
    component: ResourcesView,
    meta: { title: '学习资源', requiresAuth: true, role: 'student' }
  },
  // 新增通知相关路由
  {
    path: '/student/notices',
    name: 'StudentNotices',
    component: NoticesView,
    meta: { title: '通知消息', requiresAuth: true, role: 'student' }
  }
]

export default studentRoutes

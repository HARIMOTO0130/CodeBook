import { createRouter, createWebHistory } from 'vue-router'

// 导入学生端视图组件
const BooksView = () => import('../views/BooksView.vue')
const BookOutlineView = () => import('../views/BookOutlineView.vue')
const LearnView = () => import('../views/LearnView.vue')
const FullCodeView = () => import('../views/FullCodeView.vue')
const RecordsView = () => import('../views/RecordsView.vue')
const SettingsView = () => import('../views/SettingsView.vue')
const ToolKitView = () => import('../views/ToolKitView.vue')
const LoginView = () => import('../views/LoginView.vue')
const RegisterView = () => import('../views/RegisterView.vue')
const LearningPathView = () => import('../views/LearningPathView.vue')
const PracticeView = () => import('../views/PracticeView.vue')
const JupyterNotebookView = () => import('../views/JupyterNotebookView.vue')
const JupyterDocumentsListView = () => import('../views/JupyterDocumentsListView.vue')

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
    path: '/student/login',
    name: 'StudentLogin',
    component: LoginView,
    meta: { title: '登录', role: 'student' }
  },
  {
    path: '/student/register',
    name: 'StudentRegister',
    component: RegisterView,
    meta: { title: '注册', role: 'student' }
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
    meta: { title: '练习题', role: 'student' }
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
  }
]

export default studentRoutes

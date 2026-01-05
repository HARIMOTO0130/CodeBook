import { createRouter, createWebHistory } from 'vue-router'

// 导入所有视图组件
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

const routes = [
  {
    path: '/',
    redirect: '/books'
  },
  {
    path: '/books',
    name: 'Books',
    component: BooksView,
    meta: { title: '教材书架' }
  },
  {
    path: '/books/:bookId',
    name: 'BookOutline',
    component: BookOutlineView,
    meta: { title: '章节大纲' },
    props: true
  },
  {
    path: '/books/:bookId/chapter/:chapterId',
    name: 'Learning',
    component: LearnView,
    meta: { title: '学习页' },
    props: true
  },
  {
    path: '/fullcode',
    name: 'FullCode',
    component: FullCodeView,
    meta: { title: '代码全屏' }
  },
  {
    path: '/profile/records',
    name: 'Records',
    component: RecordsView,
    meta: { title: '学习记录', requiresAuth: true }
  },
  {
    path: '/profile/settings',
    name: 'Settings',
    component: SettingsView,
    meta: { title: '设置', requiresAuth: true }
  },
  {
    path: '/toolkit',
    name: 'ToolKit',
    component: ToolKitView,
    meta: { title: '轻量化工具包' }
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginView,
    meta: { title: '登录' }
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
    meta: { title: '注册' }
  },
  {
    path: '/learning-paths',
    name: 'LearningPath',
    component: LearningPathView,
    meta: { title: '学习路线图' }
  },
  {    path: '/practice',    name: 'Practice',    component: PracticeView,    meta: { title: '练习题' }  },
  {    path: '/jupyter',    name: 'JupyterDocumentsList',    component: JupyterDocumentsListView,    meta: { title: 'Jupyter文档列表', requiresAuth: true }  },
  {    path: '/jupyter/new',    name: 'JupyterNotebookNew',    component: JupyterNotebookView,    meta: { title: '新建Jupyter文档', requiresAuth: true },
    props: { documentId: null }  },
  {    path: '/jupyter/:documentId',    name: 'JupyterNotebook',    component: JupyterNotebookView,    meta: { title: '编辑Jupyter文档', requiresAuth: true },
    props: true  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 设置页面标题
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || 'CodeBook+——交互式非计算机专业计算机教育数字教材平台'
  const requiresAuth = to.matched.some(r => r.meta && r.meta.requiresAuth)
  const token = (() => { try { return localStorage.getItem('token') } catch { return null } })()
  if (requiresAuth && !token) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else {
    next()
  }
})

export default router
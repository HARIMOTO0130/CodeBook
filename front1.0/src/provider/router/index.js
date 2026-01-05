// 教材提供者端路由配置
const providerRoutes = [
  {
    path: '/provider',
    redirect: '/provider/dashboard'
  },
  {
    path: '/provider/dashboard',
    name: 'ProviderDashboard',
    component: () => import('../views/DashboardView.vue'),
    meta: { title: '教材提供者工作台', requiresAuth: true, role: 'provider' }
  },
  {
    path: '/provider/books',
    name: 'ProviderBooks',
    component: () => import('../views/BookListView.vue'),
    meta: { title: '书籍管理', requiresAuth: true, role: 'provider' }
  },
  {
    path: '/provider/books/create',
    name: 'ProviderBookCreate',
    component: () => import('../views/BookCreateView.vue'),
    meta: { title: '创建书籍', requiresAuth: true, role: 'provider' }
  },
  {
    path: '/provider/books/:id/edit',
    name: 'ProviderBookEdit',
    component: () => import('../views/BookEditView.vue'),
    meta: { title: '编辑书籍', requiresAuth: true, role: 'provider' },
    props: true
  },
  {
    path: '/provider/toolkit',
    name: 'ProviderToolkit',
    component: () => import('../views/ToolkitView.vue'),
    meta: { title: '工具箱管理', requiresAuth: true, role: 'provider' }
  },
  {
    path: '/provider/versions',
    name: 'ProviderVersions',
    component: () => import('../views/VersionListView.vue'),
    meta: { title: '版本管理', requiresAuth: true, role: 'provider' }
  },
  {
    path: '/provider/categories',
    name: 'ProviderCategories',
    component: () => import('../views/CategoryView.vue'),
    meta: { title: '分类与标签', requiresAuth: true, role: 'provider' }
  },
  {
    path: '/provider/settings',
    name: 'ProviderSettings',
    component: () => import('../views/SettingsView.vue'),
    meta: { title: '设置', requiresAuth: true, role: 'provider' }
  }
]

export default providerRoutes


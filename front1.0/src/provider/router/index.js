// 教材提供者端路由配置
const providerRoutes = [
  {
    path: '/provider',
    redirect: '/provider/books'
  },
  {
    path: '/provider/books',
    name: 'ProviderBooks',
    component: () => import('../views/ProviderBooksView.vue'),
    meta: { title: '书籍管理', requiresAuth: true, role: 'provider', providerNav: 'books' }
  },
  {
    path: '/provider/categories',
    name: 'ProviderCategories',
    component: () => import('../views/ProviderCategoriesView.vue'),
    meta: { title: '分类与标签', requiresAuth: true, role: 'provider', providerNav: 'categories' }
  },
  {
    path: '/provider/versions',
    name: 'ProviderVersions',
    component: () => import('../views/ProviderVersionsView.vue'),
    meta: { title: '版本管理', requiresAuth: true, role: 'provider', providerNav: 'versions' }
  }
]

export default providerRoutes


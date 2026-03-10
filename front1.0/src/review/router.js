import LayoutView from '../views/LayoutView.vue'

const reviewRoutes = [
  {
    path: '/review',
    component: LayoutView,
    meta: {
      title: '教材审核系统',
      requiresAuth: true,
      role: 'reviewer'
    },
    children: [
      {
        path: '',
        redirect: '/review/dashboard'
      },
      {
        path: 'dashboard',
        name: 'ReviewDashboard',
        component: () => import('./views/DashboardView.vue'),
        meta: { title: '审核工作台' }
      },
      {
        path: 'books',
        name: 'ReviewBooks',
        component: () => import('./views/BooksView.vue'),
        meta: { title: '教材列表' }
      },
      {
        path: 'books/:id/history',
        name: 'BookHistory',
        component: () => import('./views/BookHistoryView.vue'),
        meta: { title: '教材修改历史' }
      },
      {
        path: 'pending',
        name: 'PendingList',
        component: () => import('./views/PendingListView.vue'),
        meta: { title: '待审核任务' }
      },
      {
        path: 'review/:id',
        name: 'ReviewDetail',
        component: () => import('./views/ReviewDetailView.vue'),
        meta: { title: '审核详情' }
      },
      {
        path: 'approved',
        name: 'ApprovedList',
        component: () => import('./views/ApprovedListView.vue'),
        meta: { title: '已通过审核' }
      },
      {
        path: 'rejected',
        name: 'RejectedList',
        component: () => import('./views/RejectedListView.vue'),
        meta: { title: '已驳回审核' }
      },
      {
        path: 'history',
        name: 'ReviewHistory',
        component: () => import('./views/HistoryView.vue'),
        meta: { title: '审核历史' }
      },
      {
        path: 'settings',
        name: 'ReviewSettings',
        component: () => import('./views/SettingsView.vue'),
        meta: { title: '系统设置' }
      }
    ]
  }
]

export default reviewRoutes

import { createRouter, createWebHistory } from 'vue-router'
import studentRoutes from '../student/router'
import teacherRoutes from '../teacher/router'
import providerRoutes from '../provider/router'

// 主路由配置 - 整合所有端的路由
const routes = [
  // 根路径重定向到学生端（默认入口）
  {
    path: '/',
    redirect: '/student/books'
  },
  // 学生端路由
  ...studentRoutes,
  // 教师端路由
  ...teacherRoutes,
  // 教材提供者端路由
  ...providerRoutes,
  // 404页面
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundView.vue'),
    meta: { title: '页面未找到' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || 'CodeBook+——交互式非计算机专业计算机教育数字教材平台'
  
  // 检查是否需要认证
  const requiresAuth = to.matched.some(r => r.meta && r.meta.requiresAuth)
  const token = (() => {
    try {
      return localStorage.getItem('token')
    } catch {
      return null
    }
  })()
  
  // 检查角色权限
  const requiredRole = to.meta.role
  const userRole = (() => {
    try {
      return localStorage.getItem('userRole')
    } catch {
      return null
    }
  })()
  
  // 如果需要认证但没有token，重定向到登录页
  if (requiresAuth && !token) {
    const loginPath = requiredRole === 'teacher' ? '/teacher/login' 
                    : requiredRole === 'provider' ? '/provider/login'
                    : '/student/login'
    next({ path: loginPath, query: { redirect: to.fullPath } })
    return
  }
  
  // 如果指定了角色但用户角色不匹配
  if (requiredRole && userRole !== requiredRole) {
    // 根据用户角色重定向到对应端
    if (userRole === 'teacher') {
      next('/teacher/dashboard')
    } else if (userRole === 'provider') {
      next('/provider/dashboard')
    } else {
      next('/student/books')
    }
    return
  }
  
  next()
})

export default router

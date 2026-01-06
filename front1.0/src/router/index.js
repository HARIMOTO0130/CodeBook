import { createRouter, createWebHistory } from 'vue-router'
import studentRoutes from '../student/router'
import teacherRoutes from '../teacher/router'
import providerRoutes from '../provider/router'

// 主路由配置 - 整合所有端的路由
// 确保所有路由都是数组
const allRoutes = [
  // 根路径 - 登录/注册页面（带角色选择）
  {
    path: '/',
    name: 'Auth',
    component: () => import('../views/AuthView.vue'),
    meta: { title: '登录/注册' }
  }
]

// 添加学生端路由
if (Array.isArray(studentRoutes)) {
  allRoutes.push(...studentRoutes)
} else {
  console.error('studentRoutes is not an array:', studentRoutes)
}

// 添加教师端路由
if (Array.isArray(teacherRoutes)) {
  allRoutes.push(...teacherRoutes)
} else {
  console.error('teacherRoutes is not an array:', teacherRoutes)
}

// 添加教材提供者端路由
if (Array.isArray(providerRoutes)) {
  allRoutes.push(...providerRoutes)
} else {
  console.error('providerRoutes is not an array:', providerRoutes)
}

// 添加404页面（必须放在最后）
allRoutes.push({
  path: '/:pathMatch(.*)*',
  name: 'NotFound',
  component: () => import('../views/NotFoundView.vue'),
  meta: { title: '页面未找到' }
})

// 调试信息
if (import.meta.env.DEV) {
  console.log('Total routes registered:', allRoutes.length)
  console.log('Route paths:', allRoutes.map(r => r.path))
}

const routes = allRoutes

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 全局路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || 'CodeBook+——交互式非计算机专业计算机教育数字教材平台'
  
  // 登录/注册页面和404页面不需要任何检查，直接通过
  if (to.path === '/' || to.name === 'Auth' || to.name === 'NotFound') {
    next()
    return
  }
  
  // 检查是否需要认证（确保 to.matched 存在）
  const requiresAuth = to.matched && to.matched.length > 0 && to.matched.some(r => r.meta && r.meta.requiresAuth)
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
  
  // 调试信息（开发环境）
  if (import.meta.env.DEV) {
    console.log('Route guard:', {
      path: to.path,
      requiresAuth,
      requiredRole,
      userRole,
      hasToken: !!token
    })
  }
  
  // 如果需要认证但没有token，重定向到登录页（根路径）
  if (requiresAuth && !token) {
    // 避免重定向到当前路径
    if (to.path !== '/') {
      if (import.meta.env.DEV) {
        console.log('Redirecting to login: /')
      }
      next({ path: '/', query: { redirect: to.fullPath } })
      return
    }
  }
  
  // 如果用户已登录且有角色，检查角色是否匹配
  if (userRole && requiredRole && userRole !== requiredRole) {
    // 根据用户角色重定向到对应端，避免循环重定向
    if (userRole === 'teacher' && !to.path.startsWith('/teacher/')) {
      if (import.meta.env.DEV) {
        console.log('Role mismatch, redirecting teacher to dashboard')
      }
      next('/teacher/dashboard')
      return
    } else if (userRole === 'provider' && !to.path.startsWith('/provider/')) {
      if (import.meta.env.DEV) {
        console.log('Role mismatch, redirecting provider to dashboard')
      }
      next('/provider/dashboard')
      return
    } else if (userRole === 'student' && !to.path.startsWith('/student/') && !to.path.startsWith('/teacher/') && !to.path.startsWith('/provider/')) {
      if (import.meta.env.DEV) {
        console.log('Role mismatch, redirecting student to books')
      }
      next('/student/books')
      return
    }
  }
  
  // 如果路由需要特定角色但用户未登录，且不是学生端（学生端允许未登录访问）
  if (requiredRole && !userRole && requiredRole !== 'student') {
    // 避免重定向到当前路径
    if (to.path !== '/') {
      if (import.meta.env.DEV) {
        console.log('No role but required, redirecting to login: /')
      }
      next({ path: '/', query: { redirect: to.fullPath } })
      return
    }
  }
  
  // 确保总是调用 next()
  if (import.meta.env.DEV) {
    console.log('Route guard passed, allowing navigation to:', to.path)
  }
  next()
})

export default router

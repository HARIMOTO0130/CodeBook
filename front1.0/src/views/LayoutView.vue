<template>
  <div class="layout-container">
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2>教材审核系统</h2>
      </div>
      <nav class="sidebar-nav">
        <router-link to="/review/dashboard" class="nav-item">
          <i class="fas fa-chart-bar"></i>
          <span>仪表盘</span>
        </router-link>
        <router-link to="/review/pending" class="nav-item">
          <i class="fas fa-hourglass-half"></i>
          <span>待审核</span>
        </router-link>
        <router-link to="/review/approved" class="nav-item">
          <i class="fas fa-check-circle"></i>
          <span>已通过</span>
        </router-link>
        <router-link to="/review/rejected" class="nav-item">
          <i class="fas fa-times-circle"></i>
          <span>已驳回</span>
        </router-link>
        <router-link to="/review/history" class="nav-item">
          <i class="fas fa-history"></i>
          <span>历史记录</span>
        </router-link>
        <router-link to="/review/settings" class="nav-item">
          <i class="fas fa-cog"></i>
          <span>系统设置</span>
        </router-link>
      </nav>
    </aside>
    <main class="main-content">
      <header class="main-header">
        <div class="header-left">
          <h1>{{ $route.meta.title || '审核系统' }}</h1>
        </div>
        <div class="header-right">
          <div class="user-info">
            <span class="user-name">{{ user?.name || user?.username }}</span>
            <button class="logout-btn" @click="handleLogout">
              <i class="fas fa-sign-out-alt"></i>
              退出
            </button>
          </div>
        </div>
      </header>
      <div class="main-body">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../review/api/review.js'

const router = useRouter()
const user = ref(null)

const loadUserInfo = async () => {
  try {
    const res = await authApi.getProfile()
    user.value = res
  } catch (err) {
    console.error('加载用户信息失败:', err)
  }
}

const handleLogout = async () => {
  try {
    await authApi.logout()
  } catch (err) {
    console.error('退出登录失败:', err)
  } finally {
    localStorage.removeItem('review_token')
    localStorage.removeItem('token')
    localStorage.removeItem('userRole')
    router.push('/')
  }
}

onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.layout-container {
  display: flex;
  min-height: 100vh;
  background: var(--background-light);
}

.sidebar {
  width: 250px;
  background: var(--white);
  border-right: 1px solid var(--border-color);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-color);
}

.sidebar-header h2 {
  font-size: 18px;
  color: var(--primary-color);
  margin: 0;
}

.sidebar-nav {
  padding: 20px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: var(--text-color);
  text-decoration: none;
  transition: all 0.2s;
}

.nav-item:hover {
  background: var(--background-light);
  color: var(--primary-color);
}

.nav-item i {
  margin-right: 12px;
  font-size: 16px;
}

.nav-item.router-link-active {
  background: var(--primary-light);
  color: var(--primary-color);
  font-weight: 600;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.main-header {
  background: var(--white);
  padding: 0 30px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.header-left h1 {
  font-size: 20px;
  color: var(--text-color);
  margin: 0;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-name {
  font-size: 14px;
  color: var(--text-color);
}

.logout-btn {
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 14px;
  color: var(--text-color);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.logout-btn:hover {
  background: var(--danger-light);
  color: var(--danger-color);
  border-color: var(--danger-color);
}

.main-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .sidebar {
    width: 200px;
  }
  
  .sidebar-header h2 {
    font-size: 16px;
  }
  
  .nav-item span {
    font-size: 14px;
  }
  
  .main-header {
    padding: 0 20px;
  }
  
  .main-body {
    padding: 15px;
  }
}
</style>

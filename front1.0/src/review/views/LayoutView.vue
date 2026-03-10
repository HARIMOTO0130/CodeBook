<template>
  <div class="layout">
    <aside class="sidebar">
      <div class="logo">
        <h2>教材审核系统</h2>
      </div>
      <nav class="nav-menu">
        <router-link to="/review/dashboard" class="nav-item" :class="{ active: $route.path === '/review/dashboard' }">
          <span class="icon">📊</span>
          <span>工作台</span>
        </router-link>
        <router-link to="/review/books" class="nav-item" :class="{ active: $route.path.startsWith('/review/books') }">
          <span class="icon">📚</span>
          <span>教材列表</span>
        </router-link>
        <router-link to="/review/pending" class="nav-item" :class="{ active: $route.path.startsWith('/review/pending') || $route.path.startsWith('/review/review') }">
          <span class="icon">📋</span>
          <span>待审核</span>
          <span v-if="stats.my_pending > 0" class="badge">{{ stats.my_pending }}</span>
        </router-link>
        <router-link to="/review/approved" class="nav-item" :class="{ active: $route.path.startsWith('/review/approved') }">
          <span class="icon">✅</span>
          <span>已通过</span>
        </router-link>
        <router-link to="/review/rejected" class="nav-item" :class="{ active: $route.path.startsWith('/review/rejected') }">
          <span class="icon">❌</span>
          <span>已驳回</span>
        </router-link>
        <router-link to="/review/history" class="nav-item" :class="{ active: $route.path.startsWith('/review/history') }">
          <span class="icon">📜</span>
          <span>审核历史</span>
        </router-link>
        <router-link to="/review/settings" class="nav-item" :class="{ active: $route.path.startsWith('/review/settings') }">
          <span class="icon">⚙️</span>
          <span>设置</span>
        </router-link>
      </nav>
    </aside>
    <main class="main-content">
      <header class="header">
        <div class="header-left">
          <h1 class="page-title">{{ pageTitle }}</h1>
        </div>
        <div class="header-right">
          <span class="user-info">{{ user?.nickname || user?.username }}</span>
          <button class="btn-default" @click="handleLogout">退出</button>
        </div>
      </header>
      <div class="content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { authApi, taskApi } from '../api/review'

const router = useRouter()
const route = useRoute()

const user = ref(JSON.parse(localStorage.getItem('review_user') || '{}'))
const stats = ref({
  my_pending: 0
})

const pageTitle = computed(() => {
  const titles = {
    '/dashboard': '工作台',
    '/books': '教材列表',
    '/pending': '待审核',
    '/approved': '已通过',
    '/rejected': '已驳回',
    '/history': '审核历史',
    '/settings': '设置'
  }
  if (route.path.startsWith('/review/')) {
    return '审核详情'
  }
  if (route.path.startsWith('/books/')) {
    return '教材修改历史'
  }
  return titles[route.path] || '教材审核系统'
})

const loadStats = async () => {
  try {
    const data = await taskApi.getStats()
    stats.value = data
  } catch (err) {
    console.error('加载统计失败', err)
  }
}

const handleLogout = async () => {
  try {
    await authApi.logout()
  } catch (err) {
    console.error('退出失败', err)
  }
  localStorage.removeItem('review_token')
  localStorage.removeItem('review_user')
  router.push('/review/login')
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 240px;
  background: #001529;
  color: #fff;
  display: flex;
  flex-direction: column;
}

.logo {
  padding: 20px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo h2 {
  font-size: 18px;
  font-weight: 600;
}

.nav-menu {
  flex: 1;
  padding: 10px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 20px;
  color: rgba(255, 255, 255, 0.65);
  transition: all 0.3s;
}

.nav-item:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.nav-item.active {
  color: #fff;
  background: var(--primary-color);
}

.nav-item .icon {
  margin-right: 10px;
}

.nav-item .badge {
  margin-left: auto;
  background: var(--error-color);
  color: #fff;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-color);
}

.header {
  background: var(--white);
  padding: 16px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info {
  color: var(--text-secondary);
}

.content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
</style>

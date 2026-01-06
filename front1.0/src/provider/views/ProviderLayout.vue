<template>
  <div class="provider-layout">
    <aside class="sidebar">
      <div
        v-for="item in navItems"
        :key="item.key"
        class="nav-item"
        :class="{ active: activeKey === item.key }"
        @click="onNavClick(item)"
      >
        <span class="nav-icon">{{ item.icon }}</span>
        <span class="nav-label">{{ item.label }}</span>
      </div>
    </aside>

    <main class="main">
      <header class="header">
        <h1>{{ currentNav.label }}</h1>
        <p class="header-desc">{{ currentNav.desc }}</p>
      </header>

      <section class="content">
        <slot />
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const navItems = [
  { key: 'books', label: '书籍管理', icon: '📚', path: '/provider/books', desc: '创建、管理和维护数字教材' },
  { key: 'categories', label: '分类与标签', icon: '🏷️', path: '/provider/categories', desc: '管理教材分类体系与标签体系' },
  { key: 'versions', label: '版本管理', icon: '📑', path: '/provider/versions', desc: '查看和管理教材版本历史' },
]

const activeKey = computed(() => {
  const m = route.meta && route.meta.providerNav
  return m || 'books'
})

const currentNav = computed(() => {
  return navItems.find(i => i.key === activeKey.value) || navItems[0]
})

const onNavClick = (item) => {
  if (route.path !== item.path) {
    router.push(item.path)
  }
}
</script>

<style scoped>
.provider-layout {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 24px;
  padding: 20px 0;
}

.sidebar {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 8px 0;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background: #f5f7fa;
}

.nav-item.active {
  background: #ecf5ff;
  border-left-color: #409eff;
  color: #409eff;
}

.nav-icon {
  font-size: 20px;
}

.nav-label {
  font-size: 15px;
}

.main {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.header h1 {
  margin: 0;
  font-size: 22px;
}

.header-desc {
  margin-top: 4px;
  font-size: 13px;
  color: #666;
}

.content {
  margin-top: 8px;
}

@media (max-width: 960px) {
  .provider-layout {
    grid-template-columns: 1fr;
  }
}
</style>



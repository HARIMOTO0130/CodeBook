<template>
  <div class="provider-layout">
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
  display: flex;
  padding: 20px 0;
}

.main {
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 24px 28px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  width: 100%;
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



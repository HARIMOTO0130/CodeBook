<template>
  <ProviderLayout>
    <div class="provider-versions">
      <div class="toolbar">
        <select v-model="selectedBookId" class="select" @change="onBookChange">
          <option disabled value="">请选择教材查看版本...</option>
          <option v-for="b in books" :key="b.id" :value="b.id">
            {{ b.title }}
          </option>
        </select>
        <button class="btn" @click="loadBooks">刷新列表</button>
      </div>

      <div v-if="loadingBooks" class="empty-tip">正在加载教材列表...</div>

      <div v-else-if="!selectedBookId" class="empty-tip">
        请选择左侧下拉框中的教材，查看版本历史。
      </div>

      <div v-else class="version-panel">
        <h3 class="section-title">版本历史</h3>

        <div v-if="loadingVersions" class="empty-tip small">正在加载版本...</div>
        <div v-else-if="versions.length === 0" class="empty-tip small">该教材暂无版本记录。</div>

        <ul class="version-list">
          <li v-for="ver in versions" :key="ver.id" class="version-item">
            <div class="version-main">
              <span class="version-tag">v{{ ver.version_number }}</span>
              <span class="version-title">{{ ver.title }}</span>
            </div>
            <div class="version-meta">
              <span>{{ formatTime(ver.created_at) }}</span>
              <span v-if="ver.created_by">创建人：{{ ver.created_by }}</span>
            </div>
            <p class="version-comment" v-if="ver.comment">{{ ver.comment }}</p>
          </li>
        </ul>
      </div>
    </div>
  </ProviderLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ProviderLayout from './ProviderLayout.vue'
import { providerApi } from '../api/index.js'

const books = ref([])
const versions = ref([])
const selectedBookId = ref('')

const loadingBooks = ref(false)
const loadingVersions = ref(false)

const loadBooks = async () => {
  loadingBooks.value = true
  try {
    books.value = await providerApi.listBooks()
  } catch (e) {
    console.error('加载教材列表失败', e)
  } finally {
    loadingBooks.value = false
  }
}

const loadVersions = async () => {
  if (!selectedBookId.value) return
  loadingVersions.value = true
  try {
    versions.value = await providerApi.listVersions(selectedBookId.value)
  } catch (e) {
    console.error('加载版本失败', e)
    versions.value = []
  } finally {
    loadingVersions.value = false
  }
}

const onBookChange = () => {
  loadVersions()
}

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const d = new Date(timeStr)
  return d.toLocaleString()
}

onMounted(() => {
  loadBooks()
})
</script>

<style scoped>
.provider-versions {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
}

.select {
  min-width: 260px;
  padding: 8px 10px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  font-size: 13px;
}

.btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  background: #fff;
  font-size: 13px;
  cursor: pointer;
}

.section-title {
  margin-bottom: 8px;
  font-size: 18px;
}

.version-panel {
  margin-top: 4px;
}

.empty-tip {
  font-size: 13px;
  color: #999;
}

.empty-tip.small {
  font-size: 12px;
}

.version-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.version-item {
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.version-main {
  display: flex;
  align-items: center;
  gap: 8px;
}

.version-tag {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 4px;
  background: #ecf5ff;
  color: #409eff;
}

.version-title {
  font-size: 14px;
}

.version-meta {
  font-size: 11px;
  color: #999;
  display: flex;
  gap: 8px;
  margin-top: 2px;
}

.version-comment {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
}
</style>



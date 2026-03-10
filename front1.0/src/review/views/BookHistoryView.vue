<template>
  <ReviewLayout>
    <div class="book-history">
      <div class="header">
        <button class="btn-back" @click="goBack">← 返回教材列表</button>
        <h2 class="title">教材修改历史</h2>
      </div>

      <div v-if="loading" class="empty-tip">正在加载...</div>
      <div v-else-if="!book" class="empty-tip">未找到教材信息</div>
      <div v-else>
        <div class="book-summary">
          <h3>{{ book.title }}</h3>
          <p class="book-author">作者：{{ book.author || '未知' }}</p>
          <p class="book-desc">{{ book.description || '暂无简介' }}</p>
          <div class="book-meta">
            <span>版本：v{{ book.version_number || '1.0.0' }}</span>
            <span>章节数：{{ book.chapter_count || 0 }}</span>
            <span>字数：{{ book.word_count || 0 }}</span>
          </div>
        </div>

        <div class="history-section">
          <div class="history-header">
            <h3>修改历史</h3>
            <div class="history-stats">
              <span class="stat-item">共 {{ history.length }} 条记录</span>
            </div>
          </div>

          <div v-if="history.length === 0" class="empty-tip">暂无修改记录</div>

          <div v-else class="timeline">
            <div v-for="(item, index) in history" :key="item.id" class="timeline-item">
              <div class="timeline-marker" :class="{ first: index === 0 }"></div>
              <div class="timeline-content">
                <div class="timeline-header">
                  <span class="timeline-action">{{ item.action_display }}</span>
                  <span class="timeline-time">{{ formatDateTime(item.created_at) }}</span>
                </div>
                
                <div class="timeline-actor">
                  <span class="actor-name">{{ item.actor_name }}</span>
                  <span v-if="item.actor_employee_id" class="actor-id">({{ item.actor_employee_id }})</span>
                  <span v-if="item.actor_department" class="actor-dept">{{ item.actor_department }}</span>
                  <span class="actor-role">{{ item.actor_role_display || '未知角色' }}</span>
                </div>

                <div v-if="item.version_number" class="timeline-version">
                  <span class="version-label">版本：</span>
                  <span class="version-current">v{{ item.version_number }}</span>
                  <span v-if="item.previous_version" class="version-previous">
                    (上一版本: v{{ item.previous_version }})
                  </span>
                </div>

                <div v-if="item.changes_summary" class="timeline-summary">
                  <div class="summary-label">变更说明：</div>
                  <div class="summary-text">{{ item.changes_summary }}</div>
                </div>

                <div v-if="item.changes_detail" class="timeline-detail">
                  <div class="detail-label">详细变更：</div>
                  <div class="detail-content">
                    <pre>{{ formatJSON(item.changes_detail) }}</pre>
                  </div>
                </div>

                <div class="timeline-meta">
                  <span v-if="item.ip_address" class="meta-item">
                    IP：{{ item.ip_address }}
                  </span>
                  <span v-if="item.user_agent" class="meta-item">
                    {{ item.user_agent }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </ReviewLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { booksApi } from '../api/review'

const router = useRouter()
const route = useRoute()

const book = ref(null)
const history = ref([])
const loading = ref(false)

const loadBook = async () => {
  try {
    const data = await booksApi.getDetail(route.params.id)
    book.value = data
  } catch (err) {
    console.error('加载教材信息失败', err)
  }
}

const loadHistory = async () => {
  loading.value = true
  try {
    const data = await booksApi.getHistory(route.params.id, { page_size: 100 })
    history.value = data.results || data
  } catch (err) {
    console.error('加载修改历史失败', err)
  } finally {
    loading.value = false
  }
}

const goBack = () => {
  router.push('/review/books')
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const formatJSON = (obj) => {
  if (!obj) return ''
  try {
    return JSON.stringify(obj, null, 2)
  } catch {
    return obj
  }
}

onMounted(() => {
  loadBook()
  loadHistory()
})
</script>

<style scoped>
.book-history {
  padding: 24px;
}

.header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.btn-back {
  padding: 8px 16px;
  background: var(--white);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-back:hover {
  background: #f5f5f5;
}

.title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.empty-tip {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.book-summary {
  background: var(--white);
  border-radius: 8px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: var(--shadow);
}

.book-summary h3 {
  margin: 0 0 12px 0;
  font-size: 20px;
  font-weight: 600;
}

.book-author {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.book-desc {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.6;
}

.book-meta {
  display: flex;
  gap: 24px;
  font-size: 13px;
  color: var(--text-secondary);
}

.history-section {
  background: var(--white);
  border-radius: 8px;
  padding: 24px;
  box-shadow: var(--shadow);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
}

.history-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.history-stats {
  display: flex;
  gap: 16px;
}

.stat-item {
  font-size: 14px;
  color: var(--text-secondary);
}

.timeline {
  position: relative;
  padding-left: 24px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--border-color);
}

.timeline-item {
  position: relative;
  padding-bottom: 32px;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-marker {
  position: absolute;
  left: -20px;
  top: 4px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--border-color);
  border: 2px solid var(--white);
}

.timeline-marker.first {
  background: var(--primary-color);
  width: 18px;
  height: 18px;
  left: -22px;
}

.timeline-content {
  padding-left: 12px;
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.timeline-action {
  padding: 4px 12px;
  background: var(--primary-color);
  color: white;
  border-radius: 4px;
  font-size: 13px;
  font-weight: 500;
}

.timeline-time {
  font-size: 13px;
  color: var(--text-secondary);
}

.timeline-actor {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 14px;
}

.actor-name {
  font-weight: 500;
}

.actor-id {
  color: var(--text-secondary);
  font-size: 13px;
}

.actor-dept {
  color: var(--text-secondary);
  font-size: 13px;
}

.actor-role {
  padding: 2px 8px;
  background: #f0f5ff;
  color: #1890ff;
  border-radius: 4px;
  font-size: 12px;
}

.timeline-version {
  margin-bottom: 12px;
  font-size: 13px;
}

.version-label {
  color: var(--text-secondary);
  margin-right: 8px;
}

.version-current {
  font-weight: 600;
  color: var(--primary-color);
}

.version-previous {
  color: var(--text-secondary);
  font-size: 12px;
}

.timeline-summary {
  margin-bottom: 12px;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 4px;
}

.summary-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.summary-text {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.6;
}

.timeline-detail {
  margin-bottom: 12px;
}

.detail-label {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.detail-content {
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
  overflow-x: auto;
}

.detail-content pre {
  margin: 0;
  font-size: 12px;
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.timeline-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 12px;
  color: var(--text-secondary);
}
</style>

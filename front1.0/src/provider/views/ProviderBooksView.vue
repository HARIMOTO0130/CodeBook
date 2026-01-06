<template>
  <ProviderLayout>
    <div class="provider-books">
      <!-- 顶部操作区：搜索 + 新建按钮 -->
      <div class="toolbar">
        <div class="search-group">
          <input
            v-model="keyword"
            type="text"
            class="search-input"
            placeholder="搜索书名、作者或标签..."
            @keyup.enter="loadBooks"
          />
          <button class="search-button" @click="loadBooks">🔍 搜索</button>
        </div>

        <div class="toolbar-actions">
          <button class="btn" @click="loadBooks">刷新</button>
          <button class="btn btn-primary" @click="openCreateDialog">＋ 新建教材</button>
        </div>
      </div>

      <div class="layout">
        <!-- 左侧：书籍列表 -->
        <div class="books-list">
          <h3 class="section-title">教材列表</h3>

          <div v-if="loading" class="empty-tip">正在加载教材...</div>
          <div v-else-if="books.length === 0" class="empty-tip">暂无教材，请先创建。</div>

          <div
            v-for="book in books"
            :key="book.id"
            class="book-card"
            @click="selectBook(book)"
            :class="{ active: currentBook && currentBook.id === book.id }"
          >
            <div class="book-cover" :style="{ backgroundColor: getCoverColor(book.id) }">
              {{ book.title.charAt(0) }}
            </div>
            <div class="book-info">
              <div class="book-title-row">
                <h4 class="book-title">{{ book.title }}</h4>
                <span v-if="book.is_archived" class="status-tag archived">已归档</span>
              </div>
              <p class="book-author">作者：{{ book.author || '未知' }}</p>
              <p class="book-desc">{{ book.description || '暂无简介' }}</p>
              <div class="book-meta">
                <span class="meta-item">章节：{{ book.chapter_count }}</span>
                <span class="meta-item">标签：{{ (book.tag_objects || book.tag_list || []).length }}</span>
              </div>
              <div class="tag-row" v-if="(book.tag_objects && book.tag_objects.length) || (book.tag_list && book.tag_list.length)">
                <span
                  v-for="tag in (book.tag_objects && book.tag_objects.length ? book.tag_objects : book.tag_list)"
                  :key="tag"
                  class="tag"
                >
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：选中书籍详情 + 版本列表 -->
        <div class="sidebar" v-if="currentBook">
          <h3 class="section-title">版本与状态</h3>

          <div class="book-summary">
            <h4>{{ currentBook.title }}</h4>
            <p class="book-author">作者：{{ currentBook.author || '未知' }}</p>
            <p class="book-desc">{{ currentBook.description || '暂无简介' }}</p>
          </div>

          <div class="versions-header">
            <span>版本历史</span>
            <button class="btn btn-secondary" disabled>新建版本（预留）</button>
          </div>

          <div v-if="versionsLoading" class="empty-tip small">正在加载版本...</div>
          <div v-else-if="versions.length === 0" class="empty-tip small">暂无版本记录。</div>

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

      <!-- 预留：新建教材弹窗骨架 -->
      <div v-if="showCreate" class="modal-overlay" @click.self="showCreate = false">
        <div class="modal">
          <div class="modal-header">
            <h3>新建教材（预留表单）</h3>
            <button class="close-btn" @click="showCreate = false">×</button>
          </div>
          <div class="modal-body">
            <p>这里后续可以接入 PDF 上传、基本信息表单等。</p>
          </div>
          <div class="modal-footer">
            <button class="btn" @click="showCreate = false">取消</button>
            <button class="btn btn-primary" disabled>保存（未实现）</button>
          </div>
        </div>
      </div>
    </div>
  </ProviderLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ProviderLayout from './ProviderLayout.vue'
import { providerApi } from '../api/index.js'

const books = ref([])
const loading = ref(false)
const keyword = ref('')

const currentBook = ref(null)
const versions = ref([])
const versionsLoading = ref(false)

const showCreate = ref(false)

const loadBooks = async () => {
  loading.value = true
  try {
    const data = await providerApi.listBooks(
      keyword.value ? { search: keyword.value } : {}
    )
    books.value = data
    if (!currentBook.value && books.value.length > 0) {
      selectBook(books.value[0])
    }
  } catch (e) {
    console.error('加载教材失败', e)
  } finally {
    loading.value = false
  }
}

const selectBook = async (book) => {
  currentBook.value = book
  await loadVersions(book.id)
}

const loadVersions = async (bookId) => {
  versionsLoading.value = true
  try {
    const data = await providerApi.listVersions(bookId)
    versions.value = data
  } catch (e) {
    console.error('加载版本失败', e)
    versions.value = []
  } finally {
    versionsLoading.value = false
  }
}

const openCreateDialog = () => {
  showCreate.value = true
}

const getCoverColor = (bookId) => {
  const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9CA24', '#6C5CE7', '#A29BFE']
  return colors[bookId % colors.length]
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
.provider-books {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  margin-bottom: 8px;
}

.search-group {
  display: flex;
  flex: 1;
}

.search-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #dcdfe6;
  border-radius: 4px 0 0 4px;
  font-size: 14px;
}

.search-button {
  padding: 10px 16px;
  border: none;
  background: #409eff;
  color: #fff;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

.layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
}

.books-list,
.sidebar {
  min-height: 200px;
}

.section-title {
  margin-bottom: 12px;
  font-size: 18px;
}

.book-card {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  border: 1px solid #f0f0f0;
  margin-bottom: 10px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.book-card:hover {
  background: #f9fafc;
}

.book-card.active {
  border-color: #409eff;
  background: #ecf5ff;
}

.book-cover {
  width: 56px;
  height: 80px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: #fff;
  font-weight: bold;
}

.book-info {
  flex: 1;
}

.book-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.book-title {
  margin: 0;
  font-size: 16px;
}

.book-author {
  margin: 2px 0 4px 0;
  font-size: 13px;
  color: #666;
}

.book-desc {
  margin: 0 0 4px 0;
  font-size: 13px;
  color: #777;
}

.book-meta {
  font-size: 12px;
  color: #999;
  margin-bottom: 4px;
}

.meta-item {
  margin-right: 12px;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  background: #f0f0f0;
}

.status-tag.archived {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  background: #fef0f0;
  color: #f56c6c;
}

.empty-tip {
  font-size: 13px;
  color: #999;
  margin: 8px 0;
}

.empty-tip.small {
  font-size: 12px;
}

.book-summary {
  padding: 10px 12px;
  border-radius: 6px;
  background: #f7f9fc;
  margin-bottom: 12px;
}

.versions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
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
  margin-bottom: 2px;
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
}

.version-comment {
  margin: 2px 0 0 0;
  font-size: 12px;
  color: #666;
}

.btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  background: #fff;
  font-size: 13px;
  cursor: pointer;
}

.btn-primary {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
}

.btn-secondary {
  background: #f5f7fa;
}

/* 简单弹窗骨架 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #fff;
  border-radius: 8px;
  width: 480px;
  max-width: 90%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-header,
.modal-footer {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-footer {
  border-top: 1px solid #f0f0f0;
  border-bottom: none;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.modal-body {
  padding: 16px;
  font-size: 14px;
}

.close-btn {
  border: none;
  background: none;
  font-size: 20px;
  cursor: pointer;
}

@media (max-width: 960px) {
  .layout {
    grid-template-columns: 1fr;
  }
}
</style>



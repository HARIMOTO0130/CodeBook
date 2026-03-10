<template>
  <ReviewLayout>
    <div class="review-books">
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
          <button v-if="keyword && hasSearched" class="search-button back-button" @click="resetSearch">🔙 返回</button>
        </div>

        <div class="toolbar-actions">
          <button class="btn" @click="loadBooks">刷新</button>
          <select v-model="statusFilter" class="select" @change="loadBooks">
            <option value="">全部状态</option>
            <option value="draft">草稿</option>
            <option value="pending_review">待审核</option>
            <option value="reviewing">审核中</option>
            <option value="approved">已通过</option>
            <option value="rejected">已驳回</option>
            <option value="published">已发布</option>
          </select>
          <select v-model="categoryFilter" class="select" @change="loadBooks">
            <option value="">全部分类</option>
            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>
      </div>

      <div class="layout">
        <div class="books-list">
          <h3 class="section-title">教材列表</h3>

          <div v-if="loading" class="empty-tip">正在加载教材...</div>
          <div v-else-if="books.length === 0" class="empty-tip">暂无教材</div>

          <div
            v-for="book in books"
            :key="book.id"
            class="book-card"
            @click="selectBook(book)"
            :class="{ active: currentBook && currentBook.id === book.id }"
          >
            <div class="book-cover" :style="{ backgroundColor: getCoverColor(book.id) }">
              <span v-if="!book.cover">{{ (book.title || '书').charAt(0) }}</span>
              <img v-else :src="book.cover" :alt="book.title" />
            </div>
            <div class="book-info">
              <div class="book-title-row">
                <h4 class="book-title">{{ book.title || '未命名书籍' }}</h4>
                <span :class="['status-tag', `status-${book.status}`]">
                  {{ getStatusText(book.status) }}
                </span>
              </div>
              <p class="book-author">作者：{{ book.author || '未知' }}</p>
              <p class="book-desc">{{ book.description || '暂无简介' }}</p>
              <div class="book-meta">
                <span class="meta-item">章节：{{ book.chapter_count || 0 }}</span>
                <span class="meta-item">版本：v{{ book.version_number || '1.0.0' }}</span>
                <span class="meta-item">字数：{{ book.word_count || 0 }}</span>
              </div>
              <div class="book-time">
                <span>创建：{{ formatTime(book.created_at) }}</span>
                <span>更新：{{ formatTime(book.updated_at) }}</span>
              </div>
              <div class="tag-row" v-if="book.tag_list && book.tag_list.length">
                <span v-for="tag in book.tag_list" :key="tag" class="tag">{{ tag }}</span>
              </div>
            </div>
          </div>

          <div v-if="totalPages > 1" class="pagination">
            <div class="pagination-info">
              共 {{ totalBooks }} 本书，第 {{ currentPage }} / {{ totalPages }} 页
            </div>
            <div class="pagination-controls">
              <button class="pagination-btn" @click="goToFirstPage" :disabled="currentPage === 1">首页</button>
              <button class="pagination-btn" @click="goToPrevPage" :disabled="currentPage === 1">上一页</button>
              <span
                v-for="page in visiblePages"
                :key="page"
                class="pagination-page"
                :class="{ active: page === currentPage }"
                @click="goToPage(page)"
              >
                {{ page }}
              </span>
              <button class="pagination-btn" @click="goToNextPage" :disabled="currentPage === totalPages">下一页</button>
              <button class="pagination-btn" @click="goToLastPage" :disabled="currentPage === totalPages">末页</button>
            </div>
          </div>
        </div>

        <div class="sidebar" v-if="currentBook">
          <h3 class="section-title">教材详情</h3>

          <div class="book-summary">
            <h4>{{ currentBook.title }}</h4>
            <p class="book-author">作者：{{ currentBook.author || '未知' }}</p>
            <p class="book-desc">{{ currentBook.description || '暂无简介' }}</p>
            <div class="book-meta-full">
              <div class="meta-row">
                <span class="meta-label">ISBN：</span>
                <span>{{ currentBook.isbn || '-' }}</span>
              </div>
              <div class="meta-row">
                <span class="meta-label">语言：</span>
                <span>{{ currentBook.language || 'zh-CN' }}</span>
              </div>
              <div class="meta-row">
                <span class="meta-label">分类：</span>
                <span>{{ currentBook.category || '-' }}</span>
              </div>
              <div class="meta-row">
                <span class="meta-label">版本：</span>
                <span>v{{ currentBook.version_number || '1.0.0' }}</span>
              </div>
              <div class="meta-row">
                <span class="meta-label">章节数：</span>
                <span>{{ currentBook.chapter_count || 0 }}</span>
              </div>
              <div class="meta-row">
                <span class="meta-label">字数：</span>
                <span>{{ currentBook.word_count || 0 }}</span>
              </div>
              <div class="meta-row">
                <span class="meta-label">创建时间：</span>
                <span>{{ formatDateTime(currentBook.created_at) }}</span>
              </div>
              <div class="meta-row">
                <span class="meta-label">更新时间：</span>
                <span>{{ formatDateTime(currentBook.updated_at) }}</span>
              </div>
            </div>
          </div>

          <div class="versions-header">
            <span>修改历史</span>
            <button class="btn btn-primary btn-sm" @click="viewFullHistory">查看完整历史</button>
          </div>

          <div v-if="historyLoading" class="empty-tip small">正在加载历史...</div>
          <div v-else-if="history.length === 0" class="empty-tip small">暂无修改记录</div>

          <ul v-else class="history-list">
            <li v-for="item in history" :key="item.id" class="history-item">
              <div class="history-header">
                <span class="history-action">{{ item.action_display }}</span>
                <span class="history-time">{{ formatDateTime(item.created_at) }}</span>
              </div>
              <div class="history-actor">
                <span>{{ item.actor_name }}</span>
                <span v-if="item.actor_employee_id">({{ item.actor_employee_id }})</span>
                <span v-if="item.actor_department">- {{ item.actor_department }}</span>
              </div>
              <div class="history-version" v-if="item.version_number">
                版本: v{{ item.version_number }}
                <span v-if="item.previous_version">(上一版本: v{{ item.previous_version }})</span>
              </div>
              <div class="history-summary" v-if="item.changes_summary">
                {{ item.changes_summary }}
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </ReviewLayout>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { booksApi } from '../api/review'

const router = useRouter()

const books = ref([])
const currentBook = ref(null)
const history = ref([])
const loading = ref(false)
const historyLoading = ref(false)

const keyword = ref('')
const hasSearched = ref(false)
const statusFilter = ref('')
const categoryFilter = ref('')

const currentPage = ref(1)
const pageSize = ref(20)
const totalBooks = ref(0)
const totalPages = ref(1)

const categories = ref(['计算机科学', '数学', '物理', '化学', '生物', '文学', '历史', '哲学'])

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(totalPages.value, start + maxVisible - 1)
  
  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

const loadBooks = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }
    
    if (keyword.value) {
      params.search = keyword.value
      hasSearched.value = true
    }
    
    if (statusFilter.value) {
      params.status = statusFilter.value
    }
    
    if (categoryFilter.value) {
      params.category = categoryFilter.value
    }
    
    const data = await booksApi.getList(params)
    books.value = data.results || data
    totalBooks.value = data.count || 0
    totalPages.value = Math.ceil(totalBooks.value / pageSize.value)
    
    if (books.value.length > 0 && !currentBook.value) {
      currentBook.value = books.value[0]
      loadHistory(currentBook.value.id)
    }
  } catch (err) {
    console.error('加载教材列表失败', err)
  } finally {
    loading.value = false
  }
}

const loadHistory = async (bookId) => {
  historyLoading.value = true
  try {
    const data = await booksApi.getHistory(bookId)
    // 合并编辑历史和版本历史
    const editHistory = data.edit_history || []
    const versions = data.versions || []
    
    // 统一格式
    const mergedHistory = [
      ...editHistory.map(item => ({
        ...item,
        type: 'edit'
      })),
      ...versions.map(item => ({
        id: item.id,
        action_display: '版本更新',
        created_at: item.created_at,
        actor_name: item.created_by_name,
        version_number: item.version_number,
        changes_summary: item.comment || '创建新版本',
        type: 'version'
      }))
    ]
    
    // 按时间排序
    history.value = mergedHistory.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
  } catch (err) {
    console.error('加载修改历史失败', err)
  } finally {
    historyLoading.value = false
  }
}

const selectBook = (book) => {
  currentBook.value = book
  loadHistory(book.id)
}

const resetSearch = () => {
  keyword.value = ''
  hasSearched.value = false
  currentPage.value = 1
  loadBooks()
}

const goToFirstPage = () => {
  currentPage.value = 1
  loadBooks()
}

const goToPrevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    loadBooks()
  }
}

const goToNextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadBooks()
  }
}

const goToLastPage = () => {
  currentPage.value = totalPages.value
  loadBooks()
}

const goToPage = (page) => {
  currentPage.value = page
  loadBooks()
}

const viewFullHistory = () => {
  if (currentBook.value) {
    router.push(`/review/books/${currentBook.value.id}/history`)
  }
}

const getStatusText = (status) => {
  const statusMap = {
    'draft': '草稿',
    'pending_review': '待审核',
    'reviewing': '审核中',
    'approved': '已通过',
    'rejected': '已驳回',
    'published': '已发布',
    'archived': '已归档'
  }
  return statusMap[status] || status
}

const formatTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const getCoverColor = (id) => {
  const colors = ['#1890ff', '#52c41a', '#faad14', '#f5222d', '#722ed1', '#13c2c2']
  return colors[id % colors.length]
}

onMounted(() => {
  loadBooks()
})
</script>

<style scoped>
.review-books {
  padding: 24px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding: 16px;
  background: var(--white);
  border-radius: 8px;
  box-shadow: var(--shadow);
}

.search-group {
  display: flex;
  gap: 12px;
  flex: 1;
}

.search-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
}

.search-button {
  padding: 8px 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.search-button.back-button {
  background: #8c8c8c;
}

.toolbar-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
  background: var(--white);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
}

.select {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-size: 14px;
  background: var(--white);
}

.layout {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
}

.books-list {
  background: var(--white);
  border-radius: 8px;
  padding: 24px;
  box-shadow: var(--shadow);
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.empty-tip {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

.empty-tip.small {
  padding: 20px;
}

.book-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.3s;
}

.book-card:hover {
  border-color: var(--primary-color);
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.15);
}

.book-card.active {
  border-color: var(--primary-color);
  background: #f0f5ff;
}

.book-cover {
  width: 80px;
  height: 112px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: white;
  flex-shrink: 0;
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 4px;
}

.book-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.book-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.book-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color);
}

.status-tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-tag.status-draft { background: #f0f0f0; color: #595959; }
.status-tag.status-pending_review { background: #fff7e6; color: #fa8c16; }
.status-tag.status-reviewing { background: #e6f7ff; color: #1890ff; }
.status-tag.status-approved { background: #f6ffed; color: #52c41a; }
.status-tag.status-rejected { background: #fff2f0; color: #f5222d; }
.status-tag.status-published { background: #f6ffed; color: #52c41a; }

.book-author {
  margin: 0;
  font-size: 14px;
  color: var(--text-secondary);
}

.book-desc {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.book-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: var(--text-secondary);
}

.book-time {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-secondary);
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 2px 8px;
  background: #e6f7ff;
  color: #1890ff;
  border-radius: 4px;
  font-size: 12px;
}

.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.pagination-info {
  color: var(--text-secondary);
  font-size: 14px;
}

.pagination-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}

.pagination-btn {
  padding: 6px 12px;
  background: var(--white);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-page {
  padding: 6px 12px;
  cursor: pointer;
  font-size: 14px;
}

.pagination-page.active {
  background: var(--primary-color);
  color: white;
  border-radius: 4px;
}

.sidebar {
  background: var(--white);
  border-radius: 8px;
  padding: 24px;
  box-shadow: var(--shadow);
  height: fit-content;
}

.book-summary {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.book-summary h4 {
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
}

.book-summary .book-author {
  margin-bottom: 8px;
}

.book-summary .book-desc {
  margin-bottom: 16px;
}

.book-meta-full {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.meta-row {
  display: flex;
  font-size: 13px;
}

.meta-label {
  width: 80px;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.versions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid var(--primary-color);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.history-action {
  padding: 2px 8px;
  background: var(--primary-color);
  color: white;
  border-radius: 4px;
  font-size: 12px;
}

.history-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.history-actor {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.history-version {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.history-summary {
  font-size: 13px;
  color: var(--text-primary);
  background: white;
  padding: 8px;
  border-radius: 4px;
}
</style>

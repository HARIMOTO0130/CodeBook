<template>
  <ProviderLayout>
    <div class="provider-versions">
      <!-- 工具栏 -->
    <div class="toolbar">
      <select v-model="selectedBookId" class="select" @change="onBookChange">
        <option disabled value="">请选择教材查看版本...</option>
        <option v-for="b in books.filter(Boolean)" :key="b.id" :value="b.id">
          {{ b.title }}
        </option>
      </select>
      <select v-model="selectedChapterId" class="select" @change="onChapterChange" :disabled="!selectedBookId">
        <option disabled value="">请选择章节（可选）</option>
        <option v-for="c in chapters" :key="c.id" :value="c.id">
          {{ c.title }}
        </option>
      </select>
      <button class="btn" @click="loadBooks">刷新列表</button>
    </div>

      <div v-if="loadingBooks" class="empty-tip">正在加载教材列表...</div>

      <div v-else-if="!selectedBookId" class="empty-tip">
        请选择上方书籍卡片或下拉框中的教材，查看版本历史。
      </div>

      <div v-else class="version-panel">
        <div class="top-bar">
          <h3 class="section-title">版本历史</h3>
          <div class="compare-controls">
            <button class="btn compare-btn" :disabled="selectedVersions.length !== 2" @click="compareVersions">
              对比选中版本
            </button>
            <button class="btn" @click="clearSelection">清除选择</button>
          </div>
        </div>

        <div v-if="loadingVersions" class="empty-tip small">正在加载版本...</div>
        <div v-else-if="versions.length === 0" class="empty-tip small">
          {{ selectedChapterId ? '该章节' : '该教材' }}暂无版本记录。
        </div>

        <ul class="version-list">
          <li
            v-for="ver in versions"
            :key="ver.id"
            class="version-item"
            :class="{ 'selected': selectedVersions.includes(ver.id) }"
          >
            <div class="version-checkbox">
              <input type="checkbox" v-model="selectedVersions" :value="ver.id" @change="onVersionSelect(ver.id)" />
            </div>
            <div class="version-main" @click="goToVersionDetail(ver)">
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

        <!-- 版本对比结果区域 -->
        <div v-if="showCompare" class="compare-result">
          <div class="compare-header">
            <h3>版本对比结果</h3>
            <button class="btn close-btn" @click="closeCompare">关闭对比</button>
          </div>
          <div v-if="loadingCompare" class="loading-tip">正在对比版本...</div>
          <div v-else-if="compareError" class="error-tip">对比失败：{{ compareError }}</div>
          <div v-else-if="compareResult" class="compare-content">
            <div class="compare-info">
              <div class="version-info">
                <h4>版本 1</h4>
                <p>版本号：v{{ compareResult.version1.version_number }}</p>
                <p>创建时间：{{ formatTime(compareResult.version1.created_at) }}</p>
                <p>创建人：{{ compareResult.version1.created_by }}</p>
              </div>
              <div class="version-info">
                <h4>版本 2</h4>
                <p>版本号：v{{ compareResult.version2.version_number }}</p>
                <p>创建时间：{{ formatTime(compareResult.version2.created_at) }}</p>
                <p>创建人：{{ compareResult.version2.created_by }}</p>
              </div>
            </div>
            
            <div class="diff-sections">
              <div v-if="compareResult.base_diff.title" class="diff-section">
                <h5>标题</h5>
                <div class="diff-content">
                  <div class="diff-left">{{ compareResult.version1.title }}</div>
                  <div class="diff-right">{{ compareResult.version2.title }}</div>
                </div>
              </div>
              
              <div v-if="compareResult.base_diff.author" class="diff-section">
                <h5>作者</h5>
                <div class="diff-content">
                  <div class="diff-left">{{ compareResult.version1.author }}</div>
                  <div class="diff-right">{{ compareResult.version2.author }}</div>
                </div>
              </div>
              
              <div v-if="compareResult.base_diff.description" class="diff-section">
                <h5>描述</h5>
                <div class="diff-content">
                  <pre class="diff-text left" v-html="formatDiff(compareResult.diff_details.description)"></pre>
                  <pre class="diff-text right">{{ compareResult.version2.description }}</pre>
                </div>
              </div>
              
              <!-- 章节内容差异 -->
              <div v-if="compareResult.base_diff.content" class="diff-section">
                <h5>内容</h5>
                <div class="diff-content">
                  <pre class="diff-text left" v-html="formatDiff(compareResult.diff_details.content)"></pre>
                  <pre class="diff-text right">{{ compareResult.version2.content }}</pre>
                </div>
              </div>
              
              <!-- 代码差异 -->
              <div v-if="compareResult.base_diff.code" class="diff-section">
                <h5>代码</h5>
                <div class="diff-content">
                  <pre class="diff-text code left" v-html="formatDiff(compareResult.diff_details.code)"></pre>
                  <pre class="diff-text code right">{{ compareResult.version2.code }}</pre>
                </div>
              </div>
              
              <!-- Jupyter内容差异 -->
              <div v-if="compareResult.base_diff.jupyter_content" class="diff-section">
                <h5>Jupyter内容</h5>
                <div class="diff-content">
                  <pre class="diff-text left" v-html="formatDiff(compareResult.diff_details.jupyter_content)"></pre>
                  <pre class="diff-text right">{{ compareResult.version2.jupyter_content }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    <!-- 书籍列表展示区域 -->
    <div class="books-section">
      <h2 class="section-title">书籍列表</h2>
      <div v-if="loadingBooks" class="empty-tip">正在加载教材列表...</div>
      <div v-else-if="books.length === 0" class="empty-tip">暂无书籍</div>
      <div v-else class="books-grid">
        <div 
          v-for="book in books.filter(Boolean)" 
          :key="book.id"
          class="book-card"
          :class="{ 'active': selectedBookId === book.id }"
          @click="selectBook(book.id)"
        >
          <div class="book-cover" :style="{ backgroundColor: getBookCoverColor(book.id) }">
            <span v-if="!book.cover">{{ book.title?.charAt(0) || '书' }}</span>
            <img v-else :src="book.cover" :alt="book.title" />
          </div>
          <div class="book-info">
            <h3 class="book-title">{{ book.title }}</h3>
            <p class="book-author">{{ book.author }}</p>
            <div class="book-meta">
              <span v-if="book.current_version" class="meta-item">v{{ book.current_version }}</span>
              <span v-if="book.total_chapters" class="meta-item">{{ book.total_chapters }} 章</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>
  </ProviderLayout>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import ProviderLayout from './ProviderLayout.vue'
import { providerApi } from '../api/index.js'

const router = useRouter()

const books = ref([])
const chapters = ref([])
const versions = ref([])
const selectedBookId = ref('')
const selectedChapterId = ref('')
const selectedVersions = ref([])

const loadingBooks = ref(false)
const loadingChapters = ref(false)
const loadingVersions = ref(false)
const loadingCompare = ref(false)
const showCompare = ref(false)
const compareResult = ref(null)
const compareError = ref('')

// 加载教材列表
const loadBooks = async () => {
  loadingBooks.value = true
  try {
    const data = await providerApi.listBooks()
    // 处理后端的分页响应
    if (data.results) {
      // 有分页信息的情况
      books.value = data.results
    } else {
      // 没有分页信息的情况（兼容旧版本）
      books.value = Array.isArray(data) ? data : []
    }
  } catch (e) {
    console.error('加载教材列表失败', e)
    books.value = []
  } finally {
    loadingBooks.value = false
  }
}

// 加载章节列表
const loadChapters = async () => {
  if (!selectedBookId.value) return
  
  loadingChapters.value = true
  selectedChapterId.value = ''
  chapters.value = []
  
  try {
    const bookDetail = await providerApi.getBookDetail(selectedBookId.value)
    chapters.value = bookDetail.chapters || []
  } catch (e) {
    console.error('加载章节列表失败', e)
  } finally {
    loadingChapters.value = false
  }
}

// 加载版本列表
const loadVersions = async () => {
  if (!selectedBookId.value) return
  
  loadingVersions.value = true
  selectedVersions.value = []
  showCompare.value = false
  
  try {
    if (selectedChapterId.value) {
      // 加载章节版本
      versions.value = await providerApi.listChapterVersions(selectedChapterId.value)
    } else {
      // 加载书籍版本
      versions.value = await providerApi.listVersions(selectedBookId.value)
    }
  } catch (e) {
    console.error('加载版本失败', e)
    versions.value = []
  } finally {
    loadingVersions.value = false
  }
}



// 选择书籍（点击书籍卡片时调用）
const selectBook = (bookId) => {
  selectedBookId.value = bookId
  onBookChange()
}

const onBookChange = () => {
  loadChapters()
  loadVersions()
}

// 获取书籍封面颜色
const getBookCoverColor = (bookId) => {
  const colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0', '#FF5722', '#00BCD4', '#8BC34A']
  return colors[Math.abs(bookId) % colors.length]
}

const onChapterChange = () => {
  loadVersions()
}

const onVersionSelect = (versionId) => {
  // 限制最多选择两个版本
  if (selectedVersions.value.length > 2) {
    selectedVersions.value = selectedVersions.value.filter(id => id === versionId)
  }
}

const clearSelection = () => {
  selectedVersions.value = []
  showCompare.value = false
  compareResult.value = null
  compareError.value = ''
}

// 跳转到版本详情页
const goToVersionDetail = (ver) => {
  if (!ver || !ver.id) return

  // 目前只为“书籍版本”提供详情页；章节版本后续可扩展
  if (selectedChapterId.value) {
    return
  }

  if (selectedBookId.value) {
    router.push({
      name: 'ProviderBookVersionDetail',
      params: {
        bookId: selectedBookId.value,
        versionId: ver.id,
      },
    })
  }
}

const compareVersions = async () => {
  if (selectedVersions.value.length !== 2) return
  
  showCompare.value = true
  loadingCompare.value = false
  compareError.value = ''
  
  try {
    const [version1Id, version2Id] = selectedVersions.value
    
    if (selectedChapterId.value) {
      // 对比章节版本
      compareResult.value = await providerApi.compareChapterVersions(version1Id, version2Id)
    } else {
      // 对比书籍版本
      compareResult.value = await providerApi.compareBookVersions(version1Id, version2Id)
    }
  } catch (e) {
    console.error('版本对比失败', e)
    compareError.value = e.message || '对比失败，请重试'
  } finally {
    loadingCompare.value = false
  }
}

const closeCompare = () => {
  showCompare.value = false
  compareResult.value = null
  compareError.value = ''
}

const formatDiff = (diffLines) => {
  if (!diffLines || !Array.isArray(diffLines)) return ''
  
  return diffLines.map(line => {
    let className = ''
    if (line.startsWith('+')) {
      className = 'diff-add'
    } else if (line.startsWith('-')) {
      className = 'diff-delete'
    } else {
      className = 'diff-unchanged'
    }
    return `<span class="${className}">${line}</span>`
  }).join('\n')
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
  transition: all 0.3s;
}

.btn:hover {
  border-color: #409eff;
  color: #409eff;
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.compare-btn {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.compare-btn:hover:not(:disabled) {
  background: #409eff;
  color: #fff;
}

.close-btn {
  background: #fef0f0;
  border-color: #f56c6c;
  color: #f56c6c;
}

.close-btn:hover {
  background: #f56c6c;
  color: #fff;
}

.section-title {
  margin-bottom: 8px;
  font-size: 18px;
}

.version-panel {
  margin-top: 4px;
}

.top-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.compare-controls {
  display: flex;
  gap: 8px;
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
  padding: 8px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  gap: 8px;
  align-items: flex-start;
  transition: all 0.3s;
}

.version-item:hover {
  background-color: #f5f7fa;
}

.version-item.selected {
  background-color: #ecf5ff;
  border-radius: 4px;
}

.version-checkbox {
  margin-top: 2px;
}

.version-main {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
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
  flex: 1;
}

.version-comment {
  font-size: 12px;
  color: #666;
  margin-top: 2px;
  flex: 1;
}

/* 对比结果样式 */
.compare-result {
  margin-top: 20px;
  padding: 16px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  background: #fff;
}

.compare-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.compare-header h3 {
  margin: 0;
  font-size: 16px;
  color: #303133;
}

.loading-tip {
  text-align: center;
  padding: 20px;
  color: #909399;
}

.error-tip {
  padding: 12px;
  background-color: #fef0f0;
  color: #f56c6c;
  border-radius: 4px;
  margin-bottom: 16px;
}

.compare-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.compare-info {
  display: flex;
  gap: 40px;
  padding: 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.version-info {
  flex: 1;
}

.version-info h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #606266;
}

.version-info p {
  margin: 4px 0;
  font-size: 12px;
  color: #909399;
}

.diff-sections {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.diff-section {
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.diff-section h5 {
  margin: 0;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
  font-size: 13px;
  color: #606266;
}

.diff-content {
  display: flex;
  gap: 20px;
}

.diff-left, .diff-right {
  flex: 1;
  padding: 12px;
  background-color: #fff;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.6;
}

.diff-text {
  flex: 1;
  padding: 12px;
  background-color: #fff;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  font-size: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  font-family: monospace;
}

.diff-text.left {
  border-right: none;
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
}

.diff-text.right {
  border-left: none;
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
}

.diff-add {
  color: #67c23a;
  background-color: #f0f9eb;
}

.diff-delete {
  color: #f56c6c;
  background-color: #fef0f0;
}

.diff-unchanged {
  color: #303133;
}

/* 书籍列表区域 */
.books-section {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0 0 16px 0;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 16px;
}

.book-card {
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  background: #fff;
}

.book-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

.book-card.active {
  border-color: #409eff;
  background: #ecf5ff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.book-cover {
  width: 100%;
  height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  color: white;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-info {
  padding: 12px;
}

.book-title {
  font-size: 14px;
  font-weight: bold;
  color: #333;
  margin: 0 0 6px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author {
  font-size: 12px;
  color: #666;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: #999;
}

.meta-item {
  display: inline-block;
  padding: 2px 6px;
  background: #f5f7fa;
  border-radius: 3px;
}
</style>



<template>
  <div class="jupyter-documents-list">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">我的Jupyter文档</h1>
        <button @click="createNewDocument" class="btn btn-primary">
          <i class="icon-plus"></i> 新建文档
        </button>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filter-section">
      <div class="search-filter-content">
        <div class="search-box">
          <input 
            v-model="searchQuery" 
            type="text" 
            placeholder="搜索文档标题..." 
            class="search-input"
            @input="handleSearch"
          />
          <i class="icon-search"></i>
        </div>
        <div class="filter-controls">
          <select v-model="filterType" class="filter-select" @change="handleFilterChange">
            <option value="all">全部文档</option>
            <option value="public">公开文档</option>
            <option value="private">私有文档</option>
          </select>
          <select v-model="sortBy" class="sort-select" @change="handleSortChange">
            <option value="updated_at">最近更新</option>
            <option value="created_at">创建时间</option>
            <option value="title">标题</option>
          </select>
        </div>
      </div>
    </div>

    <!-- 文档列表 -->
    <div class="documents-container">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>加载文档中...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="errorMessage" class="error-state">
        <p>{{ errorMessage }}</p>
        <button @click="loadDocuments" class="btn btn-secondary">重试</button>
      </div>

      <!-- 空状态 -->
      <div v-else-if="filteredDocuments.length === 0" class="empty-state">
        <div class="empty-icon">📓</div>
        <h3>{{ searchQuery || filterType !== 'all' ? '没有找到匹配的文档' : '还没有任何文档' }}</h3>
        <p>{{ searchQuery || filterType !== 'all' ? '尝试更改搜索条件或筛选条件' : '点击上方按钮创建您的第一个文档' }}</p>
        <button @click="createNewDocument" class="btn btn-primary">
          <i class="icon-plus"></i> 新建文档
        </button>
      </div>

      <!-- 文档卡片列表 -->
      <div v-else class="documents-grid">
        <div 
          v-for="document in filteredDocuments" 
          :key="document.id" 
          class="document-card"
          @click="openDocument(document.id)"
        >
          <div class="document-header">
            <div class="document-title">{{ document.title || '无标题文档' }}</div>
            <div class="document-tags">
              <span v-if="document.is_public" class="tag public-tag">公开</span>
              <span v-if="document.book_id" class="tag book-tag">关联教材</span>
            </div>
          </div>
          <div class="document-preview">
            <p class="preview-text">{{ getDocumentPreview(document.content) }}</p>
          </div>
          <div class="document-footer">
            <div class="document-meta">
              <span class="meta-item">
                <i class="icon-time"></i>
                {{ formatDate(document.updated_at) }}
              </span>
              <span class="meta-item" v-if="document.created_at !== document.updated_at">
                <i class="icon-edit"></i>
                {{ getTimeAgo(document.updated_at) }}
              </span>
            </div>
            <div class="document-actions">
              <button 
                @click.stop="togglePublicStatus(document)" 
                class="action-btn"
                :title="document.is_public ? '设为私有' : '设为公开'"
              >
                <i :class="document.is_public ? 'icon-lock-open' : 'icon-lock'"></i>
              </button>
              <button 
                @click.stop="deleteDocument(document.id)" 
                class="action-btn delete-btn"
                title="删除文档"
              >
                <i class="icon-trash"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 分页 -->
    <div v-if="!isLoading && filteredDocuments.length > 0" class="pagination">
      <button 
        @click="currentPage = Math.max(1, currentPage - 1)" 
        :disabled="currentPage === 1"
        class="btn btn-secondary"
      >
        上一页
      </button>
      <span class="page-info">第 {{ currentPage }} 页，共 {{ totalPages }} 页</span>
      <button 
        @click="currentPage = Math.min(totalPages, currentPage + 1)" 
        :disabled="currentPage === totalPages"
        class="btn btn-secondary"
      >
        下一页
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/api.js'

export default {
  name: 'JupyterDocumentsListView',
  setup() {
    const router = useRouter()
    
    // 状态管理
    const documents = ref([])
    const isLoading = ref(false)
    const errorMessage = ref('')
    const searchQuery = ref('')
    const filterType = ref('all')
    const sortBy = ref('updated_at')
    const currentPage = ref(1)
    const pageSize = 10

    // 计算属性：过滤和排序后的文档列表
    const filteredDocuments = computed(() => {
      let filtered = [...documents.value]
      
      // 搜索过滤
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(doc => 
          doc.title?.toLowerCase().includes(query) || 
          doc.content?.toLowerCase().includes(query)
        )
      }
      
      // 类型过滤
      if (filterType.value === 'public') {
        filtered = filtered.filter(doc => doc.is_public)
      } else if (filterType.value === 'private') {
        filtered = filtered.filter(doc => !doc.is_public)
      }
      
      // 排序
      filtered.sort((a, b) => {
        if (sortBy.value === 'title') {
          return (a.title || '').localeCompare(b.title || '')
        } else {
          return new Date(b[sortBy.value]) - new Date(a[sortBy.value])
        }
      })
      
      // 分页
      const start = (currentPage.value - 1) * pageSize
      const end = start + pageSize
      return filtered.slice(start, end)
    })

    // 计算属性：总页数
    const totalPages = computed(() => {
      let filtered = [...documents.value]
      
      // 应用相同的过滤逻辑
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(doc => 
          doc.title?.toLowerCase().includes(query) || 
          doc.content?.toLowerCase().includes(query)
        )
      }
      
      if (filterType.value === 'public') {
        filtered = filtered.filter(doc => doc.is_public)
      } else if (filterType.value === 'private') {
        filtered = filtered.filter(doc => !doc.is_public)
      }
      
      return Math.ceil(filtered.length / pageSize)
    })

    // 加载文档列表
    const loadDocuments = async () => {
      try {
        isLoading.value = true
        errorMessage.value = ''
        documents.value = await api.getJupyterDocuments()
      } catch (error) {
        console.error('加载文档列表失败:', error)
        errorMessage.value = '加载文档失败，请重试'
      } finally {
        isLoading.value = false
      }
    }

    // 创建新文档
    const createNewDocument = () => {
      router.push('/jupyter/new')
    }

    // 打开文档
    const openDocument = (id) => {
      router.push(`/jupyter/${id}`)
    }

    // 切换公开状态
    const togglePublicStatus = async (document) => {
      try {
        const newPublicStatus = !document.is_public
        await api.updateJupyterDocument(document.id, {
          is_public: newPublicStatus
        })
        
        // 更新本地状态
        const docIndex = documents.value.findIndex(doc => doc.id === document.id)
        if (docIndex !== -1) {
          documents.value[docIndex].is_public = newPublicStatus
          documents.value[docIndex].updated_at = new Date().toISOString()
        }
        
        console.log('文档状态已更新')
      } catch (error) {
        console.error('更新文档状态失败:', error)
        alert('更新失败，请重试')
      }
    }

    // 删除文档
    const deleteDocument = async (id) => {
      if (!confirm('确定要删除这个文档吗？此操作无法撤销。')) {
        return
      }

      try {
        await api.deleteJupyterDocument(id)
        // 从本地列表中移除
        documents.value = documents.value.filter(doc => doc.id !== id)
        console.log('文档已删除')
      } catch (error) {
        console.error('删除文档失败:', error)
        alert('删除失败，请重试')
      }
    }

    // 搜索处理
    const handleSearch = () => {
      currentPage.value = 1 // 重置到第一页
    }

    // 筛选处理
    const handleFilterChange = () => {
      currentPage.value = 1
    }

    // 排序处理
    const handleSortChange = () => {
      currentPage.value = 1
    }

    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // 获取相对时间
    const getTimeAgo = (dateString) => {
      if (!dateString) return ''
      const now = new Date()
      const date = new Date(dateString)
      const diffMs = now - date
      const diffMins = Math.floor(diffMs / 60000)
      const diffHours = Math.floor(diffMins / 60)
      const diffDays = Math.floor(diffHours / 24)

      if (diffMins < 1) return '刚刚'
      if (diffMins < 60) return `${diffMins}分钟前`
      if (diffHours < 24) return `${diffHours}小时前`
      if (diffDays < 30) return `${diffDays}天前`
      return formatDate(dateString)
    }

    // 获取文档预览
    const getDocumentPreview = (content) => {
      if (!content) return '空文档'
      
      try {
        // 尝试解析JSON内容
        const cells = JSON.parse(content)
        if (Array.isArray(cells)) {
          // 获取前几个单元格的内容作为预览
          const previewTexts = cells.slice(0, 2).map(cell => {
            if (cell.source) {
              return typeof cell.source === 'string' ? cell.source : cell.source.join('')
            }
            return ''
          }).join(' ')
          
          // 移除Markdown标记和多余空白
          const plainText = previewTexts
            .replace(/#{1,6}\s/g, '') // 移除标题标记
            .replace(/\*\*|__/g, '') // 移除加粗标记
            .replace(/\*|_/g, '') // 移除斜体标记
            .replace(/\n+/g, ' ') // 换行替换为空格
            .replace(/\s+/g, ' ') // 多余空格合并
            .trim()
          
          return plainText.length > 100 ? plainText.substring(0, 100) + '...' : plainText
        }
      } catch (e) {
        // 如果不是JSON格式，直接截取文本
        return content.length > 100 ? content.substring(0, 100) + '...' : content
      }
      
      return '文档内容'
    }

    // 监听页码变化，重新加载数据
    watch(currentPage, () => {
      // 这里可以根据需要实现分页加载逻辑
      // 目前是前端分页，不需要重新请求API
    })

    // 组件挂载时加载文档列表
    onMounted(() => {
      loadDocuments()
    })

    return {
      documents,
      isLoading,
      errorMessage,
      searchQuery,
      filterType,
      sortBy,
      currentPage,
      filteredDocuments,
      totalPages,
      loadDocuments,
      createNewDocument,
      openDocument,
      togglePublicStatus,
      deleteDocument,
      handleSearch,
      handleFilterChange,
      handleSortChange,
      formatDate,
      getTimeAgo,
      getDocumentPreview
    }
  }
}
</script>

<style scoped>
.jupyter-documents-list {
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* 页面头部 */
.page-header {
  background-color: white;
  border-bottom: 1px solid #e0e0e0;
  padding: 20px 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #333;
}

/* 搜索和筛选 */
.search-filter-section {
  background-color: white;
  padding: 16px 0;
  border-bottom: 1px solid #e0e0e0;
}

.search-filter-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  gap: 16px;
  align-items: center;
  flex-wrap: wrap;
}

.search-box {
  flex: 1;
  min-width: 300px;
  position: relative;
}

.search-input {
  width: 100%;
  padding: 10px 16px 10px 40px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
}

.search-input:focus {
  border-color: #1976d2;
}

.search-box i {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
}

.filter-controls {
  display: flex;
  gap: 12px;
}

.filter-select, .sort-select {
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.3s;
}

.filter-select:focus, .sort-select:focus {
  border-color: #1976d2;
}

/* 文档容器 */
.documents-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px;
  min-height: 500px;
}

/* 状态样式 */
.loading-state, .error-state, .empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: #1976d2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-state p {
  color: #d32f2f;
  margin-bottom: 16px;
}

.empty-state {
  color: #666;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  margin: 0 0 8px;
  font-size: 20px;
  color: #333;
}

.empty-state p {
  margin: 0 0 24px;
}

/* 文档网格 */
.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.document-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
  height: 200px;
  display: flex;
  flex-direction: column;
}

.document-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.document-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.document-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.document-tags {
  display: flex;
  gap: 8px;
}

.tag {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.public-tag {
  background-color: #e3f2fd;
  color: #1976d2;
}

.book-tag {
  background-color: #e8f5e9;
  color: #388e3c;
}

.document-preview {
  flex: 1;
  overflow: hidden;
}

.preview-text {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
  margin: 0;
  display: -webkit-box;
  line-clamp: 4;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.document-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.document-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #999;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.document-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px;
  border: none;
  background: none;
  cursor: pointer;
  border-radius: 4px;
  color: #666;
  transition: all 0.2s;
}

.action-btn:hover {
  background-color: #f5f5f5;
  color: #333;
}

.delete-btn:hover {
  color: #d32f2f;
}

/* 分页 */
.pagination {
  max-width: 1200px;
  margin: 0 auto 40px;
  padding: 0 20px;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

.page-info {
  font-size: 14px;
  color: #666;
}

/* 按钮样式 */
.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
  outline: none;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #1976d2;
  color: white;
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1565c0;
}

.btn-secondary {
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #e0e0e0;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #e0e0e0;
}

/* 图标样式 */
.icon-plus::before { content: '✚'; }
.icon-search::before { content: '🔍'; }
.icon-time::before { content: '🕐'; }
.icon-edit::before { content: '✎'; }
.icon-lock::before { content: '🔒'; }
.icon-lock-open::before { content: '🔓'; }
.icon-trash::before { content: '🗑️'; }

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .search-filter-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    min-width: auto;
  }
  
  .filter-controls {
    flex-direction: column;
  }
  
  .documents-grid {
    grid-template-columns: 1fr;
  }
  
  .document-card {
    height: auto;
    min-height: 180px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 24px;
  }
  
  .documents-container {
    padding: 16px 12px;
  }
  
  .document-card {
    padding: 16px;
  }
  
  .pagination {
    flex-direction: column;
    gap: 12px;
  }
}
</style>
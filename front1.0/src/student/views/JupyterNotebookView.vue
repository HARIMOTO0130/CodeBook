<template>
  <div class="jupyter-notebook-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <input 
            v-model="documentTitle" 
            type="text" 
            class="title-input"
            :placeholder="isNewDocument ? '无标题文档' : '编辑文档'"
            @input="handleTitleChange"
          />
        </h1>
        <div class="header-controls">
          <div class="public-control">
            <label class="public-toggle">
              <input 
                type="checkbox" 
                v-model="documentIsPublic" 
                @change="handlePublicChange"
              />
              <span>公开文档</span>
            </label>
          </div>
          <div class="actions">
            <button 
              @click="deleteDocument" 
              v-if="!isNewDocument" 
              class="btn btn-danger"
              :disabled="isDeleting"
            >
              {{ isDeleting ? '删除中...' : '删除文档' }}
            </button>
            <button @click="goBack" class="btn btn-secondary">返回</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="content-container">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-spinner">
          <div class="spinner"></div>
          <p>{{ isNewDocument ? '准备新文档...' : '加载文档中...' }}</p>
        </div>
      </div>

      <!-- Jupyter笔记本组件 -->
      <JupyterNotebook 
        v-model:title="documentTitle"
        :documentId="documentId"
        v-model:isPublic="documentIsPublic"
        :bookId="bookId"
        :chapterId="chapterId"
        v-model:documentId="documentId"
        @contentChange="handleContentChange"
        @save="handleSave"
        @update:isPublic="handlePublicChange"
      />
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import JupyterNotebook from '../components/JupyterNotebook.vue'
import { api } from '../api/api.js'

export default {
  name: 'JupyterNotebookView',
  components: {
    JupyterNotebook
  },
  setup() {
    const router = useRouter()
    const route = useRoute()

    // 状态管理
    const documentId = ref(route.params.documentId || null)
    const documentTitle = ref('')
    const documentIsPublic = ref(false)
    const isLoading = ref(true)
    const isDeleting = ref(false)
    const bookId = ref(route.query.bookId || null)
    const chapterId = ref(route.query.chapterId || null)
    const lastSavedContent = ref('')

    // 计算属性：判断是否是新建文档
    const isNewDocument = computed(() => !documentId.value)

    // 处理标题变化
    const handleTitleChange = () => {
      // 可以在这里添加自动保存逻辑
    }

    // 处理公开状态变化
    const handlePublicChange = (newValue) => {
      if (typeof newValue === 'boolean') {
        documentIsPublic.value = newValue
      }
      // 公开状态改变后自动保存
      if (!isNewDocument.value) {
        autoSave()
      }
    }

    // 处理内容变化
    const handleContentChange = (content) => {
      // 可以在这里实现自动保存逻辑
    }

    // 自动保存
    const autoSave = async () => {
      // 简单的防抖逻辑，避免频繁保存
      if (autoSaveTimeout) clearTimeout(autoSaveTimeout)
      autoSaveTimeout = setTimeout(async () => {
        // 这里可以实现自动保存功能
        console.log('自动保存触发')
      }, 3000)
    }

    // 处理保存事件
    const handleSave = (saveData) => {
      console.log('文档已保存:', saveData)
      lastSavedContent.value = saveData.content
    }

    // 删除文档
    const deleteDocument = async () => {
      if (!confirm('确定要删除这个文档吗？此操作无法撤销。')) {
        return
      }

      try {
        isDeleting.value = true
        await api.deleteJupyterDocument(documentId.value)
        console.log('文档已删除')
        // 返回上一页或文档列表页
        goBack()
      } catch (error) {
        console.error('删除文档失败:', error)
        alert('删除失败: ' + (error.message || '未知错误'))
      } finally {
        isDeleting.value = false
      }
    }

    // 返回上一页
    const goBack = () => {
      if (isNewDocument.value && documentTitle.value && lastSavedContent.value) {
        // 如果是新建文档且有内容，可以询问是否保存
        const shouldSave = confirm('您的文档有未保存的更改，是否保存后再离开？')
        if (shouldSave) {
          // 触发保存操作
          // 这里需要找到子组件并调用保存方法
          const jupyterComponent = document.querySelector('jupyter-notebook')
          if (jupyterComponent && jupyterComponent.__vueParentComponent?.exposed?.saveNotebook) {
            jupyterComponent.__vueParentComponent.exposed.saveNotebook()
          }
        }
      }
      router.go(-1)
    }

    // 初始化页面数据
    const initializePage = async () => {
      if (isNewDocument.value) {
        // 新建文档，使用默认标题
        documentTitle.value = '无标题文档'
        documentIsPublic.value = false
        isLoading.value = false
      } else {
        // 编辑现有文档，从API获取文档信息
        try {
          isLoading.value = true
          const documentData = await api.getJupyterDocument(documentId.value)
          documentTitle.value = documentData.title || '无标题文档'
          documentIsPublic.value = documentData.is_public || false
          bookId.value = documentData.book_id || null
          chapterId.value = documentData.chapter_id || null
          lastSavedContent.value = documentData.content || ''
        } catch (error) {
          console.error('加载文档信息失败:', error)
          alert('加载文档失败，请重试')
          router.go(-1)
        } finally {
          isLoading.value = false
        }
      }
    }

    // 组件挂载时初始化
    onMounted(() => {
      initializePage()
    })

    // 自动保存定时器
    let autoSaveTimeout = null

    return {
      documentId,
      documentTitle,
      documentIsPublic,
      isLoading,
      isDeleting,
      isNewDocument,
      bookId,
      chapterId,
      handleTitleChange,
      handlePublicChange,
      handleContentChange,
      handleSave,
      deleteDocument,
      goBack
    }
  }
}
</script>

<style scoped>
.jupyter-notebook-view {
  min-height: 100vh;
  background-color: #f5f7fa;
}

/* 页面头部 */
.page-header {
  background-color: white;
  border-bottom: 1px solid #e0e0e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  padding: 16px 0;
  position: sticky;
  top: 0;
  z-index: 100;
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
  flex: 1;
}

.title-input {
  width: 100%;
  max-width: 500px;
  font-size: 24px;
  font-weight: 600;
  border: none;
  outline: none;
  padding: 8px 0;
  background-color: transparent;
  color: #333;
  border-bottom: 2px solid transparent;
  transition: border-color 0.3s;
}

.title-input:focus {
  border-bottom: 2px solid #1976d2;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

/* 公开状态切换 */
.public-control {
  display: flex;
  align-items: center;
}

.public-toggle {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 8px 16px;
  border-radius: 6px;
  transition: background-color 0.2s;
}

.public-toggle:hover {
  background-color: #f5f5f5;
}

.public-toggle input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.public-toggle span {
  font-size: 14px;
  color: #555;
  font-weight: 500;
}

/* 操作按钮 */
.actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 8px 16px;
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

.btn-secondary {
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #e0e0e0;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #e0e0e0;
}

.btn-danger {
  background-color: #f44336;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #d32f2f;
}

/* 主内容区 */
.content-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px;
  position: relative;
}

/* 加载状态 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  text-align: center;
  color: #333;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-left-color: #1976d2;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-spinner p {
  font-size: 16px;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .page-title {
    width: 100%;
  }
  
  .title-input {
    max-width: none;
  }
  
  .header-controls {
    justify-content: space-between;
  }
  
  .content-container {
    padding: 16px 12px;
  }
}

@media (max-width: 480px) {
  .header-controls {
    flex-direction: column;
    gap: 12px;
  }
  
  .actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .btn {
    flex: 1;
    text-align: center;
  }
}
</style>
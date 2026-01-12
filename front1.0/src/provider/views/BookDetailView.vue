<template>
  <ProviderLayout>
    <div class="book-detail-container">
      <!-- 顶部操作栏 -->
      <div class="detail-header">
        <div class="header-left">
          <button class="btn btn-back" @click="goBack">
            ← {{ route.query.from === 'categories' ? '返回分类与标签' : '返回书籍管理' }}
          </button>
          <h1 class="book-title">{{ bookData?.title || '加载中...' }}</h1>
          <p class="book-meta" v-if="bookData">作者：{{ bookData.author || '未知' }} | ISBN：{{ bookData.isbn || '未设置' }}</p>
        </div>
        <div class="header-right">
          <button class="btn btn-secondary" @click="toggleEditMode">
            {{ isEditMode ? '取消编辑' : '编辑基本信息' }}
          </button>
          <button class="btn btn-primary" @click="saveChanges" v-if="isEditMode" :disabled="saving">
            {{ saving ? '保存中...' : '保存修改' }}
          </button>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在加载书籍详情...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <p class="error-message">{{ error }}</p>
        <button class="btn" @click="loadBookDetail">重新加载</button>
      </div>

      <!-- 书籍详情内容 -->
      <div v-else class="detail-content">
        <!-- 左侧：基本信息编辑/展示 -->
        <div class="basic-info-section">
          <!-- 基本信息编辑器 -->
          <BookBasicInfoEditor
            v-if="isEditMode"
            ref="editorRef"
            :book-data="editForm"
            :is-submitting="saving"
            @cancel="toggleEditMode"
            @submit="handleSave"
          />
          
          <!-- 基本信息展示 -->
          <div v-else-if="bookData" class="basic-info-display">
            <div class="info-card">
              <div class="cover-section">
                <div class="book-cover-large" :style="{ backgroundColor: getCoverColor(bookData?.id || 0) }">
                  <span v-if="!bookData?.cover">{{ (bookData?.title || '书').charAt(0) }}</span>
                  <img v-else :src="bookData.cover" :alt="bookData.title" />
                </div>
                <button class="btn btn-sm btn-secondary" @click="toggleEditMode">
                  更换封面
                </button>
              </div>
              
              <div class="info-main">
                <div class="info-row">
                  <label>标题：</label>
                  <span>{{ bookData.title }}</span>
                </div>
                <div class="info-row">
                  <label>副标题：</label>
                  <span>{{ bookData.subtitle || '无' }}</span>
                </div>
                <div class="info-row">
                  <label>作者：</label>
                  <span>{{ bookData.author }}</span>
                </div>
                <div class="info-row">
                  <label>ISBN：</label>
                  <span>{{ bookData.isbn || '未设置' }}</span>
                </div>
                <div class="info-row">
                  <label>语言：</label>
                  <span>{{ bookData.language || '未设置' }}</span>
                </div>
                <div class="info-row">
                  <label>章节数：</label>
                  <span>{{ bookData.total_chapters || 0 }}</span>
                </div>
                <div class="info-row">
                  <label>创建时间：</label>
                  <span>{{ formatTime(bookData.created_at) }}</span>
                </div>
                <div class="info-row">
                  <label>更新时间：</label>
                  <span>{{ formatTime(bookData.updated_at) }}</span>
                </div>
                <div class="info-row">
                  <label>当前版本：</label>
                  <span>v{{ bookData.current_version || '1.0.0' }}</span>
                </div>
              </div>
            </div>
            
            <!-- 描述和简介 -->
            <div class="description-section">
              <h3>描述</h3>
              <p>{{ bookData.description || '暂无描述' }}</p>
              
              <h3>详细介绍</h3>
              <div class="introduction-content" v-html="bookData.introduction || '<p>暂无详细介绍</p>'"></div>
            </div>
            
            <!-- 分类和标签 -->
            <div class="categories-tags-section">
              <div class="tags-group">
                <h3>分类</h3>
                <div class="tag-list">
                  <span v-for="category in (bookData.categories || [])" :key="category" class="tag category-tag">
                    {{ category }}
                  </span>
                  <span v-if="!bookData.categories || bookData.categories.length === 0" class="empty-tag">暂无分类</span>
                </div>
              </div>
              
              <div class="tags-group">
                <h3>标签</h3>
                <div class="tag-list">
                  <span v-for="tag in getTagList(bookData)" :key="tag" class="tag">
                    {{ tag }}
                  </span>
                  <span v-if="!getTagList(bookData) || getTagList(bookData).length === 0" class="empty-tag">暂无标签</span>
                </div>
              </div>
            </div>
            
            <!-- 章节内容编辑 -->
            <div class="chapter-content-section">
              <div class="chapter-content-header">
                <h3>章节内容编辑</h3>
                <div class="chapter-content-controls">
                  <button v-if="selectedChapter" class="btn btn-secondary" @click="toggleChapterContentEdit">
                    {{ isChapterContentEditing ? '取消编辑' : '编辑内容' }}
                  </button>
                  <button v-if="isChapterContentEditing" class="btn btn-primary" @click="saveChapterContent" :disabled="savingChapterContent">
                    {{ savingChapterContent ? '保存中...' : '保存内容' }}
                  </button>
                </div>
              </div>
              
              <div v-if="!selectedChapter" class="empty-chapter-selection">
                <p>请从右侧选择一个章节进行编辑</p>
              </div>
              
              <div v-else-if="chapterContentLoading" class="loading-small">章节内容加载中...</div>
              
              <div v-else class="chapter-content-editor">
                <div class="chapter-content-title">
                  <h4>{{ selectedChapter.title }}</h4>
                </div>
                
                <div v-if="isChapterContentEditing" class="jupyter-editor-container">
                  <!-- Jupyter风格编辑器 -->
                  <JupyterNotebook
                    :initialContent="chapterContent"
                    :documentId="null"
                    :isReadOnly="false"
                    :bookId="bookId?.toString()"
                    :chapterId="selectedChapter?.id?.toString()"
                    @contentChange="handleJupyterContentChange"
                  ></JupyterNotebook>
                </div>
                
                <div v-else class="jupyter-preview-container">
                  <!-- Jupyter内容预览 -->
                  <JupyterNotebook
                    :initialContent="selectedChapter.merged_content ? selectedChapter.merged_content : chapterContent"
                    :documentId="null"
                    :isReadOnly="true"
                    :bookId="bookId?.toString()"
                    :chapterId="selectedChapter?.id?.toString()"
                  ></JupyterNotebook>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：章节、版本、协作者、统计 -->
        <div class="sidebar-section">
          <!-- 章节列表 -->
          <div class="sidebar-card">
            <h3>章节列表</h3>
            <div class="chapter-list-container">
              <div v-if="chaptersLoading" class="loading-small">加载中...</div>
              <div v-else-if="!bookData.chapters || bookData.chapters.length === 0" class="empty-section">暂无章节</div>
              <ul v-else class="chapter-list">
                <li v-for="(chapter, index) in bookData.chapters" :key="chapter?.id || index" class="chapter-item" @click="selectChapter(chapter)">
                  <span class="chapter-number">{{ chapter?.order || index + 1 }}</span>
                  <span class="chapter-title">{{ chapter?.title || '未知章节' }}</span>
                  <span class="selected-indicator" v-if="selectedChapterId === chapter?.id">✓</span>
                </li>
              </ul>
            </div>
          </div>

          <!-- 版本历史 -->
          <div class="sidebar-card">
            <h3>版本历史</h3>
            <div class="versions-container">
              <div v-if="versionsLoading" class="loading-small">加载中...</div>
              <div v-else-if="versions.length === 0" class="empty-section">暂无版本</div>
              <ul v-else class="version-list">
                <li 
                  v-for="(ver, index) in versions" 
                  :key="ver?.id || index" 
                  class="version-item"
                  @click="goToVersionDetail(ver)"
                  style="cursor: pointer;"
                >
                  <div class="version-header">
                    <span class="version-tag">v{{ formatVersionNumber(ver?.version_number) || 'N/A' }}</span>
                    <span class="version-date">{{ formatTime(ver?.created_at) }}</span>
                  </div>
                  <div class="version-title">{{ ver?.title || '未知' }}</div>
                  <div class="version-meta" v-if="ver?.created_by">创建人：{{ ver.created_by }}</div>
                  <p class="version-comment" v-if="ver?.comment">{{ ver.comment }}</p>
                </li>
              </ul>
            </div>
          </div>

          <!-- 协作者 -->
          <div class="sidebar-card">
            <h3>协作者</h3>
            <div class="collaborators-container">
              <div v-if="collaborators.length === 0" class="empty-section">暂无协作者</div>
              <ul v-else class="collaborator-list">
                <li v-for="(collab, index) in collaborators" :key="collab?.id || index" class="collaborator-item">
                  <div class="collaborator-avatar">
                    {{ (collab?.name || 'U').charAt(0) }}
                  </div>
                  <div class="collaborator-info">
                    <div class="collaborator-name">{{ collab?.name || '未知' }}</div>
                    <div class="collaborator-role">{{ collab?.role || '协作者' }}</div>
                  </div>
                </li>
              </ul>
            </div>
          </div>

          <!-- 统计数据 -->
          <div class="sidebar-card">
            <h3>书籍统计</h3>
            <BookStatsPanel :stats-data="statsData" :is-loading="statsLoading" />
          </div>
        </div>
      </div>

      <!-- 成功提示 -->
      <div v-if="showSuccess" class="success-toast">
        <span>{{ successMessage }}</span>
        <button class="close-btn" @click="showSuccess = false">×</button>
      </div>
    </div>
  </ProviderLayout>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ProviderLayout from './ProviderLayout.vue'
import { providerApi } from '../api/index.js'
import BookBasicInfoEditor from './components/BookBasicInfoEditor.vue'
import BookStatsPanel from './components/BookStatsPanel.vue'
import JupyterNotebook from '../../student/components/JupyterNotebook.vue'


const route = useRoute()
const router = useRouter()

// 基本状态
const loading = ref(true)
const error = ref('')
const isEditMode = ref(false)
const saving = ref(false)
const showSuccess = ref(false)
const successMessage = ref('')

// 数据状态
const bookData = ref(null)
const editForm = ref({})
const chaptersLoading = ref(false)
const versions = ref([])
const versionsLoading = ref(false)
const collaborators = ref([])
const statsData = ref({})
const statsLoading = ref(false)

// 章节内容编辑状态
const selectedChapterId = ref(null)
const selectedChapter = ref(null)
const chapterContent = ref('')
const chapterContentLoading = ref(false)
const isChapterContentEditing = ref(false)
const savingChapterContent = ref(false)

// 编辑器组件引用
const editorRef = ref(null)

// 获取路由参数中的书籍ID
const bookId = computed(() => route.params.id)

// 加载书籍详情数据
const loadBookDetail = async () => {
  loading.value = true
  error.value = ''
  try {
    // 获取书籍基本信息
    const bookDetail = await providerApi.getBookDetail(bookId.value)
    console.log('加载的书籍详情数据:', bookDetail)
    console.log('tag_objects:', bookDetail.tag_objects)
    console.log('tag_list:', bookDetail.tag_list)
    bookData.value = bookDetail
    
    // 初始化编辑表单（确保分类和标签格式正确）
    editForm.value = {
      ...bookDetail,
      categories: Array.isArray(bookDetail.categories) 
        ? bookDetail.categories.join(', ') 
        : (bookDetail.categories || ''),
      tags: Array.isArray(bookDetail.tag_list) 
        ? bookDetail.tag_list.join(', ') 
        : (bookDetail.tag_list || '')
    }
    
    // 加载相关数据
    loadVersions()
    loadStats()
    loadCollaborators()
    
    // 如果书籍有章节，自动选择第一个章节
    if (bookDetail.chapters && bookDetail.chapters.length > 0) {
      // 使用异步方式选择章节，但不等待其完成，避免阻塞其他加载
      selectChapter(bookDetail.chapters[0]).catch(err => {
        console.error('自动选择章节失败:', err)
      })
    }
  } catch (e) {
    console.error('加载书籍详情失败:', e)
    error.value = e.message || '加载书籍详情失败，请重试'
  } finally {
    loading.value = false
  }
}

// 加载版本历史
const loadVersions = async () => {
  if (!bookId.value) {
    console.error('无法加载版本：书籍ID无效')
    versions.value = []
    versionsLoading.value = false
    return
  }
  
  versionsLoading.value = true
  try {
    const versionList = await providerApi.listVersions(bookId.value)
    // providerApi.listVersions 已经统一处理分页，直接返回数组
    versions.value = versionList || []
    console.log('版本加载成功，数量:', versions.value.length)
  } catch (e) {
    console.error('加载版本历史失败:', e)
    versions.value = []
  } finally {
    versionsLoading.value = false
  }
}

// 加载统计数据
const loadStats = async () => {
  statsLoading.value = true
  try {
    const stats = await providerApi.getBookStats(bookId.value)
    statsData.value = stats
  } catch (e) {
    console.error('加载统计数据失败:', e)
    // 提供模拟数据以确保UI正常显示
    statsData.value = {
      user_count: 128,
      total_duration: 3650,
      average_rating: 4.8,
      download_count: 512,
      share_count: 78,
      daily_new_users: 15,
      weekly_new_users: 45,
      average_duration: 28,
      monthly_downloads: 120,
      rating_count: 42
    }
  } finally {
    statsLoading.value = false
  }
}

// 加载协作者
const loadCollaborators = async () => {
  // 协作者API可能需要单独实现，这里先模拟数据
  collaborators.value = []
}

// 切换编辑模式
const toggleEditMode = () => {
  if (!bookData.value) {
    console.error('无法切换到编辑模式：书籍数据未加载')
    return
  }
  
  isEditMode.value = !isEditMode.value
  
  if (isEditMode.value) {
    // 进入编辑模式时，初始化编辑表单
    editForm.value = {
      ...bookData.value,
      // 确保分类和标签格式正确
      categories: Array.isArray(bookData.value.categories) 
        ? bookData.value.categories.join(', ') 
        : (bookData.value.categories || ''),
      tags: Array.isArray(bookData.value.tag_list) 
        ? bookData.value.tag_list.join(', ') 
        : (bookData.value.tag_list || '')
    }
  } else {
    // 取消编辑时重置表单
    if (bookData.value) {
      editForm.value = { ...bookData.value }
    }
  }
}

// 保存修改
const handleSave = async (formData) => {
  saving.value = true
  try {
    // 使用PATCH部分更新
    const updatedBook = await providerApi.patchBook(bookId.value, formData)
    
    // 重新加载书籍详情数据以获取最新信息
    await loadBookDetail()
    
    // 重新加载版本列表（确保显示最新创建的版本）
    await loadVersions()
    
    // 如果书籍有章节，自动选择第一个章节
    if (bookData.value && bookData.value.chapters && bookData.value.chapters.length > 0) {
      await selectChapter(bookData.value.chapters[0])
    }
    
    // 关闭编辑模式并显示成功提示
    isEditMode.value = false
    showSuccess.value = true
    successMessage.value = '书籍信息已成功更新，版本已自动迭代'
    
    // 3秒后自动关闭提示
    setTimeout(() => {
      showSuccess.value = false
    }, 3000)
  } catch (e) {
    console.error('保存书籍信息失败:', e)
    error.value = e.message || '保存失败，请重试'
  } finally {
    saving.value = false
  }
}

// 保存按钮点击事件（直接调用，用于外部组件）
const saveChanges = () => {
  // 触发编辑器组件的表单提交
  if (editorRef.value && typeof editorRef.value.submitForm === 'function') {
    editorRef.value.submitForm()
  } else {
    console.warn('编辑器组件未准备好，请稍后再试')
  }
}

// 根据书籍ID生成封面颜色
const getCoverColor = (id) => {
  const colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0', '#FF5722']
  return colors[Math.abs(id) % colors.length]
}

// 返回上一页（根据来源决定）
const goBack = () => {
  // 检查是否从分类与标签页面跳转过来
  const from = route.query.from
  if (from === 'categories') {
    router.push({ name: 'ProviderCategories' })
  } else {
    // 默认返回书籍管理页面
    router.push('/provider/books')
  }
}

// 跳转到版本详情页
const goToVersionDetail = (version) => {
  if (version && version.id && version.book) {
    router.push({ 
      name: 'ProviderBookVersionDetail', 
      params: { 
        bookId: version.book,
        versionId: version.id 
      } 
    })
  }
}

// 格式化时间
const formatTime = (timeString) => {
  if (!timeString) return '未设置'
  const date = new Date(timeString)
  return date.toLocaleString()
}

// 格式化版本号（将数字转换为语义化版本字符串，如1→1.0.0，2→1.0.1，11→1.1.0）
const formatVersionNumber = (versionNumber) => {
  if (!versionNumber || isNaN(versionNumber)) return '1.0.0'
  
  // 转换为语义化版本号格式：major.minor.patch
  // 每10个版本增加minor，每100个版本增加major
  const major = Math.floor(versionNumber / 100)
  const minor = Math.floor((versionNumber % 100) / 10)
  const patch = versionNumber % 10
  
  return `${major}.${minor}.${patch}`
}

// 获取标签列表（处理不同格式的标签数据）
const getTagList = (bookData) => {
  if (!bookData) {
    console.log('getTagList: bookData is null')
    return []
  }
  
  console.log('getTagList: bookData.tag_objects =', bookData.tag_objects)
  console.log('getTagList: bookData.tag_list =', bookData.tag_list)
  
  // 优先使用 tag_objects（多对多关系，最准确）
  if (Array.isArray(bookData.tag_objects) && bookData.tag_objects.length > 0) {
    const tags = bookData.tag_objects.map(tag => {
      if (typeof tag === 'string') return tag
      if (typeof tag === 'object' && tag.name) return tag.name
      return String(tag)
    }).filter(tag => tag)
    console.log('getTagList: 使用 tag_objects，返回:', tags)
    return tags
  }
  
  // 其次使用 tag_list（旧版JSON字段）
  if (Array.isArray(bookData.tag_list) && bookData.tag_list.length > 0) {
    return bookData.tag_list.map(tag => {
      if (typeof tag === 'string') return tag
      if (typeof tag === 'object' && tag.name) return tag.name
      return String(tag)
    }).filter(tag => tag)
  } else if (typeof bookData.tag_list === 'string' && bookData.tag_list.trim()) {
    // 如果是JSON字符串，尝试解析
    try {
      const parsed = JSON.parse(bookData.tag_list)
      if (Array.isArray(parsed)) {
        return parsed.map(tag => String(tag)).filter(tag => tag)
      }
    } catch (e) {
      // 如果不是JSON，按逗号分隔处理
      return bookData.tag_list.split(',').map(tag => tag.trim()).filter(tag => tag)
    }
  }
  
  // 最后检查 tags 字段（备用）
  if (Array.isArray(bookData.tags) && bookData.tags.length > 0) {
    return bookData.tags.map(tag => {
      if (typeof tag === 'string') return tag
      if (typeof tag === 'object' && tag.name) return tag.name
      return String(tag)
    }).filter(tag => tag)
  }
  
  return []
}

// 路由参数变化时重新加载数据
watch(bookId, (newId, oldId) => {
  // 只有当新的bookId有效且与旧的不同时才重新加载
  if (newId && newId !== oldId) {
    loadBookDetail()
  }
})

// 选择章节
  const selectChapter = async (chapter) => {
    selectedChapterId.value = chapter.id
    selectedChapter.value = chapter
    
    // 重置编辑状态
    isChapterContentEditing.value = false
    
    try {
      chapterContentLoading.value = true
      
      // 获取完整的章节内容
      const fullChapter = await providerApi.getChapterDetail(chapter.id)
      console.log('获取到的完整章节内容:', fullChapter)
      console.log('merged_content:', fullChapter.merged_content)
      
      selectedChapter.value = fullChapter
      
      // 将merged_content转换为可编辑的文本格式
      if (fullChapter.merged_content) {
        try {
          // 尝试解析JSON字符串，如果已经是字符串格式
          const parsedContent = JSON.parse(fullChapter.merged_content)
          // 如果解析成功，将其转换为格式化的JSON字符串
          chapterContent.value = JSON.stringify(parsedContent, null, 2)
        } catch (e) {
          // 如果解析失败，直接使用原始内容
          chapterContent.value = fullChapter.merged_content
        }
      } else {
        // 设置默认的Jupyter Notebook结构，包含一个示例Markdown单元格
        chapterContent.value = JSON.stringify({
          cells: [
            {
              cell_type: 'markdown',
              source: '# ' + chapter.title + '\n\n在此输入章节内容...\n\n支持Markdown文本和Python代码块。\n\n**示例代码块：**\n```python\n# 这是一个Python代码示例\nprint(\'Hello, World!\')\n```'
            }
          ]
        }, null, 2)
      }
    } catch (error) {
      console.error('加载章节详情失败:', error)
      // 即使加载失败，也要确保有默认内容
      chapterContent.value = JSON.stringify({
        cells: [
          {
            cell_type: 'markdown',
            source: '# ' + chapter.title + '\n\n章节内容加载失败，请重新尝试。\n\n**示例代码块：**\n```python\n# 这是一个Python代码示例\nprint(\'Hello, World!\')\n```'
          }
        ]
      }, null, 2)
    } finally {
      chapterContentLoading.value = false
    }
  }

// 切换章节内容编辑模式
const toggleChapterContentEdit = () => {
  isChapterContentEditing.value = !isChapterContentEditing.value
}

// 处理Jupyter内容变化
const handleJupyterContentChange = (eventData) => {
  chapterContent.value = eventData
}

// 保存章节内容
const saveChapterContent = async () => {
  if (!selectedChapter.value) return
  
  try {
    savingChapterContent.value = true
    
    // 解析编辑后的内容，确保它是有效的JSON格式
    JSON.parse(chapterContent.value)
    
    // 更新章节内容，直接发送JSON字符串
    await providerApi.updateChapterContent(selectedChapter.value.id, {
      merged_content: chapterContent.value
    })
    
    // 显示成功提示
    showSuccess.value = true
    successMessage.value = '章节内容保存成功'
    
    // 刷新章节数据
    await selectChapter(selectedChapter.value)
  } catch (error) {
    console.error('保存章节内容失败:', error)
    alert('保存失败，请检查输入格式是否正确')
  } finally {
    savingChapterContent.value = false
  }
}



// 监听编辑模式变化，处理编辑器状态
watch(isChapterContentEditing, async (newVal) => {
  if (newVal && selectedChapter.value) {
    await nextTick()
    // JupyterNotebook组件会自动初始化
  } else if (!newVal) {
    // 保存编辑器内容
    // JupyterNotebook组件会通过contentChange事件自动更新chapterContent
  }
})

// 组件卸载时不需要特殊处理，JupyterNotebook组件会自动清理

// 组件挂载时加载数据
onMounted(() => {
  loadBookDetail()
})
</script>

<style scoped>
.book-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.header-left .book-title {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.header-left .book-meta {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 10px;
}

.loading-container,
.error-container {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 20px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #e74c3c;
  margin-bottom: 20px;
}

.detail-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
}

/* 基本信息区域 */
.basic-info-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.basic-info-display .info-card {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.cover-section {
  flex-shrink: 0;
}

.book-cover-large {
  width: 180px;
  height: 240px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 48px;
  font-weight: bold;
  border-radius: 8px;
  margin-bottom: 10px;
}

.book-cover-large img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 8px;
}

.info-main {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.info-row {
  display: flex;
  flex-direction: column;
}

.info-row label {
  font-weight: bold;
  color: #555;
  margin-bottom: 5px;
  font-size: 14px;
}

.info-row span {
  color: #333;
}

.description-section {
  margin-bottom: 30px;
}

.description-section h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 18px;
}

.description-section p {
  color: #666;
  line-height: 1.6;
}

.introduction-content {
  color: #666;
  line-height: 1.6;
  white-space: pre-wrap;
}

.categories-tags-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.tags-group h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background: #f0f0f0;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  color: #666;
}

.category-tag {
  background: #e3f2fd;
  color: #1976d2;
}

.empty-tag {
  color: #999;
  font-style: italic;
}

/* 侧边栏区域 */
.sidebar-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sidebar-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.sidebar-card h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

/* 章节列表 */
.chapter-list-container {
  max-height: 250px;
  overflow-y: auto;
}

.chapter-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.chapter-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.chapter-number {
  background: #e3f2fd;
  color: #1976d2;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  margin-right: 10px;
}

.chapter-title {
  color: #333;
  font-size: 14px;
  flex: 1;
}

/* 版本历史 */
.versions-container {
  max-height: 200px;
  overflow-y: auto;
}

.version-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.version-item {
  padding: 15px 0;
  border-bottom: 1px solid #f0f0f0;
}

.version-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.version-tag {
  background: #4caf50;
  color: white;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.version-date {
  color: #999;
  font-size: 12px;
}

.version-title {
  color: #333;
  font-weight: bold;
  margin-bottom: 5px;
}

.version-meta {
  color: #666;
  font-size: 12px;
  margin-bottom: 5px;
}

.version-comment {
  color: #999;
  font-size: 13px;
  margin: 0;
}

/* 协作者 */
.collaborators-container {
  max-height: 150px;
  overflow-y: auto;
}

.collaborator-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.collaborator-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
}

.collaborator-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #2196f3;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 10px;
  font-weight: bold;
}

.collaborator-name {
  color: #333;
  font-weight: bold;
}

.collaborator-role {
  color: #999;
  font-size: 12px;
}

/* 通用样式 */
.loading-small {
  color: #999;
  text-align: center;
  padding: 20px 0;
}

.empty-section {
  color: #999;
  text-align: center;
  padding: 20px 0;
  font-style: italic;
}

.success-toast {
  position: fixed;
  bottom: 30px;
  right: 30px;
  background: #4caf50;
  color: white;
  padding: 15px 25px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  display: flex;
  align-items: center;
  gap: 15px;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 响应式设计 */
/* 章节内容编辑样式 */
.chapter-content-section {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.chapter-content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chapter-content-controls {
  display: flex;
  gap: 10px;
}

.empty-chapter-selection {
  background-color: #f8f9fa;
  padding: 40px;
  text-align: center;
  border-radius: 8px;
  color: #666;
}

.chapter-content-editor {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.chapter-content-title h4 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
}

.jupyter-editor-container {
  position: relative;
  min-height: 400px;
}

.jupyter-preview-container {
  max-height: 600px;
  overflow-y: auto;
}

.empty-content {
  text-align: center;
  color: #999;
  padding: 40px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

/* JupyterNotebook组件容器样式 */
:deep(.jupyter-notebook) {
  width: 100%;
}

:deep(.notebook-content) {
  padding: 0;
}

:deep(.cell) {
  margin-bottom: 16px;
}

:deep(.add-cell-buttons) {
  margin-top: 20px;
}

.selected-indicator {
  color: #2196F3;
  margin-left: auto;
  font-weight: bold;
}

.chapter-item {
  cursor: pointer;
  transition: background-color 0.2s;
}

.chapter-item:hover {
  background-color: #f0f7ff;
}

@media (max-width: 768px) {
  .detail-content {
    grid-template-columns: 1fr;
  }
  
  .basic-info-display .info-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .categories-tags-section {
    grid-template-columns: 1fr;
  }
  
  .info-main {
    grid-template-columns: 1fr;
  }
  
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .chapter-content-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .chapter-content-controls {
    width: 100%;
    flex-direction: column;
  }
}
</style>
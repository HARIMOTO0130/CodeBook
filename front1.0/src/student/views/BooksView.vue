<template>
  <div class="books-container">
    <!-- 顶部栏 -->
    <div class="top-bar">
      <div class="search-filters">
          <div class="search-group">
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="搜索教材名称或标签..."
              class="search-input"
              @keyup.enter="onSearch"
            />
            <button class="search-button" @click="onSearch">
              🔍 搜索
            </button>
          </div>
          <select v-model="majorFilter" class="major-filter">
            <option value="">全部专业</option>
            <option value="经管类">经管类</option>
            <option value="文史类">文史类</option>
            <option value="艺术类">艺术类</option>
            <option value="理工科">理工科</option>
          </select>
          <button class="refresh-button" @click="onRefresh">
            🔄 刷新
          </button>
        </div>
    </div>
    
    <!-- 专业高频场景提示 -->
    <div v-if="majorFilter" class="major-scene-tip">
      <div class="tip-content">
        <span class="tip-icon">💡</span>
        <span>该专业高频场景：{{ getMajorScenes(majorFilter).join('、') }}</span>
      </div>
    </div>
    
    <!-- 热门场景卡片 -->
    <div class="popular-scenes">
      <h3>热门场景</h3>
      <div class="scenes-container">
        <div 
          v-for="scene in popularScenes" 
          :key="scene.id"
          class="scene-card"
          @click="goToTool(scene.toolId)"
        >
          <div class="scene-icon">{{ scene.icon }}</div>
          <h4 class="scene-title">{{ scene.title }}</h4>
          <p class="scene-desc">{{ scene.description }}</p>
        </div>
      </div>
    </div>
    
    <!-- 学习路线图推荐 -->
    <RoadmapRecommendation 
      v-if="majorFilter" 
      :major="getEnglishMajor(majorFilter)"
    />
    
    <!-- 智能推荐 -->
    <div class="smart-recommendations">
      <h3>你可能需要的技能</h3>
      <div class="recommendations-container">
        <div 
          v-for="rec in recommendedSkills" 
          :key="rec.id"
          class="recommendation-card"
          @click="goToTool(rec.toolId)"
        >
          <div class="rec-icon">{{ rec.icon }}</div>
          <div class="rec-info">
            <h4 class="rec-title">{{ rec.title }}</h4>
            <p class="rec-desc">{{ rec.description }}</p>
            <span class="rec-link">学习这项技能 →</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 练习题功能 -->
    <div class="practice-section">
      <h3>练习题</h3>
      <div class="practice-container">
        <div class="practice-card">
          <div class="practice-icon">🐍</div>
          <h4 class="practice-title">Python基础练习题</h4>
          <p class="practice-desc">巩固Python基础知识，包含变量、数据类型、控制流等习题</p>
          <button class="btn btn-primary" @click="startPractice('python')">开始练习</button>
        </div>
        <div class="practice-card">
          <div class="practice-icon">🟨</div>
          <h4 class="practice-title">JavaScript入门练习</h4>
          <p class="practice-desc">JavaScript核心能力练习，包括DOM操作、函数、对象等</p>
          <button class="btn btn-primary" @click="startPractice('javascript')">开始练习</button>
        </div>
        <div class="practice-card">
          <div class="practice-icon">🧮</div>
          <h4 class="practice-title">算法基础练习</h4>
          <p class="practice-desc">常见算法与数据结构的练习，提升编程思维能力</p>
          <button class="btn btn-primary" @click="startPractice('algorithm')">开始练习</button>
        </div>
      </div>
    </div>

    <div class="main-layout">
      <!-- 左侧教材列表 -->
      <div class="books-grid">
        <h3 class="books-title">我的书架</h3>
        <div 
          v-for="book in filteredBooks" 
          :key="book.id" 
          class="book-card"
        >
          <div class="book-cover">
            <div class="cover-placeholder" :style="{ backgroundColor: getCoverColor(book.id) }">
              {{ book.title.charAt(0) }}
            </div>
          </div>
          <div class="book-info">
            <h3 class="book-title">{{ book.title }}</h3>
            <p class="book-author">作者：{{ book.author }}</p>
            <div class="book-meta">
              <span class="chapter-count">{{ book.chapterCount }} 章节</span>
            </div>
            <div class="progress-section">
              <div class="progress-label">
                <span>学习进度</span>
                <span>{{ book.progress }}%</span>
              </div>
              <div class="progress-bar">
                <div class="progress-bar-fill" :style="{ width: book.progress + '%' }"></div>
              </div>
            </div>
            <div class="book-actions">
              <router-link 
                :to="`/books/${book.id}`" 
                class="btn btn-primary"
              >
                继续学习
              </router-link>
              <button 
                class="btn btn-danger delete-btn"
                @click="confirmDeleteBook(book.id, book.title)"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧边栏 -->
      <div class="sidebar">
        <!-- 上传PDF生成教材 -->
        <div class="sidebar-section">
          <h3>上传PDF生成教材（需登录）</h3>
          <div class="upload-form">
            <input class="input" type="text" v-model="uploadTitle" placeholder="教材标题" />
            <input class="input" type="text" v-model="uploadAuthor" placeholder="作者（可选）" />
            <textarea class="input" v-model="uploadDesc" placeholder="教材简介（可选）"></textarea>
            <select class="input" v-model="uploadLang">
              <option value="">自动识别语言</option>
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
            </select>
            <input class="input" type="file" accept="application/pdf" @change="onPickPdf" />
            <button class="search-btn" :disabled="uploading || !uploadFile || !uploadTitle" @click="submitPdf">
              {{ uploading ? '上传中...' : '上传并生成' }}
            </button>
            <p v-if="uploadMsg" class="upload-msg">{{ uploadMsg }}</p>
          </div>
        </div>
        <!-- 最近学习 -->
        <div class="sidebar-section">
          <h3>最近学习</h3>
          <div class="recent-books">
            <div 
              v-for="book in recentBooks" 
              :key="book.id" 
              class="recent-book-item"
              @click="goToBook(book.id)"
            >
              <div class="recent-book-info">
                <p class="recent-book-title">{{ book.title }}</p>
                <p class="recent-book-time">{{ formatTime(book.lastLearnTime) }}</p>
              </div>
              <span class="arrow">→</span>
            </div>
          </div>
        </div>

        <!-- 标签云 -->
        <div class="sidebar-section">
          <h3>标签云</h3>
          <div class="tag-cloud">
            <span 
              v-for="tag in allTags" 
              :key="tag" 
              class="tag"
              :class="{ active: selectedTag === tag }"
              @click="filterByTag(tag)"
            >
              {{ tag }}
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/api.js'
import RoadmapRecommendation from '../components/RoadmapRecommendation.vue'

export default {
  name: 'BooksView',
  components: {
    RoadmapRecommendation
  },
  setup() {
    const router = useRouter()
    
    // 搜索和过滤
    const searchQuery = ref('')
    const majorFilter = ref('')
    const selectedTag = ref('')
    
    // 搜索功能
    const onSearch = () => {
      console.log('搜索:', searchQuery.value)
      // 搜索已经通过filteredBooks计算属性实现，这里添加视觉反馈和滚动定位
      // 滚动到书籍列表区域
      const booksGrid = document.querySelector('.books-grid')
      if (booksGrid) {
        booksGrid.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }
    
    // 书籍数据
    const books = ref([])
    
    // 热门场景 - 关联到轻量化工具包
    const popularScenes = ref([
      {
        id: 1,
        title: '数据可视化',
        description: '将复杂数据转化为直观图表',
        icon: '📊',
        toolId: 6  // 关联到数据统计分析工具
      },
      {
        id: 2,
        title: '文本内容提取',
        description: '一键提取长文档关键信息',
        icon: '📝',
        toolId: 4  // 关联到文本内容提取工具
      },
      {
        id: 3,
        title: '手机照片批量处理',
        description: '一键优化、压缩和整理手机照片',
        icon: '📱',
        toolId: 3  // 关联到图片批量压缩工具
      }
    ])
    
    // 智能推荐技能 - 关联到轻量化工具包
    const recommendedSkills = ref([
      {
        id: 1,
        title: '数据统计分析',
        description: '快速分析数据，生成统计报告',
        icon: '📈',
        toolId: 6  // 关联到数据统计分析工具
      },
      {
        id: 2,
        title: '文本内容提取',
        description: '从文档中智能提取关键信息',
        icon: '📄',
        toolId: 4  // 关联到文本内容提取工具
      },
      {
        id: 3,
        title: '文件批量处理',
        description: '批量重命名和管理文件',
        icon: '📁',
        toolId: 1  // 关联到批量重命名文件工具
      }
    ])

    // 练习题相关数据
    const practiceData = ref([
      {
        id: 'python',
        title: 'Python基础练习题',
        description: '巩固Python基础知识，包含变量、数据类型、控制流等习题',
        icon: '🐍'
      },
      {
        id: 'javascript',
        title: 'JavaScript入门练习',
        description: 'JavaScript核心能力练习，包括DOM操作、函数、对象等',
        icon: '🟨'
      },
      {
        id: 'algorithm',
        title: '算法基础练习',
        description: '常见算法与数据结构的练习，提升编程思维能力',
        icon: '🧮'
      }
    ])

    // 开始练习
    const startPractice = (practiceId) => {
      console.log(`开始练习: ${practiceId}`)
      // 跳转到练习题页面
      router.push('/practice')
    }

    // 获取所有书籍
    const loadBooks = async () => {
      books.value = await api.getBooks()
    }

    const onRefresh = async () => {
      console.log('刷新书籍列表...')
      // 添加视觉反馈
      const refreshBtn = document.querySelector('.refresh-button')
      if (refreshBtn) {
        refreshBtn.classList.add('refreshing')
      }
      
      try {
        // 重置搜索查询和专业过滤
        searchQuery.value = ''
        majorFilter.value = ''
        selectedTag.value = ''
        
        // 重新加载书籍数据
        await loadBooks()
        // 添加成功提示
        console.log('刷新成功，已重置所有过滤条件')
      } catch (error) {
        console.error('刷新失败:', error)
      } finally {
        // 移除视觉反馈
        setTimeout(() => {
          if (refreshBtn) {
            refreshBtn.classList.remove('refreshing')
          }
        }, 1000)
      }
    }

    // 上传PDF
    const uploadTitle = ref('')
    const uploadAuthor = ref('')
    const uploadDesc = ref('')
    const uploadLang = ref('')
    const uploadFile = ref(null)
    const uploading = ref(false)
    const uploadMsg = ref('')

    const onPickPdf = (e) => {
      const f = e.target.files && e.target.files[0]
      uploadFile.value = f || null
    }

    const submitPdf = async () => {
      uploadMsg.value = ''
      if (!uploadTitle.value || !uploadFile.value) return
      try {
        uploading.value = true
        const result = await api.importPdf({
          title: uploadTitle.value,
          author: uploadAuthor.value,
          description: uploadDesc.value,
          language: uploadLang.value,
          file: uploadFile.value
        })
        uploadMsg.value = `成功：已创建教材(ID=${result.book_id})，章节数=${result.chapters}`
        uploadTitle.value = ''
        uploadAuthor.value = ''
        uploadDesc.value = ''
        uploadFile.value = null
        uploadLang.value = ''
        await loadBooks()
      } catch (e) {
        uploadMsg.value = '失败：' + (e && e.message ? e.message : '未知错误')
      } finally {
        uploading.value = false
      }
    }

    // 获取封面颜色
    const getCoverColor = (bookId) => {
      const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9CA24', '#6C5CE7', '#A29BFE']
      return colors[bookId % colors.length]
    }

    // 过滤后的书籍
    const filteredBooks = computed(() => {
      let result = [...books.value]

      // 搜索过滤
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(book => 
          book.title.toLowerCase().includes(query) ||
          book.tags.some(tag => tag.toLowerCase().includes(query))
        )
      }

      // 标签过滤
      if (selectedTag.value) {
        result = result.filter(book => 
          book.tags.includes(selectedTag.value)
        )
      }

      // 默认按最近学习时间排序
      result.sort((a, b) => {
        return new Date(b.lastLearnTime || 0) - new Date(a.lastLearnTime || 0)
      })
      
      // 专业过滤
      if (majorFilter.value) {
        // 根据专业过滤书籍
        // 假设每本书都有专业属性或标签来进行匹配
        result = result.filter(book => {
          // 如果书籍有major属性，直接匹配
          if (book.major) {
            return book.major === majorFilter.value;
          }
          // 否则检查标签中是否包含专业相关标签
          const majorTags = {
            '经管类': ['经济', '管理', '金融', '会计'],
            '文史类': ['文学', '历史', '哲学', '语言'],
            '艺术类': ['设计', '音乐', '美术', '创意'],
            '理工科': ['数学', '物理', '化学', '计算机']
          };
          
          const relevantTags = majorTags[majorFilter.value] || [];
          return relevantTags.some(tag => 
            book.tags.some(bookTag => bookTag.toLowerCase().includes(tag.toLowerCase()))
          );
        });
      }

      return result
    })

    // 最近学习的书籍
    const recentBooks = computed(() => {
      return [...books.value]
        .sort((a, b) => new Date(b.lastLearnTime) - new Date(a.lastLearnTime))
        .slice(0, 3)
    })

    // 所有标签
    const allTags = computed(() => {
      const tagsSet = new Set()
      books.value.forEach(book => {
        book.tags.forEach(tag => tagsSet.add(tag))
      })
      return Array.from(tagsSet)
    })

    // 跳转到书籍详情
    const goToBook = (bookId) => {
      router.push(`/books/${bookId}`)
    }

    // 过滤标签
    const filterByTag = (tag) => {
      selectedTag.value = selectedTag.value === tag ? '' : tag
    }

    // 确认删除书籍
    const confirmDeleteBook = async (bookId, bookTitle) => {
      if (confirm(`确定要删除「${bookTitle}」吗？`)) {
        try {
          console.log(`删除书籍: ${bookId}`)
          await api.deleteBook(bookId)
          console.log('书籍删除成功')
          // 刷新书籍列表
          await loadBooks()
        } catch (error) {
          console.error('删除书籍失败:', error)
          alert('删除失败: ' + (error.message || '未知错误'))
        }
      }
    }

    // 获取专业场景
    const getMajorScenes = (major) => {
      const sceneMap = {
        '经管类': ['数据分析', '报表生成', '财务计算'],
        '文史类': ['文本分析', '信息提取', '文档整理'],
        '艺术类': ['图像生成', '音频处理', '创意设计'],
        '理工科': ['算法实现', '模拟计算', '数据分析']
      }
      return sceneMap[major] || []
    }

    // 获取英文专业名
    const getEnglishMajor = (major) => {
      const majorMap = {
        '经管类': 'business',
        '文史类': 'literature',
        '艺术类': 'art',
        '理工科': 'engineering'
      }
      return majorMap[major] || major
    }

    // 格式化时间
    const formatTime = (timeStr) => {
      const date = new Date(timeStr)
      const now = new Date()
      const diff = now - date
      const days = Math.floor(diff / (1000 * 60 * 60 * 24))
      if (days === 0) {
        return '今天'
      } else if (days === 1) {
        return '昨天'
      } else if (days < 7) {
        return `${days}天前`
      } else {
        return date.toLocaleDateString()
      }
    }

    // 跳转到轻量化工具包中的对应工具
    const goToTool = (toolId) => {
      router.push({
        path: '/toolkit',
        query: { toolId }
      })
    }

    onMounted(async () => {
      await loadBooks()
      console.log('书籍数据加载完成:', books.value)
    })

    return {
      searchQuery,
      majorFilter,
      selectedTag,
      books,
      popularScenes,
      recommendedSkills,
      filteredBooks,
      recentBooks,
      allTags,
      uploadTitle, uploadAuthor, uploadDesc, uploadLang, uploadFile, uploading, uploadMsg,
      getCoverColor,
      goToBook,
      filterByTag,
      confirmDeleteBook,
      getMajorScenes,
      getEnglishMajor,
      formatTime,
      goToTool,
      onRefresh,
      onPickPdf,
      submitPdf,
      startPractice
    }
  }
}
</script>

<style scoped>
.books-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

/* 顶部栏 */
.top-bar {
  margin-bottom: 30px;
}

.search-filters {
  display: flex;
  flex-wrap: nowrap;
  gap: 15px;
  align-items: center;
  width: 100%;
  padding: 15px 0;
  box-sizing: border-box;
}

.search-group {
  display: flex;
  gap: 0;
  flex: 1;
  /* 确保搜索组占据尽可能多的空间 */
  flex-grow: 2;
}

.search-input {
  flex: 1;
  min-width: 0;
  padding: 12px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 8px 0 0 8px;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #409EFF;
}

.search-button {
  background: #409EFF;
  color: white;
  border: none;
  border-radius: 0 8px 8px 0;
  font-size: 16px;
  cursor: pointer;
  padding: 12px 24px;
  font-weight: 500;
  transition: background-color 0.3s ease;
  white-space: nowrap;
  border-left: none;
}

.search-button:hover {
  background: #66b1ff;
}

.major-filter {
  padding: 12px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-size: 16px;
  transition: border-color 0.3s ease;
  min-width: 120px;
  /* 保持专业框原有宽度 */
  flex-shrink: 0;
}

.major-filter:focus {
  outline: none;
  border-color: #409EFF;
}

.refresh-button {
  background: #67C23A;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  padding: 12px 20px;
  font-weight: 500;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
  white-space: nowrap;
}

.refresh-button:hover {
  background: #85ce61;
  transform: translateY(-1px);
}

.refresh-button:active {
  transform: translateY(0);
}

/* 刷新动画效果 */
.refresh-button.refreshing {
  animation: refreshSpin 1s linear infinite;
}

@keyframes refreshSpin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .search-filters {
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .search-input {
    width: 100%;
  }
  
  .major-filter,
  .refresh-button,
  .search-button {
    flex: 1;
    min-width: 0;
  }
}

/* 专业场景提示 */
.major-scene-tip {
  background: #e3f2fd;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.tip-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.tip-icon {
  font-size: 20px;
}

/* 热门场景 */
.popular-scenes {
  margin-bottom: 30px;
}

.popular-scenes h3 {
  margin-bottom: 15px;
  font-size: 20px;
}

.scenes-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.scene-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.scene-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.scene-icon {
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.scene-title {
  font-size: 1.2rem;
  margin-bottom: 8px;
  font-weight: 600;
}

.scene-desc {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.5;
}

/* 智能推荐样式 */
.smart-recommendations {
  margin-bottom: 30px;
}

.smart-recommendations h3 {
  margin-bottom: 15px;
  font-size: 20px;
}

.recommendations-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.recommendation-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  gap: 15px;
}

.rec-icon {
  font-size: 2rem;
  flex-shrink: 0;
}

.rec-info {
  flex: 1;
}

.rec-title {
  font-size: 1.1rem;
  margin-bottom: 5px;
  font-weight: 600;
}

.rec-desc {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 10px;
  line-height: 1.5;
}

.rec-link {
  color: #1976d2;
  text-decoration: none;
  font-size: 0.9rem;
}

.rec-link:hover {
  text-decoration: underline;
}

/* 练习题样式 */
.practice-section {
  margin: 20px 0 30px 0;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.practice-section h3 {
  margin-bottom: 15px;
  font-size: 20px;
}

.practice-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 15px;
}

.practice-card {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s;
}

.practice-card:hover {
  transform: translateY(-3px);
}

.practice-icon {
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.practice-title {
  font-size: 1.2rem;
  margin-bottom: 8px;
  font-weight: 600;
}

.practice-desc {
  color: #666;
  margin-bottom: 15px;
  font-size: 0.9rem;
  line-height: 1.5;
}

/* 主布局 */
.main-layout {
  display: grid;
  grid-template-columns: 1fr 350px;
  gap: 30px;
  margin-top: 30px;
}

/* 书架标题 */
.books-title {
  font-size: 1.8rem;
  margin-bottom: 20px;
  color: #333;
  text-align: center;
}

/* 书籍网格 */
.books-grid {
  display: flex;
  flex-direction: column;
}

.book-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  gap: 20px;
  transition: box-shadow 0.2s;
}

.book-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.book-cover {
  flex-shrink: 0;
}

.cover-placeholder {
  width: 100px;
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 2rem;
  font-weight: bold;
  border-radius: 4px;
  background: #45B7D1;
}

.book-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.book-title {
  font-size: 1.3rem;
  margin-bottom: 5px;
  color: #333;
}

.book-author {
  color: #666;
  margin-bottom: 10px;
  font-size: 0.9rem;
}

.book-meta {
  margin-bottom: 10px;
}

.chapter-count {
  background: #e3f2fd;
  color: #1976d2;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8rem;
}

.progress-section {
  margin-bottom: 15px;
}

.progress-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  font-size: 0.9rem;
  color: #666;
}

.progress-bar {
  height: 8px;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background: #4CAF50;
  transition: width 0.3s ease;
}

.book-actions {
  margin-top: auto;
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary {
  background: #1976d2;
  color: white;
}

.btn-primary:hover {
  background: #1565c0;
}

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-danger:hover {
  background: #d32f2f;
}

.delete-btn {
  flex-shrink: 0;
}

/* 侧边栏 */
.sidebar {
  position: sticky;
  top: 20px;
  align-self: start;
}

.sidebar-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.sidebar-section h3 {
  margin-bottom: 15px;
  font-size: 18px;
}

/* 上传表单 */
.upload-form {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.input {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

textarea.input {
  min-height: 80px;
  resize: vertical;
}

.upload-msg {
  margin-top: 10px;
  padding: 10px;
  border-radius: 4px;
  font-size: 14px;
}

/* 最近学习 */
.recent-books {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recent-book-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  border-radius: 4px;
  transition: background-color 0.2s;
  cursor: pointer;
}

.recent-book-item:hover {
  background: #f5f5f5;
}

.recent-book-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 3px;
}

.recent-book-time {
  font-size: 12px;
  color: #666;
}

.arrow {
  font-size: 18px;
  color: #999;
}

/* 标签云 */
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 4px 12px;
  background: #f5f5f5;
  border-radius: 16px;
  font-size: 13px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.tag:hover,
.tag.active {
  background: #e3f2fd;
  color: #1976d2;
}

/* 响应式 */
@media (max-width: 1024px) {
  .main-layout {
    grid-template-columns: 1fr;
  }
  
  .sidebar {
    position: static;
  }
}

@media (max-width: 768px) {
  .search-filters {
    flex-direction: column;
  }
  
  .filters {
    width: 100%;
    justify-content: space-between;
  }
  
  .filter-select {
    flex: 1;
    min-width: 80px;
  }
  
  .book-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .book-actions {
    justify-content: center;
  }
}
</style>
<template>
  <div class="book-outline-container">
    <!-- 顶部面包屑 -->
    <div class="breadcrumb">
        <router-link to="/student/books" class="breadcrumb-item">书架</router-link>
        <span class="breadcrumb-separator">/</span>
        <span class="breadcrumb-item current">{{ book?.title || '教材大纲' }}</span>
      </div>

    <!-- 教材信息和统计数据区域 -->
    <div v-if="book" class="book-info-section">
      <div class="book-header">
        <div class="book-basic-info">
          <h1 class="book-title">{{ book.title }}</h1>
          <p class="book-subtitle">{{ book.subtitle || '专业学习教材' }}</p>
          <div class="book-meta">
            <span class="meta-tag">
              📚 {{ book.category || '默认分类' }}
            </span>
            <span class="meta-tag">
              👨‍🏫 {{ book.author || '系统' }}
            </span>
            <span class="meta-tag">
              📅 {{ formatDate(book.publishDate) }}
            </span>
          </div>
        </div>
        <div class="book-cover">
          <div class="cover-placeholder">
            <span class="book-icon">📖</span>
            <span class="book-initials">{{ getBookInitials(book.title) }}</span>
          </div>
        </div>
      </div>
      
      <!-- 统计数据卡片 -->
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-number">{{ totalChapters }}</div>
          <div class="stat-label">章节总数</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ totalSections }}</div>
          <div class="stat-label">内容小节</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ totalDuration }}</div>
          <div class="stat-label">总时长</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ overallProgress }}%</div>
          <div class="stat-label">完成进度</div>
        </div>
      </div>
      
      <!-- 进度可视化 -->
      <div class="progress-visualization">
        <div class="progress-header">
          <h3>学习进度</h3>
          <span class="progress-text">{{ overallProgress }}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-fill" :style="{ width: overallProgress + '%' }"></div>
        </div>
        <div class="progress-details">
          <div class="progress-item">
            <span class="status-dot completed"></span>
            <span>{{ completedSections }} 个已完成</span>
          </div>
          <div class="progress-item">
            <span class="status-dot in-progress"></span>
            <span>{{ inProgressSections }} 个学习中</span>
          </div>
          <div class="progress-item">
            <span class="status-dot not-started"></span>
            <span>{{ notStartedSections }} 个未开始</span>
          </div>
        </div>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧章节树 -->
      <div class="chapter-tree">
        <h2 class="tree-title">{{ book?.title || '章节大纲' }}</h2>
        <div class="tree-content">
          <div v-if="book">
            <div 
              v-for="chapter in book.chapters" 
              :key="chapter.id"
              class="chapter-item"
            >
              <div class="chapter-header" @click="toggleChapter(chapter.id)">
                <span class="expand-icon">{{ expandedChapters.has(chapter.id) ? '▼' : '▶' }}</span>
                <span class="chapter-title">{{ chapter.title }}</span>
                <span class="chapter-status">{{ getChapterStatus(chapter) }}</span>
                <router-link 
                  :to="{ name: 'StudentPractice', query: { bookId, chapterId: chapter.id } }" 
                  class="practice-button"
                  @click.stop
                >
                  📝 练习
                </router-link>
              </div>
              
              <div 
                v-if="expandedChapters.has(chapter.id)"
                class="section-list"
              >
                <div 
                  v-for="section in chapter.sections" 
                  :key="section.id"
                  class="section-item"
                  :class="{ 
                    active: currentSectionId === section.id,
                    'status-not-started': section.status === 'notStarted',
                    'status-in-progress': section.status === 'inProgress',
                    'status-completed': section.status === 'completed'
                  }"
                  @click="selectSection(chapter.id, section.id)"
                >
                  <span class="section-icon">{{ getSectionIcon(section.type) }}</span>
                  <span class="section-title">{{ section.title }}</span>
                  <span class="section-duration">{{ section.duration }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="loading">加载中...</div>
        </div>
      </div>

      <!-- 右侧章节详情 -->
      <div class="chapter-details">
        <div v-if="selectedSection" class="section-info">
          <h2 class="section-info-title">{{ selectedSection.title }}</h2>
          
          <div class="section-meta">
            <div class="meta-item">
              <span class="meta-label">类型：</span>
              <span class="meta-value">{{ getSectionTypeText(selectedSection.type) }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">预计时长：</span>
              <span class="meta-value">{{ selectedSection.duration }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">难度：</span>
              <span class="meta-value">{{ getDifficultyStars(selectedSection.difficulty) }}</span>
            </div>
            <div class="meta-item">
              <span class="meta-label">状态：</span>
              <span class="meta-value status-badge" :class="`status-${selectedSection.status}`">
                {{ getStatusText(selectedSection.status) }}
              </span>
            </div>
          </div>

          <div class="section-description">
            <h3>简介</h3>
            <p>{{ selectedSection.description }}</p>
          </div>

          <div v-if="selectedSection.type !== 'quiz'" class="section-actions">
            <router-link 
                  :to="{ name: 'StudentLearning', params: { bookId, chapterId: selectedSection.id } }" 
              class="btn btn-primary large"
            >
              开始学习
            </router-link>
          </div>
          <div v-else class="section-actions">
            <router-link 
                  :to="{ name: 'StudentLearning', params: { bookId, chapterId: selectedSection.id } }" 
              class="btn btn-primary large"
            >
              开始练习
            </router-link>
          </div>
        </div>
        
        <div v-else-if="book" class="no-section-selected">
          <h3>选择一个章节开始学习</h3>
          <p>从左侧选择一个章节，查看详情并开始学习。</p>
        </div>
        
        <div v-else class="loading">加载中...</div>
      </div>
    </div>

    <!-- 底部浮条 -->
    <div v-if="lastLearnedSection" class="bottom-bar">
      <div class="last-progress-info">
        <span class="last-progress-icon">📚</span>
        <div class="last-progress-text">
          <p class="last-progress-section">{{ lastLearnedSection.title }}</p>
          <p class="last-progress-chapter">{{ getChapterTitle(lastLearnedSection.chapterId) }}</p>
        </div>
      </div>
      <router-link 
        :to="{ name: 'StudentLearning', params: { bookId, chapterId: lastLearnedSection.id } }" 
        class="btn btn-primary large"
      >
        继续上次进度
      </router-link>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeMount } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api/api.js'

export default {
  name: 'BookOutlineView',
  setup() {
    const route = useRoute()
    const bookId = computed(() => Number(route.params.bookId))
    
    const book = ref(null)
    const expandedChapters = ref(new Set())
    const currentSectionId = ref(null)
    const selectedSection = ref(null)
    const lastLearnedSection = ref(null)
    
    // 计算统计数据
    const totalChapters = computed(() => {
      return book.value?.chapters?.length || 0
    })
    
    const totalSections = computed(() => {
      if (!book.value) return 0
      return book.value.chapters.reduce((total, chapter) => {
        return total + chapter.sections.length
      }, 0)
    })
    
    const totalDuration = computed(() => {
      if (!book.value) return '0分钟'
      
      let totalMinutes = 0
      book.value.chapters.forEach(chapter => {
        chapter.sections.forEach(section => {
          // 假设duration格式为'xx分钟'
          const minutes = parseInt(section.duration)
          if (!isNaN(minutes)) {
            totalMinutes += minutes
          }
        })
      })
      
      if (totalMinutes < 60) {
        return `${totalMinutes}分钟`
      } else {
        const hours = Math.floor(totalMinutes / 60)
        const minutes = totalMinutes % 60
        return minutes > 0 ? `${hours}小时${minutes}分钟` : `${hours}小时`
      }
    })
    
    const completedSections = computed(() => {
      if (!book.value) return 0
      let count = 0
      book.value.chapters.forEach(chapter => {
        count += chapter.sections.filter(s => s.status === 'completed').length
      })
      return count
    })
    
    const inProgressSections = computed(() => {
      if (!book.value) return 0
      let count = 0
      book.value.chapters.forEach(chapter => {
        count += chapter.sections.filter(s => s.status === 'inProgress').length
      })
      return count
    })
    
    const notStartedSections = computed(() => {
      if (!book.value) return 0
      let count = 0
      book.value.chapters.forEach(chapter => {
        count += chapter.sections.filter(s => s.status === 'notStarted').length
      })
      return count
    })
    
    const overallProgress = computed(() => {
      const total = totalSections.value
      if (total === 0) return 0
      return Math.round((completedSections.value / total) * 100)
    })
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '未知'
      const date = new Date(dateString)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }
    
    // 获取书名首字母
    const getBookInitials = (title) => {
      if (!title) return '📚'
      return title.charAt(0).toUpperCase()
    }

    // 获取模拟书籍数据
    const getMockBookData = () => {
      return {
        id: bookId.value,
        title: 'JavaScript高级编程',
        author: '张三',
        cover: '',
        description: '本书详细介绍JavaScript的高级编程技巧和最佳实践',
        tags: ['JavaScript', '前端开发', '编程'],
        chapterCount: 5,
        publishDate: '2023-01-15',
        category: '编程学习',
        chapters: [
          {
            id: 1,
            title: '第1章 JavaScript基础回顾',
            sections: [{
              id: 1,
              title: 'JavaScript基础回顾',
              type: 'reading',
              duration: '30分钟',
              description: '回顾JavaScript的基本语法和概念',
              status: 'notStarted',
              difficulty: 2,
              lastLearnTime: null
            }]
          },
          {
            id: 2,
            title: '第2章 函数与闭包',
            sections: [{
              id: 2,
              title: '函数与闭包',
              type: 'reading',
              duration: '45分钟',
              description: '深入理解JavaScript函数和闭包概念',
              status: 'inProgress',
              difficulty: 3,
              lastLearnTime: '2024-01-10T10:30:00'
            }]
          },
          {
            id: 3,
            title: '第3章 异步编程',
            sections: [{
              id: 3,
              title: '异步编程',
              type: 'video',
              duration: '60分钟',
              description: '学习Promise、async/await等异步编程方式',
              status: 'notStarted',
              difficulty: 4,
              lastLearnTime: null
            }]
          },
          {
            id: 4,
            title: '第4章 ES6+新特性',
            sections: [{
              id: 4,
              title: 'ES6+新特性',
              type: 'reading',
              duration: '50分钟',
              description: '掌握ES6及以上版本的新特性',
              status: 'completed',
              difficulty: 3,
              lastLearnTime: '2024-01-08T15:20:00'
            }]
          },
          {
            id: 5,
            title: '第5章 实战练习',
            sections: [{
              id: 5,
              title: '实战练习',
              type: 'quiz',
              duration: '30分钟',
              description: '通过实际练习巩固所学知识',
              status: 'notStarted',
              difficulty: 5,
              lastLearnTime: null
            }]
          }
        ]
      }
    }

    // 获取书籍详情
    const loadBookDetail = async () => {
      try {
        book.value = await api.getBookDetail(bookId.value)
        // 默认展开第一个章节
        if (book.value && book.value.chapters.length > 0) {
          expandedChapters.value.add(book.value.chapters[0].id)
        }
        // 查找最后学习的章节
        findLastLearnedSection()
      } catch (error) {
        console.error('加载书籍详情失败:', error)
        // 使用模拟数据
        book.value = getMockBookData()
        console.log('使用模拟数据显示书籍信息')
        // 默认展开第一个章节
        if (book.value && book.value.chapters.length > 0) {
          expandedChapters.value.add(book.value.chapters[0].id)
        }
        // 查找最后学习的章节
        findLastLearnedSection()
      }
    }

    // 查找最后学习的章节
    const findLastLearnedSection = () => {
      if (!book.value) return
      
      let lastSection = null
      let lastLearnTime = 0
      
      book.value.chapters.forEach(chapter => {
        chapter.sections.forEach(section => {
          if (section.lastLearnTime && new Date(section.lastLearnTime) > lastLearnTime) {
            lastLearnTime = new Date(section.lastLearnTime)
            lastSection = { ...section, chapterId: chapter.id }
          }
        })
      })
      
      lastLearnedSection.value = lastSection
    }

    // 切换章节展开/折叠
    const toggleChapter = (chapterId) => {
      if (expandedChapters.value.has(chapterId)) {
        expandedChapters.value.delete(chapterId)
      } else {
        expandedChapters.value.add(chapterId)
      }
    }

    // 选择章节
    const selectSection = (chapterId, sectionId) => {
      currentSectionId.value = sectionId
      
      // 查找选中的章节信息
      book.value.chapters.forEach(chapter => {
        if (chapter.id === chapterId) {
          const section = chapter.sections.find(s => s.id === sectionId)
          if (section) {
            selectedSection.value = { ...section, chapterId }
          }
        }
      })
    }

    // 获取章节状态
    const getChapterStatus = (chapter) => {
      const total = chapter.sections.length
      if (total === 0) return '0%'
      
      const completed = chapter.sections.filter(s => s.status === 'completed').length
      return `${Math.round((completed / total) * 100)}%`
    }

    // 获取章节图标
    const getSectionIcon = (type) => {
      switch (type) {
        case 'reading': return '✏️'
        case 'video': return '🎥'
        case 'quiz': return '💡'
        default: return '📄'
      }
    }

    // 获取章节类型文本
    const getSectionTypeText = (type) => {
      switch (type) {
        case 'reading': return '阅读'
        case 'video': return '视频'
        case 'quiz': return '练习'
        default: return '未知'
      }
    }

    // 获取难度星星
    const getDifficultyStars = (difficulty) => {
      return '⭐'.repeat(difficulty)
    }

    // 获取状态文本
    const getStatusText = (status) => {
      switch (status) {
        case 'notStarted': return '未开始'
        case 'inProgress': return '学习中'
        case 'completed': return '已完成'
        default: return '未知'
      }
    }

    // 获取章节标题
    const getChapterTitle = (chapterId) => {
      const chapter = book.value?.chapters.find(c => c.id === chapterId)
      return chapter?.title || ''
    }

    onBeforeMount(() => {
      loadBookDetail()
    })

    return {
      bookId,
      book,
      expandedChapters,
      currentSectionId,
      selectedSection,
      lastLearnedSection,
      totalChapters,
      totalSections,
      totalDuration,
      overallProgress,
      completedSections,
      inProgressSections,
      notStartedSections,
      toggleChapter,
      selectSection,
      getChapterStatus,
      getSectionIcon,
      getSectionTypeText,
      getDifficultyStars,
      getStatusText,
      getChapterTitle,
      formatDate,
      getBookInitials
    }
  }
}
</script>

<style scoped>
.book-outline-container {
  padding: 20px 0;
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 120px);
}

/* 教材信息区域样式 */
.book-info-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 30px;
  margin-bottom: 30px;
}

.book-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.book-basic-info {
  flex: 1;
}

.book-title {
  font-size: 28px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
}

.book-subtitle {
  font-size: 16px;
  color: #666;
  margin: 0 0 16px 0;
}

.book-meta {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.meta-tag {
  font-size: 14px;
  color: #666;
  background-color: #f5f5f5;
  padding: 6px 12px;
  border-radius: 16px;
}

.book-cover {
  margin-left: 30px;
}

.cover-placeholder {
  width: 120px;
  height: 160px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.book-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.book-initials {
  font-size: 24px;
  font-weight: 600;
}

/* 统计卡片样式 */
.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.stat-number {
  font-size: 32px;
  font-weight: 600;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

/* 进度可视化样式 */
.progress-visualization {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.progress-header h3 {
  font-size: 18px;
  color: #333;
  margin: 0;
}

.progress-text {
  font-size: 20px;
  font-weight: 600;
  color: #409EFF;
}

.progress-bar {
  width: 100%;
  height: 12px;
  background-color: #e9ecef;
  border-radius: 6px;
  overflow: hidden;
  margin-bottom: 15px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #409EFF 0%, #67C23A 100%);
  border-radius: 6px;
  transition: width 0.5s ease;
}

.progress-details {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #666;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.status-dot.completed {
  background-color: #67C23A;
}

.status-dot.in-progress {
  background-color: #409EFF;
}

.status-dot.not-started {
  background-color: #909399;
}

@media (max-width: 768px) {
  .book-header {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .book-cover {
    margin-left: 0;
    margin-bottom: 20px;
    order: -1;
  }
  
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .progress-details {
    gap: 15px;
  }
}

.breadcrumb {
  margin-bottom: 20px;
  font-size: 14px;
  color: #666;
}

.breadcrumb-item {
  color: #409EFF;
  text-decoration: none;
}

.breadcrumb-item:hover {
  text-decoration: underline;
}

.breadcrumb-item.current {
  color: #333;
  font-weight: 500;
}

.breadcrumb-separator {
  margin: 0 10px;
  color: #999;
}

.main-content {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 30px;
  flex: 1;
}

.chapter-tree {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden;
}

.tree-title {
  padding: 20px;
  font-size: 18px;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.tree-content {
  max-height: calc(100vh - 250px);
  overflow-y: auto;
}

.chapter-item {
  border-bottom: 1px solid #f0f0f0;
}

.chapter-header {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.chapter-header:hover {
  background-color: #f5f5f5;
}

.expand-icon {
  margin-right: 10px;
  font-size: 10px;
  width: 12px;
  text-align: center;
}

.chapter-title {
  flex: 1;
  font-weight: 500;
}

.chapter-status {
  font-size: 12px;
  color: #999;
}

.practice-button {
  padding: 6px 12px;
  background-color: #409EFF;
  color: white;
  border-radius: 4px;
  font-size: 12px;
  text-decoration: none;
  transition: all 0.3s;
  margin-left: 10px;
}

.practice-button:hover {
  background-color: #66b1ff;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.3);
}

.section-list {
  background-color: #fafafa;
}

.section-item {
  display: flex;
  align-items: center;
  padding: 12px 40px 12px 35px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
  border-left: 3px solid transparent;
}

.section-item:hover {
  background-color: #f0f7ff;
}

.section-item.active {
  background-color: #ecf5ff;
  border-left-color: #409EFF;
}

.section-icon {
  margin-right: 10px;
}

.section-title {
  flex: 1;
}

.section-duration {
  font-size: 12px;
  color: #999;
}

.status-not-started {
  opacity: 0.7;
}

.status-completed .section-title {
  text-decoration: line-through;
}

.chapter-details {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 30px;
}

.section-info-title {
  font-size: 24px;
  margin-bottom: 20px;
}

.section-meta {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.meta-item {
  display: flex;
  align-items: center;
}

.meta-label {
  font-size: 14px;
  color: #999;
  margin-right: 8px;
}

.meta-value {
  font-size: 14px;
  color: #333;
}

.status-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
}

.status-notStarted {
  background-color: #f5f5f5;
  color: #999;
}

.status-inProgress {
  background-color: #ecf5ff;
  color: #409EFF;
}

.status-completed {
  background-color: #f0f9eb;
  color: #67C23A;
}

.section-description h3 {
  font-size: 16px;
  margin-bottom: 10px;
  color: #333;
}

.section-description p {
  font-size: 14px;
  line-height: 1.6;
  color: #666;
  margin-bottom: 30px;
}

.section-actions {
  display: flex;
  justify-content: center;
}

.btn.large {
  padding: 12px 30px;
  font-size: 16px;
}

.no-section-selected,
.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #999;
}

.no-section-selected h3 {
  margin-bottom: 10px;
  color: #666;
}

.bottom-bar {
  background: white;
  border-radius: 8px;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
  padding: 15px 30px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 20px;
}

.last-progress-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.last-progress-icon {
  font-size: 24px;
}

.last-progress-section {
  font-size: 16px;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.last-progress-chapter {
  font-size: 14px;
  color: #999;
}

@media (max-width: 768px) {
  .main-content {
    grid-template-columns: 1fr;
  }
  
  .bottom-bar {
    flex-direction: column;
    gap: 15px;
  }
  
  .last-progress-info {
    align-self: flex-start;
  }
}
</style>
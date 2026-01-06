<template>
  <div class="practice-view">
    <!-- 顶部面包屑 -->
    <div class="breadcrumb">
      <router-link to="/student/books" class="breadcrumb-item">首页</router-link>
      <span class="breadcrumb-separator">/</span>
      <span class="breadcrumb-item current">练习题</span>
    </div>

    <div class="page-header">
      <h1>练习题</h1>
      <p class="page-description">通过实践巩固所学知识，提升编程能力</p>
    </div>

    <!-- 书籍标签 -->
    <div class="book-tabs" v-if="books.length > 0">
      <button
        v-for="book in books"
        :key="book.book_id"
        class="book-tab"
        :class="{ active: selectedBookId === book.book_id }"
        @click="selectBook(book.book_id)"
      >
        {{ book.book_title }}
      </button>
    </div>

    <!-- 练习题列表 - 按章节分组 -->
    <div class="practice-list">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在加载练习题...</p>
      </div>
      
      <div v-else-if="currentBookChapters.length === 0" class="empty-state">
        <div class="empty-icon">📚</div>
        <p>该书籍暂无练习题</p>
      </div>
      
      <div v-else class="chapters-container">
        <div 
          v-for="chapter in currentBookChapters" 
          :key="chapter.chapter_id" 
          class="chapter-section"
        >
          <div class="chapter-section-header">
            <h2 class="chapter-section-title">{{ chapter.chapter_title }}</h2>
            <span class="chapter-section-count">{{ chapter.practices.length }} 道题</span>
          </div>
          
          <div v-if="chapter.practices.length === 0" class="chapter-empty">
            <p>该章节没有练习题</p>
          </div>

          <div v-else class="practice-grid">
            <div 
              v-for="practice in chapter.practices" 
              :key="practice.id" 
              class="practice-card"
              @click="startPractice(practice)"
            >
              <div class="practice-header">
                <div class="practice-icon">{{ helpers.getLanguageIcon(practice.language) }}</div>
                <div class="practice-info">
                  <h3 class="practice-title">{{ practice.title.replace(/- 练习题$/, '') }}</h3>
                  <p class="practice-meta">
                    <span class="practice-type">{{ helpers.getQuestionTypesText(practice) }}</span>
                    <span class="practice-language">{{ practice.language?.toUpperCase() }}</span>
                </p>
                </div>
              </div>
              
              <div class="practice-content">
                <p class="practice-description">{{ helpers.truncateText(practice.description, 120) }}</p>
              </div>
              
              <div class="practice-footer">
                <div class="practice-stats">
                  <span class="question-count-badge">{{ helpers.getQuestionCount(practice) }} 道题</span>
                    <span class="difficulty-badge" :class="helpers.getDifficultyClass(practice.difficulty)">
                        {{ helpers.getDifficultyText(practice.difficulty) }}
                    </span>
                </div>
                <button class="start-button">开始练习</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 练习统计 -->
    <div class="stats-section">
      <div class="stats-header">
        <h2>练习统计</h2>
      </div>
      <div class="stats-cards">
        <div class="stat-card">
          <div class="stat-icon">📊</div>
          <div class="stat-value">{{ totalPractices }}</div>
          <div class="stat-label">总练习次数</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">✅</div>
          <div class="stat-value">{{ completedPractices }}</div>
          <div class="stat-label">已完成练习</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🎯</div>
          <div class="stat-value">{{ averageScore }}%</div>
          <div class="stat-label">平均得分</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon">🔥</div>
          <div class="stat-value">{{ streakDays }}</div>
          <div class="stat-label">连续练习天数</div>
        </div>
      </div>
    </div>

    <!-- 练习题模态框 -->
    <PracticeModal
        v-model:visible="showPracticeModal"
        :questions="currentQuestions"
        :practice-name="currentPracticeName"
        :practice-id="currentPracticeId"
        @close="closePractice"
        @complete="handlePracticeComplete"
      />
  </div>
</template>

<script>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '../api/api.js'
import PracticeModal from '../components/PracticeModal.vue'

export default {
  name: 'PracticeView',
  components: {
    PracticeModal
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    
    // 状态管理
    const loading = ref(true)
    const books = ref([]) // 存储所有书籍及其练习题
    const selectedBookId = ref(null) // 当前选中的书籍ID
    const selectedChapterId = ref(null) // 当前选中的章节ID
    const practiceRecords = ref([])
    
    // 获取URL参数
    const urlBookId = computed(() => Number(route.query.bookId))
    const urlChapterId = computed(() => Number(route.query.chapterId))
    const urlCategory = computed(() => route.query.category)
    

    // 模态框状态
    const showPracticeModal = ref(false)
    const currentQuestions = ref([])
    const currentPracticeName = ref('')
    const currentPracticeId = ref(null)
    
    // 计算属性
    const currentBookPractices = computed(() => {
      if (!selectedBookId.value) return []
      const book = books.value.find(b => b.book_id === selectedBookId.value)
      return book ? book.practices : []
    })
    
    const currentBookChapters = computed(() => {
      if (!selectedBookId.value) return []
      const book = books.value.find(b => b.book_id === selectedBookId.value)
      if (!book) return []
      
      // 从practices中提取章节信息，使用标题作为键确保每组只保留一个
      const chaptersMap = new Map()
      
      book.practices.forEach(practice => {
        // 标准化章节标题：移除各种可能的后缀
        let chapterTitle = practice.chapter_title || `章节 ${practice.chapter_id}`
        // 移除可能的后缀，确保标题完全一致
        chapterTitle = chapterTitle
          .replace(/-练习题-练习题集$/, '')
          .replace(/- 练习题$/, '')
          .trim() // 去除前后空格
        
        // 直接使用标准化后的标题作为键，确保每组只保留一个
        if (!chaptersMap.has(chapterTitle)) {
          const chapterId = practice.chapter_id
          chaptersMap.set(chapterTitle, {
            chapter_id: chapterId,
            chapter_title: chapterTitle,
            practices: [practice] // 只添加当前练习作为第一个
          })
        }
      })
      
      // 转换为数组并按章节ID排序
      return Array.from(chaptersMap.values()).sort((a, b) => a.chapter_id - b.chapter_id)
    })
    
    const currentChapterPractices = computed(() => {
      if (!selectedChapterId.value) return []
      const chapter = currentBookChapters.value.find(c => c.chapter_id === selectedChapterId.value)
      return chapter && chapter.practices ? chapter.practices : []
    })
    
    const totalPractices = computed(() => practiceRecords.value.length)
    const completedPractices = computed(() => 
      practiceRecords.value.filter(record => record.completed).length
    )
    const averageScore = computed(() => {
      if (practiceRecords.value.length === 0) return 0
      const sum = practiceRecords.value.reduce((acc, record) => acc + record.score, 0)
      return Math.round(sum / practiceRecords.value.length)
    })
    const streakDays = computed(() => {
      return Math.floor(Math.random() * 7) + 1
    })

    // 监听URL参数变化
    watch(urlCategory, (newCategory, oldCategory) => {
      if (newCategory !== oldCategory) {
        console.log(`练习类别变化: ${oldCategory} -> ${newCategory}`)
        // 重置选中的书籍
        selectedBookId.value = null
        // 重新获取过滤后的练习数据
        fetchPracticeChapters()
      }
    })

    const selectBook = (bookId) => {
      selectedBookId.value = bookId
      selectedChapterId.value = null
    }
    
    // 根据category过滤练习
    const filterPracticesByCategory = (booksData, category) => {
      if (!category) return booksData
      
      console.log('过滤前的书籍数据:', booksData)
      console.log('过滤类别:', category)
      
      // 复制原始数据以避免修改
      const filteredBooks = JSON.parse(JSON.stringify(booksData))
      
      // 如果category是数字，设置为默认选中的书籍，但不过滤书籍列表
      if (!isNaN(category)) {
        const bookId = Number(category)
        // 检查该书籍是否存在，如果存在则设置为默认选中
        const bookExists = filteredBooks.some(book => book.book_id === bookId)
        if (bookExists && !selectedBookId.value) {
          selectedBookId.value = bookId
        }
        console.log(`设置默认选中的书籍ID:`, selectedBookId.value)
        return filteredBooks
      }
      
      // 否则按语言或其他条件过滤练习
      return filteredBooks.map(book => {
        // 过滤每本书中的练习
        const filteredPractices = book.practices.filter(practice => {
          if (category === 'python') {
            const result = practice.language === 'python'
            console.log(`Python过滤 - 练习ID: ${practice.id}, 语言: ${practice.language}, 结果: ${result}`)
            return result
          } else if (category === 'javascript') {
            const result = practice.language === 'javascript'
            console.log(`JavaScript过滤 - 练习ID: ${practice.id}, 语言: ${practice.language}, 结果: ${result}`)
            return result
          } else if (category === 'algorithm') {
            // 通过标题或内容判断是否为算法相关练习
            const title = (practice.title || '').toLowerCase()
            const description = (practice.description || '').toLowerCase()
            const algorithmKeywords = ['算法', '数据结构', '排序', '搜索', '递归', '迭代']
            const result = algorithmKeywords.some(keyword => title.includes(keyword) || description.includes(keyword))
            console.log(`算法过滤 - 练习ID: ${practice.id}, 标题: ${title}, 描述: ${description}, 结果: ${result}`)
            return result
          }
          return true
        })
        
        const bookResult = {
          ...book,
          practices: filteredPractices
        }
        console.log(`书籍ID: ${bookResult.book_id}, 过滤后练习数量: ${bookResult.practices.length}`)
        return bookResult
      }).filter(book => book.practices.length > 0) // 过滤掉没有练习的书籍
    }
    
    // 获取练习题 - 直接从数据库获取
    const fetchPracticeChapters = async () => {
      loading.value = true
      try {
        // 使用新的API端点获取按书籍分组的练习题
        const booksData = await api.getPractices()
        console.log('原始书籍数据:', booksData)
        
        // 检查是否有重复的练习题标题
        booksData.forEach(book => {
          console.log(`\n书籍: ${book.book_title}`)
          const practiceTitles = book.practices.map(p => p.title)
          console.log('练习标题:', practiceTitles)
          
          // 检查重复标题
          const uniqueTitles = [...new Set(practiceTitles)]
          if (uniqueTitles.length !== practiceTitles.length) {
            console.log('发现重复标题:', practiceTitles)
          }
        })
        
        // 根据URL参数过滤练习
        const filteredBooksData = filterPracticesByCategory(booksData, urlCategory.value)
        console.log('过滤后的书籍数据:', filteredBooksData)
        console.log('当前URL类别:', urlCategory.value)
        
        if (Array.isArray(filteredBooksData) && filteredBooksData.length > 0) {
          books.value = filteredBooksData
          // 默认选择第一本书
          if (!selectedBookId.value) {
            selectedBookId.value = filteredBooksData[0].book_id
          }
        } else {
          books.value = []
          selectedBookId.value = null
        }
      } catch (error) {
        console.error('获取练习题失败:', error)
        // 不再使用模拟数据，直接显示空状态
        books.value = []
        selectedBookId.value = null
      } finally {
        loading.value = false
      }
    }
    
    // 获取练习记录
    const fetchPracticeRecords = async () => {
      try {
        const records = await api.getPracticeRecords()
        practiceRecords.value = Array.isArray(records) ? records : []
      } catch (error) {
        console.error('获取练习记录失败:', error)
        practiceRecords.value = []
      }
    }
    
    // 开始练习
    const startPractice = (practice) => {
      console.log('开始练习:', practice)
      console.log('练习ID:', practice.id)
      console.log('练习对象结构:', Object.keys(practice))
      currentPracticeId.value = practice.id
      currentPracticeName.value = practice.title
      
      // 构建问题列表
      if (practice.questions && Array.isArray(practice.questions)) {
        // 如果已经是问题数组格式，对后端数据做一层标准化，适配前端展示/判题逻辑
        currentQuestions.value = practice.questions.map((rawQ, index) => {
          const q = { ...rawQ }
          const id = q.id || index + 1

          // 统一题型命名：后端使用 snake_case，如 true_false / code_completion
          let backendType = q.type || 'choice'
          if (backendType === 'true_false') {
            backendType = 'judgment'
          }
          const displayType = backendType.replace(/_([a-z])/g, (m, p1) => p1.toUpperCase())

          // 统一选项与正确答案
          let options = Array.isArray(q.options) ? q.options : []
          let correctAnswer = q.correctAnswer

          // 选择题：从 is_correct 推导正确选项索引
          if (backendType === 'choice' && options.length > 0 && correctAnswer === undefined) {
            const correctIndexes = options
              .map((opt, optIdx) => (opt.is_correct ? optIdx : null))
              .filter(v => v !== null)
            if (correctIndexes.length === 1) {
              correctAnswer = correctIndexes[0]
            } else if (correctIndexes.length > 1) {
              correctAnswer = correctIndexes
            }
          }

          // 判断题：如果后端只给了 boolean 正误，则构造“正确/错误”两个选项
          if (backendType === 'judgment') {
            const boolAnswer = q.correct_answer ?? q.correctAnswer ?? true
            options = [
              { content: '正确' },
              { content: '错误' }
            ]
            correctAnswer = boolAnswer ? 0 : 1
          }

          // 填空题：后端使用 correct_answer，前端使用 correctAnswer
          let blanks = Array.isArray(q.blanks) ? q.blanks.map(b => ({
            ...b,
            correctAnswer: b.correctAnswer ?? b.correct_answer
          })) : []

          // 测试用例：兼容 testCases / test_cases，字段名 input / input_data, expected_output / expectedOutput
          const rawTestCases = q.testCases || q.test_cases || []
          const testCases = Array.isArray(rawTestCases)
            ? rawTestCases.map(tc => ({
                id: tc.id,
                input: tc.input ?? tc.input_data ?? {},
                expectedOutput: tc.expectedOutput ?? tc.expected_output
              }))
            : []

          return {
            id,
            type: displayType,
            title: q.title,
            description: q.description,
            question: q.question,
            code_template: q.code_template,
            language: q.language || practice.language,
            difficulty: q.difficulty || practice.difficulty,
            options,
            blanks,
            testCases,
            correctAnswer,
            order: q.order || index + 1
          }
        })
      } else {
        // 兼容旧格式 - 直接构建编程题
        currentQuestions.value = []
        
        if (practice.practice) {
          currentQuestions.value.push({
            id: 1,
            type: 'programming',
            title: '编程练习',
            stem: practice.question,
            code_template: practice.code_template || '',
            language: 'python', // 应该从chapter获取
            testCases: practice.test_cases || []
          })
        }
      }
      console.log('练习题问题:', currentQuestions.value)
      showPracticeModal.value = true
      console.log('模态框显示状态:', showPracticeModal.value)
    }
    
    // 关闭练习
    const closePractice = () => {
      showPracticeModal.value = false
      currentQuestions.value = []
    }
    
    // 处理练习完成
    const handlePracticeComplete = (result) => {
      closePractice()
      console.log('练习完成:', result)
      
      // 收集所有问题的答案
      const questionAnswers = currentQuestions.value.map((q, index) => {
        const answer = {
          question_id: q.id || q.order || index + 1,
          type: q.type
        }
        
        // 根据题型收集答案
        if (q.type === 'choice') {
          answer.answer = q.selectedOption !== undefined ? q.selectedOption : null
        } else if (q.type === 'fill') {
          answer.blank_answers = {}
          if (q.blanks && Array.isArray(q.blanks)) {
            q.blanks.forEach((blank, idx) => {
              answer.blank_answers[idx] = q.userAnswers ? q.userAnswers[idx] : ''
            })
          }
        } else if (q.type === 'code_completion' || q.type === 'programming') {
          answer.code = q.userCode || ''
        }
        
        return answer
      })
      
      // 提交多问题答案
      submitMultiQuestionPractice(questionAnswers, result)
    }

    // 提交练习结果
    // 提交多问题练习结果
    const submitMultiQuestionPractice = async (questionAnswers, result) => {
      try {
        // 获取当前练习所属的章节ID
        const currentPractice = currentBookPractices.value.find(p => p.id === currentPracticeId.value)
        const chapterId = currentPractice ? currentPractice.chapter_id : null
        
        if (!chapterId) {
          console.error('无法找到章节ID')
          return
        }
        
        // 调用章节练习提交API
        const response = await api.submitChapterPractice(chapterId, {
          practice_id: currentPracticeId.value,
          question_answers: questionAnswers
        })
        
        console.log('多问题提交成功:', response)
        
        // 显示提交结果
        if (response.all_correct) {
          console.log('恭喜！所有题目都回答正确！')
        } else {
          console.log(`共 ${response.total_questions} 道题，答对 ${response.correct_count} 道题`)
        }
        
        // 重新获取练习记录
        fetchPracticeRecords()
      } catch (error) {
        console.error('提交多问题练习结果失败:', error)
      }
    }
    
    // 辅助函数对象
    const helpers = {
      // 获取语言图标
      getLanguageIcon: (language) => {
        const icons = {
          python: '🐍',
          javascript: '🟨',
          java: '☕',
          c: '⚙️',
          cpp: '➕'
        }
        return icons[language?.toLowerCase()] || '📝'
      },
      
      // 获取难度类名
      getDifficultyClass: (difficulty) => {
        const classMap = {
          1: 'easy',
          2: 'medium',
          3: 'hard'
        }
        return classMap[difficulty] || 'medium'
      },
      
      // 获取难度文本
      getDifficultyText: (difficulty) => {
        const textMap = {
          1: '简单',
          2: '中等',
          3: '困难'
        }
        return textMap[difficulty] || '中等'
      },
      
      // 获取单个题目类型文本
      getQuestionTypeText: (questionType) => {
        const typeMap = {
          'choice': '选择题',
          'true_false': '判断题',
          'fill': '填空题',
          'code_completion': '代码补全',
          'programming': '编程题'
        }
        return typeMap[questionType] || '未知类型'
      },
      
      // 获取题目数量
      getQuestionCount: (practice) => {
        if (practice.questions && Array.isArray(practice.questions)) {
          return practice.questions.length
        }
        return practice.practice?.test_cases?.length || 1
      },
      
      // 获取练习包含的所有题目类型文本
      getQuestionTypesText: (practice) => {
        if (!practice.questions || !Array.isArray(practice.questions)) {
          return '未知类型'
        }
        
        const typeMap = {
          'choice': '选择题',
          'true_false': '判断题',
          'fill': '填空题',
          'code_completion': '代码补全',
          'programming': '编程题'
        }
        
        const types = new Set(practice.questions.map(q => typeMap[q.type] || '未知'))
        return Array.from(types).join('、')
      },
      
      // 截断文本
      truncateText: (text, maxLength) => {
        if (!text) return ''
        return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
      }
    }

    // 生命周期钩子
    onMounted(async () => {
      await Promise.all([
        fetchPracticeChapters(),
        fetchPracticeRecords()
      ])
    })

    return {
      // 状态
      loading,
      books,
      selectedBookId,
      selectedChapterId,
      practiceRecords,
      showPracticeModal,
      currentQuestions,
      currentPracticeName,
      currentPracticeId,
      
      // 计算属性
      currentBookChapters,
      currentBookPractices,
      currentChapterPractices,
      totalPractices,
      completedPractices,
      averageScore,
      streakDays,
      
      // 方法
      selectBook,
      startPractice,
      closePractice,
      handlePracticeComplete,
      helpers
    }
  }
}
</script>

<style scoped>
/* 全局样式 */
.practice-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Microsoft YaHei', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
  min-height: 100vh;
}

/* 面包屑导航 */
.breadcrumb {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  font-size: 14px;
  color: #666;
}

.breadcrumb-item {
  color: #666;
  text-decoration: none;
  transition: color 0.3s ease;
}

.breadcrumb-item:hover {
  color: #4CAF50;
}

.breadcrumb-item.current {
  color: #333;
  font-weight: bold;
}

.breadcrumb-separator {
  margin: 0 8px;
}

/* 页面头部 */
.page-header {
  margin-bottom: 30px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e9ecef;
}

.page-header h1 {
  font-size: 28px;
  margin-bottom: 10px;
  color: #333;
  font-weight: 700;
}

.page-description {
  font-size: 16px;
  color: #666;
  margin: 0;
  line-height: 1.5;
}

/* 书籍标签 */
.book-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  overflow-x: auto;
  padding-bottom: 10px;
  scrollbar-width: thin;
  scrollbar-color: #ddd transparent;
}

.book-tabs::-webkit-scrollbar {
  height: 4px;
}

.book-tabs::-webkit-scrollbar-thumb {
  background-color: #ddd;
  border-radius: 2px;
}

.book-tab {
  padding: 10px 20px;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  background-color: #fff;
  cursor: pointer;
  font-size: 16px;
  white-space: nowrap;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  opacity: 0.8;
  transform: translateY(0);
}

.book-tab:hover {
  border-color: #4CAF50;
  color: #4CAF50;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.2);
  opacity: 1;
  transform: translateY(-2px);
}

.book-tab.active {
  background-color: #4CAF50;
  color: white;
  border-color: #4CAF50;
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
  opacity: 1;
  transform: translateY(-2px);
}

/* 练习卡片 */
.practice-card {
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  opacity: 1;
  transform: translateY(0);
}

.practice-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  transform: translateY(-4px);
  border-color: #4CAF50;
}

/* 章节部分 */
.chapter-section {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 25px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  opacity: 1;
  transform: translateY(0);
}

.chapter-section:hover {
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

/* 统计卡片 */
.stat-card {
  text-align: center;
  padding: 25px;
  background-color: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 1px solid transparent;
  opacity: 1;
  transform: translateY(0);
}

.stat-card:hover {
  background-color: #e9ecef;
  border-color: #dee2e6;
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

/* 进入动画 */
.chapters-container > .chapter-section {
  animation: fadeInUp 0.6s ease-out forwards;
}

.chapters-container > .chapter-section:nth-child(1) { animation-delay: 0.1s; }
.chapters-container > .chapter-section:nth-child(2) { animation-delay: 0.2s; }
.chapters-container > .chapter-section:nth-child(3) { animation-delay: 0.3s; }
.chapters-container > .chapter-section:nth-child(4) { animation-delay: 0.4s; }
.chapters-container > .chapter-section:nth-child(5) { animation-delay: 0.5s; }
.chapters-container > .chapter-section:nth-child(n+6) { animation-delay: 0.6s; }

.practice-grid > .practice-card {
  animation: fadeInUp 0.4s ease-out forwards;
}

.practice-grid > .practice-card:nth-child(1) { animation-delay: 0.05s; }
.practice-grid > .practice-card:nth-child(2) { animation-delay: 0.1s; }
.practice-grid > .practice-card:nth-child(3) { animation-delay: 0.15s; }
.practice-grid > .practice-card:nth-child(4) { animation-delay: 0.2s; }
.practice-grid > .practice-card:nth-child(5) { animation-delay: 0.25s; }
.practice-grid > .practice-card:nth-child(6) { animation-delay: 0.3s; }
.practice-grid > .practice-card:nth-child(n+7) { animation-delay: 0.35s; }

/* 动画关键帧 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 过渡组 */
.transition-group {
  transition: all 0.5s ease;
}

/* 练习题列表容器 */
.practice-list {
  margin-bottom: 40px;
}

/* 加载状态 */
.loading-state {
  text-align: center;
  padding: 80px 20px;
  color: #666;
  font-size: 16px;
  animation: fadeIn 0.5s ease-out;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 15px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #4CAF50;
  border-radius: 50%;
  animation: spin 1s linear infinite, pulse 1.5s ease-in-out infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #999;
  font-size: 16px;
  animation: fadeIn 0.5s ease-out;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 15px;
  opacity: 0.5;
  animation: pulse 2s ease-in-out infinite;
}

/* 章节容器 */
.chapters-container {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* 章节部分 */
.chapter-section {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 25px;
  transition: box-shadow 0.3s ease;
}

.chapter-section:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.chapter-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
}

.chapter-section-title {
  font-size: 20px;
  color: #333;
  margin: 0;
  font-weight: 600;
}

.chapter-section-count {
  font-size: 14px;
  color: #999;
  background-color: #f5f5f5;
  padding: 5px 15px;
  border-radius: 15px;
  font-weight: 500;
}

.chapter-empty {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 14px;
}

/* 练习网格 */
.practice-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}



/* 练习卡片头部 */
.practice-header {
  display: flex;
  align-items: flex-start;
  margin-bottom: 15px;
}

.practice-icon {
  font-size: 24px;
  margin-right: 15px;
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 12px;
  background-color: #f5f5f5;
  flex-shrink: 0;
  transition: background-color 0.3s ease;
}

.practice-card:hover .practice-icon {
  background-color: rgba(76, 175, 80, 0.1);
}

.practice-info {
  flex: 1;
}

.practice-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 8px 0;
  line-height: 1.4;
  transition: color 0.3s ease;
}

.practice-card:hover .practice-title {
  color: #4CAF50;
}

.practice-meta {
  display: flex;
  gap: 10px;
  align-items: center;
  margin: 0;
}

.practice-type {
  font-size: 12px;
  color: #6c757d;
  background-color: #f8f9fa;
  padding: 3px 8px;
  border-radius: 10px;
}

.practice-language {
  font-size: 10px;
  color: #fff;
  background-color: #495057;
  padding: 3px 8px;
  border-radius: 10px;
  text-transform: uppercase;
  font-weight: 600;
}

/* 练习内容 */
.practice-content {
  margin-bottom: 20px;
  flex: 1;
}

.practice-description {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 练习底部 */
.practice-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 15px;
  border-top: 1px solid #f8f9fa;
}

.practice-stats {
  display: flex;
  gap: 10px;
  align-items: center;
}

.question-count-badge {
  font-size: 12px;
  color: #666;
  background-color: #f5f5f5;
  padding: 4px 10px;
  border-radius: 12px;
}

.difficulty-badge {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 500;
}

.difficulty-badge.easy {
  background-color: #e8f5e9;
  color: #4caf50;
}

.difficulty-badge.medium {
  background-color: #fff3e0;
  color: #ff9800;
}

.difficulty-badge.hard {
  background-color: #ffebee;
  color: #f44336;
}

.start-button {
  padding: 8px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(76, 175, 80, 0.2);
}

.start-button:hover {
  background-color: #45a049;
  box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
  transform: translateY(-1px);
}

.start-button:active {
  transform: translateY(0);
}

/* 统计部分 */
.stats-section {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 25px;
}

.stats-header {
  margin-bottom: 25px;
}

.stats-header h2 {
  font-size: 20px;
  color: #333;
  margin: 0;
  font-weight: 600;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  text-align: center;
  padding: 25px;
  background-color: #f8f9fa;
  border-radius: 12px;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.stat-card:hover {
  background-color: #e9ecef;
  border-color: #dee2e6;
  transform: translateY(-2px);
}

.stat-icon {
  font-size: 32px;
  margin-bottom: 15px;
  display: block;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
  line-height: 1;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

/* 响应式设计 */
/* 大屏幕桌面 (1200px+) */
@media (min-width: 1200px) {
  .practice-grid {
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  }
}

/* 中等屏幕桌面 (992px-1199px) */
@media (max-width: 1199px) {
  .practice-grid {
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  }
}

/* 平板设备 (768px-991px) */
@media (max-width: 991px) {
  .practice-grid {
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  }
  
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 小屏平板/手机横屏 (576px-767px) */
@media (max-width: 767px) {
  .practice-view {
    padding: 15px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .page-description {
    font-size: 14px;
  }
  
  .chapter-section {
    padding: 20px;
  }
  
  .chapter-section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .practice-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .practice-card {
    padding: 18px;
  }
  
  .practice-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .practice-stats {
    justify-content: center;
  }
  
  .start-button {
    width: 100%;
    padding: 10px;
  }
  
  .stats-cards {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .stat-card {
    padding: 20px;
  }
  
  .stat-value {
    font-size: 24px;
  }
  
  /* 触摸设备优化 */
  .practice-card {
    touch-action: manipulation;
  }
  
  .book-tab {
    touch-action: manipulation;
  }
}

/* 手机设备 (小于576px) */
@media (max-width: 575px) {
  .page-header h1 {
    font-size: 20px;
  }
  
  .book-tab {
    padding: 8px 15px;
    font-size: 14px;
  }
  
  .chapter-section {
    padding: 15px;
  }
  
  .chapter-section-title {
    font-size: 18px;
  }
  
  .practice-card {
    padding: 15px;
  }
  
  .practice-icon {
    width: 40px;
    height: 40px;
    font-size: 20px;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
  
  /* 字体大小优化 */
  .practice-title {
    font-size: 15px;
  }
  
  .practice-description {
    font-size: 13px;
  }
  
  .chapter-section-count {
    font-size: 13px;
  }
}

/* 超小屏幕设备 (小于375px) */
@media (max-width: 374px) {
  .practice-view {
    padding: 10px;
  }
  
  .chapter-section {
    padding: 12px;
  }
  
  .practice-card {
    padding: 12px;
  }
  
  .book-tab {
    padding: 6px 12px;
    font-size: 13px;
  }
}
</style>

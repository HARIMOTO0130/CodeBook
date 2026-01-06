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
        <p>正在加载练习题...</p>
      </div>
      
      <div v-else-if="currentBookChapters.length === 0" class="empty-state">
        <p>该书籍暂无练习题</p>
      </div>
      
      <div v-else>
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
                <div class="practice-icon">{{ getLanguageIcon(practice.language) }}</div>
                <div class="practice-info">
                  <h3 class="practice-title">{{ practice.title.replace(/- 练习题$/, '') }}</h3>
                  <p class="practice-type">{{ getQuestionTypesText(practice) }}</p>
                </div>
              </div>
              
              <div class="practice-content">
                <p class="practice-description">{{ truncateText(practice.description, 150) }}</p>
              </div>
              
              <div class="practice-footer">
                <span class="question-count-badge">{{ getQuestionCount(practice) }} 道题</span>
                <span class="difficulty-badge" :class="getDifficultyClass(practice.difficulty)">
                  {{ getDifficultyText(practice.difficulty) }}
                </span>
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
          <div class="stat-value">{{ totalPractices }}</div>
          <div class="stat-label">总练习次数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ completedPractices }}</div>
          <div class="stat-label">已完成练习</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ averageScore }}%</div>
          <div class="stat-label">平均得分</div>
        </div>
        <div class="stat-card">
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
        // 兼容旧格式
        currentQuestions.value = buildQuestionsFromPractice(practice.practice)
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

    // 判断错误类型
    const determineErrorType = (userAnswer, correctAnswer) => {
      if (!userAnswer) return '未作答'
      if (typeof userAnswer === 'string' && typeof correctAnswer === 'string') {
        if (userAnswer.trim() === correctAnswer.trim()) return '正确'
        if (userAnswer.length !== correctAnswer.length) return '长度不匹配'
        return '内容不匹配'
      }
      if (typeof userAnswer !== typeof correctAnswer) return '类型错误'
      return '答案错误'
    }
    
    // 判断题目类型
    const determineQuestionType = (question) => {
      if (!question) return '未知'
      
      // 根据题目内容推断类型
      const title = (question.title || '').toLowerCase()
      const content = (question.content || '').toLowerCase()
      
      if (question.type) return question.type
      if (title.includes('选择') || title.includes('单选') || title.includes('多选') || 
          content.includes('选择') || content.includes('单选') || content.includes('多选')) {
        return 'mcq'
      }
      if (title.includes('填空') || title.includes('补全') || 
          content.includes('填空') || content.includes('补全')) {
        return 'fill'
      }
      if (title.includes('编程') || title.includes('code') || title.includes('函数') || 
          title.includes('算法') || content.includes('代码') || content.includes('编程') ||
          question.expectedOutput || question.codeTemplate) {
        return 'code'
      }
      return 'unknown'
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

    const submitPracticeResult = async (result) => {
      try {
        // 使用新的API参数格式
        await api.submitPractice(
          currentPracticeId.value,
          result.score,
          result.userCode || ''
        )
        
        // 记录具体错题详情
        if (result.wrongQuestions && result.wrongQuestions.length > 0) {
          try {
            await api.addWrongQuestions(result.wrongQuestions.map(q => ({
              exerciseId: q.id,
              title: q.title,
              difficulty: q.difficulty,
              type: q.type,
              practiceId: currentPracticeId.value,
              userAnswer: q.userAnswer,
              correctAnswer: q.correctAnswer,
              errorType: q.errorType
            })))
            console.log('错题记录成功:', result.wrongQuestions.length, '道错题')
          } catch (err) {
            console.warn('错题记录失败，但不影响练习结果提交:', err)
            // 备份方案：如果API调用失败，可以在本地存储错题
            saveLocalWrongQuestions(result.wrongQuestions)
          }
        }
        
        // 重新获取练习记录
        fetchPracticeRecords()
      } catch (error) {
        console.error('提交练习结果失败:', error)
      }
    }
    
    // 保存错题到本地存储（备用方案）
    const saveLocalWrongQuestions = (questions) => {
      try {
        const existing = localStorage.getItem('localWrongQuestions')
        const wrongQuestions = existing ? JSON.parse(existing) : []
        
        // 添加新的错题，避免重复
        questions.forEach(q => {
          if (!wrongQuestions.some(item => item.exerciseId === q.id && item.practiceId === currentPracticeId.value)) {
            wrongQuestions.push({
              ...q,
              savedAt: new Date().toISOString()
            })
          }
        })
        
        localStorage.setItem('localWrongQuestions', JSON.stringify(wrongQuestions))
        console.log('错题已保存到本地存储')
      } catch (error) {
        console.error('保存本地错题失败:', error)
      }
    }
    
    // 辅助函数
    const getLanguageIcon = (language) => {
      const icons = {
        python: '🐍',
        javascript: '🟨',
        java: '☕',
        c: '⚙️',
        cpp: '➕'
      }
      return icons[language?.toLowerCase()] || '📝'
    }
    
    const getDifficultyClass = (difficulty) => {
      switch (difficulty) {
        case 1: return 'easy'
        case 2: return 'medium'
        case 3: return 'hard'
        default: return 'medium'
      }
    }
    
    const getDifficultyText = (difficulty) => {
      switch (difficulty) {
        case 1: return '简单'
        case 2: return '中等'
        case 3: return '困难'
        default: return '中等'
      }
    }
    
    const getQuestionTypeText = (questionType) => {
      const typeMap = {
        'choice': '选择题',
        'true_false': '判断题',
        'fill': '填空题',
        'code_completion': '代码补全',
        'programming': '编程题'
      }
      return typeMap[questionType] || '未知类型'
    }
    
    const getQuestionCount = (practice) => {
      // 根据练习类型计算题目数量
      if (practice.questions && Array.isArray(practice.questions)) {
        return practice.questions.length
      }
      return practice.practice?.test_cases?.length || 1
    }
    
    const getQuestionTypesText = (practice) => {
      if (!practice.questions || !Array.isArray(practice.questions)) {
        return '未知类型'
      }
      
      const types = practice.questions.map(q => {
        const typeMap = {
          'choice': '选择题',
          'true_false': '判断题',
          'fill': '填空题',
          'code_completion': '代码补全',
          'programming': '编程题'
        }
        return typeMap[q.type] || '未知'
      })
      
      const uniqueTypes = [...new Set(types)]
      return uniqueTypes.join('、')
    }
    
    const truncateText = (text, maxLength) => {
      if (!text) return ''
      return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
    }
    
    const buildQuestionsFromPractice = (practice) => {
      if (!practice) return []
      
      // 根据练习内容构建问题
      const questions = []
      
      // 添加编程题
      questions.push({
        id: 1,
        type: 'programming',
        title: '编程练习',
        stem: practice.question,
        code_template: practice.code_template || '',
        language: 'python', // 应该从chapter获取
        testCases: practice.test_cases || []
      })
      
      return questions
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
      getLanguageIcon,
      getDifficultyText,
      getDifficultyClass,
      truncateText,
      getQuestionTypesText,
      getQuestionCount
    }
  }
}
</script>

<style scoped>
.practice-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Microsoft YaHei', sans-serif;
}

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
}

.breadcrumb-item.current {
  color: #333;
  font-weight: bold;
}

.breadcrumb-separator {
  margin: 0 8px;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 28px;
  margin-bottom: 10px;
  color: #333;
}

.page-description {
  font-size: 16px;
  color: #666;
  margin: 0;
}

.book-tabs {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  overflow-x: auto;
  padding-bottom: 10px;
}

.book-tab {
  padding: 10px 20px;
  border: 1px solid #e0e0e0;
  border-radius: 20px;
  background-color: #fff;
  cursor: pointer;
  font-size: 16px;
  white-space: nowrap;
  transition: all 0.3s ease;
}

.book-tab:hover {
  border-color: #4CAF50;
  color: #4CAF50;
}

.book-tab.active {
  background-color: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

.practice-list {
  margin-bottom: 40px;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  font-size: 16px;
}

.chapter-section {
  margin-bottom: 40px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.chapter-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 2px solid #f0f0f0;
}

.chapter-section-title {
  font-size: 20px;
  color: #333;
  margin: 0;
}

.chapter-section-count {
  font-size: 14px;
  color: #999;
  background-color: #f5f5f5;
  padding: 4px 12px;
  border-radius: 12px;
}

.chapter-empty {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 14px;
}

.practice-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
}

.practice-card {
  background-color: #fff;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.practice-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.practice-header {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.practice-icon {
  font-size: 24px;
  margin-right: 15px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background-color: #f5f5f5;
}

.practice-info {
  flex: 1;
}

.practice-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 5px 0;
  line-height: 1.4;
}

.practice-type {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.practice-content {
  margin-bottom: 15px;
}

.practice-description {
  font-size: 14px;
  color: #666;
  line-height: 1.6;
  margin: 0;
}

.practice-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.question-count-badge {
  font-size: 12px;
  color: #666;
  background-color: #f5f5f5;
  padding: 2px 8px;
  border-radius: 10px;
}

.difficulty-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
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
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.start-button:hover {
  background-color: #45a049;
}

.stats-section {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.stats-header {
  margin-bottom: 20px;
}

.stats-header h2 {
  font-size: 20px;
  color: #333;
  margin: 0;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  text-align: center;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}
</style>

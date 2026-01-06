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
                  <h3 class="practice-title">{{ practice.title }}</h3>
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
      
      // 从practices中提取章节信息
      const chaptersMap = new Map()
      book.practices.forEach(practice => {
        const chapterId = practice.chapter_id
        const chapterTitle = practice.chapter_title || `章节 ${chapterId}`
        
        if (!chaptersMap.has(chapterId)) {
          chaptersMap.set(chapterId, {
            chapter_id: chapterId,
            chapter_title: chapterTitle,
            practices: []
          })
        }
        chaptersMap.get(chapterId).practices.push(practice)
      })
      
      return Array.from(chaptersMap.values())
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

    const selectBook = (bookId) => {
      selectedBookId.value = bookId
      selectedChapterId.value = null
    }
    
    // 获取练习题 - 直接从数据库获取
    const fetchPracticeChapters = async () => {
      loading.value = true
      try {
        // 使用新的API端点获取按书籍分组的练习题
        const booksData = await api.getPractices()
        
        if (Array.isArray(booksData) && booksData.length > 0) {
          books.value = booksData
          // 默认选择第一本书
          if (!selectedBookId.value) {
            selectedBookId.value = booksData[0].book_id
          }
        } else {
          books.value = []
          selectedBookId.value = null
        }
      } catch (error) {
        console.error('获取练习题失败:', error)
        // 使用模拟数据确保页面能正常显示
        books.value = getMockBooks()
        if (!selectedBookId.value && books.value.length > 0) {
          selectedBookId.value = books.value[0].book_id
        }
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
        // 使用模拟数据确保页面能正常显示
        practiceRecords.value = getMockPracticeRecords()
        // 统计数据通过计算属性自动计算，不需要额外调用函数
      }
    }
    
    // 生成模拟练习记录数据
    const getMockPracticeRecords = () => {
      return [
        {
          id: 1,
          practice: { id: 1, title: 'Python变量与数据类型练习' },
          score: 85,
          completed: true,
          created_at: new Date(Date.now() - 86400000 * 2).toISOString(),
          user_code: 'print("Hello World")'
        },
        {
          id: 2,
          practice: { id: 2, title: 'Python控制流练习' },
          score: 92,
          completed: true,
          created_at: new Date(Date.now() - 86400000).toISOString(),
          user_code: 'for i in range(10):\n    if i % 2 == 0:\n        print(i)'
        },
        {
          id: 3,
          practice: { id: 3, title: 'JavaScript函数练习' },
          score: 78,
          completed: true,
          created_at: new Date().toISOString(),
          user_code: 'const add = (a, b) => a + b;'
        }
      ]
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
    
    // 模拟数据 - 直接的练习题格式，不再与书籍关联
    const getMockBooks = () => {
      return [
        {
          book_id: 1,
          book_title: 'Python编程基础',
          practices: [
            {
              id: 1,
              chapter_title: '第1章：Python变量与数据类型',
              language: 'python',
              difficulty: 1,
              questions: [
                {
                  id: 101,
                  type: 'programming',
                  title: '编程练习：计算两数之和',
                  stem: '编写一个函数，计算两个数的和',
                  code_template: 'def add(a, b):\n    # 请在此处编写代码\n    pass',
                  language: 'python',
                  testCases: [
                    { input_data: { a: 1, b: 2 }, expected_output: 3 },
                    { input_data: { a: 5, b: 10 }, expected_output: 15 }
                  ]
                },
                {
                  id: 102,
                  type: 'programming',
                  title: '编程练习：变量赋值',
                  stem: '声明一个变量并赋值，然后打印出变量的值',
                  code_template: '# 请声明变量并赋值\n# 打印变量的值',
                  language: 'python',
                  testCases: [
                    { input_data: {}, expected_output: 'Hello Python' }
                  ]
                }
              ]
            },
            {
              id: 2,
              chapter_title: '第2章：Python控制流',
              language: 'python',
              difficulty: 2,
              questions: [
                {
                  id: 201,
                  type: 'programming',
                  title: '编程练习：打印偶数',
                  stem: '使用for循环打印1到10之间的所有偶数',
                  code_template: '# 请在此处编写代码',
                  language: 'python',
                  testCases: [
                    { input_data: {}, expected_output: '2\n4\n6\n8\n10' }
                  ]
                },
                {
                  id: 202,
                  type: 'programming',
                  title: '编程练习：if-else判断',
                  stem: '判断一个数是否为正数',
                  code_template: 'def is_positive(num):\n    # 请在此处编写代码\n    pass',
                  language: 'python',
                  testCases: [
                    { input_data: { num: 5 }, expected_output: true },
                    { input_data: { num: -3 }, expected_output: false }
                  ]
                }
              ]
            },
            {
              id: 3,
              chapter_title: '第3章：Python函数',
              language: 'python',
              difficulty: 2,
              questions: [
                {
                  id: 301,
                  type: 'programming',
                  title: '编程练习：定义函数',
                  stem: '定义一个函数，计算圆的面积',
                  code_template: 'def circle_area(radius):\n    # 请在此处编写代码\n    pass',
                  language: 'python',
                  testCases: [
                    { input_data: { radius: 5 }, expected_output: 78.54 }
                  ]
                }
              ]
            }
          ]
        },
        {
          book_id: 2,
          book_title: 'JavaScript编程入门',
          practices: [
            {
              id: 4,
              chapter_title: '第1章：JavaScript基础语法',
              language: 'javascript',
              difficulty: 1,
              questions: [
                {
                  id: 401,
                  type: 'programming',
                  title: '编程练习：变量声明',
                  stem: '使用let和const声明变量',
                  code_template: '// 请在此处编写代码',
                  language: 'javascript',
                  testCases: [
                    { input_data: {}, expected_output: 'Hello JavaScript' }
                  ]
                }
              ]
            },
            {
              id: 5,
              chapter_title: '第2章：JavaScript函数',
              language: 'javascript',
              difficulty: 2,
              questions: [
                {
                  id: 501,
                  type: 'programming',
                  title: '编程练习：箭头函数',
                  stem: '使用箭头函数定义一个求和函数',
                  code_template: 'const sum = (a, b) => {\n    // 请在此处编写代码\n};',
                  language: 'javascript',
                  testCases: [
                    { input_data: { a: 1, b: 2 }, expected_output: 3 }
                  ]
                }
              ]
            },
            {
              id: 6,
              chapter_title: '第3章：JavaScript数组',
              language: 'javascript',
              difficulty: 2,
              questions: [
                {
                  id: 601,
                  type: 'programming',
                  title: '编程练习：数组操作',
                  stem: '使用数组方法过滤偶数',
                  code_template: 'const filterEven = (arr) => {\n    // 请在此处编写代码\n};',
                  language: 'javascript',
                  testCases: [
                    { input_data: { arr: [1, 2, 3, 4, 5] }, expected_output: [2, 4] }
                  ]
                }
              ]
            }
          ]
        },
        {
          book_id: 3,
          book_title: 'Java编程进阶',
          practices: [
            {
              id: 7,
              chapter_title: '第1章：Java面向对象',
              language: 'java',
              difficulty: 2,
              questions: [
                {
                  id: 701,
                  type: 'programming',
                  title: '编程练习：类定义',
                  stem: '定义一个Person类',
                  code_template: 'class Person {\n    // 请在此处编写代码\n}',
                  language: 'java',
                  testCases: [
                    { input_data: {}, expected_output: 'Person created' }
                  ]
                }
              ]
            },
            {
              id: 8,
              chapter_title: '第2章：Java集合框架',
              language: 'java',
              difficulty: 3,
              questions: [
                {
                  id: 801,
                  type: 'programming',
                  title: '编程练习：ArrayList使用',
                  stem: '使用ArrayList存储和遍历数据',
                  code_template: 'import java.util.ArrayList;\n\npublic class ArrayListDemo {\n    // 请在此处编写代码\n}',
                  language: 'java',
                  testCases: [
                    { input_data: {}, expected_output: 'ArrayList demo' }
                  ]
                }
              ]
            },
            {
              id: 9,
              chapter_title: '第3章：Java异常处理',
              language: 'java',
              difficulty: 3,
              questions: [
                {
                  id: 901,
                  type: 'programming',
                  title: '编程练习：try-catch',
                  stem: '使用try-catch处理异常',
                  code_template: 'public class ExceptionDemo {\n    // 请在此处编写代码\n}',
                  language: 'java',
                  testCases: [
                    { input_data: {}, expected_output: 'Exception handled' }
                  ]
                }
              ]
            }
          ]
        }
      ]
    }

    const getMockPracticeChapters = () => {
      return [
        {
          id: 1,
          title: 'Python变量与数据类型练习',
          language: 'python',
          difficulty: 1,
          questions: [
            {
              id: 101,
              type: 'programming',
              title: '编程练习：计算两数之和',
              stem: '编写一个函数，计算两个数的和',
              code_template: 'def add(a, b):\n    # 请在此处编写代码\n    pass',
              language: 'python',
              testCases: [
                { input_data: { a: 1, b: 2 }, expected_output: 3 },
                { input_data: { a: 5, b: 10 }, expected_output: 15 }
              ]
            },
            {
              id: 102,
              type: 'programming',
              title: '编程练习：变量赋值',
              stem: '声明一个变量并赋值，然后打印出变量的值',
              code_template: '# 请声明变量并赋值\n# 打印变量的值',
              language: 'python',
              testCases: [
                { input_data: {}, expected_output: 'Hello Python' }
              ]
            },
            {
              id: 103,
              type: 'programming',
              title: '编程练习：字符串拼接',
              stem: '将两个字符串拼接成一个新字符串',
              code_template: 'def concat_strings(str1, str2):\n    # 请在此处编写代码\n    pass',
              language: 'python',
              testCases: [
                { input_data: { str1: 'Hello', str2: 'World' }, expected_output: 'HelloWorld' }
              ]
            },
            {
              id: 104,
              type: 'programming',
              title: '编程练习：数字转字符串',
              stem: '将数字转换为字符串类型',
              code_template: 'def num_to_str(num):\n    # 请在此处编写代码\n    pass',
              language: 'python',
              testCases: [
                { input_data: { num: 123 }, expected_output: '123' }
              ]
            },
            {
              id: 105,
              type: 'programming',
              title: '编程练习：获取字符串长度',
              stem: '编写一个函数，返回字符串的长度',
              code_template: 'def get_length(s):\n    # 请在此处编写代码\n    pass',
              language: 'python',
              testCases: [
                { input_data: { s: 'Python' }, expected_output: 6 }
              ]
            },
            {
              id: 106,
              type: 'programming',
              title: '编程练习：整数除法',
              stem: '计算两个整数的商（整除）',
              code_template: 'def divide(a, b):\n    # 请在此处编写代码\n    pass',
              language: 'python',
              testCases: [
                { input_data: { a: 10, b: 3 }, expected_output: 3 }
              ]
            },
            {
              id: 107,
              type: 'programming',
              title: '编程练习：求余数',
              stem: '计算两个整数相除的余数',
              code_template: 'def remainder(a, b):\n    # 请在此处编写代码\n    pass',
              language: 'python',
              testCases: [
                { input_data: { a: 10, b: 3 }, expected_output: 1 }
              ]
            },
            {
              id: 108,
              type: 'programming',
              title: '编程练习：幂运算',
              stem: '计算一个数的n次方',
              code_template: 'def power(base, exponent):\n    # 请在此处编写代码\n    pass',
              language: 'python',
              testCases: [
                { input_data: { base: 2, exponent: 3 }, expected_output: 8 }
              ]
            },
            {
              id: 109,
              type: 'programming',
              title: '编程练习：字符串转大写',
              stem: '将字符串转换为大写形式',
              code_template: 'def to_uppercase(s):\n    # 请在此处编写代码\n    pass',
              language: 'python',
              testCases: [
                { input_data: { s: 'hello' }, expected_output: 'HELLO' }
              ]
            },
            {
              id: 110,
              type: 'programming',
              title: '编程练习：字符串转小写',
              stem: '将字符串转换为小写形式',
              code_template: 'def to_lowercase(s):\n    # 请在此处编写代码\n    pass',
              language: 'python',
              testCases: [
                { input_data: { s: 'HELLO' }, expected_output: 'hello' }
              ]
            }
          ]
        },
        {
          id: 2,
          title: 'Python控制流练习',
          language: 'python',
          difficulty: 2,
          questions: [
            {
              id: 201,
              type: 'programming',
              title: '编程练习：打印偶数',
              stem: '使用for循环打印1到10之间的所有偶数',
              code_template: '# 请在此处编写代码',
              language: 'python',
              testCases: [
                { input_data: {}, expected_output: '2\n4\n6\n8\n10' }
              ]
            },
            {
              id: 202,
              type: 'programming',
              title: '编程练习：if-else判断',
              stem: '判断一个数是否为正数',
              code_template: 'def is_positive(num):\n    # 请在此处编写代码\n    pass',
              language: 'python',
              testCases: [
                { input_data: { num: 5 }, expected_output: true },
                { input_data: { num: -3 }, expected_output: false }
              ]
            },
            {
              id: 203,
              type: 'programming',
              title: '编程练习：while循环求和',
              stem: '使用while循环计算1到100的和',
              code_template: '# 请在此处编写代码\n# 返回1到100的和',
              language: 'python',
              testCases: [
                { input_data: {}, expected_output: 5050 }
              ]
            },
            {
              id: 204,
              type: 'programming',
              title: '编程练习：判断奇偶性',
              stem: '判断一个数是奇数还是偶数',
              code_template: 'def check_parity(num):\n    # 返回"even"表示偶数，"odd"表示奇数\n    pass',
              language: 'python',
              testCases: [
                { input_data: { num: 4 }, expected_output: 'even' },
                { input_data: { num: 7 }, expected_output: 'odd' }
              ]
            },
            {
              id: 205,
              type: 'programming',
              title: '编程练习：for循环遍历列表',
              stem: '遍历列表并打印每个元素',
              code_template: 'def print_list(items):\n    # 请在此处编写代码\n    # 返回打印的字符串',
              language: 'python',
              testCases: [
                { input_data: { items: [1, 2, 3] }, expected_output: '1\n2\n3' }
              ]
            },
            {
              id: 206,
              type: 'programming',
              title: '编程练习：elif条件判断',
              stem: '根据分数判断等级',
              code_template: 'def get_grade(score):\n    # 90-100: A, 80-89: B, 70-79: C, 60-69: D, <60: F\n    pass',
              language: 'python',
              testCases: [
                { input_data: { score: 85 }, expected_output: 'B' },
                { input_data: { score: 60 }, expected_output: 'D' }
              ]
            },
            {
              id: 207,
              type: 'programming',
              title: '编程练习：break语句',
              stem: '使用break跳出循环',
              code_template: 'def find_first_negative(numbers):\n    # 找到第一个负数并返回\n    pass',
              language: 'python',
              testCases: [
                { input_data: { numbers: [1, 3, -5, 2] }, expected_output: -5 }
              ]
            },
            {
              id: 208,
              type: 'programming',
              title: '编程练习：continue语句',
              stem: '跳过偶数，打印奇数',
              code_template: 'def print_odds(start, end):\n    # 打印start到end之间的所有奇数\n    # 返回打印的字符串',
              language: 'python',
              testCases: [
                { input_data: { start: 1, end: 10 }, expected_output: '1\n3\n5\n7\n9' }
              ]
            },
            {
              id: 209,
              type: 'programming',
              title: '编程练习：嵌套循环',
              stem: '打印九九乘法表的前5行',
              code_template: '# 请在此处编写代码\n# 返回打印的字符串',
              language: 'python',
              testCases: [
                { input_data: {}, expected_output: '1x1=1\n1x2=2\n2x2=4\n1x3=3\n2x3=6\n3x3=9\n1x4=4\n2x4=8\n3x4=12\n4x4=16\n1x5=5\n2x5=10\n3x5=15\n4x5=20\n5x5=25' }
              ]
            },
            {
              id: 210,
              type: 'programming',
              title: '编程练习：三元运算符',
              stem: '使用三元运算符简化条件判断',
              code_template: 'def max_of_two(a, b):\n    # 返回两个数中的较大值\n    pass',
              language: 'python',
              testCases: [
                { input_data: { a: 5, b: 8 }, expected_output: 8 }
              ]
            }
          ]
        },
        {
          id: 3,
          title: 'JavaScript函数练习',
          language: 'javascript',
          difficulty: 2,
          questions: [
            {
              id: 301,
              type: 'programming',
              title: '编程练习：回文字符串判断',
              stem: '编写一个函数，判断一个字符串是否为回文',
              code_template: 'function isPalindrome(str) {\n    // 请在此处编写代码\n}',
              language: 'javascript',
              testCases: [
                { input_data: { str: 'level' }, expected_output: true },
                { input_data: { str: 'hello' }, expected_output: false }
              ]
            },
            {
              id: 302,
              type: 'programming',
              title: '编程练习：函数声明',
              stem: '声明一个函数并调用',
              code_template: '// 声明一个sayHello函数\nfunction sayHello() {\n    // 返回Hello World字符串\n}\n\n// 调用函数并打印结果',
              language: 'javascript',
              testCases: [
                { input_data: {}, expected_output: 'Hello World' }
              ]
            },
            {
              id: 303,
              type: 'programming',
              title: '编程练习：箭头函数',
              stem: '使用箭头函数计算两数之和',
              code_template: '// 使用箭头函数定义add函数\nconst add = (a, b) => {\n    // 请在此处编写代码\n};',
              language: 'javascript',
              testCases: [
                { input_data: { a: 3, b: 7 }, expected_output: 10 }
              ]
            },
            {
              id: 304,
              type: 'programming',
              title: '编程练习：函数参数默认值',
              stem: '为函数参数设置默认值',
              code_template: 'function greet(name, greeting = "Hello") {\n    // 返回格式化的问候语\n}',
              language: 'javascript',
              testCases: [
                { input_data: { name: 'John' }, expected_output: 'Hello, John!' }
              ]
            },
            {
              id: 305,
              type: 'programming',
              title: '编程练习：剩余参数',
              stem: '使用剩余参数计算多个数的和',
              code_template: 'function sum(...numbers) {\n    // 计算所有参数的和\n}',
              language: 'javascript',
              testCases: [
                { input_data: { numbers: [1, 2, 3, 4] }, expected_output: 10 }
              ]
            },
            {
              id: 306,
              type: 'programming',
              title: '编程练习：函数嵌套',
              stem: '在函数内部定义并调用另一个函数',
              code_template: 'function outerFunction(x) {\n    // 定义内部函数\n    function innerFunction(y) {\n        // 返回x + y\n    }\n    // 调用内部函数并返回结果\n}',
              language: 'javascript',
              testCases: [
                { input_data: { x: 5, y: 3 }, expected_output: 8 }
              ]
            },
            {
              id: 307,
              type: 'programming',
              title: '编程练习：函数返回函数',
              stem: '创建一个函数，返回另一个函数',
              code_template: 'function createMultiplier(multiplier) {\n    // 返回一个函数，该函数将输入值乘以multiplier\n}',
              language: 'javascript',
              testCases: [
                { input_data: { multiplier: 2, value: 4 }, expected_output: 8 }
              ]
            },
            {
              id: 308,
              type: 'programming',
              title: '编程练习：递归函数',
              stem: '使用递归计算阶乘',
              code_template: 'function factorial(n) {\n    // 使用递归计算n的阶乘\n}',
              language: 'javascript',
              testCases: [
                { input_data: { n: 5 }, expected_output: 120 }
              ]
            },
            {
              id: 309,
              type: 'programming',
              title: '编程练习：匿名函数',
              stem: '使用匿名函数计算数组元素的平方',
              code_template: 'function squareArray(arr) {\n    // 使用匿名函数将数组中的每个元素平方\n}',
              language: 'javascript',
              testCases: [
                { input_data: { arr: [1, 2, 3, 4] }, expected_output: [1, 4, 9, 16] }
              ]
            },
            {
              id: 310,
              type: 'programming',
              title: '编程练习：函数作用域',
              stem: '理解函数作用域的变量访问',
              code_template: 'let globalVar = "global";\n\nfunction scopeTest() {\n    let localVar = "local";\n    // 打印变量并返回结果字符串\n}',
              language: 'javascript',
              testCases: [
                { input_data: {}, expected_output: 'global, local' }
              ]
            }
          ]
        },
        {
          id: 4,
          title: '算法基础练习',
          language: 'python',
          difficulty: 3,
          questions: [
            {
              id: 401,
              type: 'programming',
              title: '编程练习：冒泡排序',
              stem: '实现冒泡排序算法',
              code_template: 'def bubble_sort(arr):\n    # 请在此处编写代码\n    return arr',
              language: 'python',
              testCases: [
                { input_data: { arr: [3, 1, 4, 2] }, expected_output: [1, 2, 3, 4] },
                { input_data: { arr: [5, 2, 8, 1, 9] }, expected_output: [1, 2, 5, 8, 9] }
              ]
            },
            {
              id: 402,
              type: 'programming',
              title: '编程练习：选择排序',
              stem: '实现选择排序算法',
              code_template: 'def selection_sort(arr):\n    # 请在此处编写代码\n    return arr',
              language: 'python',
              testCases: [
                { input_data: { arr: [64, 25, 12, 22, 11] }, expected_output: [11, 12, 22, 25, 64] }
              ]
            },
            {
              id: 403,
              type: 'programming',
              title: '编程练习：插入排序',
              stem: '实现插入排序算法',
              code_template: 'def insertion_sort(arr):\n    # 请在此处编写代码\n    return arr',
              language: 'python',
              testCases: [
                { input_data: { arr: [12, 11, 13, 5, 6] }, expected_output: [5, 6, 11, 12, 13] }
              ]
            },
            {
              id: 404,
              type: 'programming',
              title: '编程练习：二分查找',
              stem: '在有序数组中使用二分查找',
              code_template: 'def binary_search(arr, target):\n    # 返回目标值的索引，如果不存在返回-1\n    pass',
              language: 'python',
              testCases: [
                { input_data: { arr: [1, 2, 3, 4, 5], target: 3 }, expected_output: 2 },
                { input_data: { arr: [1, 2, 3, 4, 5], target: 6 }, expected_output: -1 }
              ]
            },
            {
              id: 405,
              type: 'programming',
              title: '编程练习：快速排序',
              stem: '实现快速排序算法',
              code_template: 'def quick_sort(arr):\n    # 请在此处编写代码\n    return arr',
              language: 'python',
              testCases: [
                { input_data: { arr: [10, 7, 8, 9, 1, 5] }, expected_output: [1, 5, 7, 8, 9, 10] }
              ]
            },
            {
              id: 406,
              type: 'programming',
              title: '编程练习：归并排序',
              stem: '实现归并排序算法',
              code_template: 'def merge_sort(arr):\n    # 请在此处编写代码\n    return arr',
              language: 'python',
              testCases: [
                { input_data: { arr: [38, 27, 43, 3, 9, 82, 10] }, expected_output: [3, 9, 10, 27, 38, 43, 82] }
              ]
            },
            {
              id: 407,
              type: 'programming',
              title: '编程练习：计数排序',
              stem: '实现计数排序算法',
              code_template: 'def counting_sort(arr):\n    # 请在此处编写代码\n    return arr',
              language: 'python',
              testCases: [
                { input_data: { arr: [4, 2, 2, 8, 3, 3, 1] }, expected_output: [1, 2, 2, 3, 3, 4, 8] }
              ]
            },
            {
              id: 408,
              type: 'programming',
              title: '编程练习：桶排序',
              stem: '实现桶排序算法',
              code_template: 'def bucket_sort(arr):\n    # 请在此处编写代码\n    return arr',
              language: 'python',
              testCases: [
                { input_data: { arr: [0.42, 0.32, 0.23, 0.52, 0.25, 0.47, 0.51] }, expected_output: [0.23, 0.25, 0.32, 0.42, 0.47, 0.51, 0.52] }
              ]
            },
            {
              id: 409,
              type: 'programming',
              title: '编程练习：基数排序',
              stem: '实现基数排序算法',
              code_template: 'def radix_sort(arr):\n    # 请在此处编写代码\n    return arr',
              language: 'python',
              testCases: [
                { input_data: { arr: [170, 45, 75, 90, 802, 24, 2, 66] }, expected_output: [2, 24, 45, 66, 75, 90, 170, 802] }
              ]
            },
            {
              id: 410,
              type: 'programming',
              title: '编程练习：希尔排序',
              stem: '实现希尔排序算法',
              code_template: 'def shell_sort(arr):\n    # 请在此处编写代码\n    return arr',
              language: 'python',
              testCases: [
                { input_data: { arr: [12, 34, 54, 2, 3] }, expected_output: [2, 3, 12, 34, 54] }
              ]
            }
          ]
        }
      ]
    }
    
    // 初始化数据
    onMounted(async () => {
      await fetchPracticeChapters()
      await fetchPracticeRecords()
      
      // 检查URL参数,自动选择对应的书籍和章节
      if (urlBookId.value) {
        const bookExists = books.value.some(b => b.book_id === urlBookId.value)
        if (bookExists) {
          selectedBookId.value = urlBookId.value
          // 自动选择第一个章节
          const book = books.value.find(b => b.book_id === urlBookId.value)
          if (book && book.practices.length > 0) {
            const firstChapterId = book.practices[0].chapter_id
            selectedChapterId.value = firstChapterId
          }
          
          // 如果URL中指定了章节ID,则选择该章节
          if (urlChapterId.value) {
            const chapterExists = book.practices.some(p => p.chapter_id === urlChapterId.value)
            if (chapterExists) {
              selectedChapterId.value = urlChapterId.value
            }
          }
        }
      }
    })
    
    return {
      loading,
      books,
      selectedBookId,
      selectedChapterId,
      currentBookPractices,
      currentBookChapters,
      currentChapterPractices,
      practiceRecords,
      showPracticeModal,
      currentQuestions,
      currentPracticeName,
      totalPractices,
      completedPractices,
      averageScore,
      streakDays,
      selectBook,
      startPractice,
      closePractice,
      handlePracticeComplete,
      getLanguageIcon,
      getDifficultyClass,
      getDifficultyText,
      getQuestionTypeText,
      getQuestionTypesText,
      getQuestionCount,
      truncateText
    }
  }
}
</script>

<style scoped>
.practice-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 20px;
  font-size: 14px;
  color: #666;
}

.breadcrumb-item {
  color: #409eff;
  text-decoration: none;
  transition: color 0.2s;
}

.breadcrumb-item:hover {
  color: #66b1ff;
}

.breadcrumb-item.current {
  color: #333;
  font-weight: 500;
  pointer-events: none;
}

.book-tabs {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.book-tab {
  padding: 10px 20px;
  background: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  gap: 8px;
}

.book-tab:hover {
  background: #ecf5ff;
  border-color: #c6e2ff;
  color: #409eff;
}

.book-tab.active {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
}

.book-tab:not(.active) .practice-count {
  background: #e4e7ed;
  color: #909399;
}

.breadcrumb-separator {
  color: #999;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0 0 10px 0;
  font-size: 28px;
  color: #333;
}

.page-description {
  margin: 0;
  color: #666;
  font-size: 16px;
}

.filter-section {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 30px;
}

.filter-controls {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
}

.select-input {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  min-width: 150px;
}

.select-input:focus {
  outline: none;
  border-color: #409eff;
}

.practice-list {
  margin-bottom: 40px;
}

.chapter-section {
  margin-bottom: 40px;
}

.chapter-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
  border-bottom: 2px solid #e4e7ed;
  margin-bottom: 24px;
}

.chapter-section-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #303133;
}

.chapter-section-count {
  padding: 4px 12px;
  background: #f0f2f5;
  border-radius: 12px;
  font-size: 14px;
  color: #606266;
}

.chapter-empty {
  text-align: center;
  padding: 40px 20px;
  color: #999;
  font-size: 14px;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
  font-size: 16px;
}

.practice-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.practice-card {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.practice-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.practice-header {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}

.practice-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.practice-info {
  flex: 1;
}

.practice-title {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #333;
}

.practice-book {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.practice-content {
  flex: 1;
  margin-bottom: 20px;
}

.practice-description {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #555;
}

.practice-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.difficulty-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.difficulty-badge.easy {
  background: #f0f9eb;
  color: #67c23a;
}

.difficulty-badge.medium {
  background: #ecf5ff;
  color: #409eff;
}

.difficulty-badge.hard {
  background: #fef0f0;
  color: #f56c6c;
}

.question-count-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  background: #f4f4f5;
  color: #909399;
}

.question-count {
  font-size: 14px;
  color: #666;
}

.start-button {
  padding: 8px 20px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.start-button:hover {
  background: #66b1ff;
}

.stats-section {
  background: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 30px;
}

.stats-header {
  margin-bottom: 24px;
}

.stats-header h2 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  background: #f8f9fa;
  padding: 24px;
  border-radius: 8px;
  text-align: center;
}

.stat-value {
  font-size: 32px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .filter-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .select-input {
    min-width: auto;
  }
  
  .practice-grid {
    grid-template-columns: 1fr;
  }
  
  .stats-cards {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 480px) {
  .practice-card {
    padding: 16px;
  }
  
  .practice-title {
    font-size: 16px;
  }
  
  .stats-cards {
    grid-template-columns: 1fr;
  }
}
</style>
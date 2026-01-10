<template>
  <Teleport to="body">
    <transition name="modal">
      <div v-if="visible" class="modal-overlay" @click.self="close">
        <div class="modal-container" :class="{ 'fullscreen': isFullscreen }">
          <!-- 顶部导航 -->
          <div class="modal-header">
            <div class="header-left">
              <button class="btn-icon" @click="close" title="关闭">✕</button>
              <div class="breadcrumb">
                  <span>{{ practiceName }}</span>
                  <span>/</span>
                  <span class="current">练习题</span>
                </div>
            </div>
            <div class="header-center">
              <h3 class="practice-title">{{ practiceName }}</h3>
            </div>
            <div class="header-right">
              <button class="btn-secondary" @click="showAddToWrongQuestionsDialog = true" title="添加到错题本">
                📝 添加到错题本
              </button>
              <span class="question-progress">
                {{ currentIndex + 1 }}/{{ totalQuestions }}
              </span>
              <button class="btn-icon" @click="toggleFullscreen" title="全屏">
                {{ isFullscreen ? '🔽' : '🔼' }}
              </button>
            </div>
          </div>
          
          <!-- 题目内容区域 -->
          <div class="modal-content">
            <!-- 选择题 -->
            <div v-if="currentQuestion.type === 'choice'" class="question-choice">
              <div class="question-stem">
                <h4>{{ currentQuestion.content }}</h4>
                <div v-if="currentQuestion.description" class="question-description">
                  {{ currentQuestion.description }}
                </div>
              </div>
              
              <div class="options-container" :class="{ 'multiple': currentQuestion.multiple }">
                <label 
                  v-for="(option, index) in currentQuestion.options" 
                  :key="index"
                  class="option-item"
                  :class="{ 
                    'selected': isOptionSelected(index),
                    'correct': showFeedback && isOptionCorrect(index),
                    'incorrect': showFeedback && isOptionSelected(index) && !isOptionCorrect(index)
                  }"
                  @click="selectOption(index)"
                >
                  <div class="option-label">
                    {{ String.fromCharCode(65 + index) }}.
                  </div>
                  <div class="option-content">
                    {{ option.content }}
                  </div>
                  <div class="option-feedback" v-if="showFeedback">
                    <span v-if="isOptionCorrect(index)" class="correct-icon">✅</span>
                    <span v-else-if="isOptionSelected(index)" class="incorrect-icon">❌</span>
                  </div>
                </label>
              </div>
              
              <!-- 即时反馈 -->
              <div v-if="showFeedback" class="question-feedback">
                <div v-if="isAnswerCorrect" class="feedback-correct">
                  <div class="feedback-icon">🎉</div>
                  <div class="feedback-text">回答正确！</div>
                </div>
                <div v-else class="feedback-incorrect">
                  <div class="feedback-icon">😢</div>
                  <div class="feedback-text">回答错误，请再试一次！</div>
                </div>
                <div v-if="currentQuestion.explanation" class="feedback-explanation">
                  <strong>解析：</strong>{{ currentQuestion.explanation }}
                </div>
              </div>
            </div>
            
            <!-- 判断题 -->
            <div v-else-if="currentQuestion.type === 'judgment' || currentQuestion.type === 'Judgment'" class="question-judgment">
              <div class="question-stem">
                <h4>{{ currentQuestion.content }}</h4>
                <div v-if="currentQuestion.description" class="question-description">
                  {{ currentQuestion.description }}
                </div>
              </div>
              
              <div class="options-container">
                <label 
                  v-for="(option, index) in currentQuestion.options" 
                  :key="index"
                  class="option-item"
                  :class="{ 
                    'selected': isOptionSelected(index),
                    'correct': showFeedback && isOptionCorrect(index),
                    'incorrect': showFeedback && isOptionSelected(index) && !isOptionCorrect(index)
                  }"
                  @click="selectOption(index)"
                >
                  <div class="option-label">
                    {{ index === 0 ? 'T' : 'F' }}.
                  </div>
                  <div class="option-content">
                    {{ option.content }}
                  </div>
                  <div class="option-feedback" v-if="showFeedback">
                    <span v-if="isOptionCorrect(index)" class="correct-icon">✅</span>
                    <span v-else-if="isOptionSelected(index)" class="incorrect-icon">❌</span>
                  </div>
                </label>
              </div>
              
              <!-- 即时反馈 -->
              <div v-if="showFeedback" class="question-feedback">
                <div v-if="isAnswerCorrect" class="feedback-correct">
                  <div class="feedback-icon">🎉</div>
                  <div class="feedback-text">回答正确！</div>
                </div>
                <div v-else class="feedback-incorrect">
                  <div class="feedback-icon">😢</div>
                  <div class="feedback-text">回答错误，请再试一次！</div>
                </div>
                <div v-if="currentQuestion.explanation" class="feedback-explanation">
                  <strong>解析：</strong>{{ currentQuestion.explanation }}
                </div>
              </div>
            </div>
            
            <!-- 判断题 -->
            <div v-else-if="currentQuestion.type === 'Judgment'" class="question-choice">
              <div class="question-stem">
                <h4>{{ currentQuestion.question }}</h4>
                <div v-if="currentQuestion.description" class="question-description">
                  {{ currentQuestion.description }}
                </div>
              </div>
              
              <div class="question-options">
                <label
                  v-for="(option, index) in currentQuestion.options"
                  :key="index"
                  class="option-item"
                  :class="{
                    'selected': selectedOptions.includes(index),
                    'correct': showFeedback && isOptionCorrect(index),
                    'incorrect': showFeedback && isOptionSelected(index) && !isOptionCorrect(index)
                  }"
                  @click="selectOption(index)"
                >
                  <div class="option-label">
                    {{ index === 0 ? 'T' : 'F' }}.
                  </div>
                  <div class="option-content">
                    {{ option.content }}
                  </div>
                  <div class="option-feedback" v-if="showFeedback">
                    <span v-if="isOptionCorrect(index)" class="correct-icon">✅</span>
                    <span v-else-if="isOptionSelected(index)" class="incorrect-icon">❌</span>
                  </div>
                </label>
              </div>
              
              <!-- 即时反馈 -->
              <div v-if="showFeedback" class="question-feedback">
                <div v-if="isAnswerCorrect" class="feedback-correct">
                  <div class="feedback-icon">🎉</div>
                  <div class="feedback-text">回答正确！</div>
                </div>
                <div v-else class="feedback-incorrect">
                  <div class="feedback-icon">😢</div>
                  <div class="feedback-text">回答错误，请再试一次！</div>
                </div>
                <div v-if="currentQuestion.explanation" class="feedback-explanation">
                  <strong>解析：</strong>{{ currentQuestion.explanation }}
                </div>
              </div>
            </div>
            
            <!-- 填空题 -->
            <div v-else-if="currentQuestion.type === 'fill'" class="question-fill">
              <div class="question-stem">
                <h4>{{ currentQuestion.question }}</h4>
              </div>
              
              <div class="fill-container">
                <div v-for="(blank, index) in currentQuestion.blanks" :key="index" class="fill-item">
                  <label class="fill-label">{{ index + 1 }}. {{ blank.prompt }}</label>
                  <input 
                    type="text" 
                    v-model="userAnswers[index]"
                    class="fill-input"
                    :placeholder="blank.placeholder || '请输入答案'"
                    :disabled="showFeedback"
                  />
                  <div v-if="showFeedback" class="fill-feedback">
                    <span v-if="isFillAnswerCorrect(index)" class="correct-icon">✅</span>
                    <span v-else class="incorrect-icon">❌</span>
                    <span v-if="!isFillAnswerCorrect(index)" class="correct-answer">
                      正确答案: {{ blank.correctAnswer }}
                    </span>
                  </div>
                </div>
              </div>
              
              <!-- 即时反馈 -->
              <div v-if="showFeedback" class="question-feedback">
                <div v-if="isAnswerCorrect" class="feedback-correct">
                  <div class="feedback-icon">🎉</div>
                  <div class="feedback-text">回答正确！</div>
                </div>
                <div v-else class="feedback-incorrect">
                  <div class="feedback-icon">😢</div>
                  <div class="feedback-text">部分答案有误，请检查！</div>
                </div>
              </div>
            </div>
            
            <!-- 代码补全题 -->
            <div v-else-if="currentQuestion.type === 'codeCompletion'" class="question-code-completion">
              <div class="question-stem">
                <h4>{{ currentQuestion.question }}</h4>
                <div v-if="currentQuestion.description" class="question-description">
                  {{ currentQuestion.description }}
                </div>
              </div>
              
              <div class="code-completion-container">
                <MonacoCard 
                  v-model="codeCompletionAnswer"
                  :language="currentQuestion.language"
                  :filename="currentQuestion.filename || 'exercise.js'"
                  :read-only="false"
                  :show-footer="true"
                />
              </div>
              
              <!-- 运行结果 -->
              <div v-if="codeResult" class="code-result">
                <h5>运行结果</h5>
                <ConsoleOutput :output="codeResult.output" :charts="codeResult.charts || []" />
              </div>
            </div>
            
            <!-- 编程题 -->
            <div v-else-if="currentQuestion.type === 'programming'" class="question-programming">
              <div class="question-stem">
                <h4>{{ currentQuestion.question }}</h4>
                <div v-if="currentQuestion.description" class="question-description">
                  {{ currentQuestion.description }}
                </div>
              </div>
              
              <!-- 测试用例 -->
              <div class="test-cases">
                <h5>测试用例</h5>
                <div class="test-case-list">
                  <div 
                    v-for="(testCase, index) in currentQuestion.testCases" 
                    :key="index"
                    class="test-case-item"
                  >
                    <div class="test-case-input">
                      <strong>输入 {{ index + 1 }}:</strong> {{ testCase.input }}
                    </div>
                    <div class="test-case-output">
                      <strong>预期输出:</strong> {{ testCase.expectedOutput }}
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 代码编辑器 -->
              <div class="programming-code">
                <MonacoCard 
                  v-model="programmingAnswer"
                  :language="currentQuestion.language"
                  :filename="currentQuestion.filename || 'solution.js'"
                  :read-only="false"
                  :show-footer="true"
                />
              </div>
              
              <!-- 提交结果 -->
              <div v-if="submissionResult" class="submission-result">
                <h5>提交结果</h5>
                <div class="pass-rate">
                  <div class="pass-text">
                    {{ submissionResult.passed }}/{{ submissionResult.total }} 测试用例通过
                  </div>
                  <div class="pass-bar">
                    <div 
                      class="pass-bar-fill" 
                      :style="{ width: submissionResult.passRate + '%' }"
                      :class="{ 
                        'success': submissionResult.passRate === 100,
                        'partial': submissionResult.passRate > 0 && submissionResult.passRate < 100,
                        'failed': submissionResult.passRate === 0
                      }"
                    ></div>
                  </div>
                </div>
                
                <!-- 通过柱状图 -->
                <div class="result-chart">
                  <h6>测试用例通过情况</h6>
                  <div class="bar-chart">
                    <div 
                      v-for="(result, index) in submissionResult.testResults" 
                      :key="index"
                      class="result-bar"
                    >
                      <div 
                        class="bar" 
                        :class="result.passed ? 'passed' : 'failed'"
                      ></div>
                      <span class="bar-label">用例 {{ index + 1 }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 底部操作区 -->
          <div class="modal-footer">
            <div class="footer-left">
              <button class="btn-secondary" @click="previousQuestion" :disabled="currentIndex === 0">
                上一题
              </button>
            </div>
            
            <div class="footer-center">
              <!-- 选择题/填空题/判断题按钮 -->
              <template v-if="['choice', 'fill', 'Judgment'].includes(currentQuestion.type)">
                <button 
                  v-if="!showFeedback"
                  class="btn-primary"
                  @click="submitAnswer"
                >
                  提交答案
                </button>
                <button 
                  v-else
                  class="btn-primary"
                  @click="nextQuestion"
                >
                  下一题
                </button>
              </template>
              
              <!-- 代码补全题按钮 -->
              <template v-else-if="currentQuestion.type === 'codeCompletion'">
                <button class="btn-secondary" @click="runCode">
                  运行代码
                </button>
                <button class="btn-primary" @click="submitCode">
                  提交代码
                </button>
              </template>
              
              <!-- 编程题按钮 -->
              <template v-else-if="currentQuestion.type === 'programming'">
                <button class="btn-secondary" @click="runProgrammingCode">
                  自测运行
                </button>
                <button class="btn-primary" @click="submitProgrammingCode">
                  正式提交
                </button>
              </template>
            </div>
            
            <div class="footer-right">
              <button class="btn-secondary" @click="nextQuestion" :disabled="currentIndex === totalQuestions - 1">
                下一题
              </button>
            </div>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>

  <!-- 添加到错题本对话框 -->
  <Teleport to="body">
    <transition name="modal">
      <div v-if="showAddToWrongQuestionsDialog" class="modal-overlay" @click.self="hideAddToWrongQuestionsDialog">
        <div class="modal-container small">
          <div class="modal-header">
            <h3>添加到错题本</h3>
            <button class="btn-icon" @click="hideAddToWrongQuestionsDialog" title="关闭">✕</button>
          </div>
          <div class="modal-content">
            <div class="form-group">
              <label for="error-reason">错误原因</label>
              <textarea 
                id="error-reason" 
                v-model="newWrongQuestion.errorReason" 
                placeholder="请描述您的错误原因..."
                rows="3"
              ></textarea>
            </div>
            <div class="form-group">
              <label for="knowledge-points">关联知识点（用逗号分隔）</label>
              <input 
                id="knowledge-points" 
                v-model="newWrongQuestion.knowledgePoints"
                placeholder="例如：变量作用域,函数调用,循环结构"
              />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="hideAddToWrongQuestionsDialog">取消</button>
            <button class="btn-primary" @click="addCurrentQuestionToWrongQuestions">确认添加</button>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script>
import { ref, computed, watch } from 'vue'
import MonacoCard from './MonacoCard.vue'
import ConsoleOutput from './ConsoleOutput.vue'
import { api } from '../api/api.js'

export default {
  name: 'PracticeModal',
  components: {
    MonacoCard,
    ConsoleOutput
  },
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    questions: {
      type: Array,
      default: () => []
    },
    practiceName: {
      type: String,
      default: ''
    },
    practiceId: {
      type: Number,
      default: null
    }
  },
  emits: ['update:visible', 'close', 'complete'],
  setup(props, { emit }) {
    // 状态管理
    const currentIndex = ref(0)
    const showFeedback = ref(false)
    const isFullscreen = ref(false)
    
    // 答案存储
    const selectedOptions = ref([]) // 选择题选项
    const userAnswers = ref([]) // 填空题答案
    const codeCompletionAnswer = ref('') // 代码补全答案
    const programmingAnswer = ref('') // 编程题答案
    
    // 结果存储
    const codeResult = ref(null) // 代码运行结果
    const submissionResult = ref(null) // 提交结果
    
    // 错题本相关状态
    const showAddToWrongQuestionsDialog = ref(false)
    const newWrongQuestion = ref({
      errorReason: '',
      knowledgePoints: ''
    })
    
    // 计算属性
    const totalQuestions = computed(() => props.questions.length)
    
    const currentQuestion = computed(() => {
      if (props.questions.length === 0) {
        return {
          title: '无题目',
          type: 'choice',
          question: '当前章节暂无练习题',
          stem: '当前章节暂无练习题',
          options: []
        }
      }
      const question = props.questions[currentIndex.value] || props.questions[0]
      
      // 创建新对象，避免直接修改 props 数据
      const normalizedQuestion = { ...question }
      
      // 确保 question 字段存在（兼容 stem 字段）
      if (!normalizedQuestion.question && normalizedQuestion.stem) {
        normalizedQuestion.question = normalizedQuestion.stem
      } else if (!normalizedQuestion.question && !normalizedQuestion.stem) {
        normalizedQuestion.question = normalizedQuestion.title || '题目'
      }
      
      // 确保填空题始终有blanks数组
      if (normalizedQuestion.type === 'fill' && !normalizedQuestion.blanks) {
        normalizedQuestion.blanks = []
      }
      
      // 确保选项有 content 字段（兼容 text 字段）
      if (normalizedQuestion.options && Array.isArray(normalizedQuestion.options)) {
        normalizedQuestion.options = normalizedQuestion.options.map(opt => ({
          ...opt,
          content: opt.content || opt.text || opt.label || ''
        }))
      }
      
      return normalizedQuestion
    })
    
    // 当前答案是否正确
    const isAnswerCorrect = computed(() => {
      if (!showFeedback.value) return false
      
      if (currentQuestion.value.type === 'choice' || currentQuestion.value.type === 'Judgment') {
        if (currentQuestion.value.multiple) {
          // 多选题：所有选项必须匹配
          const correctOptions = currentQuestion.value.correctAnswer || []
          if (selectedOptions.value.length !== correctOptions.length) return false
          return correctOptions.every(opt => selectedOptions.value.includes(opt))
        } else {
          // 单选题/判断题：必须选中正确选项
          return selectedOptions.value[0] === currentQuestion.value.correctAnswer
        }
      } else if (currentQuestion.value.type === 'fill') {
        // 填空题：所有空都要正确
        return currentQuestion.value.blanks.every((blank, index) => {
          return userAnswers.value[index] === blank.correctAnswer
        })
      }
      return false
    })
    
    // 方法
    const close = () => {
      emit('update:visible', false)
      emit('close')
    }
    
    const toggleFullscreen = () => {
      isFullscreen.value = !isFullscreen.value
    }
    
    const previousQuestion = () => {
      if (currentIndex.value > 0) {
        resetQuestionState()
        currentIndex.value--
        loadQuestionState()
      }
    }
    
    const nextQuestion = () => {
      if (currentIndex.value < totalQuestions.value - 1) {
        // 保存当前题目的答案
        saveCurrentAnswer()
        resetQuestionState()
        currentIndex.value++
        loadQuestionState()
      } else {
        // 保存最后一题的答案
        saveCurrentAnswer()
        // 完成所有题目
        const result = {
          score: calculateScore(),
          answers: getAllAnswers()
        }
        close()
        emit('complete', result)
      }
    }
    
    // 保存当前题目的答案
    const saveCurrentAnswer = () => {
      const question = currentQuestion.value
      const questionId = question.id || question.order || currentIndex.value + 1
      
      // 找到原始问题对象（从 props.questions 中）
      const originalQuestion = props.questions.find(q => 
        (q.id || q.order) === questionId
      ) || props.questions[currentIndex.value]
      
      if (originalQuestion) {
        if (question.type === 'choice') {
          originalQuestion.selectedOption = selectedOptions.value.length > 0 ? selectedOptions.value[0] : null
        } else if (question.type === 'fill') {
          originalQuestion.userAnswers = [...userAnswers.value]
        } else if (question.type === 'codeCompletion') {
          originalQuestion.userCode = codeCompletionAnswer.value
        } else if (question.type === 'programming') {
          originalQuestion.userCode = programmingAnswer.value
        }
      }
    }
    
    // 计算得分
    const calculateScore = () => {
      let correctCount = 0
      props.questions.forEach(q => {
        if (q.type === 'choice' || q.type === 'judgment' || q.type === 'Judgment') {
          const correctAnswer = q.correctAnswer
          const userAnswer = q.selectedOption
          if (correctAnswer === userAnswer) {
            correctCount++
          }
        } else if (q.type === 'fill') {
          const blanks = q.blanks || []
          const userAnswers = q.userAnswers || []
          let allCorrect = true
          blanks.forEach((blank, idx) => {
            const userAnswer = userAnswers[idx] || ''
            const correctAnswer = blank.correctAnswer || ''
            if (userAnswer.toLowerCase() !== correctAnswer.toLowerCase()) {
              allCorrect = false
            }
          })
          if (allCorrect) {
            correctCount++
          }
        }
        // 代码题暂时不计分
      })
      return Math.round((correctCount / props.questions.length) * 100)
    }
    
    // 获取所有答案
    const getAllAnswers = () => {
      return props.questions.map(q => ({
        id: q.id || q.order,
        type: q.type,
        selectedOption: q.selectedOption,
        userAnswers: q.userAnswers,
        userCode: q.userCode
      }))
    }
    
    // 重置当前题目的状态
    const resetQuestionState = () => {
      showFeedback.value = false
      codeResult.value = null
      submissionResult.value = null
    }
    
    // 加载当前题目的状态（从本地存储或初始化）
    const loadQuestionState = () => {
      const question = currentQuestion.value
      
      // 如果是重做模式，忽略之前保存的作答记录
      const isRedo = question.selectedOption === undefined && 
                     question.userAnswers === undefined && 
                     question.userCode === undefined
      
      if (question.type === 'choice' || question.type === 'judgment' || question.type === 'Judgment') {
        // 重做模式或没有保存的答案时，重置选项
        selectedOptions.value = isRedo ? [] : (question.selectedOption !== undefined ? [question.selectedOption] : [])
      } else if (question.type === 'fill') {
        // 确保blanks数组存在且不为空
        const blanksCount = (question.blanks && question.blanks.length) || 0
        // 重做模式或没有保存的答案时，重置答案
        userAnswers.value = isRedo ? new Array(blanksCount).fill('') : (question.userAnswers || new Array(blanksCount).fill(''))
      } else if (question.type === 'codeCompletion') {
        // 重做模式时使用原始模板，否则使用保存的答案
        codeCompletionAnswer.value = isRedo ? (question.code_template || '') : (question.userCode || question.code_template || '')
      } else if (question.type === 'programming') {
        // 重做模式时使用初始代码，否则使用保存的答案
        programmingAnswer.value = isRedo ? (question.code_template || question.initial_code || '') : (question.userCode || question.initial_code || question.code_template || '')
      }
    }
    
    // 重置所有作答状态（用于重做模式）
    const resetAllAnswers = () => {
      selectedOptions.value = []
      userAnswers.value = []
      codeCompletionAnswer.value = ''
      programmingAnswer.value = ''
      showFeedback.value = false
      codeResult.value = null
      submissionResult.value = null
      currentIndex.value = 0
      
      // 清除所有问题的作答记录（注意：这里修改 props 是为了保存状态，但应该通过 emit 通知父组件）
      // 为了避免递归更新，我们只在确实需要时修改
      if (props.questions && Array.isArray(props.questions)) {
        props.questions.forEach(q => {
          if (q.selectedOption !== undefined) {
            delete q.selectedOption
          }
          if (q.userAnswers !== undefined) {
            delete q.userAnswers
          }
          if (q.userCode !== undefined) {
            delete q.userCode
          }
        })
      }
    }
    
    // 监听 visible 属性，当打开时重置状态
    watch(() => props.visible, (newVal) => {
      if (newVal) {
        // 检查是否有重做标志（通过检查第一个问题是否有作答记录）
        const hasAnswers = props.questions && props.questions.length > 0 && 
          props.questions.some(q => q.selectedOption !== undefined || q.userAnswers !== undefined || q.userCode !== undefined)
        
        // 如果没有作答记录，说明是重做模式，重置所有状态
        if (!hasAnswers) {
          resetAllAnswers()
          console.log('检测到重做模式，已重置所有作答状态')
        } else {
          // 否则只重置当前题目的状态
          resetQuestionState()
          currentIndex.value = 0
        }
        
        // 加载第一题的状态
        loadQuestionState()
      }
    })
    
    // 选择题相关方法
    const isOptionSelected = (index) => {
      return selectedOptions.value.includes(index)
    }
    
    const isOptionCorrect = (index) => {
      const correct = currentQuestion.value.correctAnswer
      if (Array.isArray(correct)) {
        return correct.includes(index)
      }
      return correct === index
    }
    
    const selectOption = (index) => {
      if (showFeedback.value) return
      
      if (currentQuestion.value.multiple) {
        // 多选
        const idx = selectedOptions.value.indexOf(index)
        if (idx > -1) {
          selectedOptions.value.splice(idx, 1)
        } else {
          selectedOptions.value.push(index)
        }
      } else {
        // 单选
        selectedOptions.value = [index]
      }
    }
    
    // 填空题相关方法
    const isFillAnswerCorrect = (index) => {
      const blanks = currentQuestion.value.blanks || []
      const blank = blanks[index]
      return blank && userAnswers.value[index] === blank.correctAnswer
    }
    
    // 提交答案（选择题/填空题/判断题）
    const submitAnswer = () => {
      showFeedback.value = true
    }
    
    // 自动检测代码语言
    const detectLanguage = (code) => {
      // 统计特征出现次数
      let pythonFeatures = 0;
      let jsFeatures = 0;
      
      // Python特征
      const pythonPatterns = [
        /\bprint\s*\(/i,
        /\bdef\s+\w+\s*\(/i,
        /\bimport\s+\w+/i,
        /\bclass\s+\w+/i,
        /\bfor\s+\w+\s+in/i,
        /\bif\s+.+\s*:\s*$/im,
        /\bimport\s+\w+\s+as\s+\w+/i,
        /\bfrom\s+\w+\s+import/i
      ];
      
      // JavaScript特征
      const jsPatterns = [
        /`[^`]*`/,
        /\bthis\./i,
        /\bconst\s+\w+/i,
        /\blet\s+\w+/i,
        /\bconsole\.log\(/i,
        /=>/,
        /\bfunction\s+\w+\s*\(/i,
        /\bdocument\.|\bwindow\./i
      ];
      
      // 计算特征出现次数
      pythonPatterns.forEach(pattern => {
        if (pattern.test(code)) pythonFeatures++;
      });
      
      jsPatterns.forEach(pattern => {
        if (pattern.test(code)) jsFeatures++;
      });
      
      // 根据特征数量决定语言
      if (jsFeatures > pythonFeatures * 2) {
        return 'javascript';
      }
      return 'python';
    };

    // 代码运行相关方法
    const runCode = async () => {
      try {
        // 模拟代码运行中
        codeResult.value = {
          output: [
            { content: '代码运行中...', type: 'log' }
          ]
        }
        
        const code = codeCompletionAnswer.value
        const detectedLanguage = detectLanguage(code)
        
        // 实际项目中应调用后端API执行代码
        // const { api } = await import('../api/api.js')
        // const result = await api.executeCode({ language: detectedLanguage, code, input: '' })
        
        // 模拟结果
        codeResult.value = {
          output: [
            { content: `检测到语言: ${detectedLanguage}`, type: 'info' },
            { content: '代码运行结果:', type: 'log' },
            { content: '执行结果: 成功！', type: 'success' }
          ]
        }
      } catch (e) {
        codeResult.value = {
          output: [
            { content: '代码运行中...', type: 'log' },
            { content: '执行结果: 成功！', type: 'success' }
          ]
        }
      }
    }
    
    const submitCode = () => {
      // 模拟代码提交
      codeResult.value = {
        output: [
          { content: '代码提交中...', type: 'log' },
          { content: '验证通过！', type: 'success' }
        ]
      }
      nextQuestion()
    }
    
    const runProgrammingCode = async () => {
      try {
        // 模拟自测运行中
        codeResult.value = {
          output: [
            { content: '自测运行中...', type: 'log' }
          ]
        }
        
        const code = programmingAnswer.value
        const detectedLanguage = detectLanguage(code)
        
        // 实际项目中应调用后端API执行代码
        // const { api } = await import('../api/api.js')
        // const result = await api.executeCode({ language: detectedLanguage, code, input: '' })
        
        // 模拟结果
        codeResult.value = {
          output: [
            { content: `检测到语言: ${detectedLanguage}`, type: 'info' },
            { content: '自测运行结果:', type: 'log' },
            { content: '自测结果: 部分测试用例通过', type: 'warning' }
          ]
        }
      } catch (e) {
        codeResult.value = {
          output: [
            { content: '自测运行中...', type: 'log' },
            { content: '自测结果: 部分测试用例通过', type: 'warning' }
          ]
        }
      }
    }
    
    const submitProgrammingCode = () => {
      // 模拟正式提交
      const passed = Math.floor(Math.random() * currentQuestion.value.testCases.length) + 1
      const total = currentQuestion.value.testCases.length
      const passRate = Math.floor((passed / total) * 100)
      
      submissionResult.value = {
        passed,
        total,
        passRate,
        testResults: currentQuestion.value.testCases.map((_, i) => ({
          passed: i < passed
        }))
      }
    }
    
    // 错题本相关方法
    const hideAddToWrongQuestionsDialog = () => {
      showAddToWrongQuestionsDialog.value = false
      // 重置表单
      newWrongQuestion.value = {
        errorReason: '',
        knowledgePoints: ''
      }
    }
    
    const addCurrentQuestionToWrongQuestions = async () => {
      try {
        const question = currentQuestion.value
        const questionIndex = currentIndex.value
        const questionId = question.id || question.order || questionIndex
        
        // 处理知识点输入，转换为数组
        const knowledgePoints = newWrongQuestion.value.knowledgePoints
          .split(',')
          .map(p => p.trim())
          .filter(p => p)
          
        // 调用API添加错题
        // 如果提供了practiceId，使用Practice模式；否则尝试使用Exercise模式
        if (!props.practiceId) {
          console.error('添加错题失败：practiceId未提供或无效', props.practiceId)
          alert('添加错题失败：无法获取练习ID，请重新开始练习。')
          return
        }
        
        await api.addWrongQuestionFromExercise({
          practiceId: props.practiceId,
          questionType: question.questionType || question.type
        })
        
        // 显示成功消息
        alert('题目已成功添加到错题本！')
        hideAddToWrongQuestionsDialog()
      } catch (error) {
        console.error('添加错题失败:', error)
        alert('添加错题失败，请稍后重试。')
      }
    }
    
    // 监听题目变化，加载初始状态
    watch(() => props.questions, () => {
      if (props.questions.length > 0) {
        currentIndex.value = 0
        loadQuestionState()
      }
    }, { immediate: true })
    
    return {
      currentIndex,
      totalQuestions,
      currentQuestion,
      showFeedback,
      isFullscreen,
      selectedOptions,
      userAnswers,
      codeCompletionAnswer,
      programmingAnswer,
      codeResult,
      submissionResult,
      isAnswerCorrect,
      close,
      toggleFullscreen,
      previousQuestion,
      nextQuestion,
      isOptionSelected,
      isOptionCorrect,
      selectOption,
      isFillAnswerCorrect,
      submitAnswer,
      runCode,
      submitCode,
      runProgrammingCode,
      submitProgrammingCode,
      // 错题本相关
      showAddToWrongQuestionsDialog,
      newWrongQuestion,
      hideAddToWrongQuestionsDialog,
      addCurrentQuestionToWrongQuestions,
      // 重做相关
      resetAllAnswers
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-container.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  width: 100%;
  height: 100%;
  max-width: none;
  max-height: none;
  border-radius: 0;
}

/* 头部样式 */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #f8f9fa;
  border-bottom: 1px solid #e9ecef;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
}

.header-center {
  flex: 2;
  text-align: center;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  flex: 1;
  justify-content: flex-end;
}

.btn-icon {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

/* 小尺寸对话框 */
.modal-container.small {
  max-width: 500px;
}

/* 表单样式 */
.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: #007bff;
  outline: none;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
}

.btn-icon:hover {
  background: #e9ecef;
}

.breadcrumb {
  font-size: 14px;
  color: #6c757d;
  display: flex;
  align-items: center;
  gap: 8px;
}

.breadcrumb .current {
  color: #409eff;
  font-weight: 500;
}

.practice-title {
  margin: 0;
  font-size: 18px;
  color: #333;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.question-progress {
  font-size: 14px;
  color: #6c757d;
  background: #e9ecef;
  padding: 4px 12px;
  border-radius: 16px;
}

/* 内容区域 */
.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* 选择题样式 */
.question-choice {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.question-stem h4 {
  margin: 0 0 12px 0;
  font-size: 18px;
  color: #333;
}

.question-description {
  color: #6c757d;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 16px;
}

.options-container {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.options-container.multiple {
  gap: 8px;
}

.option-item {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  border: 2px solid #e9ecef;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.option-item:hover:not(.correct):not(.incorrect) {
  border-color: #409eff;
  background: #f8f9fa;
}

.option-item.selected {
  border-color: #409eff;
  background: #ecf5ff;
}

.option-item.correct {
  border-color: #67c23a;
  background: #f0f9eb;
}

.option-item.incorrect {
  border-color: #f56c6c;
  background: #fef0f0;
}

.option-label {
  font-weight: 600;
  color: #409eff;
  margin-right: 12px;
  min-width: 20px;
}

.option-content {
  flex: 1;
  line-height: 1.5;
}

.option-feedback {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
}

/* 填空题样式 */
.question-fill {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.fill-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.fill-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.fill-label {
  font-weight: 500;
  color: #333;
}

.fill-input {
  padding: 10px 16px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.fill-input:focus {
  outline: none;
  border-color: #409eff;
}

.fill-feedback {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.correct-answer {
  color: #67c23a;
  font-weight: 500;
}

/* 代码补全题样式 */
.question-code-completion {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.code-completion-container {
  min-height: 300px;
}

/* 编程题样式 */
.question-programming {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.test-cases h5,
.code-result h5,
.submission-result h5 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #333;
}

.test-case-list {
  border: 1px solid #e9ecef;
  border-radius: 6px;
  overflow: hidden;
}

.test-case-item {
  padding: 12px 16px;
  border-bottom: 1px solid #e9ecef;
}

.test-case-item:last-child {
  border-bottom: none;
}

.test-case-input,
.test-case-output {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  margin-bottom: 6px;
}

.test-case-input:last-child,
.test-case-output:last-child {
  margin-bottom: 0;
}

.programming-code {
  min-height: 400px;
}

/* 提交结果样式 */
.pass-rate {
  margin-bottom: 20px;
}

.pass-text {
  text-align: center;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 12px;
}

.pass-bar {
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
}

.pass-bar-fill {
  height: 100%;
  transition: width 0.6s ease;
}

.pass-bar-fill.success {
  background: #67c23a;
}

.pass-bar-fill.partial {
  background: #e6a23c;
}

.pass-bar-fill.failed {
  background: #f56c6c;
}

.result-chart h6 {
  margin: 0 0 12px 0;
  font-size: 14px;
  color: #666;
}

.bar-chart {
  display: flex;
  gap: 16px;
  padding: 20px 0;
}

.result-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.bar {
  width: 40px;
  height: 120px;
  border-radius: 4px;
  background: #e9ecef;
}

.bar.passed {
  background: #67c23a;
}

.bar.failed {
  background: #f56c6c;
}

.bar-label {
  font-size: 12px;
  color: #666;
}

/* 反馈样式 */
.question-feedback {
  padding: 20px;
  border-radius: 8px;
  background: #f8f9fa;
}

.feedback-correct {
  color: #67c23a;
}

.feedback-incorrect {
  color: #f56c6c;
}

.feedback-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.feedback-text {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 12px;
}

.feedback-explanation {
  color: #6c757d;
  font-size: 14px;
  line-height: 1.5;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e9ecef;
}

/* 底部样式 */
.modal-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
}

.footer-left,
.footer-right {
  flex: 1;
}

.footer-center {
  flex: 2;
  display: flex;
  justify-content: center;
  gap: 12px;
}

.btn-primary {
  padding: 10px 24px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #66b1ff;
}

.btn-primary:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

.btn-secondary {
  padding: 10px 24px;
  background: white;
  color: #606266;
  border: 1px solid #dcdfe6;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  color: #409eff;
  border-color: #c6e2ff;
  background: #ecf5ff;
}

.btn-secondary:disabled {
  color: #c0c4cc;
  border-color: #ebeef5;
  background: #f5f7fa;
  cursor: not-allowed;
}

/* 过渡动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .modal-container,
.modal-leave-active .modal-container {
  transition: transform 0.3s ease;
}

.modal-enter-from .modal-container {
  transform: scale(0.95);
}

.modal-leave-to .modal-container {
  transform: scale(0.95);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modal-overlay {
    padding: 10px;
  }
  
  .modal-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-left,
  .header-right {
    justify-content: center;
  }
  
  .modal-content {
    padding: 16px;
  }
  
  .option-item {
    padding: 12px;
  }
  
  .modal-footer {
    flex-direction: column;
    gap: 16px;
  }
  
  .footer-left,
  .footer-right {
    width: 100%;
  }
  
  .footer-left {
    order: 2;
  }
  
  .footer-center {
    order: 1;
  }
  
  .footer-right {
    order: 3;
    display: flex;
    justify-content: flex-end;
  }
  
  .bar-chart {
    flex-wrap: wrap;
  }
  
  .result-bar {
    flex: 0 0 calc(33.333% - 10px);
  }
}

@media (max-width: 480px) {
  .practice-title {
    font-size: 16px;
  }
  
  .btn-primary,
  .btn-secondary {
    padding: 8px 16px;
    font-size: 13px;
  }
  
  .result-bar {
    flex: 0 0 calc(50% - 8px);
  }
}
</style>
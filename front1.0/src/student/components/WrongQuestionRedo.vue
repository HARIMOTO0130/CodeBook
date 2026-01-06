<template>
  <div class="wrong-question-redo">
    <div class="redo-header">
      <h3>重做错题</h3>
      <div class="redo-info">
        <span>第 {{ question.attempt_count || 1 }} 次尝试</span>
      </div>
    </div>

    <div class="redo-content" v-if="questionContent">
      <!-- 题目显示 -->
      <div class="question-display">
        <h4>{{ questionContent.title || questionContent.question || question.title }}</h4>
        
        <!-- 选择题 -->
        <div v-if="questionContent.type === 'choice'" class="question-choice">
          <div class="options-list">
            <label 
              v-for="(option, idx) in questionContent.options" 
              :key="idx"
              class="option-label"
              :class="{ 'selected': selectedAnswer === idx }"
            >
              <input 
                type="radio" 
                :name="`redo-option-${question.id}`"
                :value="idx"
                v-model="selectedAnswer"
              />
              <span class="option-text">{{ option.content || option.text }}</span>
            </label>
          </div>
        </div>

        <!-- 判断题 -->
        <div v-else-if="questionContent.type === 'judgment' || (questionContent.type === 'choice' && questionContent.options.length === 2)" class="question-judgment">
          <div class="judgment-options">
            <label 
              v-for="(option, idx) in questionContent.options" 
              :key="idx"
              class="judgment-label"
              :class="{ 'selected': selectedAnswer === idx }"
            >
              <input 
                type="radio" 
                :name="`redo-judgment-${question.id}`"
                :value="idx"
                v-model="selectedAnswer"
              />
              <span class="judgment-text">{{ option.content || option.text }}</span>
            </label>
          </div>
        </div>

        <!-- 填空题 -->
        <div v-else-if="questionContent.type === 'fill'" class="question-fill">
          <div 
            v-for="(blank, idx) in questionContent.blanks" 
            :key="idx"
            class="fill-item"
          >
            <label class="fill-label">{{ blank.prompt || `空位 ${idx + 1}` }}：</label>
            <input 
              type="text" 
              v-model="fillAnswers[idx]"
              :placeholder="blank.placeholder || '请输入答案'"
              class="fill-input"
            />
          </div>
        </div>

        <!-- 代码补全/编程题 -->
        <div v-else-if="['code_completion', 'programming'].includes(questionContent.type)" class="question-code">
          <div class="code-editor-container">
            <textarea 
              v-model="codeAnswer"
              :placeholder="questionContent.code_template || '请在此处编写代码'"
              class="code-editor"
              rows="15"
            ></textarea>
          </div>
        </div>
      </div>
    </div>

    <div class="redo-actions">
      <button 
        class="btn btn-primary" 
        @click="submitAnswer"
        :disabled="!canSubmit"
      >
        ✓ 提交答案
      </button>
      <button class="btn btn-secondary" @click="$emit('cancel')">
        取消
      </button>
    </div>

    <!-- 结果显示 -->
    <div v-if="showResult" class="result-display">
      <div class="result-content" :class="resultClass">
        <div class="result-icon">{{ resultIcon }}</div>
        <div class="result-message">{{ resultMessage }}</div>
        <div v-if="resultExplanation" class="result-explanation">
          {{ resultExplanation }}
        </div>
      </div>
      <div class="result-actions">
        <button 
          class="btn btn-primary" 
          @click="handleComplete"
        >
          {{ isCorrect ? '完成' : '继续练习' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { api } from '../api/api.js'

export default {
  name: 'WrongQuestionRedo',
  props: {
    question: {
      type: Object,
      required: true
    }
  },
  emits: ['complete', 'cancel'],
  setup(props, { emit }) {
    const questionContent = ref(props.question.question_content || props.question)
    const selectedAnswer = ref(null)
    const fillAnswers = ref([])
    const codeAnswer = ref(questionContent.value.code_template || '')
    const showResult = ref(false)
    const isCorrect = ref(false)
    const resultExplanation = ref('')

    // 初始化填空题答案数组
    if (questionContent.value.type === 'fill' && questionContent.value.blanks) {
      fillAnswers.value = new Array(questionContent.value.blanks.length).fill('')
    }

    const canSubmit = computed(() => {
      if (questionContent.value.type === 'choice' || questionContent.value.type === 'judgment') {
        return selectedAnswer.value !== null
      } else if (questionContent.value.type === 'fill') {
        return fillAnswers.value.every(answer => answer.trim() !== '')
      } else if (['code_completion', 'programming'].includes(questionContent.value.type)) {
        return codeAnswer.value.trim() !== ''
      }
      return false
    })

    const resultClass = computed(() => {
      return isCorrect.value ? 'result-correct' : 'result-incorrect'
    })

    const resultIcon = computed(() => {
      return isCorrect.value ? '✓' : '✗'
    })

    const resultMessage = computed(() => {
      return isCorrect.value 
        ? '恭喜！您答对了！' 
        : '很遗憾，答案不正确。继续加油！'
    })

    const checkAnswer = () => {
      if (questionContent.value.type === 'choice' || questionContent.value.type === 'judgment') {
        // 检查选择题/判断题
        const selectedOption = questionContent.value.options[selectedAnswer.value]
        isCorrect.value = selectedOption && selectedOption.is_correct === true
      } else if (questionContent.value.type === 'fill') {
        // 检查填空题
        const allCorrect = questionContent.value.blanks.every((blank, idx) => {
          const userAnswer = fillAnswers.value[idx].trim().toLowerCase()
          const correctAnswer = (blank.correct_answer || '').trim().toLowerCase()
          return userAnswer === correctAnswer
        })
        isCorrect.value = allCorrect
      } else if (['code_completion', 'programming'].includes(questionContent.value.type)) {
        // 代码题需要后端验证，这里先简单检查是否填写
        // 实际应该调用后端API进行代码执行和测试
        isCorrect.value = codeAnswer.value.trim() !== ''
        resultExplanation.value = '代码题需要执行测试用例验证，请提交后查看结果。'
      }
    }

    const submitAnswer = () => {
      checkAnswer()
      showResult.value = true
    }

    const handleComplete = async () => {
      try {
        await api.completeWrongQuestionRedo(props.question.id, isCorrect.value)
        emit('complete', props.question.id, isCorrect.value)
      } catch (error) {
        console.error('完成重做失败:', error)
        // 即使API失败，也触发完成事件
        emit('complete', props.question.id, isCorrect.value)
      }
    }

    return {
      questionContent,
      selectedAnswer,
      fillAnswers,
      codeAnswer,
      showResult,
      isCorrect,
      resultExplanation,
      canSubmit,
      resultClass,
      resultIcon,
      resultMessage,
      submitAnswer,
      handleComplete
    }
  }
}
</script>

<style scoped>
.wrong-question-redo {
  max-width: 100%;
}

.redo-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e0e0e0;
}

.redo-header h3 {
  margin: 0;
  color: #333;
}

.redo-info {
  color: #666;
  font-size: 14px;
}

.redo-content {
  margin-bottom: 20px;
}

.question-display {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}

.question-display h4 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  line-height: 1.6;
}

/* 选择题样式 */
.options-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-label {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.option-label:hover {
  border-color: #409EFF;
  background: #F0F9FF;
}

.option-label.selected {
  border-color: #409EFF;
  background: #E1F3FF;
}

.option-label input[type="radio"] {
  cursor: pointer;
}

.option-text {
  flex: 1;
  color: #333;
}

/* 判断题样式 */
.judgment-options {
  display: flex;
  gap: 20px;
}

.judgment-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 15px 25px;
  background: white;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  flex: 1;
  justify-content: center;
}

.judgment-label:hover {
  border-color: #409EFF;
  background: #F0F9FF;
}

.judgment-label.selected {
  border-color: #409EFF;
  background: #E1F3FF;
}

.judgment-text {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

/* 填空题样式 */
.fill-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 15px;
}

.fill-label {
  min-width: 120px;
  font-weight: 500;
  color: #666;
}

.fill-input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.fill-input:focus {
  outline: none;
  border-color: #409EFF;
}

/* 代码编辑器样式 */
.code-editor-container {
  margin-top: 15px;
}

.code-editor {
  width: 100%;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
}

.code-editor:focus {
  outline: none;
  border-color: #409EFF;
}

.redo-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

/* 结果显示 */
.result-display {
  margin-top: 20px;
  padding: 20px;
  border-radius: 8px;
}

.result-content {
  text-align: center;
  padding: 30px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.result-content.result-correct {
  background: #F0F9FF;
  border: 2px solid #67C23A;
}

.result-content.result-incorrect {
  background: #FEF0F0;
  border: 2px solid #F56C6C;
}

.result-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.result-content.result-correct .result-icon {
  color: #67C23A;
}

.result-content.result-incorrect .result-icon {
  color: #F56C6C;
}

.result-message {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 10px;
}

.result-content.result-correct .result-message {
  color: #67C23A;
}

.result-content.result-incorrect .result-message {
  color: #F56C6C;
}

.result-explanation {
  font-size: 14px;
  color: #666;
  margin-top: 10px;
}

.result-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-primary {
  background: #409EFF;
  color: white;
}

.btn-primary:hover {
  background: #66b1ff;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #909399;
  color: white;
}

.btn-secondary:hover {
  background: #a6a9ad;
}
</style>


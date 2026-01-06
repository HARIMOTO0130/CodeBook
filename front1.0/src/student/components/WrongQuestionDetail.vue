<template>
  <div class="wrong-question-detail">
    <div class="detail-header">
      <div class="question-title-section">
        <h3>{{ question.title }}</h3>
        <div class="question-badges">
          <span class="badge badge-type">{{ question.question_type_display || question.question_type }}</span>
          <span class="badge badge-difficulty">{{ getDifficultyStars(question.difficulty) }}</span>
          <span class="badge badge-status" :class="`status-${question.status}`">
            {{ question.status_display || getStatusDisplay(question.status) }}
          </span>
        </div>
      </div>
    </div>

    <div class="detail-content">
      <!-- 题目信息 -->
      <div class="info-section">
        <h4>题目信息</h4>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">来源：</span>
            <span v-if="question.book_title">{{ question.book_title }}</span>
            <span v-if="question.chapter_title"> - {{ question.chapter_title }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">错误时间：</span>
            <span>{{ formatTime(question.error_time) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">最后尝试：</span>
            <span>{{ formatTime(question.attempt_time || question.attemptTime) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">尝试次数：</span>
            <span>{{ question.attempt_count || 1 }} 次</span>
          </div>
        </div>
      </div>

      <!-- 错误原因 -->
      <div v-if="question.error_reason" class="info-section">
        <h4>错误原因</h4>
        <div class="error-reason-box">
          <p>{{ question.error_reason }}</p>
        </div>
      </div>

      <!-- 关联知识点 -->
      <div v-if="question.knowledge_points && question.knowledge_points.length > 0" class="info-section">
        <h4>关联知识点</h4>
        <div class="knowledge-points-box">
          <span 
            v-for="(point, idx) in question.knowledge_points" 
            :key="idx"
            class="knowledge-point-tag"
          >
            {{ point }}
          </span>
        </div>
      </div>

      <!-- 题目内容 -->
      <div v-if="questionContent" class="info-section">
        <h4>题目内容</h4>
        <div class="question-content-box">
          <div v-if="questionContent.question" class="question-text">
            <p>{{ questionContent.question }}</p>
          </div>
          
          <!-- 选择题选项 -->
          <div v-if="questionContent.type === 'choice' && questionContent.options" class="question-options">
            <div 
              v-for="(option, idx) in questionContent.options" 
              :key="idx"
              class="option-item"
              :class="{ 'correct': option.is_correct }"
            >
              <span class="option-label">{{ String.fromCharCode(65 + idx) }}.</span>
              <span class="option-content">{{ option.content || option.text }}</span>
              <span v-if="option.is_correct" class="correct-badge">✓ 正确答案</span>
            </div>
          </div>

          <!-- 填空题空位 -->
          <div v-if="questionContent.type === 'fill' && questionContent.blanks" class="question-blanks">
            <div 
              v-for="(blank, idx) in questionContent.blanks" 
              :key="idx"
              class="blank-item"
            >
              <span class="blank-label">空位 {{ idx + 1 }}：</span>
              <span class="blank-prompt">{{ blank.prompt }}</span>
              <span class="blank-answer">正确答案：{{ blank.correct_answer }}</span>
            </div>
          </div>

          <!-- 代码模板 -->
          <div v-if="questionContent.code_template" class="question-code">
            <pre><code>{{ questionContent.code_template }}</code></pre>
          </div>
        </div>
      </div>
    </div>

    <div class="detail-actions">
      <button class="btn btn-primary" @click="handleRedo">🔄 开始重做</button>
      <button class="btn btn-secondary" @click="$emit('close')">关闭</button>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'

export default {
  name: 'WrongQuestionDetail',
  props: {
    question: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'redo'],
  setup(props, { emit }) {
    const questionContent = computed(() => {
      return props.question.question_content || props.question
    })

    const handleRedo = () => {
      emit('redo', props.question)
    }

    const formatTime = (timeStr) => {
      if (!timeStr) return '未知'
      const date = new Date(timeStr)
      return date.toLocaleString('zh-CN')
    }

    const getDifficultyStars = (difficulty) => {
      return '★'.repeat(difficulty || 1)
    }

    const getStatusDisplay = (status) => {
      const map = {
        'unresolved': '未解决',
        'redoing': '重做中',
        'resolved': '已解决'
      }
      return map[status] || status
    }

    return {
      questionContent,
      handleRedo,
      formatTime,
      getDifficultyStars,
      getStatusDisplay
    }
  }
}
</script>

<style scoped>
.wrong-question-detail {
  max-width: 100%;
}

.detail-header {
  margin-bottom: 20px;
}

.question-title-section h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 20px;
}

.question-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.badge-type {
  background: #E1F3FF;
  color: #409EFF;
}

.badge-difficulty {
  background: #FFF4E6;
  color: #E6A23C;
}

.badge-status {
  background: #F0F0F0;
  color: #666;
}

.badge-status.status-unresolved {
  background: #FEE;
  color: #F56C6C;
}

.badge-status.status-redoing {
  background: #FEF4E6;
  color: #E6A23C;
}

.badge-status.status-resolved {
  background: #F0F9FF;
  color: #67C23A;
}

.detail-content {
  margin-bottom: 20px;
}

.info-section {
  margin-bottom: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.info-section h4 {
  margin: 0 0 12px 0;
  color: #333;
  font-size: 16px;
  border-bottom: 2px solid #409EFF;
  padding-bottom: 8px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.info-label {
  font-weight: 500;
  color: #666;
}

.error-reason-box {
  padding: 12px;
  background: #FEF0F0;
  border-left: 3px solid #F56C6C;
  border-radius: 4px;
}

.error-reason-box p {
  margin: 0;
  color: #666;
  line-height: 1.6;
}

.knowledge-points-box {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.knowledge-point-tag {
  padding: 6px 12px;
  background: #E1F3FF;
  color: #409EFF;
  border-radius: 16px;
  font-size: 13px;
}

.question-content-box {
  background: white;
  padding: 15px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.question-text {
  margin-bottom: 15px;
}

.question-text p {
  margin: 0;
  line-height: 1.6;
  color: #333;
}

.question-options {
  margin-top: 15px;
}

.option-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  margin-bottom: 8px;
  background: #f5f5f5;
  border-radius: 4px;
  border-left: 3px solid transparent;
}

.option-item.correct {
  background: #F0F9FF;
  border-left-color: #67C23A;
}

.option-label {
  font-weight: bold;
  color: #409EFF;
  min-width: 24px;
}

.option-content {
  flex: 1;
  color: #333;
}

.correct-badge {
  padding: 2px 8px;
  background: #67C23A;
  color: white;
  border-radius: 12px;
  font-size: 11px;
}

.question-blanks {
  margin-top: 15px;
}

.blank-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  margin-bottom: 8px;
  background: #f5f5f5;
  border-radius: 4px;
}

.blank-label {
  font-weight: bold;
  color: #409EFF;
  min-width: 60px;
}

.blank-prompt {
  flex: 1;
  color: #333;
}

.blank-answer {
  padding: 4px 8px;
  background: #E1F3FF;
  color: #409EFF;
  border-radius: 4px;
  font-size: 12px;
}

.question-code {
  margin-top: 15px;
}

.question-code pre {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0;
}

.question-code code {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  color: #333;
}

.detail-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
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

.btn-secondary {
  background: #909399;
  color: white;
}

.btn-secondary:hover {
  background: #a6a9ad;
}
</style>


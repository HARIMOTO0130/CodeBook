<template>
  <div class="exercise-generator-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>自动习题生成</h1>
      <p>基于知识点智能生成习题，助力个性化学习</p>
    </div>

    <!-- 功能导航 -->
    <div class="feature-nav">
      <div class="nav-item" :class="{ active: activeFeature === 'generator' }" @click="activeFeature = 'generator'">
        <span class="nav-icon">📝</span>
        <span class="nav-label">习题生成</span>
      </div>
      <div class="nav-item" :class="{ active: activeFeature === 'recommend' }" @click="activeFeature = 'recommend'">
        <span class="nav-icon">🎯</span>
        <span class="nav-label">推荐习题</span>
      </div>
      <div class="nav-item" :class="{ active: activeFeature === 'history' }" @click="activeFeature = 'history'">
        <span class="nav-icon">📊</span>
        <span class="nav-label">生成历史</span>
      </div>
    </div>

    <!-- 功能内容区域 -->
    <div class="feature-content">
      <!-- 习题生成功能 -->
      <div v-if="activeFeature === 'generator'" class="feature-panel">
        <ExerciseGeneratorComponent ref="exerciseGeneratorComponent" />
      </div>

      <!-- 推荐习题功能 -->
      <div v-if="activeFeature === 'recommend'" class="feature-panel">
        <div class="recommend-section">
          <div class="section-header">
            <h3>个性化推荐习题</h3>
            <div class="recommend-controls">
              <div class="count-selector">
                <label for="recommend-count">推荐数量:</label>
                <div class="number-input">
                  <button @click="recommendCount = Math.max(1, recommendCount - 1)" class="btn btn-sm">-</button>
                  <input 
                    type="number" 
                    v-model.number="recommendCount"
                    min="1"
                    max="10"
                    class="input"
                  >
                  <button @click="recommendCount = Math.min(10, recommendCount + 1)" class="btn btn-sm">+</button>
                </div>
              </div>
              <button @click="loadRecommendedExercises" :disabled="isLoadingRecommend" class="btn btn-primary">
                {{ isLoadingRecommend ? '加载中...' : '获取推荐' }}
              </button>
            </div>
          </div>

          <div v-if="isLoadingRecommend" class="loading-state">
            <div class="loading-spinner"></div>
            <p>正在加载推荐习题...</p>
          </div>

          <div v-else-if="recommendedExercises.length === 0" class="empty-state">
            <p>暂无推荐习题</p>
            <p class="empty-hint">点击"获取推荐"按钮获取个性化习题推荐</p>
          </div>

          <div v-else class="exercises-list">
            <div 
              v-for="(exercise, index) in recommendedExercises" 
              :key="exercise.id || index"
              class="exercise-card"
            >
              <div class="exercise-header">
                <div class="exercise-meta">
                  <span class="exercise-type">{{ exercise.type_name }}</span>
                  <span class="exercise-difficulty" :class="`difficulty-${exercise.difficulty}`">
                    {{ exercise.difficulty_name }}
                  </span>
                  <span class="exercise-time">
                    ⏱ {{ exercise.estimated_time }} 分钟
                  </span>
                </div>
                <div class="exercise-actions">
                  <button @click="previewExercise(exercise)" class="btn btn-sm btn-primary">
                    预览
                  </button>
                </div>
              </div>
              
              <div class="exercise-content">
                <p class="exercise-question">{{ exercise.question }}</p>
                
                <!-- 选择题选项 -->
                <div v-if="exercise.exercise_type === 'multiple_choice' && exercise.options" class="exercise-options">
                  <div 
                    v-for="(option, optIndex) in exercise.options" 
                    :key="optIndex"
                    class="option"
                  >
                    <span class="option-label">{{ String.fromCharCode(65 + optIndex) }}.</span>
                    <span class="option-text">{{ option }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 生成历史功能 -->
      <div v-if="activeFeature === 'history'" class="feature-panel">
        <div class="history-section">
          <div class="section-header">
            <h3>生成历史记录</h3>
            <div class="history-controls">
              <button @click="refreshHistory" class="btn btn-secondary">刷新</button>
            </div>
          </div>

          <div v-if="loadingHistory" class="loading-state">
            <div class="loading-spinner"></div>
            <p>加载历史记录中...</p>
          </div>

          <div v-else-if="historyRecords.length === 0" class="empty-state">
            <p>暂无生成记录</p>
            <p class="empty-hint">开始使用习题生成功能来创建记录</p>
          </div>

          <div v-else class="history-list">
            <div v-for="record in historyRecords" :key="record.id" class="history-item">
              <div class="history-info">
                <div class="history-type">
                  <span class="type-icon">{{ getTypeIcon(record.interaction_type) }}</span>
                  <span class="type-name">{{ getTypeName(record.interaction_type) }}</span>
                </div>
                <div class="history-details">
                  <div class="history-knowledge">
                    <span class="knowledge-label">知识点:</span>
                    <span class="knowledge-list">{{ record.knowledge_points.join(', ') }}</span>
                  </div>
                  <div class="history-meta">
                    <span class="history-time">{{ formatTime(record.created_at) }}</span>
                    <span class="history-count">生成 {{ record.generated_count }} 道</span>
                  </div>
                </div>
              </div>
              <div class="history-actions">
                <span class="history-status" :class="record.generated_count > 0 ? 'success' : 'failed'">
                  {{ record.generated_count > 0 ? '成功' : '失败' }}
                </span>
              </div>
            </div>
          </div>

          <!-- 分页控件 -->
          <div v-if="historyRecords.length > 0" class="pagination">
            <button 
              @click="loadPreviousPage" 
              :disabled="currentPage === 1"
              class="btn btn-secondary"
            >
              上一页
            </button>
            <span class="page-info">第 {{ currentPage }} 页 / 共 {{ totalPages }} 页</span>
            <button 
              @click="loadNextPage" 
              :disabled="currentPage >= totalPages"
              class="btn btn-secondary"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 习题预览模态框 -->
    <div v-if="showPreview" class="modal-overlay" @click="closePreview">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>习题预览</h3>
          <button @click="closePreview" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <div v-if="previewExerciseData" class="preview-content">
            <div class="preview-header">
              <span class="preview-type">{{ previewExerciseData.type_name }}</span>
              <span class="preview-difficulty" :class="`difficulty-${previewExerciseData.difficulty}`">
                {{ previewExerciseData.difficulty_name }}
              </span>
            </div>
            
            <div class="preview-question">
              <h4>题目</h4>
              <p>{{ previewExerciseData.question }}</p>
            </div>
            
            <!-- 选项 -->
            <div v-if="previewExerciseData.exercise_type === 'multiple_choice' && previewExerciseData.options" class="preview-options">
              <h4>选项</h4>
              <div 
                v-for="(option, index) in previewExerciseData.options" 
                :key="index"
                class="preview-option"
                :class="{ correct: option === previewExerciseData.correct_answer }"
              >
                <span class="option-label">{{ String.fromCharCode(65 + index) }}.</span>
                <span class="option-text">{{ option }}</span>
              </div>
            </div>
            
            <!-- 答案和解析 -->
            <div class="preview-answer">
              <h4>答案</h4>
              <div v-if="previewExerciseData.correct_answer" class="answer-content">
                {{ previewExerciseData.correct_answer }}
              </div>
              <div v-else-if="previewExerciseData.correct_answers" class="answer-content">
                {{ previewExerciseData.correct_answers.join('，') }}
              </div>
            </div>
            
            <div class="preview-explanation">
              <h4>解析</h4>
              <p>{{ previewExerciseData.explanation }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import ExerciseGeneratorComponent from '../components/ExerciseGeneratorComponent.vue'
import { exerciseGeneratorAPI, exerciseGeneratorUtils } from '../api/exercise_generator_api'

export default {
  name: 'ExerciseGeneratorView',
  
  components: {
    ExerciseGeneratorComponent
  },

  data() {
    return {
      activeFeature: 'generator',
      recommendedExercises: [],
      historyRecords: [],
      isLoadingRecommend: false,
      loadingHistory: false,
      showPreview: false,
      previewExerciseData: null,
      recommendCount: 5,
      currentPage: 1,
      pageSize: 10,
      totalCount: 0
    }
  },

  computed: {
    totalPages() {
      return Math.ceil(this.totalCount / this.pageSize)
    }
  },

  methods: {
    getTypeIcon(type) {
      const icons = {
        'exercise_generation': '📝',
        'exercise_set_generation': '📋'
      }
      return icons[type] || '📄'
    },

    getTypeName(type) {
      const names = {
        'exercise_generation': '单类型习题',
        'exercise_set_generation': '习题集'
      }
      return names[type] || type
    },

    formatTime(timestamp) {
      return new Date(timestamp).toLocaleString('zh-CN')
    },

    async loadRecommendedExercises() {
      this.isLoadingRecommend = true
      
      try {
        const result = await exerciseGeneratorAPI.getRecommendedExercises(this.recommendCount)
        if (result.result && result.result.exercises) {
          this.recommendedExercises = exerciseGeneratorUtils.formatExercises(result.result.exercises)
        }
      } catch (error) {
        console.error('获取推荐习题失败:', error)
        alert('获取推荐习题失败，请稍后重试')
      } finally {
        this.isLoadingRecommend = false
      }
    },

    async loadHistory() {
      this.loadingHistory = true
      
      try {
        const offset = (this.currentPage - 1) * this.pageSize
        const response = await exerciseGeneratorAPI.getExerciseHistory(this.pageSize, offset)
        this.historyRecords = response.history || []
        this.totalCount = response.total_count || 0
      } catch (error) {
        console.error('加载历史记录失败:', error)
        this.historyRecords = []
      } finally {
        this.loadingHistory = false
      }
    },

    refreshHistory() {
      this.currentPage = 1
      this.loadHistory()
    },

    loadPreviousPage() {
      if (this.currentPage > 1) {
        this.currentPage--
        this.loadHistory()
      }
    },

    loadNextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++
        this.loadHistory()
      }
    },

    previewExercise(exercise) {
      this.previewExerciseData = exercise
      this.showPreview = true
    },

    closePreview() {
      this.showPreview = false
      this.previewExerciseData = null
    }
  },

  watch: {
    activeFeature(newFeature) {
      if (newFeature === 'history' && this.historyRecords.length === 0) {
        this.loadHistory()
      }
    }
  },

  mounted() {
    // 页面加载时初始化数据
    this.loadHistory()
  }
}
</script>

<style scoped>
.exercise-generator-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h1 {
  color: #2d3748;
  margin-bottom: 10px;
  font-size: 2.5rem;
}

.page-header p {
  color: #718096;
  font-size: 1.1rem;
}

.feature-nav {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
  background: white;
  border-radius: 8px;
  padding: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 15px 30px;
  cursor: pointer;
  border-radius: 6px;
  transition: all 0.3s;
  min-width: 120px;
}

.nav-item:hover {
  background: #f7fafc;
}

.nav-item.active {
  background: #4299e1;
  color: white;
}

.nav-icon {
  font-size: 24px;
  margin-bottom: 5px;
}

.nav-label {
  font-size: 14px;
  font-weight: bold;
}

.feature-content {
  min-height: 500px;
}

.feature-panel {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e2e8f0;
}

.section-header h3 {
  margin: 0;
  color: #2d3748;
}

.recommend-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

.count-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.number-input {
  display: flex;
  align-items: center;
  gap: 5px;
}

.number-input .input {
  width: 60px;
  text-align: center;
  padding: 4px 8px;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  font-size: 14px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn-primary {
  background: #4299e1;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #3182ce;
}

.btn-primary:disabled {
  background: #a0aec0;
  cursor: not-allowed;
}

.btn-secondary {
  background: #e2e8f0;
  color: #4a5568;
}

.btn-secondary:hover {
  background: #cbd5e0;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.loading-state, .empty-state {
  text-align: center;
  padding: 40px;
  color: #718096;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 15px;
}

.empty-hint {
  font-size: 14px;
  opacity: 0.7;
}

.exercises-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.exercise-card {
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 15px;
  transition: all 0.2s;
}

.exercise-card:hover {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.exercise-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #f7fafc;
}

.exercise-meta {
  display: flex;
  gap: 10px;
  align-items: center;
}

.exercise-type {
  background: #4299e1;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.exercise-difficulty {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.difficulty-easy {
  background: #38a169;
  color: white;
}

.difficulty-medium {
  background: #ed8936;
  color: white;
}

.difficulty-hard {
  background: #e53e3e;
  color: white;
}

.exercise-time {
  font-size: 12px;
  color: #718096;
}

.exercise-question {
  margin: 10px 0;
  line-height: 1.5;
  color: #2d3748;
}

.exercise-options {
  margin: 10px 0;
}

.option {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
  padding: 8px;
  border-radius: 4px;
  background: #f7fafc;
}

.option-label {
  font-weight: bold;
  min-width: 20px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 15px;
  background: #f7fafc;
  border-radius: 6px;
}

.history-info {
  flex: 1;
  margin-right: 15px;
}

.history-type {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  font-weight: bold;
  color: #2d3748;
}

.history-details {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 14px;
}

.history-knowledge {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.knowledge-label {
  color: #718096;
  margin-right: 5px;
}

.knowledge-list {
  color: #2d3748;
}

.history-meta {
  display: flex;
  gap: 15px;
  color: #718096;
  font-size: 12px;
}

.history-status {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.history-status.success {
  background: #38a169;
  color: white;
}

.history-status.failed {
  background: #e53e3e;
  color: white;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 20px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e2e8f0;
}

.page-info {
  color: #718096;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 80vh;
  overflow: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #718096;
}

.modal-body {
  padding: 20px;
}

.preview-content {
  line-height: 1.6;
}

.preview-header {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.preview-type {
  background: #4299e1;
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.preview-difficulty {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.preview-question {
  margin-bottom: 20px;
}

.preview-question h4 {
  margin-bottom: 10px;
  color: #2d3748;
}

.preview-options {
  margin-bottom: 20px;
}

.preview-options h4 {
  margin-bottom: 10px;
  color: #2d3748;
}

.preview-option {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 8px;
  padding: 8px;
  border-radius: 4px;
  background: #f7fafc;
}

.preview-option.correct {
  background: #c6f6d5;
  border: 1px solid #68d391;
}

.preview-answer {
  margin-bottom: 20px;
  padding: 15px;
  background: #ebf8ff;
  border-radius: 4px;
}

.preview-answer h4 {
  margin-bottom: 10px;
  color: #2d3748;
}

.answer-content {
  font-family: 'Courier New', monospace;
  white-space: pre-wrap;
}

.preview-explanation {
  padding: 15px;
  background: #f7fafc;
  border-radius: 4px;
}

.preview-explanation h4 {
  margin-bottom: 10px;
  color: #2d3748;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .exercise-generator-view {
    padding: 10px;
  }
  
  .feature-nav {
    flex-direction: column;
  }
  
  .nav-item {
    flex-direction: row;
    justify-content: center;
    gap: 10px;
  }
  
  .recommend-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .count-selector {
    justify-content: space-between;
  }
  
  .history-item {
    flex-direction: column;
    gap: 10px;
  }
  
  .history-actions {
    align-self: flex-start;
  }
}
</style>
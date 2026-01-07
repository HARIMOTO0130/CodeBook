<template>
  <div class="wrong-questions-view">
    <div class="view-header">
      <h2>我的错题本</h2>
      <div class="header-actions">
        <button class="btn btn-primary" @click="refreshData" :disabled="loading">
          <span v-if="loading">刷新中...</span>
          <span v-else>🔄 刷新</span>
        </button>
      </div>
    </div>

    <!-- 统计信息 -->
    <div v-if="statistics" class="statistics-section">
      <div class="stat-card">
        <div class="stat-value">{{ statistics.total || 0 }}</div>
        <div class="stat-label">总错题数</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.by_status?.unresolved || 0 }}</div>
        <div class="stat-label">未解决</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.by_status?.redoing || 0 }}</div>
        <div class="stat-label">重做中</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ statistics.by_status?.resolved || 0 }}</div>
        <div class="stat-label">已解决</div>
      </div>
    </div>

    <!-- 筛选器 -->
    <div class="filters-section">
      <div class="filter-group">
        <label>状态筛选：</label>
        <select v-model="filters.status" @change="applyFilters" class="filter-select">
          <option value="">全部</option>
          <option value="unresolved">未解决</option>
          <option value="redoing">重做中</option>
          <option value="resolved">已解决</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>题目类型：</label>
        <select v-model="filters.question_type" @change="applyFilters" class="filter-select">
          <option value="">全部</option>
          <option value="choice">选择题</option>
          <option value="judgment">判断题</option>
          <option value="fill">填空题</option>
          <option value="code_completion">代码补全</option>
          <option value="programming">编程题</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>难度：</label>
        <select v-model="filters.difficulty" @change="applyFilters" class="filter-select">
          <option value="">全部</option>
          <option value="1">★ 简单</option>
          <option value="2">★★ 中等</option>
          <option value="3">★★★ 困难</option>
          <option value="4">★★★★ 较难</option>
          <option value="5">★★★★★ 很难</option>
        </select>
      </div>
      
      <div class="filter-group">
        <button class="btn btn-secondary btn-sm" @click="clearFilters">清除筛选</button>
      </div>
    </div>

    <!-- 知识点筛选标签 -->
    <div v-if="availableKnowledgePoints.length > 0" class="knowledge-filters">
      <span class="filter-label">知识点：</span>
      <span 
        v-for="(point, index) in availableKnowledgePoints" 
        :key="index"
        class="knowledge-tag"
        :class="{ active: selectedKnowledgePoints.includes(point) }"
        @click="toggleKnowledgePoint(point)"
      >
        {{ point }}
      </span>
    </div>

    <!-- 错题列表 -->
    <div class="questions-section">
      <div v-if="loading" class="loading-state">
        <p>加载错题中...</p>
      </div>
      
      <div v-else-if="filteredQuestions.length === 0" class="no-data">
        <p>暂无错题记录</p>
        <p class="hint">继续学习并完成练习题，错题会自动添加到这里</p>
      </div>
      
      <div v-else class="questions-list">
        <div 
          v-for="question in filteredQuestions" 
          :key="question.id"
          class="question-card"
          :class="`status-${question.status}`"
        >
          <div class="question-header">
            <div class="question-title-row">
              <h3 class="question-title">{{ question.title }}</h3>
              <div class="question-badges">
                <span class="badge badge-type">{{ question.question_type_display || question.question_type }}</span>
                <span class="badge badge-difficulty">{{ getDifficultyStars(question.difficulty) }}</span>
                <span class="badge badge-status" :class="`status-${question.status}`">
                  {{ question.status_display || getStatusDisplay(question.status) }}
                </span>
              </div>
            </div>
            <div class="question-meta">
              <span class="meta-item">
                <span class="meta-label">来源：</span>
                <span v-if="question.book_title">{{ question.book_title }}</span>
                <span v-if="question.chapter_title"> - {{ question.chapter_title }}</span>
              </span>
              <span class="meta-item">
                <span class="meta-label">错误时间：</span>
                {{ formatTime(question.error_time) }}
              </span>
              <span class="meta-item">
                <span class="meta-label">尝试次数：</span>
                {{ question.attempt_count || 1 }} 次
              </span>
            </div>
          </div>
          
          <div v-if="question.error_reason" class="question-error-reason">
            <strong>错误原因：</strong>
            <p>{{ question.error_reason }}</p>
          </div>
          
          <div v-if="question.knowledge_points && question.knowledge_points.length > 0" class="question-knowledge-points">
            <strong>关联知识点：</strong>
            <span 
              v-for="(point, idx) in question.knowledge_points" 
              :key="idx"
              class="knowledge-point-tag"
            >
              {{ point }}
            </span>
          </div>
          
          <div class="question-actions">
            <button 
              class="btn btn-primary btn-sm" 
              @click="viewQuestionDetail(question)"
            >
              📖 查看详情
            </button>
            <button 
              class="btn btn-success btn-sm" 
              @click="startRedo(question)"
              :disabled="question.status === 'resolved'"
            >
              🔄 开始重做
            </button>
            <button 
              class="btn btn-secondary btn-sm" 
              @click="toggleStatus(question)"
            >
              {{ getStatusActionText(question.status) }}
            </button>
            <button 
              class="btn btn-danger btn-sm" 
              @click="deleteQuestion(question.id)"
            >
              🗑️ 删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 错题详情对话框 -->
    <div v-if="showDetailDialog" class="modal-overlay" @click="closeDetailDialog">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>错题详情</h3>
          <button class="btn-close" @click="closeDetailDialog">×</button>
        </div>
        <div class="modal-body" v-if="selectedQuestion">
          <WrongQuestionDetail :question="selectedQuestion" @close="closeDetailDialog" @redo="handleRedoFromDetail" />
        </div>
      </div>
    </div>

    <!-- 重做对话框 -->
    <div v-if="showRedoDialog" class="modal-overlay" @click="closeRedoDialog">
      <div class="modal-content modal-large" @click.stop>
        <div class="modal-header">
          <h3>重做错题</h3>
          <button class="btn-close" @click="closeRedoDialog">×</button>
        </div>
        <div class="modal-body" v-if="redoQuestion">
          <WrongQuestionRedo 
            :question="redoQuestion" 
            @complete="handleRedoComplete"
            @cancel="closeRedoDialog"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/api.js'
import WrongQuestionDetail from '../components/WrongQuestionDetail.vue'
import WrongQuestionRedo from '../components/WrongQuestionRedo.vue'

export default {
  name: 'WrongQuestionsView',
  components: {
    WrongQuestionDetail,
    WrongQuestionRedo
  },
  setup() {
    const router = useRouter()
    const wrongQuestions = ref([])
    const loading = ref(false)
    const statistics = ref(null)
    const showDetailDialog = ref(false)
    const showRedoDialog = ref(false)
    const selectedQuestion = ref(null)
    const redoQuestion = ref(null)
    
    // 筛选条件
    const filters = ref({
      status: '',
      question_type: '',
      difficulty: ''
    })
    
    const selectedKnowledgePoints = ref([])
    
    // 获取错题数据
    const fetchWrongQuestions = async () => {
      loading.value = true
      try {
        const data = await api.getWrongQuestions(filters.value)
        wrongQuestions.value = Array.isArray(data) ? data : []
      } catch (error) {
        console.error('获取错题失败:', error)
        wrongQuestions.value = []
      } finally {
        loading.value = false
      }
    }
    
    // 获取统计信息
    const fetchStatistics = async () => {
      try {
        statistics.value = await api.getWrongQuestionStatistics()
      } catch (error) {
        console.error('获取统计信息失败:', error)
      }
    }
    
    // 可用知识点
    const availableKnowledgePoints = computed(() => {
      const points = new Set()
      wrongQuestions.value.forEach(q => {
        if (q.knowledge_points && Array.isArray(q.knowledge_points)) {
          q.knowledge_points.forEach(p => points.add(p))
        }
      })
      return Array.from(points).sort()
    })
    
    // 筛选后的错题
    const filteredQuestions = computed(() => {
      let result = wrongQuestions.value
      
      // 知识点筛选
      if (selectedKnowledgePoints.value.length > 0) {
        result = result.filter(q => {
          if (!q.knowledge_points || !Array.isArray(q.knowledge_points)) return false
          return selectedKnowledgePoints.value.some(p => q.knowledge_points.includes(p))
        })
      }
      
      return result
    })
    
    // 应用筛选
    const applyFilters = () => {
      fetchWrongQuestions()
    }
    
    // 清除筛选
    const clearFilters = () => {
      filters.value = {
        status: '',
        question_type: '',
        difficulty: ''
      }
      selectedKnowledgePoints.value = []
      applyFilters()
    }
    
    // 切换知识点
    const toggleKnowledgePoint = (point) => {
      const index = selectedKnowledgePoints.value.indexOf(point)
      if (index > -1) {
        selectedKnowledgePoints.value.splice(index, 1)
      } else {
        selectedKnowledgePoints.value.push(point)
      }
    }
    
    // 查看详情
    const viewQuestionDetail = async (question) => {
      try {
        const detail = await api.getWrongQuestionDetail(question.id)
        selectedQuestion.value = detail.data || detail
        showDetailDialog.value = true
      } catch (error) {
        console.error('获取错题详情失败:', error)
        selectedQuestion.value = question
        showDetailDialog.value = true
      }
    }
    
    // 关闭详情对话框
    const closeDetailDialog = () => {
      showDetailDialog.value = false
      selectedQuestion.value = null
    }
    
    // 开始重做
    const startRedo = async (question) => {
      try {
        console.log('开始重做，错题数据:', question)
        // 更新错题状态为redoing
        await api.updateWrongQuestionStatus(question.id, 'redoing')
        
        // 尝试获取practiceId，优先从不同字段获取
        let practiceId = question.practiceId || question.practice_id || question.practice?.id
        
        // 如果practiceId不存在，尝试通过chapter_id查找练习
        if (!practiceId && (question.chapter_id || question.chapter?.id)) {
          console.log('practiceId不存在，尝试通过chapter_id查找练习...', {
            chapter_id: question.chapter_id || question.chapter?.id,
            book_id: question.book_id || question.book?.id
          })
          
          const chapterId = question.chapter_id || question.chapter?.id
          const bookId = question.book_id || question.book?.id
          
          if (chapterId) {
            // 跳转到练习页面，使用chapterId和标题参数，确保能精确匹配到对应的练习
            const practiceTitle = question.title || question.practice_title
            console.log('使用chapterId和标题跳转到练习页面...', { 
              chapterId, 
              bookId, 
              practiceTitle,
              redo: true 
            })
            router.push({ 
              path: '/student/practice', 
              query: { 
                chapterId: chapterId,
                bookId: bookId,
                practiceTitle: practiceTitle, // 添加标题参数用于精确匹配
                redo: 'true'
              } 
            })
            return
          }
        }
        
        if (practiceId) {
          // 跳转到练习题页面，添加redo标志以清除之前的作答记录
          router.push({ 
            path: '/student/practice', 
            query: { 
              practiceId: practiceId,
              redo: 'true' // 添加重做标志
            } 
          })
        } else {
          // 如果没有practiceId和chapterId，尝试使用旧的对话框方式
          console.log('无法获取practiceId或chapterId，使用对话框方式')
          const result = await api.redoWrongQuestion(question.id)
          redoQuestion.value = result.data || result
          showRedoDialog.value = true
        }
      } catch (error) {
        console.error('开始重做失败:', error)
        alert('开始重做失败，请稍后重试')
      }
    }
    
    // 从详情页重做
    const handleRedoFromDetail = (question) => {
      closeDetailDialog()
      startRedo(question)
    }
    
    // 关闭重做对话框
    const closeRedoDialog = () => {
      showRedoDialog.value = false
      redoQuestion.value = null
    }
    
    // 完成重做
    const handleRedoComplete = async (questionId, isCorrect) => {
      try {
        const result = await api.completeWrongQuestionRedo(questionId, isCorrect)
        if (result.should_remove) {
          // 从列表中移除
          wrongQuestions.value = wrongQuestions.value.filter(q => q.id !== questionId)
        }
        closeRedoDialog()
        await fetchStatistics()
        alert(result.message || (isCorrect ? '恭喜！您已掌握这道题' : '继续加油！'))
      } catch (error) {
        console.error('完成重做失败:', error)
        alert('操作失败，请稍后重试')
      }
    }
    
    // 切换状态
    const toggleStatus = async (question) => {
      try {
        const nextStatus = getNextStatus(question.status)
        await api.updateWrongQuestionStatus(question.id, nextStatus)
        
        if (nextStatus === 'resolved') {
          // 已解决，从列表中移除
          wrongQuestions.value = wrongQuestions.value.filter(q => q.id !== question.id)
        } else {
          // 更新状态
          question.status = nextStatus
        }
        
        await fetchStatistics()
      } catch (error) {
        console.error('更新状态失败:', error)
        alert('更新状态失败，请稍后重试')
      }
    }
    
    // 删除错题
    const deleteQuestion = async (questionId) => {
      if (!confirm('确定要删除这道错题吗？')) {
        return
      }
      
      try {
        await api.removeWrongQuestion(questionId)
        wrongQuestions.value = wrongQuestions.value.filter(q => q.id !== questionId)
        await fetchStatistics()
        alert('删除成功')
      } catch (error) {
        console.error('删除失败:', error)
        alert('删除失败，请稍后重试')
      }
    }
    
    // 刷新数据
    const refreshData = async () => {
      await Promise.all([fetchWrongQuestions(), fetchStatistics()])
    }
    
    // 工具函数
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
    
    const getNextStatus = (currentStatus) => {
      const statusFlow = {
        'unresolved': 'redoing',
        'redoing': 'resolved',
        'resolved': 'unresolved'
      }
      return statusFlow[currentStatus] || 'unresolved'
    }
    
    const getStatusActionText = (status) => {
      const map = {
        'unresolved': '标记为重做中',
        'redoing': '标记为已解决',
        'resolved': '标记为未解决'
      }
      return map[status] || '更新状态'
    }
    
    // 初始化
    onMounted(() => {
      refreshData()
    })
    
    return {
      wrongQuestions,
      loading,
      statistics,
      filters,
      selectedKnowledgePoints,
      availableKnowledgePoints,
      filteredQuestions,
      showDetailDialog,
      showRedoDialog,
      selectedQuestion,
      redoQuestion,
      applyFilters,
      clearFilters,
      toggleKnowledgePoint,
      viewQuestionDetail,
      closeDetailDialog,
      startRedo,
      closeRedoDialog,
      handleRedoComplete,
      handleRedoFromDetail,
      toggleStatus,
      deleteQuestion,
      refreshData,
      formatTime,
      getDifficultyStars,
      getStatusDisplay,
      getStatusActionText
    }
  }
}
</script>

<style scoped>
.wrong-questions-view {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.view-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.view-header h2 {
  margin: 0;
  color: #333;
}

/* 统计信息 */
.statistics-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.stat-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409EFF;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

/* 筛选器 */
.filters-section {
  display: flex;
  gap: 15px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 8px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-size: 14px;
  color: #666;
}

.filter-select {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #409EFF;
}

/* 知识点筛选 */
.knowledge-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 8px;
}

.filter-label {
  font-size: 14px;
  color: #666;
  margin-right: 8px;
}

.knowledge-tag {
  padding: 4px 12px;
  border-radius: 16px;
  background: #e9ecef;
  color: #495057;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.knowledge-tag:hover {
  background: #dee2e6;
}

.knowledge-tag.active {
  background: #409EFF;
  color: white;
  border-color: #409EFF;
}

/* 错题列表 */
.questions-section {
  margin-top: 20px;
}

.loading-state,
.no-data {
  text-align: center;
  padding: 40px;
  color: #999;
}

.no-data .hint {
  font-size: 14px;
  margin-top: 10px;
}

.questions-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.question-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: all 0.3s;
}

.question-card:hover {
  box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.question-card.status-unresolved {
  border-left: 4px solid #F56C6C;
}

.question-card.status-redoing {
  border-left: 4px solid #E6A23C;
}

.question-card.status-resolved {
  border-left: 4px solid #67C23A;
  opacity: 0.8;
}

.question-header {
  margin-bottom: 15px;
}

.question-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.question-title {
  margin: 0;
  font-size: 18px;
  color: #333;
  flex: 1;
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

.question-meta {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
  font-size: 13px;
  color: #666;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
}

.meta-label {
  font-weight: 500;
}

.question-error-reason {
  margin: 15px 0;
  padding: 12px;
  background: #FEF0F0;
  border-left: 3px solid #F56C6C;
  border-radius: 4px;
}

.question-error-reason strong {
  color: #F56C6C;
}

.question-error-reason p {
  margin: 8px 0 0 0;
  color: #666;
}

.question-knowledge-points {
  margin: 15px 0;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.question-knowledge-points strong {
  color: #333;
  font-size: 14px;
}

.knowledge-point-tag {
  padding: 4px 10px;
  background: #E1F3FF;
  color: #409EFF;
  border-radius: 12px;
  font-size: 12px;
}

.question-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  flex-wrap: wrap;
}

/* 模态框 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 800px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}

.modal-large {
  max-width: 1000px;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #e0e0e0;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

/* 按钮样式 */
.btn {
  padding: 8px 16px;
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

.btn-success {
  background: #67C23A;
  color: white;
}

.btn-success:hover {
  background: #85ce61;
}

.btn-secondary {
  background: #909399;
  color: white;
}

.btn-secondary:hover {
  background: #a6a9ad;
}

.btn-danger {
  background: #F56C6C;
  color: white;
}

.btn-danger:hover {
  background: #f78989;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>


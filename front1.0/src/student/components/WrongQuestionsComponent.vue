<template>
  <div class="wrong-questions-component">
    <div class="component-header">
      <h3>错题本</h3>
      <div class="header-actions">
        <div class="filter-container">
          <select v-model="statusFilter" class="filter-select" @change="applyFilters">
            <option value="">所有状态</option>
            <option value="unresolved">未解决</option>
            <option value="redoing">重做中</option>
            <option value="resolved">已解决</option>
          </select>
          <select v-model="difficultyFilter" class="filter-select" @change="applyFilters">
            <option value="">所有难度</option>
            <option value="1">★</option>
            <option value="2">★★</option>
            <option value="3">★★★</option>
            <option value="4">★★★★</option>
            <option value="5">★★★★★</option>
          </select>
        </div>
        <button class="btn btn-sm" @click="refreshQuestions" :disabled="loading">
          <span v-if="loading">刷新中...</span>
          <span v-else>🔄 刷新</span>
        </button>
      </div>
    </div>
    
    <!-- 筛选后的知识点标签 -->
    <div v-if="availableKnowledgePoints.length > 0" class="knowledge-filters">
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
    
    <div class="questions-content">
      <div v-if="loading" class="loading-state">
        <p>加载错题中...</p>
      </div>
      
      <div v-else-if="wrongQuestions.length === 0" class="no-data">
        <p>暂无错题记录</p>
        <p class="hint">继续学习并完成练习题，错题会自动添加到这里</p>
      </div>
      
      <div v-else class="questions-list">
        <div 
          v-for="(question, index) in filteredQuestions" 
          :key="question.id"
          class="question-item"
          :class="`status-${question.status}`"
        >
          <div class="question-header">
            <div class="question-title">{{ question.title }}</div>
            <div class="question-meta">
              <span class="question-time">{{ formatTime(question.attemptTime) }}</span>
              <span class="question-difficulty">难度: {{ getDifficultyStars(question.difficulty) }}</span>
              <span class="question-status" :class="`status-${question.status}`">
                {{ getStatusDisplay(question.status) }}
              </span>
            </div>
          </div>
          
          <div v-if="question.error_reason" class="question-error-reason">
            <strong>错误原因:</strong> {{ question.error_reason }}
          </div>
          
          <div v-if="question.knowledge_points && question.knowledge_points.length > 0" class="question-knowledge-points">
            <strong>关联知识点:</strong>
            <span 
              v-for="(point, idx) in question.knowledge_points" 
              :key="idx"
              class="knowledge-point-item"
            >
              {{ point }}
            </span>
          </div>
          
          <div class="question-actions">
            <button class="btn btn-primary btn-sm" @click="startRedoing(question)">
              开始重做
            </button>
            <button 
              class="btn btn-secondary btn-sm" 
              :class="{'btn-success': question.status === 'resolved', 'btn-warning': question.status === 'redoing'}"
              @click="updateQuestionStatus(question.id, getNextStatus(question.status))"
            >
              {{ getNextStatusText(question.status) }}
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="component-footer">
      <div class="stats">
        <span>共 {{ wrongQuestions.length }} 道错题</span>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed, defineEmits } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/api.js'

export default {
  name: 'WrongQuestionsComponent',
  emits: ['review-question', 'redo-question'],
  setup(props, { emit }) {
    const wrongQuestions = ref([])
    const loading = ref(false)
    const router = useRouter()
    
    // 筛选条件
    const statusFilter = ref('')
    const difficultyFilter = ref('')
    const selectedKnowledgePoints = ref([])
    
    // 获取错题数据
    const fetchWrongQuestions = async () => {
      loading.value = true
      try {
        const response = await api.getWrongQuestions()
        // 确保获取到的数据是数组格式
        let data = response
        if (response && response.data) {
          data = response.data
        }
        // 从本地存储获取已掌握的题目ID
        const masteredIds = getMasteredQuestionIds()
        // 过滤掉已掌握的题目
        wrongQuestions.value = Array.isArray(data) ? data.filter(q => !masteredIds.includes(q.id)) : []
        console.log('获取错题数据:', wrongQuestions.value)
      } catch (error) {
        console.error('获取错题失败:', error)
        // 使用模拟数据
        wrongQuestions.value = getMockWrongQuestions()
      } finally {
        loading.value = false
      }
    }
    
    // 模拟错题数据
    const getMockWrongQuestions = () => {
      const now = new Date()
      const yesterday = new Date(now - 24 * 60 * 60 * 1000)
      const twoDaysAgo = new Date(now - 48 * 60 * 60 * 1000)
      
      return [
        {
          id: 1,
          title: 'Python中的列表推导式',
          difficulty: 3,
          practiceId: 1,
          attemptTime: now.toISOString(),
          error_reason: '语法错误，忘记冒号',
          knowledge_points: ['列表', '推导式'],
          status: 'unresolved'
        },
        {
          id: 2,
          title: 'JavaScript事件循环机制',
          difficulty: 4,
          practiceId: 2,
          attemptTime: yesterday.toISOString(),
          error_reason: '不理解宏任务和微任务的执行顺序',
          knowledge_points: ['事件循环', '异步编程'],
          status: 'redoing'
        },
        {
          id: 3,
          title: '数据结构中的二叉树遍历',
          difficulty: 5,
          practiceId: 3,
          attemptTime: twoDaysAgo.toISOString(),
          error_reason: '递归逻辑错误',
          knowledge_points: ['二叉树', '遍历', '递归'],
          status: 'resolved'
        }
      ]
    }
    
    // 格式化时间
    const formatTime = (timeString) => {
      if (!timeString) return ''
      const date = new Date(timeString)
      const now = new Date()
      const diffTime = Math.abs(now - date)
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) {
        return '今天'
      } else if (diffDays === 1) {
        return '昨天'
      } else if (diffDays < 7) {
        return `${diffDays}天前`
      } else {
        return date.toLocaleDateString('zh-CN')
      }
    }
    
    // 获取难度星星
    const getDifficultyStars = (difficulty) => {
      const stars = []
      const maxStars = 5
      for (let i = 0; i < maxStars; i++) {
        stars.push(i < difficulty ? '⭐' : '☆')
      }
      return stars.join('')
    }
    
    // 获取可用的知识点列表
    const availableKnowledgePoints = computed(() => {
      const allPoints = new Set()
      wrongQuestions.value.forEach(q => {
        if (q.knowledge_points && Array.isArray(q.knowledge_points)) {
          q.knowledge_points.forEach(point => {
            if (point) {
              allPoints.add(point)
            }
          })
        }
      })
      return Array.from(allPoints)
    })
    
    // 切换知识点筛选
    const toggleKnowledgePoint = (point) => {
      const index = selectedKnowledgePoints.value.indexOf(point)
      if (index === -1) {
        selectedKnowledgePoints.value.push(point)
      } else {
        selectedKnowledgePoints.value.splice(index, 1)
      }
      applyFilters()
    }
    
    // 应用所有筛选条件
    const applyFilters = () => {
      // 筛选逻辑已在filteredQuestions计算属性中实现
    }
    
    // 筛选后的题目列表
    const filteredQuestions = computed(() => {
      return wrongQuestions.value.filter(q => {
        // 状态筛选
        const statusMatch = !statusFilter.value || q.status === statusFilter.value
        // 难度筛选
        const difficultyMatch = !difficultyFilter.value || q.difficulty === Number(difficultyFilter.value)
        // 知识点筛选
        const knowledgeMatch = selectedKnowledgePoints.value.length === 0 || 
          (q.knowledge_points && Array.isArray(q.knowledge_points) && 
           q.knowledge_points.some(p => selectedKnowledgePoints.value.includes(p)))
        
        return statusMatch && difficultyMatch && knowledgeMatch
      })
    })
    
    // 开始重做题目
    const startRedoing = async (question) => {
      console.log('开始重做函数被调用:', question)
      console.log('错题数据:', question)
      emit('redo-question', question)
      // 自动更新状态为redoing（异步执行，不阻塞路由跳转）
      updateQuestionStatus(question.id, 'redoing').catch(error => {
        console.error('更新状态失败，但仍会跳转到练习页面:', error)
      })
      
      // 尝试获取practiceId，优先从不同字段获取
      let practiceId = question.practiceId || question.practice_id || question.practice?.id
      
      // 如果practiceId不存在，尝试通过chapter_id查找练习
      if (!practiceId && (question.chapter_id || question.chapter?.id)) {
        try {
          console.log('practiceId不存在，尝试通过chapter_id查找练习...', {
            chapter_id: question.chapter_id || question.chapter?.id,
            book_id: question.book_id || question.book?.id
          })
          
          // 如果错题有chapter信息，可以跳转到练习页面，让页面根据chapter来显示
          // 或者尝试获取该章节的练习列表
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
        } catch (error) {
          console.error('通过chapter查找练习失败:', error)
        }
      }
      
      if (practiceId) {
        console.log('正在跳转到练习题页面进行重做...', { practiceId, redo: true })
        router.push({ 
          path: '/student/practice', 
          query: { 
            practiceId: practiceId,
            redo: 'true' // 添加重做标志，用于清除之前的作答记录
          } 
        })
      } else {
        console.error('无法获取practiceId或chapterId，无法跳转到练习页面', question)
        alert('无法获取练习题信息，该错题可能没有关联的练习题。请尝试从章节页面进入练习。')
      }
    }
    
    // 更新题目状态
    const updateQuestionStatus = async (questionId, newStatus) => {
      try {
        await api.updateWrongQuestionStatus(questionId, newStatus)
        // 更新本地数据
        const question = wrongQuestions.value.find(q => q.id === questionId)
        if (question) {
          question.status = newStatus
        }
        // 如果标记为已解决，从列表中移除
        if (newStatus === 'resolved') {
          const index = wrongQuestions.value.findIndex(q => q.id === questionId)
          if (index !== -1) {
            wrongQuestions.value.splice(index, 1)
          }
        }
      } catch (error) {
        console.error('更新题目状态失败:', error)
        alert('更新状态失败，请稍后重试')
      }
    }
    
    // 获取状态显示文本
    const getStatusDisplay = (status) => {
      const statusMap = {
        'unresolved': '未解决',
        'redoing': '重做中',
        'resolved': '已解决'
      }
      return statusMap[status] || '未知状态'
    }
    
    // 获取下一个状态
    const getNextStatus = (currentStatus) => {
      const statusOrder = {
        'unresolved': 'redoing',
        'redoing': 'resolved'
      }
      return statusOrder[currentStatus] || 'unresolved'
    }
    
    // 获取下一个状态的显示文本
    const getNextStatusText = (currentStatus) => {
      const statusTextMap = {
        'unresolved': '开始重做',
        'redoing': '标记为已解决'
      }
      return statusTextMap[currentStatus] || '开始重做'
    }
    
    // 重新练习题目
    const reviewQuestion = (question) => {
      emit('review-question', question)
    }
    
    // 标记为已掌握
    const markAsFixed = async (index) => {
      if (confirm('确定要将这道题标记为已掌握吗？')) {
        const question = wrongQuestions.value[index]
        try {
          // 调用后端API删除错题
          await api.removeWrongQuestion(question.id)
          console.log('错题已从服务器移除')
        } catch (error) {
          console.error('删除错题失败，使用本地存储备份:', error)
          // 备份方案：保存到本地存储
          saveMasteredQuestionId(question.id)
        }
        // 从列表中移除
        wrongQuestions.value.splice(index, 1)
      }
    }
    
    // 获取已掌握的题目ID
    const getMasteredQuestionIds = () => {
      try {
        const mastered = localStorage.getItem('masteredQuestions')
        return mastered ? JSON.parse(mastered) : []
      } catch (error) {
        console.error('获取已掌握题目失败:', error)
        return []
      }
    }
    
    // 保存已掌握的题目ID
    const saveMasteredQuestionId = (questionId) => {
      try {
        const masteredIds = getMasteredQuestionIds()
        if (!masteredIds.includes(questionId)) {
          masteredIds.push(questionId)
          localStorage.setItem('masteredQuestions', JSON.stringify(masteredIds))
        }
      } catch (error) {
        console.error('保存已掌握题目失败:', error)
      }
    }
    
    // 刷新题目
    const refreshQuestions = () => {
      fetchWrongQuestions()
    }
    
    // 组件挂载时获取数据
    onMounted(() => {
      fetchWrongQuestions()
    })
    
    return {
      wrongQuestions,
      loading,
      statusFilter,
      difficultyFilter,
      selectedKnowledgePoints,
      availableKnowledgePoints,
      filteredQuestions,
      formatTime,
      getDifficultyStars,
      toggleKnowledgePoint,
      applyFilters,
      startRedoing,
      updateQuestionStatus,
      getStatusDisplay,
      getNextStatus,
      getNextStatusText,
      reviewQuestion,
      markAsFixed,
      refreshQuestions
    }
  }
}
</script>

<style scoped>
.wrong-questions-component {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* 头部样式 */
.component-header {
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.component-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 10px;
  align-items: center;
}

.filter-container {
  display: flex;
  gap: 10px;
}

.filter-select {
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-size: 12px;
  background: white;
  cursor: pointer;
}

.filter-select:focus {
  outline: none;
  border-color: #409EFF;
}

/* 知识点筛选标签 */
.knowledge-filters {
  padding: 10px 15px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  background: #f5f5f5;
}

.knowledge-tag {
  padding: 3px 8px;
  border-radius: 12px;
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

/* 内容区域 */
.questions-content {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
}

.loading-state,
.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #999;
  text-align: center;
}

.no-data .hint {
  font-size: 14px;
  margin-top: 10px;
  color: #bbb;
}

/* 题目列表 */
.questions-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.question-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 15px;
  transition: all 0.3s;
  border: 1px solid #e0e0e0;
}

.question-item:hover {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

/* 状态样式 */
.question-item.status-unresolved {
  border-left: 4px solid #F56C6C;
}

.question-item.status-redoing {
  border-left: 4px solid #E6A23C;
}

.question-item.status-resolved {
  border-left: 4px solid #67C23A;
  opacity: 0.8;
}

.question-header {
  margin-bottom: 10px;
}

.question-title {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.4;
}

.question-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  font-size: 12px;
  color: #999;
}

/* 错误原因样式 */
.question-error-reason {
  margin: 8px 0;
  padding: 8px;
  background: rgba(245, 108, 108, 0.05);
  border-radius: 4px;
  border-left: 3px solid #F56C6C;
  font-size: 13px;
  line-height: 1.5;
}

/* 知识点样式 */
.question-knowledge-points {
  margin: 8px 0;
  font-size: 13px;
}

.knowledge-point-item {
  display: inline-block;
  padding: 2px 6px;
  margin-right: 6px;
  margin-bottom: 4px;
  background: #e7f3ff;
  color: #337ab7;
  border-radius: 3px;
  font-size: 11px;
}

/* 题目状态标签 */
.question-status {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  font-weight: 500;
}

.question-status.status-unresolved {
  background: #fef0f0;
  color: #F56C6C;
}

.question-status.status-redoing {
  background: #fdf6ec;
  color: #E6A23C;
}

.question-status.status-resolved {
  background: #f0f9eb;
  color: #67C23A;
}

.question-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding-top: 10px;
  border-top: 1px solid #e0e0e0;
}

/* 底部样式 */
.component-footer {
  padding: 15px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8f9fa;
}

.stats {
  font-size: 14px;
  color: #666;
}

/* 按钮样式 */
.btn {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.3s;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn-primary {
  background: #409EFF;
  color: white;
}

.btn-primary:hover {
  background: #66b1ff;
}

.btn-secondary {
  background: #67C23A;
  color: white;
}

.btn-secondary:hover {
  background: #85ce61;
}

.btn-warning {
  background: #E6A23C;
  color: white;
}

.btn-warning:hover {
  background: #ebb563;
}

.btn-success {
  background: #67C23A;
  color: white;
}

.btn-success:hover {
  background: #85ce61;
}
</style>
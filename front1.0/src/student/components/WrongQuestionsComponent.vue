<template>
  <div class="wrong-questions-component">
    <div class="component-header">
      <h3>错题本</h3>
      <div class="header-actions">
        <button class="btn btn-sm" @click="refreshQuestions" :disabled="loading">
          <span v-if="loading">刷新中...</span>
          <span v-else>🔄 刷新</span>
        </button>
      </div>
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
          v-for="(question, index) in wrongQuestions" 
          :key="index"
          class="question-item"
        >
          <div class="question-header">
            <div class="question-title">{{ question.title }}</div>
            <div class="question-meta">
              <span class="question-time">{{ formatTime(question.attemptTime) }}</span>
              <span class="question-difficulty">难度: {{ getDifficultyStars(question.difficulty) }}</span>
            </div>
          </div>
          
          <div class="question-actions">
            <button class="btn btn-primary btn-sm" @click="reviewQuestion(question)">
              重新练习
            </button>
            <button class="btn btn-secondary btn-sm" @click="markAsFixed(index)">
              ✅ 标记已掌握
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
import { ref, onMounted, defineEmits } from 'vue'
import { api } from '../api/api.js'

export default {
  name: 'WrongQuestionsComponent',
  emits: ['review-question'],
  setup(props, { emit }) {
    const wrongQuestions = ref([])
    const loading = ref(false)
    
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
          attemptTime: now.toISOString()
        },
        {
          id: 2,
          title: 'JavaScript事件循环机制',
          difficulty: 4,
          practiceId: 2,
          attemptTime: yesterday.toISOString()
        },
        {
          id: 3,
          title: '数据结构中的二叉树遍历',
          difficulty: 5,
          practiceId: 3,
          attemptTime: twoDaysAgo.toISOString()
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
    
    // 不再需要筛选功能，直接使用所有错题
    
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
      formatTime,
      getDifficultyStars,
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
</style>
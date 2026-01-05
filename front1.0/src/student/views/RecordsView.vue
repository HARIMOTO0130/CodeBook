<template>
  <div class="records-container">
    <div class="page-header">
      <h1>学习记录</h1>
      <div class="header-actions">
        <select v-model="timeRange" class="input filter-select">
          <option value="week">最近一周</option>
          <option value="month">最近一月</option>
          <option value="quarter">最近三月</option>
          <option value="year">最近一年</option>
        </select>
        <div class="goal-settings">
          <span>每日目标: {{ dailyGoalHours }}小时</span>
          <button class="btn btn-link" @click="showGoalModal = true">设置</button>
        </div>
      </div>
    </div>

    <!-- 学习概览 -->
    <div class="overview-section">
      <div class="stat-cards">
        <div class="stat-card">
          <div class="stat-value">{{ totalLearningDays }}</div>
          <div class="stat-label">学习天数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ totalHours }}h</div>
          <div class="stat-label">学习时长</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ completedChapters }}</div>
          <div class="stat-label">完成章节</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ accuracyRate }}%</div>
          <div class="stat-label">练习正确率</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ currentStreak }}</div>
          <div class="stat-label">连续学习天数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ goalCompletionRate }}%</div>
          <div class="stat-label">目标达成率</div>
        </div>
      </div>
    </div>
    
    <!-- 每日学习目标进度 -->
    <div class="goal-progress-section">
      <div class="goal-progress-header">
        <h3>今日学习目标</h3>
        <span class="today-date">{{ formatTodayDate() }}</span>
      </div>
      <div class="today-goal-progress">
        <div class="goal-progress-bar">
          <div 
            class="goal-progress-fill" 
            :style="{ width: todayProgressPercentage + '%' }"
          ></div>
        </div>
        <div class="goal-progress-text">
          <span>{{ todayHours }} / {{ dailyGoalHours }} 小时</span>
          <span>{{ todayProgressPercentage }}%</span>
        </div>
      </div>
    </div>

    <div class="main-content">
      <!-- 左侧区域 -->
      <div class="left-section">
          <!-- 日历热力图 -->
          <div class="chart-section">
            <h2>学习热力图</h2>
            <div class="simple-heatmap">
              <!-- 图例 -->
              <div class="simple-heatmap-legend">
                <span>少</span>
                <div class="simple-heatmap-colors">
                  <div class="simple-heatmap-color" style="background-color: #ebedf0;"></div>
                  <div class="simple-heatmap-color" style="background-color: #c6e48b;"></div>
                  <div class="simple-heatmap-color" style="background-color: #7bc96f;"></div>
                  <div class="simple-heatmap-color" style="background-color: #239a3b;"></div>
                  <div class="simple-heatmap-color" style="background-color: #196127;"></div>
                </div>
                <span>多</span>
              </div>
              
              <!-- 热力图主体 -->
              <div class="simple-heatmap-grid">
                <!-- 星期标签 -->
                <div class="simple-heatmap-weekdays">
                  <div v-for="day in ['日', '一', '二', '三', '四', '五', '六']" :key="day" class="simple-heatmap-weekday">
                    {{ day }}
                  </div>
                </div>
                
                <!-- 热力图格子 - 确保至少有一些数据 -->
                <div class="simple-heatmap-cells" v-if="heatmapData.length > 0">
                  <div
                    v-for="(day, index) in heatmapData"
                    :key="index"
                    class="simple-heatmap-cell"
                    :style="{ backgroundColor: getHeatColor(day.intensity) }"
                    :title="`${day.date}: ${day.hours.toFixed(1)}小时`"
                  ></div>
                </div>
                
                <!-- 备用格子，确保即使没有数据也能看到网格 -->
                <div v-else class="simple-heatmap-cells">
                  <div 
                    v-for="n in 21" 
                    :key="n"
                    class="simple-heatmap-cell"
                    :style="{ backgroundColor: '#ebedf0' }"
                    :title="`暂无数据`"
                  ></div>
                </div>
              </div>
            </div>
          </div>

          <!-- 学习趋势 -->
        <div class="chart-section">
          <h2>学习趋势</h2>
          <div class="trend-chart">
            <div class="trend-bars">
              <div 
                v-for="(item, index) in trendData" 
                :key="index"
                class="trend-bar"
              >
                <div class="bar" :style="{ height: item.hours * 20 + 'px' }"></div>
                <div class="bar-label">{{ item.day }}</div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 学习习惯分析 -->
        <div class="chart-section">
          <h2>学习习惯分析</h2>
          <div class="habit-analysis">
            <div class="habit-item">
              <div class="habit-title">最佳学习时段</div>
              <div class="habit-content">
                <div class="time-slots">
                  <div 
                    v-for="(slot, index) in timeSlots" 
                    :key="index"
                    class="time-slot"
                    :class="{ active: slot.active }"
                    :style="{ height: slot.intensity * 20 + 'px' }"
                    :title="`${slot.time}: ${slot.count}次学习`"
                  >
                    <span class="time-label">{{ slot.time }}</span>
                  </div>
                </div>
              </div>
            </div>
            <div class="habit-item">
              <div class="habit-title">学习类型分布</div>
              <div class="habit-content">
                <div class="learning-types">
                  <div 
                    v-for="type in learningTypes" 
                    :key="type.name"
                    class="learning-type"
                  >
                    <div class="type-label">{{ type.name }}</div>
                    <div class="type-progress">
                      <div 
                        class="type-progress-fill" 
                        :style="{ width: type.percentage + '%', backgroundColor: type.color }"
                      ></div>
                    </div>
                    <div class="type-percentage">{{ type.percentage }}%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧区域 -->
      <div class="right-section">
        <!-- 教材完成度 -->
        <div class="chart-section">
          <h2>教材完成情况</h2>
          <div class="book-progress">
            <div 
              v-for="book in bookProgressData" 
              :key="book.id"
              class="book-progress-item"
            >
              <div class="book-info">
                <div class="book-name">{{ book.title }}</div>
                <div class="progress-text">{{ book.progress }}%</div>
                <div class="book-stats">
                  <span>{{ book.completedSections }}/{{ book.totalSections }} 小节</span>
                  <span>{{ book.totalHours }} 小时</span>
                </div>
              </div>
              <div class="circular-progress">
                <svg width="100" height="100" class="progress-ring">
                  <circle
                    class="progress-ring-bg"
                    cx="50"
                    cy="50"
                    :r="40"
                    stroke="#e0e0e0"
                    stroke-width="8"
                    fill="transparent"
                  />
                  <circle
                    class="progress-ring-fill"
                    cx="50"
                    cy="50"
                    :r="40"
                    :stroke="book.progress > 70 ? '#67C23A' : book.progress > 30 ? '#E6A23C' : '#409EFF'"
                    stroke-width="8"
                    fill="transparent"
                    :stroke-dasharray="circumference"
                    :stroke-dashoffset="getProgressOffset(book.progress)"
                    transform="rotate(-90 50 50)"
                  />
                  <text x="50" y="50" text-anchor="middle" dominant-baseline="middle" class="progress-text-center">
                    {{ book.progress }}%
                  </text>
                </svg>
              </div>
            </div>
          </div>
        </div>

        <!-- 错题本 -->
        <div class="chart-section">
          <h2>错题本</h2>
          <div class="wrong-questions">
            <div v-if="wrongQuestions.length === 0" class="no-data">
              暂无错题记录
            </div>
            <div 
              v-for="(question, index) in wrongQuestions" 
              :key="index"
              class="wrong-question-item"
            >
              <div class="question-info">
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
              </div>
            </div>
          </div>
        </div>
        
        <!-- 学习记录列表 -->
        <div class="chart-section">
          <h2>最近学习记录</h2>
          <div class="learning-records">
            <div v-if="learningRecords.length === 0" class="no-data">
              暂无学习记录
            </div>
            <div 
              v-for="(record, index) in learningRecords" 
              :key="index"
              class="learning-record-item"
            >
              <div class="record-icon">{{ getRecordIcon(record.type) }}</div>
              <div class="record-content">
                <div class="record-title">{{ record.title }}</div>
                <div class="record-meta">
                  <span class="record-book">{{ record.bookTitle }}</span>
                  <span class="record-duration">{{ record.duration }}分钟</span>
                  <span class="record-time">{{ formatTime(record.timestamp) }}</span>
                </div>
              </div>
              <div class="record-status" :class="record.status">
                {{ getStatusText(record.status) }}
              </div>
            </div>
            <button 
              v-if="learningRecords.length > 0" 
              class="btn btn-link view-more-btn"
              @click="loadMoreRecords"
            >
              查看更多记录
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 目标设置弹窗 -->
    <div v-if="showGoalModal" class="modal-overlay" @click="showGoalModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>设置每日学习目标</h3>
          <button class="modal-close" @click="showGoalModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>每日学习时长 (小时)</label>
            <input 
              type="number" 
              v-model.number="dailyGoalHours" 
              min="0.5" 
              max="12" 
              step="0.5"
              class="input"
            >
          </div>
          <div class="form-group">
            <label>每日章节目标</label>
            <input 
              type="number" 
              v-model.number="dailyGoalChapters" 
              min="1" 
              max="10"
              class="input"
            >
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-default" @click="showGoalModal = false">取消</button>
          <button class="btn btn-primary" @click="saveGoalSettings">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/api.js'

export default {
  name: 'RecordsView',
  setup() {
    const router = useRouter()
    const timeRange = ref('month')
    
    // 统计数据
    const totalLearningDays = ref(15)
    const totalHours = ref(42.5)
    const completedChapters = ref(32)
    const accuracyRate = ref(87)
    const currentStreak = ref(7) // 连续学习天数
    const goalCompletionRate = ref(85) // 目标达成率
    
    // 每日目标设置
    const dailyGoalHours = ref(2) // 每日学习时长目标
    const dailyGoalChapters = ref(2) // 每日章节目标
    const todayHours = ref(1.5) // 今日已学习时长
    const todayProgressPercentage = computed(() => {
      return Math.min(100, Math.round((todayHours.value / dailyGoalHours.value) * 100))
    })
    const showGoalModal = ref(false)
    
    // 热力图数据
    const weekdays = ['日', '一', '二', '三', '四', '五', '六']
    const heatmapData = ref([])
    
    // 趋势图数据
    const trendData = ref([])
    
    // 教材进度数据
    const bookProgressData = ref([])
    const circumference = 2 * Math.PI * 40 // 圆周长
    
    // 错题本数据
    const wrongQuestions = ref([])
    
    // 学习记录数据
    const learningRecords = ref([])
    
    // 学习习惯数据
    const timeSlots = ref([
      { time: '08:00', intensity: 2, active: true },
      { time: '12:00', intensity: 1, active: false },
      { time: '15:00', intensity: 3, active: true },
      { time: '18:00', intensity: 2, active: false },
      { time: '20:00', intensity: 4, active: true },
      { time: '22:00', intensity: 1, active: false }
    ])
    
    const learningTypes = ref([
      { name: '阅读', percentage: 45, color: '#409EFF' },
      { name: '视频', percentage: 30, color: '#E6A23C' },
      { name: '练习', percentage: 25, color: '#67C23A' }
    ])
    
    // 加载数据
    const loadData = async () => {
      try {
        // 加载学习记录
        const records = await api.getLearningRecords(timeRange.value)
        // 确保records是数组类型，避免slice方法调用失败
        const recordsArray = Array.isArray(records) ? records : []
        learningRecords.value = recordsArray.slice(0, 10) // 只显示最近10条
        
        // 生成热力图数据
        generateHeatmapData()
        
        // 生成趋势图数据
        generateTrendData()
        
        // 加载教材进度
        const books = await api.getBooks()
        bookProgressData.value = books.map(book => ({
          id: book.id,
          title: book.title,
          progress: book.progress,
          completedSections: Math.floor((book.progress || 0) * ((book.totalSections || book.chapterCount || 0)) / 100),
          totalSections: book.totalSections || book.chapterCount || Math.floor(Math.random() * 20) + 10,
          totalHours: Math.floor(Math.random() * 10) + 5
        }))
        
        // 错题本：优先使用后端数据，否则用本地模拟
        try {
          wrongQuestions.value = await api.getWrongQuestions()
        } catch (e) {
          // ignore
        }
        if (wrongQuestions.value.length === 0) {
          wrongQuestions.value = [
            {
              id: 1,
              title: '以下哪个不是Python的数据类型？',
              practiceId: 1,
              attemptTime: new Date(Date.now() - 86400000).toISOString(),
              difficulty: 2
            },
            {
              id: 2,
              title: '关于JavaScript闭包，以下说法错误的是？',
              practiceId: 2,
              attemptTime: new Date(Date.now() - 172800000).toISOString(),
              difficulty: 3
            }
          ]
        }
        
        // 模拟学习记录数据（后端记录模型字段不完全匹配该视图展示）
        if (learningRecords.value.length === 0) {
          generateMockLearningRecords()
        }
      } catch (error) {
        console.error('加载学习记录失败:', error)
        // 生成模拟数据
        generateMockLearningRecords()
        // 确保在错误情况下也生成热力图和趋势图数据
        generateHeatmapData()
        generateTrendData()
      }
    }
    
    // 生成模拟学习记录
    const generateMockLearningRecords = () => {
      const records = []
      const types = ['reading', 'video', 'quiz']
      const statuses = ['completed', 'inProgress']
      const bookTitles = ['Python基础教程', 'JavaScript进阶', '数据结构与算法']
      
      for (let i = 0; i < 15; i++) {
        const type = types[Math.floor(Math.random() * types.length)]
        const title = type === 'reading' ? '章节阅读' : type === 'video' ? '视频学习' : '章节练习'
        const duration = Math.floor(Math.random() * 60) + 15 // 15-75分钟
        
        records.push({
          id: i + 1,
          type,
          title: `${bookTitles[Math.floor(Math.random() * bookTitles.length)]} - ${title} ${i + 1}`,
          bookTitle: bookTitles[Math.floor(Math.random() * bookTitles.length)],
          duration,
          status: statuses[Math.floor(Math.random() * statuses.length)],
          timestamp: new Date(Date.now() - i * 3600000 * (Math.random() * 3 + 1)).toISOString()
        })
      }
      
      learningRecords.value = records
    }
    
    // 加载更多记录
    const loadMoreRecords = () => {
      // 这里可以实现分页加载逻辑
      console.log('加载更多记录...')
    }
    
    // 保存目标设置
    const saveGoalSettings = () => {
      // 保存到localStorage或API
      localStorage.setItem('dailyGoalHours', dailyGoalHours.value.toString())
      localStorage.setItem('dailyGoalChapters', dailyGoalChapters.value.toString())
      showGoalModal.value = false
    }
    
    // 格式化今天的日期
    const formatTodayDate = () => {
      const today = new Date()
      const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
      return today.toLocaleDateString('zh-CN', options)
    }
    
    // 获取记录图标
    const getRecordIcon = (type) => {
      switch (type) {
        case 'reading': return '📄'
        case 'video': return '🎥'
        case 'quiz': return '💡'
        default: return '📚'
      }
    }
    
    // 获取状态文本
    const getStatusText = (status) => {
      switch (status) {
        case 'completed': return '已完成'
        case 'inProgress': return '学习中'
        default: return '未知'
      }
    }
    
    // 获取难度星星
    const getDifficultyStars = (difficulty) => {
      return '⭐'.repeat(difficulty)
    }
    
    // 生成热力图数据
    const generateHeatmapData = () => {
      const data = []
      const daysCount = timeRange.value === 'week' ? 7 : 
                        timeRange.value === 'month' ? 30 : 
                        timeRange.value === 'quarter' ? 90 : 365
      
      for (let i = daysCount - 1; i >= 0; i--) {
        const date = new Date()
        date.setDate(date.getDate() - i)
        
        // 随机生成学习强度 (0-4)
        const intensity = Math.floor(Math.random() * 5)
        
        data.push({
          date: date.toISOString().split('T')[0],
          intensity,
          hours: intensity * (Math.random() * 2 + 0.5)
        })
      }
      
      heatmapData.value = data
    }
    
    // 生成趋势图数据
    const generateTrendData = () => {
      const data = []
      const daysCount = timeRange.value === 'week' ? 7 : 30
      
      for (let i = daysCount - 1; i >= 0; i--) {
        const date = new Date()
        date.setDate(date.getDate() - i)
        
        data.push({
          day: date.getDate(),
          hours: Math.random() * 6 + 0.5 // 0.5-6.5小时
        })
      }
      
      trendData.value = data
    }
    
    // 获取热力图颜色
    const getHeatColor = (intensity) => {
      const colors = ['#ebedf0', '#c6e48b', '#7bc96f', '#239a3b', '#196127']
      return colors[intensity] || colors[0]
    }
    
    // 获取进度条偏移量
    const getProgressOffset = (progress) => {
      return circumference * (1 - progress / 100)
    }
    
    // 格式化时间
    const formatTime = (timeStr) => {
      const date = new Date(timeStr)
      const now = new Date()
      const diffMs = now - date
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24))
      
      if (diffDays === 0) {
        return '今天'
      } else if (diffDays === 1) {
        return '昨天'
      } else if (diffDays < 7) {
        return `${diffDays}天前`
      } else {
        return date.toLocaleDateString()
      }
    }
    
    // 重新练习错题
    const reviewQuestion = (question) => {
      router.push(`/practice?id=${question.practiceId}`)
    }
    
    onMounted(() => {
      loadData()
    })
    
    return {
      timeRange,
      totalLearningDays,
      totalHours,
      completedChapters,
      accuracyRate,
      currentStreak,
      goalCompletionRate,
      dailyGoalHours,
      dailyGoalChapters,
      todayHours,
      todayProgressPercentage,
      showGoalModal,
      weekdays,
      heatmapData,
      trendData,
      bookProgressData,
      circumference,
      wrongQuestions,
      learningRecords,
      timeSlots,
      learningTypes,
      getHeatColor,
      getProgressOffset,
      formatTime,
      reviewQuestion,
      loadMoreRecords,
      saveGoalSettings,
      formatTodayDate,
      getRecordIcon,
      getStatusText,
      getDifficultyStars
    }
  }
}
</script>

<style scoped>
.records-container {
  padding: 20px 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
  gap: 20px;
}

.goal-settings {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #666;
}

.goal-settings .btn-link {
  padding: 0;
  font-size: 14px;
  color: #409EFF;
}

.goal-settings .btn-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
}

.filter-select {
  min-width: 150px;
}

.overview-section {
  margin-bottom: 30px;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
}

/* 目标进度区域样式 */
.goal-progress-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 25px;
  margin-bottom: 30px;
}

.goal-progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.goal-progress-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.today-date {
  font-size: 14px;
  color: #666;
}

.today-goal-progress {
  width: 100%;
}

.goal-progress-bar {
  width: 100%;
  height: 20px;
  background-color: #e9ecef;
  border-radius: 10px;
  overflow: hidden;
  margin-bottom: 10px;
}

.goal-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #409EFF 0%, #67C23A 100%);
  border-radius: 10px;
  transition: width 0.5s ease;
}

.goal-progress-text {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #666;
}

.stat-card {
  background: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
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

.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 30px;
}

.chart-section {
  background: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 30px;
}

.chart-section h2 {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: #333;
}

/* 简化热力图样式 */
.simple-heatmap {
  width: 100%;
  padding: 10px 0;
}

.simple-heatmap-legend {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  margin-bottom: 15px;
  font-size: 12px;
  color: #666;
}

.simple-heatmap-colors {
  display: flex;
  gap: 2px;
}

.simple-heatmap-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  border: 1px solid #eee;
}

.simple-heatmap-grid {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.simple-heatmap-weekdays {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.simple-heatmap-weekday {
  width: 20px;
  height: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  color: #999;
}

.simple-heatmap-cells {
  display: flex;
  flex-wrap: wrap;
  gap: 2px;
  flex: 1;
}

.simple-heatmap-cell {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  border: 1px solid #eee;
  cursor: pointer;
  transition: all 0.2s ease;
  flex-shrink: 0;
}

.simple-heatmap-cell:hover {
  transform: scale(1.3);
  z-index: 1;
}

/* 确保即使没有数据也能看到一些格子 */
.simple-heatmap-cells > div {
  min-height: 12px;
  min-width: 12px;
}

.heatmap-cell {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  cursor: pointer;
  border: 1px solid #eee; /* 添加边框使其在任何背景下都可见 */
  transition: all 0.2s;
}

.heatmap-cell:hover {
  transform: scale(1.2);
  outline: 1px solid #333;
  z-index: 1;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .heatmap-cells {
    grid-template-columns: repeat(26, 1fr); /* 小屏幕减少列数 */
  }
  
  .heatmap-cell {
    width: 10px;
    height: 10px;
  }
}

/* 趋势图样式 */
.trend-chart {
  height: 200px;
}

.trend-bars {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 100%;
  padding-bottom: 20px;
}

.trend-bar {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
}

.bar {
  width: 20px;
  background: #409EFF;
  border-radius: 4px 4px 0 0;
  transition: height 0.3s;
}

.bar-label {
  font-size: 12px;
  color: #666;
}

/* 教材进度样式 */
.book-progress {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.book-progress-item {
  display: flex;
  align-items: center;
  gap: 30px;
}

.book-info {
  flex: 1;
}

.book-name {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 5px;
}

.progress-text {
  font-size: 14px;
  color: #409EFF;
  margin-bottom: 5px;
}

.book-stats {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #999;
}

.progress-ring {
  transform: rotate(-90deg);
}

.progress-ring-bg {
  stroke: #e0e0e0;
}

.progress-ring-fill {
  stroke-linecap: round;
  transition: stroke-dashoffset 0.3s;
}

.progress-text-center {
  transform: rotate(90deg);
  font-size: 12px;
  font-weight: bold;
  fill: #666;
}

/* 错题本样式 */
.wrong-questions {
  max-height: 400px;
  overflow-y: auto;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 40px;
}

.wrong-question-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  margin-bottom: 10px;
}

.question-info {
  flex: 1;
}

.question-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 5px;
}

.question-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #999;
  flex-wrap: wrap;
}

.question-actions {
  margin-left: 15px;
}

/* 学习记录列表样式 */
.learning-records {
  max-height: 400px;
  overflow-y: auto;
}

.learning-record-item {
  display: flex;
  align-items: center;
  padding: 15px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  margin-bottom: 10px;
  transition: background-color 0.3s;
}

.learning-record-item:hover {
  background-color: #f8f9fa;
}

.record-icon {
  font-size: 24px;
  margin-right: 15px;
  width: 30px;
  text-align: center;
}

.record-content {
  flex: 1;
}

.record-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 5px;
}

.record-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #999;
  flex-wrap: wrap;
}

.record-status {
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.record-status.completed {
  background-color: #f0f9eb;
  color: #67C23A;
}

.record-status.inProgress {
  background-color: #ecf5ff;
  color: #409EFF;
}

.view-more-btn {
  width: 100%;
  margin-top: 15px;
  color: #409EFF;
}

.view-more-btn:hover {
  color: #66b1ff;
  text-decoration: underline;
}

/* 学习习惯分析样式 */
.habit-analysis {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.habit-item {
  width: 100%;
}

.habit-title {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 15px;
  color: #333;
}

.time-slots {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  height: 150px;
  padding-bottom: 20px;
}

.time-slot {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  max-width: 40px;
  gap: 5px;
  cursor: pointer;
}

.time-slot .time-label {
  font-size: 12px;
  color: #666;
}

.time-slot.active {
  background-color: #409EFF;
  border-radius: 4px 4px 0 0;
}

.learning-types {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.learning-type {
  display: flex;
  align-items: center;
  gap: 10px;
}

.type-label {
  width: 60px;
  font-size: 14px;
  color: #666;
}

.type-progress {
  flex: 1;
  height: 10px;
  background-color: #e9ecef;
  border-radius: 5px;
  overflow: hidden;
}

.type-progress-fill {
  height: 100%;
  border-radius: 5px;
  transition: width 0.5s ease;
}

.type-percentage {
  width: 50px;
  font-size: 14px;
  color: #666;
  text-align: right;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.modal-close:hover {
  background-color: #f5f5f5;
  color: #333;
}

.modal-body {
  padding: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  color: #333;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #f0f0f0;
}

.btn-default {
  background-color: #f5f5f5;
  color: #666;
  border: none;
}

.btn-default:hover {
  background-color: #e9ecef;
}

@media (max-width: 1200px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .stat-cards {
    grid-template-columns: 1fr;
  }
  
  .book-progress-item {
    flex-direction: column;
    text-align: center;
  }
  
  .wrong-question-item {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .question-actions {
    margin-left: 0;
  }
}
</style>
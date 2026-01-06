<template>
  <div class="records-container">
    <div class="page-header">
      <div class="page-title-wrap">
        <h1>学习记录</h1>
        <p class="page-subtitle">回顾你的学习足迹，了解进度与习惯，持续优化学习方式</p>
      </div>
      <div class="header-actions">
        <div class="filter-row">
          <select v-model="filters.type" class="input filter-select">
            <option value="all">全部类型</option>
            <option value="reading">阅读/学习</option>
            <option value="practice">练习</option>
          </select>
          <select v-model="filters.status" class="input filter-select">
            <option value="all">全部状态</option>
            <option value="completed">已完成</option>
            <option value="inProgress">学习中</option>
          </select>
          <select v-model="timeRange" class="input filter-select">
            <option value="week">最近一周</option>
            <option value="month">最近一月</option>
            <option value="quarter">最近三月</option>
            <option value="year">最近一年</option>
          </select>
          <input type="date" v-model="filters.startDate" class="input date-input" />
          <span class="date-separator">至</span>
          <input type="date" v-model="filters.endDate" class="input date-input" />
          <button class="btn btn-primary" @click="applyFilters">筛选</button>
          <button class="btn btn-outline" @click="resetFilters">重置</button>
        </div>
        <div class="goal-settings">
          <div class="goal-text">
            <span class="goal-label">每日学习目标</span>
            <span class="goal-value">{{ dailyGoalHours }} 小时 / {{ dailyGoalChapters }} 章节</span>
          </div>
          <button class="btn-link" @click="showGoalModal = true">调整目标</button>
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
    <div class="goal-progress-section card">
      <div class="goal-progress-header">
        <div>
          <h3>今日学习目标</h3>
          <p class="goal-subtitle">坚持每天一点点，让进步变成习惯</p>
        </div>
        <span class="today-date">{{ formatTodayDate() }}</span>
      </div>
      <div class="today-goal-progress">
        <div class="progress-bar">
          <div 
            class="progress-bar-fill" 
            :style="{ width: todayProgressPercentage + '%' }"
          ></div>
        </div>
        <div class="goal-progress-text">
          <span>{{ todayHours }} / {{ dailyGoalHours }} 小时</span>
          <span class="goal-percent">{{ todayProgressPercentage }}%</span>
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
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/api.js'

export default {
  name: 'RecordsView',
  setup() {
    const router = useRouter()
    const timeRange = ref('month')
    const filters = reactive({
      type: 'all',
      status: 'all',
      startDate: '',
      endDate: '',
      page: 1,
      pageSize: 10,
      orderBy: '-timestamp'
    })
    
    // 统计数据（由真实数据计算）
    const totalLearningDays = ref(0)
    const totalHours = ref(0)
    const completedChapters = ref(0)
    const accuracyRate = ref(0)
    const currentStreak = ref(0) // 连续学习天数
    const goalCompletionRate = ref(0) // 目标达成率
    
    // 每日目标设置
    const dailyGoalHours = ref(Number(localStorage.getItem('dailyGoalHours')) || 2)
    const dailyGoalChapters = ref(Number(localStorage.getItem('dailyGoalChapters')) || 2)
    const todayHours = ref(0) // 今日已学习时长
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
    const totalRecords = ref(0)
    
    // 学习习惯数据（可后续基于真实数据优化）
    const timeSlots = ref([
      { time: '08:00', intensity: 2, active: true },
      { time: '12:00', intensity: 1, active: false },
      { time: '15:00', intensity: 3, active: true },
      { time: '18:00', intensity: 2, active: false },
      { time: '20:00', intensity: 4, active: true },
      { time: '22:00', intensity: 1, active: false }
    ])
    
    const learningTypes = ref([
      { name: '阅读', percentage: 0, color: '#409EFF' },
      { name: '视频', percentage: 0, color: '#E6A23C' },
      { name: '练习', percentage: 0, color: '#67C23A' }
    ])
    
    const applyFilters = () => {
      filters.page = 1
      loadData()
    }
    
    const resetFilters = () => {
      filters.type = 'all'
      filters.status = 'all'
      filters.startDate = ''
      filters.endDate = ''
      filters.page = 1
      filters.orderBy = '-timestamp'
      loadData()
    }
    
    const fetchActivities = async () => {
      const res = await api.getLearningActivities({
        startDate: filters.startDate,
        endDate: filters.endDate,
        type: filters.type,
        status: filters.status,
        orderBy: filters.orderBy,
        page: filters.page,
        pageSize: filters.pageSize
      })
      const results = Array.isArray(res?.results) ? res.results : []
      totalRecords.value = res?.total || results.length
      learningRecords.value = results.map(item => ({
        id: item.id,
        type: item.type,
        title: `${item.bookTitle || ''} - ${item.chapterTitle || ''}`,
        bookTitle: item.bookTitle,
        duration: item.duration || 30,
        status: item.status,
        timestamp: item.timestamp
      }))
      calcStats(results)
      buildTrendFromActivities(results)
      updateTodayHours(results)
    }
    
    const fetchHeatmap = async () => {
      try {
        const data = await api.getHeatmapData()
        heatmapData.value = (data || []).map(item => {
          const minutes = item.minutes || 0
          let intensity = 0
          if (minutes > 180) intensity = 4
          else if (minutes > 120) intensity = 3
          else if (minutes > 60) intensity = 2
          else if (minutes > 30) intensity = 1
          return {
            date: item.date,
            hours: minutes / 60,
            intensity
          }
        })
      } catch (e) {
        heatmapData.value = []
      }
    }
    
    const fetchPracticeStats = async () => {
      try {
        const records = await api.getPracticeRecords()
        if (Array.isArray(records) && records.length > 0) {
          const scores = records.map(r => r.score || 0)
          accuracyRate.value = Math.round(scores.reduce((a, b) => a + b, 0) / scores.length)
          const completed = records.filter(r => r.completed)
          completedChapters.value = completed.length
        } else {
          accuracyRate.value = 0
          completedChapters.value = 0
        }
      } catch (e) {
        accuracyRate.value = 0
        completedChapters.value = 0
      }
    }
    
    const fetchBooksProgress = async () => {
      try {
        const books = await api.getBooks()
        bookProgressData.value = books.map(book => ({
          id: book.id,
          title: book.title,
          progress: book.progress || 0,
          completedSections: book.completedSections || 0,
          totalSections: book.totalSections || book.chapterCount || 0,
          totalHours: book.totalHours || 0
        }))
      } catch (e) {
        bookProgressData.value = []
      }
    }
    
    const fetchWrongQuestions = async () => {
      try {
        wrongQuestions.value = await api.getWrongQuestions()
      } catch (e) {
        wrongQuestions.value = []
      }
    }
    
    const loadData = async () => {
      try {
        await Promise.all([
          fetchActivities(),
          fetchHeatmap(),
          fetchPracticeStats(),
          fetchBooksProgress(),
          fetchWrongQuestions()
        ])
      } catch (error) {
        console.error('加载学习记录失败:', error)
      }
    }
    
    const updateTodayHours = (activities) => {
      const today = new Date().toISOString().slice(0, 10)
      const minutes = activities
        .filter(a => (a.timestamp || '').slice(0, 10) === today)
        .reduce((sum, a) => sum + (a.duration || 30), 0)
      todayHours.value = Math.round((minutes / 60) * 10) / 10
      goalCompletionRate.value = Math.min(100, Math.round((todayHours.value / dailyGoalHours.value) * 100))
    }
    
    const calcStats = (activities) => {
      const dates = new Set()
      let minutes = 0
      const typeCounter = {
        reading: 0,
        video: 0,
        practice: 0
      }

      activities.forEach(a => {
        const dateStr = (a.timestamp || '').slice(0, 10)
        if (dateStr) dates.add(dateStr)
        minutes += a.duration || 30
        // 统计不同类型学习次数
        if (a.type && typeCounter.hasOwnProperty(a.type)) {
          typeCounter[a.type] += 1
        }
      })
      totalLearningDays.value = dates.size
      totalHours.value = Math.round((minutes / 60) * 10) / 10

      // 更新学习类型分布百分比
      const totalCount = Object.values(typeCounter).reduce((sum, val) => sum + val, 0)
      if (totalCount > 0) {
        const readingPercent = Math.round((typeCounter.reading / totalCount) * 100)
        const practicePercent = Math.round((typeCounter.practice / totalCount) * 100)
        const videoPercent = 100 - readingPercent - practicePercent
        learningTypes.value = [
          { name: '阅读', percentage: readingPercent, color: '#409EFF' },
          { name: '视频', percentage: Math.max(0, videoPercent), color: '#E6A23C' },
          { name: '练习', percentage: practicePercent, color: '#67C23A' }
        ]
      } else {
        learningTypes.value = [
          { name: '阅读', percentage: 0, color: '#409EFF' },
          { name: '视频', percentage: 0, color: '#E6A23C' },
          { name: '练习', percentage: 0, color: '#67C23A' }
        ]
      }
      
      // 简单连续天数计算
      const sortedDates = Array.from(dates).sort().reverse()
      let streak = 0
      let cursor = new Date()
      sortedDates.forEach(d => {
        const day = new Date(d)
        if (Math.abs((cursor - day) / (1000 * 60 * 60 * 24)) <= 1) {
          streak += 1
          cursor = day
        }
      })
      currentStreak.value = streak
    }
    
    const buildTrendFromActivities = (activities) => {
      const daysCount = timeRange.value === 'week' ? 7 : 30
      const map = new Map()
      for (let i = daysCount - 1; i >= 0; i--) {
        const d = new Date()
        d.setDate(d.getDate() - i)
        const key = d.toISOString().slice(0, 10)
        map.set(key, 0)
      }
      activities.forEach(a => {
        const key = (a.timestamp || '').slice(0, 10)
        if (map.has(key)) {
          map.set(key, map.get(key) + (a.duration || 30) / 60)
        }
      })
      trendData.value = Array.from(map.entries()).map(([date, hours]) => ({
        day: date.slice(5),
        hours: Math.round(hours * 10) / 10
      }))
    }
    
    // 分页
    const loadMoreRecords = () => {
      if (filters.page * filters.pageSize >= totalRecords.value) return
      filters.page += 1
      fetchActivities()
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
      filters,
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
      applyFilters,
      resetFilters,
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
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 18px;
  flex-wrap: wrap;
  gap: 15px;
  padding-bottom: 12px;
  border-bottom: 1px solid #eee;
}

.page-title-wrap h1 {
  margin: 0;
  font-size: 28px;
  font-weight: 600;
  color: #333;
  line-height: 1.3;
}

.page-subtitle {
  margin-top: 8px;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.header-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
  align-items: flex-end;
}

.filter-row {
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  gap: 8px;
  justify-content: flex-end;
  overflow-x: auto;
  padding: 4px 0;
}

.filter-row::-webkit-scrollbar {
  height: 4px;
}

.filter-row::-webkit-scrollbar-thumb {
  background-color: #ddd;
  border-radius: 2px;
}

.filter-row::-webkit-scrollbar-track {
  background-color: #f5f5f5;
}

.goal-settings {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  color: #666;
}

.goal-text {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.goal-label {
  font-size: 12px;
  color: #999;
}

.goal-value {
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.btn-link {
  padding: 0;
  font-size: 14px;
  color: #409EFF;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.3s ease;
}

.btn-link:hover {
  color: #66b1ff;
  text-decoration: underline;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
}

.filter-select {
  min-width: 130px;
}

.date-input {
  min-width: 140px;
}

.date-separator {
  color: #999;
  font-size: 14px;
  margin: 0 5px;
}

.overview-section {
  margin-bottom: 20px;
}

.stat-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
  gap: 8px;
}

/* 目标进度区域样式 */
.goal-progress-section {
  margin-bottom: 15px;
}

.goal-progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

/* 响应式布局 */


.goal-progress-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
}

.goal-subtitle {
  margin-top: 6px;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.today-date {
  font-size: 14px;
  color: #666;
}

.today-goal-progress {
  width: 100%;
}

.today-goal-progress .progress-bar {
  height: 12px;
  margin-bottom: 10px;
}

.today-goal-progress .progress-bar-fill {
  background: linear-gradient(90deg, #409EFF 0%, #67C23A 100%);
}

.goal-progress-text {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.goal-percent {
  font-weight: 500;
  color: #409EFF;
}

.stat-card {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  text-align: center;
  transition: box-shadow 0.3s ease;
}

.stat-card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #409EFF;
  margin-bottom: 8px;
  line-height: 1.2;
}

.stat-label {
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.main-content {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 12px;
  margin-top: 12px;
}

.chart-section {
  background: white;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  margin-bottom: 10px;
  transition: box-shadow 0.3s ease;
}

.chart-section:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.chart-section h2 {
  margin: 0 0 15px 0;
  font-size: 18px;
  font-weight: 600;
  color: #333;
  line-height: 1.4;
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
  gap: 15px;
}

.book-progress-item {
  display: flex;
  align-items: center;
  gap: 20px;
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
  padding: 10px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  margin-bottom: 6px;
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
  padding: 10px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  margin-bottom: 6px;
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
  gap: 15px;
}

.habit-item {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.habit-title {
  font-size: 14px;
  font-weight: 500;
  color: #666;
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
  width: 92%;
  max-width: 460px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 20px;
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
    gap: 20px;
  }
}

@media (max-width: 768px) {
  .records-container {
    padding: 15px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }

  .header-actions {
    width: 100%;
    align-items: stretch;
  }

  .filter-row {
    flex-direction: column;
    justify-content: flex-start;
  }

  .filter-select,
  .date-input {
    width: 100%;
  }

  .stat-cards {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .stat-card {
    padding: 16px;
  }

  .stat-value {
    font-size: 28px;
  }

  .main-content {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .chart-section {
    padding: 15px;
    margin-bottom: 15px;
  }

  .chart-section h2 {
    font-size: 18px;
  }

  .goal-progress-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }

  .today-goal-progress .progress-bar {
    height: 10px;
  }

  .page-title-wrap h1 {
    font-size: 24px;
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
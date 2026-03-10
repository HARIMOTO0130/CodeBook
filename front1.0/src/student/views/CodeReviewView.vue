<template>
  <div class="code-review-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>智能代码审查</h1>
      <p>使用AI技术分析代码质量，提供改进建议，帮助提升编程技能</p>
    </div>

    <!-- 功能导航 -->
    <div class="feature-nav">
      <div class="nav-item" :class="{ active: activeFeature === 'review' }" @click="activeFeature = 'review'">
        <span class="nav-icon">🔍</span>
        <span class="nav-label">代码审查</span>
      </div>
      <div class="nav-item" :class="{ active: activeFeature === 'history' }" @click="activeFeature = 'history'">
        <span class="nav-icon">📊</span>
        <span class="nav-label">审查历史</span>
      </div>
      <div class="nav-item" :class="{ active: activeFeature === 'stats' }" @click="activeFeature = 'stats'">
        <span class="nav-icon">📈</span>
        <span class="nav-label">统计报告</span>
      </div>
    </div>

    <!-- 功能内容区域 -->
    <div class="feature-content">
      <!-- 代码审查功能 -->
      <div v-if="activeFeature === 'review'" class="feature-panel">
        <CodeReviewComponent ref="codeReviewComponent" />
      </div>

      <!-- 审查历史功能 -->
      <div v-if="activeFeature === 'history'" class="feature-panel">
        <div class="history-section">
          <div class="section-header">
            <h3>审查历史记录</h3>
            <div class="history-controls">
              <button @click="refreshHistory" class="btn btn-secondary">刷新</button>
            </div>
          </div>

          <div v-if="loadingHistory" class="loading-state">
            <div class="loading-spinner"></div>
            <p>加载历史记录中...</p>
          </div>

          <div v-else-if="historyRecords.length === 0" class="empty-state">
            <p>暂无审查记录</p>
            <p class="empty-hint">开始使用代码审查功能来创建记录</p>
          </div>

          <div v-else class="history-list">
            <div v-for="record in historyRecords" :key="record.id" class="history-item" @click="viewHistoryDetail(record.id)">
              <div class="history-info">
                <div class="history-score" :style="{ color: getScoreColor(record.overall_score) }">
                  {{ record.overall_score }}
                </div>
                <div class="history-details">
                  <div class="history-language">
                    <span class="lang-icon">{{ getLanguageIcon(record.language) }}</span>
                    <span>{{ record.language }}</span>
                  </div>
                  <div class="history-time">{{ formatTime(record.created_at) }}</div>
                </div>
              </div>
              <div class="history-actions">
                <button @click.stop="viewHistoryDetail(record.id)" class="btn btn-sm btn-primary">查看详情</button>
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

      <!-- 统计报告功能 -->
      <div v-if="activeFeature === 'stats'" class="feature-panel">
        <div class="stats-section">
          <div class="section-header">
            <h3>代码审查统计</h3>
            <button @click="refreshStats" class="btn btn-secondary">刷新数据</button>
          </div>

          <div v-if="loadingStats" class="loading-state">
            <div class="loading-spinner"></div>
            <p>加载统计数据中...</p>
          </div>

          <div v-else-if="!statsData" class="empty-state">
            <p>暂无统计数据</p>
          </div>

          <div v-else class="stats-content">
            <!-- 基础统计 -->
            <div class="stats-overview">
              <div class="stat-card">
                <div class="stat-value">{{ statsData.total_reviews }}</div>
                <div class="stat-label">总审查次数</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ statsData.average_score }}</div>
                <div class="stat-label">平均分数</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ statsData.valid_reviews }}</div>
                <div class="stat-label">有效审查</div>
              </div>
            </div>

            <!-- 语言分布 -->
            <div class="stats-chart">
              <h4>语言分布</h4>
              <div class="chart-container">
                <div 
                  v-for="(count, lang) in statsData.language_distribution" 
                  :key="lang"
                  class="chart-item"
                >
                  <div class="chart-bar" :style="{ height: (count / maxLanguageCount) * 100 + '%' }"></div>
                  <div class="chart-label">
                    <span class="lang-icon">{{ getLanguageIcon(lang) }}</span>
                    <span>{{ lang }}</span>
                    <span class="chart-count">{{ count }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 最近活动 -->
            <div class="stats-activity">
              <h4>最近30天活动</h4>
              <div class="activity-grid">
                <div 
                  v-for="(count, date) in statsData.recent_activity" 
                  :key="date"
                  class="activity-day"
                  :class="{ active: count > 0 }"
                  :style="{ opacity: Math.min(count / maxActivityCount, 1) * 0.8 + 0.2 }"
                >
                  <div class="activity-count">{{ count }}</div>
                  <div class="activity-date">{{ formatActivityDate(date) }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 历史详情模态框 -->
    <div v-if="showHistoryDetail" class="modal-overlay" @click="closeHistoryDetail">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>审查记录详情</h3>
          <button @click="closeHistoryDetail" class="btn-close">×</button>
        </div>
        <div class="modal-body">
          <div v-if="loadingDetail" class="loading-state">
            <div class="loading-spinner"></div>
            <p>加载详情中...</p>
          </div>
          <div v-else-if="historyDetail" class="detail-content">
            <!-- 详情内容实现 -->
            <p>详情内容待实现...</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import CodeReviewComponent from '../components/CodeReviewComponent.vue'
import { codeReviewAPI, codeReviewUtils } from '../api/code_review_api'

export default {
  name: 'CodeReviewView',
  
  components: {
    CodeReviewComponent
  },

  data() {
    return {
      activeFeature: 'review',
      historyRecords: [],
      statsData: null,
      loadingHistory: false,
      loadingStats: false,
      loadingDetail: false,
      showHistoryDetail: false,
      historyDetail: null,
      currentPage: 1,
      pageSize: 10,
      totalCount: 0
    }
  },

  computed: {
    totalPages() {
      return Math.ceil(this.totalCount / this.pageSize)
    },

    maxLanguageCount() {
      if (!this.statsData?.language_distribution) return 1
      return Math.max(...Object.values(this.statsData.language_distribution))
    },

    maxActivityCount() {
      if (!this.statsData?.recent_activity) return 1
      return Math.max(...Object.values(this.statsData.recent_activity))
    }
  },

  methods: {
    getScoreColor(score) {
      return codeReviewUtils.getScoreLevel(score).color
    },

    getLanguageIcon(language) {
      const icons = {
        python: '🐍',
        javascript: '📜',
        java: '☕',
        cpp: '⚡',
        csharp: '🔷',
        unknown: '❓'
      }
      return icons[language] || icons.unknown
    },

    formatTime(timestamp) {
      return new Date(timestamp).toLocaleString('zh-CN')
    },

    formatActivityDate(dateStr) {
      const date = new Date(dateStr)
      return date.getDate()
    },

    async loadHistory() {
      this.loadingHistory = true
      try {
        const offset = (this.currentPage - 1) * this.pageSize
        const response = await codeReviewAPI.getCodeReviewHistory(this.pageSize, offset)
        this.historyRecords = response.history || []
        this.totalCount = response.total_count || 0
      } catch (error) {
        console.error('加载历史记录失败:', error)
        this.historyRecords = []
      } finally {
        this.loadingHistory = false
      }
    },

    async loadStats() {
      this.loadingStats = true
      try {
        const response = await codeReviewAPI.getCodeReviewStats()
        this.statsData = response
      } catch (error) {
        console.error('加载统计数据失败:', error)
        this.statsData = null
      } finally {
        this.loadingStats = false
      }
    },

    async viewHistoryDetail(recordId) {
      this.loadingDetail = true
      this.showHistoryDetail = true
      
      try {
        const response = await codeReviewAPI.getCodeReviewDetail(recordId)
        this.historyDetail = response
      } catch (error) {
        console.error('加载详情失败:', error)
        this.historyDetail = null
      } finally {
        this.loadingDetail = false
      }
    },

    closeHistoryDetail() {
      this.showHistoryDetail = false
      this.historyDetail = null
    },

    refreshHistory() {
      this.currentPage = 1
      this.loadHistory()
    },

    refreshStats() {
      this.loadStats()
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
    }
  },

  watch: {
    activeFeature(newFeature) {
      if (newFeature === 'history' && this.historyRecords.length === 0) {
        this.loadHistory()
      } else if (newFeature === 'stats' && !this.statsData) {
        this.loadStats()
      }
    }
  },

  mounted() {
    // 页面加载时初始化数据
    this.loadHistory()
    this.loadStats()
  }
}
</script>

<style scoped>
.code-review-view {
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

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  background: #f7fafc;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  background: #edf2f7;
  transform: translateY(-1px);
}

.history-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.history-score {
  font-size: 24px;
  font-weight: bold;
  min-width: 50px;
}

.history-details {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.history-language {
  display: flex;
  align-items: center;
  gap: 5px;
  font-weight: bold;
}

.history-time {
  font-size: 12px;
  color: #718096;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 12px;
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

.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  text-align: center;
  padding: 20px;
  background: #f7fafc;
  border-radius: 8px;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #4299e1;
  margin-bottom: 5px;
}

.stat-label {
  color: #718096;
  font-size: 14px;
}

.stats-chart {
  margin-bottom: 30px;
}

.stats-chart h4 {
  margin-bottom: 15px;
  color: #2d3748;
}

.chart-container {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  height: 200px;
  padding: 20px;
  background: #f7fafc;
  border-radius: 8px;
}

.chart-item {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.chart-bar {
  width: 30px;
  background: #4299e1;
  border-radius: 3px 3px 0 0;
  transition: height 0.3s;
}

.chart-label {
  margin-top: 10px;
  text-align: center;
  font-size: 12px;
}

.chart-count {
  display: block;
  font-weight: bold;
  margin-top: 2px;
}

.stats-activity h4 {
  margin-bottom: 15px;
  color: #2d3748;
}

.activity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(40px, 1fr));
  gap: 5px;
}

.activity-day {
  text-align: center;
  padding: 10px 5px;
  background: #f7fafc;
  border-radius: 4px;
  font-size: 12px;
}

.activity-day.active {
  background: #4299e1;
  color: white;
}

.activity-count {
  font-weight: bold;
  margin-bottom: 2px;
}

.activity-date {
  opacity: 0.7;
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
  max-width: 600px;
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

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .code-review-view {
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
  
  .stats-overview {
    grid-template-columns: 1fr;
  }
  
  .chart-container {
    flex-direction: column;
    height: auto;
  }
  
  .chart-item {
    flex-direction: row;
    align-items: center;
    height: auto;
  }
  
  .chart-bar {
    width: 100%;
    height: 20px;
    border-radius: 3px;
  }
  
  .activity-grid {
    grid-template-columns: repeat(7, 1fr);
  }
}
</style>
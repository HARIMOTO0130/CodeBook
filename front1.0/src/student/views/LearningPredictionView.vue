<template>
  <div class="learning-prediction-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>学习效果预测</h1>
      <p>基于历史数据预测学习效果，提前干预，优化学习路径</p>
    </div>

    <!-- 功能导航 -->
    <div class="feature-nav">
      <div class="nav-item" :class="{ active: activeFeature === 'prediction' }" @click="activeFeature = 'prediction'">
        <span class="nav-icon">📊</span>
        <span class="nav-label">预测结果</span>
      </div>
      <div class="nav-item" :class="{ active: activeFeature === 'history' }" @click="activeFeature = 'history'">
        <span class="nav-icon">📈</span>
        <span class="nav-label">历史趋势</span>
      </div>
      <div class="nav-item" :class="{ active: activeFeature === 'stats' }" @click="activeFeature = 'stats'">
        <span class="nav-icon">📋</span>
        <span class="nav-label">统计分析</span>
      </div>
    </div>

    <!-- 功能内容区域 -->
    <div class="feature-content">
      <!-- 预测结果功能 -->
      <div v-if="activeFeature === 'prediction'" class="feature-panel">
        <LearningPredictionComponent ref="learningPredictionComponent" />
      </div>

      <!-- 历史趋势功能 -->
      <div v-if="activeFeature === 'history'" class="feature-panel">
        <div class="history-section">
          <div class="section-header">
            <h3>学习历史趋势</h3>
            <div class="history-controls">
              <div class="days-selector">
                <label for="history-days">历史天数:</label>
                <select v-model="historyDays" id="history-days" @change="loadHistory" class="select">
                  <option value="7">7天</option>
                  <option value="14">14天</option>
                  <option value="30">30天</option>
                  <option value="60">60天</option>
                </select>
              </div>
              <button @click="loadHistory" :disabled="isLoadingHistory" class="btn btn-primary">
                {{ isLoadingHistory ? '加载中...' : '加载历史' }}
              </button>
            </div>
          </div>

          <div v-if="isLoadingHistory" class="loading-state">
            <div class="loading-spinner"></div>
            <p>加载历史数据中...</p>
          </div>

          <div v-else-if="historyData.length === 0" class="empty-state">
            <p>暂无历史数据</p>
            <p class="empty-hint">开始学习后将生成历史数据</p>
          </div>

          <div v-else class="history-content">
            <!-- 趋势图表 -->
            <div class="chart-section">
              <h4>学习评分趋势</h4>
              <div class="chart-container">
                <canvas ref="historyChart"></canvas>
              </div>
            </div>

            <!-- 历史数据表格 -->
            <div class="table-section">
              <h4>详细历史记录</h4>
              <div class="history-table">
                <table>
                  <thead>
                    <tr>
                      <th>日期</th>
                      <th>学习评分</th>
                      <th>掌握度</th>
                      <th>风险等级</th>
                      <th>实际掌握度</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(item, index) in historyData" :key="index">
                      <td>{{ item.dateFormatted }}</td>
                      <td>{{ Math.round(item.score * 100) }}%</td>
                      <td>{{ Math.round(item.predicted_mastery * 100) }}%</td>
                      <td>
                        <span 
                          class="risk-badge"
                          :style="{ backgroundColor: item.riskInfo.color }"
                        >
                          {{ item.riskInfo.label }}
                        </span>
                      </td>
                      <td>{{ Math.round(item.actual_mastery * 100) }}%</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 统计分析功能 -->
      <div v-if="activeFeature === 'stats'" class="feature-panel">
        <div class="stats-section">
          <div class="section-header">
            <h3>学习统计分析</h3>
            <button @click="loadStats" :disabled="isLoadingStats" class="btn btn-primary">
              {{ isLoadingStats ? '加载中...' : '刷新统计' }}
            </button>
          </div>

          <div v-if="isLoadingStats" class="loading-state">
            <div class="loading-spinner"></div>
            <p>加载统计数据中...</p>
          </div>

          <div v-else-if="!statsData" class="empty-state">
            <p>暂无统计数据</p>
          </div>

          <div v-else class="stats-content">
            <!-- 概览统计 -->
            <div class="overview-stats">
              <div class="stat-card">
                <div class="stat-value">{{ Math.round(statsData.average_score * 100) }}%</div>
                <div class="stat-label">平均评分</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ Math.round(statsData.average_mastery * 100) }}%</div>
                <div class="stat-label">平均掌握度</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ Math.round(statsData.max_score * 100) }}%</div>
                <div class="stat-label">最高评分</div>
              </div>
              <div class="stat-card">
                <div class="stat-value">{{ Math.round(statsData.min_score * 100) }}%</div>
                <div class="stat-label">最低评分</div>
              </div>
            </div>

            <!-- 趋势分析 -->
            <div class="trend-analysis">
              <h4>学习趋势</h4>
              <div class="trend-card" :class="trendDirection">
                <div class="trend-icon">{{ trendIcon }}</div>
                <div class="trend-content">
                  <div class="trend-value">{{ trendValue }}%</div>
                  <div class="trend-description">{{ statsData.score_trend_description }}</div>
                </div>
              </div>
            </div>

            <!-- 风险分布 -->
            <div class="risk-distribution">
              <h4>风险分布</h4>
              <div class="distribution-chart">
                <div class="distribution-item">
                  <div class="distribution-bar" :style="{ width: (statsData.risk_distribution.high / statsData.total_predictions * 100) + '%' }">
                    <span class="distribution-value">{{ statsData.risk_distribution.high }}</span>
                  </div>
                  <div class="distribution-label">高风险</div>
                </div>
                <div class="distribution-item">
                  <div class="distribution-bar medium" :style="{ width: (statsData.risk_distribution.medium / statsData.total_predictions * 100) + '%' }">
                    <span class="distribution-value">{{ statsData.risk_distribution.medium }}</span>
                  </div>
                  <div class="distribution-label">中等风险</div>
                </div>
                <div class="distribution-item">
                  <div class="distribution-bar low" :style="{ width: (statsData.risk_distribution.low / statsData.total_predictions * 100) + '%' }">
                    <span class="distribution-value">{{ statsData.risk_distribution.low }}</span>
                  </div>
                  <div class="distribution-label">低风险</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LearningPredictionComponent from '../components/LearningPredictionComponent.vue'
import { learningPredictionAPI, learningPredictionUtils } from '../api/learning_prediction_api'
import Chart from 'chart.js/auto'

export default {
  name: 'LearningPredictionView',
  
  components: {
    LearningPredictionComponent
  },

  data() {
    return {
      activeFeature: 'prediction',
      historyData: [],
      statsData: null,
      isLoadingHistory: false,
      isLoadingStats: false,
      historyDays: 30,
      historyChart: null
    }
  },

  computed: {
    trendDirection() {
      if (!this.statsData) return 'stable'
      const trend = this.statsData.score_trend
      if (trend > 0.05) return 'up'
      if (trend < -0.05) return 'down'
      return 'stable'
    },

    trendIcon() {
      if (!this.statsData) return '➡️'
      const trend = this.statsData.score_trend
      if (trend > 0.05) return '📈'
      if (trend < -0.05) return '📉'
      return '➡️'
    },

    trendValue() {
      if (!this.statsData) return '0'
      return Math.abs(Math.round(this.statsData.score_trend * 100))
    }
  },

  methods: {
    async loadHistory() {
      this.isLoadingHistory = true
      
      try {
        const result = await learningPredictionAPI.getPredictionHistory(this.historyDays)
        if (result.history) {
          this.historyData = learningPredictionUtils.formatHistory(result.history)
          this.renderHistoryChart()
        }
      } catch (error) {
        console.error('加载历史数据失败:', error)
        // 使用模拟数据
        this.historyData = this.generateMockHistory()
        this.renderHistoryChart()
      } finally {
        this.isLoadingHistory = false
      }
    },

    async loadStats() {
      this.isLoadingStats = true
      
      try {
        const result = await learningPredictionAPI.getPredictionStats()
        if (result.stats) {
          this.statsData = {
            ...result.stats,
            score_trend_description: this.getTrendDescription(result.stats.score_trend)
          }
        }
      } catch (error) {
        console.error('加载统计数据失败:', error)
        // 使用模拟数据
        this.statsData = this.generateMockStats()
      } finally {
        this.isLoadingStats = false
      }
    },

    renderHistoryChart() {
      // 销毁旧图表
      if (this.historyChart) {
        this.historyChart.destroy()
      }
      
      // 获取图表容器
      const chartElement = this.$refs.historyChart
      if (!chartElement) {
        console.warn('图表容器不存在')
        return
      }
      
      const ctx = chartElement.getContext('2d')
      if (!ctx) {
        console.warn('无法获取图表上下文')
        return
      }
      
      // 准备图表数据
      let labels, scores, masteries, actuals
      if (this.historyData.length > 0) {
        labels = this.historyData.map(item => item.dateFormatted)
        scores = this.historyData.map(item => item.score * 100)
        masteries = this.historyData.map(item => item.predicted_mastery * 100)
        actuals = this.historyData.map(item => item.actual_mastery * 100)
      } else {
        // 生成模拟数据
        const mockData = this.generateMockChartData()
        labels = mockData.labels
        scores = mockData.scores
        masteries = mockData.masteries
        actuals = mockData.actuals
      }
      
      // 创建新图表
      this.historyChart = new Chart(ctx, {
        type: 'line',
        data: {
          labels,
          datasets: [
            {
              label: '学习评分',
              data: scores,
              borderColor: '#4299e1',
              backgroundColor: 'rgba(66, 153, 225, 0.1)',
              tension: 0.4
            },
            {
              label: '预测掌握度',
              data: masteries,
              borderColor: '#38a169',
              backgroundColor: 'rgba(56, 161, 105, 0.1)',
              tension: 0.4
            },
            {
              label: '实际掌握度',
              data: actuals,
              borderColor: '#ed8936',
              backgroundColor: 'rgba(237, 137, 54, 0.1)',
              tension: 0.4,
              borderDash: [5, 5]
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
            },
            tooltip: {
              mode: 'index',
              intersect: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              max: 100,
              title: {
                display: true,
                text: '百分比 (%)'
              }
            },
            x: {
              title: {
                display: true,
                text: '日期'
              }
            }
          }
        }
      })
    },

    generateMockChartData() {
      const labels = []
      const scores = []
      const masteries = []
      const actuals = []
      
      const today = new Date()
      for (let i = 30; i > 0; i--) {
        const date = new Date(today)
        date.setDate(today.getDate() - i)
        labels.push(date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }))
        const score = 60 + Math.sin(i / 7) * 20 + Math.random() * 10
        scores.push(score)
        masteries.push(score * 1.1)
        actuals.push(score * 1.05)
      }
      
      return { labels, scores, masteries, actuals }
    },

    getTrendDescription(trend) {
      if (trend > 0.05) {
        return '学习效果呈上升趋势'
      } else if (trend < -0.05) {
        return '学习效果呈下降趋势'
      } else {
        return '学习效果保持稳定'
      }
    },

    generateMockHistory() {
      const history = []
      const today = new Date()
      
      for (let i = this.historyDays; i > 0; i--) {
        const date = new Date(today)
        date.setDate(today.getDate() - i)
        
        // 生成模拟数据
        const score = 0.5 + Math.sin(i / 7) * 0.2 + Math.random() * 0.1
        const mastery = score * 1.1
        const actualMastery = score * 1.05
        
        history.push({
          date: date.toISOString(),
          dateFormatted: date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' }),
          score: Math.max(0, Math.min(1, score)),
          predicted_mastery: Math.max(0, Math.min(1, mastery)),
          actual_mastery: Math.max(0, Math.min(1, actualMastery)),
          risk_level: score > 0.6 ? 'low' : score > 0.4 ? 'medium' : 'high',
          riskInfo: learningPredictionUtils.getRiskLevelInfo(score > 0.6 ? 'low' : score > 0.4 ? 'medium' : 'high')
        })
      }
      
      return history
    },

    generateMockStats() {
      return {
        average_score: 0.7,
        average_mastery: 0.75,
        max_score: 0.9,
        min_score: 0.5,
        score_trend: 0.03,
        score_trend_description: '学习效果呈上升趋势',
        risk_distribution: { high: 5, medium: 10, low: 15 },
        total_predictions: 30
      }
    }
  },

  watch: {
    activeFeature(newFeature) {
      if (newFeature === 'history' && this.historyData.length === 0) {
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
  },

  updated() {
    // 组件更新后重新渲染图表
    if (this.activeFeature === 'history' && this.historyData.length > 0) {
      this.$nextTick(() => {
        this.renderHistoryChart()
      })
    }
  },

  beforeUnmount() {
    // 组件卸载时销毁图表
    if (this.historyChart) {
      this.historyChart.destroy()
    }
  }
}
</script>

<style scoped>
.learning-prediction-view {
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

.history-controls {
  display: flex;
  align-items: center;
  gap: 20px;
}

.days-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.select {
  padding: 8px 12px;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  background: white;
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
  margin-top: 10px;
}

.chart-section {
  margin-bottom: 30px;
}

.chart-section h4 {
  margin-bottom: 15px;
  color: #2d3748;
}

.chart-container {
  height: 300px;
  background: #f7fafc;
  border-radius: 8px;
  padding: 20px;
}

.table-section {
  margin-top: 30px;
}

.table-section h4 {
  margin-bottom: 15px;
  color: #2d3748;
}

.history-table {
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

table th, table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}

table th {
  background: #f7fafc;
  font-weight: bold;
  color: #4a5568;
}

table tr:hover {
  background: #f7fafc;
}

.risk-badge {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.overview-stats {
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

.trend-analysis {
  margin-bottom: 30px;
}

.trend-analysis h4 {
  margin-bottom: 15px;
  color: #2d3748;
}

.trend-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  background: #f7fafc;
  border-radius: 8px;
  transition: all 0.2s;
}

.trend-card.up {
  background: #c6f6d5;
  border: 1px solid #68d391;
}

.trend-card.down {
  background: #fed7d7;
  border: 1px solid #fc8181;
}

.trend-card.stable {
  background: #ebf8ff;
  border: 1px solid #90cdf4;
}

.trend-icon {
  font-size: 48px;
}

.trend-content {
  flex: 1;
}

.trend-value {
  font-size: 24px;
  font-weight: bold;
  color: #2d3748;
  margin-bottom: 5px;
}

.trend-description {
  color: #718096;
}

.risk-distribution {
  margin-top: 30px;
}

.risk-distribution h4 {
  margin-bottom: 15px;
  color: #2d3748;
}

.distribution-chart {
  display: flex;
  flex-direction: column;
  gap: 15px;
  background: #f7fafc;
  padding: 20px;
  border-radius: 8px;
}

.distribution-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.distribution-bar {
  flex: 1;
  height: 30px;
  background: #e53e3e;
  border-radius: 4px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  color: white;
  font-weight: bold;
  font-size: 12px;
}

.distribution-bar.medium {
  background: #ed8936;
}

.distribution-bar.low {
  background: #38a169;
}

.distribution-label {
  min-width: 80px;
  font-size: 14px;
  color: #4a5568;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .learning-prediction-view {
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
  
  .history-controls {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .days-selector {
    justify-content: space-between;
  }
  
  .overview-stats {
    grid-template-columns: 1fr;
  }
  
  .trend-card {
    flex-direction: column;
    text-align: center;
  }
}
</style>
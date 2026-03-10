<template>
  <div class="learning-analytics-component">
    <!-- 分析结果卡片 -->
    <div class="analytics-card">
      <div class="card-header">
        <h3>学习智能分析</h3>
        <button @click="refreshAnalytics" :disabled="isLoading" class="btn btn-primary">
          {{ isLoading ? '分析中...' : '刷新分析' }}
        </button>
      </div>
      
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在分析学习数据...</p>
      </div>
      
      <div v-else-if="!analysis" class="empty-state">
        <p>暂无分析数据</p>
        <p class="empty-hint">点击"刷新分析"按钮获取学习智能分析</p>
      </div>
      
      <div v-else class="analytics-content">
        <!-- 核心指标 -->
        <div class="core-metrics">
          <div class="metric-card">
            <div class="metric-icon">📊</div>
            <div class="metric-content">
              <div class="metric-value">{{ efficiencyInfo.label }}</div>
              <div class="metric-label">学习效率</div>
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-icon">⏰</div>
            <div class="metric-content">
              <div class="metric-value">{{ timePreferenceInfo.label }}</div>
              <div class="metric-label">时间偏好</div>
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-icon">📅</div>
            <div class="metric-content">
              <div class="metric-value">{{ frequencyPatternInfo.label }}</div>
              <div class="metric-label">学习频率</div>
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-icon">📈</div>
            <div class="metric-content">
              <div class="metric-value">{{ completionRate }}%</div>
              <div class="metric-label">学习完成率</div>
            </div>
          </div>
        </div>
        
        <!-- 学习时间分布 -->
        <div class="chart-section">
          <h4>学习时间分布</h4>
          <div class="chart-container">
            <canvas ref="timeDistributionChart"></canvas>
          </div>
        </div>
        
        <!-- 学习内容分布 -->
        <div class="chart-section">
          <h4>学习内容分布</h4>
          <div class="chart-container">
            <canvas ref="contentDistributionChart"></canvas>
          </div>
        </div>
        
        <!-- 学习效率分析 -->
        <div class="chart-section">
          <h4>学习效率分析</h4>
          <div class="chart-container">
            <canvas ref="efficiencyChart"></canvas>
          </div>
        </div>
        
        <!-- 学习建议 -->
        <div class="recommendations-section">
          <h4>个性化学习建议</h4>
          <div v-if="recommendations.length === 0" class="no-recommendations">
            <p>🎉 学习状态良好，暂无建议</p>
          </div>
          <div v-else class="recommendations-list">
            <div 
              v-for="(recommendation, index) in recommendations" 
              :key="index"
              class="recommendation-card"
            >
              <div class="recommendation-header">
                <div class="recommendation-meta">
                  <span class="recommendation-icon">{{ recommendation.priorityInfo.icon }}</span>
                  <span class="recommendation-title">{{ recommendation.title }}</span>
                  <span 
                    class="recommendation-priority"
                    :style="{ backgroundColor: recommendation.priorityInfo.color }"
                  >
                    {{ recommendation.priorityInfo.label }}
                  </span>
                </div>
                <span class="recommendation-time">{{ recommendation.estimatedTimeFormatted }}</span>
              </div>
              <div class="recommendation-description">{{ recommendation.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { learningAnalyticsAPI, learningAnalyticsUtils, learningAnalyticsExamples } from '../api/learning_analytics_api'
import Chart from 'chart.js/auto'

export default {
  name: 'LearningAnalyticsComponent',
  
  data() {
    return {
      isLoading: false,
      analysis: null,
      recommendations: [],
      timeDistributionChart: null,
      contentDistributionChart: null,
      efficiencyChart: null
    }
  },

  computed: {
    efficiencyInfo() {
      if (!this.analysis || !this.analysis.learningEfficiency) {
        return learningAnalyticsUtils.getEfficiencyLevelInfo('average')
      }
      return learningAnalyticsUtils.getEfficiencyLevelInfo(this.analysis.learningEfficiency.efficiency_level)
    },
    
    timePreferenceInfo() {
      if (!this.analysis || !this.analysis.learningHabits) {
        return learningAnalyticsUtils.getTimePreferenceInfo('')
      }
      return learningAnalyticsUtils.getTimePreferenceInfo(this.analysis.learningHabits.time_preference)
    },
    
    frequencyPatternInfo() {
      if (!this.analysis || !this.analysis.learningHabits) {
        return learningAnalyticsUtils.getFrequencyPatternInfo('no_pattern')
      }
      return learningAnalyticsUtils.getFrequencyPatternInfo(this.analysis.learningHabits.frequency_pattern)
    },
    
    completionRate() {
      if (!this.analysis || !this.analysis.learningProgress) {
        return 0
      }
      return Math.round(this.analysis.learningProgress.completion_rate || 0)
    }
  },

  methods: {
    async refreshAnalytics() {
      this.isLoading = true
      
      try {
        // 调用API获取分析结果
        const result = await learningAnalyticsAPI.getLearningAnalytics()
        
        if (result.analysis) {
          this.analysis = learningAnalyticsUtils.formatLearningPatterns(result.analysis.patterns)
          this.recommendations = learningAnalyticsUtils.formatRecommendations(result.recommendations.recommendations || [])
          
          // 绘制图表
          this.$nextTick(() => {
            this.renderTimeDistributionChart()
            this.renderContentDistributionChart()
            this.renderEfficiencyChart()
          })
        }
      } catch (error) {
        console.error('获取分析失败:', error)
        // 使用示例数据
        const mockAnalysis = learningAnalyticsExamples.getExampleAnalysis()
        const mockRecommendations = learningAnalyticsExamples.getExampleRecommendations()
        this.analysis = learningAnalyticsUtils.formatLearningPatterns(mockAnalysis.patterns)
        this.recommendations = learningAnalyticsUtils.formatRecommendations(mockRecommendations.recommendations || [])
        
        // 绘制图表
        this.$nextTick(() => {
          this.renderTimeDistributionChart()
          this.renderContentDistributionChart()
          this.renderEfficiencyChart()
        })
      } finally {
        this.isLoading = false
      }
    },

    renderTimeDistributionChart() {
      // 销毁旧图表
      if (this.timeDistributionChart) {
        this.timeDistributionChart.destroy()
      }
      
      // 获取图表容器
      const chartElement = this.$refs.timeDistributionChart
      if (!chartElement) {
        console.warn('时间分布图表容器不存在')
        return
      }
      
      const ctx = chartElement.getContext('2d')
      if (!ctx) {
        console.warn('无法获取时间分布图表上下文')
        return
      }
      
      // 准备图表数据
      const chartData = learningAnalyticsUtils.generateTimeDistributionChartData(this.analysis?.timeDistribution)
      
      // 创建图表
      this.timeDistributionChart = new Chart(ctx, {
        type: 'line',
        data: chartData,
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
              title: {
                display: true,
                text: '学习次数'
              }
            },
            x: {
              title: {
                display: true,
                text: '时间'
              }
            }
          }
        }
      })
    },

    renderContentDistributionChart() {
      // 销毁旧图表
      if (this.contentDistributionChart) {
        this.contentDistributionChart.destroy()
      }
      
      // 获取图表容器
      const chartElement = this.$refs.contentDistributionChart
      if (!chartElement) {
        console.warn('内容分布图表容器不存在')
        return
      }
      
      const ctx = chartElement.getContext('2d')
      if (!ctx) {
        console.warn('无法获取内容分布图表上下文')
        return
      }
      
      // 准备图表数据
      const chartData = learningAnalyticsUtils.generateContentDistributionChartData(this.analysis?.contentDistribution)
      
      // 创建图表
      this.contentDistributionChart = new Chart(ctx, {
        type: 'bar',
        data: chartData,
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
              title: {
                display: true,
                text: '学习次数'
              }
            },
            x: {
              title: {
                display: true,
                text: '知识点'
              }
            }
          }
        }
      })
    },

    renderEfficiencyChart() {
      // 销毁旧图表
      if (this.efficiencyChart) {
        this.efficiencyChart.destroy()
      }
      
      // 获取图表容器
      const chartElement = this.$refs.efficiencyChart
      if (!chartElement) {
        console.warn('效率分析图表容器不存在')
        return
      }
      
      const ctx = chartElement.getContext('2d')
      if (!ctx) {
        console.warn('无法获取效率分析图表上下文')
        return
      }
      
      // 准备图表数据
      const chartData = learningAnalyticsUtils.generateEfficiencyRadarData(this.analysis?.learningEfficiency)
      
      // 创建图表
      this.efficiencyChart = new Chart(ctx, {
        type: 'radar',
        data: chartData,
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
            r: {
              beginAtZero: true,
              max: 100,
              title: {
                display: true,
                text: '评分'
              }
            }
          }
        }
      })
    }
  },

  mounted() {
    // 组件加载时获取分析
    this.refreshAnalytics()
  },

  updated() {
    // 组件更新后重新渲染图表
    if (this.analysis) {
      this.$nextTick(() => {
        this.renderTimeDistributionChart()
        this.renderContentDistributionChart()
        this.renderEfficiencyChart()
      })
    }
  },

  beforeUnmount() {
    // 组件卸载时销毁图表
    if (this.timeDistributionChart) {
      this.timeDistributionChart.destroy()
    }
    if (this.contentDistributionChart) {
      this.contentDistributionChart.destroy()
    }
    if (this.efficiencyChart) {
      this.efficiencyChart.destroy()
    }
  }
}
</script>

<style scoped>
.learning-analytics-component {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.analytics-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e2e8f0;
}

.card-header h3 {
  margin: 0;
  color: #2d3748;
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

.loading-state, .empty-state, .no-recommendations {
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

.core-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.metric-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: #f7fafc;
  border-radius: 8px;
  transition: transform 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.metric-icon {
  font-size: 32px;
  min-width: 40px;
}

.metric-content {
  flex: 1;
}

.metric-value {
  font-size: 20px;
  font-weight: bold;
  color: #2d3748;
  margin-bottom: 5px;
}

.metric-label {
  font-size: 14px;
  color: #718096;
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

.recommendations-section {
  margin-top: 30px;
}

.recommendations-section h4 {
  margin-bottom: 15px;
  color: #2d3748;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.recommendation-card {
  padding: 20px;
  background: #f7fafc;
  border-radius: 8px;
  transition: transform 0.2s;
}

.recommendation-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.recommendation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.recommendation-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.recommendation-icon {
  font-size: 18px;
}

.recommendation-title {
  font-weight: bold;
  color: #2d3748;
  flex: 1;
}

.recommendation-priority {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.recommendation-time {
  font-size: 12px;
  color: #718096;
}

.recommendation-description {
  color: #4a5568;
  line-height: 1.5;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .learning-analytics-component {
    padding: 10px;
  }
  
  .core-metrics {
    grid-template-columns: 1fr;
  }
  
  .card-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .recommendation-header {
    flex-direction: column;
    align-items: stretch;
    gap: 5px;
    text-align: left;
  }
  
  .recommendation-meta {
    justify-content: space-between;
  }
}
</style>

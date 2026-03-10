<template>
  <div class="learning-prediction-component">
    <!-- 预测结果卡片 -->
    <div class="prediction-card">
      <div class="card-header">
        <h3>学习效果预测</h3>
        <button @click="refreshPrediction" :disabled="isLoading" class="btn btn-primary">
          {{ isLoading ? '加载中...' : '刷新预测' }}
        </button>
      </div>
      
      <div v-if="isLoading" class="loading-state">
        <div class="loading-spinner"></div>
        <p>正在分析学习数据...</p>
      </div>
      
      <div v-else-if="!prediction" class="empty-state">
        <p>暂无预测数据</p>
        <p class="empty-hint">点击"刷新预测"按钮获取学习效果预测</p>
      </div>
      
      <div v-else class="prediction-content">
        <!-- 核心指标 -->
        <div class="core-metrics">
          <div class="metric-card">
            <div class="metric-icon">📊</div>
            <div class="metric-content">
              <div class="metric-value">{{ Math.round(prediction.currentScore * 100) }}%</div>
              <div class="metric-label">学习评分</div>
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-icon">🎯</div>
            <div class="metric-content">
              <div class="metric-value">{{ Math.round(prediction.currentMastery * 100) }}%</div>
              <div class="metric-label">知识掌握度</div>
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-icon" :style="{ color: riskInfo.color }">{{ riskInfo.icon }}</div>
            <div class="metric-content">
              <div class="metric-value" :style="{ color: riskInfo.color }">{{ riskInfo.label }}</div>
              <div class="metric-label">风险等级</div>
            </div>
          </div>
          
          <div class="metric-card">
            <div class="metric-icon">🔍</div>
            <div class="metric-content">
              <div class="metric-value">{{ Math.round(prediction.confidence * 100) }}%</div>
              <div class="metric-label">预测置信度</div>
            </div>
          </div>
        </div>
        
        <!-- 趋势图表 -->
        <div class="chart-section">
          <h4>学习趋势</h4>
          <div class="chart-container">
            <canvas ref="trendChart"></canvas>
          </div>
        </div>
        
        <!-- 干预建议 -->
        <div class="intervention-section">
          <h4>干预建议</h4>
          <div v-if="interventions.length === 0" class="no-interventions">
            <p>🎉 学习状态良好，暂无干预建议</p>
          </div>
          <div v-else class="intervention-list">
            <div 
              v-for="(intervention, index) in interventions" 
              :key="index"
              class="intervention-card"
            >
              <div class="intervention-header">
                <div class="intervention-meta">
                  <span class="intervention-icon">{{ intervention.priorityInfo.icon }}</span>
                  <span class="intervention-title">{{ intervention.title }}</span>
                  <span 
                    class="intervention-priority"
                    :style="{ backgroundColor: intervention.priorityInfo.color }"
                  >
                    {{ intervention.priorityInfo.label }}
                  </span>
                </div>
                <span class="intervention-time">{{ intervention.estimatedTimeFormatted }}</span>
              </div>
              <div class="intervention-description">{{ intervention.description }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { learningPredictionAPI, learningPredictionUtils, learningPredictionExamples } from '../api/learning_prediction_api'
import Chart from 'chart.js/auto'

export default {
  name: 'LearningPredictionComponent',
  
  data() {
    return {
      isLoading: false,
      prediction: null,
      interventions: [],
      trendChart: null
    }
  },

  computed: {
    riskInfo() {
      if (!this.prediction) {
        return learningPredictionUtils.getRiskLevelInfo('medium')
      }
      return learningPredictionUtils.getRiskLevelInfo(this.prediction.riskLevel)
    }
  },

  methods: {
    async refreshPrediction() {
      this.isLoading = true
      
      try {
        // 调用API获取预测结果
        const result = await learningPredictionAPI.getLearningPrediction()
        
        if (result.result) {
          this.prediction = learningPredictionUtils.formatPrediction(result.result.prediction)
          this.interventions = learningPredictionUtils.formatInterventions(result.result.interventions || [])
          
          // 绘制趋势图表
          this.renderTrendChart()
        }
      } catch (error) {
        console.error('获取预测失败:', error)
        // 使用示例数据
        this.prediction = learningPredictionUtils.formatPrediction(learningPredictionExamples.getExamplePrediction())
        this.interventions = learningPredictionUtils.formatInterventions(learningPredictionExamples.getExampleInterventions())
        this.renderTrendChart()
      } finally {
        this.isLoading = false
      }
    },

    renderTrendChart() {
      if (!this.prediction) return
      
      // 合并历史和未来预测数据
      const allPredictions = [
        ...this.prediction.historicalPredictions,
        ...this.prediction.futurePredictions
      ]
      
      // 销毁旧图表
      if (this.trendChart) {
        this.trendChart.destroy()
      }
      
      // 获取图表容器
      const chartElement = this.$refs.trendChart
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
      let chartData
      if (allPredictions.length > 0) {
        chartData = learningPredictionUtils.generateChartData(allPredictions)
      } else {
        // 生成模拟数据
        chartData = this.generateMockChartData()
      }
      
      // 创建新图表
      this.trendChart = new Chart(ctx, {
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
      const predictedData = []
      const actualData = []
      
      const today = new Date()
      for (let i = 10; i >= 0; i--) {
        const date = new Date(today)
        date.setDate(today.getDate() - i)
        labels.push(date.toLocaleDateString())
        const score = 50 + Math.sin(i / 3) * 20 + Math.random() * 10
        predictedData.push(score)
        actualData.push(50 + Math.sin(i / 3) * 15 + Math.random() * 10)
      }
      for (let i = 1; i <= 5; i++) {
        const date = new Date(today)
        date.setDate(today.getDate() + i)
        labels.push(date.toLocaleDateString())
        const score = 50 + Math.sin((10 + i) / 3) * 20 + Math.random() * 10
        predictedData.push(score)
        actualData.push(null)
      }
      
      return {
        labels: labels,
        datasets: [
          {
            label: '预测分数',
            data: predictedData,
            borderColor: '#4CAF50',
            backgroundColor: 'rgba(76, 175, 80, 0.1)',
            borderWidth: 2,
            tension: 0.3,
            fill: true
          },
          {
            label: '实际分数',
            data: actualData,
            borderColor: '#2196F3',
            backgroundColor: 'rgba(33, 150, 243, 0.1)',
            borderWidth: 2,
            tension: 0.3,
            fill: true
          }
        ]
      }
    }
  },

  mounted() {
    // 组件加载时获取预测
    this.refreshPrediction()
  },

  updated() {
    // 组件更新后重新渲染图表
    if (this.prediction) {
      this.$nextTick(() => {
        this.renderTrendChart()
      })
    }
  },

  beforeUnmount() {
    // 组件卸载时销毁图表
    if (this.trendChart) {
      this.trendChart.destroy()
    }
  }
}
</script>

<style scoped>
.learning-prediction-component {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.prediction-card {
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
  font-size: 24px;
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

.intervention-section {
  margin-top: 30px;
}

.intervention-section h4 {
  margin-bottom: 15px;
  color: #2d3748;
}

.no-interventions {
  text-align: center;
  padding: 40px;
  background: #f7fafc;
  border-radius: 8px;
  color: #718096;
}

.intervention-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.intervention-card {
  padding: 20px;
  background: #f7fafc;
  border-radius: 8px;
  transition: transform 0.2s;
}

.intervention-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.intervention-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.intervention-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.intervention-icon {
  font-size: 18px;
}

.intervention-title {
  font-weight: bold;
  color: #2d3748;
  flex: 1;
}

.intervention-priority {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.intervention-time {
  font-size: 12px;
  color: #718096;
}

.intervention-description {
  color: #4a5568;
  line-height: 1.5;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .learning-prediction-component {
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
  
  .intervention-header {
    flex-direction: column;
    align-items: stretch;
    gap: 5px;
    text-align: left;
  }
  
  .intervention-meta {
    justify-content: space-between;
  }
}
</style>
<template>
  <div class="learning-analytics-view">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1>学习智能分析</h1>
      <p>深入分析学习行为，提供个性化学习建议</p>
    </div>

    <!-- 功能导航 -->
    <div class="feature-nav">
      <div class="nav-item" :class="{ active: activeFeature === 'overview' }" @click="activeFeature = 'overview'">
        <span class="nav-icon">📊</span>
        <span class="nav-label">分析概览</span>
      </div>
      <div class="nav-item" :class="{ active: activeFeature === 'patterns' }" @click="activeFeature = 'patterns'">
        <span class="nav-icon">🔍</span>
        <span class="nav-label">学习模式</span>
      </div>
      <div class="nav-item" :class="{ active: activeFeature === 'recommendations' }" @click="activeFeature = 'recommendations'">
        <span class="nav-icon">💡</span>
        <span class="nav-label">学习建议</span>
      </div>
      <div class="nav-item" :class="{ active: activeFeature === 'efficiency' }" @click="activeFeature = 'efficiency'">
        <span class="nav-icon">⚡</span>
        <span class="nav-label">效率分析</span>
      </div>
    </div>

    <!-- 功能内容区域 -->
    <div class="feature-content">
      <!-- 分析概览功能 -->
      <div v-if="activeFeature === 'overview'" class="feature-panel">
        <LearningAnalyticsComponent ref="learningAnalyticsComponent" />
      </div>

      <!-- 学习模式分析功能 -->
      <div v-if="activeFeature === 'patterns'" class="feature-panel">
        <div class="patterns-section">
          <div class="section-header">
            <h3>学习模式分析</h3>
            <button @click="loadPatterns" :disabled="isLoadingPatterns" class="btn btn-primary">
              {{ isLoadingPatterns ? '加载中...' : '加载模式' }}
            </button>
          </div>

          <div v-if="isLoadingPatterns" class="loading-state">
            <div class="loading-spinner"></div>
            <p>加载学习模式数据中...</p>
          </div>

          <div v-else-if="!patternsData" class="empty-state">
            <p>暂无学习模式数据</p>
            <p class="empty-hint">点击"加载模式"按钮获取学习模式分析</p>
          </div>

          <div v-else class="patterns-content">
            <!-- 时间模式 -->
            <div class="pattern-card">
              <h4>📅 时间模式</h4>
              <div class="pattern-details">
                <div class="pattern-item">
                  <span class="pattern-label">学习高峰期:</span>
                  <span class="pattern-value">{{ patternsData.timeDistribution.peak_hour }}:00</span>
                </div>
                <div class="pattern-item">
                  <span class="pattern-label">最活跃日:</span>
                  <span class="pattern-value">{{ patternsData.timeDistribution.peak_day }}</span>
                </div>
                <div class="pattern-item">
                  <span class="pattern-label">总学习次数:</span>
                  <span class="pattern-value">{{ patternsData.timeDistribution.total_learning_sessions }}</span>
                </div>
                <div class="pattern-item">
                  <span class="pattern-label">时间偏好:</span>
                  <span class="pattern-value">{{ timePreferenceInfo.icon }} {{ timePreferenceInfo.label }}</span>
                </div>
              </div>
            </div>

            <!-- 内容模式 -->
            <div class="pattern-card">
              <h4>📚 内容模式</h4>
              <div class="pattern-details">
                <div class="pattern-item">
                  <span class="pattern-label">最常学习:</span>
                  <span class="pattern-value">{{ patternsData.contentDistribution.most_studied_knowledge }}</span>
                </div>
                <div class="pattern-item">
                  <span class="pattern-label">学习知识点数:</span>
                  <span class="pattern-value">{{ patternsData.contentDistribution.unique_knowledge_nodes }}</span>
                </div>
              </div>
              <div class="knowledge-distribution">
                <h5>知识点分布</h5>
                <div class="distribution-list">
                  <div 
                    v-for="(count, knowledge) in patternsData.contentDistribution.knowledge_distribution" 
                    :key="knowledge"
                    class="distribution-item"
                  >
                    <div class="distribution-label">{{ knowledge }}</div>
                    <div class="distribution-bar">
                      <div 
                        class="distribution-fill"
                        :style="{ width: (count / maxKnowledgeCount * 100) + '%' }"
                      ></div>
                    </div>
                    <div class="distribution-value">{{ count }}次</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 习惯模式 -->
            <div class="pattern-card">
              <h4>🎯 习惯模式</h4>
              <div class="pattern-details">
                <div class="pattern-item">
                  <span class="pattern-label">时长偏好:</span>
                  <span class="pattern-value">{{ durationPreferenceInfo.icon }} {{ durationPreferenceInfo.label }}</span>
                </div>
                <div class="pattern-item">
                  <span class="pattern-label">频率模式:</span>
                  <span class="pattern-value">{{ frequencyPatternInfo.icon }} {{ frequencyPatternInfo.label }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 学习建议功能 -->
      <div v-if="activeFeature === 'recommendations'" class="feature-panel">
        <div class="recommendations-section">
          <div class="section-header">
            <h3>个性化学习建议</h3>
            <button @click="loadRecommendations" :disabled="isLoadingRecommendations" class="btn btn-primary">
              {{ isLoadingRecommendations ? '加载中...' : '刷新建议' }}
            </button>
          </div>

          <div v-if="isLoadingRecommendations" class="loading-state">
            <div class="loading-spinner"></div>
            <p>生成学习建议中...</p>
          </div>

          <div v-else-if="recommendations.length === 0" class="empty-state">
            <p>暂无学习建议</p>
            <p class="empty-hint">点击"刷新建议"按钮获取个性化学习建议</p>
          </div>

          <div v-else class="recommendations-content">
            <div class="recommendations-list">
              <div 
                v-for="(recommendation, index) in recommendations" 
                :key="index"
                class="recommendation-card"
                :class="recommendation.priority"
              >
                <div class="recommendation-header">
                  <div class="recommendation-icon">{{ recommendation.priorityInfo.icon }}</div>
                  <div class="recommendation-title">{{ recommendation.title }}</div>
                  <span 
                    class="recommendation-priority"
                    :style="{ backgroundColor: recommendation.priorityInfo.color }"
                  >
                    {{ recommendation.priorityInfo.label }}
                  </span>
                </div>
                <div class="recommendation-description">{{ recommendation.description }}</div>
                <div class="recommendation-footer">
                  <span class="recommendation-time">{{ recommendation.estimatedTimeFormatted }}</span>
                  <button class="btn btn-secondary">标记已完成</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 效率分析功能 -->
      <div v-if="activeFeature === 'efficiency'" class="feature-panel">
        <div class="efficiency-section">
          <div class="section-header">
            <h3>学习效率分析</h3>
            <button @click="loadEfficiency" :disabled="isLoadingEfficiency" class="btn btn-primary">
              {{ isLoadingEfficiency ? '加载中...' : '分析效率' }}
            </button>
          </div>

          <div v-if="isLoadingEfficiency" class="loading-state">
            <div class="loading-spinner"></div>
            <p>分析学习效率中...</p>
          </div>

          <div v-else-if="!efficiencyData" class="empty-state">
            <p>暂无效率分析数据</p>
            <p class="empty-hint">点击"分析效率"按钮获取学习效率分析</p>
          </div>

          <div v-else class="efficiency-content">
            <!-- 效率概览 -->
            <div class="efficiency-overview">
              <div class="efficiency-card">
                <div class="efficiency-icon">⚡</div>
                <div class="efficiency-content">
                  <div class="efficiency-value">{{ efficiencyLevelInfo.label }}</div>
                  <div class="efficiency-label">整体效率</div>
                </div>
              </div>
              <div class="efficiency-card">
                <div class="efficiency-icon">📈</div>
                <div class="efficiency-content">
                  <div class="efficiency-value">{{ Math.round(efficiencyData.learning_efficiency.continuity_score) }}%</div>
                  <div class="efficiency-label">学习连续性</div>
                </div>
              </div>
              <div class="efficiency-card">
                <div class="efficiency-icon">⏰</div>
                <div class="efficiency-content">
                  <div class="efficiency-value">{{ efficiencyData.learning_efficiency.average_session_duration }}分钟</div>
                  <div class="efficiency-label">平均时长</div>
                </div>
              </div>
              <div class="efficiency-card">
                <div class="efficiency-icon">📅</div>
                <div class="efficiency-content">
                  <div class="efficiency-value">{{ efficiencyData.learning_efficiency.daily_frequency.toFixed(1) }}次/天</div>
                  <div class="efficiency-label">每日频率</div>
                </div>
              </div>
            </div>

            <!-- 效率详细分析 -->
            <div class="efficiency-details">
              <h4>详细效率分析</h4>
              <div class="detail-item">
                <span class="detail-label">总学习时间:</span>
                <span class="detail-value">{{ Math.round(efficiencyData.learning_efficiency.total_learning_time / 60) }}小时</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">时间偏好:</span>
                <span class="detail-value">{{ timePreferenceInfo.icon }} {{ timePreferenceInfo.label }}</span>
              </div>
              <div class="detail-item">
                <span class="detail-label">学习高峰期:</span>
                <span class="detail-value">{{ efficiencyData.time_distribution.peak_hour }}:00</span>
              </div>
            </div>

            <!-- 效率改进建议 -->
            <div class="efficiency-suggestions">
              <h4>效率改进建议</h4>
              <ul class="suggestions-list">
                <li v-if="efficiencyData.learning_efficiency.continuity_score < 60">
                  建议建立固定的学习时间表，提高学习连续性
                </li>
                <li v-if="efficiencyData.learning_efficiency.average_session_duration < 15">
                  建议每次学习时间不少于15分钟，以提高学习效果
                </li>
                <li v-if="efficiencyData.learning_efficiency.daily_frequency < 1">
                  建议每天至少进行1次学习，保持学习状态
                </li>
                <li v-if="efficiencyData.learning_efficiency.continuity_score >= 80 && efficiencyData.learning_efficiency.daily_frequency >= 2">
                  学习习惯良好，继续保持！
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import LearningAnalyticsComponent from '../components/LearningAnalyticsComponent.vue'
import { learningAnalyticsAPI, learningAnalyticsUtils } from '../api/learning_analytics_api'

export default {
  name: 'LearningAnalyticsView',
  
  components: {
    LearningAnalyticsComponent
  },

  data() {
    return {
      activeFeature: 'overview',
      patternsData: null,
      recommendations: [],
      efficiencyData: null,
      isLoadingPatterns: false,
      isLoadingRecommendations: false,
      isLoadingEfficiency: false
    }
  },

  computed: {
    timePreferenceInfo() {
      if (this.patternsData?.learningHabits) {
        return learningAnalyticsUtils.getTimePreferenceInfo(this.patternsData.learningHabits.time_preference)
      } else if (this.efficiencyData?.learning_habits) {
        return learningAnalyticsUtils.getTimePreferenceInfo(this.efficiencyData.learning_habits.time_preference)
      }
      return learningAnalyticsUtils.getTimePreferenceInfo('')
    },
    
    durationPreferenceInfo() {
      if (this.patternsData?.learningHabits) {
        return learningAnalyticsUtils.getDurationPreferenceInfo(this.patternsData.learningHabits.duration_preference)
      }
      return learningAnalyticsUtils.getDurationPreferenceInfo('')
    },
    
    frequencyPatternInfo() {
      if (this.patternsData?.learningHabits) {
        return learningAnalyticsUtils.getFrequencyPatternInfo(this.patternsData.learningHabits.frequency_pattern)
      }
      return learningAnalyticsUtils.getFrequencyPatternInfo('no_pattern')
    },
    
    efficiencyLevelInfo() {
      if (this.efficiencyData?.learning_efficiency) {
        return learningAnalyticsUtils.getEfficiencyLevelInfo(this.efficiencyData.learning_efficiency.efficiency_level)
      }
      return learningAnalyticsUtils.getEfficiencyLevelInfo('average')
    },
    
    maxKnowledgeCount() {
      if (!this.patternsData?.contentDistribution?.knowledge_distribution) {
        return 1
      }
      return Math.max(...Object.values(this.patternsData.contentDistribution.knowledge_distribution))
    }
  },

  methods: {
    async loadPatterns() {
      this.isLoadingPatterns = true
      
      try {
        const result = await learningAnalyticsAPI.getLearningPatterns()
        if (result.result?.patterns) {
          this.patternsData = learningAnalyticsUtils.formatLearningPatterns(result.result.patterns)
        }
      } catch (error) {
        console.error('加载学习模式失败:', error)
        // 使用示例数据
        const mockAnalysis = learningAnalyticsAPI.generateMockAnalysis()
        this.patternsData = learningAnalyticsUtils.formatLearningPatterns(mockAnalysis.patterns)
      } finally {
        this.isLoadingPatterns = false
      }
    },

    async loadRecommendations() {
      this.isLoadingRecommendations = true
      
      try {
        const result = await learningAnalyticsAPI.getLearningRecommendations()
        if (result.result?.recommendations) {
          this.recommendations = learningAnalyticsUtils.formatRecommendations(result.result.recommendations)
        }
      } catch (error) {
        console.error('加载学习建议失败:', error)
        // 使用示例数据
        const mockRecommendations = learningAnalyticsAPI.generateMockRecommendations()
        this.recommendations = learningAnalyticsUtils.formatRecommendations(mockRecommendations.recommendations || [])
      } finally {
        this.isLoadingRecommendations = false
      }
    },

    async loadEfficiency() {
      this.isLoadingEfficiency = true
      
      try {
        const result = await learningAnalyticsAPI.getLearningEfficiency()
        if (result.result) {
          this.efficiencyData = result.result
        }
      } catch (error) {
        console.error('加载效率分析失败:', error)
        // 使用示例数据
        this.efficiencyData = learningAnalyticsAPI.generateMockEfficiencyData()
      } finally {
        this.isLoadingEfficiency = false
      }
    }
  },

  watch: {
    activeFeature(newFeature) {
      if (newFeature === 'patterns' && !this.patternsData) {
        this.loadPatterns()
      } else if (newFeature === 'recommendations' && this.recommendations.length === 0) {
        this.loadRecommendations()
      } else if (newFeature === 'efficiency' && !this.efficiencyData) {
        this.loadEfficiency()
      }
    }
  },

  mounted() {
    // 页面加载时初始化数据
    this.loadPatterns()
    this.loadRecommendations()
    this.loadEfficiency()
  }
}
</script>

<style scoped>
.learning-analytics-view {
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

/* 学习模式样式 */
.patterns-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.pattern-card {
  background: #f7fafc;
  border-radius: 8px;
  padding: 20px;
}

.pattern-card h4 {
  margin-top: 0;
  color: #2d3748;
  margin-bottom: 15px;
}

.pattern-details {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.pattern-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.pattern-label {
  color: #718096;
  font-size: 14px;
}

.pattern-value {
  font-weight: bold;
  color: #2d3748;
}

.knowledge-distribution {
  margin-top: 20px;
}

.knowledge-distribution h5 {
  margin-bottom: 15px;
  color: #4a5568;
}

.distribution-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.distribution-item {
  display: flex;
  align-items: center;
  gap: 15px;
}

.distribution-label {
  min-width: 120px;
  font-size: 14px;
  color: #4a5568;
}

.distribution-bar {
  flex: 1;
  height: 20px;
  background: #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
}

.distribution-fill {
  height: 100%;
  background: #4299e1;
  border-radius: 10px;
  transition: width 0.3s ease;
}

.distribution-value {
  min-width: 60px;
  font-size: 14px;
  color: #718096;
  text-align: right;
}

/* 学习建议样式 */
.recommendations-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.recommendation-card {
  background: #f7fafc;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.2s;
  border-left: 4px solid #e2e8f0;
}

.recommendation-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.recommendation-card.high {
  border-left-color: #e53e3e;
}

.recommendation-card.medium {
  border-left-color: #dd6b20;
}

.recommendation-card.low {
  border-left-color: #38a169;
}

.recommendation-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 10px;
}

.recommendation-icon {
  font-size: 24px;
  min-width: 30px;
}

.recommendation-title {
  flex: 1;
  font-weight: bold;
  color: #2d3748;
  font-size: 16px;
}

.recommendation-priority {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.recommendation-description {
  color: #4a5568;
  line-height: 1.5;
  margin-bottom: 15px;
}

.recommendation-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.recommendation-time {
  font-size: 12px;
  color: #718096;
}

/* 效率分析样式 */
.efficiency-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.efficiency-card {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 20px;
  background: #f7fafc;
  border-radius: 8px;
  transition: transform 0.2s;
}

.efficiency-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.efficiency-icon {
  font-size: 32px;
  min-width: 40px;
}

.efficiency-content {
  flex: 1;
}

.efficiency-value {
  font-size: 20px;
  font-weight: bold;
  color: #2d3748;
  margin-bottom: 5px;
}

.efficiency-label {
  font-size: 14px;
  color: #718096;
}

.efficiency-details {
  background: #f7fafc;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.efficiency-details h4 {
  margin-top: 0;
  color: #2d3748;
  margin-bottom: 15px;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
  padding-bottom: 10px;
  border-bottom: 1px solid #e2e8f0;
}

.detail-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.detail-label {
  color: #718096;
  font-size: 14px;
}

.detail-value {
  font-weight: bold;
  color: #2d3748;
}

.efficiency-suggestions {
  background: #f7fafc;
  border-radius: 8px;
  padding: 20px;
}

.efficiency-suggestions h4 {
  margin-top: 0;
  color: #2d3748;
  margin-bottom: 15px;
}

.suggestions-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.suggestions-list li {
  padding: 10px 0;
  border-bottom: 1px solid #e2e8f0;
  color: #4a5568;
  line-height: 1.5;
}

.suggestions-list li:last-child {
  border-bottom: none;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .learning-analytics-view {
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
  
  .section-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .pattern-details {
    grid-template-columns: 1fr;
  }
  
  .efficiency-overview {
    grid-template-columns: 1fr;
  }
  
  .recommendation-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
    text-align: left;
  }
  
  .recommendation-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
}
</style>

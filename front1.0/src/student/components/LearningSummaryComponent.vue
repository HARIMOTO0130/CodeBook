<template>
  <div class="learning-summary-container">
    <h2 class="section-title">学习摘要</h2>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>生成摘要中...</p>
    </div>
    
    <!-- 错误提示 -->
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="resetError" class="retry-button">重试</button>
    </div>
    
    <!-- 内容区域 -->
    <div v-else class="content-wrapper">
      <!-- 时间范围选择 -->
      <div class="time-range-selector">
        <h3>选择时间范围</h3>
        <div class="time-buttons">
          <button 
            v-for="range in timeRanges" 
            :key="range.value"
            @click="selectTimeRange(range.value)"
            :class="['time-button', { active: selectedTimeRange === range.value }]"
          >
            {{ range.label }}
          </button>
        </div>
      </div>
      
      <!-- 主题摘要输入 -->
      <div class="topic-summary-section">
        <h3>主题学习摘要</h3>
        <div class="topic-input-group">
          <input 
            type="text" 
            v-model="topic" 
            placeholder="输入学习主题，例如：Python"
            class="topic-input"
          />
          <button @click="generateTopicSummary" class="btn-secondary" :disabled="!topic">
            <span class="btn-icon">📚</span>
            生成主题摘要
          </button>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="action-buttons">
        <button @click="generateSummary" class="btn-primary">
          <span class="btn-icon">📊</span>
          生成学习摘要
        </button>
        <button @click="exportSummary" class="btn-secondary" :disabled="!summaryResult">
          <span class="btn-icon">📤</span>
          导出摘要
        </button>
      </div>
      
      <!-- 学习摘要结果 -->
      <div v-if="summaryResult" class="summary-result">
        <div class="result-header">
          <h3>{{ summaryTitle }}</h3>
          <div class="result-meta">
            <span class="meta-item">生成时间：{{ formatDate(summaryResult.timestamp) }}</span>
            <span v-if="summaryResult.time_range" class="meta-item">时间范围：{{ formatTimeRange(summaryResult.time_range) }}</span>
          </div>
        </div>
        
        <!-- 摘要内容 -->
        <div class="summary-content">
          <pre class="summary-text">{{ summaryResult.summary }}</pre>
        </div>
        
        <!-- 学习统计 -->
        <div class="learning-stats">
          <h4>学习统计</h4>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">总学习内容</span>
              <span class="stat-value">{{ summaryResult.statistics.total_records }}</span>
              <span class="stat-unit">个</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">总学习时长</span>
              <span class="stat-value">{{ formatDuration(summaryResult.statistics.total_duration) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">平均得分</span>
              <span class="stat-value">{{ summaryResult.statistics.average_score.toFixed(1) }}</span>
              <span class="stat-unit">分</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">完成率</span>
              <span class="stat-value">{{ summaryResult.statistics.completion_rate.toFixed(0) }}</span>
              <span class="stat-unit">%</span>
            </div>
          </div>
        </div>
        
        <!-- 关键知识点 -->
        <div class="key-points">
          <h4>关键知识点</h4>
          <div class="points-tagcloud">
            <span v-for="(point, index) in summaryResult.key_points" :key="index" class="point-tag">
              {{ point }}
            </span>
          </div>
        </div>
        
        <!-- 学习建议 -->
        <div class="recommendations">
          <h4>学习建议</h4>
          <ul class="recommendations-list">
            <li v-for="(recommendation, index) in summaryResult.recommendations" :key="index" class="recommendation-item">
              <span :class="`priority-badge priority-${recommendation.priority}`">
                {{ recommendation.priority }}
              </span>
              <div class="recommendation-content">
                <strong>{{ recommendation.title }}</strong>
                <p>{{ recommendation.description }}</p>
              </div>
            </li>
          </ul>
        </div>
        
        <!-- 内容类型分布 -->
        <div class="content-type-distribution">
          <h4>内容类型分布</h4>
          <div class="distribution-chart">
            <div v-for="(stats, content_type) in summaryResult.statistics.content_type_stats" :key="content_type" class="distribution-item">
              <div class="distribution-label">{{ content_type }}</div>
              <div class="distribution-bar">
                <div 
                  class="distribution-fill" 
                  :style="{ width: (stats.count / summaryResult.statistics.total_records) * 100 + '%' }"
                ></div>
              </div>
              <div class="distribution-value">{{ stats.count }}个</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 学习摘要历史 -->
      <div class="summary-history">
        <h3>摘要历史</h3>
        <div class="history-list">
          <div v-for="item in summaryHistory" :key="item.id" class="history-item">
            <div class="history-content">
              <div class="history-header">
                <span class="history-time-range">{{ formatTimeRange(item.time_range) }}摘要</span>
                <span class="history-date">{{ formatDate(item.generated_at) }}</span>
              </div>
              <p class="history-preview">{{ item.summary_preview }}</p>
            </div>
            <button @click="loadHistorySummary(item.id)" class="history-button">
              查看
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { 
  generateSummary, 
  generateTopicSummary as apiGenerateTopicSummary, 
  getSummaryHistory, 
  formatTimeRange, 
  formatDuration 
} from '../api/learning_summary_api';

export default {
  name: 'LearningSummaryComponent',
  data() {
    return {
      loading: false,
      error: null,
      selectedTimeRange: 'week',
      topic: '',
      summaryResult: null,
      summaryHistory: [],
      timeRanges: [
        { value: 'day', label: '一天' },
        { value: 'week', label: '一周' },
        { value: 'month', label: '一个月' },
        { value: 'year', label: '一年' }
      ]
    };
  },
  computed: {
    summaryTitle() {
      if (!this.summaryResult) return '';
      if (this.summaryResult.topic) {
        return `${this.summaryResult.topic}学习摘要`;
      }
      return `${formatTimeRange(this.summaryResult.time_range)}学习摘要`;
    }
  },
  mounted() {
    this.loadSummaryHistory();
  },
  methods: {
    async generateSummary() {
      this.loading = true;
      this.error = null;
      
      try {
        const result = await generateSummary(this.selectedTimeRange);
        this.summaryResult = result;
      } catch (error) {
        this.error = '生成学习摘要失败，请稍后重试';
        console.error('生成学习摘要失败:', error);
      } finally {
        this.loading = false;
      }
    },
    async generateTopicSummary() {
      if (!this.topic) {
        this.error = '请输入学习主题';
        return;
      }
      
      this.loading = true;
      this.error = null;
      
      try {
        const result = await apiGenerateTopicSummary(this.topic);
        this.summaryResult = result;
      } catch (error) {
        this.error = '生成主题学习摘要失败，请稍后重试';
        console.error('生成主题学习摘要失败:', error);
      } finally {
        this.loading = false;
      }
    },
    async loadSummaryHistory() {
      try {
        const history = await getSummaryHistory();
        this.summaryHistory = history.history || [];
      } catch (error) {
        console.error('获取学习摘要历史失败:', error);
      }
    },
    selectTimeRange(range) {
      this.selectedTimeRange = range;
    },
    exportSummary() {
      if (!this.summaryResult) return;
      
      const content = `# ${this.summaryTitle}\n\n${this.summaryResult.summary}\n\n## 关键知识点\n${this.summaryResult.key_points.map(point => `- ${point}`).join('\n')}\n\n## 学习建议\n${this.summaryResult.recommendations.map(rec => `- ${rec.title}: ${rec.description}`).join('\n')}\n\n## 学习统计\n- 总学习内容: ${this.summaryResult.statistics.total_records}个\n- 总学习时长: ${formatDuration(this.summaryResult.statistics.total_duration)}\n- 平均得分: ${this.summaryResult.statistics.average_score.toFixed(1)}分\n- 完成率: ${this.summaryResult.statistics.completion_rate.toFixed(0)}%`;
      
      const blob = new Blob([content], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${this.summaryTitle.replace(/\s+/g, '_')}.txt`;
      a.click();
      URL.revokeObjectURL(url);
    },
    loadHistorySummary(id) {
      // 模拟加载历史摘要
      this.generateSummary();
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString('zh-CN');
    },
    resetError() {
      this.error = null;
    }
  }
};
</script>

<style scoped>
.learning-summary-container {
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 8px;
  min-height: 600px;
}

.section-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #303133;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409EFF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  background-color: #fef0f0;
  border: 1px solid #fbc4c4;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 20px;
  color: #f56c6c;
  text-align: center;
}

.retry-button {
  margin-top: 10px;
  padding: 6px 12px;
  background-color: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.retry-button:hover {
  background-color: #66b1ff;
}

.content-wrapper {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.time-range-selector {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.time-range-selector h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.time-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.time-button {
  padding: 8px 16px;
  background-color: #f5f7fa;
  color: #606266;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.time-button:hover {
  background-color: #ecf5ff;
  border-color: #c6e2ff;
  color: #409EFF;
}

.time-button.active {
  background-color: #409EFF;
  color: white;
  border-color: #409EFF;
}

.topic-summary-section {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.topic-summary-section h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.topic-input-group {
  display: flex;
  gap: 10px;
  align-items: center;
}

.topic-input {
  flex: 1;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.topic-input:focus {
  outline: none;
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.action-buttons {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin: 20px 0;
}

.btn-primary {
  padding: 10px 20px;
  background-color: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-primary:hover {
  background-color: #66b1ff;
}

.btn-secondary {
  padding: 10px 20px;
  background-color: #ffffff;
  color: #606266;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn-secondary:hover {
  background-color: #f5f7fa;
  border-color: #c6e2ff;
  color: #409EFF;
}

.btn-secondary:disabled {
  background-color: #f5f7fa;
  color: #c0c4cc;
  border-color: #ebeef5;
  cursor: not-allowed;
}

.summary-result {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #ebeef5;
}

.result-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.result-meta {
  display: flex;
  flex-direction: column;
  gap: 5px;
  font-size: 12px;
  color: #909399;
}

.summary-content {
  margin-bottom: 20px;
}

.summary-text {
  white-space: pre-wrap;
  font-size: 14px;
  line-height: 1.6;
  color: #303133;
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
  margin: 0;
}

.learning-stats {
  margin-bottom: 20px;
}

.learning-stats h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
}

.stat-item {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #606266;
  margin-bottom: 5px;
}

.stat-value {
  display: inline-block;
  font-size: 20px;
  font-weight: bold;
  color: #409EFF;
  margin-right: 5px;
}

.stat-unit {
  font-size: 14px;
  color: #606266;
}

.key-points {
  margin-bottom: 20px;
}

.key-points h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.points-tagcloud {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.point-tag {
  background-color: #ecf5ff;
  color: #409EFF;
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 14px;
  border: 1px solid #d9ecff;
}

.recommendations {
  margin-bottom: 20px;
}

.recommendations h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.recommendations-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recommendation-item {
  display: flex;
  gap: 10px;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.priority-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
  flex-shrink: 0;
  align-self: flex-start;
}

.priority-high {
  background-color: #fef0f0;
  color: #f56c6c;
}

.priority-medium {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.priority-low {
  background-color: #f0f9eb;
  color: #67c23a;
}

.recommendation-content {
  flex: 1;
}

.recommendation-content strong {
  display: block;
  margin-bottom: 5px;
  color: #303133;
}

.recommendation-content p {
  margin: 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.4;
}

.content-type-distribution {
  margin-bottom: 20px;
}

.content-type-distribution h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.distribution-chart {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.distribution-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.distribution-label {
  width: 80px;
  font-size: 14px;
  color: #606266;
  flex-shrink: 0;
}

.distribution-bar {
  flex: 1;
  height: 20px;
  background-color: #ebeef5;
  border-radius: 10px;
  overflow: hidden;
}

.distribution-fill {
  height: 100%;
  background-color: #409EFF;
  border-radius: 10px;
  transition: width 0.3s ease;
}

.distribution-value {
  width: 60px;
  font-size: 14px;
  color: #303133;
  text-align: right;
  flex-shrink: 0;
}

.summary-history {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.summary-history h3 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
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
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
  transition: background-color 0.3s;
}

.history-item:hover {
  background-color: #f0f0f0;
}

.history-content {
  flex: 1;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 5px;
}

.history-time-range {
  font-weight: 500;
  color: #303133;
  font-size: 14px;
}

.history-date {
  font-size: 12px;
  color: #909399;
}

.history-preview {
  margin: 0;
  font-size: 13px;
  color: #606266;
  line-height: 1.4;
}

.history-button {
  padding: 6px 12px;
  background-color: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.history-button:hover {
  background-color: #66b1ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .time-buttons {
    flex-direction: column;
  }
  
  .topic-input-group {
    flex-direction: column;
    align-items: stretch;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .result-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .distribution-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .distribution-label {
    width: 100%;
  }
  
  .distribution-value {
    width: 100%;
    text-align: left;
  }
}
</style>
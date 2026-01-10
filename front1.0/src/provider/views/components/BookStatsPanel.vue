<template>
  <div class="book-stats-panel">
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-stats">
      <div class="loading-spinner-small"></div>
      <span>加载统计数据中...</span>
    </div>
    
    <!-- 无数据状态 -->
    <div v-else-if="!statsData || Object.keys(statsData).length === 0" class="no-stats">
      <span>暂无统计数据</span>
    </div>
    
    <!-- 统计数据展示 -->
    <div v-else class="stats-content">
      <!-- 用户统计 -->
      <div class="stat-card">
        <div class="stat-header">
          <span class="stat-icon">👥</span>
          <span class="stat-title">学习人数</span>
        </div>
        <div class="stat-value">{{ statsData.user_count || 0 }}</div>
        <div class="stat-detail">
          <span v-if="statsData.daily_new_users">今日新增: {{ statsData.daily_new_users }}</span>
          <span v-if="statsData.weekly_new_users"> | 本周新增: {{ statsData.weekly_new_users }}</span>
        </div>
      </div>
      
      <!-- 学习时长统计 -->
      <div class="stat-card">
        <div class="stat-header">
          <span class="stat-icon">⏱️</span>
          <span class="stat-title">学习时长</span>
        </div>
        <div class="stat-value">{{ formatDuration(statsData.total_duration || 0) }}</div>
        <div class="stat-detail">
          <span v-if="statsData.average_duration">平均: {{ formatDuration(statsData.average_duration) }}</span>
        </div>
      </div>
      
      <!-- 评分统计 -->
      <div class="stat-card">
        <div class="stat-header">
          <span class="stat-icon">⭐</span>
          <span class="stat-title">评分</span>
        </div>
        <div class="stat-value">{{ statsData.average_rating || 0 }}/5</div>
        <div class="stat-detail">
          <span v-if="statsData.rating_count">评价数: {{ statsData.rating_count }}</span>
        </div>
      </div>
      
      <!-- 下载统计 -->
      <div class="stat-card">
        <div class="stat-header">
          <span class="stat-icon">📥</span>
          <span class="stat-title">下载次数</span>
        </div>
        <div class="stat-value">{{ statsData.download_count || 0 }}</div>
        <div class="stat-detail">
          <span v-if="statsData.monthly_downloads">本月: {{ statsData.monthly_downloads }}</span>
        </div>
      </div>
      
      <!-- 分享统计 -->
      <div class="stat-card">
        <div class="stat-header">
          <span class="stat-icon">🔗</span>
          <span class="stat-title">分享次数</span>
        </div>
        <div class="stat-value">{{ statsData.share_count || 0 }}</div>
        <div class="stat-detail">
          <span v-if="statsData.share_channels">渠道: {{ Object.keys(statsData.share_channels || {}).length }}</span>
        </div>
      </div>
      
      <!-- 趋势图表区域（预留） -->
      <div class="trend-section">
        <h4>数据趋势</h4>
        <div class="trend-placeholder">
          <!-- 这里可以集成图表库，如ECharts或Chart.js -->
          <span>图表展示区域（预留）</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

// 组件属性
const props = defineProps({
  statsData: {
    type: Object,
    default: () => ({})
  },
  isLoading: {
    type: Boolean,
    default: false
  }
})

// 格式化时长（秒转小时:分钟:秒）
const formatDuration = (seconds) => {
  if (!seconds || isNaN(seconds)) return '0分钟'
  
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  
  if (hours > 0) {
    return `${hours}小时${minutes}分钟`
  } else {
    return `${minutes}分钟`
  }
}
</script>

<style scoped>
.book-stats-panel {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.loading-stats {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  padding: 20px 0;
  color: #666;
}

.loading-spinner-small {
  width: 16px;
  height: 16px;
  border: 2px solid #f3f3f3;
  border-top: 2px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.no-stats {
  text-align: center;
  padding: 20px 0;
  color: #999;
  font-style: italic;
}

.stats-content {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.stat-card {
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.stat-icon {
  font-size: 18px;
}

.stat-title {
  font-weight: bold;
  color: #555;
  font-size: 14px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
  margin-bottom: 5px;
}

.stat-detail {
  font-size: 12px;
  color: #999;
}

.trend-section {
  margin-top: 10px;
}

.trend-section h4 {
  margin: 0 0 10px 0;
  color: #555;
  font-size: 14px;
  font-weight: bold;
}

.trend-placeholder {
  background: #fafafa;
  padding: 30px 20px;
  text-align: center;
  border-radius: 8px;
  color: #999;
  font-style: italic;
  border: 1px dashed #ddd;
}
</style>
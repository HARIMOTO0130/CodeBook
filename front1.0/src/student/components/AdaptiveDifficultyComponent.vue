<template>
  <div class="adaptive-difficulty-container">
    <h2 class="section-title">自适应难度调整</h2>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <!-- 错误提示 -->
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="loadData" class="retry-button">重试</button>
    </div>
    
    <!-- 内容区域 -->
    <div v-else class="content-wrapper">
      <!-- 能力评估卡片 -->
      <div class="ability-card">
        <h3 class="card-title">能力评估</h3>
        <div class="ability-info">
          <div class="ability-item">
            <span class="label">能力水平：</span>
            <span class="value">{{ formattedAbilityLevel }}</span>
            <div class="ability-bar">
              <div class="ability-fill" :style="{ width: (abilityEvaluation.ability_level / 5) * 100 + '%' }"></div>
            </div>
          </div>
          <div class="ability-item">
            <span class="label">平均成绩：</span>
            <span class="value">{{ abilityEvaluation.average_score.toFixed(1) }}%</span>
          </div>
          <div class="ability-item">
            <span class="label">成绩趋势：</span>
            <span class="value" :class="`trend-${abilityEvaluation.score_trend}`">
              {{ trendText }}
            </span>
          </div>
        </div>
        <button @click="loadAbilityEvaluation" class="refresh-button">
          刷新评估
        </button>
      </div>
      
      <!-- 难度调整卡片 -->
      <div class="difficulty-card">
        <h3 class="card-title">难度调整</h3>
        <div class="difficulty-adjustment">
          <div class="current-difficulty">
            <span class="label">当前难度：</span>
            <span class="value">{{ currentDifficulty.toFixed(1) }}</span>
            <span class="difficulty-label">{{ formattedCurrentDifficulty }}</span>
          </div>
          <div class="performance-input">
            <span class="label">用户表现：</span>
            <input 
              type="range" 
              min="0" 
              max="100" 
              v-model.number="performance" 
              class="performance-slider"
            />
            <span class="performance-value">{{ performance }}%</span>
          </div>
          <button @click="adjustDifficultyLevel" class="adjust-button">
            调整难度
          </button>
        </div>
        <!-- 调整结果 -->
        <div v-if="adjustmentResult" class="adjustment-result">
          <h4>调整结果</h4>
          <p>旧难度：{{ adjustmentResult.old_difficulty.toFixed(1) }} → 新难度：{{ adjustmentResult.new_difficulty.toFixed(1) }}</p>
          <p class="adjustment-reason">{{ adjustmentResult.adjustment_reason }}</p>
        </div>
      </div>
      
      <!-- 难度建议卡片 -->
      <div class="recommendations-card">
        <h3 class="card-title">难度建议</h3>
        <div class="recommendations-list">
          <div v-for="(recommendation, index) in recommendations" :key="index" class="recommendation-item">
            <div class="recommendation-header">
              <h4>{{ recommendation.title }}</h4>
              <span :class="`priority-badge priority-${recommendation.priority}`">
                {{ priorityText(recommendation.priority) }}
              </span>
            </div>
            <p class="recommendation-description">{{ recommendation.description }}</p>
            <div class="recommendation-footer">
              <span class="estimated-time">预计时间：{{ recommendation.estimated_time }}分钟</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 知识点掌握情况 -->
      <div class="mastery-card">
        <h3 class="card-title">知识点掌握情况</h3>
        <div class="mastery-list">
          <div v-for="(mastery, knowledge) in abilityEvaluation.knowledge_mastery.mastery_levels" :key="knowledge" class="mastery-item">
            <span class="knowledge-name">{{ knowledge }}</span>
            <div class="mastery-bar">
              <div class="mastery-fill" :style="{ width: (mastery * 100) + '%' }"></div>
            </div>
            <span class="mastery-percentage">{{ (mastery * 100).toFixed(1) }}%</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { evaluateAbility, adjustDifficulty, generateDifficultyRecommendations, formatDifficulty, formatAbilityLevel, generateMockAbilityEvaluation, generateMockDifficultyRecommendations } from '../api/adaptive_difficulty_api';

export default {
  name: 'AdaptiveDifficultyComponent',
  data() {
    return {
      loading: true,
      error: null,
      abilityEvaluation: {
        ability_level: 3.0,
        average_score: 75.0,
        score_trend: 'stable',
        knowledge_mastery: {
          mastery_levels: {},
          average_mastery: 0.6,
          total_knowledge_points: 0
        },
        data_available: false
      },
      currentDifficulty: 3.0,
      performance: 70,
      adjustmentResult: null,
      recommendations: []
    };
  },
  computed: {
    formattedAbilityLevel() {
      return formatAbilityLevel(this.abilityEvaluation.ability_level);
    },
    formattedCurrentDifficulty() {
      return formatDifficulty(this.currentDifficulty);
    },
    trendText() {
      const trends = {
        'improving': '上升',
        'declining': '下降',
        'stable': '稳定',
        'insufficient_data': '数据不足'
      };
      return trends[this.abilityEvaluation.score_trend] || '未知';
    }
  },
  mounted() {
    this.loadData();
  },
  methods: {
    async loadData() {
      this.loading = true;
      this.error = null;
      try {
        // 并行加载数据
        const [abilityData, recommendationsData] = await Promise.all([
          this.loadAbilityEvaluation(),
          this.loadRecommendations()
        ]);
        
        this.abilityEvaluation = abilityData;
        this.recommendations = recommendationsData.recommendations;
      } catch (error) {
        this.error = '加载数据失败，请重试';
        // 使用模拟数据
        this.abilityEvaluation = generateMockAbilityEvaluation();
        this.recommendations = generateMockDifficultyRecommendations().recommendations;
      } finally {
        this.loading = false;
      }
    },
    async loadAbilityEvaluation() {
      try {
        const data = await evaluateAbility();
        return data;
      } catch (error) {
        // 使用模拟数据
        return generateMockAbilityEvaluation();
      }
    },
    async loadRecommendations() {
      try {
        const data = await generateDifficultyRecommendations();
        return data;
      } catch (error) {
        // 使用模拟数据
        return generateMockDifficultyRecommendations();
      }
    },
    async adjustDifficultyLevel() {
      this.loading = true;
      try {
        const result = await adjustDifficulty(this.currentDifficulty, this.performance);
        this.adjustmentResult = result;
        this.currentDifficulty = result.new_difficulty;
        // 重新加载能力评估
        this.abilityEvaluation = await this.loadAbilityEvaluation();
      } catch (error) {
        // 模拟调整结果
        const adjustment = this.performance >= 90 ? 0.5 : this.performance >= 70 ? 0.2 : this.performance >= 40 ? 0 : -0.5;
        const newDifficulty = Math.max(1, Math.min(5, this.currentDifficulty + adjustment));
        this.adjustmentResult = {
          old_difficulty: this.currentDifficulty,
          new_difficulty: newDifficulty,
          adjustment: adjustment,
          adjustment_reason: newDifficulty >= 4.5 ? '基于您的优秀表现，推荐挑战更高难度的内容' : newDifficulty >= 2.5 ? '建议保持当前难度或适当调整' : '推荐从简单内容开始，打好基础'
        };
        this.currentDifficulty = newDifficulty;
      } finally {
        this.loading = false;
      }
    },
    priorityText(priority) {
      const priorities = {
        'high': '高',
        'medium': '中',
        'low': '低'
      };
      return priorities[priority] || '未知';
    }
  }
};
</script>

<style scoped>
.adaptive-difficulty-container {
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
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.ability-card,
.difficulty-card,
.recommendations-card,
.mastery-card {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.card-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 15px;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 10px;
}

.ability-info {
  margin-bottom: 20px;
}

.ability-item {
  margin-bottom: 15px;
}

.label {
  display: inline-block;
  width: 100px;
  font-weight: 500;
  color: #606266;
}

.value {
  font-weight: bold;
  color: #303133;
}

.ability-bar {
  width: 100%;
  height: 8px;
  background-color: #ebeef5;
  border-radius: 4px;
  margin-top: 5px;
  overflow: hidden;
}

.ability-fill {
  height: 100%;
  background-color: #409EFF;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.trend-improving {
  color: #67c23a;
}

.trend-declining {
  color: #f56c6c;
}

.trend-stable {
  color: #e6a23c;
}

.refresh-button {
  width: 100%;
  padding: 8px;
  background-color: #f0f9eb;
  color: #67c23a;
  border: 1px solid #c2e7b0;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.refresh-button:hover {
  background-color: #e1f5cb;
}

.difficulty-adjustment {
  margin-bottom: 20px;
}

.current-difficulty {
  margin-bottom: 15px;
}

.difficulty-label {
  margin-left: 10px;
  padding: 2px 8px;
  background-color: #ecf5ff;
  color: #409EFF;
  border-radius: 10px;
  font-size: 12px;
}

.performance-input {
  margin-bottom: 20px;
}

.performance-slider {
  width: 200px;
  margin: 0 10px;
}

.performance-value {
  font-weight: bold;
  color: #409EFF;
  min-width: 40px;
  display: inline-block;
}

.adjust-button {
  width: 100%;
  padding: 10px;
  background-color: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
}

.adjust-button:hover {
  background-color: #66b1ff;
}

.adjustment-result {
  margin-top: 20px;
  padding: 15px;
  background-color: #ecf5ff;
  border-radius: 4px;
  border-left: 4px solid #409EFF;
}

.adjustment-result h4 {
  margin-top: 0;
  color: #303133;
}

.adjustment-reason {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}

.recommendations-list {
  max-height: 300px;
  overflow-y: auto;
}

.recommendation-item {
  background-color: #f9f9f9;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 10px;
}

.recommendation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.recommendation-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.priority-badge {
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 500;
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

.recommendation-description {
  margin: 8px 0;
  font-size: 14px;
  color: #606266;
  line-height: 1.4;
}

.recommendation-footer {
  margin-top: 10px;
  font-size: 12px;
  color: #909399;
}

.mastery-list {
  max-height: 300px;
  overflow-y: auto;
}

.mastery-item {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}

.knowledge-name {
  width: 120px;
  font-size: 14px;
  color: #303133;
}

.mastery-bar {
  flex: 1;
  height: 6px;
  background-color: #ebeef5;
  border-radius: 3px;
  margin: 0 10px;
  overflow: hidden;
}

.mastery-fill {
  height: 100%;
  background-color: #67c23a;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.mastery-percentage {
  width: 50px;
  font-size: 12px;
  color: #909399;
  text-align: right;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content-wrapper {
    grid-template-columns: 1fr;
  }
  
  .ability-item {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .label {
    width: 100%;
    margin-bottom: 5px;
  }
  
  .performance-input {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
  }
  
  .performance-slider {
    flex: 1;
    margin: 10px 0;
  }
  
  .mastery-item {
    flex-wrap: wrap;
  }
  
  .knowledge-name {
    width: 100%;
    margin-bottom: 5px;
  }
  
  .mastery-bar {
    flex: 1;
    margin: 0;
  }
  
  .mastery-percentage {
    width: 100%;
    text-align: left;
    margin-top: 5px;
  }
}
</style>
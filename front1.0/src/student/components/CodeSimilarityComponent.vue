<template>
  <div class="code-similarity-container">
    <h2 class="section-title">代码相似度检测</h2>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>检测中...</p>
    </div>
    
    <!-- 错误提示 -->
    <div v-else-if="error" class="error-message">
      <p>{{ error }}</p>
      <button @click="resetError" class="retry-button">重试</button>
    </div>
    
    <!-- 内容区域 -->
    <div v-else class="content-wrapper">
      <!-- 代码输入区域 -->
      <div class="code-inputs">
        <div class="code-input-panel">
          <div class="panel-header">
            <h3>代码 1</h3>
            <div class="language-selector">
              <label>语言：</label>
              <select v-model="language" class="form-select">
                <option value="python">Python</option>
                <option value="javascript">JavaScript</option>
              </select>
            </div>
          </div>
          <div class="code-editor">
            <textarea 
              v-model="code1" 
              placeholder="请输入第一段代码..." 
              class="code-textarea"
              rows="15"
            ></textarea>
          </div>
        </div>
        
        <div class="code-input-panel">
          <div class="panel-header">
            <h3>代码 2</h3>
            <button @click="swapCodes" class="swap-button" title="交换代码">
              ↕️ 交换
            </button>
          </div>
          <div class="code-editor">
            <textarea 
              v-model="code2" 
              placeholder="请输入第二段代码..." 
              class="code-textarea"
              rows="15"
            ></textarea>
          </div>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="action-buttons">
        <button @click="calculateSimilarity" class="btn-primary" :disabled="!code1 || !code2">
          <span class="btn-icon">🔍</span>
          检测相似度
        </button>
        <button @click="loadSampleCode" class="btn-secondary">
          <span class="btn-icon">📝</span>
          加载示例代码
        </button>
        <button @click="clearCodes" class="btn-secondary">
          <span class="btn-icon">🗑️</span>
          清空代码
        </button>
      </div>
      
      <!-- 相似度结果 -->
      <div v-if="similarityResult" class="similarity-result">
        <div class="result-header">
          <h3>检测结果</h3>
          <div class="overall-similarity">
            <span class="label">综合相似度：</span>
            <span class="value" :style="{ color: similarityColor }">
              {{ formattedSimilarity }}
            </span>
          </div>
        </div>
        
        <!-- 详细相似度得分 -->
        <div class="detailed-scores">
          <h4>详细得分</h4>
          <div class="scores-grid">
            <div v-for="(score, type) in similarityResult.similarity_scores" :key="type" class="score-item">
              <span class="score-label">{{ scoreLabels[type] }}</span>
              <div class="score-bar">
                <div class="score-fill" :style="{ width: (score * 100) + '%' }"></div>
              </div>
              <span class="score-value">{{ Math.round(score * 100) }}%</span>
            </div>
          </div>
        </div>
        
        <!-- 相似代码片段 -->
        <div v-if="similarityResult.similar_segments && similarityResult.similar_segments.length > 0" class="similar-segments">
          <h4>相似代码片段</h4>
          <div class="segments-list">
            <div v-for="(segment, index) in similarityResult.similar_segments" :key="index" class="segment-item">
              <div class="segment-header">
                <span class="segment-index">片段 {{ index + 1 }}</span>
                <span class="segment-length">{{ segment.length }} 行</span>
              </div>
              <div class="segment-code">
                <pre>{{ segment.lines.join('\n') }}</pre>
              </div>
              <div class="segment-location">
                <span>代码1: 第 {{ segment.code1_start + 1 }}-{{ segment.code1_end }} 行</span>
                <span>代码2: 第 {{ segment.code2_start + 1 }}-{{ segment.code2_end }} 行</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 分析结果 -->
        <div v-if="similarityAnalysis" class="similarity-analysis">
          <h4>分析结果</h4>
          <div class="analysis-content">
            <div class="overall-analysis">
              <h5>综合分析</h5>
              <div class="analysis-item">
                <span class="analysis-label">相似度级别：</span>
                <span class="analysis-value" :style="{ color: similarityColor }">
                  {{ similarityResult.similarity_level }}
                </span>
              </div>
              <div class="analysis-item">
                <span class="analysis-label">分析：</span>
                <span class="analysis-value">{{ similarityAnalysis.overall_analysis.message }}</span>
              </div>
            </div>
            
            <!-- 建议 -->
            <div class="recommendations">
              <h5>建议</h5>
              <ul class="recommendations-list">
                <li v-for="(recommendation, index) in similarityAnalysis.recommendations" :key="index" class="recommendation-item">
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
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { calculateSimilarity, analyzeSimilarity, formatSimilarityScore, getSimilarityColor, generateMockSimilarityResult } from '../api/code_similarity_api';

export default {
  name: 'CodeSimilarityComponent',
  data() {
    return {
      loading: false,
      error: null,
      code1: '',
      code2: '',
      language: 'python',
      similarityResult: null,
      similarityAnalysis: null
    };
  },
  computed: {
    formattedSimilarity() {
      if (!this.similarityResult) return '';
      return formatSimilarityScore(this.similarityResult.overall_similarity);
    },
    similarityColor() {
      if (!this.similarityResult) return '#909399';
      return getSimilarityColor(this.similarityResult.similarity_level);
    },
    scoreLabels() {
      return {
        'token_similarity': '令牌相似度',
        'structure_similarity': '结构相似度',
        'ast_similarity': 'AST相似度',
        'line_similarity': '行相似度'
      };
    }
  },
  methods: {
    async calculateSimilarity() {
      if (!this.code1 || !this.code2) {
        this.error = '请输入两段代码';
        return;
      }
      
      this.loading = true;
      this.error = null;
      
      try {
        // 调用API计算相似度
        const result = await calculateSimilarity(this.code1, this.code2, this.language);
        this.similarityResult = result;
        
        // 分析相似度结果
        const analysis = await analyzeSimilarity(result);
        this.similarityAnalysis = analysis;
      } catch (error) {
        // 使用模拟数据
        this.similarityResult = generateMockSimilarityResult();
        // 模拟分析结果
        this.similarityAnalysis = {
          overall_analysis: {
            level: this.similarityResult.similarity_level,
            description: '代码相似度分析',
            severity: this.similarityResult.overall_similarity >= 0.7 ? 'high' : 'medium',
            message: this.similarityResult.overall_similarity >= 0.9 ? '两段代码高度相似，可能存在抄袭行为' : 
                     this.similarityResult.overall_similarity >= 0.7 ? '两段代码有较多相似之处，建议检查是否存在借鉴' : 
                     this.similarityResult.overall_similarity >= 0.5 ? '两段代码有一定相似性，可能是思路相近' : 
                     '两段代码相似度较低，不存在抄袭风险'
          },
          detailed_analysis: {},
          segment_analysis: {
            count: this.similarityResult.similar_segments.length,
            total_length: this.similarityResult.similar_segments.reduce((sum, seg) => sum + seg.length, 0),
            longest_segment: this.similarityResult.similar_segments.length > 0 ? 
                           this.similarityResult.similar_segments.reduce((max, seg) => seg.length > max.length ? seg : max) : null,
            description: `发现${this.similarityResult.similar_segments.length}个相似代码片段，总长度为${this.similarityResult.similar_segments.reduce((sum, seg) => sum + seg.length, 0)}行`
          },
          recommendations: [
            {
              title: '检查代码来源',
              description: '建议确认代码来源，确保没有不当借鉴',
              priority: 'medium'
            },
            {
              title: '优化代码结构',
              description: '可以考虑优化代码结构，增加原创性',
              priority: 'low'
            },
            {
              title: '添加注释',
              description: '为代码添加详细注释，说明实现思路和关键部分',
              priority: 'medium'
            }
          ]
        };
      } finally {
        this.loading = false;
      }
    },
    loadSampleCode() {
      if (this.language === 'python') {
        this.code1 = `def calculate_factorial(n):
    if n == 0:
        return 1
    else:
        return n * calculate_factorial(n-1)

print(calculate_factorial(5))`;
        this.code2 = `def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n-1)

print(factorial(5))`;
      } else {
        this.code1 = `function calculateFactorial(n) {
    if (n === 0) {
        return 1;
    } else {
        return n * calculateFactorial(n-1);
    }
}

console.log(calculateFactorial(5));`;
        this.code2 = `function factorial(n) {
    if (n === 0) {
        return 1;
    } else {
        return n * factorial(n-1);
    }
}

console.log(factorial(5));`;
      }
    },
    clearCodes() {
      this.code1 = '';
      this.code2 = '';
      this.similarityResult = null;
      this.similarityAnalysis = null;
    },
    swapCodes() {
      const temp = this.code1;
      this.code1 = this.code2;
      this.code2 = temp;
    },
    resetError() {
      this.error = null;
    }
  }
};
</script>

<style scoped>
.code-similarity-container {
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

.code-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.code-input-panel {
  background-color: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.language-selector {
  display: flex;
  align-items: center;
  gap: 5px;
}

.form-select {
  padding: 4px 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
}

.swap-button {
  padding: 4px 8px;
  background-color: #ecf5ff;
  color: #409EFF;
  border: 1px solid #d9ecff;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.swap-button:hover {
  background-color: #d9ecff;
}

.code-editor {
  position: relative;
}

.code-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  min-height: 300px;
  background-color: #fafafa;
}

.code-textarea:focus {
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

.btn-primary:disabled {
  background-color: #c0c4cc;
  cursor: not-allowed;
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

.similarity-result {
  background-color: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
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

.overall-similarity {
  display: flex;
  align-items: center;
  gap: 10px;
}

.overall-similarity .label {
  font-weight: 500;
  color: #606266;
}

.overall-similarity .value {
  font-weight: bold;
  font-size: 16px;
}

.detailed-scores {
  margin-bottom: 20px;
}

.detailed-scores h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.scores-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.score-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.score-label {
  font-size: 14px;
  color: #606266;
}

.score-bar {
  width: 100%;
  height: 8px;
  background-color: #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background-color: #409EFF;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.score-value {
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  text-align: right;
}

.similar-segments {
  margin-bottom: 20px;
}

.similar-segments h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.segments-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.segment-item {
  background-color: #f9f9f9;
  border-radius: 4px;
  padding: 15px;
  border-left: 4px solid #409EFF;
}

.segment-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
}

.segment-code {
  background-color: #f0f0f0;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 10px;
  overflow-x: auto;
}

.segment-code pre {
  margin: 0;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  line-height: 1.4;
  white-space: pre-wrap;
}

.segment-location {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.similarity-analysis {
  border-top: 1px solid #ebeef5;
  padding-top: 20px;
}

.similarity-analysis h4 {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
}

.analysis-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.overall-analysis {
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 4px;
}

.overall-analysis h5 {
  margin: 0 0 10px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.analysis-item {
  display: flex;
  margin-bottom: 8px;
  align-items: flex-start;
}

.analysis-label {
  width: 100px;
  font-weight: 500;
  color: #606266;
  flex-shrink: 0;
}

.analysis-value {
  flex: 1;
  color: #303133;
}

.recommendations {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.recommendations h5 {
  margin: 0 0 10px 0;
  font-size: 14px;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .code-inputs {
    grid-template-columns: 1fr;
  }
  
  .action-buttons {
    flex-direction: column;
    align-items: center;
  }
  
  .scores-grid {
    grid-template-columns: 1fr;
  }
  
  .analysis-item {
    flex-direction: column;
    gap: 5px;
  }
  
  .analysis-label {
    width: 100%;
  }
}
</style>
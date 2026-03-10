<template>
  <div class="code-review-component">
    <!-- 代码编辑器区域 -->
    <div class="editor-section">
      <div class="editor-header">
        <h3>代码编辑器</h3>
        <div class="language-selector">
          <label for="language-select">编程语言:</label>
          <select id="language-select" v-model="selectedLanguage" @change="onLanguageChange">
            <option v-for="lang in supportedLanguages" :key="lang.value" :value="lang.value">
              {{ lang.icon }} {{ lang.label }}
            </option>
          </select>
        </div>
        <div class="editor-actions">
          <button @click="loadExample" class="btn btn-secondary">加载示例</button>
          <button @click="clearCode" class="btn btn-secondary">清空代码</button>
          <button @click="submitReview" :disabled="isSubmitting" class="btn btn-primary">
            {{ isSubmitting ? '审查中...' : '开始审查' }}
          </button>
        </div>
      </div>
      
      <div class="editor-container">
        <textarea
          v-model="codeContent"
          placeholder="请输入您的代码..."
          class="code-editor"
          :style="{ height: editorHeight + 'px' }"
        ></textarea>
        <div class="editor-info">
          <span>行数: {{ lineCount }}</span>
          <span>字符数: {{ charCount }}</span>
        </div>
      </div>
    </div>

    <!-- 审查结果区域 -->
    <div class="result-section" v-if="reviewResult">
      <div class="result-header">
        <h3>审查结果</h3>
        <div class="score-display" :style="{ color: scoreLevel.color }">
          <span class="score-icon">{{ scoreLevel.icon }}</span>
          <span class="score-value">{{ reviewResult.overallScore }}</span>
          <span class="score-level">{{ scoreLevel.level }}</span>
        </div>
      </div>

      <!-- 问题摘要 -->
      <div class="summary-section">
        <div class="summary-item" v-for="item in summaryItems" :key="item.type">
          <span class="summary-count" :style="{ color: item.color }">{{ item.count }}</span>
          <span class="summary-label">{{ item.label }}</span>
        </div>
      </div>

      <!-- 问题详情 -->
      <div class="issues-section">
        <div class="issues-tabs">
          <button 
            v-for="tab in tabs" 
            :key="tab.key"
            :class="{ active: activeTab === tab.key }"
            @click="activeTab = tab.key"
            class="tab-btn"
          >
            {{ tab.label }} ({{ tab.count }})
          </button>
        </div>

        <div class="issues-content">
          <!-- 语法问题 -->
          <div v-if="activeTab === 'syntax' && syntaxIssues.length" class="issue-list">
            <div v-for="issue in syntaxIssues" :key="issue.message" class="issue-item">
              <div class="issue-header">
                <span class="issue-severity" :style="{ backgroundColor: getSeverityColor(issue.severity) }">
                  {{ issue.severity }}
                </span>
                <span class="issue-line" v-if="issue.line">第 {{ issue.line }} 行</span>
              </div>
              <div class="issue-message">{{ issue.message }}</div>
            </div>
          </div>

          <!-- 质量问题 -->
          <div v-if="activeTab === 'quality' && qualityIssues.length" class="issue-list">
            <div v-for="issue in qualityIssues" :key="issue.message" class="issue-item">
              <div class="issue-header">
                <span class="issue-severity" :style="{ backgroundColor: getSeverityColor(issue.severity) }">
                  {{ issue.severity }}
                </span>
                <span class="issue-line" v-if="issue.line">第 {{ issue.line }} 行</span>
                <span class="issue-element" v-if="issue.element">{{ issue.element }}</span>
              </div>
              <div class="issue-message">{{ issue.message }}</div>
            </div>
          </div>

          <!-- AI建议 -->
          <div v-if="activeTab === 'suggestions' && reviewResult.suggestions.length" class="suggestion-list">
            <div v-for="(suggestion, index) in reviewResult.suggestions" :key="index" class="suggestion-item">
              <div class="suggestion-header">
                <span class="suggestion-type">{{ suggestion.type || '建议' }}</span>
                <span class="suggestion-severity" :style="{ backgroundColor: getSeverityColor(suggestion.severity) }">
                  {{ suggestion.severity }}
                </span>
              </div>
              <div class="suggestion-message">{{ suggestion.message }}</div>
            </div>
          </div>

          <!-- 改进建议 -->
          <div v-if="activeTab === 'improvements' && reviewResult.improvementSuggestions.length" class="improvement-list">
            <div v-for="(suggestion, index) in reviewResult.improvementSuggestions" :key="index" class="improvement-item">
              <span class="improvement-icon">💡</span>
              <span class="improvement-text">{{ suggestion }}</span>
            </div>
          </div>

          <!-- 空状态 -->
          <div v-if="activeTabCount === 0" class="empty-state">
            <p>🎉 恭喜！代码质量良好，没有发现问题。</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="isSubmitting" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p>正在分析代码...</p>
    </div>
  </div>
</template>

<script>
import { codeReviewAPI, codeReviewUtils, codeReviewExamples } from '../api/code_review_api'

export default {
  name: 'CodeReviewComponent',
  
  data() {
    return {
      codeContent: '',
      selectedLanguage: 'python',
      isSubmitting: false,
      reviewResult: null,
      activeTab: 'syntax',
      editorHeight: 300,
      supportedLanguages: codeReviewExamples.getSupportedLanguages()
    }
  },

  computed: {
    lineCount() {
      return this.codeContent.split('\n').length
    },

    charCount() {
      return this.codeContent.length
    },

    scoreLevel() {
      if (!this.reviewResult) return { level: '', color: '#718096', icon: '' }
      return codeReviewUtils.getScoreLevel(this.reviewResult.overallScore)
    },

    syntaxIssues() {
      return this.reviewResult?.issues?.filter(issue => issue.category === 'syntax') || []
    },

    qualityIssues() {
      return this.reviewResult?.issues?.filter(issue => issue.category === 'quality') || []
    },

    summaryItems() {
      if (!this.reviewResult) return []
      
      const summary = codeReviewUtils.generateSummary(this.reviewResult)
      
      return [
        {
          type: 'high',
          label: '严重问题',
          count: summary.highIssues,
          color: codeReviewUtils.getSeverityColor('high')
        },
        {
          type: 'medium',
          label: '中等问题',
          count: summary.mediumIssues,
          color: codeReviewUtils.getSeverityColor('medium')
        },
        {
          type: 'low',
          label: '轻微问题',
          count: summary.lowIssues,
          color: codeReviewUtils.getSeverityColor('low')
        },
        {
          type: 'suggestions',
          label: 'AI建议',
          count: summary.totalSuggestions,
          color: '#4299e1'
        }
      ]
    },

    tabs() {
      return [
        {
          key: 'syntax',
          label: '语法问题',
          count: this.syntaxIssues.length
        },
        {
          key: 'quality',
          label: '质量问题',
          count: this.qualityIssues.length
        },
        {
          key: 'suggestions',
          label: 'AI建议',
          count: this.reviewResult?.suggestions?.length || 0
        },
        {
          key: 'improvements',
          label: '改进建议',
          count: this.reviewResult?.improvementSuggestions?.length || 0
        }
      ]
    },

    activeTabCount() {
      const tab = this.tabs.find(t => t.key === this.activeTab)
      return tab ? tab.count : 0
    }
  },

  methods: {
    getSeverityColor(severity) {
      return codeReviewUtils.getSeverityColor(severity)
    },

    async submitReview() {
      if (!this.codeContent.trim()) {
        alert('请输入代码内容')
        return
      }

      this.isSubmitting = true
      
      try {
        const result = await codeReviewAPI.submitCodeReview(
          this.codeContent,
          this.selectedLanguage,
          { source: 'code_review_component' }
        )
        
        this.reviewResult = codeReviewUtils.formatReviewResult(result)
        
        // 自动切换到有问题最多的标签页
        const maxTab = this.tabs.reduce((max, tab) => 
          tab.count > max.count ? tab : max
        )
        if (maxTab.count > 0) {
          this.activeTab = maxTab.key
        }
        
      } catch (error) {
        console.error('代码审查失败:', error)
        alert('代码审查失败，请稍后重试')
      } finally {
        this.isSubmitting = false
      }
    },

    loadExample() {
      this.codeContent = codeReviewExamples.getExampleCode(this.selectedLanguage)
    },

    clearCode() {
      this.codeContent = ''
      this.reviewResult = null
    },

    onLanguageChange() {
      this.reviewResult = null
      // 如果当前有代码内容，重新加载对应语言的示例
      if (this.codeContent) {
        this.loadExample()
      }
    }
  },

  mounted() {
    // 加载默认示例代码
    this.loadExample()
  }
}
</script>

<style scoped>
.code-review-component {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

.editor-section {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 20px;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  flex-wrap: wrap;
  gap: 15px;
}

.editor-header h3 {
  margin: 0;
  color: #2d3748;
}

.language-selector {
  display: flex;
  align-items: center;
  gap: 10px;
}

.language-selector select {
  padding: 5px 10px;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  background: white;
}

.editor-actions {
  display: flex;
  gap: 10px;
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

.editor-container {
  position: relative;
}

.code-editor {
  width: 100%;
  padding: 15px;
  border: 1px solid #cbd5e0;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  background: white;
}

.editor-info {
  position: absolute;
  bottom: 5px;
  right: 10px;
  font-size: 12px;
  color: #718096;
}

.result-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e2e8f0;
}

.result-header h3 {
  margin: 0;
  color: #2d3748;
}

.score-display {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: bold;
}

.score-icon {
  font-size: 24px;
}

.score-value {
  font-size: 32px;
}

.summary-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.summary-item {
  text-align: center;
  padding: 15px;
  background: #f7fafc;
  border-radius: 6px;
}

.summary-count {
  display: block;
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.summary-label {
  font-size: 14px;
  color: #718096;
}

.issues-tabs {
  display: flex;
  border-bottom: 1px solid #e2e8f0;
  margin-bottom: 20px;
}

.tab-btn {
  padding: 10px 20px;
  border: none;
  background: none;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-btn.active {
  border-bottom-color: #4299e1;
  color: #4299e1;
  font-weight: bold;
}

.tab-btn:hover {
  background: #f7fafc;
}

.issue-item, .suggestion-item, .improvement-item {
  padding: 15px;
  margin-bottom: 10px;
  border-radius: 6px;
  background: #f7fafc;
}

.issue-header, .suggestion-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.issue-severity, .suggestion-severity {
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
  color: white;
  font-weight: bold;
}

.issue-line, .issue-element, .suggestion-type {
  font-size: 12px;
  color: #718096;
}

.issue-message, .suggestion-message {
  color: #2d3748;
  line-height: 1.4;
}

.improvement-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.improvement-icon {
  font-size: 18px;
}

.improvement-text {
  color: #2d3748;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #718096;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-top: 4px solid #4299e1;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

@media (max-width: 768px) {
  .code-review-component {
    padding: 10px;
  }
  
  .editor-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .language-selector {
    justify-content: space-between;
  }
  
  .editor-actions {
    justify-content: center;
  }
  
  .summary-section {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .issues-tabs {
    flex-wrap: wrap;
  }
  
  .tab-btn {
    flex: 1;
    min-width: 120px;
  }
}
</style>
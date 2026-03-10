<template>
  <div class="review-detail">
    <!-- 内容访问控制提示 -->
    <ContentAccessAlert access-level="metadata" />

    <div class="detail-header card">
      <div class="header-info">
        <h2>{{ task.book_title }}</h2>
        <p class="meta">
          <span>作者：{{ task.book_author }}</span>
          <span>版本：{{ task.version_number }}</span>
          <span>章节数：{{ task.chapter_count }}</span>
          <span :class="['status-badge', `status-${task.status}`]">{{ task.status_display }}</span>
        </p>
      </div>
      <div class="header-actions">
        <button v-if="task.status === 'pending'" class="btn-primary" @click="claimTask">
          认领任务
        </button>
        <button v-if="task.status === 'in_review' && task.assigned_reviewer_name === currentUser" 
                class="btn-default" @click="releaseTask">
          释放任务
        </button>
      </div>
    </div>

    <div class="detail-content">
      <div class="left-panel">
        <!-- 教材基本信息 -->
        <div class="card">
          <h3 class="card-title">教材基本信息</h3>
          <div class="info-grid">
            <div class="info-item">
              <label>教材ID</label>
              <span>{{ task.book_id }}</span>
            </div>
            <div class="info-item">
              <label>标题</label>
              <span>{{ task.book_title }}</span>
            </div>
            <div class="info-item" v-if="task.book_subtitle">
              <label>副标题</label>
              <span>{{ task.book_subtitle }}</span>
            </div>
            <div class="info-item">
              <label>作者</label>
              <span>{{ task.book_author }}</span>
            </div>
            <div class="info-item" v-if="task.book_isbn">
              <label>ISBN</label>
              <span>{{ task.book_isbn }}</span>
            </div>
            <div class="info-item">
              <label>语言</label>
              <span>{{ task.book_language || 'zh-CN' }}</span>
            </div>
            <div class="info-item">
              <label>字数</label>
              <span>{{ task.book_word_count || 0 }} 字</span>
            </div>
            <div class="info-item">
              <label>章节数</label>
              <span>{{ task.chapter_count }}</span>
            </div>
            <div class="info-item" v-if="task.category_name">
              <label>分类</label>
              <span>{{ task.category_name }}</span>
            </div>
            <div class="info-item" v-if="task.tags?.length">
              <label>标签</label>
              <div class="tags">
                <span v-for="tag in task.tags" :key="tag" class="tag">{{ tag }}</span>
              </div>
            </div>
            <div class="info-item full-width">
              <label>描述</label>
              <span>{{ task.description || '暂无描述' }}</span>
            </div>
          </div>
        </div>

        <!-- 教师信息 -->
        <div class="card" v-if="task.submitted_by_info?.name">
          <h3 class="card-title">教师信息</h3>
          <div class="teacher-info-section">
            <!-- 提交人信息 -->
            <div class="teacher-card">
              <h4>提交人</h4>
              <div class="info-list">
                <div class="info-item">
                  <label>姓名</label>
                  <span>{{ task.submitted_by_info.name }}</span>
                </div>
                <div class="info-item" v-if="task.submitted_by_info.employee_id">
                  <label>工号</label>
                  <span>{{ task.submitted_by_info.employee_id }}</span>
                </div>
                <div class="info-item" v-if="task.submitted_by_info.department">
                  <label>部门</label>
                  <span>{{ task.submitted_by_info.department }}</span>
                </div>
                <div class="info-item" v-if="task.submitted_by_info.email">
                  <label>邮箱</label>
                  <span>{{ task.submitted_by_info.email }}</span>
                </div>
                <div class="info-item" v-if="task.submitted_by_info.phone">
                  <label>电话</label>
                  <span>{{ task.submitted_by_info.phone }}</span>
                </div>
              </div>
            </div>

            <!-- 原始上传者信息 -->
            <div class="teacher-card" v-if="task.original_uploader_info?.name && task.original_uploader_info.name !== task.submitted_by_info.name">
              <h4>原始上传者</h4>
              <div class="info-list">
                <div class="info-item">
                  <label>姓名</label>
                  <span>{{ task.original_uploader_info.name }}</span>
                </div>
                <div class="info-item" v-if="task.original_uploader_info.employee_id">
                  <label>工号</label>
                  <span>{{ task.original_uploader_info.employee_id }}</span>
                </div>
                <div class="info-item" v-if="task.original_uploader_info.department">
                  <label>部门</label>
                  <span>{{ task.original_uploader_info.department }}</span>
                </div>
              </div>
            </div>

            <!-- 修改者信息 -->
            <div class="teacher-card" v-if="task.modified_by_info?.name && task.modified_by_info.name !== task.submitted_by_info.name">
              <h4>修改者</h4>
              <div class="info-list">
                <div class="info-item">
                  <label>姓名</label>
                  <span>{{ task.modified_by_info.name }}</span>
                </div>
                <div class="info-item" v-if="task.modified_by_info.employee_id">
                  <label>工号</label>
                  <span>{{ task.modified_by_info.employee_id }}</span>
                </div>
                <div class="info-item" v-if="task.modified_by_info.department">
                  <label>部门</label>
                  <span>{{ task.modified_by_info.department }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 时间记录 -->
        <div class="card">
          <h3 class="card-title">时间记录</h3>
          <div class="timeline">
            <div class="timeline-item" v-if="task.original_uploaded_at">
              <div class="timeline-marker"></div>
              <div class="timeline-content">
                <div class="timeline-time">{{ formatDateTime(task.original_uploaded_at) }}</div>
                <div class="timeline-title">原始上传</div>
              </div>
            </div>
            <div class="timeline-item" v-if="task.last_modified_at">
              <div class="timeline-marker"></div>
              <div class="timeline-content">
                <div class="timeline-time">{{ formatDateTime(task.last_modified_at) }}</div>
                <div class="timeline-title">最后修改</div>
              </div>
            </div>
            <div class="timeline-item">
              <div class="timeline-marker active"></div>
              <div class="timeline-content">
                <div class="timeline-time">{{ formatDateTime(task.submitted_at) }}</div>
                <div class="timeline-title">提交审核</div>
                <div class="timeline-desc" v-if="task.change_summary">{{ task.change_summary }}</div>
              </div>
            </div>
            <div class="timeline-item" v-if="task.deadline">
              <div class="timeline-marker deadline"></div>
              <div class="timeline-content">
                <div class="timeline-time">{{ formatDateTime(task.deadline) }}</div>
                <div class="timeline-title">审核截止</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 修改历史 -->
        <div class="card" v-if="editHistory?.length">
          <h3 class="card-title">
            修改历史
            <span class="history-count">({{ editHistory.length }}条)</span>
          </h3>
          <div class="history-list">
            <div v-for="record in editHistory" :key="record.id" class="history-item">
              <div class="history-header">
                <span class="history-action">{{ record.action_display }}</span>
                <span class="history-time">{{ formatDateTime(record.created_at) }}</span>
              </div>
              <div class="history-actor">
                <span>{{ record.actor_name }}</span>
                <span v-if="record.actor_employee_id">({{ record.actor_employee_id }})</span>
                <span v-if="record.actor_department">- {{ record.actor_department }}</span>
              </div>
              <div class="history-version" v-if="record.version_number">
                版本: v{{ record.version_number }}
                <span v-if="record.previous_version">(上一版本: v{{ record.previous_version }})</span>
              </div>
              <div class="history-summary" v-if="record.changes_summary">
                {{ record.changes_summary }}
              </div>
            </div>
          </div>
        </div>

        <div class="card">
          <h3 class="card-title">
            AI审核结果
            <button v-if="!aiRecord || aiRecord.status !== 'completed'" 
                    class="btn-primary" style="float: right; padding: 4px 12px;"
                    @click="triggerAIReview" :disabled="aiLoading">
              {{ aiLoading ? '审核中...' : '触发AI审核' }}
            </button>
          </h3>
          
          <div v-if="!aiRecord" class="empty">暂未进行AI审核</div>
          <div v-else-if="aiRecord.status === 'pending'" class="loading">AI审核等待中...</div>
          <div v-else-if="aiRecord.status === 'processing'" class="loading">AI审核进行中...</div>
          <div v-else-if="aiRecord.status === 'failed'" class="error">
            AI审核失败：{{ aiRecord.error_message }}
          </div>
          <div v-else class="ai-result">
            <div class="ai-score">
              <div class="score-circle" :class="getScoreClass(aiRecord.overall_score)">
                {{ aiRecord.overall_score || 0 }}
              </div>
              <div class="score-info">
                <div class="risk-level" :class="`risk-${aiRecord.risk_level}`">
                  {{ aiRecord.risk_level_display }}
                </div>
                <div class="processing-time">处理耗时：{{ aiRecord.processing_time }}ms</div>
              </div>
            </div>

            <div class="score-details">
              <div class="score-item">
                <span class="score-label">内容合规性</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: `${aiRecord.content_compliance_score}%` }"></div>
                </div>
                <span class="score-value">{{ aiRecord.content_compliance_score }}</span>
              </div>
              <div class="score-item">
                <span class="score-label">准确性</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: `${aiRecord.accuracy_score}%` }"></div>
                </div>
                <span class="score-value">{{ aiRecord.accuracy_score }}</span>
              </div>
              <div class="score-item">
                <span class="score-label">完整性</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: `${aiRecord.completeness_score}%` }"></div>
                </div>
                <span class="score-value">{{ aiRecord.completeness_score }}</span>
              </div>
              <div class="score-item">
                <span class="score-label">可读性</span>
                <div class="score-bar">
                  <div class="score-fill" :style="{ width: `${aiRecord.readability_score}%` }"></div>
                </div>
                <span class="score-value">{{ aiRecord.readability_score }}</span>
              </div>
            </div>

            <!-- 风险项警告 -->
            <div v-if="aiRecord.risk_items?.length" class="risk-section">
              <h4 class="risk-title">
                <span class="warning-icon">⚠️</span>
                风险警告
              </h4>
              <div v-for="(risk, index) in aiRecord.risk_items" :key="index" 
                   class="risk-item" :class="`risk-level-${risk.level}`">
                <div class="risk-header">
                  <span class="risk-level-badge">{{ risk.level }}</span>
                  <span class="risk-category">{{ risk.category }}</span>
                </div>
                <div class="risk-desc">{{ risk.description }}</div>
              </div>
            </div>

            <div v-if="aiRecord.detected_issues?.length" class="issues-section">
              <h4>检测到的问题 ({{ aiRecord.detected_issues.length }}个)</h4>
              <div v-for="(issue, index) in sortedIssues" :key="index" class="issue-item"
                   :class="{ 'issue-highlight': issue.severity === 'high' || issue.severity === 'critical' }">
                <span class="issue-type">{{ issue.type }}</span>
                <span class="issue-severity" :class="`severity-${issue.severity}`">{{ issue.severity }}</span>
                <span v-if="issue.location" class="issue-location">{{ issue.location }}</span>
                <span class="issue-desc">{{ issue.description }}</span>
              </div>
            </div>

            <div v-if="aiRecord.suggestions?.length" class="suggestions-section">
              <h4>AI建议</h4>
              <ul>
                <li v-for="(suggestion, index) in aiRecord.suggestions" :key="index">
                  {{ suggestion }}
                  <button class="btn-link" @click="adoptSuggestion(suggestion)">采纳</button>
                </li>
              </ul>
            </div>

            <!-- AI辅助决策提示 -->
            <div v-if="aiRecord.status === 'completed'" class="ai-assistant-section">
              <h4>AI辅助决策参考</h4>
              <div class="ai-recommendation" :class="`recommend-${aiRecommendation.type}`">
                <div class="recommendation-title">
                  AI建议：{{ aiRecommendation.text }}
                </div>
                <div class="recommendation-reason">{{ aiRecommendation.reason }}</div>
              </div>
              <div class="quick-actions">
                <button class="btn-default" @click="applyAIScores">
                  应用AI评分作为参考
                </button>
                <button class="btn-default" @click="copyAIComment">
                  复制AI分析到审核意见
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="right-panel">
        <div class="card review-form-card">
          <h3 class="card-title">人工审核</h3>
          
          <div v-if="task.status !== 'in_review' || task.assigned_reviewer_name !== currentUser" class="empty">
            请先认领任务后再进行审核
          </div>
          
          <form v-else @submit.prevent="submitReview" class="review-form">
            <div class="form-section">
              <h4>评分（1-5分）</h4>
              <div class="score-inputs">
                <div class="score-input-item">
                  <label>内容质量</label>
                  <div class="star-rating">
                    <span v-for="i in 5" :key="i" 
                          :class="['star', { active: i <= form.content_quality_score }]"
                          @click="form.content_quality_score = i">★</span>
                  </div>
                </div>
                <div class="score-input-item">
                  <label>准确性</label>
                  <div class="star-rating">
                    <span v-for="i in 5" :key="i" 
                          :class="['star', { active: i <= form.accuracy_score }]"
                          @click="form.accuracy_score = i">★</span>
                  </div>
                </div>
                <div class="score-input-item">
                  <label>完整性</label>
                  <div class="star-rating">
                    <span v-for="i in 5" :key="i" 
                          :class="['star', { active: i <= form.completeness_score }]"
                          @click="form.completeness_score = i">★</span>
                  </div>
                </div>
                <div class="score-input-item">
                  <label>格式规范</label>
                  <div class="star-rating">
                    <span v-for="i in 5" :key="i" 
                          :class="['star', { active: i <= form.formatting_score }]"
                          @click="form.formatting_score = i">★</span>
                  </div>
                </div>
                <div class="score-input-item">
                  <label>语言表达</label>
                  <div class="star-rating">
                    <span v-for="i in 5" :key="i" 
                          :class="['star', { active: i <= form.language_score }]"
                          @click="form.language_score = i">★</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="form-section">
              <h4>审核决定</h4>
              <div class="decision-buttons">
                <button type="button" 
                        :class="['decision-btn', { active: form.decision === 'approved' }]"
                        @click="form.decision = 'approved'">
                  ✓ 通过
                </button>
                <button type="button" 
                        :class="['decision-btn', { active: form.decision === 'rejected' }]"
                        @click="form.decision = 'rejected'">
                  ✗ 驳回
                </button>
                <button type="button" 
                        :class="['decision-btn', { active: form.decision === 'needs_revision' }]"
                        @click="form.decision = 'needs_revision'">
                  ⟲ 需修改
                </button>
              </div>
            </div>

            <div class="form-section">
              <h4>审核意见</h4>
              <textarea v-model="form.overall_comment" 
                        placeholder="请输入审核意见..."
                        rows="4"></textarea>
            </div>

            <div class="form-section">
              <h4>修改建议</h4>
              <textarea v-model="form.suggestions" 
                        placeholder="请输入修改建议..."
                        rows="3"></textarea>
            </div>

            <div class="form-actions">
              <button type="submit" class="btn-primary" :disabled="submitting">
                {{ submitting ? '提交中...' : '提交审核' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { taskApi, reviewApi, editHistoryApi } from '../api/review'
import ContentAccessAlert from '../components/ContentAccessAlert.vue'

const route = useRoute()
const router = useRouter()

const task = ref({})
const aiRecord = ref(null)
const aiLoading = ref(false)
const submitting = ref(false)
const editHistory = ref([])

const currentUser = computed(() => {
  const user = JSON.parse(localStorage.getItem('review_user') || '{}')
  return user.username
})

const form = ref({
  content_quality_score: 3,
  accuracy_score: 3,
  completeness_score: 3,
  formatting_score: 3,
  language_score: 3,
  decision: '',
  overall_comment: '',
  suggestions: ''
})

const loadTask = async () => {
  try {
    const data = await taskApi.getDetail(route.params.id)
    task.value = data
    aiRecord.value = data.ai_record
    editHistory.value = data.edit_history || []
  } catch (err) {
    console.error('加载任务失败', err)
  }
}

const claimTask = async () => {
  try {
    await taskApi.claim(task.value.id)
    loadTask()
  } catch (err) {
    alert(err.response?.data?.error || '认领失败')
  }
}

const releaseTask = async () => {
  try {
    await taskApi.release(task.value.id)
    router.push('/review/pending')
  } catch (err) {
    alert(err.response?.data?.error || '释放失败')
  }
}

const triggerAIReview = async () => {
  aiLoading.value = true
  try {
    const data = await taskApi.triggerAIReview(task.value.id)
    aiRecord.value = data.ai_record
  } catch (err) {
    alert(err.response?.data?.error || 'AI审核失败')
  } finally {
    aiLoading.value = false
  }
}

const submitReview = async () => {
  if (!form.value.decision) {
    alert('请选择审核决定')
    return
  }
  
  submitting.value = true
  try {
    await reviewApi.createManualReview({
      task_id: task.value.id,
      ...form.value
    })
    alert('审核提交成功')
    router.push('/review/pending')
  } catch (err) {
    alert(err.response?.data?.error || '提交失败')
  } finally {
    submitting.value = false
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getScoreClass = (score) => {
  if (score >= 80) return 'score-high'
  if (score >= 60) return 'score-medium'
  return 'score-low'
}

// 按严重程度排序的问题列表
const sortedIssues = computed(() => {
  if (!aiRecord.value?.detected_issues) return []
  const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 }
  return [...aiRecord.value.detected_issues].sort((a, b) => {
    return (severityOrder[a.severity] || 4) - (severityOrder[b.severity] || 4)
  })
})

// AI推荐决策
const aiRecommendation = computed(() => {
  if (!aiRecord.value) return { type: 'neutral', text: '暂无建议', reason: '' }
  
  const score = aiRecord.value.overall_score || 0
  const riskLevel = aiRecord.value.risk_level
  const hasCriticalIssues = aiRecord.value.detected_issues?.some(
    issue => issue.severity === 'critical' || issue.severity === 'high'
  )
  
  if (score >= 80 && riskLevel === 'low' && !hasCriticalIssues) {
    return {
      type: 'approve',
      text: '建议通过',
      reason: `总体评分${score}分，风险等级低，无严重问题`
    }
  } else if (score >= 60 && riskLevel !== 'critical' && !hasCriticalIssues) {
    return {
      type: 'revise',
      text: '建议需修改',
      reason: `评分${score}分，存在一些问题需要修改`
    }
  } else {
    return {
      type: 'reject',
      text: '建议驳回',
      reason: `评分${score}分，风险等级${riskLevel}，存在严重问题`
    }
  }
})

// 采纳AI建议
const adoptSuggestion = (suggestion) => {
  if (!form.value.suggestions) {
    form.value.suggestions = suggestion
  } else {
    form.value.suggestions += '\n' + suggestion
  }
}

// 应用AI评分（转换为5分制）
const applyAIScores = () => {
  if (!aiRecord.value) return
  
  // 将百分制转换为5分制
  const convertScore = (score) => {
    if (!score) return 3
    return Math.max(1, Math.min(5, Math.round(score / 20)))
  }
  
  form.value.content_quality_score = convertScore(aiRecord.value.content_compliance_score)
  form.value.accuracy_score = convertScore(aiRecord.value.accuracy_score)
  form.value.completeness_score = convertScore(aiRecord.value.completeness_score)
  form.value.formatting_score = convertScore(aiRecord.value.readability_score)
  form.value.language_score = convertScore(aiRecord.value.readability_score)
}

// 复制AI分析到审核意见
const copyAIComment = () => {
  if (!aiRecord.value) return
  
  const issuesText = aiRecord.value.detected_issues?.map(issue => 
    `- [${issue.severity}] ${issue.type}: ${issue.description}`
  ).join('\n') || ''
  
  const suggestionsText = aiRecord.value.suggestions?.map((s, i) => 
    `${i + 1}. ${s}`
  ).join('\n') || ''
  
  form.value.overall_comment = `【AI审核分析】\n总体评分：${aiRecord.value.overall_score}分\n风险等级：${aiRecord.value.risk_level}\n\n【发现问题】\n${issuesText}\n\n【AI建议】\n${suggestionsText}`
}

onMounted(() => {
  loadTask()
})
</script>

<style scoped>
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-info h2 {
  margin-bottom: 8px;
}

.meta {
  display: flex;
  gap: 16px;
  color: var(--text-secondary);
}

.detail-content {
  display: grid;
  grid-template-columns: 1fr 400px;
  gap: 24px;
  margin-top: 24px;
}

.info-list {
  display: grid;
  gap: 12px;
}

.info-item {
  display: flex;
  gap: 12px;
}

.info-item label {
  width: 80px;
  color: var(--text-secondary);
}

.ai-score {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 20px;
}

.score-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: bold;
  color: #fff;
}

.score-circle.score-high { background: var(--success-color); }
.score-circle.score-medium { background: var(--warning-color); }
.score-circle.score-low { background: var(--error-color); }

.score-details {
  margin-bottom: 20px;
}

.score-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.score-label {
  width: 80px;
  color: var(--text-secondary);
}

.score-bar {
  flex: 1;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.score-fill {
  height: 100%;
  background: var(--primary-color);
  border-radius: 4px;
  transition: width 0.3s;
}

.score-value {
  width: 40px;
  text-align: right;
  font-weight: 600;
}

.issues-section, .suggestions-section, .risk-section, .ai-assistant-section {
  margin-top: 20px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.issues-section h4, .suggestions-section h4, .risk-section h4, .ai-assistant-section h4 {
  margin-bottom: 12px;
}

/* 风险警告区域 */
.risk-title {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #f5222d;
}

.warning-icon {
  font-size: 18px;
}

.risk-item {
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 12px;
  border-left: 4px solid;
}

.risk-item.risk-level-critical {
  background: #fff2f0;
  border-left-color: #f5222d;
}

.risk-item.risk-level-high {
  background: #fff7e6;
  border-left-color: #fa8c16;
}

.risk-item.risk-level-medium {
  background: #fffbe6;
  border-left-color: #faad14;
}

.risk-item.risk-level-low {
  background: #f6ffed;
  border-left-color: #52c41a;
}

.risk-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.risk-level-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
}

.risk-level-critical .risk-level-badge {
  background: #f5222d;
  color: #fff;
}

.risk-level-high .risk-level-badge {
  background: #fa8c16;
  color: #fff;
}

.risk-level-medium .risk-level-badge {
  background: #faad14;
  color: #fff;
}

.risk-level-low .risk-level-badge {
  background: #52c41a;
  color: #fff;
}

.risk-category {
  font-weight: 600;
  color: var(--text-color);
}

.risk-desc {
  color: var(--text-secondary);
  font-size: 14px;
}

/* 问题列表 */
.issue-item {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 10px;
  background: #fafafa;
  border-radius: 4px;
  margin-bottom: 8px;
  align-items: flex-start;
}

.issue-item.issue-highlight {
  background: #fff2f0;
  border: 1px solid #ffccc7;
}

.issue-type {
  padding: 2px 8px;
  background: #e6f7ff;
  border-radius: 4px;
  font-size: 12px;
  white-space: nowrap;
}

.issue-location {
  padding: 2px 8px;
  background: #f0f0f0;
  border-radius: 4px;
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.issue-desc {
  flex: 1;
  min-width: 200px;
  font-size: 14px;
}

/* AI建议 */
.suggestions-section li {
  margin-bottom: 12px;
  padding: 8px;
  background: #f6ffed;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.btn-link {
  padding: 2px 8px;
  background: #52c41a;
  color: #fff;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  white-space: nowrap;
}

.btn-link:hover {
  background: #389e0d;
}

/* AI辅助决策 */
.ai-assistant-section {
  background: #f0f5ff;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #d6e4ff;
}

.ai-recommendation {
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.ai-recommendation.recommend-approve {
  background: #f6ffed;
  border: 1px solid #b7eb8f;
}

.ai-recommendation.recommend-revise {
  background: #fffbe6;
  border: 1px solid #ffe58f;
}

.ai-recommendation.recommend-reject {
  background: #fff2f0;
  border: 1px solid #ffccc7;
}

.recommendation-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 8px;
}

.recommend-approve .recommendation-title {
  color: #52c41a;
}

.recommend-revise .recommendation-title {
  color: #fa8c16;
}

.recommend-reject .recommendation-title {
  color: #f5222d;
}

.recommendation-reason {
  font-size: 14px;
  color: var(--text-secondary);
}

.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.quick-actions button {
  font-size: 13px;
  padding: 6px 12px;
}

.issue-severity {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.severity-low { background: #f6ffed; color: #52c41a; }
.severity-medium { background: #fff7e6; color: #fa8c16; }
.severity-high { background: #fff2f0; color: #f5222d; }
.severity-critical { background: #f5222d; color: #fff; }

.suggestions-section ul {
  padding-left: 20px;
}

.suggestions-section li {
  margin-bottom: 8px;
}

.review-form-card {
  position: sticky;
  top: 24px;
}

.form-section {
  margin-bottom: 20px;
}

.form-section h4 {
  margin-bottom: 12px;
  color: var(--text-secondary);
}

.score-inputs {
  display: grid;
  gap: 12px;
}

.score-input-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-input-item label {
  width: 80px;
}

.star-rating {
  display: flex;
  gap: 4px;
}

.star {
  cursor: pointer;
  font-size: 20px;
  color: #ddd;
  transition: color 0.2s;
}

.star.active {
  color: #faad14;
}

.decision-buttons {
  display: flex;
  gap: 12px;
}

.decision-btn {
  flex: 1;
  padding: 12px;
  border: 2px solid var(--border-color);
  background: var(--white);
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s;
}

.decision-btn:hover {
  border-color: var(--primary-color);
}

.decision-btn.active {
  border-color: var(--primary-color);
  background: var(--primary-color);
  color: var(--white);
}

.form-actions {
  margin-top: 24px;
}

.form-actions button {
  width: 100%;
  padding: 12px;
}

/* 教材信息网格 */
.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-grid .info-item.full-width {
  grid-column: 1 / -1;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  padding: 2px 8px;
  background: #e6f7ff;
  color: #1890ff;
  border-radius: 4px;
  font-size: 12px;
}

/* 教师信息 */
.teacher-info-section {
  display: grid;
  gap: 16px;
}

.teacher-card {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.teacher-card h4 {
  margin-bottom: 12px;
  color: var(--text-secondary);
  font-size: 14px;
}

/* 时间线 */
.timeline {
  position: relative;
  padding-left: 24px;
}

.timeline::before {
  content: '';
  position: absolute;
  left: 6px;
  top: 0;
  bottom: 0;
  width: 2px;
  background: var(--border-color);
}

.timeline-item {
  position: relative;
  padding-bottom: 20px;
}

.timeline-marker {
  position: absolute;
  left: -20px;
  top: 4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: var(--border-color);
  border: 2px solid var(--white);
}

.timeline-marker.active {
  background: var(--primary-color);
}

.timeline-marker.deadline {
  background: #f5222d;
}

.timeline-content {
  padding-left: 12px;
}

.timeline-time {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.timeline-title {
  font-weight: 600;
  margin-bottom: 4px;
}

.timeline-desc {
  font-size: 13px;
  color: var(--text-secondary);
  background: #f8f9fa;
  padding: 8px;
  border-radius: 4px;
  margin-top: 8px;
}

/* 修改历史 */
.history-count {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: normal;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 3px solid var(--primary-color);
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.history-action {
  padding: 2px 8px;
  background: var(--primary-color);
  color: white;
  border-radius: 4px;
  font-size: 12px;
}

.history-time {
  font-size: 12px;
  color: var(--text-secondary);
}

.history-actor {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.history-version {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 8px;
}

.history-summary {
  font-size: 13px;
  color: var(--text-primary);
  background: white;
  padding: 8px;
  border-radius: 4px;
}
</style>

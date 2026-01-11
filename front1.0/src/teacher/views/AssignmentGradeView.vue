<template>
  <div class="assignment-grade">
    <div class="back-header">
      <button class="btn-back" @click="$router.back()">
        ← 返回
      </button>
    </div>

    <div class="page-header">
      <h1>批改作业</h1>
      <div v-if="assignment" class="assignment-title">
        {{ assignment.title }}
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="assignment" class="grade-content">
      <!-- 作业信息卡片 -->
      <div class="info-card">
        <div class="info-item">
          <span class="info-label">总分：</span>
          <span class="info-value">{{ assignment.total_score }} 分</span>
        </div>
        <div class="info-item">
          <span class="info-label">截止时间：</span>
          <span class="info-value">{{ formatDate(assignment.due_date) }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">提交数：</span>
          <span class="info-value">{{ submissions.length }} / {{ totalStudents }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">已批改：</span>
          <span class="info-value">{{ gradedCount }} / {{ submissions.length }}</span>
        </div>
      </div>

      <!-- 提交列表 -->
      <div class="submissions-section">
        <div class="section-header">
          <h2>提交列表</h2>
          <div class="filter-tabs">
            <button
              class="tab-btn"
              :class="{ active: filterStatus === 'all' }"
              @click="filterStatus = 'all'"
            >
              全部 ({{ submissions.length }})
            </button>
            <button
              class="tab-btn"
              :class="{ active: filterStatus === 'pending' }"
              @click="filterStatus = 'pending'"
            >
              待批改 ({{ pendingCount }})
            </button>
            <button
              class="tab-btn"
              :class="{ active: filterStatus === 'graded' }"
              @click="filterStatus = 'graded'"
            >
              已批改 ({{ gradedCount }})
            </button>
          </div>
        </div>

        <div v-if="filteredSubmissions.length > 0" class="submissions-list">
          <div
            v-for="submission in filteredSubmissions"
            :key="submission.id"
            class="submission-card"
            :class="{ 'graded': submission.score !== null && submission.score !== undefined }"
          >
            <div class="submission-header">
              <div class="student-info">
                <div class="student-avatar">
                  {{ (submission.student?.username || 'S').charAt(0).toUpperCase() }}
                </div>
                <div>
                  <h4>{{ submission.student?.username || '未知' }}</h4>
                  <p class="submit-time">提交时间：{{ formatDate(submission.submitted_at) }}</p>
                </div>
              </div>
              <div class="submission-badges">
                <span v-if="submission.is_late" class="badge late">迟交</span>
                <span v-if="submission.score !== null && submission.score !== undefined" class="badge graded">已批改</span>
                <span v-else class="badge pending">待批改</span>
              </div>
            </div>

            <!-- 批改表单 -->
            <div class="grading-form" v-if="editingSubmissionId === submission.id">
              <div class="form-group">
                <label>得分 (0 - {{ assignment.total_score }})</label>
                <input
                  v-model.number="gradingForm.score"
                  type="number"
                  min="0"
                  :max="assignment.total_score"
                  class="form-input"
                  placeholder="请输入得分"
                />
              </div>
              <div class="form-group">
                <label>反馈意见</label>
                <textarea
                  v-model="gradingForm.feedback"
                  rows="4"
                  class="form-textarea"
                  placeholder="请输入反馈意见..."
                ></textarea>
              </div>
              <div class="form-actions">
                <button class="btn btn-secondary" @click="cancelGrading">取消</button>
                <button class="btn btn-primary" @click="submitGrading(submission.id)">保存</button>
              </div>
            </div>

            <!-- 已批改信息 -->
            <div v-else-if="submission.score !== null && submission.score !== undefined" class="graded-info">
              <div class="score-display" :class="getScoreClass(submission.score)">
                <span class="score-value">{{ submission.score }}</span>
                <span class="score-total">/ {{ assignment.total_score }}</span>
              </div>
              <div v-if="submission.feedback" class="feedback-content">
                <strong>反馈：</strong>
                <p>{{ submission.feedback }}</p>
              </div>
              <div class="graded-meta">
                <span>批改时间：{{ formatDate(submission.graded_at) }}</span>
                <span v-if="submission.graded_by">批改人：{{ submission.graded_by.username }}</span>
              </div>
              <button class="btn btn-small" @click="startGrading(submission)">重新批改</button>
            </div>

            <!-- 待批改操作 -->
            <div v-else class="pending-actions">
              <button class="btn btn-primary" @click="startGrading(submission)">开始批改</button>
            </div>
          </div>
        </div>

        <div v-else class="empty-state">
          <p>{{ filterStatus === 'pending' ? '暂无待批改的提交' : filterStatus === 'graded' ? '暂无已批改的提交' : '暂无提交记录' }}</p>
        </div>
      </div>
    </div>

    <div v-else class="error-container">
      <p>加载失败，请重试</p>
      <button class="btn btn-primary" @click="loadData">重新加载</button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { assignmentApi } from '../api/assignment'
import { formatDate } from '../../utils/dataFormatter'

export default {
  name: 'AssignmentGradeView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const loading = ref(true)
    const assignment = ref(null)
    const submissions = ref([])
    const filterStatus = ref('all')
    const editingSubmissionId = ref(null)
    const gradingForm = ref({
      score: null,
      feedback: ''
    })
    const totalStudents = ref(0)

    const loadData = async () => {
      loading.value = true
      try {
        const assignmentId = route.params.id
        
        // 加载作业详情
        const assignmentRes = await assignmentApi.getAssignmentDetail(assignmentId)
        assignment.value = assignmentRes.data?.data || assignmentRes.data || assignmentRes
        
        // 计算总学生数（从分配的班级）
        if (assignment.value.classes && assignment.value.classes.length > 0) {
          totalStudents.value = assignment.value.classes.reduce((sum, cls) => {
            return sum + (cls.student_count || 0)
          }, 0)
        }
        
        // 加载提交记录
        await loadSubmissions()
      } catch (error) {
        console.error('加载数据失败:', error)
        alert('加载失败: ' + (error.response?.data?.error || error.message))
      } finally {
        loading.value = false
      }
    }

    const loadSubmissions = async () => {
      try {
        const assignmentId = route.params.id
        const response = await assignmentApi.getSubmissions(assignmentId)
        
        // 处理不同的响应格式
        let submissionsData = response.data
        if (Array.isArray(submissionsData)) {
          submissions.value = submissionsData
        } else if (submissionsData && Array.isArray(submissionsData.data)) {
          submissions.value = submissionsData.data
        } else if (submissionsData && Array.isArray(submissionsData.results)) {
          submissions.value = submissionsData.results
        } else {
          submissions.value = []
        }
      } catch (error) {
        console.error('加载提交记录失败:', error)
        submissions.value = []
      }
    }

    const filteredSubmissions = computed(() => {
      if (filterStatus.value === 'all') {
        return submissions.value
      } else if (filterStatus.value === 'pending') {
        return submissions.value.filter(s => s.score === null || s.score === undefined)
      } else if (filterStatus.value === 'graded') {
        return submissions.value.filter(s => s.score !== null && s.score !== undefined)
      }
      return submissions.value
    })

    const pendingCount = computed(() => {
      return submissions.value.filter(s => s.score === null || s.score === undefined).length
    })

    const gradedCount = computed(() => {
      return submissions.value.filter(s => s.score !== null && s.score !== undefined).length
    })

    const startGrading = (submission) => {
      editingSubmissionId.value = submission.id
      gradingForm.value = {
        score: submission.score || null,
        feedback: submission.feedback || ''
      }
    }

    const cancelGrading = () => {
      editingSubmissionId.value = null
      gradingForm.value = {
        score: null,
        feedback: ''
      }
    }

    const submitGrading = async (submissionId) => {
      if (gradingForm.value.score === null || gradingForm.value.score === undefined) {
        alert('请输入得分')
        return
      }

      if (gradingForm.value.score < 0 || gradingForm.value.score > assignment.value.total_score) {
        alert(`得分必须在 0 到 ${assignment.value.total_score} 之间`)
        return
      }

      try {
        const assignmentId = route.params.id
        await assignmentApi.gradeAssignment(assignmentId, {
          submission_id: submissionId,
          score: gradingForm.value.score,
          feedback: gradingForm.value.feedback || ''
        })
        
        alert('批改成功！')
        cancelGrading()
        // 重新加载提交记录
        await loadSubmissions()
      } catch (error) {
        console.error('批改失败:', error)
        alert('批改失败: ' + (error.response?.data?.error || error.message))
      }
    }

    const getScoreClass = (score) => {
      const percentage = (score / (assignment.value?.total_score || 100)) * 100
      if (percentage >= 90) return 'excellent'
      if (percentage >= 80) return 'good'
      if (percentage >= 60) return 'average'
      return 'poor'
    }

    onMounted(() => {
      loadData()
    })

    return {
      loading,
      assignment,
      submissions,
      filterStatus,
      filteredSubmissions,
      pendingCount,
      gradedCount,
      totalStudents,
      editingSubmissionId,
      gradingForm,
      loadData,
      startGrading,
      cancelGrading,
      submitGrading,
      getScoreClass,
      formatDate
    }
  }
}
</script>

<style scoped>
.assignment-grade {
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
  background: #f8fafc;
  min-height: 100vh;
}

.back-header {
  margin-bottom: 24px;
}

.btn-back {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  font-size: 14px;
  padding: 8px 0;
  transition: color 0.2s;
}

.btn-back:hover {
  color: #3b82f6;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.assignment-title {
  font-size: 16px;
  color: #64748b;
}

.loading-container {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.info-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.info-label {
  font-size: 14px;
  color: #64748b;
}

.info-value {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.submissions-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  flex-wrap: wrap;
  gap: 16px;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
  color: #1e293b;
}

.filter-tabs {
  display: flex;
  gap: 8px;
}

.tab-btn {
  padding: 8px 16px;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}

.tab-btn.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.submissions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.submission-card {
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  transition: all 0.2s;
}

.submission-card.graded {
  background: #f0fdf4;
  border-color: #86efac;
}

.submission-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
}

.student-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.student-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
}

.student-info h4 {
  margin: 0 0 4px 0;
  font-size: 18px;
  color: #1e293b;
}

.submit-time {
  margin: 0;
  font-size: 14px;
  color: #64748b;
}

.submission-badges {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.badge.late {
  background: #fee2e2;
  color: #dc2626;
}

.badge.graded {
  background: #dcfce7;
  color: #16a34a;
}

.badge.pending {
  background: #fef3c7;
  color: #d97706;
}

.grading-form {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 2px solid #e2e8f0;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 16px;
}

.graded-info {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 2px solid #e2e8f0;
}

.score-display {
  display: inline-flex;
  align-items: baseline;
  gap: 4px;
  padding: 12px 20px;
  border-radius: 8px;
  font-weight: 600;
  margin-bottom: 12px;
}

.score-value {
  font-size: 24px;
}

.score-total {
  font-size: 16px;
  opacity: 0.7;
}

.score-display.excellent {
  background: #dcfce7;
  color: #16a34a;
}

.score-display.good {
  background: #dbeafe;
  color: #2563eb;
}

.score-display.average {
  background: #fef3c7;
  color: #d97706;
}

.score-display.poor {
  background: #fee2e2;
  color: #dc2626;
}

.feedback-content {
  margin: 16px 0;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
}

.feedback-content strong {
  display: block;
  margin-bottom: 8px;
  color: #374151;
}

.feedback-content p {
  margin: 0;
  color: #475569;
  line-height: 1.6;
}

.graded-meta {
  display: flex;
  gap: 16px;
  font-size: 14px;
  color: #64748b;
  margin-bottom: 12px;
}

.pending-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 2px solid #e2e8f0;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #64748b;
}

.error-container {
  text-align: center;
  padding: 60px 20px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.btn-small {
  padding: 8px 16px;
  font-size: 14px;
}
</style>

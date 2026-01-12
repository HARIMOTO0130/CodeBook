<template>
  <div class="assignment-detail">
    <div class="back-header">
      <button class="btn-back" @click="$router.back()">
        ← 返回
      </button>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="assignment" class="detail-content">
      <!-- 作业基本信息 -->
      <div class="assignment-header-card">
        <div class="header-content">
          <div class="assignment-icon">📝</div>
          <div class="assignment-info">
            <h1>{{ assignment.title }}</h1>
            <p class="assignment-meta">
              <span>创建时间：{{ formatDate(assignment.created_at) }}</span>
              <span>截止时间：{{ formatDate(assignment.due_date) }}</span>
              <span>总分：{{ assignment.total_score }} 分</span>
            </p>
            <div class="status-badge" :class="getStatusClass()">
              {{ getStatusText() }}
            </div>
          </div>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary" @click="goToGrade">
            📊 批改作业
          </button>
          <button class="btn btn-secondary" @click="editAssignment">
            ✏️ 编辑
          </button>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon blue">👥</div>
          <div class="stat-info">
            <div class="stat-value">{{ assignment.classes?.length || 0 }}</div>
            <div class="stat-label">分配班级</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green">📤</div>
          <div class="stat-info">
            <div class="stat-value">{{ assignment.submission_count || 0 }}</div>
            <div class="stat-label">提交数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon purple">✓</div>
          <div class="stat-info">
            <div class="stat-value">{{ assignment.graded_count || 0 }}</div>
            <div class="stat-label">已批改</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orange">⏱️</div>
          <div class="stat-info">
            <div class="stat-value">{{ getRemainingTime() }}</div>
            <div class="stat-label">剩余时间</div>
          </div>
        </div>
      </div>

      <!-- 作业说明 -->
      <div class="section-card">
        <div class="section-header">
          <h2>作业说明</h2>
        </div>
        <div class="section-content">
          <p v-if="assignment.description">{{ assignment.description }}</p>
          <p v-else class="empty-text">暂无说明</p>
        </div>
      </div>

      <!-- 分配班级 -->
      <div class="section-card">
        <div class="section-header">
          <h2>分配班级</h2>
        </div>
        <div v-if="assignment.classes && assignment.classes.length > 0" class="classes-list">
          <div
            v-for="classItem in assignment.classes"
            :key="classItem.id"
            class="class-item"
            @click="goToClassDetail(classItem.id)"
          >
            <div class="class-avatar">{{ (classItem.name || '班').charAt(0) }}</div>
            <div class="class-details">
              <h4>{{ classItem.name }}</h4>
              <p>{{ classItem.student_count || 0 }} 名学生</p>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>未分配班级</p>
        </div>
      </div>

      <!-- 提交记录 -->
      <div class="section-card">
        <div class="section-header">
          <h2>提交记录</h2>
          <button class="btn btn-small" @click="loadSubmissions">
            🔄 刷新
          </button>
        </div>
        <div v-if="submissions.length > 0" class="submissions-list">
          <div
            v-for="submission in submissions"
            :key="submission.id"
            class="submission-item"
            @click="goToGradeSubmission(submission.id)"
          >
            <div class="submission-student">
              <div class="student-avatar">
                {{ (submission.student?.username || 'S').charAt(0).toUpperCase() }}
              </div>
              <div class="student-info">
                <h4>{{ submission.student?.username || '未知' }}</h4>
                <p>提交时间：{{ formatDate(submission.submitted_at) }}</p>
              </div>
            </div>
            <div class="submission-status">
              <div v-if="submission.score !== null && submission.score !== undefined" class="score-display" :class="getScoreClass(submission.score)">
                {{ submission.score }} / {{ assignment.total_score }}
              </div>
              <div v-else class="status-pending">待批改</div>
              <div v-if="submission.is_late" class="late-badge">迟交</div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>暂无提交记录</p>
        </div>
      </div>
    </div>

    <div v-else class="error-container">
      <p>加载失败，请重试</p>
      <button class="btn btn-primary" @click="loadAssignment">重新加载</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { assignmentApi } from '../api/assignment'
import { formatDate } from '../utils/dataFormatter'

export default {
  name: 'AssignmentDetailView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const loading = ref(true)
    const assignment = ref(null)
    const submissions = ref([])

    const loadAssignment = async () => {
      loading.value = true
      try {
        const assignmentId = route.params.id
        const response = await assignmentApi.getAssignmentDetail(assignmentId)
        
        // 处理不同的响应格式
        let assignmentData = response.data?.data || response.data || response
        
        // 格式化作业数据，确保显示正常
        assignment.value = {
          ...assignmentData,
          title: assignmentData.homework_name || `作业${assignmentData.id}`,
          description: assignmentData.homework_content || '暂无说明',
          due_date: assignmentData.end_time || null,
          total_score: assignmentData.total_score || 100,
          // 处理班级数据
          classes: assignmentData.class_obj && assignmentData.class_obj.id ? [{
            id: assignmentData.class_obj.id,
            name: assignmentData.class_obj.name || '未知班级',
            student_count: assignmentData.class_obj.student_count || 0
          }] : []
        }
        
        console.log('作业详情数据:', assignment.value)
        
        // 加载提交记录
        await loadSubmissions()
      } catch (error) {
        console.error('加载作业详情失败:', error)
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

    const getStatusClass = () => {
      if (!assignment.value) return 'normal'
      const now = new Date()
      const dueDate = new Date(assignment.value.due_date)
      if (dueDate < now) return 'overdue'
      const daysLeft = (dueDate - now) / (1000 * 60 * 60 * 24)
      if (daysLeft <= 1) return 'urgent'
      return 'normal'
    }

    const getStatusText = () => {
      if (!assignment.value) return '未知'
      const now = new Date()
      const dueDate = new Date(assignment.value.due_date)
      if (dueDate < now) return '已截止'
      const daysLeft = Math.ceil((dueDate - now) / (1000 * 60 * 60 * 24))
      if (daysLeft <= 1) return '即将截止'
      return '进行中'
    }

    const getRemainingTime = () => {
      if (!assignment.value) return '-' 
      if (!assignment.value.due_date) return '未设置'
      
      try {
        const now = new Date()
        const dueDate = new Date(assignment.value.due_date)
        
        if (isNaN(dueDate.getTime())) return '未设置'
        
        if (dueDate < now) return '已截止'
        
        const diff = dueDate - now
        const days = Math.floor(diff / (1000 * 60 * 60 * 24))
        const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
        
        if (days > 0) return `${days}天${hours}小时`
        if (hours > 0) return `${hours}小时`
        const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60))
        return `${minutes}分钟`
      } catch (error) {
        return '未设置'
      }
    }

    const getScoreClass = (score) => {
      const percentage = (score / (assignment.value?.total_score || 100)) * 100
      if (percentage >= 90) return 'excellent'
      if (percentage >= 80) return 'good'
      if (percentage >= 60) return 'average'
      return 'poor'
    }

    const goToGrade = () => {
      router.push(`/teacher/assignments/${route.params.id}/grade`)
    }

    const goToGradeSubmission = (submissionId) => {
      router.push(`/teacher/assignments/${route.params.id}/grade?submission=${submissionId}`)
    }

    const editAssignment = () => {
      alert('编辑功能开发中...')
    }

    const goToClassDetail = (classId) => {
      router.push(`/teacher/classes/${classId}`)
    }

    onMounted(() => {
      loadAssignment()
    })

    return {
      loading,
      assignment,
      submissions,
      loadAssignment,
      loadSubmissions,
      getStatusClass,
      getStatusText,
      getRemainingTime,
      getScoreClass,
      goToGrade,
      goToGradeSubmission,
      editAssignment,
      goToClassDetail,
      formatDate
    }
  }
}
</script>

<style scoped>
.assignment-detail {
  padding: 24px;
  max-width: 1400px;
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

.assignment-header-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-content {
  display: flex;
  gap: 24px;
  flex: 1;
}

.assignment-icon {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
}

.assignment-info h1 {
  margin: 0 0 12px 0;
  font-size: 28px;
  color: #1e293b;
}

.assignment-meta {
  display: flex;
  gap: 24px;
  color: #64748b;
  font-size: 14px;
  margin-bottom: 12px;
}

.status-badge {
  display: inline-block;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
}

.status-badge.normal {
  background: #dcfce7;
  color: #16a34a;
}

.status-badge.urgent {
  background: #fef3c7;
  color: #d97706;
}

.status-badge.overdue {
  background: #fee2e2;
  color: #dc2626;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.blue { background: #dbeafe; }
.stat-icon.green { background: #d1fae5; }
.stat-icon.purple { background: #e9d5ff; }
.stat-icon.orange { background: #fed7aa; }

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #1e293b;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
}

.section-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
  color: #1e293b;
}

.section-content {
  color: #475569;
  line-height: 1.6;
}

.empty-text {
  color: #94a3b8;
  font-style: italic;
}

.classes-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.class-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.class-item:hover {
  border-color: #3b82f6;
  background: #f0f9ff;
}

.class-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: bold;
}

.class-details h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: #1e293b;
}

.class-details p {
  margin: 0;
  font-size: 14px;
  color: #64748b;
}

.submissions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.submission-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.submission-item:hover {
  border-color: #3b82f6;
  background: #f0f9ff;
}

.submission-student {
  display: flex;
  align-items: center;
  gap: 12px;
}

.student-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
}

.student-info h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: #1e293b;
}

.student-info p {
  margin: 0;
  font-size: 14px;
  color: #64748b;
}

.submission-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.score-display {
  padding: 8px 16px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
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

.status-pending {
  padding: 8px 16px;
  background: #f3f4f6;
  color: #64748b;
  border-radius: 8px;
  font-weight: 600;
}

.late-badge {
  padding: 4px 12px;
  background: #fee2e2;
  color: #dc2626;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.empty-state {
  text-align: center;
  padding: 40px;
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

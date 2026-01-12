<template>
  <div class="student-detail">
    <!-- 返回按钮 -->
    <div class="back-header">
      <button class="btn-back" @click="$router.back()">
        ← 返回学生列表
      </button>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 学生详情内容 -->
    <div v-else-if="studentInfo" class="detail-content">
      <!-- 学生基本信息 -->
      <div class="student-header-card">
        <div class="header-content">
          <div class="student-avatar-large">
            {{ (studentInfo.username || 'S').charAt(0).toUpperCase() }}
          </div>
          <div class="student-info">
            <h1>{{ studentInfo.username || '未知' }}</h1>
            <p class="student-meta">
              <span>学号：{{ studentProfile?.student_id || '未设置' }}</span>
              <span>邮箱：{{ studentInfo.email || '未设置' }}</span>
              <span>加入时间：{{ formatDate(studentInfo.date_joined) }}</span>
            </p>
            <div class="student-classes">
              <span v-for="className in studentProfile?.class_name || []" :key="className" class="class-tag">
                {{ className }}
              </span>
              <span v-if="!studentProfile?.class_name || studentProfile.class_name.length === 0" class="no-class">
                未分配班级
              </span>
            </div>
          </div>
        </div>
        <div class="header-actions">
          <button class="btn btn-primary" @click="sendMessage">发送消息</button>
          <button class="btn btn-secondary" @click="viewReports">查看报告</button>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon blue">📚</div>
          <div class="stat-info">
            <div class="stat-value">{{ learningProgress?.total_chapters || 0 }}</div>
            <div class="stat-label">学习章节</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green">📝</div>
          <div class="stat-info">
            <div class="stat-value">{{ practiceRecords?.total_practices || 0 }}</div>
            <div class="stat-label">练习次数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon purple">⭐</div>
          <div class="stat-info">
            <div class="stat-value">{{ practiceRecords?.avg_score || 0 }}</div>
            <div class="stat-label">平均分数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orange">📊</div>
          <div class="stat-info">
            <div class="stat-value">{{ learningProgress?.avg_progress || 0 }}%</div>
            <div class="stat-label">学习进度</div>
          </div>
        </div>
      </div>

      <!-- 学习进度 -->
      <div class="section-card">
        <div class="section-header">
          <h2>学习进度</h2>
        </div>
        <div v-if="learningProgress" class="progress-content">
          <div class="progress-item">
            <div class="progress-label">总体进度</div>
            <div class="progress-bar-container">
              <div class="progress-bar" :style="{ width: (learningProgress.avg_progress || 0) + '%' }"></div>
            </div>
            <div class="progress-value">{{ learningProgress.avg_progress || 0 }}%</div>
          </div>
          <div class="progress-details">
            <div class="detail-item">
              <span class="detail-label">已完成章节：</span>
              <span class="detail-value">{{ learningProgress.completed_chapters || 0 }} / {{ learningProgress.total_chapters || 0 }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">学习时长：</span>
              <span class="detail-value">{{ learningProgress.total_learning_time || '0' }} 分钟</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">最后学习时间：</span>
              <span class="detail-value">{{ learningProgress.last_learning_time ? formatDate(learningProgress.last_learning_time) : '暂无' }}</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>暂无学习进度数据</p>
        </div>
      </div>

      <!-- 练习记录 -->
      <div class="section-card">
        <div class="section-header">
          <h2>练习记录</h2>
        </div>
        <div v-if="practiceRecords?.records && practiceRecords.records.length > 0" class="practice-list">
          <div 
            v-for="record in practiceRecords.records.slice(0, 10)" 
            :key="record.id"
            class="practice-item"
          >
            <div class="practice-info">
              <h4>{{ record.chapter_title || '未知章节' }}</h4>
              <p>{{ record.book_title || '未知书籍' }}</p>
              <div class="practice-meta">
                <span>完成时间：{{ formatDate(record.created_at) }}</span>
                <span>用时：{{ record.time_spent || 0 }} 分钟</span>
              </div>
            </div>
            <div class="practice-score" :class="getScoreClass(record.score)">
              {{ record.score || 0 }} 分
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>暂无练习记录</p>
        </div>
      </div>

      <!-- 作业提交记录 -->
      <div class="section-card">
        <div class="section-header">
          <h2>作业提交记录</h2>
        </div>
        <div v-if="submissions.length > 0" class="submissions-list">
          <div 
            v-for="submission in submissions" 
            :key="submission.id"
            class="submission-item"
          >
            <div class="submission-info">
              <h4>{{ submission.assignment?.title || '未知作业' }}</h4>
              <p>提交时间：{{ formatDate(submission.submitted_at) }}</p>
              <div class="submission-meta">
                <span>状态：{{ getSubmissionStatus(submission) }}</span>
                <span v-if="submission.graded_at">批改时间：{{ formatDate(submission.graded_at) }}</span>
              </div>
            </div>
            <div class="submission-score">
              <div v-if="submission.score !== null && submission.score !== undefined" class="score-display" :class="getScoreClass(submission.score)">
                {{ submission.score }} 分
              </div>
              <div v-else class="score-pending">待批改</div>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>暂无作业提交记录</p>
        </div>
      </div>
    </div>

    <!-- 错误提示 -->
    <div v-else class="error-container">
      <p>加载失败，请重试</p>
      <button class="btn btn-primary" @click="loadStudentDetail">重新加载</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { studentApi } from '../api/student'
import { assignmentApi } from '../api/assignment'
import { formatDate } from '../utils/dataFormatter'

export default {
  name: 'StudentDetailView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const loading = ref(true)
    const studentInfo = ref(null)
    const studentProfile = ref(null)
    const learningProgress = ref(null)
    const practiceRecords = ref(null)
    const submissions = ref([])

    const loadStudentDetail = async () => {
      loading.value = true
      try {
        const studentId = route.params.id
        
        // 加载学生基本信息
        const studentRes = await studentApi.getStudentDetail(studentId)
        // 处理不同的响应格式
        studentInfo.value = studentRes.data?.data || studentRes.data || studentRes
        
        console.log('学生详情数据:', studentInfo.value)
        
        // 加载学生档案
        try {
          const profileRes = await studentApi.getStudentProfile(studentId)
          studentProfile.value = profileRes.data?.data || profileRes.data || profileRes
          console.log('学生档案数据:', studentProfile.value)
        } catch (e) {
          console.log('加载学生档案失败:', e)
          studentProfile.value = null
        }
        
        // 加载学习进度
        try {
          const progressRes = await studentApi.getStudentLearningProgress(studentId)
          learningProgress.value = progressRes.data?.data || progressRes.data || progressRes
          console.log('学习进度数据:', learningProgress.value)
        } catch (e) {
          console.log('加载学习进度失败:', e)
          learningProgress.value = null
        }
        
        // 加载练习记录
        try {
          const practiceRes = await studentApi.getStudentPracticeRecords(studentId)
          practiceRecords.value = practiceRes.data?.data || practiceRes.data || practiceRes
          console.log('练习记录数据:', practiceRecords.value)
        } catch (e) {
          console.log('加载练习记录失败:', e)
          practiceRecords.value = null
        }
        
        // 加载作业提交记录（需要从作业API获取）
        try {
          const assignmentsRes = await assignmentApi.getAssignments()
          // 这里需要后端支持通过学生ID查询提交记录
          // 暂时先留空，等待后端API支持
          submissions.value = []
        } catch (e) {
          console.log('加载作业提交记录失败:', e)
          submissions.value = []
        }
      } catch (error) {
        console.error('加载学生详情失败:', error)
        alert('加载失败: ' + (error.response?.data?.error || error.message))
      } finally {
        loading.value = false
      }
    }

    const sendMessage = () => {
      alert('发送消息功能开发中...')
    }

    const viewReports = () => {
      router.push(`/teacher/analytics?student=${route.params.id}`)
    }

    const getScoreClass = (score) => {
      if (score >= 90) return 'excellent'
      if (score >= 80) return 'good'
      if (score >= 60) return 'average'
      return 'poor'
    }

    const getSubmissionStatus = (submission) => {
      if (submission.graded_at) return '已批改'
      return '待批改'
    }

    onMounted(() => {
      loadStudentDetail()
    })

    return {
      loading,
      studentInfo,
      studentProfile,
      learningProgress,
      practiceRecords,
      submissions,
      loadStudentDetail,
      sendMessage,
      viewReports,
      getScoreClass,
      getSubmissionStatus,
      formatDate
    }
  }
}
</script>

<style scoped>
.student-detail {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
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

.student-header-card {
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

.student-avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: bold;
}

.student-info h1 {
  margin: 0 0 12px 0;
  font-size: 28px;
  color: #1e293b;
}

.student-meta {
  display: flex;
  gap: 24px;
  color: #64748b;
  font-size: 14px;
  margin-bottom: 12px;
}

.student-classes {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.class-tag {
  background: #dbeafe;
  color: #1e40af;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
}

.no-class {
  color: #94a3b8;
  font-size: 14px;
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

.section-header h2 {
  margin: 0 0 20px 0;
  font-size: 20px;
  color: #1e293b;
}

.progress-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.progress-label {
  min-width: 100px;
  font-size: 14px;
  color: #64748b;
}

.progress-bar-container {
  flex: 1;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6);
  transition: width 0.3s;
}

.progress-value {
  min-width: 60px;
  text-align: right;
  font-weight: bold;
  color: #1e293b;
}

.progress-details {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-top: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: #94a3b8;
}

.detail-value {
  font-size: 16px;
  font-weight: 500;
  color: #1e293b;
}

.practice-list, .submissions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.practice-item, .submission-item {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.practice-info h4, .submission-info h4 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #1e293b;
}

.practice-info p, .submission-info p {
  margin: 0 0 12px 0;
  color: #64748b;
}

.practice-meta, .submission-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #94a3b8;
}

.practice-score, .score-display {
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 18px;
  font-weight: bold;
}

.practice-score.excellent, .score-display.excellent {
  background: #d1fae5;
  color: #065f46;
}

.practice-score.good, .score-display.good {
  background: #dbeafe;
  color: #1e40af;
}

.practice-score.average, .score-display.average {
  background: #fed7aa;
  color: #92400e;
}

.practice-score.poor, .score-display.poor {
  background: #fee2e2;
  color: #991b1b;
}

.score-pending {
  padding: 8px 16px;
  border-radius: 8px;
  background: #f3f4f6;
  color: #64748b;
  font-size: 14px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #94a3b8;
}

.error-container {
  text-align: center;
  padding: 60px 20px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #e2e8f0;
  color: #475569;
}

.btn-secondary:hover {
  background: #cbd5e1;
}
</style>

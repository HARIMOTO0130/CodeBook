<template>
  <div class="assignment-list">
    <div class="page-header">
    <h1>作业管理</h1>
      <button class="btn btn-primary" @click="createAssignment">
        <span>➕</span> 创建作业
      </button>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    
    <div v-else class="assignments-grid">
      <div
        v-for="assignment in assignments"
        :key="assignment.id"
        class="assignment-card"
      >
        <div class="assignment-header">
          <h3 @click="viewAssignment(assignment.id)">{{ assignment.title }}</h3>
          <div class="assignment-actions">
            <span class="status-badge" :class="getStatusClass(assignment)">
              {{ getStatusText(assignment) }}
            </span>
            <button
              class="delete-btn"
              @click.stop="deleteAssignment(assignment)"
              title="删除作业"
            >
              🗑️
            </button>
          </div>
        </div>
        <p class="assignment-description" @click="viewAssignment(assignment.id)">{{ assignment.description || '无描述' }}</p>
        <div class="assignment-meta" @click="viewAssignment(assignment.id)">
          <span>📅 截止时间: {{ formatDate(assignment.due_date) }}</span>
          <span>📝 提交数: {{ assignment.submission_count || 0 }}</span>
        </div>
      </div>
    </div>
    
    <div v-if="!loading && assignments.length === 0" class="empty-state">
      <p>暂无作业，点击"创建作业"开始</p>
    </div>
  </div>
</template>

<script>
import { assignmentApi } from '../api/assignment'
import { useRouter } from 'vue-router'

export default {
  name: 'AssignmentListView',
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    return {
      loading: false,
      assignments: []
    }
  },
  mounted() {
    this.loadAssignments()
  },
  methods: {
    async loadAssignments() {
      this.loading = true
      try {
        const response = await assignmentApi.getAssignments()
        // 处理不同的响应格式
        let assignmentsData = response.data
        let assignments = []
        
        if (Array.isArray(assignmentsData)) {
          assignments = assignmentsData
        } else if (assignmentsData && Array.isArray(assignmentsData.data)) {
          assignments = assignmentsData.data
        } else if (assignmentsData && Array.isArray(assignmentsData.results)) {
          assignments = assignmentsData.results
        } 
        
        // 格式化作业数据，确保显示正常
        this.assignments = assignments.map(assignment => ({
          ...assignment,
          title: assignment.homework_name || `作业${assignment.id}`,
          description: assignment.homework_content || '无描述',
          due_date: assignment.end_time || null,
          submission_count: assignment.submission_count || 0
        }))
        
        console.log('加载的作业数据:', this.assignments)
      } catch (error) {
        console.error('加载作业失败:', error)
        this.assignments = []
        // 不显示错误提示，避免干扰用户体验
      } finally {
        this.loading = false
      }
    },
    createAssignment() {
      this.router.push('/teacher/assignments/create')
    },
    viewAssignment(id) {
      this.router.push(`/teacher/assignments/${id}`)
    },
    async deleteAssignment(assignment) {
      if (confirm(`确定要删除作业"${assignment.title}"吗？此操作不可恢复。`)) {
        try {
          await assignmentApi.deleteAssignment(assignment.id)
          // 从本地状态中移除已删除的作业
          this.assignments = this.assignments.filter(a => a.id !== assignment.id)
          alert('作业删除成功！')
        } catch (error) {
          console.error('删除作业失败:', error)
          alert('删除作业失败: ' + (error.response?.data?.error || error.message))
        }
      }
    },
    getStatusClass(assignment) {
      const now = new Date()
      const dueDate = new Date(assignment.due_date)
      if (dueDate < now) return 'overdue'
      if (dueDate - now < 24 * 60 * 60 * 1000) return 'urgent'
      return 'normal'
    },
    getStatusText(assignment) {
      const now = new Date()
      const dueDate = new Date(assignment.due_date)
      if (dueDate < now) return '已截止'
      if (dueDate - now < 24 * 60 * 60 * 1000) return '即将截止'
      return '进行中'
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN')
    }
  }
}
</script>

<style scoped>
.assignment-list {
  padding: 24px;
  background: #f8fafc;
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #64748b;
}

.assignments-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.assignment-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.assignment-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.assignment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.assignment-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.delete-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.delete-btn:hover {
  background-color: rgba(220, 38, 38, 0.1);
  color: #dc2626;
}

.assignment-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
  flex: 1;
}

.status-badge {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
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

.assignment-description {
  color: #64748b;
  font-size: 14px;
  margin: 12px 0;
  line-height: 1.5;
}

.assignment-meta {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 12px;
  color: #94a3b8;
  margin-top: 16px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #64748b;
}
</style>

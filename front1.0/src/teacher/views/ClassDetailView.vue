<template>
  <div class="class-detail">
    <!-- 返回按钮 -->
    <div class="back-header">
      <button class="btn-back" @click="$router.back()">
        ← 返回班级列表
      </button>
    </div>

    <!-- 加载中 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 班级详情内容 -->
    <div v-else-if="classInfo" class="detail-content">
      <!-- 班级基本信息 -->
      <div class="class-header-card">
        <div class="header-content">
          <div class="class-avatar-large">
            {{ (classInfo.name || '班').charAt(0) }}
          </div>
          <div class="class-info">
            <h1>{{ classInfo.name }}</h1>
            <p class="class-meta">
              <span>专业：{{ classInfo.major || '未设置' }}</span>
              <span>年级：{{ classInfo.grade || '未设置' }}</span>
              <span>教材：{{ classInfo.book?.title || classInfo.textbooks?.[0]?.title || '未设置' }}</span>
              <span>创建时间：{{ formatDate(classInfo.created_at) }}</span>
            </p>
            <p class="class-description">{{ classInfo.description || '暂无描述' }}</p>
          </div>
          
          <!-- 头部操作按钮 -->
          <div class="header-actions">
            <button class="btn btn-small btn-primary" @click="editClass">编辑班级</button>
            <button class="btn btn-small btn-secondary" @click="addStudent">添加学生</button>
          </div>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon blue">👥</div>
          <div class="stat-info">
            <div class="stat-value">{{ classInfo.students?.length || classInfo.student_count || 0 }}</div>
            <div class="stat-label">学生总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green">📝</div>
          <div class="stat-info">
            <div class="stat-value">{{ assignments.length }}</div>
            <div class="stat-label">作业总数</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon purple">📚</div>
          <div class="stat-info">
            <div class="stat-value">{{ resources.length }}</div>
            <div class="stat-label">教学资源</div>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orange">📊</div>
          <div class="stat-info">
            <div class="stat-value">{{ analytics.avg_progress || 0 }}%</div>
            <div class="stat-label">平均进度</div>
          </div>
        </div>
      </div>

      <!-- 学生列表 -->
      <div class="section-card">
        <div class="section-header">
          <h2>学生列表</h2>
          <button class="btn btn-small" @click="addStudent">+ 添加学生</button>
        </div>
        <div v-if="classInfo.students && classInfo.students.length > 0" class="students-grid">
          <div 
            v-for="student in classInfo.students" 
            :key="student.id"
            class="student-card"
            @click="goToStudentDetail(student.id)"
          >
            <div class="student-avatar">
              {{ (student.student_name || student.username || 'S').charAt(0).toUpperCase() }}
            </div>
            <div class="student-info">
              <h4>{{ student.student_name || student.username || '未知' }}</h4>
              <p>{{ student.student_no || '学号未设置' }}</p>
            </div>
            <div class="student-actions">
              <button class="btn-icon" @click.stop="viewStudentProgress(student.id)">📊</button>
              <button class="btn-icon btn-danger" @click.stop="confirmRemoveStudent(student.id, student.student_name || student.username || '未知')">×</button>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>暂无学生，点击"添加学生"按钮添加学生到班级</p>
        </div>
      </div>

      <!-- 作业列表 -->
      <div class="section-card">
        <div class="section-header">
          <h2>作业列表</h2>
          <button class="btn btn-small" @click="createAssignment">+ 创建作业</button>
        </div>
        <div v-if="assignments.length > 0" class="assignments-list">
          <div 
            v-for="assignment in assignments" 
            :key="assignment.id"
            class="assignment-item"
            @click="goToAssignmentDetail(assignment.id)"
          >
            <div class="assignment-info">
              <h4>{{ assignment.title }}</h4>
              <p>{{ assignment.description || '暂无描述' }}</p>
              <div class="assignment-meta">
                <span>截止时间：{{ formatDate(assignment.due_date) }}</span>
                <span>提交数：{{ assignment.submission_count || 0 }}</span>
                <span>已批改：{{ assignment.graded_count || 0 }}</span>
              </div>
            </div>
            <div class="assignment-status" :class="getAssignmentStatus(assignment)">
              {{ getAssignmentStatusText(assignment) }}
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>暂无作业，点击"创建作业"按钮创建新作业</p>
        </div>
      </div>

      <!-- 教学资源 -->
      <div class="section-card">
        <div class="section-header">
          <h2>教学资源</h2>
          <button class="btn btn-small" @click="showUploadModal = true">+ 上传资源</button>
        </div>
        <div v-if="resources.length > 0" class="resources-grid">
          <div 
            v-for="resource in resources" 
            :key="resource.id"
            class="resource-item"
          >
            <div class="resource-icon">{{ getResourceIcon(resource.resource_type) }}</div>
            <div class="resource-info">
              <h4>{{ resource.title }}</h4>
              <p>{{ resource.description || '暂无描述' }}</p>
              <span class="resource-meta">{{ formatDate(resource.created_at) }}</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-state">
          <p>暂无教学资源</p>
        </div>
      </div>

      <!-- 资源上传模态框 -->
      <div v-if="showUploadModal" class="modal-overlay" @click.self="showUploadModal = false">
        <div class="modal upload-modal">
          <div class="modal-header">
            <h2>上传教学资源</h2>
            <button class="close-btn" @click="showUploadModal = false">×</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label>资源标题</label>
              <input type="text" v-model="uploadResource.title" placeholder="输入资源标题" />
            </div>
            <div class="form-group">
              <label>资源类型</label>
              <select v-model="uploadResource.type">
                <option value="document">文档</option>
                <option value="ppt">PPT</option>
                <option value="video">视频</option>
                <option value="image">图片</option>
                <option value="other">其他</option>
              </select>
            </div>
            <div class="form-group">
              <label>资源描述</label>
              <textarea v-model="uploadResource.description" rows="4" placeholder="输入资源描述"></textarea>
            </div>
            <div class="form-group">
              <label>选择文件</label>
              <div class="file-input-wrapper">
                <input type="file" @change="handleFileSelect" ref="fileInput" />
                <button class="btn btn-secondary" @click="$refs.fileInput.click()">选择文件</button>
                <span v-if="selectedFile" class="file-name">{{ selectedFile.name }}</span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showUploadModal = false">取消</button>
            <button class="btn btn-primary" @click="uploadResourceAction" :disabled="!selectedFile">上传资源</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 添加学生模态框 -->
    <div v-if="showAddStudentModal" class="modal-overlay" @click.self="showAddStudentModal = false">
      <div class="modal add-student-modal">
        <div class="modal-header">
          <h2>添加学生</h2>
          <button class="close-btn" @click="showAddStudentModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>搜索学生</label>
            <div class="search-box">
              <input 
                type="text" 
                v-model="searchQuery" 
                @input="searchStudents" 
                placeholder="输入学生姓名或学号" 
                :disabled="loadingStudents"
              />
              <button class="btn btn-small" @click="searchStudents" :disabled="loadingStudents">
                <span v-if="loadingStudents">搜索中...</span>
                <span v-else>搜索</span>
              </button>
            </div>
          </div>
          
          <div class="search-results" v-if="searchResults.length > 0">
            <div 
              v-for="student in searchResults" 
              :key="student.id"
              class="student-item"
              :class="{ 'selected': selectedStudents.includes(student.id) }"
              @click="toggleStudentSelection(student.id)"
            >
              <div class="student-info">
                <h4>{{ student.student_name || student.username }}</h4>
                <p>{{ student.student_no || '学号未设置' }}</p>
              </div>
              <div class="student-status" v-if="isStudentInClass(student.id)">
                <span class="tag tag-success">已在班</span>
              </div>
            </div>
          </div>
          <div v-else-if="loadingStudents" class="loading-state">
            <p>搜索中...</p>
          </div>
          <div v-else-if="searchQuery" class="empty-state">
            <p>未找到匹配的学生</p>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showAddStudentModal = false">取消</button>
          <button 
            class="btn btn-primary" 
            @click="confirmAddStudents" 
            :disabled="selectedStudents.length === 0"
          >
            添加选中的学生 ({{ selectedStudents.length }})
          </button>
        </div>
      </div>
    </div>

    
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { classApi } from '../api/class'
import { assignmentApi } from '../api/assignment'
import { resourceApi } from '../api/resource'
import { studentApi } from '../api/student'
import { formatDate } from '../utils/dataFormatter'

export default {
  name: 'ClassDetailView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const loading = ref(true)
    const classInfo = ref(null)
    const assignments = ref([])
    const resources = ref([])
    const analytics = ref({})
    // 资源上传相关状态
    const showUploadModal = ref(false)
    const uploadResource = ref({
      title: '',
      type: 'document',
      description: ''
    })
    const selectedFile = ref(null)
    
    // 添加学生相关状态
    const showAddStudentModal = ref(false)
    const searchQuery = ref('')
    const searchResults = ref([])
    const loadingStudents = ref(false)
    const selectedStudents = ref([])

    const loadClassDetail = async () => {
      loading.value = true
      try {
        const classId = route.params.id
        
        // 检查classId是否有效
        if (!classId) {
          throw new Error('班级ID无效')
        }
        
        // 加载班级详情
        const classRes = await classApi.getClassDetail(classId)
        // 处理不同的响应格式
        let classData = classRes.data?.data || classRes.data || classRes
        
        console.log('班级详情原始数据:', classRes)
        console.log('班级详情处理后数据:', classData)
        
        // 确保students字段存在并正确处理
        if (!classData.students) {
          classData.students = []
        } else if (Array.isArray(classData.students)) {
          // 确保每个学生对象都有正确的结构
          classData.students = classData.students.map(student => {
            // 处理后端返回的学生数据格式
            return {
              id: student.id,
              user: {
                id: student.id,
                username: student.student_name || '未知',
                email: ''
              },
              username: student.student_name || '未知',
              student_id: student.student_no || null
            }
          })
        }
        
        classInfo.value = classData
        
        console.log('班级学生数据:', classInfo.value.students)
        console.log('学生数量:', classInfo.value.students?.length || 0)
        
        // 加载班级的作业
        try {
          const assignmentsRes = await assignmentApi.getAssignments({ class_id: classId })
          // 处理不同的响应格式
          let assignmentsData = assignmentsRes.data
          if (assignmentsData && Array.isArray(assignmentsData)) {
            assignments.value = assignmentsData
          } else if (assignmentsData && Array.isArray(assignmentsData.data)) {
            assignments.value = assignmentsData.data
          } else if (assignmentsData && Array.isArray(assignmentsData.results)) {
            assignments.value = assignmentsData.results
          } else {
            assignments.value = []
          }
        } catch (e) {
          console.log('加载作业失败:', e)
          assignments.value = []
        }
        
        // 加载班级的资源（通过分类筛选）
        try {
          const resourcesRes = await resourceApi.getResources({ category: classInfo.value?.name || '' })
          // 处理不同的响应格式
          let resourcesData = resourcesRes.data
          if (resourcesData && Array.isArray(resourcesData)) {
            resources.value = resourcesData
          } else if (resourcesData && Array.isArray(resourcesData.data)) {
            resources.value = resourcesData.data
          } else if (resourcesData && Array.isArray(resourcesData.results)) {
            resources.value = resourcesData.results
          } else {
            resources.value = []
          }
        } catch (e) {
          console.log('加载资源失败:', e)
          resources.value = []
        }
        
        // 加载班级分析数据
        try {
          const analyticsRes = await classApi.getClassAnalytics(classId)
          analytics.value = analyticsRes.data?.data || analyticsRes.data || analyticsRes || {}
        } catch (e) {
          console.log('加载分析数据失败:', e)
          analytics.value = {}
        }
      } catch (error) {
        console.error('加载班级详情失败:', error)
        // 更友好的错误提示
        let errorMessage = '加载班级详情失败'
        if (error.message === '班级ID无效') {
          errorMessage = '班级不存在或链接无效'
        } else if (error.response) {
          // 服务器返回了错误响应
          errorMessage = error.response.data?.error || error.response.data?.detail || error.response.statusText || errorMessage
        } else if (error.request) {
          // 请求已发送但没有收到响应
          errorMessage = '服务器无响应，请检查网络连接'
        } else {
          // 请求配置出错
          errorMessage = error.message || errorMessage
        }
        alert(errorMessage)
        // 自动返回上一页
        router.back()
      } finally {
        loading.value = false
      }
    }

    const goToStudentDetail = (studentId) => {
      router.push(`/teacher/students/${studentId}`)
    }

    const goToAssignmentDetail = (assignmentId) => {
      router.push(`/teacher/assignments/${assignmentId}`)
    }

    const addStudent = () => {
      showAddStudentModal.value = true
      searchQuery.value = ''
      searchResults.value = []
      selectedStudents.value = []
    }
    
    const searchStudents = async () => {
      const query = searchQuery.value.trim()
      if (!query) {
        searchResults.value = []
        return
      }
      
      loadingStudents.value = true
      try {
        // 调用搜索学生API
        const response = await studentApi.getStudents({
          search: query
        })
        
        let students = []
        if (response.data && Array.isArray(response.data)) {
          students = response.data
        } else if (response.data && Array.isArray(response.data.results)) {
          students = response.data.results
        }
        
        searchResults.value = students
      } catch (error) {
        console.error('搜索学生失败:', error)
        searchResults.value = []
        alert('搜索学生失败: ' + (error.response?.data?.error || error.message))
      } finally {
        loadingStudents.value = false
      }
    }
    
    const toggleStudentSelection = (studentId) => {
      const index = selectedStudents.value.indexOf(studentId)
      if (index === -1) {
        // 检查学生是否已在班级中
        if (!isStudentInClass(studentId)) {
          selectedStudents.value.push(studentId)
        }
      } else {
        selectedStudents.value.splice(index, 1)
      }
    }
    
    const isStudentInClass = (studentId) => {
      if (!classInfo.value || !classInfo.value.students) {
        return false
      }
      return classInfo.value.students.some(student => student.id === studentId)
    }
    
    const confirmAddStudents = async () => {
      if (selectedStudents.value.length === 0) {
        alert('请先选择要添加的学生')
        return
      }
      
      try {
        const classId = route.params.id
        
        // 批量添加学生到班级
        for (const studentId of selectedStudents.value) {
          await classApi.addStudent(classId, studentId)
        }
        
        alert('学生添加成功！')
        showAddStudentModal.value = false
        
        // 刷新班级详情数据
        await loadClassDetail()
      } catch (error) {
        console.error('添加学生失败:', error)
        alert('添加学生失败: ' + (error.response?.data?.error || error.message))
      }
    }

    const editClass = () => {
      router.push(`/teacher/classes?action=edit&id=${route.params.id}`)
    }

    const createAssignment = () => {
      router.push('/teacher/assignments/create')
    }

    const viewStudentProgress = (studentId) => {
      router.push(`/teacher/students/${studentId}`)
    }
    
    // 确认移除学生
    const confirmRemoveStudent = async (studentId, studentName) => {
      if (confirm(`确定要将学生 "${studentName}" 从班级中移除吗？`)) {
        try {
          await classApi.removeStudent(route.params.id, studentId)
          alert('学生移除成功！')
          // 刷新班级详情数据
          await loadClassDetail()
        } catch (error) {
          console.error('移除学生失败:', error)
          alert('移除学生失败: ' + (error.response?.data?.error || error.message || '请稍后重试'))
        }
      }
    }

    const getAssignmentStatus = (assignment) => {
      const now = new Date()
      const dueDate = new Date(assignment.due_date)
      if (dueDate < now) return 'overdue'
      const daysLeft = Math.ceil((dueDate - now) / (1000 * 60 * 60 * 24))
      if (daysLeft <= 3) return 'urgent'
      return 'normal'
    }

    const getAssignmentStatusText = (assignment) => {
      const status = getAssignmentStatus(assignment)
      if (status === 'overdue') return '已截止'
      if (status === 'urgent') return '即将截止'
      return '进行中'
    }

    const getResourceIcon = (type) => {
      const icons = {
        'document': '📄',
        'ppt': '📊',
        'video': '🎥',
        'image': '🖼️',
        'other': '📎'
      }
      return icons[type] || '📎'
    }

    // 处理文件选择
    const handleFileSelect = (event) => {
      if (event.target.files && event.target.files[0]) {
        selectedFile.value = event.target.files[0]
      }
    }

    // 上传资源
    const uploadResourceAction = async () => {
      if (!uploadResource.value.title || !selectedFile.value) {
        alert('请填写资源标题并选择文件')
        return
      }

      try {
        const formData = new FormData()
        formData.append('title', uploadResource.value.title)
        formData.append('description', uploadResource.value.description)
        formData.append('resource_type', uploadResource.value.type)
        formData.append('file', selectedFile.value)
        formData.append('class_id', route.params.id)

        await resourceApi.uploadResource(route.params.id, formData)
        alert('资源上传成功！')
        showUploadModal.value = false
        // 重置表单
        uploadResource.value = {
          title: '',
          type: 'document',
          description: ''
        }
        selectedFile.value = null
        // 刷新资源列表
        await loadClassDetail()
      } catch (error) {
        console.error('资源上传失败:', error)
        alert('资源上传失败: ' + (error.response?.data?.error || error.message))
      }
    }

    onMounted(() => {
      loadClassDetail()
    })
    
    // 监听路由变化，确保班级ID变化时重新加载数据
    watch(
      () => route.params.id,
      (newId) => {
        if (newId) {
          loadClassDetail()
        }
      },
      { immediate: true }
    )
    
    // 添加页面返回时的重新加载逻辑
    const originalBack = window.history.back
    window.history.back = function() {
      // 在返回之前记录当前路径
      const currentPath = window.location.pathname
      originalBack.call(this)
      // 如果返回的是当前页面，重新加载数据
      setTimeout(() => {
        if (window.location.pathname === currentPath) {
          loadClassDetail()
        }
      }, 100)
    }

    return {
      loading,
      classInfo,
      assignments,
      resources,
      analytics,
      showUploadModal,
      uploadResource,
      selectedFile,
      loadClassDetail,
      goToStudentDetail,
      goToAssignmentDetail,
      addStudent,
      editClass,
      createAssignment,
      viewStudentProgress,
      confirmRemoveStudent,
      getAssignmentStatus,
      getAssignmentStatusText,
      getResourceIcon,
      handleFileSelect,
      uploadResourceAction,
      formatDate
    }
  }
}
</script>

<style scoped>
.class-detail {
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

.class-header-card {
  background: white;
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  gap: 24px;
  align-items: flex-start;
  width: 100%;
}

.class-info {
  flex: 1;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.class-avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 16px;
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  font-weight: bold;
}

.class-info h1 {
  margin: 0 0 12px 0;
  font-size: 28px;
  color: #1e293b;
}

.class-meta {
  display: flex;
  gap: 24px;
  color: #64748b;
  font-size: 14px;
  margin-bottom: 12px;
}

.class-description {
  color: #475569;
  line-height: 1.6;
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

.students-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.student-card {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.student-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
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
  font-weight: bold;
}

.student-info {
  flex: 1;
}

.student-info h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  color: #1e293b;
}

.student-info p {
  margin: 0;
  font-size: 12px;
  color: #64748b;
}

.assignments-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.assignment-item {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  transition: all 0.2s;
}

.assignment-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.assignment-info h4 {
  margin: 0 0 8px 0;
  font-size: 18px;
  color: #1e293b;
}

.assignment-info p {
  margin: 0 0 12px 0;
  color: #64748b;
}

.assignment-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #94a3b8;
}

.assignment-status {
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.assignment-status.normal {
  background: #dbeafe;
  color: #1e40af;
}

.assignment-status.urgent {
  background: #fed7aa;
  color: #92400e;
}

.assignment-status.overdue {
  background: #fee2e2;
  color: #991b1b;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.resource-item {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  gap: 12px;
}

.resource-icon {
  font-size: 32px;
}

.resource-info h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #1e293b;
}

.resource-info p {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #64748b;
}

.resource-meta {
  font-size: 12px;
  color: #94a3b8;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #94a3b8;
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

.btn-small {
  padding: 6px 12px;
  font-size: 14px;
}

.btn-icon {
  background: none;
  border: none;
  padding: 8px;
  font-size: 18px;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.btn-icon:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.btn-icon.btn-danger {
  color: #d32f2f;
}

.btn-icon.btn-danger:hover {
  background-color: rgba(211, 47, 47, 0.1);
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: #f1f5f9;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #e2e8f0;
}

.modal-body {
  padding: 24px;
  max-height: 60vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.form-group input[type="text"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-group input[type="text"]:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.file-input-wrapper {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-input-wrapper input[type="file"] {
  display: none;
}

.file-name {
  font-size: 14px;
  color: #64748b;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #f1f5f9;
  background: #f8fafc;
}

.upload-modal {
  max-width: 560px;
}
</style>

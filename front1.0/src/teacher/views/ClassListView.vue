<template>
  <div class="class-management">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-left">
        <h1>班级管理</h1>
        <p>管理您的教学班级，查看学生进度</p>
      </div>
      <div class="header-right">
        <button class="btn btn-primary" @click="showCreateModal = true">
          <span>➕</span> 创建班级
        </button>
      </div>
    </div>

    <!-- 统计概览 -->
    <div class="stats-row">
      <div class="stat-item">
        <div class="stat-icon blue">📚</div>
        <div class="stat-content">
          <span class="stat-value">{{ totalClasses }}</span>
          <span class="stat-label">班级总数</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon green">👥</div>
        <div class="stat-content">
          <span class="stat-value">{{ totalStudents }}</span>
          <span class="stat-label">学生总数</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon purple">📝</div>
        <div class="stat-content">
          <span class="stat-value">{{ totalAssignments }}</span>
          <span class="stat-label">作业总数</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon orange">📊</div>
        <div class="stat-content">
          <span class="stat-value">{{ avgProgress }}%</span>
          <span class="stat-label">平均完成率</span>
        </div>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filter-section">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索班级名称..."
        />
      </div>
      <div class="filter-options">
        <select v-model="statusFilter">
          <option value="all">全部状态</option>
          <option value="active">进行中</option>
          <option value="completed">已结束</option>
        </select>
        <select v-model="sortBy">
          <option value="name">按名称排序</option>
          <option value="students">按学生数排序</option>
          <option value="progress">按进度排序</option>
          <option value="created">按创建时间</option>
        </select>
      </div>
    </div>

    <!-- 班级列表 -->
    <div class="classes-grid">
      <div 
        v-for="classItem in filteredClasses" 
        :key="classItem.id" 
        class="class-card"
        @click="goToClassDetail(classItem.id)"
      >
        <div class="class-header" :style="{ background: classItem.gradient }">
          <div class="class-avatar">
            {{ (classItem.name || '班').charAt(0) }}
          </div>
          <div class="class-status" :class="classItem.status">
            {{ classItem.status === 'active' ? '进行中' : '已结束' }}
          </div>
        </div>
        
        <div class="class-body">
          <h3>{{ classItem.name }}</h3>
          <p class="class-course">{{ classItem.course }}</p>
          
          <div class="class-info-row">
            <div class="info-item">
              <span class="info-icon">👥</span>
              <span>{{ classItem.studentCount }} 名学生</span>
            </div>
            <div class="info-item">
              <span class="info-icon">📝</span>
              <span>{{ classItem.assignmentCount }} 份作业</span>
            </div>
          </div>
          
          <div class="progress-section">
            <div class="progress-header">
              <span>课程进度</span>
              <span class="progress-value">{{ classItem.progress }}%</span>
            </div>
            <div class="progress-bar">
              <div 
                class="progress-fill" 
                :style="{ width: classItem.progress + '%', background: classItem.gradient }"
              ></div>
            </div>
          </div>
          
          <div class="class-meta">
            <span class="meta-item">
              📅 创建于 {{ formatDate(classItem.createdAt) }}
            </span>
          </div>
        </div>
        
        <div class="class-actions">
          <button class="action-btn" @click.stop="editClass(classItem)" title="编辑">
            ✏️
          </button>
          <button class="action-btn" @click.stop="viewStudents(classItem)" title="查看学生">
            👥
          </button>
          <button class="action-btn danger" @click.stop="deleteClass(classItem)" title="删除">
            🗑️
          </button>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="filteredClasses.length === 0" class="empty-state">
      <div class="empty-icon">📚</div>
      <h3>没有找到班级</h3>
      <p>尝试调整搜索条件或创建新班级</p>
      <button class="btn btn-primary" @click="showCreateModal = true">
        创建第一个班级
      </button>
    </div>

    <!-- 创建/编辑班级弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal">
        <div class="modal-header">
          <h2>{{ editingClass ? '编辑班级' : '创建班级' }}</h2>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        
        <form @submit.prevent="saveClass" class="modal-body">
          <div class="form-group">
            <label>班级名称 <span class="required">*</span></label>
            <input 
              type="text" 
              v-model="classForm.name" 
              placeholder="例如：Python入门班"
              required
            />
          </div>
          
          <div class="form-group">
            <label>课程名称 <span class="required">*</span></label>
            <input 
              type="text" 
              v-model="classForm.course" 
              placeholder="例如：Python编程基础"
              required
            />
          </div>
          
          <div class="form-group">
            <label>选择教材 <span class="required">*</span></label>
            <select 
              v-model="classForm.bookId" 
              required
              :disabled="loadingBooks"
            >
              <option value="">请选择教材</option>
              <option v-for="book in books" :key="book.id" :value="book.id">
                {{ book.title }} - {{ book.author }}
              </option>
            </select>
            <p v-if="loadingBooks" class="form-hint">正在加载教材列表...</p>
            <p v-if="!loadingBooks && books.length === 0" class="form-hint text-warning">
              没有可用的教材，系统将自动选择默认教材
            </p>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>开始日期</label>
              <input type="date" v-model="classForm.startDate" />
            </div>
            <div class="form-group">
              <label>结束日期</label>
              <input type="date" v-model="classForm.endDate" />
            </div>
          </div>
          
          <div class="form-group">
            <label>班级描述</label>
            <textarea 
              v-model="classForm.description" 
              placeholder="描述这个班级的教学目标和内容..."
              rows="3"
            ></textarea>
          </div>
          
          <div class="form-group">
            <label>选择主题颜色</label>
            <div class="color-picker">
              <div 
                v-for="color in colorOptions" 
                :key="color"
                class="color-option"
                :class="{ selected: classForm.gradient === color }"
                :style="{ background: color }"
                @click="classForm.gradient = color"
              ></div>
            </div>
          </div>
          
          <div class="form-group">
            <label>班级设置</label>
            <div class="checkbox-group">
              <label class="checkbox-item">
                <input type="checkbox" v-model="classForm.allowJoin" />
                <span>允许学生加入</span>
              </label>
              <label class="checkbox-item">
                <input type="checkbox" v-model="classForm.autoGrade" />
                <span>自动批改作业</span>
              </label>
            </div>
          </div>
          
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">
              取消
            </button>
            <button type="submit" class="btn btn-primary">
              {{ editingClass ? '保存修改' : '创建班级' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { classApi } from '../api/class'
import { teacherApi } from '../api/teacher'
import { assignmentApi } from '../api/assignment'

export default {
  name: 'ClassManagement',
  setup() {
    const router = useRouter()
    const searchQuery = ref('')
    const statusFilter = ref('all')
    const sortBy = ref('name')
    const showCreateModal = ref(false)
    const editingClass = ref(null)
    const loading = ref(false)

    const classForm = ref({
      name: '',
      course: '',
      bookId: '',
      startDate: '',
      endDate: '',
      description: '',
      gradient: 'linear-gradient(135deg, #667eea, #764ba2)',
      allowJoin: true,
      autoGrade: false
    })
    
    const books = ref([])
    const loadingBooks = ref(false)

    const colorOptions = [
      'linear-gradient(135deg, #667eea, #764ba2)',
      'linear-gradient(135deg, #f093fb, #f5576c)',
      'linear-gradient(135deg, #4facfe, #00f2fe)',
      'linear-gradient(135deg, #43e97b, #38f9d7)',
      'linear-gradient(135deg, #fa709a, #fee140)',
      'linear-gradient(135deg, #a8edea, #fed6e3)',
      'linear-gradient(135deg, #ff9a9e, #fecfef)',
      'linear-gradient(135deg, #ffecd2, #fcb69f)'
    ]

    const classes = ref([])
    const totalClasses = ref(0)

    // 从API加载班级列表
    const loadClasses = async () => {
      loading.value = true
      try {
        const response = await classApi.getClasses()
        // axios返回的数据在response.data中，但如果是数组则直接使用
        let data = response.data
        let results = []
        
        // 处理不同的数据格式
        if (Array.isArray(data)) {
          // 数据已经是数组
          results = data
        } else if (data && Array.isArray(data.results)) {
          // 分页格式
          results = data.results
        } else if (data && Array.isArray(data.data)) {
          // 嵌套data格式
          results = data.data
        } else {
          results = []
        }
        
        // 先映射班级基本信息
        classes.value = results.map(cls => ({
          id: cls.id,
          name: cls.name || `班级${cls.id}`,
          course: cls.major || '',
          studentCount: cls.student_count || 0,
          assignmentCount: 0, // 初始化为0，后续从作业API获取
          progress: 0, // 可以从analytics获取
          status: 'active',
          gradient: getClassColor(cls.id),
          createdAt: cls.created_at || new Date().toISOString().split('T')[0],
          major: cls.major,
          grade: cls.grade,
          description: cls.description
        }))
        
        // 基于实际映射后的班级数组长度设置班级总数
        totalClasses.value = classes.value.length
        
        // 为每个班级获取作业数量
        for (let i = 0; i < classes.value.length; i++) {
          const classItem = classes.value[i]
          try {
            const assignmentResponse = await assignmentApi.getAssignments({ class_id: classItem.id })
            let assignments = []
            
            // 处理作业数据的不同格式
            if (Array.isArray(assignmentResponse.data)) {
              assignments = assignmentResponse.data
            } else if (assignmentResponse.data && Array.isArray(assignmentResponse.data.results)) {
              assignments = assignmentResponse.data.results
            } else if (assignmentResponse.data && Array.isArray(assignmentResponse.data.data)) {
              assignments = assignmentResponse.data.data
            }
            
            // 更新班级的作业数量
            classes.value[i].assignmentCount = assignments.length
          } catch (error) {
            console.error(`获取班级${classItem.name}的作业数量失败:`, error)
            // 如果获取失败，保持assignmentCount为0
            classes.value[i].assignmentCount = 0
          }
        }
        
        console.log('加载的班级数据:', classes.value)
        console.log('班级总数:', totalClasses.value)
      } catch (error) {
        console.error('加载班级失败:', error)
        alert('加载班级失败: ' + (error.response?.data?.error || error.message))
      } finally {
        loading.value = false
      }
    }

    const getClassColor = (id) => {
      const colors = [
        'linear-gradient(135deg, #667eea, #764ba2)',
        'linear-gradient(135deg, #f093fb, #f5576c)',
        'linear-gradient(135deg, #4facfe, #00f2fe)',
        'linear-gradient(135deg, #43e97b, #38f9d7)',
        'linear-gradient(135deg, #fa709a, #fee140)',
        'linear-gradient(135deg, #a8edea, #fed6e3)',
        'linear-gradient(135deg, #ff9a9e, #fecfef)',
        'linear-gradient(135deg, #ffecd2, #fcb69f)'
      ]
      return colors[id % colors.length]
    }

    // 加载教材列表
    const loadBooks = async () => {
      loadingBooks.value = true
      try {
        const response = await teacherApi.getBooks()
        let data = response.data
        if (Array.isArray(data)) {
          books.value = data
        } else if (data && Array.isArray(data.results)) {
          books.value = data.results
        } else if (data && Array.isArray(data.data)) {
          books.value = data.data
        } else {
          books.value = []
        }
        
        // 如果有教材且没有选择，默认选择第一个
        if (books.value.length > 0 && !classForm.value.bookId) {
          classForm.value.bookId = books.value[0].id
        }
      } catch (error) {
        console.error('加载教材失败:', error)
        books.value = []
      } finally {
        loadingBooks.value = false
      }
    }

    onMounted(() => {
      loadClasses()
      loadBooks()
    })

    const totalStudents = computed(() => {
      return classes.value.reduce((sum, c) => sum + c.studentCount, 0)
    })

    const totalAssignments = computed(() => {
      return classes.value.reduce((sum, c) => sum + c.assignmentCount, 0)
    })

    const avgProgress = computed(() => {
      const sum = classes.value.reduce((sum, c) => sum + c.progress, 0)
      return Math.round(sum / classes.value.length)
    })

    const filteredClasses = computed(() => {
      let result = [...classes.value]
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(c => 
          c.name.toLowerCase().includes(query) ||
          c.course.toLowerCase().includes(query)
        )
      }
      
      if (statusFilter.value !== 'all') {
        result = result.filter(c => c.status === statusFilter.value)
      }
      
      switch (sortBy.value) {
        case 'students':
          result.sort((a, b) => b.studentCount - a.studentCount)
          break
        case 'progress':
          result.sort((a, b) => b.progress - a.progress)
          break
        case 'created':
          result.sort((a, b) => new Date(b.createdAt) - new Date(a.createdAt))
          break
        default:
          result.sort((a, b) => a.name.localeCompare(b.name))
      }
      
      return result
    })

    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
    }

    const goToClassDetail = (classId) => {
      router.push(`/teacher/classes/${classId}`)
    }

    const editClass = (classItem) => {
      editingClass.value = classItem
      classForm.value = {
        name: classItem.name || '',
        course: classItem.major || classItem.course || '',
        bookId: classItem.book?.id || classItem.book_id || '',
        startDate: '',
        endDate: '',
        description: classItem.description || '',
        gradient: classItem.gradient || 'linear-gradient(135deg, #667eea, #764ba2)',
        allowJoin: true,
        autoGrade: false
      }
      showCreateModal.value = true
    }

    const viewStudents = (classItem) => {
      router.push(`/teacher/students?classId=${classItem.id}`)
    }

    const moreOptions = (classItem) => {
      console.log('更多选项:', classItem)
    }

    const closeModal = () => {
      showCreateModal.value = false
      editingClass.value = null
      classForm.value = {
        name: '',
        course: '',
        bookId: books.value.length > 0 ? books.value[0].id : '',
        startDate: '',
        endDate: '',
        description: '',
        gradient: 'linear-gradient(135deg, #667eea, #764ba2)',
        allowJoin: true,
        autoGrade: false
      }
    }

    const saveClass = async () => {
      if (!classForm.value.name) {
        alert('请输入班级名称')
        return
      }
      
      if (!editingClass.value && !classForm.value.bookId && books.value.length > 0) {
        alert('请选择教材')
        return
      }

      loading.value = true
      try {
        const data = {
          name: classForm.value.name,
          major: classForm.value.course || '',
          grade: '',
          description: classForm.value.description || ''
        }
        
        // 创建时添加book_id
        if (!editingClass.value && classForm.value.bookId) {
          data.book = classForm.value.bookId
        }

        if (editingClass.value) {
          // 更新班级
          await classApi.updateClass(editingClass.value.id, data)
          alert('班级更新成功！')
        } else {
          // 创建班级
          await classApi.createClass(data)
          alert('班级创建成功！')
        }
        
        closeModal()
        // 重新加载班级列表
        await loadClasses()
      } catch (error) {
        console.error('保存班级失败:', error)
        const errorMsg = error.response?.data?.error || error.response?.data?.detail || error.message
        alert('保存失败: ' + errorMsg)
      } finally {
        loading.value = false
      }
    }

    const deleteClass = async (classItem) => {
      if (!confirm(`确定要删除班级"${classItem.name}"吗？此操作不可恢复！`)) {
        return
      }

      loading.value = true
      try {
        await classApi.deleteClass(classItem.id)
        alert('班级删除成功！')
        // 重新加载班级列表
        await loadClasses()
      } catch (error) {
        console.error('删除班级失败:', error)
        alert('删除失败: ' + (error.response?.data?.error || error.message))
      } finally {
        loading.value = false
      }
    }

    return {
      searchQuery,
      statusFilter,
      sortBy,
      classes,
      totalClasses,
      totalStudents,
      totalAssignments,
      avgProgress,
      filteredClasses,
      showCreateModal,
      editingClass,
      classForm,
      colorOptions,
      books,
      loadingBooks,
      loading,
      formatDate,
      goToClassDetail,
      editClass,
      viewStudents,
      moreOptions,
      closeModal,
      saveClass,
      deleteClass,
      loadClasses
    }
  }
}
</script>

<style scoped>
.class-management {
  max-width: 1400px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.header-left h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.header-left p {
  color: #6b7280;
  margin: 0;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 24px;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
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

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.stat-item {
  background: white;
  border-radius: 14px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

.stat-icon {
  width: 52px;
  height: 52px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.blue { background: #667eea20; }
.stat-icon.green { background: #43e97b20; }
.stat-icon.purple { background: #f093fb20; }
.stat-icon.orange { background: #fa709a20; }

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 26px;
  font-weight: 700;
  color: #1f2937;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
}

.filter-section {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.search-box {
  flex: 1;
  position: relative;
}

.search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
}

.search-box input {
  width: 100%;
  padding: 14px 16px 14px 48px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 15px;
  outline: none;
  transition: all 0.3s;
}

.search-box input:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.filter-options {
  display: flex;
  gap: 12px;
}

.filter-options select {
  padding: 14px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 14px;
  background: white;
  cursor: pointer;
  outline: none;
}

.filter-options select:focus {
  border-color: #667eea;
}

.classes-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
  gap: 24px;
}

.class-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  cursor: pointer;
  transition: all 0.3s;
  position: relative;
}

.class-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.1);
}

.class-header {
  padding: 24px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.class-avatar {
  width: 56px;
  height: 56px;
  background: white;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  font-weight: 700;
  color: #667eea;
}

.class-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.class-status.active {
  background: rgba(255,255,255,0.2);
  color: white;
}

.class-status.completed {
  background: rgba(0,0,0,0.2);
  color: white;
}

.class-body {
  padding: 20px 24px 24px;
}

.class-body h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 6px 0;
}

.class-course {
  color: #6b7280;
  font-size: 14px;
  margin: 0 0 16px 0;
}

.class-info-row {
  display: flex;
  gap: 20px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6b7280;
}

.progress-section {
  margin-bottom: 16px;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 13px;
  color: #6b7280;
}

.progress-value {
  font-weight: 600;
  color: #1f2937;
}

.progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.5s ease;
}

.class-meta {
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
}

.meta-item {
  font-size: 12px;
  color: #9ca3af;
}

.class-actions {
  position: absolute;
  top: 16px;
  right: 16px;
  display: flex;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}

.class-card:hover .class-actions {
  opacity: 1;
}

.action-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.action-btn:hover {
  background: #f3f4f6;
  transform: scale(1.1);
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 20px;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.empty-state p {
  color: #6b7280;
  margin: 0 0 24px 0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #f3f4f6;
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  border-radius: 8px;
  background: #f3f4f6;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
}

.close-btn:hover {
  background: #e5e7eb;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.required {
  color: #ef4444;
}

.form-group input,
.form-group textarea,
.form-group select {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  font-size: 15px;
  outline: none;
  transition: all 0.3s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.color-picker {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.color-option {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.3s;
  border: 3px solid transparent;
}

.color-option:hover {
  transform: scale(1.1);
}

.color-option.selected {
  border-color: #1f2937;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-item {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  font-size: 14px;
  color: #374151;
}

.checkbox-item input {
  width: auto;
}

.form-hint {
  font-size: 13px;
  color: #6b7280;
  margin-top: 6px;
}

.form-hint.text-warning {
  color: #f59e0b;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 20px;
  border-top: 1px solid #f3f4f6;
  margin-top: 8px;
}

@media (max-width: 768px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .classes-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-section {
    flex-direction: column;
  }
  
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>

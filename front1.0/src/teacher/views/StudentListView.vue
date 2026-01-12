<template>
  <div class="student-management">
    <div class="page-header">
      <div class="header-left">
        <h1>学生管理</h1>
        <p>管理所有学生，查看学习进度和成绩表现</p>
      </div>
      <div class="header-right">
        <button class="btn btn-secondary" @click="exportData">
          <span>📊</span> 导出数据
        </button>
        <button class="btn btn-primary" @click="showAddModal = true">
          <span>➕</span> 添加学生
        </button>
      </div>
    </div>

    <div class="stats-row">
      <div class="stat-item">
        <div class="stat-icon blue">👥</div>
        <div class="stat-content">
          <span class="stat-value">{{ students.length }}</span>
          <span class="stat-label">学生总数</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon green">📈</div>
        <div class="stat-content">
          <span class="stat-value">{{ averageProgress }}%</span>
          <span class="stat-label">平均进度</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon purple">⭐</div>
        <div class="stat-content">
          <span class="stat-value">{{ averageScore }}</span>
          <span class="stat-label">平均成绩</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon orange">🔥</div>
        <div class="stat-content">
          <span class="stat-value">{{ activeStudents }}</span>
          <span class="stat-label">活跃学生</span>
        </div>
      </div>
    </div>

    <div class="filter-section">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input
          type="text"
          v-model="searchQuery"
          placeholder="搜索学生姓名、学号..."
        />
      </div>
      <div class="filter-options">
        <select v-model="classFilter">
          <option value="all">全部班级</option>
          <option v-for="cls in classes" :key="cls.id" :value="cls.id">
            {{ cls.name }}
          </option>
        </select>
        <select v-model="statusFilter">
          <option value="all">全部状态</option>
          <option value="active">学习中</option>
          <option value="inactive">已暂停</option>
          <option value="completed">已完成</option>
        </select>
        <select v-model="sortBy">
          <option value="name">按姓名排序</option>
          <option value="progress">按进度排序</option>
          <option value="score">按成绩排序</option>
          <option value="activity">按活跃度排序</option>
          <option value="recent">最近活跃</option>
        </select>
        <div class="view-toggle">
          <button
            class="view-btn"
            :class="{ active: viewMode === 'card' }"
            @click="viewMode = 'card'"
          >
            ⊞
          </button>
          <button
            class="view-btn"
            :class="{ active: viewMode === 'table' }"
            @click="viewMode = 'table'"
          >
            ☰
          </button>
        </div>
      </div>
    </div>

    <!-- 加载状态和空数据提示 -->
    <div v-if="loading" class="loading-state" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 20px; text-align: center;">
      <div style="width: 40px; height: 40px; border: 4px solid #e2e8f0; border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite;"></div>
      <p style="margin-top: 16px; color: #64748b;">加载学生数据中...</p>
    </div>
    <div v-else-if="filteredStudents.length === 0" class="empty-state" style="display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px 20px; text-align: center;">
      <div style="font-size: 48px; margin-bottom: 16px;">👥</div>
      <p style="font-size: 16px; color: #374151; margin-bottom: 8px;">暂无学生数据</p>
      <p style="font-size: 14px; color: #64748b;">请尝试调整筛选条件或添加学生</p>
    </div>
    
    <!-- 学生卡片视图 -->
    <div v-else-if="viewMode === 'card'" class="students-grid">
      <div
        v-for="student in filteredStudents"
        :key="student.id"
        class="student-card"
        @click="viewStudentDetail(student)"
      >
        <div class="student-header">
          <div class="student-avatar" :style="{ background: student.avatarColor }">
            {{ (student.name || 'S').charAt(0) }}
          </div>
          <div class="student-status" :class="student.status">
            {{ getStatusText(student.status) }}
          </div>
        </div>

        <div class="student-body">
          <h3>{{ student.name }}</h3>
          <p class="student-id">学号: {{ student.studentId }}</p>
          <p class="student-class">{{ student.className }}</p>

          <div class="student-stats">
            <div class="mini-stat">
              <span class="mini-value">{{ student.progress }}%</span>
              <span class="mini-label">进度</span>
            </div>
            <div class="mini-stat">
              <span class="mini-value">{{ student.score }}</span>
              <span class="mini-label">成绩</span>
            </div>
            <div class="mini-stat">
              <span class="mini-value">{{ student.assignmentCount }}</span>
              <span class="mini-label">作业</span>
            </div>
          </div>

          <div class="progress-mini">
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: student.progress + '%', background: student.progressColor }"
              ></div>
            </div>
            <span class="progress-label">学习进度</span>
          </div>

          <div class="student-meta">
            <span class="meta-item">
              🕐 最后活跃: {{ formatDate(student.lastActive) }}
            </span>
          </div>
        </div>

        <div class="student-actions">
          <button class="action-btn" @click.stop="sendMessage(student)" title="发送消息">
            💬
          </button>
          <button class="action-btn" @click.stop="viewStudentDetail(student)" title="查看详情">
            👁️
          </button>
          <button class="action-btn" @click.stop="moreOptions(student)" title="更多">
            ⋯
          </button>
        </div>
      </div>
    </div>

    <div v-else class="students-table">
      <table>
        <thead>
          <tr>
            <th>学生信息</th>
            <th>学号</th>
            <th>班级</th>
            <th>学习进度</th>
            <th>成绩</th>
            <th>作业完成</th>
            <th>最近活跃</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="student in filteredStudents"
            :key="student.id"
            @click="viewStudentDetail(student)"
          >
            <td>
              <div class="student-info">
                <div class="student-avatar small" :style="{ background: student.avatarColor }">
                  {{ (student.name || 'S').charAt(0) }}
                </div>
                <span>{{ student.name }}</span>
              </div>
            </td>
            <td>{{ student.studentId }}</td>
            <td>{{ student.className }}</td>
            <td>
              <div class="progress-cell">
                <div class="progress-bar small">
                  <div
                    class="progress-fill"
                    :style="{ width: student.progress + '%', background: student.progressColor }"
                  ></div>
                </div>
                <span>{{ student.progress }}%</span>
              </div>
            </td>
            <td>
              <span class="score-badge" :class="getScoreClass(student.score)">
                {{ student.score }}
              </span>
            </td>
            <td>{{ student.completedAssignments }}/{{ student.totalAssignments }}</td>
            <td>{{ formatDate(student.lastActive) }}</td>
            <td>
              <span class="status-badge" :class="student.status">
                {{ getStatusText(student.status) }}
              </span>
            </td>
            <td>
              <div class="table-actions">
                <button class="action-btn small" @click.stop="sendMessage(student)">
                  💬
                </button>
                <button class="action-btn small" @click.stop="viewStudentDetail(student)">
                  👁️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <button
        class="page-btn"
        :disabled="currentPage === 1"
        @click="currentPage--"
      >
        ← 上一页
      </button>
      <span class="page-info">
        第 {{ currentPage }} 页 / 共 {{ totalPages }} 页
      </span>
      <button
        class="page-btn"
        :disabled="currentPage === totalPages"
        @click="currentPage++"
      >
        下一页 →
      </button>
    </div>

    <!-- 消息提示 -->
    <div v-if="message" class="message" :class="messageType" style="position: fixed; top: 20px; right: 20px; padding: 12px 20px; border-radius: 8px; color: white; font-weight: 500; z-index: 1001; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);">
      {{ message }}
    </div>
    
    <!-- 选择学生模态框 -->
    <div v-if="showAddModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal" style="max-width: 600px;">
        <div class="modal-header">
          <h2>添加学生到班级</h2>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <!-- 搜索区域 -->
          <div class="search-section" style="margin-bottom: 20px;">
            <div style="display: flex; gap: 10px; align-items: center;">
              <input 
                type="text" 
                v-model="searchExistingStudent" 
                placeholder="搜索学生姓名或学号..." 
                @keyup.enter="searchStudents"
                style="flex: 1; padding: 10px; border: 1px solid #e2e8f0; border-radius: 8px;"
              />
              <button 
                @click="searchStudents" 
                class="btn btn-primary" 
                :disabled="searching"
                style="padding: 10px 20px;"
              >
                {{ searching ? '搜索中...' : '搜索' }}
              </button>
            </div>
          </div>
          
          <!-- 班级选择 -->
          <div class="form-group" style="margin-bottom: 20px;">
            <label>目标班级 *</label>
            <select v-model="assigningClassId" required style="width: 100%; padding: 12px; border: 1px solid #e2e8f0; border-radius: 8px;">
              <option value="">请选择班级</option>
              <option v-for="cls in classes" :key="cls.id" :value="cls.id">
                {{ cls.name }}
              </option>
            </select>
          </div>
          
          <!-- 搜索结果 -->
          <div class="search-results" style="margin-bottom: 20px; max-height: 300px; overflow-y: auto; border: 1px solid #e2e8f0; border-radius: 8px;">
            <div v-if="searching" style="padding: 20px; text-align: center; color: #64748b;">
              <div style="width: 24px; height: 24px; border: 3px solid #e2e8f0; border-top-color: #3b82f6; border-radius: 50%; animation: spin 1s linear infinite; margin: 0 auto 8px;"></div>
              <span>搜索中...</span>
            </div>
            <div v-else-if="searchResults.length === 0 && searchExistingStudent" style="padding: 30px 20px; text-align: center; color: #64748b;">
              <div style="font-size: 32px; margin-bottom: 12px;">🔍</div>
              <p style="margin-bottom: 8px;">没有找到匹配的学生</p>
              <p style="font-size: 13px;">请尝试调整搜索关键词</p>
              <div style="margin-top: 16px; padding: 12px; background: #f8fafc; border-radius: 8px; font-size: 13px;">
                <p>搜索示例：</p>
                <p style="margin: 4px 0;">• 姓名：zzh</p>
                <p style="margin: 4px 0;">• 学号：202230033027</p>
              </div>
            </div>
            <div v-else-if="searchResults.length === 0" style="padding: 30px 20px; text-align: center; color: #64748b;">
              <div style="font-size: 32px; margin-bottom: 12px;">👥</div>
              <p>请输入关键词搜索学生</p>
            </div>
            <div v-else>
              <!-- 全选按钮 -->
              <div style="padding: 10px 15px; background: #f8fafc; border-bottom: 1px solid #e2e8f0; display: flex; align-items: center; gap: 10px;">
                <input 
                  type="checkbox" 
                  :checked="selectedStudents.length === searchResults.length && searchResults.length > 0" 
                  @change="selectAllStudents"
                />
                <span style="font-weight: 500;">全选 ({{ selectedStudents.length }}/{{ searchResults.length }})</span>
              </div>
              
              <!-- 学生列表 -->
              <div 
                v-for="student in searchResults" 
                :key="student.id" 
                style="padding: 15px; border-bottom: 1px solid #f1f5f9; display: flex; align-items: center; gap: 15px;"
              >
                <input 
                  type="checkbox" 
                  :checked="selectedStudents.includes(student.id)" 
                  @change="toggleStudentSelection(student.id)"
                />
                <div style="flex: 1;">
                  <div style="font-weight: 500;">{{ student.name }}</div>
                  <div style="font-size: 13px; color: #64748b;">学号: {{ student.studentId }}</div>
                </div>
                <div style="font-size: 12px; color: #3b82f6;">
                  当前班级: {{ student.currentClass }}
                </div>
              </div>
            </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="form-actions" style="display: flex; justify-content: flex-end; gap: 12px; margin-top: 24px;">
            <button type="button" class="btn btn-secondary" @click="closeModal">
              取消
            </button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="assignStudentsToClass" 
              :disabled="assigning || selectedStudents.length === 0 || !assigningClassId"
            >
              {{ assigning ? '分配中...' : `分配 ${selectedStudents.length} 名学生` }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showMessageModal" class="modal-overlay" @click.self="closeMessageModal">
      <div class="modal">
        <div class="modal-header">
          <h2>发送消息</h2>
          <button class="close-btn" @click="closeMessageModal">×</button>
        </div>
        <form @submit.prevent="sendMessageToStudent" class="modal-body">
          <div class="form-group">
            <label>发送给</label>
            <input type="text" :value="selectedStudent?.name" disabled />
          </div>
          <div class="form-group">
            <label>消息内容 *</label>
            <textarea
              v-model="messageContent"
              rows="4"
              placeholder="请输入消息内容..."
              required
            ></textarea>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="closeMessageModal">
              取消
            </button>
            <button type="submit" class="btn btn-primary">
              发送消息
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { studentApi } from '../api/student'
import { classApi } from '../api/class'

export default {
  name: 'StudentListView',
  data() {
    return {
      searchQuery: '',
      classFilter: 'all',
      statusFilter: 'all',
      sortBy: 'name',
      viewMode: 'card',
      currentPage: 1,
      pageSize: 12,
      showAddModal: false,
      showMessageModal: false,
      selectedStudent: null,
      messageContent: '',
      // 新添加的状态变量
      searchExistingStudent: '',
      searchResults: [],
      selectedStudents: [],
      assigningClassId: '',
      searching: false,
      assigning: false,
      message: '',
      messageType: '',
      classes: [],
      students: [],
      loading: false
    }
  },
  mounted() {
    this.loadClasses()
    // 检查URL参数中是否有classId
    const classId = this.$route.query.classId
    if (classId) {
      this.classFilter = classId
    }
    this.loadStudents()
  },
  methods: {
    async loadClasses() {
      try {
        const response = await classApi.getClasses()
        // 处理不同的响应格式
        let data = response.data
        if (Array.isArray(data)) {
          // 数据已经是数组
        } else if (data && Array.isArray(data.results)) {
          data = data.results
        } else if (data && Array.isArray(data.data)) {
          data = data.data
        } else {
          data = []
        }
        
        this.classes = data.map(cls => ({
          id: cls.id,
          name: cls.name
        }))
      } catch (error) {
        console.error('加载班级失败:', error)
      }
    },
    async loadStudents() {
      this.loading = true
      console.log('开始加载学生数据，班级筛选:', this.classFilter)
      try {
        const params = {}
        if (this.classFilter !== 'all') {
          params.class_id = this.classFilter
        }
        const response = await studentApi.getStudents(params)
        
        console.log('加载学生API响应:', response)
        console.log('加载学生响应data结构:', response.data)
        console.log('加载学生响应data类型:', typeof response.data)
        console.log('加载学生响应data键名:', Object.keys(response.data))
        
        // 处理不同的响应格式
        let data = response.data
        let results = []
        
        // 处理分页数据
        console.log('检查data是否为数组:', Array.isArray(data))
        if (Array.isArray(data)) {
          console.log('情况1: data是数组')
          results = data
        } else if (data && Array.isArray(data.results)) {
          console.log('情况2: data.results是数组，长度:', data.results.length)
          results = data.results
        } else if (data && Array.isArray(data.data)) {
          console.log('情况3: data.data是数组，长度:', data.data.length)
          results = data.data
        } else {
          console.log('情况4: 未找到数据数组')
          console.log('data的完整内容:', JSON.stringify(data))
          results = []
        }
        
        console.log('加载的学生原始数据:', results)
        
        // 直接使用获取到的学生数据，不再使用模拟数据
        this.students = results.map(student => ({
          id: student.id,
          name: student.student_name || student.username,
          studentId: student.student_no || '',
          className: student.class_name || '未分配班级',
          classId: student.class_obj || null,
          progress: student.progress || 0,
          score: Math.round(student.avg_score || 0),
          assignmentCount: student.submission_count || 0,
          completedAssignments: student.completed_assignments || 0,
          totalAssignments: student.total_assignments || 0,
          lastActive: student.last_learn_time || student.last_login || student.updated_at || student.date_joined || new Date().toISOString(),
          status: student.status === 1 ? 'active' : 'inactive',
          avatarColor: this.getAvatarColor(student.id),
          progressColor: this.getProgressColor(student.id)
        }))
        
        console.log('处理后的学生数据:', this.students)
        console.log('页面显示的学生列表（部分）:', this.students.map(s => ({id: s.id, name: s.name, studentId: s.studentId})))
        
      } catch (error) {
        console.error('加载学生失败:', error)
        console.error('错误详情:', error.response || error.message)
        alert('加载学生失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.loading = false
      }
    },
    getAvatarColor(id) {
      const colors = ['#3498db', '#2ecc71', '#9b59b6', '#e74c3c', '#f39c12', '#1abc9c']
      return colors[id % colors.length]
    },
    getProgressColor(id) {
      return this.getAvatarColor(id)
    },
    getStatusText(status) {
      const statusMap = {
        active: '学习中',
        inactive: '已暂停',
        completed: '已完成'
      }
      return statusMap[status] || status
    },
    getScoreClass(score) {
      if (score >= 90) return 'excellent'
      if (score >= 80) return 'good'
      if (score >= 70) return 'average'
      return 'poor'
    },
    formatDate(dateStr) {
      const date = new Date(dateStr)
      const now = new Date()
      const diff = Math.floor((now - date) / (1000 * 60 * 60 * 24))
      if (diff === 0) return '今天'
      if (diff === 1) return '昨天'
      if (diff < 7) return `${diff}天前`
      return date.toLocaleDateString('zh-CN')
    },
    viewStudentDetail(student) {
      this.$router.push(`/teacher/students/${student.id}`)
    },
    sendMessage(student) {
      this.selectedStudent = student
      this.showMessageModal = true
    },
    sendMessageToStudent() {
      console.log('Sending message to', this.selectedStudent?.name, ':', this.messageContent)
      this.closeMessageModal()
    },
    moreOptions(student) {
      console.log('More options for', student.name)
    },
    exportData() {
      console.log('Exporting student data...')
    },
    // 搜索学生 - 直接调用API搜索
    async searchStudents() {
      const searchKey = this.searchExistingStudent.trim()
      if (!searchKey) {
        this.searchResults = []
        return
      }
      
      this.searching = true
      console.log('开始搜索学生，关键词:', searchKey)
      
      try {
        // 直接调用API搜索学生
        const response = await studentApi.getStudents({
          search: searchKey
        })
        
        console.log('搜索API响应:', response)
        
        // 处理API响应
        let data = response.data
        let results = []
        
        // 处理不同的响应格式
        if (Array.isArray(data)) {
          results = data
        } else if (data && Array.isArray(data.results)) {
          results = data.results
        } else if (data && Array.isArray(data.data)) {
          results = data.data
        } else {
          results = []
        }
        
        console.log('API返回的搜索结果:', results)
        
        // 转换为搜索结果所需的格式
        this.searchResults = results.map(student => ({
          id: student.id,
          name: student.student_name || student.username,
          studentId: student.student_no || '',
          currentClass: student.class_name || '未分配班级'
        }))
        
        console.log('最终搜索结果:', this.searchResults)
        
        // 如果搜索结果为空，显示提示信息
        if (this.searchResults.length === 0) {
          this.showMessage('没有找到匹配的学生，请尝试其他关键词', 'info')
        }
      } catch (error) {
        console.error('搜索学生失败:', error)
        this.showMessage('搜索学生失败，请稍后重试', 'error')
        this.searchResults = []
      } finally {
        this.searching = false
      }
    },
    
    // 切换学生选择状态
    toggleStudentSelection(studentId) {
      const index = this.selectedStudents.indexOf(studentId)
      if (index > -1) {
        this.selectedStudents.splice(index, 1)
      } else {
        this.selectedStudents.push(studentId)
      }
    },
    
    // 全选/取消全选
    selectAllStudents() {
      if (this.selectedStudents.length === this.searchResults.length) {
        this.selectedStudents = []
      } else {
        this.selectedStudents = this.searchResults.map(s => s.id)
      }
    },
    
    // 分配学生到班级
    async assignStudentsToClass() {
      if (this.selectedStudents.length === 0) {
        this.showMessage('请选择要分配的学生', 'warning')
        return
      }
      
      if (!this.assigningClassId) {
        this.showMessage('请选择班级', 'warning')
        return
      }
      
      this.assigning = true
      try {
        // 调用真实API更新学生班级
        const selectedClass = this.classes.find(cls => cls.id === parseInt(this.assigningClassId))
        const className = selectedClass ? selectedClass.name : '未知班级'
        
        // 使用updateStudent方法逐个更新学生的班级
        let successCount = 0
        const errorMessages = []
        
        for (const studentId of this.selectedStudents) {
          try {
            await studentApi.updateStudent(studentId, {
              class_id: this.assigningClassId
            })
            successCount++
          } catch (error) {
            console.error(`更新学生${studentId}失败:`, error)
            errorMessages.push(`学生ID ${studentId} 更新失败`)
          }
        }
        
        // 显示结果消息
        if (successCount > 0) {
          this.showMessage(`成功分配${successCount}名学生到班级`, 'success')
        }
        
        if (errorMessages.length > 0) {
          this.showMessage(`${errorMessages.length}名学生分配失败，请检查网络或学生信息`, 'error')
          console.error('分配失败详情:', errorMessages)
        }
        
        this.closeModal()
        
        // 刷新学生列表，获取最新数据
        await this.loadStudents()
        
        console.log('学生分配到班级操作完成', {
          totalSelected: this.selectedStudents.length,
          successCount: successCount,
          classId: this.assigningClassId,
          className: className
        })
      } catch (error) {
        console.error('分配学生失败:', error)
        this.showMessage('分配学生失败，请稍后重试', 'error')
        this.closeModal()
      } finally {
        this.assigning = false
      }
    },
    
    // 显示消息提示
    showMessage(text, type) {
      this.message = text
      this.messageType = type
      setTimeout(() => {
        this.message = ''
        this.messageType = ''
      }, 3000)
    },
    
    // 关闭模态框
    closeModal() {
      this.showAddModal = false
      // 重置搜索和选择状态
      this.searchExistingStudent = ''
      this.searchResults = []
      this.selectedStudents = []
      this.assigningClassId = ''
      this.searching = false
      this.assigning = false
    },
    closeMessageModal() {
      this.showMessageModal = false
      this.selectedStudent = null
      this.messageContent = ''
    }
  },
  computed: {
    filteredStudents() {
      let result = [...this.students]

      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        result = result.filter(
          s =>
            s.name.toLowerCase().includes(query) ||
            s.studentId.toLowerCase().includes(query)
        )
      }

      if (this.classFilter !== 'all') {
        result = result.filter(s => s.classId === parseInt(this.classFilter))
      }

      if (this.statusFilter !== 'all') {
        result = result.filter(s => s.status === this.statusFilter)
      }

      switch (this.sortBy) {
        case 'progress':
          result.sort((a, b) => b.progress - a.progress)
          break
        case 'score':
          result.sort((a, b) => b.score - a.score)
          break
        case 'activity':
          result.sort((a, b) => new Date(b.lastActive) - new Date(a.lastActive))
          break
        case 'name':
        default:
          result.sort((a, b) => a.name.localeCompare(b.name))
      }

      return result
    },
    totalPages() {
      return Math.ceil(this.filteredStudents.length / this.pageSize)
    },
    averageProgress() {
      const total = this.students.reduce((sum, s) => sum + s.progress, 0)
      return this.students.length > 0 ? Math.round(total / this.students.length) : 0
    },
    averageScore() {
      const total = this.students.reduce((sum, s) => sum + s.score, 0)
      return this.students.length > 0 ? Math.round(total / this.students.length) : 0
    },
    activeStudents() {
      return this.students.filter(s => s.status === 'active').length
    }
  }
}
</script>

<style scoped>
/* 全局动画定义 */
@keyframes spin {
  to { transform: rotate(360deg); }
}

.student-management {
  padding: 24px;
  background: #f8fafc;
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-left h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.header-left p {
  color: #64748b;
  margin: 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-secondary {
  background: white;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #f1f5f9;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-item {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
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

.stat-icon.blue {
  background: #dbeafe;
}

.stat-icon.green {
  background: #dcfce7;
}

.stat-icon.purple {
  background: #f3e8ff;
}

.stat-icon.orange {
  background: #ffedd5;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-box .search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
}

.search-box input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  background: white;
}

.search-box input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-options {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-options select {
  padding: 10px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.view-toggle {
  display: flex;
  background: white;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.view-btn {
  padding: 10px 14px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
}

.view-btn.active {
  background: #3b82f6;
  color: white;
}

.students-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.student-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.student-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.student-header {
  padding: 20px 20px 0;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.student-avatar {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: 600;
}

.student-avatar.small {
  width: 36px;
  height: 36px;
  font-size: 14px;
  border-radius: 8px;
}

.student-status {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.student-status.active {
  background: #dcfce7;
  color: #16a34a;
}

.student-status.inactive {
  background: #fef3c7;
  color: #d97706;
}

.student-status.completed {
  background: #dbeafe;
  color: #2563eb;
}

.student-body {
  padding: 16px 20px;
}

.student-body h3 {
  margin: 0 0 4px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.student-id {
  color: #64748b;
  font-size: 13px;
  margin: 0 0 4px 0;
}

.student-class {
  color: #3b82f6;
  font-size: 13px;
  margin: 0 0 16px 0;
}

.student-stats {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.mini-stat {
  flex: 1;
  text-align: center;
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
}

.mini-value {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.mini-label {
  font-size: 11px;
  color: #64748b;
}

.progress-mini {
  margin-bottom: 16px;
}

.progress-bar {
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 6px;
}

.progress-bar.small {
  height: 6px;
  width: 80px;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.progress-label {
  font-size: 12px;
  color: #64748b;
}

.student-meta {
  font-size: 12px;
  color: #94a3b8;
}

.students-table {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.students-table table {
  width: 100%;
  border-collapse: collapse;
}

.students-table th,
.students-table td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
}

.students-table th {
  background: #f8fafc;
  font-weight: 600;
  color: #475569;
  font-size: 13px;
}

.students-table td {
  color: #1e293b;
  font-size: 14px;
}

.students-table tbody tr {
  cursor: pointer;
  transition: background 0.2s;
}

.students-table tbody tr:hover {
  background: #f8fafc;
}

.student-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.score-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 13px;
}

.score-badge.excellent {
  background: #dcfce7;
  color: #16a34a;
}

.score-badge.good {
  background: #dbeafe;
  color: #2563eb;
}

.score-badge.average {
  background: #fef3c7;
  color: #d97706;
}

.score-badge.poor {
  background: #fee2e2;
  color: #dc2626;
}

.status-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.table-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 8px;
  border: none;
  background: #f1f5f9;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #e2e8f0;
}

.action-btn.small {
  padding: 6px;
  font-size: 14px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

.page-btn {
  padding: 10px 20px;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #f1f5f9;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #64748b;
  font-size: 14px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  color: #1e293b;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f1f5f9;
  border-radius: 8px;
  cursor: pointer;
  font-size: 20px;
  color: #64748b;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
}

.form-group input:focus,
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

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
</style>

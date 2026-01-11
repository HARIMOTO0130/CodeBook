<template>
  <div class="teacher-dashboard">
    <!-- 首次登录引导模态框 -->
    <div v-if="showProfileGuide" class="profile-guide-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h2>🎓 完善教师资料</h2>
          <button class="close-btn" @click="closeProfileGuide">×</button>
        </div>
        <div class="modal-body">
          <p>欢迎使用 CodeBook+ 教师端！为了更好地使用系统功能，建议您完善教师资料。</p>
          <ul>
            <li>教师编号</li>
            <li>联系电话</li>
            <li>所属部门</li>
            <li>教师简介</li>
          </ul>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeProfileGuide">稍后完善</button>
          <button class="btn btn-primary" @click="goToSettings">前往完善</button>
        </div>
      </div>
    </div>

    <!-- 欢迎区域 -->
    <div class="welcome-section">
      <div class="welcome-content">
        <div class="welcome-text">
          <h1>{{ greeting }}，{{ teacherName }}！</h1>
          <p>今天是 {{ currentDate }}，您有 <span class="highlight">{{ stats.pendingTasks }}</span> 个待处理任务</p>
        </div>
        <div class="quick-actions">
          <button class="quick-btn primary" @click="createClass">
            <span>➕</span> 创建班级
          </button>
          <button class="quick-btn secondary" @click="createAssignment">
            <span>📝</span> 发布作业
          </button>
          <button class="quick-btn tertiary" @click="uploadResource">
            <span>📚</span> 上传资源
          </button>
        </div>
      </div>
      <div class="welcome-decoration">
        <div class="decoration-circle"></div>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon blue">👥</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.totalStudents }}</span>
          <span class="stat-label">学生总数</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon green">📚</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.totalClasses }}</span>
          <span class="stat-label">班级数量</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple">📝</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.pendingReviews }}</span>
          <span class="stat-label">待批改作业</span>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange">📊</div>
        <div class="stat-info">
          <span class="stat-value">{{ stats.avgProgress }}%</span>
          <span class="stat-label">平均完成率</span>
        </div>
      </div>
    </div>

    <!-- 主要内容区 -->
    <div class="dashboard-content">
      <!-- 左侧 - 待办事项和近期活动 -->
      <div class="content-left">
        <!-- 作业管理 -->
        <div class="card todo-card">
          <div class="card-header">
            <h2>作业管理</h2>
            <button class="view-all-btn" @click="goToAssignments">查看全部 →</button>
          </div>
          <div class="todo-list">
            <div 
              v-for="todo in todos" 
              :key="todo.id" 
              class="todo-item"
              :class="{ completed: todo.completed }"
            >
              <div class="todo-checkbox" @click="toggleTodo(todo)">
                <span v-if="todo.completed">✅</span>
                <span v-else>📝</span>
              </div>
              <div class="todo-content">
                <p class="todo-title">{{ todo.title }}</p>
                <span class="todo-meta">{{ todo.class }} · {{ todo.time }}</span>
              </div>
              <span class="todo-priority" :class="todo.priority">{{ todo.priority }}</span>
            </div>
          </div>
        </div>

        <!-- 近期活动 -->
        <div class="card activity-card">
          <div class="card-header">
            <h2>近期活动</h2>
            <span class="activity-filter">
              <select v-model="activityFilter">
                <option value="all">全部</option>
                <option value="homework">作业</option>
                <option value="class">班级</option>
                <option value="resource">资源</option>
              </select>
            </span>
          </div>
          <div class="activity-list">
            <div 
              v-for="activity in filteredActivities" 
              :key="activity.id" 
              class="activity-item"
            >
              <div class="activity-icon">{{ activity.icon }}</div>
              <div class="activity-content">
                <p class="activity-text">{{ activity.text }}</p>
                <span class="activity-time">{{ activity.time }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧 - 班级概览和快捷入口 -->
      <div class="content-right">
        <!-- 班级概览 -->
        <div class="card class-overview-card">
          <div class="card-header">
            <h2>班级概览</h2>
            <router-link to="/teacher/classes" class="view-all-btn">管理班级 →</router-link>
          </div>
          <div class="class-list">
            <div 
              v-for="classItem in classes" 
              :key="classItem.id" 
              class="class-item"
              @click="goToClass(classItem.id)"
            >
              <div class="class-info">
                <div class="class-avatar" :style="{ background: classItem.color }">
                  {{ (classItem.name || '班').charAt(0) }}
                </div>
                <div class="class-details">
                  <h4>{{ classItem.name }}</h4>
                  <p>{{ classItem.studentCount }} 名学生 · {{ classItem.course }}</p>
                </div>
              </div>
              <div class="class-progress">
                <div class="progress-ring">
                  <svg viewBox="0 0 36 36">
                    <path
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      stroke="#e5e7eb"
                      stroke-width="3"
                    />
                    <path
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                      fill="none"
                      :stroke="classItem.color"
                      stroke-width="3"
                      :stroke-dasharray="`${classItem.progress}, 100`"
                    />
                  </svg>
                  <span class="progress-text">{{ classItem.progress }}%</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 快捷功能 -->
        <div class="card quick-features-card">
          <div class="card-header">
            <h2>快捷功能</h2>
          </div>
          <div class="quick-features">
            <div 
              v-for="feature in quickFeatures" 
              :key="feature.id"
              class="quick-feature-item"
              @click="goToFeature(feature.path)"
            >
              <div class="feature-icon">{{ feature.icon }}</div>
              <span class="feature-name">{{ feature.name }}</span>
            </div>
          </div>
        </div>

        <!-- 学习进度提醒 -->
        <div class="card progress-alert-card">
          <div class="card-header">
            <h2>进度提醒</h2>
          </div>
          <div class="alert-list">
            <div 
              v-for="alert in progressAlerts" 
              :key="alert.id" 
              class="alert-item"
            >
              <div class="alert-icon" :class="alert.type">
                {{ alert.type === 'warning' ? '⚠️' : '📢' }}
              </div>
              <div class="alert-content">
                <p>{{ alert.message }}</p>
                <span class="alert-class">{{ alert.className }}</span>
              </div>
              <button class="alert-action" @click="handleAlert(alert)">
                查看
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { classApi } from '../api/class'
import { assignmentApi } from '../api/assignment'
import { analyticsApi } from '../api/analytics'
import { notificationApi } from '../api/notification'
import { teacherApi } from '../api/teacher'

export default {
  name: 'TeacherDashboard',
  setup() {
    const router = useRouter()
    const activityFilter = ref('all')
    const loading = ref(false)
    const teacherName = ref('老师')
    const showProfileGuide = ref(false)

    const currentDate = computed(() => {
      const now = new Date()
      const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
      return now.toLocaleDateString('zh-CN', options)
    })

    const greeting = computed(() => {
      const hour = new Date().getHours()
      if (hour < 6) return '凌晨好'
      if (hour < 9) return '早上好'
      if (hour < 12) return '上午好'
      if (hour < 14) return '中午好'
      if (hour < 18) return '下午好'
      if (hour < 22) return '晚上好'
      return '夜深了'
    })

    const stats = ref({
      totalStudents: 0,
      totalClasses: 0,
      pendingReviews: 0,
      avgProgress: 0,
      pendingTasks: 0
    })

    const todos = ref([])
    const activities = ref([])

    const filteredActivities = computed(() => {
      if (activityFilter.value === 'all') return activities.value
      return activities.value.filter(a => a.type === activityFilter.value)
    })

    const classes = ref([])

    // 从API加载数据
    const loadData = async () => {
      loading.value = true
      try {
        // 获取当前用户信息（从localStorage和API双重获取，确保数据最新）
        let userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
        
        // 调用教师信息API获取最新数据
        try {
          const teacherRes = await teacherApi.getTeacherInfo()
          if (teacherRes.data) {
            userInfo = { ...userInfo, ...teacherRes.data }
            // 更新localStorage
            localStorage.setItem('userInfo', JSON.stringify(userInfo))
          }
        } catch (e) {
          console.log('获取教师信息失败，使用localStorage数据:', e)
        }
        
        // 确保teacherName始终有值，即使没有完整的姓名信息
        if (userInfo.username) {
          // 优先使用 last_name + first_name，如果没有则使用 username
          if (userInfo.last_name && userInfo.first_name) {
            teacherName.value = `${userInfo.last_name}${userInfo.first_name}老师`
          } else if (userInfo.last_name) {
            teacherName.value = `${userInfo.last_name}老师`
          } else {
            teacherName.value = `${userInfo.username}老师`
          }
        } else if (userInfo.last_name) {
          teacherName.value = `${userInfo.last_name}老师`
        } else {
          // 如果没有任何姓名信息，使用默认值
          teacherName.value = '李华老师'
        }
        
        console.log('教师信息:', userInfo)
        console.log('显示的教师姓名:', teacherName.value)
        
        // 检查教师资料是否完整，如果不完整且是首次登录则显示引导
        const profileCheckKey = 'profile_checked'
        const isProfileChecked = localStorage.getItem(profileCheckKey)
        const isProfileComplete = userInfo.teacher_number && userInfo.department
        
        if (!isProfileChecked && !isProfileComplete) {
          showProfileGuide.value = true
        }

        // 加载统计信息（概览）
        const analyticsRes = await analyticsApi.getOverview()
        if (analyticsRes.data) {
          // 暂时不使用API返回的班级数量，而是从实际班级列表计算
          // stats.value.totalClasses = analyticsRes.data.total_classes || 0
          stats.value.totalStudents = analyticsRes.data.total_students || 0
        }
        
        // 加载仪表盘统计数据（包含待批改作业数、平均完成率等）
        const dashboardRes = await analyticsApi.getDashboardStats()
        if (dashboardRes.data) {
          stats.value.pendingReviews = dashboardRes.data.pending_reviews || 0
          stats.value.avgProgress = dashboardRes.data.avg_progress || 0
          // 计算待处理任务数：待批改作业 + 待发布作业
          stats.value.pendingTasks = (dashboardRes.data.pending_reviews || 0) + (dashboardRes.data.pending_homeworks || 0)
        }

        // 加载班级列表
        const classesRes = await classApi.getClasses()
        // 处理不同的数据格式
        let classesData = []
        if (classesRes.data) {
          if (Array.isArray(classesRes.data)) {
            classesData = classesRes.data
          } else if (Array.isArray(classesRes.data.results)) {
            classesData = classesRes.data.results
          }
        }
        
        if (classesData.length > 0) {
          classes.value = classesData.map(cls => ({
            id: cls.id,
            name: cls.name,
            studentCount: cls.student_count || 0,
            course: cls.major || '',
            progress: 0, // 可以从analytics获取
            color: getClassColor(cls.id)
          }))
          
          // 直接从班级列表计算班级数量，确保与班级管理页面一致
          stats.value.totalClasses = classesData.length
          
          // 加载进度提醒
          progressAlerts.value = []
          for (const cls of classesData) {
            try {
              const analyticsRes = await classApi.getClassAnalytics(cls.id)
              // 可以根据分析数据生成提醒
            } catch (e) {
              console.log('获取班级分析失败:', e)
            }
          }
        } else {
          // 如果没有班级数据，班级数量设为0
          stats.value.totalClasses = 0
        }
        
        // 加载待办事项（从作业中获取即将截止的作业）
        try {
          const assignmentsRes = await assignmentApi.getAssignments()
          if (assignmentsRes.data && Array.isArray(assignmentsRes.data)) {
            const now = new Date()
            todos.value = assignmentsRes.data
              .filter(a => {
                const dueDate = new Date(a.due_date)
                return dueDate > now && dueDate - now < 7 * 24 * 60 * 60 * 1000 // 7天内截止
              })
              .slice(0, 5)
              .map(a => ({
                id: a.id,
                title: `批改「${a.title}」作业`,
                class: a.classes?.[0]?.name || '',
                time: formatDueTime(a.due_date),
                priority: getPriority(a.due_date),
                completed: false
              }))
          }
        } catch (e) {
          console.log('加载待办事项失败:', e)
        }
        
        // 加载活动记录（从通知中获取）
        try {
          const notificationsRes = await notificationApi.getNotifications({ limit: 5 })
          if (notificationsRes.data && Array.isArray(notificationsRes.data)) {
            activities.value = notificationsRes.data.map(n => ({
              id: n.id,
              icon: getActivityIcon(n.type),
              text: n.title,
              type: n.type,
              time: formatTimeAgo(n.created_at)
            }))
          }
        } catch (e) {
          console.log('加载活动记录失败:', e)
        }
      } catch (error) {
        console.error('加载数据失败:', error)
      } finally {
        loading.value = false
      }
    }
    
    const formatDueTime = (dueDateStr) => {
      const dueDate = new Date(dueDateStr)
      const now = new Date()
      const diff = dueDate - now
      const days = Math.floor(diff / (24 * 60 * 60 * 1000))
      if (days === 0) return '今天截止'
      if (days === 1) return '明天截止'
      return `${days}天后截止`
    }
    
    const getPriority = (dueDateStr) => {
      const dueDate = new Date(dueDateStr)
      const now = new Date()
      const diff = dueDate - now
      const hours = diff / (60 * 60 * 1000)
      if (hours < 24) return 'urgent'
      if (hours < 72) return 'high'
      return 'medium'
    }
    
    const getActivityIcon = (type) => {
      const icons = {
        'assignment': '📝',
        'system': '⚙️',
        'reminder': '📢',
        'feedback': '💬'
      }
      return icons[type] || '📢'
    }
    
    const formatTimeAgo = (dateStr) => {
      const date = new Date(dateStr)
      const now = new Date()
      const diff = now - date
      const minutes = Math.floor(diff / (60 * 1000))
      const hours = Math.floor(diff / (60 * 60 * 1000))
      const days = Math.floor(diff / (24 * 60 * 60 * 1000))
      if (minutes < 60) return `${minutes}分钟前`
      if (hours < 24) return `${hours}小时前`
      return `${days}天前`
    }

    const getClassColor = (id) => {
      const colors = [
        'linear-gradient(135deg, #667eea, #764ba2)',
        'linear-gradient(135deg, #f093fb, #f5576c)',
        'linear-gradient(135deg, #4facfe, #00f2fe)',
        'linear-gradient(135deg, #43e97b, #38f9d7)',
        'linear-gradient(135deg, #fa709a, #fee140)',
      ]
      return colors[id % colors.length]
    }

    onMounted(() => {
      loadData()
    })

    const quickFeatures = [
      { id: 1, name: '学生管理', icon: '👥', path: '/teacher/students' },
      { id: 2, name: '作业批改', icon: '✏️', path: '/teacher/assignments' },
      { id: 3, name: '资源上传', icon: '☁️', path: '/teacher/resources' },
      { id: 4, name: '数据分析', icon: '📈', path: '/teacher/analytics' },
      { id: 5, name: '学习报告', icon: '📊', path: '/teacher/reports' },
      { id: 6, name: '发送通知', icon: '📢', path: '/teacher/notifications' },
      { id: 7, name: '个人设置', icon: '⚙️', path: '/teacher/settings' },
    ]

    const progressAlerts = ref([])

    const toggleTodo = (todo) => {
      todo.completed = !todo.completed
    }

    const createClass = () => {
      router.push('/teacher/classes?action=create')
    }

    const createAssignment = () => {
      router.push('/teacher/assignments/create')
    }

    const uploadResource = () => {
      router.push('/teacher/resources?action=upload')
    }

    const goToClass = (classId) => {
      router.push(`/teacher/classes/${classId}`)
    }

    const goToFeature = (path) => {
      router.push(path)
    }

    const handleAlert = (alert) => {
      console.log('处理提醒:', alert)
    }

    const goToAssignments = () => {
      router.push('/teacher/assignments')
    }

    // 关闭引导模态框
    const closeProfileGuide = () => {
      showProfileGuide.value = false
      // 标记已检查过资料状态，避免每次都显示
      localStorage.setItem('profile_checked', 'true')
    }

    // 前往设置页面
    const goToSettings = () => {
      showProfileGuide.value = false
      localStorage.setItem('profile_checked', 'true')
      router.push('/teacher/settings')
    }

    return {
      activityFilter,
      currentDate,
      greeting,
      teacherName,
      stats,
      todos,
      activities,
      filteredActivities,
      classes,
      quickFeatures,
      progressAlerts,
      loading,
      toggleTodo,
      createClass,
      createAssignment,
      uploadResource,
      goToClass,
      goToFeature,
      handleAlert,
      goToAssignments,
      loadData,
      showProfileGuide,
      closeProfileGuide,
      goToSettings
    }
  }
}
</script>

<style scoped>
.teacher-dashboard {
  max-width: 1400px;
  margin: 0 auto;
}

/* 欢迎区域 */
.welcome-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  padding: 40px;
  margin-bottom: 32px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: relative;
  overflow: hidden;
  color: white;
}

.welcome-content {
  position: relative;
  z-index: 1;
}

.welcome-text h1 {
  font-size: 32px;
  font-weight: 700;
  margin: 0 0 12px 0;
}

.welcome-text p {
  font-size: 16px;
  opacity: 0.9;
  margin: 0;
}

.highlight {
  font-weight: 700;
  color: #fef08a;
}

.quick-actions {
  display: flex;
  gap: 16px;
  margin-top: 24px;
}

.quick-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 24px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.quick-btn.primary {
  background: white;
  color: #667eea;
}

.quick-btn.secondary {
  background: rgba(255,255,255,0.2);
  color: white;
  border: 1px solid rgba(255,255,255,0.3);
}

.quick-btn.tertiary {
  background: rgba(255,255,255,0.2);
  color: white;
  border: 1px solid rgba(255,255,255,0.3);
}

.quick-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}

.welcome-decoration {
  position: absolute;
  right: 40px;
  top: 50%;
  transform: translateY(-50%);
}

.decoration-circle {
  width: 200px;
  height: 200px;
  background: rgba(255,255,255,0.1);
  border-radius: 50%;
}

/* 统计卡片 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(0,0,0,0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
}

.stat-icon.blue { background: linear-gradient(135deg, #667eea20, #764ba220); }
.stat-icon.green { background: linear-gradient(135deg, #43e97b20, #38f9d720); }
.stat-icon.purple { background: linear-gradient(135deg, #f093fb20, #f5576c20); }
.stat-icon.orange { background: linear-gradient(135deg, #fa709a20, #fee14020); }

.stat-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #1f2937;
}

.stat-label {
  font-size: 14px;
  color: #6b7280;
}

.stat-trend {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
}

.stat-trend.up {
  background: #dcfce7;
  color: #16a34a;
}

.stat-trend.down {
  background: #fee2e2;
  color: #dc2626;
}

/* 内容区 */
.dashboard-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

.content-left,
.content-right {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 卡片通用样式 */
.card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}

.view-all-btn {
  background: none;
  border: none;
  color: #667eea;
  font-size: 14px;
  cursor: pointer;
  font-weight: 500;
}

.view-all-btn:hover {
  text-decoration: underline;
}

/* 待办事项 */
.todo-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.todo-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 12px;
  transition: all 0.3s;
}

.todo-item:hover {
  background: #f3f4f6;
}

.todo-item.completed {
  opacity: 0.6;
}

.todo-item.completed .todo-title {
  text-decoration: line-through;
}

.todo-checkbox {
  font-size: 20px;
  cursor: pointer;
}

.todo-content {
  flex: 1;
}

.todo-title {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #374151;
  font-weight: 500;
}

.todo-meta {
  font-size: 12px;
  color: #9ca3af;
}

.todo-priority {
  font-size: 11px;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 600;
  text-transform: uppercase;
}

.todo-priority.urgent { background: #fee2e2; color: #dc2626; }
.todo-priority.high { background: #fef3c7; color: #d97706; }
.todo-priority.medium { background: #dbeafe; color: #2563eb; }
.todo-priority.low { background: #f3f4f6; color: #6b7280; }

/* 近期活动 */
.activity-filter select {
  padding: 6px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 13px;
  color: #374151;
  cursor: pointer;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f3f4f6;
}

.activity-item:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.activity-icon {
  width: 40px;
  height: 40px;
  background: #f3f4f6;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.activity-content {
  flex: 1;
}

.activity-text {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #374151;
}

.activity-time {
  font-size: 12px;
  color: #9ca3af;
}

/* 班级概览 */
.class-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.class-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f9fafb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.class-item:hover {
  background: #f3f4f6;
  transform: translateX(4px);
}

.class-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.class-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
  font-weight: 700;
}

.class-details h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
  color: #1f2937;
}

.class-details p {
  margin: 0;
  font-size: 13px;
  color: #6b7280;
}

.progress-ring {
  position: relative;
  width: 48px;
  height: 48px;
}

.progress-ring svg {
  transform: rotate(-90deg);
}

.progress-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 11px;
  font-weight: 600;
  color: #374151;
}

/* 快捷功能 */
.quick-features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.quick-feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px;
  background: #f9fafb;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-feature-item:hover {
  background: linear-gradient(135deg, #667eea10, #764ba210);
  transform: translateY(-2px);
}

.feature-icon {
  font-size: 28px;
}

.feature-name {
  font-size: 12px;
  color: #374151;
  font-weight: 500;
}

/* 进度提醒 */
.alert-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: #fefce8;
  border-radius: 10px;
  border-left: 4px solid #eab308;
}

.alert-item.warning {
  background: #fefce8;
  border-color: #eab308;
}

.alert-item.info {
  background: #eff6ff;
  border-color: #3b82f6;
}

.alert-icon {
  font-size: 20px;
}

.alert-content {
  flex: 1;
}

.alert-content p {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #374151;
}

.alert-class {
  font-size: 12px;
  color: #6b7280;
}

.alert-action {
  padding: 8px 16px;
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  font-size: 13px;
  color: #374151;
  cursor: pointer;
  transition: all 0.3s;
}

.alert-action:hover {
  background: #667eea;
  color: white;
  border-color: #667eea;
}

/* 响应式 */
@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .dashboard-content {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .welcome-section {
    padding: 24px;
  }
  
  .welcome-text h1 {
    font-size: 24px;
  }
  
  .quick-actions {
    flex-direction: column;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .quick-features {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* 首次登录引导模态框样式 */
.profile-guide-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background-color: white;
  border-radius: 16px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.modal-header h2 {
  margin: 0;
  font-size: 24px;
  color: #1f2937;
}

.close-btn {
  background: none;
  border: none;
  font-size: 32px;
  cursor: pointer;
  color: #6b7280;
  padding: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: #f3f4f6;
}

.modal-body {
  padding: 24px;
}

.modal-body p {
  font-size: 16px;
  line-height: 1.6;
  color: #4b5563;
  margin-bottom: 20px;
}

.modal-body ul {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.modal-body li {
  padding: 8px 0;
  font-size: 15px;
  color: #374151;
  display: flex;
  align-items: center;
  gap: 8px;
}

.modal-body li::before {
  content: '✓';
  color: #10b981;
  font-weight: bold;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e5e7eb;
  background-color: #f9fafb;
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

.btn-secondary {
  background-color: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background-color: #e5e7eb;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}
</style>

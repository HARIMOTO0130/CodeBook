<template>
  <div class="settings-page">
    <div class="page-header">
      <div class="header-left">
        <h1>个人中心</h1>
        <p>管理您的账户信息和偏好设置</p>
      </div>
    </div>

    <div class="settings-layout">
      <aside class="settings-sidebar">
        <nav class="settings-nav">
          <a
            v-for="tab in tabs"
            :key="tab.id"
            class="nav-item"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            <span class="nav-icon">{{ tab.icon }}</span>
            <span class="nav-text">{{ tab.name }}</span>
          </a>
        </nav>
      </aside>

      <main class="settings-content">
        <div v-if="activeTab === 'profile'" class="settings-section">
          <div class="section-header">
            <h2>个人信息</h2>
            <p>管理您的个人资料和联系方式</p>
          </div>

          <div class="profile-card">
            <div class="avatar-section">
              <div class="avatar-wrapper">
                <img :src="profile.avatar || defaultAvatar" alt="头像" class="avatar" />
                <button class="avatar-edit-btn" @click="triggerAvatarUpload">
                  <span>📷</span>
                </button>
                <input
                  type="file"
                  ref="avatarInput"
                  style="display: none"
                  accept="image/*"
                  @change="handleAvatarChange"
                />
              </div>
              <div class="avatar-info">
                <h3>{{ profile.name }}</h3>
                <p>{{ profile.title }}</p>
              </div>
            </div>

            <form class="profile-form" @submit.prevent="saveProfile">
              <div class="form-row">
                <div class="form-group">
                  <label>姓名</label>
                  <input type="text" v-model="profile.name" />
                </div>
                <div class="form-group">
                  <label>职称</label>
                  <select v-model="profile.title">
                    <option value="">请选择职称</option>
                    <option value="教授">教授</option>
                    <option value="副教授">副教授</option>
                    <option value="讲师">讲师</option>
                    <option value="助理讲师">助理讲师</option>
                  </select>
                </div>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label>电子邮箱</label>
                  <input type="email" v-model="profile.email" />
                </div>
                <div class="form-group">
                  <label>联系电话</label>
                  <input type="tel" v-model="profile.phone" />
                </div>
              </div>

              <div class="form-group">
                <label>所属院系</label>
                <input type="text" v-model="profile.department" />
              </div>

              <div class="form-group">
                <label>个人简介</label>
                <textarea v-model="profile.bio" rows="4" placeholder="介绍一下您的教学背景和研究方向..."></textarea>
              </div>

              <div class="form-actions">
                <button type="submit" class="btn btn-primary">保存修改</button>
              </div>
            </form>
          </div>
        </div>

        <div v-if="activeTab === 'account'" class="settings-section">
          <div class="section-header">
            <h2>账户安全</h2>
            <p>管理您的密码和账户安全设置</p>
          </div>

          <div class="settings-card">
            <div class="setting-item">
              <div class="setting-info">
                <h3>修改密码</h3>
                <p>定期更换密码可以保护您的账户安全</p>
              </div>
              <button class="btn btn-secondary" @click="showPasswordModal = true">修改密码</button>
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h3>绑定手机</h3>
                <p>当前绑定: {{ profile.phone || '未绑定' }}</p>
              </div>
              <button class="btn btn-secondary">更换绑定</button>
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h3>绑定邮箱</h3>
                <p>当前绑定: {{ profile.email }}</p>
              </div>
              <button class="btn btn-secondary">更换绑定</button>
            </div>

            <div class="setting-item">
              <div class="setting-info">
                <h3>两步验证</h3>
                <p>增强账户安全性，建议开启</p>
              </div>
              <label class="switch">
                <input type="checkbox" v-model="security.twoFactor" />
                <span class="slider"></span>
              </label>
            </div>

            <div class="setting-item danger">
              <div class="setting-info">
                <h3>注销账户</h3>
                <p>注销后您的所有数据将被永久删除</p>
              </div>
              <button class="btn btn-danger">注销账户</button>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'notifications'" class="settings-section">
          <div class="section-header">
            <h2>通知设置</h2>
            <p>控制您接收到的通知类型和方式</p>
          </div>

          <div class="settings-card">
            <div class="setting-group">
              <h3>邮件通知</h3>
              <div class="setting-item" v-for="item in notificationSettings.email" :key="item.key">
                <div class="setting-info">
                  <h4>{{ item.title }}</h4>
                  <p>{{ item.description }}</p>
                </div>
                <label class="switch">
                  <input type="checkbox" v-model="item.enabled" />
                  <span class="slider"></span>
                </label>
              </div>
            </div>

            <div class="setting-group">
              <h3>站内通知</h3>
              <div class="setting-item" v-for="item in notificationSettings.inApp" :key="item.key">
                <div class="setting-info">
                  <h4>{{ item.title }}</h4>
                  <p>{{ item.description }}</p>
                </div>
                <label class="switch">
                  <input type="checkbox" v-model="item.enabled" />
                  <span class="slider"></span>
                </label>
              </div>
            </div>

            <div class="setting-group">
              <h3>通知时间</h3>
              <div class="setting-item">
                <div class="setting-info">
                  <h4>免打扰时间</h4>
                  <p>在设定时间段内不发送通知</p>
                </div>
                <div class="time-range">
                  <input type="time" v-model="notificationSettings.doNotDisturb.start" />
                  <span>至</span>
                  <input type="time" v-model="notificationSettings.doNotDisturb.end" />
                </div>
              </div>
            </div>

            <div class="form-actions">
              <button class="btn btn-primary" @click="saveNotificationSettings">保存设置</button>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'teaching'" class="settings-section">
          <div class="section-header">
            <h2>教学偏好</h2>
            <p>设置您的教学偏好和默认选项</p>
          </div>

          <div class="settings-card">
            <div class="setting-group">
              <h3>默认设置</h3>
              <div class="form-group">
                <label>默认班级视图</label>
                <select v-model="teachingPreferences.defaultClassView">
                  <option value="grid">网格视图</option>
                  <option value="list">列表视图</option>
                  <option value="table">表格视图</option>
                </select>
              </div>

              <div class="form-group">
                <label>每页显示学生数</label>
                <select v-model="teachingPreferences.studentsPerPage">
                  <option value="10">10 人</option>
                  <option value="20">20 人</option>
                  <option value="50">50 人</option>
                  <option value="100">100 人</option>
                </select>
              </div>

              <div class="form-group">
                <label>默认作业截止时间</label>
                <select v-model="teachingPreferences.defaultDueTime">
                  <option value="23:59">当天 23:59</option>
                  <option value="18:00">当天 18:00</option>
                  <option value="next-day">次日 23:59</option>
                  <option value="week">一周后</option>
                </select>
              </div>
            </div>

            <div class="setting-group">
              <h3>数据分析</h3>
              <div class="setting-item">
                <div class="setting-info">
                  <h4>自动生成周报</h4>
                  <p>每周自动生成班级学习数据报告</p>
                </div>
                <label class="switch">
                  <input type="checkbox" v-model="teachingPreferences.autoWeeklyReport" />
                  <span class="slider"></span>
                </label>
              </div>

              <div class="setting-item">
                <div class="setting-info">
                  <h4>学习预警提醒</h4>
                  <p>当学生进度落后时自动发送提醒</p>
                </div>
                <label class="switch">
                  <input type="checkbox" v-model="teachingPreferences.progressAlert" />
                  <span class="slider"></span>
                </label>
              </div>
            </div>

            <div class="form-actions">
              <button class="btn btn-primary" @click="saveTeachingPreferences">保存偏好</button>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'appearance'" class="settings-section">
          <div class="section-header">
            <h2>界面设置</h2>
            <p>自定义您的界面外观和布局</p>
          </div>

          <div class="settings-card">
            <div class="setting-group">
              <h3>主题</h3>
              <div class="theme-options">
                <div
                  class="theme-option"
                  :class="{ active: appearance.theme === 'light' }"
                  @click="appearance.theme = 'light'"
                >
                  <div class="theme-preview light"></div>
                  <span>浅色主题</span>
                </div>
                <div
                  class="theme-option"
                  :class="{ active: appearance.theme === 'dark' }"
                  @click="appearance.theme = 'dark'"
                >
                  <div class="theme-preview dark"></div>
                  <span>深色主题</span>
                </div>
                <div
                  class="theme-option"
                  :class="{ active: appearance.theme === 'auto' }"
                  @click="appearance.theme = 'auto'"
                >
                  <div class="theme-preview auto"></div>
                  <span>跟随系统</span>
                </div>
              </div>
            </div>

            <div class="setting-group">
              <h3>布局</h3>
              <div class="form-group">
                <label>侧边栏位置</label>
                <select v-model="appearance.sidebarPosition">
                  <option value="left">左侧</option>
                  <option value="right">右侧</option>
                </select>
              </div>

              <div class="form-group">
                <label>侧边栏宽度</label>
                <select v-model="appearance.sidebarWidth">
                  <option value="narrow">窄</option>
                  <option value="medium">中</option>
                  <option value="wide">宽</option>
                </select>
              </div>
            </div>

            <div class="form-actions">
              <button class="btn btn-primary" @click="saveAppearance">保存设置</button>
            </div>
          </div>
        </div>
      </main>
    </div>

    <div v-if="showPasswordModal" class="modal-overlay" @click.self="showPasswordModal = false">
      <div class="modal">
        <div class="modal-header">
          <h2>修改密码</h2>
          <button class="close-btn" @click="showPasswordModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>当前密码</label>
            <input type="password" v-model="passwordForm.current" placeholder="输入当前密码" />
          </div>
          <div class="form-group">
            <label>新密码</label>
            <input type="password" v-model="passwordForm.new" placeholder="输入新密码" />
          </div>
          <div class="form-group">
            <label>确认新密码</label>
            <input type="password" v-model="passwordForm.confirm" placeholder="再次输入新密码" />
          </div>
          <div class="password-strength" v-if="passwordForm.new">
            <div class="strength-bar">
              <div class="strength-fill" :style="{ width: passwordStrength + '%', background: passwordStrengthColor }"></div>
            </div>
            <span :style="{ color: passwordStrengthColor }">密码强度: {{ passwordStrengthText }}</span>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showPasswordModal = false">取消</button>
          <button class="btn btn-primary" @click="changePassword">确认修改</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../api/index'
import { teacherApi } from '../api/teacher'

export default {
  name: 'TeacherSettingsView',
  data() {
    return {
      activeTab: 'profile',
      showPasswordModal: false,
      defaultAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=teacher',
      tabs: [
        { id: 'profile', name: '个人信息', icon: '👤' },
        { id: 'account', name: '账户安全', icon: '🔐' },
        { id: 'notifications', name: '通知设置', icon: '🔔' },
        { id: 'teaching', name: '教学偏好', icon: '📚' },
        { id: 'appearance', name: '界面设置', icon: '🎨' }
      ],
      profile: {
        name: '',
        title: '',
        email: '',
        phone: '',
        department: '',
        bio: '',
        avatar: ''
      },
      security: {
        twoFactor: false
      },
      notificationSettings: {
        email: [
          { key: 'assignment-submission', title: '作业提交通知', description: '当学生提交作业时发送邮件', enabled: true },
          { key: 'student-message', title: '学生留言提醒', description: '当学生留言时发送邮件', enabled: true },
          { key: 'weekly-report', title: '周报推送', description: '每周发送班级学习数据报告', enabled: false },
          { key: 'system-update', title: '系统更新', description: '接收平台功能更新通知', enabled: true }
        ],
        inApp: [
          { key: 'deadline-reminder', title: '截止提醒', description: '作业截止前提醒学生', enabled: true },
          { key: 'progress-alert', title: '进度预警', description: '学生进度异常时提醒教师', enabled: true },
          { key: 'message-notification', title: '消息通知', description: '新消息即时提醒', enabled: true }
        ],
        doNotDisturb: {
          start: '22:00',
          end: '08:00'
        }
      },
      teachingPreferences: {
        defaultClassView: 'grid',
        studentsPerPage: '20',
        defaultDueTime: '23:59',
        autoWeeklyReport: true,
        progressAlert: true
      },
      appearance: {
        theme: 'light',
        sidebarPosition: 'left',
        sidebarWidth: 'medium'
      },
      passwordForm: {
        current: '',
        new: '',
        confirm: ''
      }
    }
  },
  mounted() {
    this.loadUserProfile()
    this.loadUserSettings()
  },
  computed: {
    passwordStrength() {
      const password = this.passwordForm.new
      if (!password) return 0
      let strength = 0
      if (password.length >= 8) strength += 25
      if (/[a-z]/.test(password)) strength += 25
      if (/[A-Z]/.test(password)) strength += 25
      if (/[0-9]/.test(password) || /[^a-zA-Z0-9]/.test(password)) strength += 25
      return strength
    },
    passwordStrengthColor() {
      if (this.passwordStrength <= 25) return '#ef4444'
      if (this.passwordStrength <= 50) return '#f59e0b'
      if (this.passwordStrength <= 75) return '#3b82f6'
      return '#10b981'
    },
    passwordStrengthText() {
      if (this.passwordStrength <= 25) return '弱'
      if (this.passwordStrength <= 50) return '一般'
      if (this.passwordStrength <= 75) return '较强'
      return '强'
    }
  },
  methods: {
    async loadUserProfile() {
      try {
        // 从后端API获取最新的教师信息
        const response = await teacherApi.getTeacherInfo()
        const userInfo = response.data
        
        // 保存到localStorage作为备份
        localStorage.setItem('user', JSON.stringify(userInfo))
        localStorage.setItem('username', userInfo.username)
        localStorage.setItem('userId', userInfo.id)
        if (userInfo.first_name) {
          localStorage.setItem('userFullName', userInfo.first_name)
        }
        
        // 合并数据到profile对象 - API现在返回所有字段
        this.profile = {
          ...this.profile,
          name: userInfo.first_name || userInfo.username,
          email: userInfo.email || '',
          phone: userInfo.phone || '',
          title: userInfo.title || '',
          department: userInfo.department || '',
          bio: userInfo.bio || '',
          avatar: userInfo.avatar || this.defaultAvatar
        }
        
        console.log('从API加载的用户信息:', this.profile)
      } catch (error) {
        console.error('从API加载用户信息失败:', error)
        
        // 如果API请求失败，从localStorage加载备份数据
        const userInfo = JSON.parse(localStorage.getItem('user') || '{}')
        const userFullName = localStorage.getItem('userFullName') || ''
        const username = localStorage.getItem('username') || ''
        const userId = localStorage.getItem('userId')
        
        // 优先级：userFullName > userInfo.first_name > userInfo.username > username
        // 确保用户设置的姓名优先显示，同时处理不同字段名
        this.profile = {
          ...this.profile,
          name: userFullName || userInfo.first_name || userInfo.username || username || '',
          email: userInfo.email || '',
          phone: userInfo.phone || '',
          title: userInfo.title || '',
          department: userInfo.department || '',
          bio: userInfo.bio || '',
          avatar: userInfo.avatar || this.defaultAvatar
        }
        
        console.log('从localStorage加载的用户信息:', this.profile)
      }
    },
    loadUserSettings() {
      // 从localStorage加载用户的个性化设置
      const userId = localStorage.getItem('userId')
      if (!userId) return
      
      // 加载通知设置
      const savedNotificationSettings = localStorage.getItem(`notificationSettings_${userId}`)
      if (savedNotificationSettings) {
        try {
          this.notificationSettings = JSON.parse(savedNotificationSettings)
          console.log('加载的通知设置:', this.notificationSettings)
        } catch (e) {
          console.error('解析通知设置失败:', e)
        }
      }
      
      // 加载教学偏好
      const savedTeachingPreferences = localStorage.getItem(`teachingPreferences_${userId}`)
      if (savedTeachingPreferences) {
        try {
          this.teachingPreferences = JSON.parse(savedTeachingPreferences)
          console.log('加载的教学偏好:', this.teachingPreferences)
        } catch (e) {
          console.error('解析教学偏好失败:', e)
        }
      }
      
      // 加载界面设置
      const savedAppearance = localStorage.getItem(`appearance_${userId}`)
      if (savedAppearance) {
        try {
          this.appearance = JSON.parse(savedAppearance)
          console.log('加载的界面设置:', this.appearance)
        } catch (e) {
          console.error('解析界面设置失败:', e)
        }
      }
      
      // 加载安全设置
      const savedSecurity = localStorage.getItem(`security_${userId}`)
      if (savedSecurity) {
        try {
          this.security = JSON.parse(savedSecurity)
          console.log('加载的安全设置:', this.security)
        } catch (e) {
          console.error('解析安全设置失败:', e)
        }
      }
    },
    async saveProfile() {
      try {
        // 1. 调用后端API更新教师信息 - 现在一个API调用即可保存所有字段
        const updateResult = await teacherApi.updateTeacherInfo({
          first_name: this.profile.name,
          email: this.profile.email,
          phone: this.profile.phone,
          title: this.profile.title,
          department: this.profile.department,
          bio: this.profile.bio
        })
        
        // 2. 保存到localStorage作为备份
        const userId = localStorage.getItem('userId')
        if (userId) {
          // 更新用户基本信息
          const userInfo = updateResult.data // 使用API返回的最新数据
          localStorage.setItem('user', JSON.stringify(userInfo))
          
          // 更新用户全名
          if (this.profile.name) {
            localStorage.setItem('userFullName', this.profile.name)
          }
          
          console.log('个人信息已保存到数据库和localStorage:', userInfo)
        }
        
        alert('个人信息已保存！')
      } catch (error) {
        console.error('保存个人信息失败:', error)
        alert('保存个人信息失败，请重试！')
      }
    },
    saveNotificationSettings() {
      // 保存通知设置到localStorage
      const userId = localStorage.getItem('userId')
      if (userId) {
        localStorage.setItem(`notificationSettings_${userId}`, JSON.stringify(this.notificationSettings))
        console.log('通知设置已保存:', this.notificationSettings)
      }
      alert('通知设置已保存！')
    },
    saveTeachingPreferences() {
      // 保存教学偏好到localStorage
      const userId = localStorage.getItem('userId')
      if (userId) {
        localStorage.setItem(`teachingPreferences_${userId}`, JSON.stringify(this.teachingPreferences))
        console.log('教学偏好已保存:', this.teachingPreferences)
      }
      alert('教学偏好已保存！')
    },
    saveAppearance() {
      // 保存界面设置到localStorage
      const userId = localStorage.getItem('userId')
      if (userId) {
        localStorage.setItem(`appearance_${userId}`, JSON.stringify(this.appearance))
        console.log('界面设置已保存:', this.appearance)
      }
      alert('界面设置已保存！')
    },
    changePassword() {
      if (this.passwordForm.new !== this.passwordForm.confirm) {
        alert('两次输入的密码不一致！')
        return
      }
      if (this.passwordStrength < 50) {
        alert('密码强度不足，请设置更复杂的密码！')
        return
      }
      alert('密码修改成功！')
      this.showPasswordModal = false
      this.passwordForm = { current: '', new: '', confirm: '' }
    },
    triggerAvatarUpload() {
      // 触发隐藏的文件输入框
      this.$refs.avatarInput.click()
    },
    async handleAvatarChange(event) {
      const file = event.target.files[0]
      if (!file) return
      
      try {
        // 创建FormData对象
        const formData = new FormData()
        formData.append('file', file)
        
        // 调用后端API上传头像
        const response = await api.post('/info/avatar/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        })
        
        // 更新头像URL
        this.profile.avatar = response.data.avatar
        
        // 保存到localStorage
        const userId = localStorage.getItem('userId')
        if (userId) {
          const userInfo = JSON.parse(localStorage.getItem('user') || '{}')
          userInfo.avatar = response.data.avatar
          localStorage.setItem('user', JSON.stringify(userInfo))
        }
        
        alert('头像上传成功！')
        console.log('头像上传成功:', response.data)
      } catch (error) {
        console.error('头像上传失败:', error)
        alert('头像上传失败，请重试！')
      }
      
      // 清空文件输入框，允许再次选择同一个文件
      event.target.value = ''
    }
  }
}
</script>

<style scoped>
.settings-page {
  padding: 24px;
  background: #f8fafc;
  min-height: 100%;
}

.page-header {
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 24px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.page-header p {
  color: #64748b;
  margin: 0;
}

.settings-layout {
  display: flex;
  gap: 24px;
}

.settings-sidebar {
  width: 240px;
  flex-shrink: 0;
}

.settings-nav {
  background: white;
  border-radius: 12px;
  padding: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: #64748b;
}

.nav-item:hover {
  background: #f1f5f9;
}

.nav-item.active {
  background: #eff6ff;
  color: #3b82f6;
}

.nav-icon {
  font-size: 18px;
}

.nav-text {
  font-size: 14px;
  font-weight: 500;
}

.settings-content {
  flex: 1;
  min-width: 0;
}

.settings-section {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.section-header {
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.section-header p {
  color: #64748b;
  margin: 0;
  font-size: 14px;
}

.settings-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.profile-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #f1f5f9;
}

.avatar-wrapper {
  position: relative;
}

.avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-edit-btn {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 28px;
  height: 28px;
  border: none;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avatar-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.avatar-info p {
  color: #64748b;
  margin: 0;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
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
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
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

.btn-danger {
  background: #fee2e2;
  color: #dc2626;
}

.btn-danger:hover {
  background: #fecaca;
}

.setting-group {
  margin-bottom: 24px;
}

.setting-group:last-child {
  margin-bottom: 0;
}

.setting-group h3 {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px 0;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #f1f5f9;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-item.danger {
  padding: 20px;
  background: #fef2f2;
  border-radius: 8px;
  margin-top: 16px;
}

.setting-info h3,
.setting-info h4 {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.setting-info p {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

.switch {
  position: relative;
  width: 48px;
  height: 26px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: #e2e8f0;
  border-radius: 26px;
  transition: 0.3s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background: white;
  border-radius: 50%;
  transition: 0.3s;
}

input:checked + .slider {
  background: #3b82f6;
}

input:checked + .slider:before {
  transform: translateX(22px);
}

.time-range {
  display: flex;
  align-items: center;
  gap: 8px;
}

.time-range input {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
}

.time-range span {
  color: #64748b;
}

.theme-options {
  display: flex;
  gap: 16px;
}

.theme-option {
  flex: 1;
  text-align: center;
  cursor: pointer;
  padding: 12px;
  border-radius: 8px;
  border: 2px solid transparent;
  transition: all 0.2s;
}

.theme-option:hover {
  background: #f8fafc;
}

.theme-option.active {
  border-color: #3b82f6;
  background: #eff6ff;
}

.theme-preview {
  height: 60px;
  border-radius: 6px;
  margin-bottom: 8px;
}

.theme-preview.light {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
}

.theme-preview.dark {
  background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
}

.theme-preview.auto {
  background: linear-gradient(135deg, #f8fafc 50%, #1e293b 50%);
}

.theme-option span {
  font-size: 13px;
  color: #64748b;
}

.password-strength {
  margin-top: 12px;
}

.strength-bar {
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 4px;
}

.strength-fill {
  height: 100%;
  border-radius: 2px;
  transition: all 0.3s;
}

.password-strength span {
  font-size: 12px;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 440px;
  overflow: hidden;
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
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #f1f5f9;
  background: #f8fafc;
}
</style>
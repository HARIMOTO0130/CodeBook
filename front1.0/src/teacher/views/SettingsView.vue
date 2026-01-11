<template>
  <div class="settings">
    <div class="page-header">
      <h1>教师设置</h1>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else class="settings-content">
      <!-- 个人信息 -->
      <div class="settings-section">
        <div class="section-header">
          <h2>个人信息</h2>
          <button class="btn btn-primary" @click="saveProfile" :disabled="saving">
            <span v-if="saving">保存中...</span>
            <span v-else>保存更改</span>
          </button>
        </div>

        <div class="profile-form">
          <!-- 头像上传 -->
          <div class="form-row">
            <div class="form-group avatar-upload">
              <label>头像</label>
              <div class="avatar-container">
                <div class="avatar-preview">
                  <img :src="profileForm.avatar || defaultAvatar" alt="头像" />
                  <input
                    type="file"
                    accept="image/*"
                    @change="handleAvatarUpload"
                    class="avatar-input"
                  />
                  <div class="avatar-upload-btn">
                    更换头像
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label>用户名</label>
              <input
                v-model="profileForm.username"
                type="text"
                class="form-input"
                disabled
              />
              <p class="form-hint">用户名不可修改</p>
            </div>

            <div class="form-group">
              <label>邮箱</label>
              <input
                v-model="profileForm.email"
                type="email"
                class="form-input"
                placeholder="请输入邮箱"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>教师编号</label>
              <input
                v-model="profileForm.teacher_number"
                type="text"
                class="form-input"
                placeholder="请输入教师编号"
              />
            </div>

            <div class="form-group">
              <label>姓名</label>
              <input
                v-model="profileForm.first_name"
                type="text"
                class="form-input"
                placeholder="请输入姓名"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>部门</label>
              <input
                v-model="profileForm.department"
                type="text"
                class="form-input"
                placeholder="请输入所属部门"
              />
            </div>

            <div class="form-group">
              <label>联系电话</label>
              <input
                v-model="profileForm.phone"
                type="text"
                class="form-input"
                placeholder="请输入联系电话"
              />
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>职位</label>
              <input
                v-model="profileForm.title"
                type="text"
                class="form-input"
                placeholder="请输入职位"
              />
            </div>

            <div class="form-group">
              <label>办公室</label>
              <input
                v-model="profileForm.office"
                type="text"
                class="form-input"
                placeholder="请输入办公室"
              />
            </div>
          </div>

          <div class="form-group">
            <label>办公时间</label>
            <input
              v-model="profileForm.office_hours"
              type="text"
              class="form-input"
              placeholder="例如：周一至周五 9:00-17:00"
            />
          </div>

          <div class="form-group">
            <label>个人简介</label>
            <textarea
              v-model="profileForm.bio"
              rows="5"
              class="form-textarea"
              placeholder="请输入个人简介..."
            ></textarea>
          </div>
        </div>
      </div>

      <!-- 账户安全 -->
      <div class="settings-section">
        <div class="section-header">
          <h2>账户安全</h2>
        </div>

        <div class="security-form">
          <div class="form-group">
            <label>当前密码</label>
            <input
              v-model="passwordForm.current_password"
              type="password"
              class="form-input"
              placeholder="请输入当前密码"
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>新密码</label>
              <input
                v-model="passwordForm.new_password"
                type="password"
                class="form-input"
                placeholder="请输入新密码"
              />
            </div>

            <div class="form-group">
              <label>确认新密码</label>
              <input
                v-model="passwordForm.confirm_password"
                type="password"
                class="form-input"
                placeholder="请再次输入新密码"
              />
            </div>
          </div>

          <div class="form-actions">
            <button class="btn btn-primary" @click="changePassword" :disabled="changingPassword">
              <span v-if="changingPassword">修改中...</span>
              <span v-else>修改密码</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 统计信息 -->
      <div class="settings-section">
        <div class="section-header">
          <h2>账户统计</h2>
        </div>

        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-label">创建时间</div>
            <div class="stat-value">{{ formatDate(userInfo.date_joined) }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">最后登录</div>
            <div class="stat-value">{{ formatDate(userInfo.last_login) || '从未登录' }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">班级数量</div>
            <div class="stat-value">{{ stats.totalClasses || 0 }}</div>
          </div>
          <div class="stat-item">
            <div class="stat-label">学生数量</div>
            <div class="stat-value">{{ stats.totalStudents || 0 }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '../api/index'
import { analyticsApi } from '../api/analytics'
import { formatDate } from '../../utils/dataFormatter'

export default {
  name: 'SettingsView',
  setup() {
    const loading = ref(true)
    const saving = ref(false)
    const changingPassword = ref(false)
    const userInfo = ref({})
    const stats = ref({
      totalClasses: 0,
      totalStudents: 0
    })
    // 默认头像
    const defaultAvatar = 'https://via.placeholder.com/150'    
    
    const profileForm = ref({
      username: '',
      email: '',
      first_name: '',
      teacher_number: '',
      department: '',
      title: '',
      office: '',
      office_hours: '',
      phone: '',
      bio: '',
      avatar: ''
    })
    const passwordForm = ref({
      current_password: '',
      new_password: '',
      confirm_password: ''
    })

    // 处理头像上传
    const handleAvatarUpload = (event) => {
      const file = event.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          // 更新头像预览
          profileForm.value.avatar = e.target.result
          
          // 保存到localStorage
          const userInfoFromStorage = JSON.parse(localStorage.getItem('userInfo') || '{}')
          const updatedUserInfo = {
            ...userInfoFromStorage,
            avatar: e.target.result
          }
          localStorage.setItem('userInfo', JSON.stringify(updatedUserInfo))
          
          // 尝试调用API上传头像
          const formData = new FormData()
          formData.append('file', file)
          api.post('/teacher/info/avatar/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          }).catch(error => {
            console.log('头像上传API调用失败，已保存到本地:', error)
          })
        }
        reader.readAsDataURL(file)
      }
    }
    
    const loadUserInfo = async () => {
      try {
        // 1. 从localStorage获取用户基本信息和教师详细信息
        const userInfoFromStorage = JSON.parse(localStorage.getItem('userInfo') || '{}')
        const teacherProfileFromStorage = JSON.parse(localStorage.getItem('teacherProfile') || '{}')
        
        // 2. 尝试调用后端API获取数据
        let userInfoData = userInfoFromStorage
        let teacherProfileData = teacherProfileFromStorage
        
        // 获取用户基本信息
        const userResponse = await api.get('/teacher/info/').catch(() => null)
        if (userResponse && userResponse.data) {
          userInfoData = {
            ...userInfoFromStorage,
            ...userResponse.data
          }
          localStorage.setItem('userInfo', JSON.stringify(userInfoData))
        }
        
        // 获取教师详细信息
        const profileResponse = await api.get('/teacher/profile/').catch(() => null)
        if (profileResponse && profileResponse.data) {
          teacherProfileData = {
            ...teacherProfileFromStorage,
            ...profileResponse.data
          }
          localStorage.setItem('teacherProfile', JSON.stringify(teacherProfileData))
        }
        
        // 5. 合并数据到表单
        profileForm.value = {
          username: userInfoData.username || '',
          email: userInfoData.email || '',
          first_name: userInfoData.first_name || '',
          teacher_number: teacherProfileData.teacher_number || '',
          department: teacherProfileData.department || '',
          title: teacherProfileData.title || '',
          office: teacherProfileData.office || '',
          office_hours: teacherProfileData.office_hours || '',
          phone: teacherProfileData.phone || '',
          bio: teacherProfileData.bio || '',
          avatar: userInfoData.avatar || ''
        }

        // 加载统计信息
        try {
          const analyticsRes = await analyticsApi.getOverview()
          if (analyticsRes.data) {
            stats.value.totalClasses = analyticsRes.data.total_classes || 0
            stats.value.totalStudents = analyticsRes.data.total_students || 0
          }
        } catch (e) {
          console.log('加载统计信息失败:', e)
        }
      } catch (error) {
        console.error('加载用户信息失败:', error)
      } finally {
        loading.value = false
      }
    }

    const saveProfile = async () => {
      saving.value = true
      try {
        // 1. 首先尝试调用后端API保存数据
        try {
          // 更新用户基本信息
          await api.put('/teacher/info/', {
            email: profileForm.value.email,
            first_name: profileForm.value.first_name
          })
          
          // 更新教师详细信息
          await api.put('/teacher/profile/', {
            department: profileForm.value.department,
            title: profileForm.value.title,
            office: profileForm.value.office,
            office_hours: profileForm.value.office_hours,
            bio: profileForm.value.bio,
            teacher_number: profileForm.value.teacher_number,
            phone: profileForm.value.phone
          })
          
          alert('保存成功！')
        } catch (apiError) {
          console.log('API保存失败，使用localStorage保存:', apiError)
        }
        
        // 2. 无论API是否成功，都更新localStorage，确保下次加载时能看到最新数据
        const userInfoFromStorage = JSON.parse(localStorage.getItem('userInfo') || '{}')
        const updatedUserInfo = {
          ...userInfoFromStorage,
          email: profileForm.value.email,
          first_name: profileForm.value.first_name
        }
        localStorage.setItem('userInfo', JSON.stringify(updatedUserInfo))
        
        // 保存教师详细信息到localStorage
        const teacherProfile = {
          department: profileForm.value.department,
          title: profileForm.value.title,
          office: profileForm.value.office,
          office_hours: profileForm.value.office_hours,
          bio: profileForm.value.bio,
          teacher_number: profileForm.value.teacher_number,
          phone: profileForm.value.phone
        }
        localStorage.setItem('teacherProfile', JSON.stringify(teacherProfile))
      } catch (error) {
        console.error('保存失败:', error)
        alert('保存失败: ' + (error.response?.data?.error || error.message))
      } finally {
        saving.value = false
      }
    }

    const changePassword = async () => {
      if (!passwordForm.value.current_password) {
        alert('请输入当前密码')
        return
      }

      if (!passwordForm.value.new_password) {
        alert('请输入新密码')
        return
      }

      if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
        alert('两次输入的新密码不一致')
        return
      }

      if (passwordForm.value.new_password.length < 6) {
        alert('新密码长度至少为6位')
        return
      }

      changingPassword.value = true
      try {
        // 这里需要后端提供修改密码的API
        alert('修改密码功能需要后端API支持，请联系开发人员')
        
        // 如果有API，可以这样调用：
        // await api.post('/users/change-password/', {
        //   current_password: passwordForm.value.current_password,
        //   new_password: passwordForm.value.new_password
        // })
        
        // 清空表单
        passwordForm.value = {
          current_password: '',
          new_password: '',
          confirm_password: ''
        }
      } catch (error) {
        console.error('修改密码失败:', error)
        alert('修改密码失败: ' + (error.response?.data?.error || error.message))
      } finally {
        changingPassword.value = false
      }
    }

    onMounted(() => {
      loadUserInfo()
    })

    return {
      loading,
      saving,
      changingPassword,
      userInfo,
      stats,
      profileForm,
      passwordForm,
      saveProfile,
      changePassword,
      formatDate,
      handleAvatarUpload,
      defaultAvatar
    }
  }
}
</script>

<style scoped>
.settings {
  padding: 24px;
  max-width: 1000px;
  margin: 0 auto;
  background: #f8fafc;
  min-height: 100vh;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 32px 0;
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

.settings-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.settings-section {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e2e8f0;
}

.section-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
}

.profile-form,
.security-form {
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
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.form-input,
.form-textarea {
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
  font-family: inherit;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
}

.form-input:disabled {
  background: #f3f4f6;
  color: #64748b;
  cursor: not-allowed;
}

.form-textarea {
  resize: vertical;
}

.form-hint {
  font-size: 12px;
  color: #64748b;
  margin: 0;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-item {
  padding: 20px;
  background: #f8fafc;
  border-radius: 8px;
  border: 2px solid #e2e8f0;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 8px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
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

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 头像上传样式 */
.avatar-upload {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.avatar-container {
  width: 100%;
  display: flex;
  justify-content: center;
}

.avatar-preview {
  position: relative;
  width: 150px;
  height: 150px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #e2e8f0;
  cursor: pointer;
  transition: all 0.2s;
}

.avatar-preview:hover {
  border-color: #3b82f6;
  transform: scale(1.05);
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-input {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  opacity: 0;
  cursor: pointer;
}

.avatar-upload-btn {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  background: rgba(0, 0, 0, 0.6);
  color: white;
  text-align: center;
  padding: 8px 0;
  font-size: 14px;
  transition: all 0.2s;
}

.avatar-preview:hover .avatar-upload-btn {
  background: rgba(59, 130, 246, 0.8);
}

@media (max-width: 768px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .avatar-preview {
    width: 120px;
    height: 120px;
  }
}
</style>

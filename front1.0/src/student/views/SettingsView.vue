<template>
  <div class="settings-container">
    <div class="page-header">
      <h1>设置</h1>
    </div>

    <div class="settings-content">
      <!-- 左侧导航 -->
      <div class="settings-sidebar">
        <div 
          v-for="section in settingSections" 
          :key="section.key"
          class="sidebar-item"
          :class="{ active: activeSection === section.key }"
          @click="activeSection = section.key"
        >
          <span class="sidebar-icon">{{ section.icon }}</span>
          <span class="sidebar-label">{{ section.label }}</span>
        </div>
      </div>

      <!-- 右侧内容 -->
      <div class="settings-main">
        <!-- 账号设置 -->
        <div v-if="activeSection === 'account'" class="setting-section">
          <h2>账号设置</h2>
          <div class="form-content">
            <div class="avatar-setting">
              <div class="avatar-preview">
                <img v-if="userInfo.avatar" :src="userInfo.avatar" class="avatar-image" alt="头像" />
                <div v-else class="avatar-placeholder">{{ userInfo.username ? userInfo.username.charAt(0) : '👤' }}</div>
              </div>
              <input type="file" ref="avatarInput" accept="image/*" style="display: none" @change="handleAvatarUpload" />
              <button class="btn" @click="triggerAvatarUpload">更换头像</button>
            </div>

            <div class="form-group">
              <label class="form-label">昵称</label>
              <input 
                type="text" 
                v-model="userInfo.username" 
                class="input"
                placeholder="请输入昵称"
              />
            </div>

            <div class="form-group">
              <label class="form-label">邮箱</label>
              <input 
                type="email" 
                v-model="userInfo.email" 
                class="input"
                placeholder="请输入邮箱"
                disabled
              />
              <p class="form-hint">邮箱用于账号安全，不可修改</p>
            </div>

            <div class="form-group">
              <label class="form-label">修改密码</label>
              <button class="btn btn-secondary" @click="showChangePassword = true">修改密码</button>
            </div>
          </div>
        </div>

        <!-- 学习偏好 -->
        <div v-if="activeSection === 'preferences'" class="setting-section">
          <h2>学习偏好</h2>
          <div class="form-content">
            <div class="form-group">
              <label class="form-label">默认编程语言</label>
              <select v-model="preferences.defaultLanguage" class="input">
                <option value="javascript">JavaScript</option>
                <option value="python">Python</option>
                <option value="java">Java</option>
                <option value="c">C</option>
                <option value="html">HTML</option>
              </select>
            </div>

            <div class="form-group">
              <label class="form-label">代码编辑器主题</label>
              <div class="theme-options">
                <label class="theme-option">
                  <input type="radio" name="editorTheme" value="vs-dark" v-model="preferences.editorTheme">
                  <span class="theme-name">深色主题</span>
                  <div class="theme-preview dark"></div>
                </label>
                <label class="theme-option">
                  <input type="radio" name="editorTheme" value="vs" v-model="preferences.editorTheme">
                  <span class="theme-name">浅色主题</span>
                  <div class="theme-preview light"></div>
                </label>
                <label class="theme-option">
                  <input type="radio" name="editorTheme" value="hc-black" v-model="preferences.editorTheme">
                  <span class="theme-name">高对比度</span>
                  <div class="theme-preview high-contrast"></div>
                </label>
              </div>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="preferences.autoPlayVideo">
                <span>自动播放视频讲解</span>
              </label>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="preferences.enableKeyboardShortcuts">
                <span>启用键盘快捷键</span>
              </label>
              <p class="form-hint">启用后可以使用键盘快捷键提高学习效率</p>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="preferences.showLineNumbers">
                <span>显示代码行号</span>
              </label>
            </div>

            <div class="form-group">
              <label class="checkbox-label">
                <input type="checkbox" v-model="preferences.useVimMode">
                <span>使用Vim模式</span>
              </label>
            </div>
          </div>
        </div>

        <!-- 数据管理 -->
        <div v-if="activeSection === 'data'" class="setting-section">
          <h2>数据管理</h2>
          <div class="form-content">
            <div class="data-export">
              <h3>导出数据</h3>
              <div class="export-options">
                <button class="btn btn-secondary" @click="exportLearningData('csv')">
                  📊 导出学习记录 (CSV)
                </button>
                <button class="btn btn-secondary" @click="exportLearningData('pdf')">
                  📄 导出学习报告 (PDF)
                </button>
              </div>
            </div>

            <div class="data-clear">
              <h3>清除数据</h3>
              <div class="clear-options">
                <div class="clear-option">
                  <div class="clear-info">
                    <h4>本地缓存</h4>
                    <p>清除编辑器缓存和临时数据</p>
                  </div>
                  <button class="btn btn-danger" @click="clearLocalCache">清除</button>
                </div>
                <div class="clear-option">
                  <div class="clear-info">
                    <h4>学习进度</h4>
                    <p class="warning-text">⚠️ 此操作不可恢复，将清除所有学习记录</p>
                  </div>
                  <button class="btn btn-danger" @click="clearLearningProgress" disabled>
                    清除
                  </button>
                </div>
              </div>
            </div>

            <div class="storage-info">
              <h3>存储空间</h3>
              <div class="storage-details">
                <div class="storage-item">
                  <span class="storage-label">本地存储使用</span>
                  <span class="storage-value">{{ storageUsed }} / {{ storageTotal }} MB</span>
                </div>
                <div class="storage-bar">
                  <div class="storage-bar-fill" :style="{ width: storageUsedPercentage + '%' }"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 修改密码弹窗 -->
    <div v-if="showChangePassword" class="modal-overlay" @click.self="showChangePassword = false">
      <div class="modal-container">
        <div class="modal-header">
          <h3>修改密码</h3>
          <button class="close-btn" @click="showChangePassword = false">×</button>
        </div>
        <div class="modal-content">
          <div class="form-group">
            <label class="form-label">当前密码</label>
            <input 
              type="password" 
              v-model="passwordForm.currentPassword" 
              class="input"
              placeholder="请输入当前密码"
            />
          </div>
          <div class="form-group">
            <label class="form-label">新密码</label>
            <input 
              type="password" 
              v-model="passwordForm.newPassword" 
              class="input"
              placeholder="请输入新密码"
            />
          </div>
          <div class="form-group">
            <label class="form-label">确认新密码</label>
            <input 
              type="password" 
              v-model="passwordForm.confirmPassword" 
              class="input"
              placeholder="请再次输入新密码"
            />
          </div>
          <div class="modal-actions">
            <button class="btn btn-secondary" @click="showChangePassword = false">取消</button>
            <button class="btn btn-primary" @click="changePassword">确认修改</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 保存按钮 -->
    <div class="save-bar">
      <button class="btn btn-primary large" @click="saveSettings">保存设置</button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { api } from '../api/api.js'

export default {
  name: 'SettingsView',
  setup() {
    const activeSection = ref('account')
    const showChangePassword = ref(false)
    
    // 用户信息
    const userInfo = ref({
      username: '张三',
      email: 'zhangsan@example.com',
      avatar: ''
    })
    
    // 学习偏好
    const preferences = ref({
      defaultLanguage: 'javascript',
      editorTheme: 'vs-dark',
      autoPlayVideo: true,
      enableKeyboardShortcuts: true,
      showLineNumbers: true,
      useVimMode: false
    })
    
    // 修改密码表单
    const passwordForm = ref({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })
    
    // 存储空间信息
    const storageUsed = ref('2.5')
    const storageTotal = ref('50')
    const storageUsedPercentage = ref(5)
    
    // 头像上传相关
    const avatarInput = ref(null)
    
    // 设置分类
    const settingSections = [
      { key: 'account', label: '账号设置', icon: '👤' },
      { key: 'preferences', label: '学习偏好', icon: '⚙️' },
      { key: 'data', label: '数据管理', icon: '💾' }
    ]
    
    // 加载设置
    const loadSettings = async () => {
      try {
        // 加载用户信息
        const user = await api.getUserInfo()
        if (user) {
          userInfo.value = user
        }
        
        // 从后端加载偏好设置
        const preferencesData = await api.getUserPreferences()
        if (preferencesData) {
          preferences.value = {
            defaultLanguage: preferencesData.default_language || 'javascript',
            editorTheme: preferencesData.code_theme || 'vs-dark',
            autoPlayVideo: preferencesData.auto_play_video || true,
            enableKeyboardShortcuts: preferencesData.keyboard_shortcuts || true,
            showLineNumbers: true,
            useVimMode: false
          }
          // 保存到localStorage作为备份
          localStorage.setItem('userPreferences', JSON.stringify(preferences.value))
        } else {
          // 从localStorage加载偏好设置作为备用
          const savedPreferences = localStorage.getItem('userPreferences')
          if (savedPreferences) {
            preferences.value = { ...preferences.value, ...JSON.parse(savedPreferences) }
          }
        }
      } catch (error) {
        console.error('加载设置失败:', error)
        // 错误情况下从localStorage加载作为备用
        const savedPreferences = localStorage.getItem('userPreferences')
        if (savedPreferences) {
          preferences.value = { ...preferences.value, ...JSON.parse(savedPreferences) }
        }
      }
    }
    
    // 触发头像上传
    const triggerAvatarUpload = () => {
      avatarInput.value?.click()
    }
    
    // 处理头像上传
    const handleAvatarUpload = async (event) => {
      const file = event.target.files?.[0]
      if (!file) return
      
      try {
        // 直接使用文件上传到后端
        const result = await api.updateUserInfo({}, { avatar: file })
        if (result && result.avatar) {
          // 更新用户头像
          userInfo.value.avatar = result.avatar
          alert('头像上传成功')
        }
      } catch (error) {
        console.error('上传头像失败:', error)
        alert('上传头像失败，请重试')
      } finally {
        // 重置文件输入
        if (avatarInput.value) {
          avatarInput.value.value = ''
        }
      }
    }
    
    // 保存设置
    const saveSettings = async () => {
      try {
        // 根据当前激活的设置部分执行不同的保存逻辑
        if (activeSection.value === 'account') {
          // 保存账号设置
          await api.updateUserInfo({
            username: userInfo.value.username,
            // avatar已经在上传时单独保存了
          })
          alert('账号设置已保存！')
        } else if (activeSection === 'preferences') {
          // 保存学习偏好
          await api.updateUserPreferences({
            default_language: preferences.value.defaultLanguage,
            code_theme: preferences.value.editorTheme,
            auto_play_video: preferences.value.autoPlayVideo,
            keyboard_shortcuts: preferences.value.enableKeyboardShortcuts
          })
          // 保存到本地作为备份
          localStorage.setItem('userPreferences', JSON.stringify(preferences.value))
          alert('学习偏好已保存！')
        }
      } catch (error) {
        console.error('保存设置失败:', error)
        alert('保存失败，请重试')
      }
    }
    
    // 修改密码
    const changePassword = async () => {
      if (!passwordForm.value.currentPassword) {
        alert('请输入当前密码')
        return
      }
      
      if (!passwordForm.value.newPassword) {
        alert('请输入新密码')
        return
      }
      
      if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
        alert('两次输入的密码不一致')
        return
      }
      
      try {
        // 调用后端API修改密码
        await api.changePassword({
          current_password: passwordForm.value.currentPassword,
          new_password: passwordForm.value.newPassword,
          confirm_password: passwordForm.value.confirmPassword
        })
        
        alert('密码修改成功')
        showChangePassword.value = false
        
        // 重置表单
        passwordForm.value = {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        }
      } catch (error) {
        console.error('修改密码失败:', error)
        alert('密码修改失败，请检查当前密码是否正确')
      }
    }
    
    // 导出学习数据
    const exportLearningData = async (format) => {
      try {
        // 调用后端API获取学习记录
        const learningRecords = await api.getLearningRecords('year')
        const practiceRecords = await api.getPracticeRecords()
        const wrongQuestions = await api.getWrongQuestions()
        
        // 构建完整的导出数据
        const exportData = {
          user: userInfo.value,
          exportDate: new Date().toISOString(),
          learningRecords: learningRecords || [],
          practiceRecords: practiceRecords || [],
          wrongQuestions: wrongQuestions || []
        }
        
        alert(`${format.toUpperCase()} 文件正在生成，请稍后...`)
        
        // 根据格式生成并下载文件
        if (format === 'csv') {
          // 生成CSV内容
          const csvContent = generateCSV(exportData)
          downloadFile(csvContent, `learning_data_${new Date().getTime()}.csv`, 'text/csv')
        } else if (format === 'pdf') {
          // 生成PDF内容（简化实现，实际项目中可使用更复杂的PDF生成库）
          const pdfContent = generatePDF(exportData)
          downloadFile(pdfContent, `learning_report_${new Date().getTime()}.pdf`, 'application/pdf')
        }
        
        alert(`学习数据已成功导出为 ${format.toUpperCase()} 格式！`)
      } catch (error) {
        console.error('导出学习数据失败:', error)
        alert('导出失败，请重试')
      }
    }
    
    // 生成CSV内容
    const generateCSV = (data) => {
      // 简化实现，仅导出学习记录
      if (!data.learningRecords || data.learningRecords.length === 0) {
        return '记录ID,课程ID,章节ID,学习时长,完成状态,学习日期\n'
      }
      
      let csv = '记录ID,课程ID,章节ID,学习时长,完成状态,学习日期\n'
      data.learningRecords.forEach(record => {
        csv += `${record.id || ''},${record.course_id || ''},${record.chapter_id || ''},${record.duration || ''},${record.completed ? '已完成' : '未完成'},${record.learn_date || ''}\n`
      })
      return csv
    }
    
    // 生成PDF内容（简化实现）
    const generatePDF = (data) => {
      // 实际项目中可使用jsPDF等库生成复杂PDF
      const pdfContent = `Learning Report\n\nUser: ${data.user.nickname || 'Unknown'}\nExport Date: ${new Date(data.exportDate).toLocaleString()}\n\nLearning Records: ${data.learningRecords.length || 0}\nPractice Records: ${data.practiceRecords.length || 0}\nWrong Questions: ${data.wrongQuestions.length || 0}\n\nThis is a simplified PDF report. For detailed reports, please use CSV format.`
      return pdfContent
    }
    
    // 下载文件
    const downloadFile = (content, filename, mimeType) => {
      const blob = new Blob([content], { type: mimeType })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = filename
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    }
    
    // 清除本地缓存
    const clearLocalCache = () => {
      if (confirm('确定要清除本地缓存吗？这不会影响您的学习记录。')) {
        localStorage.removeItem('codeVersions')
        localStorage.removeItem('lastOpenFile')
        alert('本地缓存已清除！')
      }
    }
    
    // 清除学习进度
    const clearLearningProgress = () => {
      if (confirm('⚠️ 此操作不可恢复，确定要清除所有学习记录吗？')) {
        // 实际应用中这里会调用API
        alert('学习记录已清除')
      }
    }
    
    onMounted(() => {
      loadSettings()
    })
    
    return {
      activeSection,
      settingSections,
      userInfo,
      preferences,
      showChangePassword,
      passwordForm,
      storageUsed,
      storageTotal,
      storageUsedPercentage,
      avatarInput,
      saveSettings,
      changePassword,
      exportLearningData,
      clearLocalCache,
      clearLearningProgress,
      triggerAvatarUpload,
      handleAvatarUpload
    }
  }
}
</script>

<style scoped>
.settings-container {
  padding: 20px 0;
}

.page-header {
  margin-bottom: 30px;
}

.page-header h1 {
  margin: 0;
  font-size: 28px;
}

.settings-content {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 30px;
  margin-bottom: 50px;
}

/* 侧边栏样式 */
.settings-sidebar {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 10px 0;
}

.sidebar-item {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 15px 20px;
  cursor: pointer;
  transition: all 0.3s;
  border-left: 3px solid transparent;
}

.sidebar-item:hover {
  background-color: #f5f5f5;
}

.sidebar-item.active {
  background-color: #ecf5ff;
  border-left-color: #409EFF;
  color: #409EFF;
}

.sidebar-icon {
  font-size: 20px;
}

.sidebar-label {
  font-size: 16px;
}

/* 主内容样式 */
.settings-main {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 30px;
}

.setting-section h2 {
  margin: 0 0 30px 0;
  font-size: 24px;
  color: #333;
}

/* 表单样式 */
.form-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

.avatar-setting {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.avatar-preview {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #e0e0e0;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #409EFF;
  color: white;
  font-size: 48px;
  font-weight: bold;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-hint {
  margin-top: 5px;
  font-size: 12px;
  color: #999;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 10px 0;
}

/* 主题选项 */
.theme-options {
  display: flex;
  gap: 30px;
  flex-wrap: wrap;
}

.theme-option {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.theme-name {
  min-width: 80px;
}

.theme-preview {
  width: 60px;
  height: 40px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.theme-preview.dark {
  background: #1e1e1e;
}

.theme-preview.light {
  background: #ffffff;
}

.theme-preview.high-contrast {
  background: #000000;
  border-color: #ffffff;
}

/* 数据管理 */
.data-export,
.data-clear,
.storage-info {
  margin-bottom: 30px;
}

.data-export h3,
.data-clear h3,
.storage-info h3 {
  margin-bottom: 15px;
  font-size: 18px;
  color: #333;
}

.export-options {
  display: flex;
  gap: 15px;
}

.clear-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  margin-bottom: 15px;
}

.clear-info h4 {
  margin: 0 0 5px 0;
  font-size: 16px;
}

.clear-info p {
  margin: 0;
  font-size: 14px;
  color: #666;
}

.warning-text {
  color: #f56c6c !important;
  font-weight: 500;
}

.storage-details {
  padding: 15px;
  background: #f5f5f5;
  border-radius: 6px;
}

.storage-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
}

.storage-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.storage-bar-fill {
  height: 100%;
  background: #409EFF;
  transition: width 0.3s;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-container {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.modal-content {
  padding: 20px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 30px;
}

/* 保存栏 */
.save-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  padding: 20px;
  box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
  display: flex;
  justify-content: center;
}

.btn.large {
  padding: 12px 40px;
  font-size: 16px;
}

@media (max-width: 768px) {
  .settings-content {
    grid-template-columns: 1fr;
  }
  
  .theme-options {
    flex-direction: column;
  }
  
  .theme-option {
    margin-bottom: 10px;
  }
  
  .clear-option {
    flex-direction: column;
    align-items: stretch;
    gap: 15px;
  }
  
  .save-bar {
    position: static;
    margin-top: 30px;
  }
}
</style>
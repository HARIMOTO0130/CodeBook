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
                <div class="avatar-placeholder">{{ userInfo.nickname.charAt(0) }}</div>
              </div>
              <button class="btn">更换头像</button>
            </div>

            <div class="form-group">
              <label class="form-label">昵称</label>
              <input 
                type="text" 
                v-model="userInfo.nickname" 
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
      nickname: '张三',
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
        
        // 从localStorage加载偏好设置
        const savedPreferences = localStorage.getItem('userPreferences')
        if (savedPreferences) {
          preferences.value = { ...preferences.value, ...JSON.parse(savedPreferences) }
        }
      } catch (error) {
        console.error('加载设置失败:', error)
      }
    }
    
    // 保存设置
    const saveSettings = async () => {
      try {
        // 先调用后端更新偏好中可映射的字段
        await api.updateUserPreferences({
          defaultLanguage: preferences.value.defaultLanguage,
          codeTheme: preferences.value.editorTheme,
          autoPlayVideo: preferences.value.autoPlayVideo,
          keyboardShortcuts: preferences.value.enableKeyboardShortcuts
        })
        // 其余仅前端生效的设置落地到本地
        localStorage.setItem('userPreferences', JSON.stringify(preferences.value))
        alert('设置已保存！')
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
        // 模拟修改密码
        alert('密码修改成功')
        showChangePassword.value = false
        
        // 重置表单
        passwordForm.value = {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        }
      } catch (error) {
        alert('密码修改失败，请重试')
      }
    }
    
    // 导出学习数据
    const exportLearningData = async (format) => {
      try {
        const records = await api.getLearningRecords('year')
        alert(`${format.toUpperCase()} 文件正在生成，请稍后...`)
        // 模拟导出
        setTimeout(() => {
          alert(`学习数据已成功导出为 ${format.toUpperCase()} 格式！`)
        }, 1000)
      } catch (error) {
        alert('导出失败，请重试')
      }
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
      saveSettings,
      changePassword,
      exportLearningData,
      clearLocalCache,
      clearLearningProgress
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
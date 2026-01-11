import api from './index'

// 设置管理API - 基于teacher_setting表结构
export const settingsApi = {
  // 获取所有设置
  getSettings() {
    return api.get('/settings/')
  },
  
  // 获取单个设置
  getSetting(key) {
    return api.get(`/settings/${key}/`)
  },
  
  // 更新单个设置
  updateSetting(key, value) {
    return api.post('/settings/', { 
      setting_key: key, 
      setting_value: value 
    })
  },
  
  // 批量更新设置
  batchUpdateSettings(settings) {
    // settings: [{ setting_key, setting_value }]
    return api.post('/settings/batch/', { settings })
  },
  
  // 重置设置为默认值
  resetSettings() {
    return api.post('/settings/reset/')
  },
  
  // 获取教师信息
  getTeacherInfo() {
    return api.get('/info/')
  },
  
  // 更新教师信息
  updateTeacherInfo(data) {
    // data: { teacher_name, phone, email, avatar }
    return api.put('/info/', data)
  },
  
  // 上传头像
  uploadAvatar(formData) {
    return api.post('/info/avatar/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  // 修改密码
  changePassword(data) {
    // data: { old_password, new_password }
    return api.post('/info/change_password/', data)
  }
}

export default settingsApi

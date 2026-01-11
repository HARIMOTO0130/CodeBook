import api from './index'

// 班级管理API - 基于class表结构
export const classApi = {
  // 获取班级列表
  getClasses(params) {
    // params: { status, search }
    return api.get('/classes/', { params })
  },
  
  // 获取班级详情
  getClassDetail(classId) {
    return api.get(`/classes/${classId}/`)
  },
  
  // 创建班级
  createClass(data) {
    // data: { class_name, book_id, major, grade, class_desc }
    return api.post('/classes/', data)
  },
  
  // 更新班级
  updateClass(classId, data) {
    return api.put(`/classes/${classId}/`, data)
  },
  
  // 删除班级
  deleteClass(classId) {
    return api.delete(`/classes/${classId}/`)
  },
  
  // 添加学生到班级
  addStudent(classId, studentId) {
    return api.post(`/classes/${classId}/students/`, { student_id: studentId })
  },
  
  // 从班级移除学生
  removeStudent(classId, studentId) {
    return api.delete(`/classes/${classId}/students/${studentId}/`)
  },
  
  // 获取班级学生列表
  getClassStudents(classId, params) {
    return api.get(`/classes/${classId}/students/`, { params })
  },
  
  // 获取班级学习进度
  getClassProgress(classId) {
    return api.get(`/classes/${classId}/progress/`)
  },
  
  // 获取班级分析数据
  getClassAnalytics(classId, params) {
    return api.get(`/classes/${classId}/analytics/`, { params })
  },
  
  // 获取班级资源
  getClassResources(classId, params) {
    return api.get(`/classes/${classId}/resources/`, { params })
  },
  
  // 上传班级资源
  uploadResource(classId, formData) {
    return api.post(`/classes/${classId}/resources/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  // 删除班级资源
  deleteResource(resourceId) {
    return api.delete(`/resources/${resourceId}/`)
  },
  
  // 导出班级报告
  exportReport(classId, params) {
    return api.get(`/classes/${classId}/export/`, {
      params,
      responseType: 'blob'
    })
  }
}

export default classApi

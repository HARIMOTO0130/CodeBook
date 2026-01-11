import api from './index'

// 学生管理API - 基于student和student_learning_progress表结构
export const studentApi = {
  // 获取学生列表
  getStudents(params) {
    // params: { class_id, search, status }
    return api.get('/students/', { params })
  },
  
  // 获取学生详情
  getStudentDetail(studentId) {
    return api.get(`/students/${studentId}/`)
  },
  
  // 添加学生
  addStudent(data) {
    // data: { student_no, student_name, gender, phone, class_id }
    return api.post('/students/', data)
  },
  
  // 更新学生信息
  updateStudent(studentId, data) {
    return api.put(`/students/${studentId}/`, data)
  },
  
  // 删除学生
  deleteStudent(studentId) {
    return api.delete(`/students/${studentId}/`)
  },
  
  // 导入学生（批量）
  importStudents(classId, file) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('class_id', classId)
    return api.post('/students/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  // 获取学生学习进度
  getStudentProgress(studentId, params) {
    // params: { chapter_id }
    return api.get(`/students/${studentId}/progress/`, { params })
  },
  
  // 获取学生作业提交记录
  getStudentHomeworks(studentId, params) {
    return api.get(`/students/${studentId}/homeworks/`, { params })
  },
  
  // 获取学生分析数据
  getStudentAnalytics(studentId, params) {
    return api.get(`/students/${studentId}/analytics/`, { params })
  },
  
  // 导出学生报告
  exportStudentReport(studentId) {
    return api.get(`/students/${studentId}/export/`, {
      responseType: 'blob'
    })
  },
  
  // 发送消息给学生
  sendMessage(studentId, data) {
    // data: { message }
    return api.post(`/students/${studentId}/message/`, data)
  },
  
  // 以下是兼容旧代码的方法
  getStudentProfile(id) {
    return this.getStudentDetail(id)
  },
  getStudentLearningProgress(id) {
    return this.getStudentProgress(id)
  },
  getStudentPracticeRecords(id) {
    return this.getStudentHomeworks(id)
  }
}

export default studentApi

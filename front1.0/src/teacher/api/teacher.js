import api from './index'

// 教师端API - 基于数据库表结构
export const teacherApi = {
  // 教师信息管理
  getTeacherInfo() {
    return api.get('/info/')
  },
  updateTeacherInfo(data) {
    // 使用占位符pk=1，因为update方法会忽略pk，直接使用当前登录用户
    return api.put('/info/1/', data)
  },
  
  // 班级管理 (class表)
  getClasses(params) {
    return api.get('/classes/', { params })
  },
  getClassDetail(classId) {
    return api.get(`/classes/${classId}/`)
  },
  createClass(data) {
    // data: { class_name, book_id, major, grade, class_desc }
    return api.post('/classes/', data)
  },
  updateClass(classId, data) {
    return api.put(`/classes/${classId}/`, data)
  },
  deleteClass(classId) {
    return api.delete(`/classes/${classId}/`)
  },
  
  // 学生管理 (student表)
  getStudents(params) {
    // params: { class_id, search, status }
    return api.get('/students/', { params })
  },
  getStudentDetail(studentId) {
    return api.get(`/students/${studentId}/`)
  },
  addStudent(data) {
    // data: { student_no, student_name, gender, phone, class_id }
    return api.post('/students/', data)
  },
  updateStudent(studentId, data) {
    return api.put(`/students/${studentId}/`, data)
  },
  deleteStudent(studentId) {
    return api.delete(`/students/${studentId}/`)
  },
  importStudents(classId, file) {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('class_id', classId)
    return api.post('/students/import/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  // 学生学习进度 (student_learning_progress表)
  getStudentProgress(studentId, params) {
    return api.get(`/students/${studentId}/progress/`, { params })
  },
  getClassProgress(classId) {
    return api.get(`/classes/${classId}/progress/`)
  },
  
  // 作业管理 (homework表)
  getHomeworks(params) {
    // params: { class_id, status, chapter_id }
    return api.get('/homeworks/', { params })
  },
  getHomeworkDetail(homeworkId) {
    return api.get(`/homeworks/${homeworkId}/`)
  },
  createHomework(data) {
    // data: { homework_name, class_id, chapter_id, homework_content, start_time, end_time, total_score }
    return api.post('/homeworks/', data)
  },
  updateHomework(homeworkId, data) {
    return api.put(`/homeworks/${homeworkId}/`, data)
  },
  deleteHomework(homeworkId) {
    return api.delete(`/homeworks/${homeworkId}/`)
  },
  publishHomework(homeworkId) {
    return api.post(`/homeworks/${homeworkId}/publish/`)
  },
  
  // 作业提交与批改 (student_homework表)
  getHomeworkSubmissions(homeworkId, params) {
    return api.get(`/homeworks/${homeworkId}/submissions/`, { params })
  },
  gradeSubmission(submitId, data) {
    // data: { score, correct_comment }
    return api.post(`/submissions/${submitId}/grade/`, data)
  },
  batchGrade(homeworkId, data) {
    // data: { submissions: [{ submit_id, score, correct_comment }] }
    return api.post(`/homeworks/${homeworkId}/batch_grade/`, data)
  },
  returnSubmission(submitId, data) {
    // data: { correct_comment }
    return api.post(`/submissions/${submitId}/return/`, data)
  },
  
  // 班级资源管理 (class_resource表)
  getClassResources(classId, params) {
    return api.get(`/classes/${classId}/resources/`, { params })
  },
  uploadResource(classId, data) {
    // data: FormData with file, resource_name, resource_type, resource_desc
    return api.post(`/classes/${classId}/resources/`, data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  deleteResource(resourceId) {
    return api.delete(`/resources/${resourceId}/`)
  },
  downloadResource(resourceId) {
    return api.get(`/resources/${resourceId}/download/`, {
      responseType: 'blob'
    })
  },
  
  // 教学资源管理 (teaching_resource表)
  getTeachingResources(params) {
    // params: { chapter_id, resource_type }
    return api.get('/teaching_resources/', { params })
  },
  uploadTeachingResource(data) {
    return api.post('/teaching_resources/', data, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  deleteTeachingResource(resourceId) {
    return api.delete(`/teaching_resources/${resourceId}/`)
  },
  
  // 通知管理 (notice表)
  getNotices(params) {
    return api.get('/notices/', { params })
  },
  createNotice(data) {
    // data: { class_id, notice_title, notice_content, expire_time }
    return api.post('/notices/', data)
  },
  updateNotice(noticeId, data) {
    return api.put(`/notices/${noticeId}/`, data)
  },
  deleteNotice(noticeId) {
    return api.delete(`/notices/${noticeId}/`)
  },
  getNoticeReadStatus(noticeId) {
    return api.get(`/notices/${noticeId}/read_status/`)
  },
  
  // 课程设计 (course_design表)
  getCourseDesigns(params) {
    return api.get('/course_designs/', { params })
  },
  createCourseDesign(data) {
    // data: { class_id, chapter_id, design_title, design_content, teaching_hours }
    return api.post('/course_designs/', data)
  },
  updateCourseDesign(designId, data) {
    return api.put(`/course_designs/${designId}/`, data)
  },
  deleteCourseDesign(designId) {
    return api.delete(`/course_designs/${designId}/`)
  },
  
  // 教材和章节 (book, chapter表)
  getBooks(params) {
    return api.get('/books/', { params })
  },
  getBookDetail(bookId) {
    return api.get(`/books/${bookId}/`)
  },
  getChapters(bookId) {
    return api.get(`/books/${bookId}/chapters/`)
  },
  
  // 数据分析
  getDashboardStats() {
    return api.get('/dashboard/stats/')
  },
  getClassAnalytics(classId, params) {
    return api.get(`/classes/${classId}/analytics/`, { params })
  },
  getStudentAnalytics(studentId, params) {
    return api.get(`/students/${studentId}/analytics/`, { params })
  },
  exportClassReport(classId, params) {
    return api.get(`/classes/${classId}/export/`, {
      params,
      responseType: 'blob'
    })
  },
  
  // 教师设置 (teacher_setting表)
  getSettings() {
    return api.get('/settings/')
  },
  updateSetting(key, value) {
    return api.post('/settings/', { setting_key: key, setting_value: value })
  },
  batchUpdateSettings(settings) {
    // settings: [{ setting_key, setting_value }]
    return api.post('/settings/batch/', { settings })
  },
  
  // 教学工具使用记录 (teaching_tool_log表)
  logToolUsage(data) {
    // data: { tool_name, class_id, use_duration }
    return api.post('/tool_logs/', data)
  },
  getToolUsageHistory(params) {
    return api.get('/tool_logs/', { params })
  }
}

export default teacherApi
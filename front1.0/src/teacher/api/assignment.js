import api from './index'

// 作业管理API - 基于homework和student_homework表结构
export const assignmentApi = {
  // 获取作业列表
  getAssignments(params) {
    // params: { class_id, status, chapter_id }
    return api.get('/homeworks/', { params })
  },
  
  // 获取作业详情
  getAssignmentDetail(homeworkId) {
    return api.get(`/homeworks/${homeworkId}/`)
  },
  
  // 创建作业
  createAssignment(data) {
    // data: { homework_name, class_id, chapter_id, homework_content, start_time, end_time, total_score }
    return api.post('/homeworks/', data)
  },
  
  // 更新作业
  updateAssignment(homeworkId, data) {
    return api.put(`/homeworks/${homeworkId}/`, data)
  },
  
  // 删除作业
  deleteAssignment(homeworkId) {
    return api.delete(`/homeworks/${homeworkId}/`)
  },
  
  // 发布作业
  publishAssignment(homeworkId) {
    return api.post(`/homeworks/${homeworkId}/publish/`)
  },
  
  // 获取作业提交列表
  getSubmissions(homeworkId, params) {
    // params: { status, student_id }
    return api.get(`/homeworks/${homeworkId}/submissions/`, { params })
  },
  
  // 批改单个提交
  gradeSubmission(submitId, data) {
    // data: { score, correct_comment }
    return api.post(`/submissions/${submitId}/grade/`, data)
  },
  
  // 批量批改
  batchGrade(homeworkId, data) {
    // data: { submissions: [{ submit_id, score, correct_comment }] }
    return api.post(`/homeworks/${homeworkId}/batch_grade/`, data)
  },
  
  // 退回作业
  returnSubmission(submitId, data) {
    // data: { correct_comment }
    return api.post(`/submissions/${submitId}/return/`, data)
  },
  
  // 获取作业统计
  getAssignmentStats(homeworkId) {
    return api.get(`/homeworks/${homeworkId}/stats/`)
  },
  
  // 导出作业成绩
  exportGrades(homeworkId) {
    return api.get(`/homeworks/${homeworkId}/export/`, {
      responseType: 'blob'
    })
  }
}

export default assignmentApi

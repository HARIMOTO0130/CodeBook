import api from './index'

// 数据分析API
export const analyticsApi = {
  // 获取仪表盘统计数据
  getDashboardStats() {
    return api.get('/dashboard/stats/')
  },
  
  // 获取概览数据
  getOverview() {
    return api.get('/analytics/overview/')
  },
  
  // 获取班级分析数据
  getClassAnalytics(classId, params) {
    // params: { start_date, end_date }
    return api.get(`/classes/${classId}/analytics/`, { params })
  },
  
  // 获取学生分析数据
  getStudentAnalytics(studentId, params) {
    return api.get(`/students/${studentId}/analytics/`, { params })
  },
  
  // 获取作业分析数据
  getHomeworkAnalytics(homeworkId) {
    return api.get(`/homeworks/${homeworkId}/analytics/`)
  },
  
  // 获取学习进度趋势
  getProgressTrend(params) {
    // params: { class_id, start_date, end_date }
    return api.get('/analytics/progress_trend/', { params })
  },
  
  // 获取学习活跃度数据
  getActivity(params) {
    // params: { class_id, time_range }
    return api.get('/analytics/activity/', { params })
  },
  
  // 获取学生表现分析
  getStudentAnalyticsSummary(params) {
    // params: { class_id }
    return api.get('/analytics/student_analytics/', { params })
  },
  
  // 获取AI教学建议
  getRecommendations(params) {
    // params: { class_id, time_range }
    return api.get('/analytics/recommendations/', { params })
  },
  
  // 获取成绩分布
  getScoreDistribution(params) {
    // params: { class_id, homework_id }
    return api.get('/analytics/score_distribution/', { params })
  },
  
  // 导出分析报告
  exportReport(params) {
    return api.get('/analytics/export/', {
      params,
      responseType: 'blob'
    })
  }
}

export default analyticsApi

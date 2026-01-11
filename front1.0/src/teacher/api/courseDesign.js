import api from './index'

// 课程设计API - 基于course_design表结构
export const courseDesignApi = {
  // 获取课程设计列表
  getCourseDesigns(params) {
    // params: { class_id, chapter_id }
    return api.get('/course_designs/', { params })
  },
  
  // 获取课程设计详情
  getCourseDesignDetail(designId) {
    return api.get(`/course_designs/${designId}/`)
  },
  
  // 创建课程设计
  createCourseDesign(data) {
    // data: { class_id, chapter_id, design_title, design_content, teaching_hours }
    return api.post('/course_designs/', data)
  },
  
  // 更新课程设计
  updateCourseDesign(designId, data) {
    return api.put(`/course_designs/${designId}/`, data)
  },
  
  // 删除课程设计
  deleteCourseDesign(designId) {
    return api.delete(`/course_designs/${designId}/`)
  },
  
  // 复制课程设计
  copyCourseDesign(designId, data) {
    // data: { target_class_id }
    return api.post(`/course_designs/${designId}/copy/`, data)
  },
  
  // 导出课程设计
  exportCourseDesign(designId) {
    return api.get(`/course_designs/${designId}/export/`, {
      responseType: 'blob'
    })
  }
}

export default courseDesignApi

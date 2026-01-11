import api from './index'

// 资源管理API - 基于class_resource和teaching_resource表结构
export const resourceApi = {
  // 班级资源管理
  getClassResources(classId, params) {
    // params: { resource_type, search }
    return api.get(`/classes/${classId}/resources/`, { params })
  },
  
  uploadClassResource(classId, formData) {
    // formData: file, resource_name, resource_type, resource_desc
    return api.post(`/classes/${classId}/resources/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  deleteClassResource(resourceId) {
    return api.delete(`/resources/${resourceId}/`)
  },
  
  downloadResource(resourceId) {
    return api.get(`/resources/${resourceId}/download/`, {
      responseType: 'blob'
    })
  },
  
  // 教学资源管理
  getTeachingResources(params) {
    // params: { chapter_id, resource_type }
    return api.get('/teaching_resources/', { params })
  },
  
  uploadTeachingResource(formData) {
    // formData: file, chapter_id, resource_name, resource_type, resource_desc
    return api.post('/teaching_resources/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  
  deleteTeachingResource(resourceId) {
    return api.delete(`/teaching_resources/${resourceId}/`)
  },
  
  // 获取教材列表
  getBooks(params) {
    return api.get('/books/', { params })
  },
  
  // 获取教材详情
  getBookDetail(bookId) {
    return api.get(`/books/${bookId}/`)
  },
  
  // 获取章节列表
  getChapters(bookId, params) {
    return api.get(`/books/${bookId}/chapters/`, { params })
  },
  
  // 获取章节详情
  getChapterDetail(chapterId) {
    return api.get(`/chapters/${chapterId}/`)
  }
}

export default resourceApi

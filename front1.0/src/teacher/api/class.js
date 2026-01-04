import api from './index'

export const classApi = {
  getClasses(params) {
    return api.get('/classes/', { params })
  },
  getClassDetail(id) {
    return api.get(`/classes/${id}/`)
  },
  createClass(data) {
    return api.post('/classes/', data)
  },
  updateClass(id, data) {
    return api.put(`/classes/${id}/`, data)
  },
  deleteClass(id) {
    return api.delete(`/classes/${id}/`)
  },
  addStudent(classId, studentId) {
    return api.post(`/classes/${classId}/add_student/`, { student_id: studentId })
  },
  removeStudent(classId, studentId) {
    return api.post(`/classes/${classId}/remove_student/`, { student_id: studentId })
  },
  getClassAnalytics(id) {
    return api.get(`/classes/${id}/analytics/`)
  }
}

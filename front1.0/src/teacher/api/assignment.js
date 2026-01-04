import api from './index'

export const assignmentApi = {
  getAssignments(params) {
    return api.get('/assignments/', { params })
  },
  getAssignmentDetail(id) {
    return api.get(`/assignments/${id}/`)
  },
  createAssignment(data) {
    return api.post('/assignments/', data)
  },
  updateAssignment(id, data) {
    return api.put(`/assignments/${id}/`, data)
  },
  deleteAssignment(id) {
    return api.delete(`/assignments/${id}/`)
  },
  getSubmissions(id) {
    return api.get(`/assignments/${id}/submissions/`)
  },
  gradeAssignment(id, data) {
    return api.post(`/assignments/${id}/grade/`, data)
  }
}

import api from './index'

export const studentApi = {
  getStudents(params) {
    return api.get('/students/', { params })
  },
  getStudentDetail(id) {
    return api.get(`/students/${id}/`)
  },
  getStudentProfile(id) {
    return api.get(`/students/${id}/profile/`)
  },
  getStudentLearningProgress(id) {
    return api.get(`/students/${id}/learning_progress/`)
  },
  getStudentPracticeRecords(id) {
    return api.get(`/students/${id}/practice_records/`)
  }
}

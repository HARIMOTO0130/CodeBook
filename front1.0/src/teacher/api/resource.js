import api from './index'

export const resourceApi = {
  getResources(params) {
    return api.get('/resources/', { params })
  },
  getResourceDetail(id) {
    return api.get(`/resources/${id}/`)
  },
  createResource(data) {
    return api.post('/resources/', data)
  },
  updateResource(id, data) {
    return api.put(`/resources/${id}/`, data)
  },
  deleteResource(id) {
    return api.delete(`/resources/${id}/`)
  }
}

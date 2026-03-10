import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/student/learning'

const strategyAPI = {
  nodes: {
    list: (params) => axios.get(`${API_BASE_URL}/strategy/nodes/`, { params }),
    byLevel: (level, params) => axios.get(`${API_BASE_URL}/strategy/nodes/by_level/?level=${level}`, { params }),
    graphData: (params) => axios.get(`${API_BASE_URL}/strategy/nodes/graph_data/`, { params }),
    detail: (id) => axios.get(`${API_BASE_URL}/strategy/nodes/${id}/`),
    relatedNodes: (id) => axios.get(`${API_BASE_URL}/strategy/nodes/${id}/related_nodes/`),
    resources: (id) => axios.get(`${API_BASE_URL}/strategy/nodes/${id}/resources/`),
    create: (data) => axios.post(`${API_BASE_URL}/strategy/nodes/`, data),
    update: (id, data) => axios.put(`${API_BASE_URL}/strategy/nodes/${id}/`, data),
    delete: (id) => axios.delete(`${API_BASE_URL}/strategy/nodes/${id}/`)
  },

  relations: {
    list: (params) => axios.get(`${API_BASE_URL}/strategy/relations/`, { params }),
    detail: (id) => axios.get(`${API_BASE_URL}/strategy/relations/${id}/`),
    create: (data) => axios.post(`${API_BASE_URL}/strategy/relations/`, data),
    update: (id, data) => axios.put(`${API_BASE_URL}/strategy/relations/${id}/`, data),
    delete: (id) => axios.delete(`${API_BASE_URL}/strategy/relations/${id}/`)
  },

  paths: {
    list: (params) => axios.get(`${API_BASE_URL}/strategy/paths/`, { params }),
    recommended: (params) => axios.get(`${API_BASE_URL}/strategy/paths/recommended/`, { params }),
    detail: (id) => axios.get(`${API_BASE_URL}/strategy/paths/${id}/`),
    nodes: (id) => axios.get(`${API_BASE_URL}/strategy/paths/${id}/nodes/`),
    start: (id) => axios.post(`${API_BASE_URL}/strategy/paths/${id}/start/`),
    pause: (id) => axios.post(`${API_BASE_URL}/strategy/paths/${id}/pause/`),
    resume: (id) => axios.post(`${API_BASE_URL}/strategy/paths/${id}/resume/`),
    create: (data) => axios.post(`${API_BASE_URL}/strategy/paths/`, data),
    update: (id, data) => axios.put(`${API_BASE_URL}/strategy/paths/${id}/`, data),
    delete: (id) => axios.delete(`${API_BASE_URL}/strategy/paths/${id}/`)
  },

  userPaths: {
    list: (params) => axios.get(`${API_BASE_URL}/strategy/user-paths/`, { params }),
    active: (params) => axios.get(`${API_BASE_URL}/strategy/user-paths/active/`, { params }),
    detail: (id) => axios.get(`${API_BASE_URL}/strategy/user-paths/${id}/`),
    progress: (id) => axios.get(`${API_BASE_URL}/strategy/user-paths/${id}/progress/`),
    updateProgress: (id, data) => axios.post(`${API_BASE_URL}/strategy/user-paths/${id}/update_progress/`, data),
    create: (data) => axios.post(`${API_BASE_URL}/strategy/user-paths/`, data),
    update: (id, data) => axios.put(`${API_BASE_URL}/strategy/user-paths/${id}/`, data),
    delete: (id) => axios.delete(`${API_BASE_URL}/strategy/user-paths/${id}/`)
  },

  recommendations: {
    list: (params) => axios.get(`${API_BASE_URL}/strategy/recommendations/`, { params }),
    paths: (params) => axios.get(`${API_BASE_URL}/strategy/recommendations/paths/`, { params }),
    nodes: (params) => axios.get(`${API_BASE_URL}/strategy/recommendations/nodes/`, { params }),
    detail: (id) => axios.get(`${API_BASE_URL}/strategy/recommendations/${id}/`),
    accept: (id) => axios.post(`${API_BASE_URL}/strategy/recommendations/${id}/accept/`),
    reject: (id, data) => axios.post(`${API_BASE_URL}/strategy/recommendations/${id}/reject/`, data),
    create: (data) => axios.post(`${API_BASE_URL}/strategy/recommendations/`, data),
    update: (id, data) => axios.put(`${API_BASE_URL}/strategy/recommendations/${id}/`, data),
    delete: (id) => axios.delete(`${API_BASE_URL}/strategy/recommendations/${id}/`)
  },

  profile: {
    me: (data) => {
      if (data) {
        return axios.post(`${API_BASE_URL}/strategy/profile/me/`, data)
      }
      return axios.get(`${API_BASE_URL}/strategy/profile/me/`)
    },
    list: (params) => axios.get(`${API_BASE_URL}/strategy/profile/`, { params }),
    detail: (id) => axios.get(`${API_BASE_URL}/strategy/profile/${id}/`),
    create: (data) => axios.post(`${API_BASE_URL}/strategy/profile/`, data),
    update: (id, data) => axios.put(`${API_BASE_URL}/strategy/profile/${id}/`, data),
    delete: (id) => axios.delete(`${API_BASE_URL}/strategy/profile/${id}/`)
  },

  resources: {
    list: (params) => axios.get(`${API_BASE_URL}/strategy/resources/`, { params }),
    byNode: (nodeId, params) => axios.get(`${API_BASE_URL}/strategy/resources/by_node/?node_id=${nodeId}`, { params }),
    detail: (id) => axios.get(`${API_BASE_URL}/strategy/resources/${id}/`),
    create: (data) => axios.post(`${API_BASE_URL}/strategy/resources/`, data),
    update: (id, data) => axios.put(`${API_BASE_URL}/strategy/resources/${id}/`, data),
    delete: (id) => axios.delete(`${API_BASE_URL}/strategy/resources/${id}/`)
  }
}

export default strategyAPI
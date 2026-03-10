import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/review'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  }
})

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Token ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  response => response.data,
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/auth?role=reviewer'
    }
    return Promise.reject(error)
  }
)

export const authApi = {
  login(username, password) {
    return api.post('/auth/login/', { username, password })
  },

  register(data) {
    return api.post('/auth/register/', data)
  },

  logout() {
    return api.post('/auth/logout/')
  },

  getProfile() {
    return api.get('/auth/profile/')
  }
}

export const taskApi = {
  getList(params = {}) {
    return api.get('/tasks/', { params })
  },

  getDetail(id) {
    return api.get(`/tasks/${id}/`)
  },

  getStats() {
    return api.get('/tasks/stats/')
  },

  claim(id) {
    return api.post(`/tasks/${id}/claim/`)
  },

  release(id) {
    return api.post(`/tasks/${id}/release/`)
  },

  triggerAIReview(id) {
    return api.post(`/tasks/${id}/trigger_ai_review/`)
  },

  getLogs(id) {
    return api.get(`/tasks/${id}/logs/`)
  }
}

export const reviewApi = {
  createManualReview(data) {
    return api.post('/manual-reviews/', data)
  },

  getManualReviewList(params = {}) {
    return api.get('/manual-reviews/', { params })
  },

  getManualReviewDetail(id) {
    return api.get(`/manual-reviews/${id}/`)
  },

  getAIReviewList(params = {}) {
    return api.get('/ai-reviews/', { params })
  },

  getAIReviewDetail(id) {
    return api.get(`/ai-reviews/${id}/`)
  }
}

export const ruleApi = {
  getList(params = {}) {
    return api.get('/rules/', { params })
  },

  getDetail(id) {
    return api.get(`/rules/${id}/`)
  },

  create(data) {
    return api.post('/rules/', data)
  },

  update(id, data) {
    return api.patch(`/rules/${id}/`, data)
  },

  delete(id) {
    return api.delete(`/rules/${id}/`)
  }
}

export const editHistoryApi = {
  getList(params = {}) {
    return api.get('/edit-history/', { params })
  },

  getByBook(bookId) {
    return api.get('/edit-history/by_book/', { params: { book_id: bookId } })
  },

  getDetail(id) {
    return api.get(`/edit-history/${id}/`)
  }
}

export const teacherApi = {
  getList(params = {}) {
    return api.get('/teachers/', { params })
  },

  getDetail(id) {
    return api.get(`/teachers/${id}/`)
  },

  getStats(id) {
    return api.get(`/teachers/${id}/stats/`)
  },

  getBooks(id) {
    return api.get(`/teachers/${id}/books/`)
  }
}

export const contentAccessApi = {
  getBookMetadata(bookId) {
    return api.get(`/books/${bookId}/metadata/`)
  },

  // 检查当前用户的内容访问权限
  checkAccess(bookId) {
    return api.get(`/books/${bookId}/metadata/`)
      .then(() => ({ canAccess: true, level: 'metadata' }))
      .catch(err => ({ 
        canAccess: false, 
        level: 'none',
        error: err.response?.data?.detail || '无访问权限'
      }))
  }
}

export const booksApi = {
  getList(params = {}) {
    return api.get('/books/', { params })
  },

  getDetail(id) {
    return api.get(`/books/${id}/`)
  },

  getHistory(bookId, params = {}) {
    return api.get(`/books/${bookId}/history/`, { params })
  },

  getVersions(bookId, params = {}) {
    return api.get(`/books/${bookId}/versions/`, { params })
  },

  getStats(bookId) {
    return api.get(`/books/${bookId}/stats/`)
  }
}

export default api

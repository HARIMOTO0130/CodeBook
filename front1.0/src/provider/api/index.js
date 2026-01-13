// 教材提供者端 API 封装（自行处理鉴权与基址）
const PROVIDER_BASE = 'http://127.0.0.1:8000/api/provider/books'

const getToken = () => {
  try {
    return localStorage.getItem('token') || ''
  } catch {
    return ''
  }
}

const buildHeaders = (auth = false, isFormData = false) => {
  const headers = {}
  if (auth) {
    const token = getToken()
    if (token) headers['Authorization'] = `Token ${token}`
  }
  // 如果是FormData，不设置Content-Type，让浏览器自动设置
  if (!isFormData) {
    headers['Content-Type'] = 'application/json'
  }
  return headers
}

async function request(path, { method = 'GET', body = null, auth = false, isFormData = false } = {}) {
  const url = path.startsWith('http') ? path : `${PROVIDER_BASE}${path}`
  
  // 处理body：如果是FormData，直接使用；否则转换为JSON字符串
  let requestBody = body
  if (body && !isFormData && typeof body === 'object') {
    requestBody = JSON.stringify(body)
  }
  
  const resp = await fetch(url, {
    method,
    headers: buildHeaders(auth, isFormData),
    body: requestBody,
  })
  if (!resp.ok) {
    let detail = ''
    try { 
      const text = await resp.text()
      try {
        detail = JSON.parse(text)
      } catch {
        detail = text
      }
    } catch {}
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }
  return resp.json().catch(() => ({}))
}

export const providerApi = {
  // 书籍列表
  async listBooks(params = {}) {
    const query = new URLSearchParams(params).toString()
    // 使用认证，获取用户可访问的书籍
    return request(query ? `/?${query}` : '/', { auth: true })
  },

  // 创建书籍
  async createBook(payload) {
    const isFormData = payload instanceof FormData
    return request('/', { method: 'POST', body: payload, auth: true, isFormData })
  },

  // 上传PDF文件
  async uploadPDF(payload) {
    return request('/import-pdf/', { method: 'POST', body: payload, auth: true, isFormData: true })
  },

  // 上传DOCX文件 - 使用新的独立端点
  async uploadDOCX(payload) {
    return request('/upload-docx/', { method: 'POST', body: payload, auth: false, isFormData: true })
  },

  // 上传MD文件
  async uploadMD(payload) {
    return request('/import-md/', { method: 'POST', body: payload, auth: true, isFormData: true })
  },

  // 上传EPUB文件
  async uploadEPUB(payload) {
    return request('/import-epub/', { method: 'POST', body: payload, auth: true, isFormData: true })
  },

  // 从GitHub导入
  async importFromGitHub(payload) {
    return request('/import-github/', { method: 'POST', body: payload, auth: true })
  },

  // 分类
  async listCategories() {
    return request('/categories/', { auth: true })
  },
  async createCategory(payload) {
    return request('/categories/', { method: 'POST', body: payload, auth: true })
  },
  async updateCategory(categoryId, payload) {
    return request(`/categories/${categoryId}/`, { method: 'PUT', body: payload, auth: true })
  },
  async patchCategory(categoryId, payload) {
    return request(`/categories/${categoryId}/`, { method: 'PATCH', body: payload, auth: true })
  },
  async deleteCategory(categoryId) {
    return request(`/categories/${categoryId}/`, { method: 'DELETE', auth: true })
  },
  async getCategoryDetail(categoryId) {
    return request(`/categories/${categoryId}/`, { auth: true })
  },

  // 标签
  async listTags() {
    return request('/tags/', { auth: true })
  },
  async createTag(payload) {
    return request('/tags/', { method: 'POST', body: payload, auth: true })
  },
  async updateTag(tagId, payload) {
    return request(`/tags/${tagId}/`, { method: 'PUT', body: payload, auth: true })
  },
  async patchTag(tagId, payload) {
    return request(`/tags/${tagId}/`, { method: 'PATCH', body: payload, auth: true })
  },
  async deleteTag(tagId) {
    return request(`/tags/${tagId}/`, { method: 'DELETE', auth: true })
  },
  async getTagDetail(tagId) {
    return request(`/tags/${tagId}/`, { auth: true })
  },

  // 版本
  async listVersions(bookId) {
    const raw = await request(`/versions/?book=${bookId}`, { auth: true })
    // 统一处理分页和非分页两种返回格式
    if (Array.isArray(raw)) {
      return raw
    }
    if (raw && Array.isArray(raw.results)) {
      return raw.results
    }
    return []
  },
  
  // 获取版本详情
  async getVersionDetail(versionId) {
    return request(`/versions/${versionId}/`, { auth: true })
  },
  
  // 对比书籍版本
  async compareBookVersions(version1Id, version2Id) {
    return request(`/versions/compare/?version1=${version1Id}&version2=${version2Id}`, { auth: true })
  },
  
  // 对比章节版本
  async compareChapterVersions(version1Id, version2Id) {
    return request(`/chapter-versions/compare/?version1=${version1Id}&version2=${version2Id}`, { auth: true })
  },
  
  // 获取版本详情（书籍版本）
  async getBookVersionDetail(versionId) {
    return request(`/versions/${versionId}/`, { auth: true })
  },
  
  // 获取版本详情（章节版本）
  async getChapterVersionDetail(versionId) {
    return request(`/chapter-versions/${versionId}/`, { auth: true })
  },
  
  // 章节版本列表
  async listChapterVersions(chapterId) {
    return request(`/chapter-versions/?chapter=${chapterId}`, { auth: true })
  },

  // 删除书籍
  async deleteBook(bookId) {
    return request(`/${bookId}/`, { method: 'DELETE', auth: true })
  },
  
  // 获取书籍详情
  async getBookDetail(bookId) {
    return request(`/${bookId}/`, { auth: true })
  },
  
  // 完整更新书籍信息
  async updateBook(bookId, payload) {
    const isFormData = payload instanceof FormData
    return request(`/${bookId}/`, { method: 'PUT', body: payload, auth: true, isFormData })
  },
  
  // 部分更新书籍信息
  async patchBook(bookId, payload) {
    const isFormData = payload instanceof FormData
    return request(`/${bookId}/`, { method: 'PATCH', body: payload, auth: true, isFormData })
  },
  
  // 获取书籍统计数据
  async getBookStats(bookId) {
    return request(`/${bookId}/stats/`, { auth: true })
  },
  
  // 更新书籍设置
  async updateBookSettings(bookId, payload) {
    return request(`/${bookId}/settings/`, { method: 'PUT', body: payload, auth: true })
  },
  
  // 获取章节详情
  async getChapterDetail(chapterId) {
    return request(`/chapters/${chapterId}/`, { auth: true })
  },
  
  // 更新章节内容
  async updateChapterContent(chapterId, payload) {
    return request(`/chapters/${chapterId}/`, { method: 'PATCH', body: payload, auth: true })
  },
}



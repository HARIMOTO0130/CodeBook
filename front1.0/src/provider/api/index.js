// 教材提供者端 API 封装
import { API_BASE_URL, api as studentApi } from '../../student/api/api.js'

// 统一以 /api/provider/books 为前缀
const PROVIDER_BASE = API_BASE_URL.replace('/student', '/provider/books')

// 复用学生端的 request 封装
const request = studentApi.request || studentApi._request || null

// 简单兜底：如果没有暴露 request，就直接用 fetch
async function rawRequest(url, options = {}) {
  const resp = await fetch(url, options)
  if (!resp.ok) {
    const text = await resp.text()
    throw new Error(text || resp.statusText)
  }
  return resp.json()
}

const doRequest = request || rawRequest

export const providerApi = {
  async listBooks(params = {}) {
    const query = new URLSearchParams(params).toString()
    const url = query ? `${PROVIDER_BASE}/?${query}` : `${PROVIDER_BASE}/`
    return doRequest(url)
  },

  async listCategories() {
    return doRequest(`${PROVIDER_BASE}/categories/`)
  },

  async createCategory(payload) {
    return doRequest(`${PROVIDER_BASE}/categories/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  },

  async listTags() {
    return doRequest(`${PROVIDER_BASE}/tags/`)
  },

  async createTag(payload) {
    return doRequest(`${PROVIDER_BASE}/tags/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
  },

  async listVersions(bookId) {
    const url = `${PROVIDER_BASE}/versions/?book=${bookId}`
    return doRequest(url)
  },
}



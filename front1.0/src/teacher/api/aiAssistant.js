import axios from 'axios'

// AI助手API使用learning应用的URL前缀
const aiApi = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/learning',
  headers: {
    'Content-Type': 'application/json'
  }
})

aiApi.interceptors.request.use(
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

// 教师端AI助手API
export const teacherAIApi = {
  /**
   * 获取教师端AI助手回复
   * @param {Object} data - 请求数据
   * @param {string} data.question - 问题内容
   * @param {string} [data.session_id] - 会话ID（可选）
   * @param {number} [data.student_id] - 学生ID（可选）
   * @param {number} [data.class_id] - 班级ID（可选）
   * @param {Object} [data.context] - 额外上下文（可选）
   * @returns {Promise} API响应
   */
  getTeacherAIAssistantResponse(data) {
    return aiApi.post('/ai-assistant/', data)
  },

  /**
   * 获取学生的AI交互记录
   * @param {number} studentId - 学生ID
   * @param {Object} params - 查询参数
   * @returns {Promise} API响应
   */
  getStudentAIInteractions(studentId, params = {}) {
    return aiApi.get('/student-data/ai_interactions/', {
      params: { student_id: studentId, ...params }
    })
  },

  /**
   * 获取学生的学习进度
   * @param {number} studentId - 学生ID
   * @returns {Promise} API响应
   */
  getStudentLearningProgress(studentId) {
    return aiApi.get('/student-data/learning_progress/', {
      params: { student_id: studentId }
    })
  },

  /**
   * 获取学生的练习记录
   * @param {number} studentId - 学生ID
   * @param {Object} params - 查询参数
   * @returns {Promise} API响应
   */
  getStudentPracticeRecords(studentId, params = {}) {
    return aiApi.get('/student-data/practice_records/', {
      params: { student_id: studentId, ...params }
    })
  },

  /**
   * 获取班级学生数据摘要
   * @param {number} classId - 班级ID
   * @returns {Promise} API响应
   */
  getClassStudentsSummary(classId) {
    return aiApi.get('/student-data/class_students_summary/', {
      params: { class_id: classId }
    })
  }
}

export default teacherAIApi

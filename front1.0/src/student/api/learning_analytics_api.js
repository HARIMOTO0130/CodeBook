import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/learning'

// 创建axios实例，添加认证token
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器，添加认证token
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Token ${token}`
  }
  return config
})

/**
 * 学情智能分析API接口
 */
export const learningAnalyticsAPI = {
  
  /**
   * 获取完整的学习智能分析
   * @param {string} sessionId - 会话ID
   * @returns {Promise} 分析结果和建议
   */
  async getLearningAnalytics(sessionId = null) {
    try {
      const params = {}
      if (sessionId) {
        params.session_id = sessionId
      }
      
      const response = await apiClient.get('/learning-analytics/', { params })
      return response.data
    } catch (error) {
      console.error('获取学习智能分析失败:', error)
      // 返回模拟数据
      return {
        analysis: this.generateMockAnalysis(),
        recommendations: this.generateMockRecommendations()
      }
    }
  },

  /**
   * 获取学习模式分析
   * @param {string} sessionId - 会话ID
   * @returns {Promise} 学习模式分析结果
   */
  async getLearningPatterns(sessionId = null) {
    try {
      const params = {}
      if (sessionId) {
        params.session_id = sessionId
      }
      
      const response = await apiClient.get('/learning-analytics/patterns/', { params })
      return response.data
    } catch (error) {
      console.error('获取学习模式分析失败:', error)
      // 返回模拟数据
      return {
        result: this.generateMockAnalysis()
      }
    }
  },

  /**
   * 获取学习建议
   * @param {string} sessionId - 会话ID
   * @returns {Promise} 学习建议列表
   */
  async getLearningRecommendations(sessionId = null) {
    try {
      const params = {}
      if (sessionId) {
        params.session_id = sessionId
      }
      
      const response = await apiClient.get('/learning-analytics/recommendations/', { params })
      return response.data
    } catch (error) {
      console.error('获取学习建议失败:', error)
      // 返回模拟数据
      return {
        result: this.generateMockRecommendations()
      }
    }
  },

  /**
   * 获取学习效率评估
   * @param {string} sessionId - 会话ID
   * @returns {Promise} 学习效率评估结果
   */
  async getLearningEfficiency(sessionId = null) {
    try {
      const params = {}
      if (sessionId) {
        params.session_id = sessionId
      }
      
      const response = await apiClient.get('/learning-analytics/efficiency/', { params })
      return response.data
    } catch (error) {
      console.error('获取学习效率评估失败:', error)
      // 返回模拟数据
      return {
        result: this.generateMockEfficiencyData()
      }
    }
  },

  /**
   * 生成模拟分析数据
   * @returns {Object} 模拟分析数据
   */
  generateMockAnalysis() {
    return {
      patterns: {
        time_distribution: {
          hourly_distribution: {
            8: 5, 9: 8, 10: 12, 11: 10, 12: 6,
            13: 4, 14: 7, 15: 9, 16: 11, 17: 8,
            18: 6, 19: 4, 20: 3, 21: 2, 22: 1
          },
          daily_distribution: {
            'Monday': 12, 'Tuesday': 10, 'Wednesday': 15,
            'Thursday': 11, 'Friday': 9, 'Saturday': 6, 'Sunday': 4
          },
          peak_hour: 10,
          peak_day: 'Wednesday',
          total_learning_sessions: 67
        },
        content_distribution: {
          knowledge_distribution: {
            'Python基础': 20,
            '数据结构': 15,
            '算法': 12,
            'Web开发': 10,
            '数据库': 8
          },
          most_studied_knowledge: 'Python基础',
          unique_knowledge_nodes: 5
        },
        learning_efficiency: {
          total_learning_time: 1200, // 分钟
          average_session_duration: 18,
          daily_frequency: 2.3,
          continuity_score: 75,
          efficiency_level: 'good'
        },
        learning_habits: {
          time_preference: 'morning',
          duration_preference: 'medium',
          frequency_pattern: 'regular'
        },
        learning_progress: {
          score_trend: {
            trend: 'improving',
            average_score: 75,
            score_improvement: 8
          },
          knowledge_mastery: {
            mastery_levels: {
              'Python基础': 'excellent',
              '数据结构': 'good',
              '算法': 'good',
              'Web开发': 'average',
              '数据库': 'average'
            },
            total_knowledge_nodes: 5
          },
          completion_rate: 45
        }
      },
      data_available: true,
      user_id: 1
    }
  },

  /**
   * 生成模拟建议数据
   * @returns {Object} 模拟建议数据
   */
  generateMockRecommendations() {
    return {
      recommendations: [
        {
          title: '保持晨学习惯',
          description: '您在早晨学习效率较高，建议继续保持这个好习惯',
          priority: 'high',
          estimated_time: 5
        },
        {
          title: '培养学习习惯',
          description: '建议每天固定时间学习，培养良好的学习习惯',
          priority: 'medium',
          estimated_time: 10
        },
        {
          title: '加强薄弱知识点',
          description: '建议重点加强以下知识点：Web开发, 数据库',
          priority: 'high',
          estimated_time: 20
        },
        {
          title: '多样化学习内容',
          description: '建议学习更多不同类型的知识点，拓宽知识面',
          priority: 'medium',
          estimated_time: 10
        }
      ],
      analysis: this.generateMockAnalysis().patterns,
      user_id: 1
    }
  },

  /**
   * 生成模拟效率数据
   * @returns {Object} 模拟效率数据
   */
  generateMockEfficiencyData() {
    return {
      learning_efficiency: {
        total_learning_time: 1200,
        average_session_duration: 18,
        daily_frequency: 2.3,
        continuity_score: 75,
        efficiency_level: 'good'
      },
      learning_habits: {
        time_preference: 'morning',
        duration_preference: 'medium',
        frequency_pattern: 'regular'
      },
      time_distribution: {
        hourly_distribution: {
          8: 5, 9: 8, 10: 12, 11: 10, 12: 6,
          13: 4, 14: 7, 15: 9, 16: 11, 17: 8,
          18: 6, 19: 4, 20: 3, 21: 2, 22: 1
        },
        daily_distribution: {
          'Monday': 12, 'Tuesday': 10, 'Wednesday': 15,
          'Thursday': 11, 'Friday': 9, 'Saturday': 6, 'Sunday': 4
        },
        peak_hour: 10,
        peak_day: 'Wednesday',
        total_learning_sessions: 67
      }
    }
  }
}

/**
 * 学情智能分析工具类
 */
export const learningAnalyticsUtils = {
  
  /**
   * 格式化学习模式数据
   * @param {Object} patterns - 学习模式数据
   * @returns {Object} 格式化后的数据
   */
  formatLearningPatterns(patterns) {
    if (!patterns) {
      return {
        timeDistribution: {},
        contentDistribution: {},
        learningEfficiency: {},
        learningHabits: {},
        learningProgress: {}
      }
    }
    
    return {
      timeDistribution: patterns.time_distribution || {},
      contentDistribution: patterns.content_distribution || {},
      learningEfficiency: patterns.learning_efficiency || {},
      learningHabits: patterns.learning_habits || {},
      learningProgress: patterns.learning_progress || {}
    }
  },

  /**
   * 格式化学习建议
   * @param {Array} recommendations - 学习建议列表
   * @returns {Array} 格式化后的建议列表
   */
  formatRecommendations(recommendations) {
    if (!recommendations || !Array.isArray(recommendations)) {
      return []
    }
    
    return recommendations.map(rec => ({
      ...rec,
      priorityInfo: this.getPriorityInfo(rec.priority),
      estimatedTimeFormatted: this.formatEstimatedTime(rec.estimated_time)
    }))
  },

  /**
   * 获取优先级信息
   * @param {string} priority - 优先级
   * @returns {Object} 优先级信息
   */
  getPriorityInfo(priority) {
    const priorityMap = {
      high: { label: '高', color: '#e53e3e', icon: '🔥' },
      medium: { label: '中', color: '#dd6b20', icon: '⚠️' },
      low: { label: '低', color: '#38a169', icon: '💡' }
    }
    return priorityMap[priority] || priorityMap.medium
  },

  /**
   * 格式化预计时间
   * @param {number} minutes - 分钟数
   * @returns {string} 格式化后的时间
   */
  formatEstimatedTime(minutes) {
    if (minutes < 60) {
      return `${minutes}分钟`
    }
    const hours = Math.floor(minutes / 60)
    const remainingMinutes = minutes % 60
    return remainingMinutes > 0 ? `${hours}小时${remainingMinutes}分钟` : `${hours}小时`
  },

  /**
   * 获取效率等级信息
   * @param {string} level - 效率等级
   * @returns {Object} 效率等级信息
   */
  getEfficiencyLevelInfo(level) {
    const levelMap = {
      excellent: { label: '优秀', color: '#38a169', icon: '🌟' },
      good: { label: '良好', color: '#3182ce', icon: '✅' },
      average: { label: '一般', color: '#dd6b20', icon: '⚠️' },
      needs_improvement: { label: '需要改进', color: '#e53e3e', icon: '📈' }
    }
    return levelMap[level] || levelMap.average
  },

  /**
   * 获取时间偏好信息
   * @param {string} preference - 时间偏好
   * @returns {Object} 时间偏好信息
   */
  getTimePreferenceInfo(preference) {
    const preferenceMap = {
      morning: { label: '早晨', icon: '🌅' },
      afternoon: { label: '下午', icon: '☀️' },
      evening: { label: '晚上', icon: '🌙' }
    }
    return preferenceMap[preference] || { label: '无偏好', icon: '⏰' }
  },

  /**
   * 获取时长偏好信息
   * @param {string} preference - 时长偏好
   * @returns {Object} 时长偏好信息
   */
  getDurationPreferenceInfo(preference) {
    const preferenceMap = {
      short: { label: '短时间', icon: '⏱️' },
      medium: { label: '中等时间', icon: '⏲️' },
      long: { label: '长时间', icon: '⏰' }
    }
    return preferenceMap[preference] || { label: '无偏好', icon: '📏' }
  },

  /**
   * 获取频率模式信息
   * @param {string} pattern - 频率模式
   * @returns {Object} 频率模式信息
   */
  getFrequencyPatternInfo(pattern) {
    const patternMap = {
      frequent: { label: '频繁', icon: '🔄' },
      regular: { label: '规律', icon: '📅' },
      occasional: { label: '偶尔', icon: '⏳' },
      no_pattern: { label: '无规律', icon: '❓' }
    }
    return patternMap[pattern] || patternMap.no_pattern
  },

  /**
   * 生成时间分布图表数据
   * @param {Object} timeDistribution - 时间分布数据
   * @returns {Object} 图表数据
   */
  generateTimeDistributionChartData(timeDistribution) {
    if (!timeDistribution) {
      return {
        labels: [],
        datasets: []
      }
    }

    // 小时分布数据
    const hourlyLabels = Object.keys(timeDistribution.hourly_distribution || {}).map(hour => `${hour}:00`)
    const hourlyData = Object.values(timeDistribution.hourly_distribution || {})

    return {
      labels: hourlyLabels,
      datasets: [{
        label: '学习次数',
        data: hourlyData,
        borderColor: '#4299e1',
        backgroundColor: 'rgba(66, 153, 225, 0.1)',
        tension: 0.4,
        fill: true
      }]
    }
  },

  /**
   * 生成内容分布图表数据
   * @param {Object} contentDistribution - 内容分布数据
   * @returns {Object} 图表数据
   */
  generateContentDistributionChartData(contentDistribution) {
    if (!contentDistribution) {
      return {
        labels: [],
        datasets: []
      }
    }

    const knowledgeLabels = Object.keys(contentDistribution.knowledge_distribution || {})
    const knowledgeData = Object.values(contentDistribution.knowledge_distribution || {})

    return {
      labels: knowledgeLabels,
      datasets: [{
        label: '学习次数',
        data: knowledgeData,
        backgroundColor: [
          '#4299e1', '#38a169', '#dd6b20', '#805ad5', '#e53e3e'
        ],
        borderWidth: 1
      }]
    }
  },

  /**
   * 生成学习效率雷达图数据
   * @param {Object} learningEfficiency - 学习效率数据
   * @returns {Object} 图表数据
   */
  generateEfficiencyRadarData(learningEfficiency) {
    if (!learningEfficiency) {
      return {
        labels: [],
        datasets: []
      }
    }

    return {
      labels: ['连续性', '频率', '平均时长', '总学习时间'],
      datasets: [{
        label: '学习效率',
        data: [
          learningEfficiency.continuity_score || 0,
          (learningEfficiency.daily_frequency || 0) * 20, // 转换为0-100
          Math.min(100, (learningEfficiency.average_session_duration || 0) * 2), // 转换为0-100
          Math.min(100, (learningEfficiency.total_learning_time || 0) / 20) // 转换为0-100
        ],
        backgroundColor: 'rgba(66, 153, 225, 0.2)',
        borderColor: '#4299e1',
        pointBackgroundColor: '#4299e1',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: '#4299e1'
      }]
    }
  }
}

/**
 * 学情智能分析示例数据
 */
export const learningAnalyticsExamples = {
  getExampleAnalysis() {
    return learningAnalyticsAPI.generateMockAnalysis()
  },
  
  getExampleRecommendations() {
    return learningAnalyticsAPI.generateMockRecommendations()
  },
  
  getExampleEfficiencyData() {
    return learningAnalyticsAPI.generateMockEfficiencyData()
  }
}

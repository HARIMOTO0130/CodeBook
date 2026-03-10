import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/learning'

/**
 * 习题生成API接口
 */
export const exerciseGeneratorAPI = {
  
  /**
   * 生成习题
   * @param {Array} knowledgePoints - 知识点列表
   * @param {string} exerciseType - 习题类型
   * @param {string} difficulty - 难度等级
   * @param {number} count - 生成数量
   * @param {Object} context - 上下文信息
   * @param {string} sessionId - 会话ID
   * @returns {Promise} 生成结果
   */
  async generateExercises(knowledgePoints, exerciseType = 'multiple_choice', 
                         difficulty = 'medium', count = 5, context = {}, sessionId = null) {
    try {
      const response = await axios.post(`${API_BASE_URL}/exercise-generator/`, {
        knowledge_points: knowledgePoints,
        exercise_type: exerciseType,
        difficulty: difficulty,
        count: count,
        context: context,
        session_id: sessionId
      })
      return response.data
    } catch (error) {
      console.error('生成习题失败:', error)
      throw error
    }
  },

  /**
   * 生成习题集
   * @param {Object} knowledgeTree - 知识点树
   * @param {Object} difficultyDistribution - 难度分布
   * @param {Object} typeDistribution - 类型分布
   * @param {number} totalCount - 总题数
   * @param {Object} context - 上下文信息
   * @param {string} sessionId - 会话ID
   * @returns {Promise} 生成结果
   */
  async generateExerciseSet(knowledgeTree, difficultyDistribution = null, 
                           typeDistribution = null, totalCount = 10, 
                           context = {}, sessionId = null) {
    try {
      const response = await axios.post(`${API_BASE_URL}/exercise-generator/set/`, {
        knowledge_tree: knowledgeTree,
        difficulty_distribution: difficultyDistribution,
        type_distribution: typeDistribution,
        total_count: totalCount,
        context: context,
        session_id: sessionId
      })
      return response.data
    } catch (error) {
      console.error('生成习题集失败:', error)
      throw error
    }
  },

  /**
   * 获取推荐习题
   * @param {number} count - 推荐数量
   * @param {string} sessionId - 会话ID
   * @returns {Promise} 推荐结果
   */
  async getRecommendedExercises(count = 5, sessionId = null) {
    try {
      const response = await axios.get(`${API_BASE_URL}/exercise-generator/recommend/`, {
        params: { count, session_id: sessionId }
      })
      return response.data
    } catch (error) {
      console.error('获取推荐习题失败:', error)
      throw error
    }
  },

  /**
   * 获取习题生成历史
   * @param {number} limit - 限制数量
   * @param {number} offset - 偏移量
   * @returns {Promise} 历史记录
   */
  async getExerciseHistory(limit = 10, offset = 0) {
    try {
      const response = await axios.get(`${API_BASE_URL}/exercise-generator/history/`, {
        params: { limit, offset }
      })
      return response.data
    } catch (error) {
      console.error('获取习题生成历史失败:', error)
      throw error
    }
  },

  /**
   * 获取习题类型配置
   * @returns {Promise} 习题类型配置
   */
  async getExerciseTypes() {
    try {
      const response = await axios.get(`${API_BASE_URL}/exercise-generator/types/`)
      return response.data
    } catch (error) {
      console.error('获取习题类型失败:', error)
      throw error
    }
  }
}

/**
 * 习题生成工具类
 */
export const exerciseGeneratorUtils = {
  
  /**
   * 格式化习题数据
   * @param {Array} exercises - 习题列表
   * @returns {Array} 格式化后的习题
   */
  formatExercises(exercises) {
    return (exercises || []).map(exercise => {
      const formatted = { ...exercise }
      
      // 标准化习题类型
      formatted.type_name = this.getExerciseTypeName(formatted.exercise_type)
      
      // 标准化难度
      formatted.difficulty_name = this.getDifficultyName(formatted.difficulty)
      
      // 计算预估完成时间
      formatted.estimated_time = this.calculateEstimatedTime(formatted)
      
      return formatted
    })
  },

  /**
   * 获取习题类型名称
   * @param {string} type - 习题类型
   * @returns {string} 类型名称
   */
  getExerciseTypeName(type) {
    const typeNames = {
      multiple_choice: '选择题',
      true_false: '判断题',
      fill_blank: '填空题',
      coding: '编程题',
      short_answer: '简答题'
    }
    return typeNames[type] || type
  },

  /**
   * 获取难度名称
   * @param {string} difficulty - 难度
   * @returns {string} 难度名称
   */
  getDifficultyName(difficulty) {
    const difficultyNames = {
      easy: '简单',
      medium: '中等',
      hard: '困难'
    }
    return difficultyNames[difficulty] || difficulty
  },

  /**
   * 计算预估完成时间
   * @param {Object} exercise - 习题
   * @returns {number} 预估时间（分钟）
   */
  calculateEstimatedTime(exercise) {
    const baseTimes = {
      multiple_choice: 1,
      true_false: 0.5,
      fill_blank: 1.5,
      short_answer: 2,
      coding: 5
    }
    
    const difficultyMultipliers = {
      easy: 0.8,
      medium: 1.0,
      hard: 1.5
    }
    
    const baseTime = baseTimes[exercise.exercise_type] || 1
    const multiplier = difficultyMultipliers[exercise.difficulty] || 1
    
    return Math.round(baseTime * multiplier * 10) / 10
  },

  /**
   * 验证知识点列表
   * @param {Array} knowledgePoints - 知识点列表
   * @returns {Object} 验证结果
   */
  validateKnowledgePoints(knowledgePoints) {
    if (!Array.isArray(knowledgePoints)) {
      return { valid: false, message: '知识点必须是数组' }
    }
    
    if (knowledgePoints.length === 0) {
      return { valid: false, message: '知识点不能为空' }
    }
    
    if (knowledgePoints.length > 10) {
      return { valid: false, message: '知识点数量不能超过10个' }
    }
    
    return { valid: true, message: '知识点验证通过' }
  },

  /**
   * 生成默认知识点树
   * @returns {Object} 知识点树
   */
  generateDefaultKnowledgeTree() {
    return {
      name: '编程基础',
      children: [
        {
          name: 'Python',
          children: [
            { name: '语法基础' },
            { name: '数据结构' },
            { name: '函数编程' }
          ]
        },
        {
          name: '数据结构',
          children: [
            { name: '数组' },
            { name: '链表' },
            { name: '树' }
          ]
        },
        {
          name: '算法',
          children: [
            { name: '排序算法' },
            { name: '搜索算法' },
            { name: '动态规划' }
          ]
        }
      ]
    }
  },

  /**
   * 从知识点树中提取知识点列表
   * @param {Object} tree - 知识点树
   * @returns {Array} 知识点列表
   */
  extractKnowledgePoints(tree) {
    const points = []
    
    function traverse(node) {
      if (node.name) {
        points.push(node.name)
      }
      if (node.children) {
        node.children.forEach(child => traverse(child))
      }
    }
    
    traverse(tree)
    return points
  }
}

/**
 * 习题示例数据
 */
export const exerciseExamples = {
  
  /**
   * 获取示例知识点
   * @returns {Array} 示例知识点
   */
  getExampleKnowledgePoints() {
    return [
      'Python语法基础',
      '数据结构',
      '算法',
      '面向对象编程',
      '函数式编程'
    ]
  },

  /**
   * 获取示例知识点树
   * @returns {Object} 示例知识点树
   */
  getExampleKnowledgeTree() {
    return {
      name: '编程学习',
      children: [
        {
          name: 'Python',
          children: [
            { name: '语法基础' },
            { name: '数据类型' },
            { name: '控制流' },
            { name: '函数' },
            { name: '面向对象' }
          ]
        },
        {
          name: '数据结构',
          children: [
            { name: '数组' },
            { name: '链表' },
            { name: '栈' },
            { name: '队列' },
            { name: '树' },
            { name: '图' }
          ]
        },
        {
          name: '算法',
          children: [
            { name: '排序算法' },
            { name: '搜索算法' },
            { name: '动态规划' },
            { name: '贪心算法' },
            { name: '回溯算法' }
          ]
        }
      ]
    }
  }
}
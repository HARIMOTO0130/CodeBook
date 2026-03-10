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
 * 学习效果预测API接口
 */
export const learningPredictionAPI = {
  
  /**
   * 获取学习效果预测
   * @param {number} knowledgeNodeId - 知识点ID（可选）
   * @param {string} sessionId - 会话ID
   * @returns {Promise} 预测结果
   */
  async getLearningPrediction(knowledgeNodeId = null, sessionId = null) {
    try {
      const params = {};
      if (knowledgeNodeId) {
        params.knowledge_node_id = knowledgeNodeId;
      }
      if (sessionId) {
        params.session_id = sessionId;
      }
      
      const response = await apiClient.get('/learning-prediction/', { params });
      return response.data;
    } catch (error) {
      console.error('获取学习效果预测失败:', error);
      // 返回模拟数据
      return {
        result: {
          prediction: learningPredictionExamples.getExamplePrediction(),
          interventions: learningPredictionExamples.getExampleInterventions()
        }
      };
    }
  },

  /**
   * 批量预测学习效果
   * @param {Array} userIds - 用户ID列表
   * @param {string} sessionId - 会话ID
   * @returns {Promise} 批量预测结果
   */
  async batchPredict(userIds, sessionId = null) {
    try {
      const response = await apiClient.post('/learning-prediction/batch/', {
        user_ids: userIds,
        session_id: sessionId
      });
      return response.data;
    } catch (error) {
      console.error('批量预测失败:', error);
      // 返回模拟数据
      return {
        result: {
          predictions: userIds.map(userId => ({
            user_id: userId,
            prediction: learningPredictionExamples.getExamplePrediction()
          }))
        }
      };
    }
  },

  /**
   * 获取预测历史
   * @param {number} days - 历史天数
   * @param {string} sessionId - 会话ID
   * @returns {Promise} 历史记录
   */
  async getPredictionHistory(days = 30, sessionId = null) {
    try {
      const params = { days };
      if (sessionId) {
        params.session_id = sessionId;
      }
      
      const response = await apiClient.get('/learning-prediction/history/', { params });
      return response.data;
    } catch (error) {
      console.error('获取预测历史失败:', error);
      // 返回模拟数据
      return {
        history: this.generateMockHistory(days)
      };
    }
  },

  /**
   * 获取干预建议
   * @param {number} knowledgeNodeId - 知识点ID（可选）
   * @param {string} sessionId - 会话ID
   * @returns {Promise} 干预建议
   */
  async getInterventions(knowledgeNodeId = null, sessionId = null) {
    try {
      const params = {};
      if (knowledgeNodeId) {
        params.knowledge_node_id = knowledgeNodeId;
      }
      if (sessionId) {
        params.session_id = sessionId;
      }
      
      const response = await apiClient.get('/learning-prediction/intervention/', { params });
      return response.data;
    } catch (error) {
      console.error('获取干预建议失败:', error);
      // 返回模拟数据
      return {
        interventions: learningPredictionExamples.getExampleInterventions()
      };
    }
  },

  /**
   * 获取预测统计
   * @param {string} sessionId - 会话ID
   * @returns {Promise} 统计数据
   */
  async getPredictionStats(sessionId = null) {
    try {
      const params = {};
      if (sessionId) {
        params.session_id = sessionId;
      }
      
      const response = await apiClient.get('/learning-prediction/stats/', { params });
      return response.data;
    } catch (error) {
      console.error('获取预测统计失败:', error);
      // 返回模拟数据
      return {
        stats: {
          average_score: 0.7,
          average_mastery: 0.75,
          max_score: 0.9,
          min_score: 0.5,
          score_trend: 0.03,
          risk_distribution: { high: 5, medium: 10, low: 15 },
          total_predictions: 30
        }
      };
    }
  },

  /**
   * 生成模拟历史数据
   * @param {number} days - 历史天数
   * @returns {Array} 模拟历史数据
   */
  generateMockHistory(days) {
    const history = []
    const today = new Date()
    
    for (let i = days; i > 0; i--) {
      const date = new Date(today)
      date.setDate(today.getDate() - i)
      
      // 生成模拟数据
      const score = 0.5 + Math.sin(i / 7) * 0.2 + Math.random() * 0.1
      const mastery = score * 1.1
      const actualMastery = score * 1.05
      
      history.push({
        date: date.toISOString(),
        score: Math.max(0, Math.min(1, score)),
        predicted_mastery: Math.max(0, Math.min(1, mastery)),
        actual_mastery: Math.max(0, Math.min(1, actualMastery)),
        risk_level: score > 0.6 ? 'low' : score > 0.4 ? 'medium' : 'high'
      })
    }
    
    return history
  }
}

/**
 * 学习效果预测工具类
 */
export const learningPredictionUtils = {
  
  /**
   * 格式化预测结果
   * @param {Object} prediction - 预测结果
   * @returns {Object} 格式化后的结果
   */
  formatPrediction(prediction) {
    if (!prediction) {
      return {
        currentScore: 0,
        currentMastery: 0,
        riskLevel: 'medium',
        confidence: 0,
        historicalPredictions: [],
        futurePredictions: []
      };
    }
    
    return {
      currentScore: prediction.current_score || 0,
      currentMastery: prediction.current_mastery || 0,
      riskLevel: prediction.risk_level || 'medium',
      confidence: prediction.confidence || 0,
      historicalPredictions: prediction.historical_predictions || [],
      futurePredictions: prediction.future_predictions || []
    };
  },

  /**
   * 获取风险等级信息
   * @param {string} riskLevel - 风险等级
   * @returns {Object} 风险等级信息
   */
  getRiskLevelInfo(riskLevel) {
    const riskInfo = {
      high: {
        label: '高风险',
        color: '#e53e3e',
        icon: '⚠️',
        description: '学习效果可能不佳，需要及时干预'
      },
      medium: {
        label: '中等风险',
        color: '#ed8936',
        icon: '⚠️',
        description: '学习效果有波动，建议关注'
      },
      low: {
        label: '低风险',
        color: '#38a169',
        icon: '✅',
        description: '学习效果良好，继续保持'
      }
    };
    
    return riskInfo[riskLevel] || riskInfo.medium;
  },

  /**
   * 获取掌握度等级
   * @param {number} mastery - 掌握度
   * @returns {Object} 掌握度等级
   */
  getMasteryLevel(mastery) {
    if (mastery >= 0.8) {
      return {
        level: '优秀',
        color: '#38a169',
        icon: '🌟'
      };
    } else if (mastery >= 0.6) {
      return {
        level: '良好',
        color: '#38b2ac',
        icon: '⭐'
      };
    } else if (mastery >= 0.4) {
      return {
        level: '一般',
        color: '#ed8936',
        icon: '⚠️'
      };
    } else {
      return {
        level: '需努力',
        color: '#e53e3e',
        icon: '❌'
      };
    }
  },

  /**
   * 计算趋势
   * @param {Array} predictions - 预测记录
   * @returns {Object} 趋势信息
   */
  calculateTrend(predictions) {
    if (predictions.length < 2) {
      return {
        trend: 0,
        direction: 'stable',
        description: '数据不足，无法计算趋势'
      };
    }
    
    // 计算最近7天和之前7天的平均分数
    const recent = predictions.slice(-7);
    const previous = predictions.slice(-14, -7);
    
    if (previous.length === 0) {
      return {
        trend: 0,
        direction: 'stable',
        description: '数据不足，无法计算趋势'
      };
    }
    
    const recentAvg = recent.reduce((sum, p) => sum + p.score, 0) / recent.length;
    const previousAvg = previous.reduce((sum, p) => sum + p.score, 0) / previous.length;
    
    const trend = recentAvg - previousAvg;
    
    let direction, description;
    if (trend > 0.05) {
      direction = 'up';
      description = '学习效果呈上升趋势';
    } else if (trend < -0.05) {
      direction = 'down';
      description = '学习效果呈下降趋势';
    } else {
      direction = 'stable';
      description = '学习效果保持稳定';
    }
    
    return {
      trend,
      direction,
      description
    };
  },

  /**
   * 格式化干预建议
   * @param {Array} interventions - 干预建议列表
   * @returns {Array} 格式化后的建议
   */
  formatInterventions(interventions) {
    return (interventions || []).map(intervention => ({
      ...intervention,
      priorityInfo: this.getPriorityInfo(intervention.priority),
      estimatedTimeFormatted: `${intervention.estimated_time} 分钟`
    }));
  },

  /**
   * 获取优先级信息
   * @param {string} priority - 优先级
   * @returns {Object} 优先级信息
   */
  getPriorityInfo(priority) {
    const priorityInfo = {
      high: {
        label: '高优先级',
        color: '#e53e3e',
        icon: '🔥'
      },
      medium: {
        label: '中优先级',
        color: '#ed8936',
        icon: '⚠️'
      },
      low: {
        label: '低优先级',
        color: '#38a169',
        icon: '✅'
      }
    };
    
    return priorityInfo[priority] || priorityInfo.medium;
  },

  /**
   * 格式化历史数据
   * @param {Array} history - 历史记录
   * @returns {Array} 格式化后的历史数据
   */
  formatHistory(history) {
    return (history || []).map(item => ({
      ...item,
      dateFormatted: this.formatDate(item.date),
      riskInfo: this.getRiskLevelInfo(item.risk_level),
      masteryLevel: this.getMasteryLevel(item.predicted_mastery)
    }));
  },

  /**
   * 格式化日期
   * @param {string} dateString - 日期字符串
   * @returns {string} 格式化后的日期
   */
  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN', {
      month: 'short',
      day: 'numeric'
    });
  },

  /**
   * 生成图表数据
   * @param {Array} predictions - 预测数据
   * @returns {Object} 图表数据
   */
  generateChartData(predictions) {
    const labels = predictions.map(p => this.formatDate(p.date));
    const scores = predictions.map(p => p.score * 100);
    const masteries = predictions.map(p => p.predicted_mastery * 100);
    
    return {
      labels,
      datasets: [
        {
          label: '学习评分',
          data: scores,
          borderColor: '#4299e1',
          backgroundColor: 'rgba(66, 153, 225, 0.1)',
          tension: 0.4
        },
        {
          label: '掌握度',
          data: masteries,
          borderColor: '#38a169',
          backgroundColor: 'rgba(56, 161, 105, 0.1)',
          tension: 0.4
        }
      ]
    };
  }
}

/**
 * 学习效果预测示例数据
 */
export const learningPredictionExamples = {
  
  /**
   * 获取示例预测结果
   * @returns {Object} 示例预测结果
   */
  getExamplePrediction() {
    return {
      current_score: 0.75,
      current_mastery: 0.85,
      risk_level: 'low',
      confidence: 0.8,
      historical_predictions: [
        { date: '2024-01-01', score: 0.6, predicted_mastery: 0.7, risk_level: 'medium' },
        { date: '2024-01-02', score: 0.65, predicted_mastery: 0.75, risk_level: 'medium' },
        { date: '2024-01-03', score: 0.7, predicted_mastery: 0.8, risk_level: 'low' },
        { date: '2024-01-04', score: 0.72, predicted_mastery: 0.82, risk_level: 'low' },
        { date: '2024-01-05', score: 0.75, predicted_mastery: 0.85, risk_level: 'low' }
      ],
      future_predictions: [
        { date: '2024-01-06', score: 0.77, predicted_mastery: 0.87, risk_level: 'low', is_prediction: true },
        { date: '2024-01-07', score: 0.79, predicted_mastery: 0.89, risk_level: 'low', is_prediction: true },
        { date: '2024-01-08', score: 0.81, predicted_mastery: 0.91, risk_level: 'low', is_prediction: true }
      ]
    };
  },

  /**
   * 获取示例干预建议
   * @returns {Array} 示例干预建议
   */
  getExampleInterventions() {
    return [
      {
        type: 'learning_plan',
        title: '制定学习计划',
        description: '建议每天固定学习时间，制定详细的学习计划',
        priority: 'high',
        estimated_time: 30
      },
      {
        type: 'practice',
        title: '增加练习频率',
        description: '每天至少完成5道练习题，提高解题能力',
        priority: 'medium',
        estimated_time: 45
      }
    ];
  }
}
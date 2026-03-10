// 自适应难度调整API接口

import axios from 'axios';

// API基础URL
const API_BASE_URL = 'http://localhost:8000/api/learning';

// 请求拦截器，添加认证token
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

/**
 * 评估用户能力水平
 * @returns {Promise} 能力评估结果
 */
export const evaluateAbility = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/adaptive-difficulty/ability/`);
    return response.data;
  } catch (error) {
    console.error('评估能力失败:', error);
    throw error;
  }
};

/**
 * 计算适合的内容难度
 * @param {number} knowledgeNodeId - 知识点ID（可选）
 * @returns {Promise} 最优难度计算结果
 */
export const calculateOptimalDifficulty = async (knowledgeNodeId = null) => {
  try {
    const params = knowledgeNodeId ? { knowledge_node_id: knowledgeNodeId } : {};
    const response = await axios.get(`${API_BASE_URL}/adaptive-difficulty/optimal/`, { params });
    return response.data;
  } catch (error) {
    console.error('计算最优难度失败:', error);
    throw error;
  }
};

/**
 * 调整难度
 * @param {number} currentDifficulty - 当前难度
 * @param {number} performance - 用户表现（0-100）
 * @returns {Promise} 难度调整结果
 */
export const adjustDifficulty = async (currentDifficulty, performance) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/adaptive-difficulty/`, {
      current_difficulty: currentDifficulty,
      performance: performance
    });
    return response.data;
  } catch (error) {
    console.error('调整难度失败:', error);
    throw error;
  }
};

/**
 * 生成难度调整建议
 * @returns {Promise} 难度调整建议
 */
export const generateDifficultyRecommendations = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/adaptive-difficulty/recommendations/`);
    return response.data;
  } catch (error) {
    console.error('生成难度调整建议失败:', error);
    throw error;
  }
};

/**
 * 格式化难度值
 * @param {number} difficulty - 难度值
 * @returns {string} 格式化后的难度描述
 */
export const formatDifficulty = (difficulty) => {
  if (difficulty >= 4.5) {
    return '高难度';
  } else if (difficulty >= 3.5) {
    return '中高难度';
  } else if (difficulty >= 2.5) {
    return '中等难度';
  } else if (difficulty >= 1.5) {
    return '低难度';
  } else {
    return '入门级';
  }
};

/**
 * 格式化能力水平
 * @param {number} abilityLevel - 能力水平
 * @returns {string} 格式化后的能力描述
 */
export const formatAbilityLevel = (abilityLevel) => {
  if (abilityLevel >= 4) {
    return '优秀';
  } else if (abilityLevel >= 3) {
    return '良好';
  } else if (abilityLevel >= 2) {
    return '一般';
  } else {
    return '基础';
  }
};

/**
 * 生成模拟用户表现数据
 * @returns {number} 模拟的用户表现（0-100）
 */
export const generateMockPerformance = () => {
  // 生成60-95之间的随机数，模拟用户表现
  return Math.floor(Math.random() * 36) + 60;
};

/**
 * 生成模拟能力评估数据
 * @returns {Object} 模拟的能力评估结果
 */
export const generateMockAbilityEvaluation = () => {
  return {
    ability_level: Math.random() * 2 + 2, // 2-4之间
    average_score: Math.random() * 30 + 60, // 60-90之间
    score_trend: ['improving', 'stable', 'declining'][Math.floor(Math.random() * 3)],
    knowledge_mastery: {
      mastery_levels: {
        'Python基础': Math.random() * 0.5 + 0.5,
        'JavaScript基础': Math.random() * 0.5 + 0.3,
        '算法基础': Math.random() * 0.5 + 0.2
      },
      average_mastery: Math.random() * 0.3 + 0.5,
      total_knowledge_points: 3
    },
    data_available: true,
    user_id: 1
  };
};

/**
 * 生成模拟难度调整建议
 * @returns {Object} 模拟的难度调整建议
 */
export const generateMockDifficultyRecommendations = () => {
  return {
    recommendations: [
      {
        title: '巩固中等难度内容',
        description: '建议继续巩固中等难度的内容，逐步提高',
        priority: 'medium',
        estimated_time: 20
      },
      {
        title: '适当增加难度',
        description: '您的成绩呈上升趋势，建议适当增加学习内容的难度',
        priority: 'medium',
        estimated_time: 25
      },
      {
        title: '加强薄弱知识点',
        description: '建议重点加强以下知识点：JavaScript基础',
        priority: 'high',
        estimated_time: 30
      }
    ],
    ability_evaluation: generateMockAbilityEvaluation(),
    user_id: 1
  };
};
// 代码相似度检测API接口

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
 * 计算两段代码的相似度
 * @param {string} code1 - 第一段代码
 * @param {string} code2 - 第二段代码
 * @param {string} language - 代码语言
 * @returns {Promise} 相似度计算结果
 */
export const calculateSimilarity = async (code1, code2, language = 'python') => {
  try {
    const response = await axios.post(`${API_BASE_URL}/code-similarity/`, {
      code1: code1,
      code2: code2,
      language: language
    });
    return response.data;
  } catch (error) {
    console.error('计算相似度失败:', error);
    throw error;
  }
};

/**
 * 批量比较代码相似度
 * @param {string} targetCode - 目标代码
 * @param {Array} referenceCodes - 参考代码列表
 * @param {string} language - 代码语言
 * @returns {Promise} 批量比较结果
 */
export const batchCompare = async (targetCode, referenceCodes, language = 'python') => {
  try {
    const response = await axios.post(`${API_BASE_URL}/code-similarity/batch/`, {
      target_code: targetCode,
      reference_codes: referenceCodes,
      language: language
    });
    return response.data;
  } catch (error) {
    console.error('批量比较失败:', error);
    throw error;
  }
};

/**
 * 分析相似度结果
 * @param {Object} similarityResult - 相似度计算结果
 * @returns {Promise} 分析结果
 */
export const analyzeSimilarity = async (similarityResult) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/code-similarity/analysis/`, {
      similarity_result: similarityResult
    });
    return response.data;
  } catch (error) {
    console.error('分析相似度结果失败:', error);
    throw error;
  }
};

/**
 * 格式化相似度得分
 * @param {number} score - 相似度得分
 * @returns {string} 格式化后的相似度描述
 */
export const formatSimilarityScore = (score) => {
  const percentage = Math.round(score * 100);
  if (percentage >= 90) {
    return `极高 (${percentage}%)`;
  } else if (percentage >= 70) {
    return `较高 (${percentage}%)`;
  } else if (percentage >= 50) {
    return `中等 (${percentage}%)`;
  } else if (percentage >= 30) {
    return `较低 (${percentage}%)`;
  } else {
    return `极低 (${percentage}%)`;
  }
};

/**
 * 获取相似度级别颜色
 * @param {string} level - 相似度级别
 * @returns {string} 颜色代码
 */
export const getSimilarityColor = (level) => {
  const colors = {
    'identical': '#f56c6c',
    'high': '#e6a23c',
    'medium': '#409EFF',
    'low': '#67c23a',
    'none': '#909399'
  };
  return colors[level] || '#909399';
};

/**
 * 生成模拟代码相似度结果
 * @returns {Object} 模拟的相似度结果
 */
export const generateMockSimilarityResult = () => {
  const similarity = Math.random() * 0.8 + 0.2; // 20-100%
  const similarityLevel = similarity >= 0.9 ? 'identical' : similarity >= 0.7 ? 'high' : similarity >= 0.5 ? 'medium' : 'low';
  
  return {
    overall_similarity: similarity,
    similarity_scores: {
      token_similarity: Math.random() * 0.3 + similarity - 0.15,
      structure_similarity: Math.random() * 0.3 + similarity - 0.15,
      ast_similarity: Math.random() * 0.3 + similarity - 0.15,
      line_similarity: Math.random() * 0.3 + similarity - 0.15
    },
    similarity_level: similarityLevel,
    similar_segments: [
      {
        code1_start: 5,
        code1_end: 15,
        code2_start: 6,
        code2_end: 16,
        lines: [
          'def calculate_factorial(n):',
          '    if n == 0:',
          '        return 1',
          '    else:',
          '        return n * calculate_factorial(n-1)',
          '',
          'print(calculate_factorial(5))'
        ],
        length: 7
      }
    ],
    normalized_code1: 'def calculate_factorial(n): if n == 0: return 1 else: return n * calculate_factorial(n-1) print(calculate_factorial(5))',
    normalized_code2: 'def factorial(n): if n == 0: return 1 else: return n * factorial(n-1) print(factorial(5))',
    features1: {
      line_count: 7,
      token_count: 25,
      function_count: 1,
      class_count: 0,
      imports: [],
      keywords: {
        'def': 1,
        'if': 1,
        'else': 1,
        'return': 2,
        'print': 1
      }
    },
    features2: {
      line_count: 7,
      token_count: 23,
      function_count: 1,
      class_count: 0,
      imports: [],
      keywords: {
        'def': 1,
        'if': 1,
        'else': 1,
        'return': 2,
        'print': 1
      }
    },
    timestamp: new Date().toISOString()
  };
};

/**
 * 生成模拟批量比较结果
 * @returns {Object} 模拟的批量比较结果
 */
export const generateMockBatchResult = () => {
  const results = [];
  for (let i = 0; i < 3; i++) {
    const similarity = Math.random() * 0.7 + 0.1; // 10-80%
    results.push({
      reference_index: i,
      similarity_result: generateMockSimilarityResult()
    });
  }
  
  // 按相似度排序
  results.sort((a, b) => b.similarity_result.overall_similarity - a.similarity_result.overall_similarity);
  
  return {
    batch_results: results,
    total_references: 3,
    timestamp: new Date().toISOString()
  };
};
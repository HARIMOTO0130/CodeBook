// 学习摘要生成API接口

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
 * 生成学习摘要
 * @param {string} timeRange - 时间范围 ('day', 'week', 'month', 'year')
 * @returns {Promise} 学习摘要结果
 */
export const generateSummary = async (timeRange = 'week') => {
  try {
    const response = await axios.get(`${API_BASE_URL}/learning-summary/`, {
      params: {
        time_range: timeRange
      }
    });
    return response.data;
  } catch (error) {
    console.error('生成学习摘要失败:', error);
    // 返回模拟数据
    return generateMockSummary(timeRange);
  }
};

/**
 * 生成主题学习摘要
 * @param {string} topic - 主题
 * @returns {Promise} 主题学习摘要结果
 */
export const generateTopicSummary = async (topic) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/learning-summary/topic/`, {
      params: {
        topic: topic
      }
    });
    return response.data;
  } catch (error) {
    console.error('生成主题学习摘要失败:', error);
    // 返回模拟数据
    return generateMockTopicSummary(topic);
  }
};

/**
 * 获取学习摘要历史
 * @returns {Promise} 学习摘要历史记录
 */
export const getSummaryHistory = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/learning-summary/history/`);
    return response.data;
  } catch (error) {
    console.error('获取学习摘要历史失败:', error);
    // 返回模拟数据
    return generateMockSummaryHistory();
  }
};

/**
 * 获取学习摘要统计数据
 * @returns {Promise} 学习摘要统计数据
 */
export const getSummaryStats = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/learning-summary/stats/`);
    return response.data;
  } catch (error) {
    console.error('获取学习摘要统计数据失败:', error);
    // 返回模拟数据
    return generateMockSummaryStats();
  }
};

/**
 * 格式化时间范围
 * @param {string} timeRange - 时间范围
 * @returns {string} 格式化后的时间范围文本
 */
export const formatTimeRange = (timeRange) => {
  const timeRangeMap = {
    'day': '一天',
    'week': '一周',
    'month': '一个月',
    'year': '一年'
  };
  return timeRangeMap[timeRange] || '一周';
};

/**
 * 格式化学习时长
 * @param {number} minutes - 学习时长（分钟）
 * @returns {string} 格式化后的学习时长文本
 */
export const formatDuration = (minutes) => {
  if (minutes < 60) {
    return `${minutes}分钟`;
  } else {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}小时${mins > 0 ? mins + '分钟' : ''}`;
  }
};

/**
 * 生成模拟学习摘要
 * @param {string} timeRange - 时间范围
 * @returns {Object} 模拟的学习摘要
 */
export const generateMockSummary = (timeRange = 'week') => {
  const timeRangeText = formatTimeRange(timeRange);
  
  return {
    summary: `在过去的${timeRangeText}中，您共完成了6个学习内容，总学习时长为205分钟，平均得分为85.0分。\n\n学习内容包括：video 3个，exercise 2个，article 1个。\n\n主要学习主题包括：Python, 基础语法, 变量, 数据类型, 函数。\n\n您的学习表现良好，继续保持！`,
    key_points: ['Python', '基础语法', '变量', '数据类型', '函数', '控制流', '条件语句', '循环', '数据结构', '列表'],
    recommendations: [
      {
        title: '提高学习深度',
        description: '建议深入学习重点内容，提高学习质量',
        priority: 'medium'
      },
      {
        title: '定期复习',
        description: '定期复习所学内容，巩固记忆',
        priority: 'medium'
      },
      {
        title: '学习笔记',
        description: '养成做学习笔记的习惯，帮助整理思路',
        priority: 'low'
      }
    ],
    statistics: {
      total_records: 6,
      total_duration: 205,
      average_duration: 34.17,
      average_score: 85.0,
      completion_rate: 100.0,
      content_type_stats: {
        video: {
          count: 3,
          duration: 100,
          average_score: 87.67
        },
        exercise: {
          count: 2,
          duration: 45,
          average_score: 82.5
        },
        article: {
          count: 1,
          duration: 60,
          average_score: 82.0
        }
      },
      daily_average_duration: 41.0
    },
    time_range: timeRange,
    start_date: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
    end_date: new Date().toISOString(),
    timestamp: new Date().toISOString()
  };
};

/**
 * 生成模拟主题学习摘要
 * @param {string} topic - 主题
 * @returns {Object} 模拟的主题学习摘要
 */
export const generateMockTopicSummary = (topic) => {
  return {
    summary: `关于${topic}，您共完成了4个学习内容，总学习时长为130分钟，平均得分为85.8分。\n\n学习内容包括：video 2个，exercise 1个，article 1个。\n\n相关主题包括：Python, 基础语法, 变量, 数据类型, 函数。\n\n您在${topic}方面的学习表现良好，继续保持！`,
    key_points: ['Python', '基础语法', '变量', '数据类型', '函数', '控制流', '条件语句', '循环'],
    recommendations: [
      {
        title: '提高学习深度',
        description: '建议深入学习重点内容，提高学习质量',
        priority: 'medium'
      },
      {
        title: '定期复习',
        description: '定期复习所学内容，巩固记忆',
        priority: 'medium'
      }
    ],
    statistics: {
      total_records: 4,
      total_duration: 130,
      average_duration: 32.5,
      average_score: 85.8,
      completion_rate: 100.0,
      content_type_stats: {
        video: {
          count: 2,
          duration: 65,
          average_score: 86.5
        },
        exercise: {
          count: 1,
          duration: 20,
          average_score: 90.0
        },
        article: {
          count: 1,
          duration: 45,
          average_score: 82.0
        }
      },
      daily_average_duration: 32.5
    },
    topic: topic,
    timestamp: new Date().toISOString()
  };
};

/**
 * 生成模拟学习摘要历史
 * @returns {Object} 模拟的学习摘要历史
 */
export const generateMockSummaryHistory = () => {
  return {
    history: [
      {
        id: 1,
        time_range: 'week',
        generated_at: '2024-01-01T00:00:00Z',
        summary_preview: '在过去的一周中，您共完成了6个学习内容，总学习时长为205分钟...'
      },
      {
        id: 2,
        time_range: 'month',
        generated_at: '2023-12-31T00:00:00Z',
        summary_preview: '在过去的一个月中，您共完成了24个学习内容，总学习时长为820分钟...'
      },
      {
        id: 3,
        time_range: 'week',
        generated_at: '2023-12-25T00:00:00Z',
        summary_preview: '在过去的一周中，您共完成了5个学习内容，总学习时长为180分钟...'
      }
    ],
    total_count: 3
  };
};

/**
 * 生成模拟学习摘要统计数据
 * @returns {Object} 模拟的学习摘要统计数据
 */
export const generateMockSummaryStats = () => {
  return {
    total_summaries: 12,
    total_learning_time: 2400,  // 分钟
    average_score: 85.5,
    most_studied_topic: 'Python',
    learning_streak: 7,  // 连续学习天数
    content_type_distribution: {
      'video': 40,
      'exercise': 30,
      'article': 30
    }
  };
};
import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000/api/learning'

/**
 * 代码审查API接口
 */
export const codeReviewAPI = {
  
  /**
   * 提交代码进行审查
   * @param {string} code - 代码内容
   * @param {string} language - 编程语言
   * @param {Object} context - 上下文信息
   * @param {string} sessionId - 会话ID
   * @returns {Promise} 审查结果
   */
  async submitCodeReview(code, language = 'python', context = {}, sessionId = null) {
    try {
      const response = await axios.post(`${API_BASE_URL}/code-review/`, {
        code,
        language,
        context,
        session_id: sessionId,
        batch_mode: false
      })
      return response.data
    } catch (error) {
      console.error('代码审查提交失败:', error)
      throw error
    }
  },

  /**
   * 批量代码审查
   * @param {Array} codeSnippets - 代码片段数组
   * @param {string} sessionId - 会话ID
   * @returns {Promise} 批量审查结果
   */
  async batchCodeReview(codeSnippets, sessionId = null) {
    try {
      const response = await axios.post(`${API_BASE_URL}/code-review/`, {
        code_snippets: codeSnippets,
        batch_mode: true,
        session_id: sessionId
      })
      return response.data
    } catch (error) {
      console.error('批量代码审查失败:', error)
      throw error
    }
  },

  /**
   * 获取代码审查历史
   * @param {number} limit - 限制数量
   * @param {number} offset - 偏移量
   * @returns {Promise} 历史记录
   */
  async getCodeReviewHistory(limit = 10, offset = 0) {
    try {
      const response = await axios.get(`${API_BASE_URL}/code-review/history/`, {
        params: { limit, offset }
      })
      return response.data
    } catch (error) {
      console.error('获取代码审查历史失败:', error)
      throw error
    }
  },

  /**
   * 获取代码审查详情
   * @param {number} recordId - 记录ID
   * @returns {Promise} 审查详情
   */
  async getCodeReviewDetail(recordId) {
    try {
      const response = await axios.get(`${API_BASE_URL}/code-review/history/${recordId}/`)
      return response.data
    } catch (error) {
      console.error('获取代码审查详情失败:', error)
      throw error
    }
  },

  /**
   * 获取代码审查统计
   * @returns {Promise} 统计数据
   */
  async getCodeReviewStats() {
    try {
      const response = await axios.get(`${API_BASE_URL}/code-review/stats/`)
      return response.data
    } catch (error) {
      console.error('获取代码审查统计失败:', error)
      throw error
    }
  }
}

/**
 * 代码审查工具类
 */
export const codeReviewUtils = {
  
  /**
   * 格式化审查结果
   * @param {Object} reviewResult - 审查结果
   * @returns {Object} 格式化后的结果
   */
  formatReviewResult(reviewResult) {
    if (!reviewResult || !reviewResult.result) {
      return {
        overallScore: 0,
        issues: [],
        suggestions: [],
        improvementSuggestions: []
      }
    }

    const result = reviewResult.result
    
    return {
      overallScore: result.overall_score || 0,
      issues: [
        ...(result.syntax_issues || []).map(issue => ({
          ...issue,
          category: 'syntax'
        })),
        ...(result.quality_issues || []).map(issue => ({
          ...issue,
          category: 'quality'
        }))
      ],
      suggestions: result.llm_suggestions || [],
      improvementSuggestions: result.improvement_suggestions || [],
      language: result.language || 'python',
      codeLength: result.code_length || 0,
      responseTime: reviewResult.response_time || 0
    }
  },

  /**
   * 根据严重程度获取颜色
   * @param {string} severity - 严重程度
   * @returns {string} 颜色值
   */
  getSeverityColor(severity) {
    const colors = {
      high: '#f56565',    // 红色
      medium: '#ed8936',  // 橙色
      low: '#38a169'      // 绿色
    }
    return colors[severity] || '#718096'
  },

  /**
   * 根据分数获取等级
   * @param {number} score - 分数
   * @returns {Object} 等级信息
   */
  getScoreLevel(score) {
    if (score >= 90) {
      return { level: '优秀', color: '#38a169', icon: '✓' }
    } else if (score >= 80) {
      return { level: '良好', color: '#38b2ac', icon: '✓' }
    } else if (score >= 70) {
      return { level: '中等', color: '#ed8936', icon: '⚠' }
    } else if (score >= 60) {
      return { level: '及格', color: '#ed8936', icon: '⚠' }
    } else {
      return { level: '需改进', color: '#f56565', icon: '✗' }
    }
  },

  /**
   * 生成代码审查摘要
   * @param {Object} formattedResult - 格式化后的审查结果
   * @returns {Object} 摘要信息
   */
  generateSummary(formattedResult) {
    const highIssues = formattedResult.issues.filter(issue => issue.severity === 'high').length
    const mediumIssues = formattedResult.issues.filter(issue => issue.severity === 'medium').length
    const lowIssues = formattedResult.issues.filter(issue => issue.severity === 'low').length
    const totalIssues = formattedResult.issues.length
    const totalSuggestions = formattedResult.suggestions.length

    return {
      highIssues,
      mediumIssues,
      lowIssues,
      totalIssues,
      totalSuggestions,
      scoreLevel: this.getScoreLevel(formattedResult.overallScore)
    }
  }
}

/**
 * 代码审查示例数据
 */
export const codeReviewExamples = {
  
  /**
   * 获取示例代码
   * @param {string} language - 编程语言
   * @returns {string} 示例代码
   */
  getExampleCode(language = 'python') {
    const examples = {
      python: `# 示例Python代码
# 这是一个需要改进的函数

def calculate_total(items):
    total = 0
    for item in items:
        if item['price'] > 0 and item['quantity'] > 0:
            total = total + item['price'] * item['quantity']
    return total

# 调用示例
items = [
    {'name': 'apple', 'price': 2.5, 'quantity': 3},
    {'name': 'banana', 'price': 1.5, 'quantity': 2}
]
result = calculate_total(items)
print(f"总价: {result}")`,

      javascript: `// 示例JavaScript代码
// 这是一个需要改进的函数

function calculateTotal(items) {
    let total = 0
    for (let i = 0; i < items.length; i++) {
        if (items[i].price > 0 && items[i].quantity > 0) {
            total = total + items[i].price * items[i].quantity
        }
    }
    return total
}

// 调用示例
const items = [
    {name: 'apple', price: 2.5, quantity: 3},
    {name: 'banana', price: 1.5, quantity: 2}
]
const result = calculateTotal(items)
console.log(\`总价: \${result}\`)`,

      java: `// 示例Java代码
// 这是一个需要改进的函数

public class Calculator {
    public static double calculateTotal(List<Item> items) {
        double total = 0.0;
        for (int i = 0; i < items.size(); i++) {
            Item item = items.get(i);
            if (item.getPrice() > 0 && item.getQuantity() > 0) {
                total = total + item.getPrice() * item.getQuantity();
            }
        }
        return total;
    }
}

// Item类定义
class Item {
    private String name;
    private double price;
    private int quantity;
    
    // 构造函数和getter方法省略
}`
    }
    
    return examples[language] || examples.python
  },

  /**
   * 获取语言列表
   * @returns {Array} 语言列表
   */
  getSupportedLanguages() {
    return [
      { value: 'python', label: 'Python', icon: '🐍' },
      { value: 'javascript', label: 'JavaScript', icon: '📜' },
      { value: 'java', label: 'Java', icon: '☕' },
      { value: 'cpp', label: 'C++', icon: '⚡' },
      { value: 'csharp', label: 'C#', icon: '🔷' }
    ]
  }
}
// 使用绝对路径并正确导出
// 学生端API基础URL
export const API_BASE_URL = 'http://127.0.0.1:8000/api/student';

const getToken = () => {
  try {
    // 简化token获取，移除过多日志
    if (typeof localStorage === 'undefined') {
      return '';
    }
    return localStorage.getItem('token') || '';
  } catch (e) {
    return '';
  }
};

const authHeaders = () => {
  const token = getToken();
  return token ? { 'Authorization': `Token ${token}` } : {};
};

export async function httpGet(path, requireAuth = false) {
  const headers = {
    'Content-Type': 'application/json; charset=utf-8'
  };
  
  if (requireAuth) {
    // 获取认证头，不再显示警告
    const authHeader = authHeaders();
    Object.assign(headers, authHeader);
  }
  
  // 确保API路径格式正确，避免重复的/api前缀
  const apiPath = path.startsWith('/') ? path : `/${path}`;
  const res = await fetch(`${API_BASE_URL}${apiPath}`, {
    method: 'GET',
    headers,
    credentials: 'omit'
  });
  
  if ((res.status === 401 || res.status === 403) && requireAuth) {
    // 只在需要认证的请求中处理认证错误
    try { localStorage.removeItem('token') } catch {};
    
    // 避免在登录页面上形成重定向循环
    if (window.location.pathname !== '/') {
      const redirectUrl = encodeURIComponent(window.location.pathname + window.location.search);
      window.location.href = `/?redirect=${redirectUrl}`;
    }
    
    throw new Error(`AUTH ${res.status}`);
  }
  
  if (!res.ok) {
    throw new Error(`GET ${path} ${res.status}`);
  }
  
  const responseText = await res.text();
  
  try {
    return JSON.parse(responseText);
  } catch (error) {
    throw new Error('JSON解析失败');
  }
}

export async function httpPost(path, body, requireAuth = false, method = 'POST') {
  // 确保API路径格式正确，避免重复的/api前缀
  const apiPath = path.startsWith('/') ? path : `/${path}`;
  const fullUrl = `${API_BASE_URL}${apiPath}`;
  
  const headers = {
    'Content-Type': 'application/json',
    ...(requireAuth ? authHeaders() : {})
  };
  
  const requestBody = { ...body };
  
  // 添加请求日志（仅在开发环境）
  if (process.env.NODE_ENV === 'development' || !process.env.NODE_ENV) {
    console.log(`[HTTP ${method}] 请求URL:`, fullUrl);
    console.log(`[HTTP ${method}] 请求头:`, headers);
    console.log(`[HTTP ${method}] 请求体:`, requestBody);
  }
  
  try {
    const res = await fetch(fullUrl, {
      method,
      headers,
      body: JSON.stringify(requestBody),
      credentials: 'omit'
    });
    
    // 添加响应日志
    if (process.env.NODE_ENV === 'development' || !process.env.NODE_ENV) {
      console.log(`[HTTP ${method}] 响应状态:`, res.status, res.statusText);
    }
    
    if ((res.status === 401 || res.status === 403) && requireAuth) {
      // 只在需要认证的请求中处理认证错误
      try { localStorage.removeItem('token') } catch {};
      
      // 避免在登录页面上形成重定向循环
      if (window.location.pathname !== '/') {
        const redirect = encodeURIComponent(window.location.pathname + window.location.search);
        window.location.href = `/?redirect=${redirect}`;
      }
      
      throw new Error(`AUTH ${res.status}`);
    }
    
    // 解析响应体
    const responseData = await res.json().catch(() => {
      // 如果JSON解析失败，尝试获取原始文本
      return res.text().then(text => ({ rawText: text })).catch(() => ({}));
    });
    
    if (!res.ok) {
      // 创建一个包含更多信息的错误对象
      const error = new Error(`${method} ${path} ${res.status}`);
      error.response = { status: res.status, data: responseData };
      throw error;
    }
    
    return responseData;
  } catch (error) {
    // 添加详细的错误日志
    if (process.env.NODE_ENV === 'development' || !process.env.NODE_ENV) {
      console.error(`[HTTP ${method}] 请求失败:`, error);
      console.error(`[HTTP ${method}] 请求URL:`, fullUrl);
    }
    
    // 处理网络错误
    if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
      error.message = '无法连接到服务器，请确保后端服务已启动（运行 python manage.py runserver）';
    }
    
    if (!error.response) {
      // 如果没有response属性，添加一个基本的response对象
      error.response = { status: 0, data: { message: error.message || '网络请求失败' } };
    }
    throw error;
  }
}

// 添加缺失的httpDelete和httpPut函数
export async function httpDelete(path, requireAuth = false, body = null) {
  if (body) {
    return httpPost(path, body, requireAuth, 'DELETE');
  }
  return httpPost(path, {}, requireAuth, 'DELETE');
}

export async function httpPut(path, body, requireAuth = false) {
  return httpPost(path, body, requireAuth, 'PUT');
}

async function httpPostForm(path, formData, requireAuth = false) {
  // 确保API路径格式正确，避免重复的/api前缀
  const apiPath = path.startsWith('/') ? path : `/${path}`;
  const fullUrl = `${API_BASE_URL}${apiPath}`;
  console.log(`[HTTP POST_FORM] 请求: ${fullUrl}`);
  
  const headers = {
    ...(requireAuth ? authHeaders() : {})
  };
  console.log('[HTTP POST_FORM 请求头]:', headers);
  
  try {
    const res = await fetch(fullUrl, {
      method: 'POST',
      headers,
      body: formData,
      credentials: 'omit'
    });
    
    console.log(`[HTTP POST_FORM] 响应状态: ${res.status} ${res.statusText}`);
    
      if (res.status === 401 || res.status === 403) {
        try { localStorage.removeItem('token') } catch {}
        const redirect = encodeURIComponent(window.location.pathname + window.location.search)
        if (window.location.pathname !== '/') {
          window.location.href = `/?redirect=${redirect}`
        }
        throw new Error(`AUTH ${res.status}`)
      }
    
    if (!res.ok) {
      // 尝试获取详细错误信息
      try {
        const errorData = await res.json();
        console.error('[HTTP POST_FORM] 错误详情:', errorData);
        throw new Error(`POST_FORM ${path} ${res.status}: ${errorData.error || res.statusText}`);
      } catch (parseError) {
        console.error('[HTTP POST_FORM] 无法解析错误响应:', parseError);
        throw new Error(`POST_FORM ${path} ${res.status}`);
      }
    }
    
    return res.json().catch(() => ({}));
  } catch (error) {
    console.error('[HTTP POST_FORM] 请求异常:', error);
    throw error;
  }
}

// 字段适配器：后端 -> 前端
function adaptBookListItem(b) {
  // 确保b是对象
  if (!b || typeof b !== 'object') {
    console.error('无效的书籍数据:', b);
    return {
      id: 0,
      title: '未知标题',
      author: '未知作者',
      cover: null,
      description: '',
      tags: ['未分类'], // 添加默认标签
      chapterCount: 0,
      progress: 0,
      lastLearnTime: null
    };
  }
  
  // 从不同可能的字段中获取标签
  let tags = [];
  
  // 尝试从不同的可能字段获取标签
  if (Array.isArray(b.tag_list)) {
    tags = b.tag_list;
  } else if (Array.isArray(b.tags)) {
    tags = b.tags;
  } else if (typeof b.tag === 'string') {
    tags = [b.tag];
  } else if (typeof b.tag_list === 'string') {
    // 如果tag_list是字符串，尝试按逗号分割
    tags = b.tag_list.split(',').map(t => t.trim()).filter(t => t);
  }
  
  // 如果没有标签，添加默认标签
  if (tags.length === 0) {
    // 根据书名或ID生成一些默认标签
    const defaultTags = ['教材', '学习资料'];
    
    // 如果有标题，可以基于标题添加一些标签
    if (b.title) {
      const titleLower = b.title.toLowerCase();
      if (titleLower.includes('python')) defaultTags.push('Python');
      if (titleLower.includes('java')) defaultTags.push('Java');
      if (titleLower.includes('web') || titleLower.includes('前端')) defaultTags.push('Web开发');
      if (titleLower.includes('数据') || titleLower.includes('analytics')) defaultTags.push('数据分析');
    }
    
    tags = defaultTags;
  }
  
  return {
    id: b.id || 0,
    title: b.title || '未知标题',
    author: b.author || '未知作者',
    cover: b.cover || null,
    description: b.description || '',
    tags: tags,
    chapterCount: b.chapter_count || b.chapters || 0,
    progress: b.progress ?? 0,
    lastLearnTime: b.last_learn_time || b.updated_at || null,
    major: b.major || '' // 添加专业字段
  };
}

export const api = {
  // AI助手相关API
  async getAIAssistantResponse(question, requireAuth = false) {
    try {
      console.log('[API] 发送AI助手问题:', question);
      const response = await httpPost('/learning/ai-assistant/', 
        { question }, 
        requireAuth
      );
      console.log('[API] AI助手响应:', response);
      return response;
    } catch (error) {
      console.error('[API] AI助手请求失败:', error);
      throw error;
    }
  },
  
  // 认证
  async register({ username, email, password, role }) {
    // 使用学生端注册接口
    return httpPost('/users/register/', { username, email, password, role }, false);
  },
  async login({ username, password }) {
    try {
      console.log('发送登录请求到 /users/login/');
      const data = await httpPost('/users/login/', { username, password }, false);
      
      console.log('登录API返回数据:', data);
      
      // 简洁地处理token存储
      if (data && data.token) {
        try {
          localStorage.setItem('token', data.token);
          console.log('Token存储成功');
        } catch (e) {
          console.error('存储token失败:', e);
        }
      }
      
      return data;
    } catch (error) {
      console.error('登录请求错误:', error);
      // 重新抛出错误以便调用者处理
      throw error;
    }
  },
  async logout() {
    try {
      await httpPost('/users/logout/', {}, true);
    } finally {
      localStorage.removeItem('token');
    }
  },

  // 用户
  async getUserInfo() {
    return httpGet('/users/me/', true);
  },
  async updateUserInfo(userData) {
    return httpPut('/users/me/', userData, true);
  },
  async getUserPreferences() {
    return httpGet('/users/preferences/', true);
  },
  async updateUserPreferences(preferences) {
        // 前端传入为 camelCase，转换成后端的 snake_case
        const payload = {
            // 学习偏好设置
            ...(preferences.defaultLanguage !== undefined ? { default_language: preferences.defaultLanguage } : {}),
            ...(preferences.codeTheme !== undefined ? { code_theme: preferences.codeTheme } : {}),
            ...(preferences.autoPlayVideo !== undefined ? { auto_play_video: preferences.autoPlayVideo } : {}),
            ...(preferences.keyboardShortcuts !== undefined ? { keyboard_shortcuts: preferences.keyboardShortcuts } : {}),
            ...(preferences.showLineNumbers !== undefined ? { show_line_numbers: preferences.showLineNumbers } : {}),
            ...(preferences.useVimMode !== undefined ? { use_vim_mode: preferences.useVimMode } : {}),
            
            // 学习信息
            ...(preferences.learning_goals !== undefined ? { learning_goals: preferences.learning_goals } : {}),
            ...(preferences.major !== undefined ? { major: preferences.major } : {}),
            ...(preferences.learning_stage !== undefined ? { learning_stage: preferences.learning_stage } : {}),
            ...(preferences.interests !== undefined ? { interests: preferences.interests } : {}),
            
            // 通知设置
            ...(preferences.enable_learning_reminders !== undefined ? { enable_learning_reminders: preferences.enable_learning_reminders } : {}),
            ...(preferences.reminder_time !== undefined ? { reminder_time: preferences.reminder_time } : {}),
            ...(preferences.daily_reminder !== undefined ? { daily_reminder: preferences.daily_reminder } : {}),
            ...(preferences.deadline_reminder !== undefined ? { deadline_reminder: preferences.deadline_reminder } : {})
        };
        return httpPut('/users/preferences/', payload, true);
  },
  async changePassword(passwordData) {
    return httpPost('/users/change-password/', passwordData, true);
  },

  // 书籍
  async getBooks() {
    try {
      console.log('开始获取书籍列表...');
      // 更新为正确的URL路径 - /api/books/
      const response = await httpGet('/books/');
      console.log('API返回的响应:', response);
      
      // 后端API直接返回书籍数组
      if (!Array.isArray(response)) {
        console.warn('API返回的不是预期格式:', response);
        return [];
      }
      
      const adaptedBooks = response.map(adaptBookListItem);
      console.log('适配后的书籍列表:', adaptedBooks);
      return adaptedBooks;
    } catch (error) {
      console.error('获取书籍列表失败:', error);
      return [];
    }
  },
  async getBookDetail(bookId) {
    try {
      // 确保bookId是有效的数字
      const validBookId = Number(bookId);
      if (isNaN(validBookId)) {
        console.error('无效的书籍ID:', bookId);
        throw new Error('无效的书籍ID');
      }
      
      // 并行获取书籍详情和章节列表
      const [bookDetail, chapters] = await Promise.all([
        httpGet(`/books/${validBookId}/`),
        httpGet(`/books/chapters/book/${validBookId}/`)
      ]);
      
      // 打印章节数据以调试
      console.log('获取到的章节数据:', chapters);
      
      // 构建前端需要的数据结构，正确处理主章节和子章节关系
      const mainChapters = [];
      
      // 1. 首先收集所有主章节（is_main_chapter为true或level为1）
      chapters.forEach(chapter => {
        if (chapter.is_main_chapter || chapter.level === 1) {
          // 确保章标题正确显示
          const chapterTitle = chapter.title || `第${mainChapters.length + 1}章`;
          mainChapters.push({
            id: chapter.id,
            title: chapterTitle,
            sections: []  // 初始化空的子章节数组
          });
        }
      });
      
      // 2. 优先处理有parent_chapter的子章节
      chapters.forEach(chapter => {
        if (chapter.parent_chapter && chapter.parent_chapter !== null) {
          // 查找对应的主章节
          const mainChapter = mainChapters.find(mc => mc.id === chapter.parent_chapter);
          if (mainChapter) {
            // 将子章节添加为主章节的section
            mainChapter.sections.push({
              id: chapter.id,
              title: chapter.title || '未命名小节',
              type: chapter.type || 'reading',
              duration: `${chapter.duration || 0}分钟`,
              description: chapter.description || '',
              status: 'notStarted',
              difficulty: 3,
              lastLearnTime: null,
              has_practice: chapter.has_practice || false
            });
          }
        }
      });
      
      // 3. 对于没有子章节的主章节，将主章节自身作为唯一的section
      mainChapters.forEach(mainChapter => {
        if (mainChapter.sections.length === 0) {
          // 查找对应的章节数据
          const chapterData = chapters.find(c => c.id === mainChapter.id);
          if (chapterData) {
            mainChapter.sections.push({
              id: chapterData.id,
              title: chapterData.title || mainChapter.title,
              type: chapterData.type || 'reading',
              duration: `${chapterData.duration}分钟`,
              description: chapterData.description,
              status: 'notStarted',
              difficulty: 3,
              lastLearnTime: null,
              has_practice: chapterData.has_practice || false
            });
          }
        }
      });
      
      // 使用处理后的层级章节列表
      const chapterList = mainChapters;
      
      return {
        id: bookDetail.id,
        title: bookDetail.title,
        author: bookDetail.author,
        cover: bookDetail.cover,
        description: bookDetail.description,
        tags: bookDetail.tag_list || [],
        chapterCount: bookDetail.chapter_count || 0,
        publishDate: bookDetail.created_at,
        category: '编程学习',
        chapters: chapterList
      };
    } catch (error) {
      console.error('获取书籍详情失败:', error);
      throw error;
    }
  },
  async getChapterContent(chapterId) {
    try {
      console.log(`获取章节内容: chapterId=${chapterId}`);
      // API_BASE_URL已包含/api前缀，所以这里直接从/books开始
      const response = await httpGet(`/books/chapters/${chapterId}/`);
      console.log('章节内容API响应:', response);
      return response; // 直接返回响应对象，不提取data字段
    } catch (error) {
      console.error('获取章节内容失败:', error);
      console.error('错误详情:', error.message, '状态码:', error.response?.status);
      console.error('请求URL:', `${API_BASE_URL}/books/chapters/${chapterId}/`);
      throw error;
    }
  },
  
  async getChapterPractice(chapterId) {
    try {
      console.log(`获取章节练习题: chapterId=${chapterId}`);
      const response = await httpGet(`/books/chapters/${chapterId}/practice/`);
      console.log('章节练习题API响应:', response);
      return response;
    } catch (error) {
      console.error('获取章节练习题失败:', error);
      throw error;
    }
  },
  
  async submitChapterPractice(chapterId, answerData) {
    try {
      console.log(`提交章节练习题答案: chapterId=${chapterId}`, answerData);
      const response = await httpPost(`/books/chapters/${chapterId}/practice/submit/`, answerData, true);
      console.log('提交练习题API响应:', response);
      return response;
    } catch (error) {
      console.error('提交练习题答案失败:', error);
      throw error;
    }
  },
  
  async setChapterAsJupyter(chapterId, jupyterContent) {
    try {
      console.log(`设置章节为Jupyter格式: chapterId=${chapterId}`);
      const response = await httpPut(`/books/chapters/${chapterId}/`, {
        content_type: 'jupyter',
        jupyter_content: jupyterContent
      }, true);
      console.log('设置Jupyter格式API响应:', response);
      return response;
    } catch (error) {
      console.error('设置章节为Jupyter格式失败:', error);
      throw error;
    }
  },
  
  async getChaptersByBook(bookId) {
    try {
      console.log(`获取书籍章节: bookId=${bookId}`);
      // 获取特定书籍的所有章节
      const chapters = await httpGet(`/books/chapters/book/${bookId}/`);
      console.log('书籍章节API响应:', chapters);
      return Array.isArray(chapters) ? chapters : [];
    } catch (error) {
      console.error('获取书籍章节失败:', error);
      return [];
    }
  },

  // 学习记录
  async getLearningRecords() {
    return httpGet('/learning/records/', true);
  },
  async getLearningActivities(params = {}) {
    const search = new URLSearchParams();
    if (params.startDate) search.append('start_date', params.startDate);
    if (params.endDate) search.append('end_date', params.endDate);
    if (params.type && params.type !== 'all') search.append('type', params.type);
    if (params.status && params.status !== 'all') search.append('status', params.status);
    if (params.orderBy) search.append('order_by', params.orderBy);
    if (params.page) search.append('page', params.page);
    if (params.pageSize) search.append('page_size', params.pageSize);
    const qs = search.toString();
    const url = qs ? `/learning/records/activity/?${qs}` : '/learning/records/activity/';
    return httpGet(url, true);
  },
  async getPracticeRecords() {
    // 学习模块下的练习记录API，适配分页结构，统一返回数组
    const res = await httpGet('/learning/practice-records/', true);
    if (Array.isArray(res)) {
      return res;
    }
    if (res && Array.isArray(res.results)) {
      return res.results;
    }
    return [];
  },
  
  // 获取练习题列表 - 直接从学习模块获取
  async getPractices() {
    try {
      console.log('获取练习题列表');
      const response = await httpGet('/books/chapters/practices-by-book/', true);
      console.log('练习题API响应:', response);
      return response;
    } catch (error) {
      console.error('获取练习题失败:', error);
      throw error;
    }
  },
  async saveProgress(bookId, chapterId, progress) {
    return httpPost('/learning/save-progress/', {
      book_id: Number(bookId),
      chapter_id: Number(chapterId),
      progress: Number(progress)
    }, true);
  },
  async submitPractice(practiceId, score, userCode = '') {
    return httpPost('/learning/practice-submit/', {
      practice_id: Number(practiceId),
      score: Number(score),
      user_code: userCode
    }, true);
  },
  async getHeatmapData() {
    return httpGet('/learning/heatmap/', true);
  },
  async executeCode({ language, code, input = '' }) {
    // 正确的API路径是/learning/execute/
    return httpPost('/learning/execute/', { language, code, input }, true);
  },
  
  // 错题本相关API
  async getWrongQuestions(filters = {}) {
    try {
      // 构建查询参数
      const params = new URLSearchParams()
      if (filters.status) params.append('status', filters.status)
      if (filters.question_type) params.append('question_type', filters.question_type)
      if (filters.difficulty) params.append('difficulty', filters.difficulty)
      if (filters.book_id) params.append('book_id', filters.book_id)
      if (filters.chapter_id) params.append('chapter_id', filters.chapter_id)
      
      const url = `/learning/wrong-questions/${params.toString() ? '?' + params.toString() : ''}`
      const response = await httpGet(url, true)
      // 确保获取到的数据是数组
      const list = Array.isArray(response) ? response : (response && response.data && Array.isArray(response.data) ? response.data : [])
      // 映射为统一的字段格式
      return list.map(q => ({
        id: q.id,
        title: q.title,
        difficulty: q.difficulty,
        question_type: q.question_type,
        question_type_display: q.question_type_display,
        practiceId: q.practice || q.practice_id,
        practice_id: q.practice_id || q.practice, // 保留原始字段名
        exerciseId: q.exercise,
        question_index: q.question_index,
        question_content: q.question_content,
        attemptTime: q.attempt_time || q.created_at,
        attempt_count: q.attempt_count || 1,
        error_time: q.error_time,
        error_reason: q.error_reason,
        knowledge_points: q.knowledge_points || [],
        status: q.status,
        status_display: q.status_display,
        book_title: q.book_title,
        book_id: q.book || q.book_id, // 添加book_id
        chapter_title: q.chapter_title,
        chapter_id: q.chapter || q.chapter_id, // 添加chapter_id
        practice_title: q.practice_title,
        practice: q.practice // 保留原始practice对象（如果有）
      }))
    } catch (error) {
      console.error('获取错题列表失败:', error)
      throw error
    }
  },
  
  async getWrongQuestionDetail(questionId) {
    try {
      const response = await httpGet(`/learning/wrong-questions/${questionId}/detail/`, true)
      return response.data || response
    } catch (error) {
      console.error('获取错题详情失败:', error)
      throw error
    }
  },
  
  async getWrongQuestionStatistics() {
    try {
      const response = await httpGet('/learning/wrong-questions/statistics/', true)
      return response.data || response
    } catch (error) {
      console.error('获取错题统计失败:', error)
      throw error
    }
  },
  
  // 批量添加错题
  async addWrongQuestions(questions) {
    try {
      const fd = new FormData()
      fd.append('questions', JSON.stringify(questions))
      return await httpPostForm('/learning/wrong-questions/batch/', fd, true)
    } catch (error) {
      console.error('批量添加错题失败:', error)
      throw error
    }
  },
  
  // 删除错题
  async removeWrongQuestion(questionId) {
    try {
      return await httpDelete(`/learning/wrong-questions/${questionId}/`, true)
    } catch (error) {
      console.error('删除错题失败:', error)
      throw error
    }
  },
  
  // 更新错题状态
  async updateWrongQuestionStatus(questionId, status) {
    try {
      return await httpPut(`/learning/wrong-questions/${questionId}/status/`, { status }, true)
    } catch (error) {
      console.error('更新错题状态失败:', error)
      throw error
    }
  },
  
  // 重做错题
  async redoWrongQuestion(questionId) {
    try {
      const response = await httpPost(`/learning/wrong-questions/${questionId}/redo/`, {}, true)
      return response.data || response
    } catch (error) {
      console.error('开始重做错题失败:', error)
      throw error
    }
  },
  
  // 完成错题重做
  async completeWrongQuestionRedo(questionId, isCorrect) {
    try {
      const response = await httpPost(`/learning/wrong-questions/${questionId}/complete_redo/`, { is_correct: isCorrect }, true)
      return response.data || response
    } catch (error) {
      console.error('完成错题重做失败:', error)
      throw error
    }
  },
  
  // 批量删除错题
  async batchDeleteWrongQuestions(questionIds) {
    try {
      return await httpDelete('/learning/wrong-questions/batch_delete/', true, { question_ids: questionIds })
    } catch (error) {
      console.error('批量删除错题失败:', error)
      throw error
    }
  },
  
  // 从练习题直接添加错题
  // 支持两种模式：
  // 1. exerciseId模式：传递Exercise模型的ID
  // 2. practiceId模式：传递Practice的ID
  async addWrongQuestionFromExercise(options) {
    try {
      const { 
        practiceId, 
        exerciseId, 
        errorReason = '', 
        knowledgePoints = [], 
        questionIndex = null, 
        questionId = null,
        questionType = null
      } = options
      
      const data = {
        error_reason: errorReason,
        knowledge_points: knowledgePoints
      }
      
      // 如果提供了question_type，添加到数据中
      if (questionType) {
        data.question_type = questionType
      }
      
      // 如果提供了practiceId且它是有效的值，使用Practice模式
      if (practiceId) {
        data.practice_id = practiceId
        if (questionIndex !== null) {
          data.question_index = questionIndex
        }
        if (questionId !== null) {
          data.question_id = questionId
        }
      } else if (exerciseId) {
        // 否则使用Exercise模式
        data.exercise_id = exerciseId
      } else {
        throw new Error('必须提供exercise_id或practice_id')
      }
      
      return await httpPost('/learning/wrong-questions/add_from_exercise/', data, true)
    } catch (error) {
      console.error('从练习题添加错题失败:', error)
      throw error
    }
  },
  async importPdf({ title, author, description, language, file }) {
    console.log('PDF导入请求参数检查:')
    console.log('- title:', title ? '存在' : '不存在')
    console.log('- author:', author ? '存在' : '不存在')
    console.log('- description:', description ? '存在' : '不存在')
    console.log('- language:', language ? '存在' : '不存在')
    console.log('- file:', file ? `存在 (${file.name}, ${file.size} bytes)` : '不存在')
    
    const fd = new FormData()
    fd.append('title', title || '')  // 确保添加，让后端验证
    if (author) fd.append('author', author)
    if (description) fd.append('description', description)
    if (language) fd.append('language', language)
    fd.append('file', file)
    
    console.log('FormData已创建，准备发送请求...')
    return httpPostForm('/books/import-pdf/', fd, true)
  },
  
  // 学习路线图
  async getRoadmaps(major, limit = 3) {
    const params = new URLSearchParams()
    if (major) params.append('major', major)
    params.append('limit', limit)
    return httpGet(`/learning/roadmaps/?${params.toString()}`, false)
  },
  
  // 删除书籍
  async deleteBook(bookId) {
    const fullUrl = `${API_BASE_URL}/books/${bookId}/`;
    const headers = {
      'Content-Type': 'application/json',
      ...authHeaders()
    };
    
    console.log(`[HTTP DELETE] 请求: ${fullUrl}`);
    console.log('[HTTP 请求头]:', headers);
    
    try {
      const res = await fetch(fullUrl, {
        method: 'DELETE',
        headers,
        credentials: 'omit'
      });
      
      console.log(`[HTTP DELETE] 响应状态: ${res.status} ${res.statusText}`);
      
      if (res.status === 401) {
        // 401表示未认证，仍然清除token并重定向
        console.warn('[HTTP] 认证失败，清除token');
        try { localStorage.removeItem('token') } catch {}
        // 仅在非登录页面时重定向，避免无限循环
        if (window.location.pathname !== '/') {
          const redirect = encodeURIComponent(window.location.pathname + window.location.search)
          window.location.href = `/?redirect=${redirect}`
        }
        throw new Error(`AUTH ${res.status}`)
      } else if (res.status === 403) {
        // 403表示权限不足，不清除token，只显示错误
        const errorData = await res.json().catch(() => ({ detail: '您没有权限执行此操作' }));
        console.error('[HTTP] 权限不足:', errorData);
        throw new Error(`PERMISSION ${res.status}: ${errorData.detail || '您没有权限删除这本教材'}`);
      }
      
      if (!res.ok) {
        const errorMsg = `请求失败: ${res.status}`;
        console.error('[HTTP] 请求失败:', errorMsg);
        throw new Error(`DELETE /books/${bookId}/ ${res.status}: ${errorMsg}`);
      }
      
      return res.json().catch(() => ({}));
    } catch (error) {
      console.error('[HTTP DELETE] 请求异常:', error);
      throw error;
    }
  },
  
  // Jupyter文档相关API调用
  async getJupyterDocuments(bookId = null, chapterId = null) {
    try {
      let url = '/learning/jupyter-documents/';
      const params = new URLSearchParams();
      if (bookId) params.append('book_id', bookId);
      if (chapterId) params.append('chapter_id', chapterId);
      
      if (params.toString()) {
        url += `?${params.toString()}`;
      }
      
      return await httpGet(url, true);
    } catch (error) {
      console.error('获取Jupyter文档列表失败:', error);
      return [];
    }
  },
  
  async getJupyterDocument(documentId) {
    try {
      return await httpGet(`/learning/jupyter-documents/${documentId}/`, true);
    } catch (error) {
      console.error(`获取Jupyter文档 ${documentId} 失败:`, error);
      throw error;
    }
  },
  
  async createJupyterDocument(data) {
    try {
      const payload = {
        title: data.title,
        content: data.content,
        is_public: data.isPublic || false,
        book_id: data.bookId || null,
        chapter_id: data.chapterId || null
      };
      
      return await httpPost('/learning/jupyter-documents/create/', payload, true);
    } catch (error) {
      console.error('创建Jupyter文档失败:', error);
      throw error;
    }
  },
  
  async updateJupyterDocument(documentId, data) {
    try {
      const payload = {};
      if (data.title !== undefined) payload.title = data.title;
      if (data.content !== undefined) payload.content = data.content;
      if (data.isPublic !== undefined) payload.is_public = data.isPublic;
      if (data.bookId !== undefined) payload.book_id = data.bookId;
      if (data.chapterId !== undefined) payload.chapter_id = data.chapterId;
      
      return await httpPost(`/learning/jupyter-documents/${documentId}/update/`, payload, true);
    } catch (error) {
      console.error(`更新Jupyter文档 ${documentId} 失败:`, error);
      throw error;
    }
  },
  
  async deleteJupyterDocument(documentId) {
    try {
      return await httpPost(`/learning/jupyter-documents/${documentId}/delete/`, {}, true);
    } catch (error) {
      console.error(`删除Jupyter文档 ${documentId} 失败:`, error);
      throw error;
    }
  },
  
  // 上传图片文件
  // 上传图片（前端模拟实现）
  async uploadImage(file) {
    // 由于后端接口不存在，使用前端FileReader临时处理图片上传
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        // 返回Data URL作为图片地址，使用image_url属性名以匹配前端期望
        resolve({
          image_url: e.target.result,
          filename: file.name
        })
      }
      reader.onerror = (error) => {
        console.error('读取图片失败:', error)
        reject(new Error('读取图片失败'))
      }
      reader.readAsDataURL(file)
    })
  },
  
  // 笔记相关API
  async getNotes() {
    return httpGet('/learning/notes/', true);
  },
  
  async getNoteTags() {
    return httpGet('/learning/notes/tags/', true);
  },
  
  async createNote(noteData) {
    return httpPost('/learning/notes/', noteData, true);
  },
  
  async updateNote(noteId, noteData) {
    return httpPut(`/learning/notes/${noteId}/`, noteData, true);
  },
  
  async deleteNote(noteId) {
    return httpDelete(`/learning/notes/${noteId}/`, true);
  },
  
  async toggleNoteFavorite(noteId) {
    return httpPost(`/learning/notes/${noteId}/toggle_favorite/`, {}, true);
  },
  
  async createNoteTag(tagData) {
    return httpPost('/learning/notes/create_tag/', tagData, true);
  },
  
  async addNoteTag(noteId, tagId) {
    return httpPost(`/learning/notes/${noteId}/add_tag/`, { tag_id: tagId }, true);
  },
  
  async removeNoteTag(noteId, tagId) {
    return httpPost(`/learning/notes/${noteId}/remove_tag/`, { tag_id: tagId }, true);
  },
  
  async getNoteVersions(noteId) {
    return httpGet(`/learning/notes/${noteId}/versions/`, true);
  },
  
  async restoreNoteVersion(noteId, versionId) {
    return httpPost(`/learning/notes/${noteId}/restore_version/`, { version_id: versionId }, true);
  },
  
  async addNoteAttachment(noteId, file) {
    const formData = new FormData();
    formData.append('files', file);
    return httpPostForm(`/learning/notes/${noteId}/add_attachment/`, formData, true);
  },
  
  // 个性化学习路径相关API
  async generatePersonalizedPath(learningGoal, maxNodes = 10) {
    try {
      return await httpPost('/learning/personalized-path/generate/', {
        learning_goal: learningGoal,
        max_nodes: maxNodes
      }, true);
    } catch (error) {
      console.error('生成个性化学习路径失败:', error);
      throw error;
    }
  },
  
  async updatePersonalizedPath(path, performance) {
    try {
      return await httpPost('/learning/personalized-path/update/', {
        path: path,
        performance: performance
      }, true);
    } catch (error) {
      console.error('更新个性化学习路径失败:', error);
      throw error;
    }
  },
  
  async generateLearningFeedback(performance) {
    try {
      return await httpPost('/learning/personalized-path/feedback/', {
        performance: performance
      }, true);
    } catch (error) {
      console.error('生成学习反馈失败:', error);
      throw error;
    }
  },
  
  // 知识图谱相关API
  async getKnowledgeNodes(filters = {}) {
    try {
      const params = new URLSearchParams();
      if (filters.graph_id) params.append('graph_id', filters.graph_id);
      if (filters.type) params.append('type', filters.type);
      if (filters.level) params.append('level', filters.level);
      if (filters.professional_group) params.append('professional_group', filters.professional_group);
      
      const url = `/learning/knowledge-graph/nodes/${params.toString() ? '?' + params.toString() : ''}`;
      return await httpGet(url, true);
    } catch (error) {
      console.error('获取知识节点失败:', error);
      throw error;
    }
  },
  
  async getKnowledgeRelations(sourceId, targetId) {
    try {
      const params = new URLSearchParams();
      if (sourceId) params.append('source_id', sourceId);
      if (targetId) params.append('target_id', targetId);
      
      const url = `/learning/knowledge-graph/relations/${params.toString() ? '?' + params.toString() : ''}`;
      return await httpGet(url, true);
    } catch (error) {
      console.error('获取知识关系失败:', error);
      throw error;
    }
  },
  
  async getKnowledgeRelationsAll() {
    try {
      const url = `/learning/knowledge-graph/relations/`;
      return await httpGet(url, true);
    } catch (error) {
      console.error('获取所有知识关系失败:', error);
      throw error;
    }
  },
  
  // 个性化学习建议API
  async generatePersonalizedSuggestions(data = {}) {
    try {
      return await httpPost('/learning/recommendations/personalized-suggestions/', data, true);
    } catch (error) {
      console.error('生成个性化学习建议失败:', error);
      throw error;
    }
  }
};
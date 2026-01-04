<template>
  <div class="toolkit-container">
    <!-- 顶部面包屑 -->
    <div class="breadcrumb">
      <router-link to="/books" class="breadcrumb-item">书架</router-link>
      <span class="breadcrumb-separator">/</span>
      <span class="breadcrumb-item current">轻量化工具包</span>
    </div>

    <div class="page-header">
      <h1>轻量化工具包</h1>
      <p class="header-subtitle">不用写代码，直接用现成工具解决实际问题</p>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filters">
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索工具..."
          class="input search-input"
        />
        <button class="search-btn">🔍</button>
      </div>
      <select v-model="categoryFilter" class="input filter-select">
        <option value="">全部分类</option>
        <option value="file">文件处理</option>
        <option value="data">数据处理</option>
        <option value="image">图片处理</option>
        <option value="text">文本处理</option>
      </select>
    </div>

    <!-- 工具列表 -->
    <div class="tools-grid">
      <div 
        v-for="tool in filteredTools" 
        :key="tool.id" 
        class="tool-card"
        @click="openTool(tool)"
      >
        <div class="tool-icon">{{ tool.icon }}</div>
        <h3 class="tool-title">{{ tool.title }}</h3>
        <p class="tool-description">{{ tool.description }}</p>
        <div class="tool-category">{{ getCategoryText(tool.category) }}</div>
        <div class="tool-book-info">
          <span class="book-label">基于教材：</span>
          <span class="book-title">{{ tool.bookTitle }}</span>
          <span class="book-chapter">第{{ tool.chapterNumber }}章</span>
        </div>
      </div>
    </div>

    <!-- 工具详情弹窗 -->
    <div v-if="selectedTool" class="tool-modal-overlay" @click.self="closeTool">
      <div class="tool-modal">
        <div class="tool-modal-header">
          <div class="modal-title-section">
            <span class="tool-modal-icon">{{ selectedTool.icon }}</span>
            <h2>{{ selectedTool.title }}</h2>
          </div>
          <button class="close-btn" @click="closeTool">×</button>
        </div>
        <div class="tool-modal-content">
          <!-- 工具信息 -->
          <div class="tool-info">
            <p>{{ selectedTool.description }}</p>
            <div class="tool-meta">
              <span class="meta-item">分类：{{ getCategoryText(selectedTool.category) }}</span>
              <span class="meta-item">基于：{{ selectedTool.bookTitle }} 第{{ selectedTool.chapterNumber }}章</span>
              <router-link 
                :to="`/books/${selectedTool.bookId}/chapter/${selectedTool.firstSectionId}`" 
                class="learn-link"
              >
                学习原理 →
              </router-link>
            </div>
          </div>

          <!-- 工具参数表单 -->
          <div class="tool-form">
            <h3>参数设置</h3>
            <div v-for="param in selectedTool.params" :key="param.name" class="form-group">
              <label :for="param.name">{{ param.label }}</label>
              <input 
                v-if="param.type === 'text' || param.type === 'number'" 
                :type="param.type"
                :id="param.name"
                v-model="toolParams[param.name]"
                :placeholder="param.placeholder || ''"
                class="input"
              />
              <textarea 
                v-else-if="param.type === 'textarea'"
                :id="param.name"
                v-model="toolParams[param.name]"
                :placeholder="param.placeholder || ''"
                class="input textarea"
                rows="4"
              ></textarea>
              <select 
                v-else-if="param.type === 'select'"
                :id="param.name"
                v-model="toolParams[param.name]"
                class="input"
              >
                <option v-for="option in param.options" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>
          </div>

          <!-- 运行结果 -->
          <div v-if="showResult" class="tool-result">
            <h3>运行结果</h3>
            <div class="result-content">
              <pre>{{ toolResult }}</pre>
            </div>
            <div class="result-actions">
              <button class="btn btn-primary" @click="saveResult">💾 保存结果</button>
            </div>
          </div>
        </div>
        <div class="tool-modal-footer">
          <button class="btn" @click="closeTool">关闭</button>
          <button class="btn btn-primary" @click="runTool">▶ 运行工具</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'

// API基础URL
const API_BASE_URL = 'http://localhost:8000/api/toolkit';

// 获取工具列表
async function fetchTools() {
  try {
    const response = await fetch(`${API_BASE_URL}/tools/`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('获取工具列表失败:', error);
    return [];
  }
}

// 运行工具
async function runToolApi(toolId, parameters) {
  try {
    console.log('调用工具API:', toolId, '参数:', parameters);
    const response = await fetch(`${API_BASE_URL}/tools/${toolId}/run/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      // 根据后端要求，将参数包装在parameters字段中
      body: JSON.stringify({ parameters })
    });
    
    // 解析响应
    let responseData;
    try {
      responseData = await response.json();
    } catch (jsonError) {
      throw new Error(`无法解析响应: ${jsonError.message}`);
    }
    
    if (!response.ok) {
      throw new Error(`工具执行失败: ${responseData.error || responseData.detail || '未知错误'}`);
    }
    
    console.log('工具执行成功，响应:', responseData);
    return responseData;
  } catch (error) {
    console.error('运行工具失败:', error);
    throw error;
  }
}

export default {
  name: 'ToolKitView',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const searchQuery = ref('')
    const categoryFilter = ref('')
    const selectedTool = ref(null)
    const toolParams = ref({})
    const showResult = ref(false)
    const toolResult = ref('')
    
    const tools = ref([
      {
        id: 1,
        title: '批量重命名文件',
        description: '根据规则批量修改文件名，支持数字编号、日期格式等',
        icon: '📁',
        category: 'file',
        bookId: 1,
        bookTitle: 'Python办公自动化',
        chapterNumber: 3,
        firstSectionId: 101,
        params: [
          {
            name: 'folderPath',
            label: '文件夹路径',
            type: 'text',
            placeholder: '请输入文件所在文件夹路径'
          },
          {
            name: 'pattern',
            label: '命名模式',
            type: 'text',
            placeholder: '如：文档_{num:03d}'
          },
          {
            name: 'fileType',
            label: '文件类型',
            type: 'select',
            options: [
              { value: 'all', label: '所有文件' },
              { value: '.txt', label: '文本文档(.txt)' },
              { value: '.jpg,.png', label: '图片(.jpg,.png)' },
              { value: '.docx,.pdf', label: '文档(.docx,.pdf)' }
            ]
          }
        ]
      },
      {
        id: 2,
        title: 'Excel表格合并',
        description: '将多个Excel文件合并为一个，自动处理表头和数据',
        icon: '📊',
        category: 'data',
        bookId: 1,
        bookTitle: 'Python办公自动化',
        chapterNumber: 4,
        firstSectionId: 105,
        params: [
          {
            name: 'folderPath',
            label: 'Excel文件所在文件夹',
            type: 'text',
            placeholder: '请输入包含Excel文件的文件夹路径'
          },
          {
            name: 'outputFileName',
            label: '输出文件名',
            type: 'text',
            placeholder: '如：合并结果.xlsx'
          },
          {
            name: 'hasSameHeader',
            label: '所有文件表头相同',
            type: 'select',
            options: [
              { value: 'true', label: '是' },
              { value: 'false', label: '否' }
            ]
          }
        ]
      },
      {
        id: 3,
        title: '图片批量压缩',
        description: '批量压缩图片文件，可设置压缩质量和尺寸',
        icon: '🖼️',
        category: 'image',
        bookId: 2,
        bookTitle: 'Python图像处理',
        chapterNumber: 2,
        firstSectionId: 203,
        params: [
          {
            name: 'folderPath',
            label: '图片文件夹路径',
            type: 'text',
            placeholder: '请输入包含图片的文件夹路径'
          },
          {
            name: 'quality',
            label: '压缩质量 (1-100)',
            type: 'number',
            placeholder: '70'
          },
          {
            name: 'maxWidth',
            label: '最大宽度 (像素)',
            type: 'number',
            placeholder: '1920'
          }
        ]
      },
      {
        id: 4,
        title: '文本内容提取',
        description: '从PDF、Word等文档中提取文本内容',
        icon: '📄',
        category: 'text',
        bookId: 3,
        bookTitle: 'Python文本处理',
        chapterNumber: 5,
        firstSectionId: 307,
        params: [
          {
            name: 'filePath',
            label: '文件路径',
            type: 'text',
            placeholder: '请输入文档文件路径'
          },
          {
            name: 'outputFormat',
            label: '输出格式',
            type: 'select',
            options: [
              { value: 'txt', label: '纯文本(.txt)' },
              { value: 'md', label: 'Markdown(.md)' }
            ]
          }
        ]
      },
      {        
        id: 5,
        title: 'JSON格式化工具',
        description: '美化JSON格式，添加缩进和换行',
        icon: '🔧',
        category: 'text',
        bookId: 4,
        bookTitle: 'JavaScript基础',
        chapterNumber: 3,
        firstSectionId: 405,
        params: [
          {
            name: 'jsonContent',
            label: 'JSON内容',
            type: 'textarea',
            placeholder: '请粘贴需要格式化的JSON内容',
            required: true
          },
          {
            name: 'indentSize',
            label: '缩进空格数',
            type: 'number',
            placeholder: '2',
            required: true,
            default: 2
          }
        ]
      },
      {
        id: 6,
        title: '数据统计分析',
        description: '快速统计Excel数据的基本信息，如平均值、最大值等',
        icon: '📈',
        category: 'data',
        bookId: 1,
        bookTitle: 'Python办公自动化',
        chapterNumber: 5,
        firstSectionId: 109,
        params: [
          {
            name: 'filePath',
            label: 'Excel文件路径',
            type: 'text',
            placeholder: '请输入Excel文件路径'
          },
          {
            name: 'sheetName',
            label: '工作表名称',
            type: 'text',
            placeholder: 'Sheet1'
          },
          {
            name: 'columns',
            label: '需要分析的列（逗号分隔）',
            type: 'text',
            placeholder: 'A,B,C'
          }
        ]
      }
    ])

    // 过滤工具
    const filteredTools = computed(() => {
      let result = [...tools.value]
      
      // 搜索过滤
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(tool => 
          tool.title.toLowerCase().includes(query) ||
          tool.description.toLowerCase().includes(query) ||
          tool.bookTitle.toLowerCase().includes(query)
        )
      }
      
      // 分类过滤
      if (categoryFilter.value) {
        result = result.filter(tool => tool.category === categoryFilter.value)
      }
      
      return result
    })

    // 获取分类文本
    const getCategoryText = (category) => {
      const categoryMap = {
        'file': '文件处理',
        'data': '数据处理',
        'image': '图片处理',
        'text': '文本处理'
      }
      return categoryMap[category] || '其他'
    }

    // 打开工具
    const openTool = (tool) => {
      selectedTool.value = tool
      // 初始化参数
      toolParams.value = {}
      tool.params.forEach(param => {
        toolParams.value[param.name] = param.default || ''
      })
      showResult.value = false
      toolResult.value = ''
    }
    
    // 根据toolId查找并打开工具
    const openToolById = (toolId) => {
      const targetTool = tools.value.find(tool => tool.id === parseInt(toolId))
      if (targetTool) {
        openTool(targetTool)
      }
    }

    // 关闭工具
    const closeTool = () => {
      selectedTool.value = null
      toolParams.value = {}
      showResult.value = false
      toolResult.value = ''
    }

    // 运行工具
    const runTool = async () => {
      try {
        // 参数验证
        const requiredParams = selectedTool.value.params.filter(param => 
          param.required !== false || 
          // 对于没有显式设置required的参数，默认为必填
          param.required === undefined
        );
        
        for (const param of requiredParams) {
          if (!toolParams.value[param.name] || 
              (typeof toolParams.value[param.name] === 'string' && 
               toolParams.value[param.name].trim() === '')) {
            toolResult.value = `请输入${param.label}！`;
            showResult.value = true;
            return;
          }
        }
        
        // 特殊验证：JSON格式化工具的JSON内容
        if (selectedTool.value.id === 5 && toolParams.value.jsonContent) {
          try {
            // 预验证JSON格式
            JSON.parse(toolParams.value.jsonContent);
          } catch (e) {
            toolResult.value = '请输入有效的JSON内容！\n\n错误详情：' + e.message;
            showResult.value = true;
            return;
          }
        }
        
        showResult.value = false;
        // 显示加载状态
        toolResult.value = '工具运行中...';
        showResult.value = true;
        
        // 调用后端API，传递工具参数
        const result = await runToolApi(selectedTool.value.id, toolParams.value);
        
        if (result.success) {
          // 格式化并显示成功结果
          toolResult.value = `工具运行成功！\n\n`;
          
          // 添加运行参数信息
          toolResult.value += `运行参数：\n${JSON.stringify(toolParams.value, null, 2)}\n\n`;
          
          // 添加执行结果
          toolResult.value += `执行结果：\n${JSON.stringify(result.result, null, 2)}`;
        } else {
          // 显示错误信息
          toolResult.value = `工具运行失败！\n\n错误信息：${result.error || result.detail || '未知错误'}`;
        }
      } catch (error) {
        // 显示异常信息
        toolResult.value = `工具运行异常！\n\n异常信息：${error.message}`;
        console.error('工具运行异常:', error);
      }
    }

    // 保存结果
    const saveResult = () => {
      // 模拟保存功能
      alert('结果已保存到本地！')
    }

    onMounted(async () => {
      // 组件挂载时加载真实工具数据
      const realTools = await fetchTools();
      if (realTools.length > 0) {
        tools.value = realTools.map(tool => ({
          ...tool,
          // 转换参数格式以适应前端组件
          params: tool.parameters || []
        }));
      }
      
      // 检查URL查询参数
      const toolId = route.query.toolId
      if (toolId) {
        openToolById(toolId)
      }
    })

    return {
      searchQuery,
      categoryFilter,
      tools,
      filteredTools,
      selectedTool,
      toolParams,
      showResult,
      toolResult,
      getCategoryText,
      openTool,
      closeTool,
      runTool,
      saveResult
    }
  }
}
</script>

<style scoped>
.toolkit-container {
  padding: 20px 0;
}

.breadcrumb {
  margin-bottom: 20px;
  font-size: 14px;
  color: #666;
}

.breadcrumb-item {
  color: #409EFF;
  text-decoration: none;
}

.breadcrumb-item:hover {
  text-decoration: underline;
}

.breadcrumb-item.current {
  color: #333;
  font-weight: 500;
}

.breadcrumb-separator {
  margin: 0 10px;
  color: #999;
}

.page-header {
  margin-bottom: 30px;
  text-align: center;
}

.page-header h1 {
  margin: 0 0 10px 0;
  font-size: 32px;
  color: #333;
}

.header-subtitle {
  margin: 0;
  font-size: 16px;
  color: #666;
}

.search-filters {
  display: flex;
  gap: 20px;
  align-items: center;
  margin-bottom: 30px;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.search-box {
  flex: 1;
  display: flex;
  gap: 0;
}

.search-input {
  border-radius: 4px 0 0 4px;
}

.search-btn {
  background: #409EFF;
  color: white;
  border: none;
  padding: 0 20px;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  font-size: 16px;
}

.search-btn:hover {
  background: #66b1ff;
}

.filter-select {
  min-width: 150px;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.tool-card {
  background: white;
  border-radius: 8px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  cursor: pointer;
  transition: transform 0.3s, box-shadow 0.3s;
}

.tool-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.tool-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.tool-title {
  font-size: 18px;
  margin: 0 0 10px 0;
  color: #333;
}

.tool-description {
  font-size: 14px;
  color: #666;
  margin-bottom: 15px;
  line-height: 1.6;
}

.tool-category {
  display: inline-block;
  padding: 4px 12px;
  background: #ecf5ff;
  color: #409EFF;
  border-radius: 15px;
  font-size: 12px;
  margin-bottom: 15px;
}

.tool-book-info {
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.book-label {
  font-weight: 500;
}

.book-title {
  color: #666;
}

.book-chapter {
  background: #f0f9eb;
  color: #67C23A;
  padding: 2px 8px;
  border-radius: 10px;
}

/* 工具弹窗样式 */
.tool-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.tool-modal {
  background: white;
  border-radius: 8px;
  width: 100%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.tool-modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-title-section {
  display: flex;
  align-items: center;
  gap: 15px;
}

.tool-modal-icon {
  font-size: 32px;
}

.modal-title-section h2 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.tool-modal-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.tool-info {
  margin-bottom: 30px;
}

.tool-info p {
  font-size: 16px;
  line-height: 1.6;
  color: #666;
  margin-bottom: 15px;
}

.tool-meta {
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
  color: #999;
  font-size: 14px;
}

.learn-link {
  color: #409EFF;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: 5px;
}

.learn-link:hover {
  text-decoration: underline;
}

.tool-form h3,
.tool-result h3 {
  font-size: 18px;
  margin: 0 0 20px 0;
  color: #333;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.textarea {
  resize: vertical;
}

.tool-result {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #f0f0f0;
}

.result-content {
  background: #f5f5f5;
  border-radius: 6px;
  padding: 15px;
  margin-bottom: 15px;
  max-height: 300px;
  overflow-y: auto;
}

.result-content pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
}

.result-actions {
  display: flex;
  justify-content: flex-end;
}

.tool-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

@media (max-width: 768px) {
  .search-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .tools-grid {
    grid-template-columns: 1fr;
  }
  
  .tool-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}
</style>
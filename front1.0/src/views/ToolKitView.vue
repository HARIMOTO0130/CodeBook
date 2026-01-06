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

    <!-- 消息提示 -->
    <div v-if="errorMessage" class="message message-error" @click="clearMessages">
      <span class="message-icon">⚠️</span>
      <span class="message-text">{{ errorMessage }}</span>
      <button class="message-close">×</button>
    </div>
    <div v-if="successMessage" class="message message-success" @click="clearMessages">
      <span class="message-icon">✅</span>
      <span class="message-text">{{ successMessage }}</span>
      <button class="message-close">×</button>
    </div>

    <!-- 搜索和筛选 -->
    <div class="search-filters">
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索工具..."
          class="input search-input"
          @input="clearMessages"
        />
        <button class="search-btn" @click="clearMessages">🔍</button>
      </div>
      <select 
        v-model="categoryFilter" 
        class="input filter-select"
        @change="clearMessages"
      >
        <option value="">全部分类</option>
        <option value="file">文件处理</option>
        <option value="data">数据处理</option>
        <option value="image">图片处理</option>
        <option value="text">文本处理</option>
      </select>
      <div v-if="loading" class="loading-indicator">加载中...</div>
    </div>

    <!-- 工具列表 -->
    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>正在加载工具...</p>
    </div>
    <div v-else-if="filteredTools.length === 0" class="empty-state">
      <p>暂无可用工具</p>
    </div>
    <div v-else class="tools-grid">
      <div 
        v-for="tool in filteredTools" 
        :key="tool.id" 
        class="tool-card"
        :class="{ 'tool-card-featured': tool.id === 6 }"
        @click="openTool(tool)"
      >
        <div class="tool-icon">{{ tool.icon }}</div>
        <h3 class="tool-title">{{ tool.title }}</h3>
        <p class="tool-description">{{ tool.description }}</p>
        <div class="tool-category">{{ getCategoryText(tool.category) }}</div>
        <div class="tool-book-info">
          <span class="book-label">基于教材：</span>
          <span class="book-title">{{ tool.bookTitle }}</span>
          <span v-if="tool.chapterNumber" class="book-chapter">第{{ tool.chapterNumber }}章</span>
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
              <label :for="param.name">
                {{ param.label }}
                <span v-if="param.required" class="required-mark">*</span>
              </label>
              <input 
                v-if="param.type === 'text' || param.type === 'number'" 
                :type="param.type"
                :id="param.name"
                v-model="toolParams[param.name]"
                :placeholder="param.placeholder || ''"
                class="input"
                :class="{ 'input-error': errorMessage && !toolParams[param.name] && param.required }"
              />
              <textarea 
                v-else-if="param.type === 'textarea'"
                :id="param.name"
                v-model="toolParams[param.name]"
                :placeholder="param.placeholder || ''"
                class="input textarea"
                :class="{ 'input-error': errorMessage && !toolParams[param.name] && param.required }"
                :rows="selectedTool && selectedTool.id === 6 ? 8 : 4"
              ></textarea>
              <select 
                v-else-if="param.type === 'select'"
                :id="param.name"
                v-model="toolParams[param.name]"
                class="input"
                :class="{ 'input-error': errorMessage && !toolParams[param.name] && param.required }"
              >
                <option value="">{{ param.placeholder || '请选择' }}</option>
                <option v-for="option in param.options" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
              <div v-if="param.type === 'number' && param.name === 'indentSize'" class="input-hint">
                建议值：2-4（默认：2）
              </div>
            </div>
          </div>

          <!-- 运行结果 -->
          <div v-if="showResult" class="tool-result">
            <h3>运行结果</h3>
            <div class="result-content" :class="{ 
              'json-result': selectedTool && selectedTool.id === 6 && toolResult.includes('✅'),
              'result-error': toolResult.includes('❌')
            }">
              <pre v-if="selectedTool && selectedTool.id === 6 && toolResult.includes('格式化后的JSON')" class="json-formatted">{{ getFormattedJson() }}</pre>
              <pre v-else>{{ toolResult }}</pre>
            </div>
            <div class="result-actions">
              <button 
                v-if="selectedTool && selectedTool.id === 6 && toolResult.includes('格式化后的JSON') && !toolResult.includes('❌')" 
                class="btn btn-secondary" 
                @click="copyJson"
              >
                📋 复制JSON
              </button>
              <button 
                v-if="!toolResult.includes('❌')"
                class="btn btn-primary" 
                @click="saveResult"
              >
                💾 保存结果
              </button>
              <button 
                v-if="toolResult.includes('❌')"
                class="btn btn-secondary" 
                @click="runTool"
                :disabled="running"
              >
                🔄 重试
              </button>
            </div>
          </div>
        </div>
        <div class="tool-modal-footer">
          <button class="btn" @click="closeTool">关闭</button>
          <button 
            class="btn btn-primary" 
            @click="runTool"
            :disabled="running"
          >
            <span v-if="running" class="btn-loading">⏳</span>
            <span v-else>▶</span>
            {{ running ? '运行中...' : '运行工具' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '../api/api.js'

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
    const loading = ref(false)
    const running = ref(false)
    const errorMessage = ref('')
    const successMessage = ref('')
    const debounceTimer = ref(null)
    
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
        id: 6,
        title: 'JSON格式化',
        description: '格式化和美化JSON字符串，添加缩进和换行，使JSON更易读',
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
            placeholder: '请粘贴需要格式化的JSON内容，例如：{"name":"张三","value":123}',
            required: true
          },
          {
            name: 'indentSize',
            label: '缩进空格数',
            type: 'number',
            placeholder: '2',
            required: false,
            default: 2
          }
        ]
      }
    ])

    // 过滤工具（带防抖）
    const filteredTools = computed(() => {
      let result = [...tools.value]
      
      // 搜索过滤
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase().trim()
        result = result.filter(tool => 
          tool.title.toLowerCase().includes(query) ||
          tool.description.toLowerCase().includes(query) ||
          tool.bookTitle.toLowerCase().includes(query) ||
          (tool.params && tool.params.some(p => p.label.toLowerCase().includes(query)))
        )
      }
      
      // 分类过滤
      if (categoryFilter.value) {
        result = result.filter(tool => tool.category === categoryFilter.value)
      }
      
      return result
    })
    
    // 清除消息
    const clearMessages = () => {
      errorMessage.value = ''
      successMessage.value = ''
    }
    
    // 显示成功消息
    const showSuccess = (message) => {
      successMessage.value = message
      setTimeout(() => {
        successMessage.value = ''
      }, 3000)
    }
    
    // 显示错误消息
    const showError = (message) => {
      errorMessage.value = message
      setTimeout(() => {
        errorMessage.value = ''
      }, 5000)
    }

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
        const defaultValue = param.default !== undefined 
          ? param.default 
          : (param.type === 'number' ? (param.name === 'indentSize' ? 2 : 0) : '')
        toolParams.value[param.name] = defaultValue
      })
      showResult.value = false
      toolResult.value = ''
      clearMessages()
      
      // 更新URL但不刷新页面
      router.replace({
        query: { ...route.query, toolId: tool.id }
      })
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
      clearMessages()
      
      // 清除URL参数
      router.replace({
        query: { ...route.query, toolId: undefined }
      })
    }

    // 运行工具
    const runTool = async () => {
      if (running.value) return // 防止重复提交
      
      try {
        clearMessages()
        
        // 参数验证
        const requiredParams = selectedTool.value.params.filter(param => 
          param.required !== false && param.required !== undefined
        );
        
        const validationErrors = []
        for (const param of requiredParams) {
          const value = toolParams.value[param.name]
          if (!value || 
              (typeof value === 'string' && value.trim() === '') ||
              (param.type === 'number' && (value === '' || value === null || value === undefined))) {
            validationErrors.push(`${param.label}是必填项`)
          }
        }
        
        // 特殊验证：JSON格式化工具的JSON内容（toolId=6）
        if (selectedTool.value.id === 6 && toolParams.value.jsonContent) {
          try {
            const trimmedJson = toolParams.value.jsonContent.trim()
            if (!trimmedJson) {
              validationErrors.push('请输入JSON内容')
            } else {
              // 预验证JSON格式
              JSON.parse(trimmedJson)
            }
          } catch (e) {
            validationErrors.push(`JSON格式错误：${e.message}`)
          }
        }
        
        if (validationErrors.length > 0) {
          showError(validationErrors.join('；'))
          return
        }
        
        // 设置默认值
        if (selectedTool.value.id === 6 && (!toolParams.value.indentSize || toolParams.value.indentSize === '')) {
          toolParams.value.indentSize = 2
        }
        
        // 转换参数类型
        const processedParams = { ...toolParams.value }
        selectedTool.value.params.forEach(param => {
          if (param.type === 'number' && processedParams[param.name] !== undefined) {
            processedParams[param.name] = Number(processedParams[param.name])
          }
        })
        
        running.value = true
        showResult.value = false
        toolResult.value = ''
        
        // 调用后端API，传递工具参数
        let result
        try {
          result = await api.runTool(selectedTool.value.id, processedParams)
        } catch (apiError) {
          // 处理API调用异常
          running.value = false
          const errorMsg = apiError.error || apiError.message || '网络错误，请检查连接后重试'
          showError(errorMsg)
          toolResult.value = `❌ 工具运行异常！\n\n异常信息：${errorMsg}`
          showResult.value = true
          return
        }
        
        running.value = false
        
        if (result && result.success) {
          showSuccess('工具执行成功！')
          
          // JSON格式化工具特殊处理
          if (selectedTool.value.id === 6 && result.result) {
            const formattedResult = result.result
            toolResult.value = `✅ JSON格式化成功！\n\n`
            
            // 显示格式化后的JSON
            if (formattedResult.formatted_json) {
              toolResult.value += `📄 格式化后的JSON：\n${formattedResult.formatted_json}\n\n`
            }
            
            // 显示统计信息
            if (formattedResult.statistics) {
              const stats = formattedResult.statistics
              toolResult.value += `📊 统计信息：\n`
              toolResult.value += `  • 原始大小：${stats.original_size} 字符\n`
              toolResult.value += `  • 格式化后大小：${stats.formatted_size} 字符\n`
              toolResult.value += `  • 大小差异：${stats.size_difference > 0 ? '+' : ''}${stats.size_difference} 字符\n`
              toolResult.value += `  • 缩进空格数：${stats.indent_size}\n`
            }
          } else {
            // 其他工具的通用处理
            toolResult.value = `✅ 工具运行成功！\n\n`
            toolResult.value += `📋 执行结果：\n${JSON.stringify(result.result, null, 2)}`
          }
          
          showResult.value = true
        } else {
          const errorMsg = result.error || result.detail || result.message || '未知错误'
          showError(`工具执行失败：${errorMsg}`)
          toolResult.value = `❌ 工具运行失败！\n\n错误信息：${errorMsg}`
          showResult.value = true
        }
      } catch (error) {
        running.value = false
        const errorMsg = error.message || '网络错误，请检查连接后重试'
        showError(errorMsg)
        toolResult.value = `❌ 工具运行异常！\n\n异常信息：${errorMsg}`
        showResult.value = true
        console.error('工具运行异常:', error)
      }
    }

    // 获取格式化后的JSON（用于toolId=6）
    const getFormattedJson = () => {
      if (!selectedTool.value || selectedTool.value.id !== 6) return toolResult.value;
      
      try {
        // 从结果中提取JSON
        const jsonMatch = toolResult.value.match(/格式化后的JSON：\n([\s\S]+?)\n\n/);
        if (jsonMatch && jsonMatch[1]) {
          return jsonMatch[1].trim();
        }
      } catch (e) {
        console.error('提取JSON失败:', e);
      }
      return toolResult.value;
    }
    
    // 复制JSON到剪贴板
    const copyJson = async () => {
      try {
        const jsonText = getFormattedJson()
        if (!jsonText || jsonText.trim() === '') {
          showError('没有可复制的内容')
          return
        }
        
        await navigator.clipboard.writeText(jsonText)
        showSuccess('JSON已复制到剪贴板！')
      } catch (error) {
        console.error('复制失败:', error)
        // 降级方案：使用传统方法
        try {
          const textArea = document.createElement('textarea')
          textArea.value = getFormattedJson()
          textArea.style.position = 'fixed'
          textArea.style.opacity = '0'
          document.body.appendChild(textArea)
          textArea.select()
          const success = document.execCommand('copy')
          document.body.removeChild(textArea)
          
          if (success) {
            showSuccess('JSON已复制到剪贴板！')
          } else {
            showError('复制失败，请手动复制')
          }
        } catch (e) {
          showError('复制失败，请手动复制')
        }
      }
    }
    
    // 保存结果
    const saveResult = () => {
      try {
        const resultText = selectedTool.value && selectedTool.value.id === 6 
          ? getFormattedJson() 
          : toolResult.value
        
        if (!resultText || resultText.trim() === '') {
          showError('没有可保存的内容')
          return
        }
        
        // 创建下载链接
        const blob = new Blob([resultText], { type: 'text/plain;charset=utf-8' })
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        const toolName = selectedTool.value?.title?.replace(/\s+/g, '_') || 'tool'
        link.download = `${toolName}_${Date.now()}.${selectedTool.value?.id === 6 ? 'json' : 'txt'}`
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        URL.revokeObjectURL(url)
        
        showSuccess('结果已保存！')
      } catch (error) {
        console.error('保存失败:', error)
        showError('保存失败，请手动复制结果')
      }
    }

    onMounted(async () => {
      loading.value = true
      clearMessages()
      
      try {
        // 组件挂载时加载真实工具数据
        const realTools = await api.getTools()
        if (realTools && realTools.length > 0) {
          // 转换后端数据格式为前端需要的格式
          tools.value = realTools.map(tool => ({
            id: tool.id,
            title: tool.title,
            description: tool.description,
            icon: tool.icon || '🔧',
            category: tool.category_name?.toLowerCase() || tool.category?.slug || 'other',
            bookId: tool.book_id,
            bookTitle: tool.book_title || '未指定教材',
            chapterNumber: tool.chapter_number || 0,
            firstSectionId: tool.first_section_id,
            params: (tool.params || []).map(param => ({
              name: param.name,
              label: param.label,
              type: param.type,
              placeholder: param.placeholder || '',
              required: param.is_required !== false,
              default: param.default_value || (param.type === 'number' ? (param.name === 'indentSize' ? 2 : 0) : ''),
              options: param.options || []
            }))
          }))
        } else {
          showError('未找到可用工具，请稍后重试')
        }
      } catch (error) {
        console.error('加载工具列表失败:', error)
        showError('加载工具列表失败，请刷新页面重试')
        // 如果加载失败，使用默认数据
      } finally {
        loading.value = false
      }
      
      // 检查URL查询参数
      const toolId = route.query.toolId
      if (toolId) {
        // 等待工具列表加载完成后再打开
        setTimeout(() => {
          const tool = tools.value.find(t => t.id === parseInt(toolId))
          if (tool) {
            openTool(tool)
          } else {
            showError(`未找到ID为${toolId}的工具`)
          }
        }, 300)
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
      loading,
      running,
      errorMessage,
      successMessage,
      getCategoryText,
      openTool,
      closeTool,
      runTool,
      saveResult,
      getFormattedJson,
      copyJson,
      clearMessages
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

.loading-indicator {
  padding: 8px 16px;
  background: #f0f9ff;
  color: #409EFF;
  border-radius: 4px;
  font-size: 14px;
  white-space: nowrap;
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

.tool-card-featured {
  border: 2px solid #409EFF;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409EFF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #999;
  font-size: 16px;
}

/* 消息提示样式 */
.message {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  animation: slideIn 0.3s ease-out;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-error {
  background: #fef0f0;
  border-left: 4px solid #f56c6c;
  color: #f56c6c;
}

.message-success {
  background: #f0f9eb;
  border-left: 4px solid #67c23a;
  color: #67c23a;
}

.message-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.message-text {
  flex: 1;
  font-size: 14px;
  line-height: 1.5;
}

.message-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: inherit;
  opacity: 0.7;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.message-close:hover {
  opacity: 1;
}

.btn-loading {
  display: inline-block;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.result-content.json-result {
  background: #1e1e1e;
  color: #d4d4d4;
}

.result-content.json-result pre.json-formatted {
  color: #d4d4d4;
  font-size: 13px;
  line-height: 1.6;
}

.result-content.json-result pre:not(.json-formatted) {
  color: #d4d4d4;
}

.result-content.result-error {
  background: #fef0f0;
  border-left: 4px solid #f56c6c;
}

.result-content.result-error pre {
  color: #f56c6c;
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

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  font-weight: 500;
}

.btn-primary {
  background: #409EFF;
  color: white;
}

.btn-primary:hover {
  background: #66b1ff;
}

.btn-primary:active {
  background: #3a8ee6;
}

.btn-secondary {
  background: #f0f0f0;
  color: #666;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input {
  width: 100%;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.input:focus {
  outline: none;
  border-color: #409EFF;
}

.input.textarea {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  resize: vertical;
}

.input-error {
  border-color: #f56c6c !important;
  background-color: #fef0f0;
}

.input-error:focus {
  border-color: #f56c6c !important;
  box-shadow: 0 0 0 2px rgba(245, 108, 108, 0.2);
}

.required-mark {
  color: #f56c6c;
  margin-left: 4px;
}

.input-hint {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  margin-left: 2px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .toolkit-container {
    padding: 15px;
  }
  
  .page-header h1 {
    font-size: 24px;
  }
  
  .header-subtitle {
    font-size: 14px;
  }
  
  .search-filters {
    flex-direction: column;
    align-items: stretch;
    padding: 15px;
  }
  
  .search-box {
    width: 100%;
  }
  
  .filter-select {
    width: 100%;
    min-width: auto;
  }
  
  .tools-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .tool-card {
    padding: 20px;
  }
  
  .tool-icon {
    font-size: 40px;
  }
  
  .tool-title {
    font-size: 16px;
  }
  
  .tool-description {
    font-size: 13px;
  }
  
  .tool-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
  
  .tool-modal-overlay {
    padding: 10px;
  }
  
  .tool-modal {
    max-width: 100%;
    max-height: 95vh;
  }
  
  .tool-modal-header {
    padding: 15px;
  }
  
  .modal-title-section h2 {
    font-size: 20px;
  }
  
  .tool-modal-content {
    padding: 15px;
  }
  
  .tool-form h3,
  .tool-result h3 {
    font-size: 16px;
  }
  
  .form-group {
    margin-bottom: 15px;
  }
  
  .result-content {
    max-height: 200px;
    font-size: 12px;
  }
  
  .tool-modal-footer {
    padding: 15px;
    flex-direction: column;
    gap: 10px;
  }
  
  .tool-modal-footer .btn {
    width: 100%;
  }
  
  .result-actions {
    flex-direction: column;
    gap: 10px;
  }
  
  .result-actions .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .toolkit-container {
    padding: 10px;
  }
  
  .page-header h1 {
    font-size: 20px;
  }
  
  .header-subtitle {
    font-size: 13px;
  }
  
  .tools-grid {
    gap: 10px;
  }
  
  .tool-card {
    padding: 15px;
  }
  
  .tool-icon {
    font-size: 36px;
  }
  
  .result-content {
    padding: 10px;
    font-size: 11px;
  }
  
  .message {
    padding: 10px 15px;
    font-size: 13px;
  }
  
  .message-icon {
    font-size: 16px;
  }
  
  .message-close {
    width: 20px;
    height: 20px;
    font-size: 18px;
  }
}
</style>
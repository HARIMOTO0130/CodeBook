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
        <div 
          class="tool-category"
          :style="{ backgroundColor: `${getCategoryInfo(tool.category).color}22`, color: getCategoryInfo(tool.category).color }"
        >
          <span class="category-icon">{{ getCategoryInfo(tool.category).icon }}</span>
          <span class="category-text">{{ getCategoryInfo(tool.category).text }}</span>
        </div>
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
            <span class="meta-item" :style="{ color: getCategoryInfo(selectedTool.category).color }">
              <span class="category-icon">{{ getCategoryInfo(selectedTool.category).icon }}</span>
              分类：{{ getCategoryInfo(selectedTool.category).text }}
            </span>
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
              
              <!-- 文件上传类型：支持选择文件或文件夹 -->
              <div v-if="param.type === 'file' || param.name.toLowerCase().includes('path') || param.name.toLowerCase().includes('folder')" class="file-upload-container">
                <div class="file-input-wrapper">
                  <input 
                    type="text" 
                    :id="param.name"
                    v-model="toolParams[param.name]"
                    :placeholder="param.placeholder || '请选择文件或文件夹'"
                    class="input file-input-text"
                    :class="{ 'input-error': errorMessage && !toolParams[param.name] && param.required }"
                    readonly
                  />
                  <label class="file-upload-btn" :for="`file-${param.name}`">
                    📁 选择文件
                  </label>
                  <input 
                    type="file" 
                    :id="`file-${param.name}`"
                    class="file-upload-hidden"
                    @change="handleFileUpload($event, param.name)"
                    :multiple="param.multiple || false"
                    :webkitdirectory="param.directory || param.name.includes('folder')"
                    :directory="param.directory || param.name.includes('folder')"
                  />
                </div>
                <p class="file-upload-hint" v-if="param.hint">{{ param.hint }}</p>
                <p class="file-upload-hint" v-else-if="param.name.includes('folder')">支持选择文件夹，会处理文件夹内所有符合条件的文件</p>
                <p class="file-upload-hint" v-else>支持选择单个或多个文件</p>
              </div>
              
              <!-- 文本和数字类型输入框 -->
              <input 
                v-else-if="param.type === 'text' || param.type === 'number'" 
                :type="param.type"
                :id="param.name"
                v-model="toolParams[param.name]"
                :placeholder="param.placeholder || ''"
                class="input"
                :class="{ 'input-error': errorMessage && !toolParams[param.name] && param.required }"
              />
              
              <!-- 文本域类型 -->
              <textarea 
                v-else-if="param.type === 'textarea'"
                :id="param.name"
                v-model="toolParams[param.name]"
                :placeholder="param.placeholder || ''"
                class="input textarea"
                :class="{ 'input-error': errorMessage && !toolParams[param.name] && param.required }"
                :rows="selectedTool && selectedTool.id === 6 ? 8 : 4"
              ></textarea>
              
              <!-- 下拉选择类型 -->
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
              
              <!-- 输入提示 -->
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

    // 获取分类文本和图标
    const getCategoryInfo = (category) => {
      const categoryMap = {
        'file': { text: '文件处理', icon: '📁', color: '#409EFF' },
        'data': { text: '数据处理', icon: '📊', color: '#67C23A' },
        'image': { text: '图片处理', icon: '🖼️', color: '#E6A23C' },
        'text': { text: '文本处理', icon: '📝', color: '#F56C6C' },
        'other': { text: '其他', icon: '🔧', color: '#909399' }
      }
      return categoryMap[category] || categoryMap['other']
    }
    
    // 获取分类文本（兼容原有调用）
    const getCategoryText = (category) => {
      return getCategoryInfo(category).text
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
        
        // 参数验证 - 检查必填参数
        // 如果required为true或undefined（默认必填），则认为是必填项
        const requiredParams = selectedTool.value.params.filter(param => {
          // 如果明确设置为false，则不是必填
          if (param.required === false) {
            return false
          }
          // 如果明确设置为true，则是必填
          if (param.required === true) {
            return true
          }
          // 如果未设置，默认认为是必填（向后兼容）
          return true
        });
        
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
        
        // 转换参数类型并处理值
        const processedParams = {}
        selectedTool.value.params.forEach(param => {
          let value = toolParams.value[param.name]
          
          // 处理默认值
          if ((value === undefined || value === null || value === '') && param.default !== undefined && param.default !== null && param.default !== '') {
            value = param.default
          }
          
          // 处理不同类型的参数
          if (value !== undefined && value !== null && value !== '') {
            if (param.type === 'number') {
              const numValue = Number(value)
              if (!isNaN(numValue)) {
                processedParams[param.name] = numValue
              }
            } else if (param.type === 'select' && value) {
              // 下拉选择的值直接使用
              processedParams[param.name] = value
            } else if (typeof value === 'string') {
              // 字符串值去除首尾空格后使用
              const trimmed = value.trim()
              if (trimmed !== '') {
                processedParams[param.name] = trimmed
              }
            } else {
              // 其他类型直接使用
              processedParams[param.name] = value
            }
          }
        })
        
        // 记录处理后的参数，便于调试
        console.log('处理后的参数:', processedParams)
        console.log('参数数量:', Object.keys(processedParams).length)
        console.log('参数键:', Object.keys(processedParams))
        
        running.value = true
        showResult.value = false
        toolResult.value = ''
        
        // 调用后端API，传递工具参数
        let result
        try {
          // 添加详细的调试日志
          console.log('调用工具API详情:', {
            toolId: selectedTool.value.id,
            toolName: selectedTool.value.title,
            params: processedParams,
            paramsStringified: JSON.stringify(processedParams),
            timestamp: new Date().toISOString()
          })
          
          // 保存请求数据到本地存储，便于调试
          localStorage.setItem('lastToolRequest', JSON.stringify({
            toolId: selectedTool.value.id,
            params: processedParams,
            timestamp: new Date().toISOString()
          }))
          
          result = await api.runTool(selectedTool.value.id, processedParams)
          
          console.log('API返回结果详情:', {
            result: result,
            timestamp: new Date().toISOString()
          })
        } catch (apiError) {
          // 处理API调用异常
          running.value = false
          
          // 添加详细的错误日志
          const errorData = apiError.response?.data || {}
          console.error('API调用异常详情:', {
            error: apiError,
            response: apiError.response,
            responseData: errorData,
            errorMessage: apiError.message,
            debugInfo: errorData.debug_info,
            timestamp: new Date().toISOString()
          })
          
          // 提取更详细的错误信息
          let errorMsg = '网络错误，请检查连接后重试'
          let errorDetails = ''
          
          if (apiError.response) {
            // 服务器返回了错误响应
            errorDetails = JSON.stringify(errorData, null, 2)
            
            // 优先显示details数组中的错误信息
            if (errorData.details && Array.isArray(errorData.details) && errorData.details.length > 0) {
              errorMsg = errorData.details.join('；')
            } else if (errorData.details && typeof errorData.details === 'string') {
              errorMsg = errorData.details
            } else if (errorData.error) {
              errorMsg = errorData.error
            } else if (errorData.message) {
              errorMsg = errorData.message
            } else if (errorData['detail']) {
              errorMsg = errorData['detail']
            } else {
              errorMsg = `服务器返回错误：${JSON.stringify(errorData)}`
            }
            
            // 如果有debug_info，添加到详细信息中
            if (errorData.debug_info) {
              errorDetails += '\n\n调试信息：\n' + JSON.stringify(errorData.debug_info, null, 2)
            }
          } else if (apiError.message) {
            errorMsg = apiError.message
          }
          
          showError(errorMsg)
          toolResult.value = `❌ 工具运行异常！\n\n异常信息：${errorMsg}\n\n详细信息：${errorDetails}`
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
    
    // 处理文件上传
    const handleFileUpload = (event, paramName) => {
      const fileInput = event.target
      if (fileInput.files && fileInput.files.length > 0) {
        const files = Array.from(fileInput.files)
        
        // 如果是文件夹选择，获取文件夹路径
        if (fileInput.webkitdirectory || fileInput.directory) {
          // 获取第一个文件的路径，然后截取到文件夹部分
          const firstFilePath = files[0].webkitRelativePath || files[0].path
          const folderPath = firstFilePath.substring(0, firstFilePath.indexOf('/'))
          toolParams.value[paramName] = folderPath
        } 
        // 如果是文件选择，获取文件名列表或单个文件路径
        else if (fileInput.multiple) {
          // 对于多文件选择，保存文件列表
          toolParams.value[paramName] = files.map(file => file.name).join(', ')
          // 保存实际文件对象，用于后续处理
          toolParams.value[`${paramName}_files`] = files
        } 
        else {
          // 单个文件选择，保存文件路径
          toolParams.value[paramName] = files[0].name
          // 保存实际文件对象
          toolParams.value[`${paramName}_file`] = files[0]
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
        const realToolsResponse = await api.getTools()
        // 处理后端返回的分页数据结构
        const realTools = realToolsResponse.results || realToolsResponse
        if (realTools && realTools.length > 0) {
          // 转换后端数据格式为前端需要的格式
          tools.value = realTools.map(tool => {
            // 处理分类信息，兼容category_name和category字段
            let category = 'other';
            
            // 分类ID到分类名称的映射
            const categoryIdMap = {
              1: 'file',
              2: 'data',
              3: 'image',
              4: 'text'
            };
            
            // 分类名称到分类标识的映射（支持中文和英文）
            const categoryNameMap = {
              '文件处理': 'file',
              '数据处理': 'data',
              '图片处理': 'image',
              '文本处理': 'text',
              '文件': 'file',
              '数据': 'data',
              '图片': 'image',
              '文本': 'text',
              'file': 'file',
              'data': 'data',
              'image': 'image',
              'text': 'text'
            };
            
            // 处理category_id（如果存在）
            if (tool.category_id) {
              category = categoryIdMap[tool.category_id] || 'other';
            }
            // 处理category（如果存在，可能是数字或字符串）
            else if (tool.category) {
              if (typeof tool.category === 'number') {
                category = categoryIdMap[tool.category] || 'other';
              } else {
                category = categoryNameMap[tool.category] || 'other';
              }
            }
            // 处理category_name（如果存在）
            else if (tool.category_name) {
              category = categoryNameMap[tool.category_name] || 'other';
            }
            
            // 图标映射：将后端返回的图标名称映射到对应的emoji
            const iconMap = {
              'file-text': '📄',
              'file': '📁',
              'file-excel': '📊',
              'file-image': '🖼️',
              'text': '📝',
              'code': '💻',
              'tool': '🔧',
              'settings': '⚙️',
              'database': '🗄️',
              'image': '🖼️',
              'file-json': '📋'
            };
            
            // 处理图标
            let icon = '🔧'; // 默认图标
            if (tool.icon) {
              icon = iconMap[tool.icon] || '🔧';
            }
            
            return {
              id: tool.id,
              title: tool.title || tool.name || '未命名工具', // 兼容后端可能返回的name字段
              description: tool.description || '无描述',
              icon: icon,
              category: category,
              bookId: tool.book_id,
              bookTitle: tool.book_title || '未指定教材',
              chapterNumber: tool.chapter_number || 0,
              firstSectionId: tool.first_section_id,
              params: (tool.params || []).map(param => ({
        name: param.name,
        label: param.label,
        type: param.type,
        placeholder: param.placeholder || '',
        required: param.is_required === true || param.is_required === '1' || param.is_required === 1,
        default: param.default_value || (param.type === 'number' ? (param.name === 'indentSize' ? 2 : 0) : ''),
        options: param.options || []
      }))
            };
          })
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
      getCategoryInfo,
      openTool,
      closeTool,
      runTool,
      saveResult,
      getFormattedJson,
      copyJson,
      clearMessages,
      handleFileUpload
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
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  margin-bottom: 15px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0,0,0,0.08);
}

.tool-category:hover {
  transform: translateY(-1px);
  box-shadow: 0 3px 6px rgba(0,0,0,0.12);
}

.category-icon {
  font-size: 14px;
  vertical-align: middle;
}

.category-text {
  vertical-align: middle;
}

/* 工具详情弹窗中的分类图标样式 */
.tool-meta .category-icon {
  margin-right: 4px;
  font-size: 16px;
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

/* 文件上传组件样式 */
.file-upload-container {
  margin-bottom: 20px;
}

.file-input-wrapper {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 8px;
}

.file-input-text {
  flex: 1;
  cursor: not-allowed;
  background-color: #fafafa;
}

.file-upload-btn {
  background: #409EFF;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s;
  white-space: nowrap;
}

.file-upload-btn:hover {
  background: #66b1ff;
}

.file-upload-hidden {
  display: none;
}

.file-upload-hint {
  margin: 5px 0 0 0;
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
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
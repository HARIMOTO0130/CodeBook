<template>
  <div class="console-output">
    <div class="console-header">
      <div class="console-title">
        <span class="icon">📊</span>
        <span>控制台输出</span>
      </div>
      <div class="console-actions">
        <button class="action-btn" @click="clearOutput" title="清屏">
          🧹 清屏
        </button>
        <button class="action-btn" @click="copyOutput" title="复制">
          📋 复制
        </button>
        <button class="action-btn" @click="toggleExpanded" title="展开/收起">
          {{ expanded ? '📱 收起' : '📱 展开' }}
        </button>
      </div>
    </div>
    
    <div class="console-body" :class="{ 'expanded': expanded }">
      <div v-if="output.length === 0" class="empty-output">
        <p>暂无输出</p>
        <small>运行代码后，输出将显示在这里</small>
      </div>
      
      <div v-else class="output-content" ref="outputContainer">
        <div 
          v-for="(line, index) in output" 
          :key="index"
          class="output-line"
          :class="getLineClass(line)"
        >
          <!-- 普通文本行 -->
          <span v-if="!line.isObject" v-html="formatLine(line.content)"></span>
          
          <!-- 对象/数组格式化显示 -->
          <div v-else class="object-output">
            <div class="object-preview" @click="toggleObjectExpand(index)">
              <span class="expand-icon">{{ line.expanded ? '▼' : '▶' }}</span>
              <span class="object-type">{{ getObjectType(line.content) }}</span>
              <span class="object-summary">{{ getObjectSummary(line.content) }}</span>
            </div>
            
            <div v-if="line.expanded" class="object-details">
              <pre>{{ JSON.stringify(line.content, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 图表输出 -->
      <div v-if="charts.length > 0" class="charts-container">
        <div 
          v-for="(chart, index) in charts" 
          :key="index"
          class="chart-item"
        >
          <div class="chart-header">
            <span class="chart-title">{{ chart.title || `图表 ${index + 1}` }}</span>
            <button class="chart-close" @click="removeChart(index)">×</button>
          </div>
          <div class="chart-content" ref="chartContainers[index]">
            <!-- 这里使用简单的图表模拟，实际应用中可以使用Chart.js等库 -->
            <div v-if="chart.type === 'bar'" class="bar-chart">
              <div 
                v-for="(item, i) in chart.data" 
                :key="i"
                class="bar-item"
              >
                <div 
                  class="bar" 
                  :style="{ 
                    height: `${(item.value / chart.maxValue) * 100}%`,
                    backgroundColor: getBarColor(i)
                  }"
                ></div>
                <span class="bar-label">{{ item.label }}</span>
                <span class="bar-value">{{ item.value }}</span>
              </div>
            </div>
            
            <div v-else-if="chart.type === 'line'" class="line-chart">
              <!-- 简化的折线图表示 -->
              <div class="line-container">
                <svg width="100%" height="150">
                  <polyline 
                    :points="getLinePoints(chart.data)"
                    fill="none"
                    stroke="#409EFF"
                    stroke-width="2"
                  />
                  <circle 
                    v-for="(item, i) in chart.data" 
                    :key="i"
                    :cx="getPointX(i, chart.data.length)"
                    :cy="getPointY(item.value, chart.maxValue)"
                    r="4"
                    fill="#409EFF"
                  />
                </svg>
              </div>
              <div class="line-labels">
                <span 
                  v-for="(item, i) in chart.data" 
                  :key="i"
                  class="line-label"
                >
                  {{ item.label }}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 标准输入区域 -->
    <div v-if="showStdin" class="stdin-section">
      <input 
        type="text" 
        v-model="stdinInput" 
        class="stdin-input"
        @keypress.enter="handleStdinSubmit"
        placeholder="输入内容，按Enter发送..."
      />
      <button class="stdin-btn" @click="handleStdinSubmit">发送</button>
    </div>
  </div>
</template>

<script>
import { ref, watch, nextTick } from 'vue'

export default {
  name: 'ConsoleOutput',
  props: {
    output: {
      type: Array,
      default: () => []
    },
    charts: {
      type: Array,
      default: () => []
    },
    expanded: {
      type: Boolean,
      default: true
    },
    showStdin: {
      type: Boolean,
      default: true
    },
    autoScroll: {
      type: Boolean,
      default: true
    }
  },
  emits: ['update:expanded', 'stdinSubmit', 'clear'],
  setup(props, { emit }) {
    const outputContainer = ref(null)
    const chartContainers = ref([])
    const stdinInput = ref('')
    
    // 监听输出变化，自动滚动到底部
    watch(() => props.output.length, () => {
      if (props.autoScroll && outputContainer.value) {
        nextTick(() => {
          outputContainer.value.scrollTop = outputContainer.value.scrollHeight
        })
      }
    })
    
    // 初始化图表容器引用
    watch(() => props.charts.length, (newLength) => {
      chartContainers.value = Array(newLength).fill().map(() => ref(null))
    }, { immediate: true })
    
    // 获取行样式类
    const getLineClass = (line) => {
      const classes = []
      
      if (line.type) {
        classes.push(`type-${line.type}`)
      }
      
      if (line.isError) {
        classes.push('error')
      }
      
      if (line.isWarning) {
        classes.push('warning')
      }
      
      if (line.isSuccess) {
        classes.push('success')
      }
      
      return classes
    }
    
    // 格式化输出行（处理ANSI颜色等）
    const formatLine = (content) => {
      // 如果content是对象，提取其content属性
      if (typeof content === 'object' && content !== null) {
        content = content.content
      }
      if (typeof content !== 'string') return content
      
      // 简单的ANSI颜色处理示例
      let formatted = content
      
      // 移除ANSI颜色代码，但保留其语义
      formatted = formatted
        .replace(/\u001b\[31m([^\u001b]*)/g, '<span class="ansi-red">$1</span>')
        .replace(/\u001b\[32m([^\u001b]*)/g, '<span class="ansi-green">$1</span>')
        .replace(/\u001b\[33m([^\u001b]*)/g, '<span class="ansi-yellow">$1</span>')
        .replace(/\u001b\[34m([^\u001b]*)/g, '<span class="ansi-blue">$1</span>')
        .replace(/\u001b\[35m([^\u001b]*)/g, '<span class="ansi-purple">$1</span>')
        .replace(/\u001b\[36m([^\u001b]*)/g, '<span class="ansi-cyan">$1</span>')
        .replace(/\u001b\[\d+m/g, '') // 移除剩余的ANSI控制码
        .replace(/\n/g, '<br>') // 换行处理
        .replace(/\t/g, '&nbsp;&nbsp;&nbsp;&nbsp;') // Tab处理
        .replace(/ /g, '&nbsp;') // 空格处理
      
      // 处理错误信息的高亮显示
      if (typeof content === 'string' && (content.includes('SyntaxError') || content.includes('IndentationError') || 
          content.includes('NameError') || content.includes('TypeError') || 
          content.includes('AttributeError'))) {
        // 高亮显示错误类型
        formatted = formatted.replace(/(SyntaxError|IndentationError|NameError|TypeError|AttributeError):/g, '<span class="error-highlight">$1:</span>')
      }
      
      // 高亮显示行号信息
      formatted = formatted.replace(/(File ".*", line \d+)/g, '<span class="line-highlight">$1</span>')
      
      return formatted
    }
    
    // 切换对象展开状态
    const toggleObjectExpand = (index) => {
      // 通知父组件切换展开状态
      // 这里需要父组件配合实现展开状态的管理
      console.log(`Toggle expand for object at index ${index}`)
    }
    
    // 获取对象类型
    const getObjectType = (obj) => {
      if (obj === null) return 'null'
      if (Array.isArray(obj)) return 'Array'
      return typeof obj
    }
    
    // 获取对象摘要
    const getObjectSummary = (obj) => {
      if (obj === null) return ''
      if (Array.isArray(obj)) return `[${obj.length} items]`
      if (typeof obj === 'object') {
        const keys = Object.keys(obj)
        return `{${keys.length} properties}`
      }
      return String(obj)
    }
    
    // 切换展开/收起
    const toggleExpanded = () => {
      emit('update:expanded', !props.expanded)
    }
    
    // 清屏
    const clearOutput = () => {
      emit('clear')
    }
    
    // 复制输出
    const copyOutput = async () => {
      const textToCopy = props.output.map(line => {
        if (line.isObject) {
          return JSON.stringify(line.content, null, 2)
        }
        return line.content
      }).join('\n')
      
      try {
        await navigator.clipboard.writeText(textToCopy)
        // 可以添加一个临时提示
        console.log('输出已复制到剪贴板')
      } catch (err) {
        console.error('复制失败:', err)
      }
    }
    
    // 处理标准输入提交
    const handleStdinSubmit = () => {
      if (stdinInput.value.trim()) {
        emit('stdinSubmit', stdinInput.value)
        stdinInput.value = ''
      }
    }
    
    // 移除图表
    const removeChart = (index) => {
      // 通知父组件移除图表
      console.log(`Remove chart at index ${index}`)
    }
    
    // 获取柱状图颜色
    const getBarColor = (index) => {
      const colors = [
        '#409EFF', '#67C23A', '#E6A23C', '#F56C6C', 
        '#909399', '#C0C4CC', '#DCDFE6'
      ]
      return colors[index % colors.length]
    }
    
    // 获取折线图点
    const getLinePoints = (data) => {
      return data.map((item, index) => {
        const x = getPointX(index, data.length)
        const y = getPointY(item.value, Math.max(...data.map(d => d.value)))
        return `${x},${y}`
      }).join(' ')
    }
    
    // 获取点的X坐标
    const getPointX = (index, total) => {
      const padding = 50
      const width = 300 - padding * 2
      return padding + (index / (total - 1)) * width
    }
    
    // 获取点的Y坐标
    const getPointY = (value, maxValue) => {
      const padding = 20
      const height = 150 - padding * 2
      return 150 - padding - (value / maxValue) * height
    }
    
    return {
      outputContainer,
      chartContainers,
      stdinInput,
      getLineClass,
      formatLine,
      toggleObjectExpand,
      getObjectType,
      getObjectSummary,
      toggleExpanded,
      clearOutput,
      copyOutput,
      handleStdinSubmit,
      removeChart,
      getBarColor,
      getLinePoints,
      getPointX,
      getPointY
    }
  }
}
</script>

<style scoped>
.console-output {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 200px;
}

/* 头部样式 */
.console-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  border-radius: 8px 8px 0 0;
}

.console-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #333;
}

.console-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 6px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.action-btn:hover {
  background: #f0f0f0;
  border-color: #bbb;
}

/* 主体样式 */
.console-body {
  flex: 1;
  overflow: auto;
  padding: 16px;
  transition: height 0.3s ease;
}

.console-body:not(.expanded) {
  height: 150px;
}

.empty-output {
  text-align: center;
  color: #999;
  padding: 40px 20px;
}

.empty-output p {
  margin: 0 0 8px 0;
  font-size: 14px;
}

.empty-output small {
  font-size: 12px;
}

.output-content {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.output-line {
  margin-bottom: 8px;
  padding: 2px 0;
}

/* 输出类型样式 */
.output-line.error {
  color: #f56c6c;
}

.output-line.warning {
  color: #e6a23c;
}

.output-line.success {
  color: #67c23a;
}

.output-line.type-log {
  color: #303133;
}

.output-line.type-debug {
  color: #409eff;
}

/* ANSI颜色样式 */
.ansi-red { color: #f56c6c; }
.ansi-green { color: #67c23a; }
.ansi-yellow { color: #e6a23c; }
.ansi-blue { color: #409eff; }
.ansi-purple { color: #909399; }
.ansi-cyan { color: #66b1ff; }

/* 错误高亮样式 */
.error-highlight {
  color: #f56c6c;
  font-weight: bold;
}

/* 行号高亮样式 */
.line-highlight {
  color: #409eff;
  font-weight: bold;
}

/* 对象输出样式 */
.object-output {
  margin-left: 20px;
}

.object-preview {
  cursor: pointer;
  padding: 4px 8px;
  background: #f5f5f5;
  border-radius: 4px;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  user-select: none;
}

.object-preview:hover {
  background: #e0e0e0;
}

.expand-icon {
  font-size: 10px;
  width: 12px;
  text-align: center;
}

.object-type {
  font-weight: 600;
  color: #409eff;
}

.object-summary {
  color: #666;
  font-size: 12px;
}

.object-details {
  margin-top: 8px;
  margin-left: 20px;
  padding: 12px;
  background: #fafafa;
  border-radius: 4px;
  border-left: 3px solid #409eff;
  overflow-x: auto;
}

.object-details pre {
  margin: 0;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  line-height: 1.4;
  white-space: pre-wrap;
}

/* 图表容器 */
.charts-container {
  margin-top: 20px;
  border-top: 1px solid #e0e0e0;
  padding-top: 20px;
}

.chart-item {
  margin-bottom: 20px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.chart-title {
  font-weight: 500;
  font-size: 14px;
}

.chart-close {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
  padding: 0;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-close:hover {
  color: #333;
}

.chart-content {
  padding: 16px;
  min-height: 150px;
}

/* 简单图表样式 */
.bar-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  height: 150px;
  padding: 0 10px;
}

.bar-item {
  flex: 1;
  margin: 0 5px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  height: 100%;
}

.bar {
  width: 80%;
  border-radius: 4px 4px 0 0;
  transition: height 0.5s ease;
}

.bar-label {
  margin-top: 8px;
  font-size: 12px;
  color: #666;
  text-align: center;
}

.bar-value {
  margin-top: 4px;
  font-size: 12px;
  font-weight: 500;
}

.line-chart {
  height: 150px;
  position: relative;
}

.line-container {
  height: 150px;
  position: relative;
}

.line-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
}

.line-label {
  font-size: 12px;
  color: #666;
  text-align: center;
  flex: 1;
}

/* 标准输入区域 */
.stdin-section {
  display: flex;
  padding: 12px 16px;
  background: #f5f5f5;
  border-top: 1px solid #e0e0e0;
  gap: 10px;
}

.stdin-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

.stdin-input:focus {
  outline: none;
  border-color: #409eff;
}

.stdin-btn {
  padding: 8px 20px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: background 0.2s;
}

.stdin-btn:hover {
  background: #66b1ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .console-header {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .console-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .console-title {
    justify-content: center;
  }
  
  .action-btn {
    font-size: 11px;
    padding: 5px 8px;
  }
  
  .stdin-section {
    flex-direction: column;
  }
  
  .bar-chart {
    height: 120px;
  }
  
  .bar-label {
    font-size: 10px;
  }
  
  .line-label {
    font-size: 10px;
  }
}
</style>
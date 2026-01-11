<template>
  <div class="code-playground">
    <div class="tool-header">
      <div class="language-selector">
        <label>编程语言</label>
        <select v-model="selectedLanguage">
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="html">HTML</option>
          <option value="css">CSS</option>
        </select>
      </div>
      <div class="theme-selector">
        <label>代码主题</label>
        <select v-model="codeTheme">
          <option value="vs-dark">深色主题</option>
          <option value="light">浅色主题</option>
        </select>
      </div>
      <div class="font-size">
        <label>字体大小</label>
        <select v-model="fontSize">
          <option value="12">12px</option>
          <option value="14">14px</option>
          <option value="16">16px</option>
          <option value="18">18px</option>
        </select>
      </div>
    </div>

    <div class="playground-container">
      <div class="editor-section">
        <div class="section-header">
          <span class="section-title">代码编辑器</span>
          <div class="editor-actions">
            <button class="action-btn" @click="formatCode" title="格式化代码">
              <span>📐</span>
            </button>
            <button class="action-btn" @click="copyCode" title="复制代码">
              <span>📋</span>
            </button>
            <button class="action-btn" @click="clearCode" title="清空代码">
              <span>🗑️</span>
            </button>
          </div>
        </div>
        <div class="code-editor" ref="codeEditor">
          <div class="line-numbers">
            <span v-for="n in lineCount" :key="n">{{ n }}</span>
          </div>
          <textarea
            v-model="code"
            @input="updateLineCount"
            @keydown="handleKeydown"
            spellcheck="false"
            :style="{ fontSize: fontSize + 'px' }"
          ></textarea>
        </div>
      </div>

      <div class="output-section">
        <div class="section-header">
          <span class="section-title">运行结果</span>
          <div class="output-actions">
            <button class="run-btn" @click="runCode">
              <span>▶️</span> 运行代码
            </button>
            <button class="action-btn" @click="clearOutput" title="清空输出">
              <span>🗑️</span>
            </button>
          </div>
        </div>
        <div class="output-content" ref="outputContent">
          <div v-if="output" class="output-text" :class="{ error: isError }">
            <pre>{{ output }}</pre>
          </div>
          <div v-else class="output-placeholder">
            <span>💻</span>
            <p>点击"运行代码"查看输出结果</p>
          </div>
        </div>
      </div>
    </div>

    <div class="templates-section">
      <h3>代码模板</h3>
      <div class="templates-grid">
        <div
          v-for="template in templates"
          :key="template.id"
          class="template-card"
          @click="loadTemplate(template)"
        >
          <span class="template-icon">{{ template.icon }}</span>
          <span class="template-name">{{ template.name }}</span>
          <span class="template-desc">{{ template.description }}</span>
        </div>
      </div>
    </div>

    <div class="history-section">
      <h3>运行历史</h3>
      <div class="history-list">
        <div
          v-for="(record, index) in runHistory"
          :key="index"
          class="history-item"
        >
          <div class="history-info">
            <span class="history-lang">{{ record.language }}</span>
            <span class="history-time">{{ record.time }}</span>
          </div>
          <div class="history-code">
            {{ record.code.substring(0, 50) }}{{ record.code.length > 50 ? '...' : '' }}
          </div>
          <span
            class="history-status"
            :class="{ success: record.success, error: !record.success }"
          >
            {{ record.success ? '成功' : '失败' }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'CodePlayground',
  setup() {
    const selectedLanguage = ref('python')
    const codeTheme = ref('vs-dark')
    const fontSize = ref(14)
    const code = ref('')
    const output = ref('')
    const isError = ref(false)
    const runHistory = ref([])

    const codeEditor = ref(null)
    const outputContent = ref(null)

    const templates = ref([
      { id: 1, name: 'Hello World', icon: '👋', description: '经典入门程序', language: 'python', code: 'print("Hello, World!")' },
      { id: 2, name: '计算器', icon: '🧮', description: '简单四则运算', language: 'python', code: 'a = 10\nb = 5\nprint(f"{a} + {b} = {a + b}")\nprint(f"{a} - {b} = {a - b}")\nprint(f"{a} * {b} = {a * b}")\nprint(f"{a} / {b} = {a / b}")' },
      { id: 3, name: '列表操作', icon: '📋', description: '列表常用操作', language: 'python', code: 'fruits = ["apple", "banana", "cherry"]\nprint("水果列表:", fruits)\nprint("第一个水果:", fruits[0])\nprint("水果数量:", len(fruits))\nfruits.append("date")\nprint("添加后:", fruits)' },
      { id: 4, name: '函数定义', icon: '⚡', description: 'Python函数示例', language: 'python', code: 'def greet(name):\n    """打招呼函数"""\n    return f"Hello, {name}! Welcome to Python!"\n\nprint(greet("Teacher"))\nprint(greet("Student"))' },
      { id: 5, name: '循环示例', icon: '🔄', description: 'for循环演示', language: 'python', code: '# 打印1到10的平方\nfor i in range(1, 11):\n    square = i ** 2\n    print(f"{i}的平方是: {square}")' },
      { id: 6, name: '条件判断', icon: '❓', description: 'if-else示例', language: 'python', code: 'score = 85\n\nif score >= 90:\n    grade = "优秀"\nelif score >= 80:\n    grade = "良好"\nelif score >= 60:\n    grade = "及格"\nelse:\n    grade = "不及格"\n\nprint(f"成绩: {score}分, 等级: {grade}")' }
    ])

    const lineCount = computed(() => {
      const lines = code.value.split('\n')
      return lines.length > 1 ? lines.length : 1
    })

    const updateLineCount = () => {}

    const handleKeydown = (e) => {
      if (e.key === 'Tab') {
        e.preventDefault()
        const start = e.target.selectionStart
        const end = e.target.selectionEnd
        code.value = code.value.substring(0, start) + '    ' + code.value.substring(end)
      }
    }

    const formatCode = () => {
      alert('格式化功能开发中...')
    }

    const copyCode = () => {
      navigator.clipboard.writeText(code.value)
      alert('代码已复制到剪贴板！')
    }

    const clearCode = () => {
      if (confirm('确定要清空代码吗？')) {
        code.value = ''
        output.value = ''
      }
    }

    const clearOutput = () => {
      output.value = ''
      isError.value = false
    }

    const runCode = () => {
      if (!code.value.trim()) {
        output.value = '请输入代码后再运行！'
        isError.value = true
        return
      }

      try {
        let result = ''
        const lines = code.value.split('\n')
        
        lines.forEach(line => {
          line = line.trim()
          if (line.startsWith('print(')) {
            const match = line.match(/print\((.*)\)/)
            if (match) {
              let content = match[1]
              content = content.replace(/"/g, '').replace(/'/g, '')
              result += content + '\n'
            }
          }
        })

        if (result) {
          output.value = result.trim()
          isError.value = false
        } else {
          output.value = '代码执行完成（没有输出）'
          isError.value = false
        }

        runHistory.value.unshift({
          language: selectedLanguage.value,
          code: code.value,
          time: new Date().toLocaleTimeString(),
          success: true
        })

        if (runHistory.value.length > 10) {
          runHistory.value.pop()
        }
      } catch (error) {
        output.value = '错误: ' + error.message
        isError.value = true

        runHistory.value.unshift({
          language: selectedLanguage.value,
          code: code.value,
          time: new Date().toLocaleTimeString(),
          success: false
        })
      }
    }

    const loadTemplate = (template) => {
      selectedLanguage.value = template.language
      code.value = template.code
    }

    watch(selectedLanguage, (newLang) => {
      code.value = ''
      output.value = ''
    })

    return {
      selectedLanguage,
      codeTheme,
      fontSize,
      code,
      output,
      isError,
      runHistory,
      codeEditor,
      outputContent,
      templates,
      lineCount,
      updateLineCount,
      handleKeydown,
      formatCode,
      copyCode,
      clearCode,
      clearOutput,
      runCode,
      loadTemplate
    }
  }
}
</script>

<style scoped>
.code-playground {
  padding: 20px;
}

.tool-header {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  background: #f8fafc;
  padding: 16px 20px;
  border-radius: 12px;
}

.tool-header > div {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tool-header label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.tool-header select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  background: white;
  min-width: 120px;
  cursor: pointer;
}

.tool-header select:focus {
  border-color: #3b82f6;
}

.playground-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.editor-section,
.output-section {
  background: #1e1e1e;
  border-radius: 12px;
  overflow: hidden;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #2d2d2d;
  border-bottom: 1px solid #404040;
}

.section-title {
  color: #d4d4d4;
  font-size: 14px;
  font-weight: 500;
}

.editor-actions,
.output-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  background: #3d3d3d;
  border: none;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.action-btn:hover {
  background: #4d4d4d;
}

.run-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.run-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(34, 197, 94, 0.4);
}

.code-editor {
  display: flex;
  min-height: 300px;
}

.line-numbers {
  display: flex;
  flex-direction: column;
  padding: 12px 0;
  background: #1e1e1e;
  color: #6e6e6e;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.6;
  text-align: right;
  padding-right: 12px;
  border-right: 1px solid #404040;
  min-width: 50px;
}

.line-numbers span {
  padding: 0 8px;
}

.code-editor textarea {
  flex: 1;
  background: #1e1e1e;
  color: #d4d4d4;
  border: none;
  outline: none;
  padding: 12px;
  font-family: 'Consolas', 'Monaco', monospace;
  line-height: 1.6;
  resize: none;
}

.output-content {
  min-height: 300px;
  max-height: 400px;
  overflow-y: auto;
  padding: 16px;
}

.output-text {
  color: #4ec9b0;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.6;
}

.output-text.error {
  color: #f14c4c;
}

.output-text pre {
  margin: 0;
  white-space: pre-wrap;
}

.output-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6e6e6e;
}

.output-placeholder span {
  font-size: 48px;
  margin-bottom: 12px;
}

.output-placeholder p {
  font-size: 14px;
}

.templates-section,
.history-section {
  margin-bottom: 24px;
}

.templates-section h3,
.history-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.templates-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
}

.template-card {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.template-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
  transform: translateY(-2px);
}

.template-icon {
  font-size: 32px;
  display: block;
  margin-bottom: 8px;
}

.template-name {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
  display: block;
  margin-bottom: 4px;
}

.template-desc {
  font-size: 12px;
  color: #94a3b8;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: #f8fafc;
  border-radius: 10px;
}

.history-info {
  display: flex;
  flex-direction: column;
  min-width: 100px;
}

.history-lang {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.history-time {
  font-size: 12px;
  color: #94a3b8;
}

.history-code {
  flex: 1;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  color: #64748b;
  background: white;
  padding: 8px 12px;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.history-status {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  font-weight: 500;
}

.history-status.success {
  background: #dcfce7;
  color: #166534;
}

.history-status.error {
  background: #fef2f2;
  color: #dc2626;
}

@media (max-width: 1024px) {
  .playground-container {
    grid-template-columns: 1fr;
  }

  .templates-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .tool-header {
    flex-direction: column;
  }

  .templates-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

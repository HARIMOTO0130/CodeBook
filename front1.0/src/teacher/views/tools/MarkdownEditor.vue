<template>
  <div class="markdown-editor">
    <div class="tool-header">
      <div class="file-info">
        <input
          type="text"
          v-model="fileName"
          placeholder="输入文件名..."
          class="filename-input"
        />
        <span class="file-ext">.md</span>
      </div>
      <div class="header-actions">
        <button class="btn btn-secondary" @click="newFile">
          <span>📄</span> 新建
        </button>
        <button class="btn btn-secondary" @click="loadFile">
          <span>📂</span> 打开
        </button>
        <button class="btn btn-secondary" @click="saveFile">
          <span>💾</span> 保存
        </button>
        <button class="btn btn-primary" @click="exportFile">
          <span>📤</span> 导出
        </button>
      </div>
    </div>

    <div class="editor-container">
      <div class="editor-panel">
        <div class="panel-header">
          <span>编辑区</span>
          <div class="panel-actions">
            <button class="tool-btn" @click="insertText('# ')" title="标题">
              H
            </button>
            <button class="tool-btn" @click="insertText('**粗体**')" title="粗体">
              <strong>B</strong>
            </button>
            <button class="tool-btn" @click="insertText('*斜体*')" title="斜体">
              <em>I</em>
            </button>
            <button class="tool-btn" @click="insertText('~~删除线~~')" title="删除线">
              <s>S</s>
            </button>
            <button class="tool-btn" @click="insertText('```\n\n```')" title="代码块">
              &lt;/&gt;
            </button>
            <button class="tool-btn" @click="insertText('> ')" title="引用">
              ❝
            </button>
            <button class="tool-btn" @click="insertText('- ')" title="列表">
              •
            </button>
            <button class="tool-btn" @click="insertText('1. ')" title="有序列表">
              1.
            </button>
            <button class="tool-btn" @click="insertText('![alt](url)')" title="图片">
              🖼️
            </button>
            <button class="tool-btn" @click="insertText('[链接](url)')" title="链接">
              🔗
            </button>
            <button class="tool-btn" @click="insertText('---')" title="分割线">
              ―
            </button>
          </div>
        </div>
        <textarea
          v-model="content"
          @input="updatePreview"
          @keydown="handleKeydown"
          placeholder="在此输入Markdown内容..."
          spellcheck="false"
        ></textarea>
      </div>

      <div class="preview-panel">
        <div class="panel-header">
          <span>预览区</span>
          <div class="preview-info">
            <span class="word-count">{{ wordCount }} 字</span>
            <span class="char-count">{{ charCount }} 字符</span>
          </div>
        </div>
        <div class="preview-content" v-html="previewHtml"></div>
      </div>
    </div>

    <div class="quick-guide">
      <h3>Markdown 语法快速参考</h3>
      <div class="guide-grid">
        <div class="guide-item">
          <span class="guide-title">标题</span>
          <code># 一级标题</code>
          <code>## 二级标题</code>
          <code>### 三级标题</code>
        </div>
        <div class="guide-item">
          <span class="guide-title">文本</span>
          <code>**粗体**</code>
          <code>*斜体*</code>
          <code>~~删除线~~</code>
        </div>
        <div class="guide-item">
          <span class="guide-title">列表</span>
          <code>- 无序列表</code>
          <code>1. 有序列表</code>
        </div>
        <div class="guide-item">
          <span class="guide-title">代码</span>
          <code>`行内代码`</code>
          <code>```代码块```</code>
        </div>
        <div class="guide-item">
          <span class="guide-title">链接</span>
          <code>[链接](URL)</code>
          <code>![图片](URL)</code>
        </div>
        <div class="guide-item">
          <span class="guide-title">其他</span>
          <code>> 引用</code>
          <code>--- 分割线</code>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'MarkdownEditor',
  setup() {
    const fileName = ref('未命名文档')
    const content = ref('# 欢迎使用 Markdown 编辑器\n\n在这里您可以轻松编写格式化的文档。\n\n## 主要功能\n\n- **实时预览**：编辑内容立即显示预览效果\n- **丰富工具栏**：快速插入常用Markdown语法\n- **多种导出**：支持导出为HTML、PDF等格式\n\n## 示例代码\n\n```python\ndef greet(name):\n    """打招呼函数"""\n    return f"Hello, {name}!"\n\nprint(greet("World"))\n```\n\n> 好的文档让教学更高效！\n\n---\n\n希望这个工具对您的教学工作有所帮助。')

    const wordCount = computed(() => {
      const text = content.value.trim()
      if (!text) return 0
      return text.split(/\s+/).filter(word => word.length > 0).length
    })

    const charCount = computed(() => content.value.length)

    const previewHtml = computed(() => {
      let html = content.value
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/\*([^*]+)\*/g, '<em>$1</em>')
        .replace(/~~([^~]+)~~/g, '<del>$1</del>')
        .replace(/^> (.*$)/gm, '<blockquote>$1</blockquote>')
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        .replace(/^- (.*$)/gm, '<li>$1</li>')
        .replace(/^(\d+)\. (.*$)/gm, '<li>$2</li>')
        .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" />')
        .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2">$1</a>')
        .replace(/^---$/gm, '<hr />')
        .replace(/\n/g, '<br />')
      return html
    })

    const updatePreview = () => {}

    const handleKeydown = (e) => {
      if (e.key === 'Tab') {
        e.preventDefault()
        const start = e.target.selectionStart
        const end = e.target.selectionEnd
        content.value = content.value.substring(0, start) + '  ' + content.value.substring(end)
      }
    }

    const insertText = (text) => {
      const textarea = document.querySelector('.editor-panel textarea')
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      content.value = content.value.substring(0, start) + text + content.value.substring(end)
      setTimeout(() => {
        textarea.focus()
        textarea.setSelectionRange(start + text.length, start + text.length)
      }, 0)
    }

    const newFile = () => {
      if (confirm('新建将清空当前内容，是否继续？')) {
        content.value = ''
        fileName.value = '未命名文档'
      }
    }

    const loadFile = () => {
      alert('打开文件功能开发中...')
    }

    const saveFile = () => {
      localStorage.setItem('markdown_content', content.value)
      localStorage.setItem('markdown_filename', fileName.value)
      alert('文件已保存！')
    }

    const exportFile = () => {
      alert('导出功能开发中...')
    }

    return {
      fileName,
      content,
      wordCount,
      charCount,
      previewHtml,
      updatePreview,
      handleKeydown,
      insertText,
      newFile,
      loadFile,
      saveFile,
      exportFile
    }
  }
}
</script>

<style scoped>
.markdown-editor {
  padding: 20px;
}

.tool-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  background: #f8fafc;
  padding: 16px 20px;
  border-radius: 12px;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filename-input {
  border: none;
  background: white;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  color: #1e293b;
  outline: none;
  min-width: 200px;
}

.filename-input:focus {
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
}

.file-ext {
  color: #94a3b8;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.editor-container {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.editor-panel,
.preview-panel {
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.panel-actions {
  display: flex;
  gap: 6px;
}

.tool-btn {
  width: 32px;
  height: 32px;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.tool-btn:hover {
  background: #f1f5f9;
  border-color: #3b82f6;
}

.editor-panel textarea {
  flex: 1;
  border: none;
  outline: none;
  padding: 16px;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.8;
  resize: none;
  min-height: 400px;
}

.preview-info {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #64748b;
}

.preview-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  min-height: 400px;
  line-height: 1.8;
}

.preview-content :deep(h1) {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin: 16px 0 12px 0;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 8px;
}

.preview-content :deep(h2) {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin: 14px 0 10px 0;
}

.preview-content :deep(h3) {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 12px 0 8px 0;
}

.preview-content :deep(p) {
  margin: 10px 0;
  color: #475569;
}

.preview-content :deep(strong) {
  font-weight: 600;
  color: #1e293b;
}

.preview-content :deep(em) {
  font-style: italic;
}

.preview-content :deep(del) {
  text-decoration: line-through;
  color: #94a3b8;
}

.preview-content :deep(blockquote) {
  border-left: 4px solid #3b82f6;
  margin: 12px 0;
  padding: 10px 16px;
  background: #f8fafc;
  color: #64748b;
}

.preview-content :deep(ul),
.preview-content :deep(ol) {
  margin: 10px 0;
  padding-left: 24px;
}

.preview-content :deep(li) {
  margin: 6px 0;
  color: #475569;
}

.preview-content :deep(pre) {
  background: #1e1e1e;
  border-radius: 8px;
  padding: 16px;
  overflow-x: auto;
  margin: 12px 0;
}

.preview-content :deep(code) {
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 13px;
}

.preview-content :deep(pre code) {
  color: #d4d4d4;
}

.preview-content :deep(img) {
  max-width: 100%;
  border-radius: 8px;
  margin: 12px 0;
}

.preview-content :deep(a) {
  color: #3b82f6;
  text-decoration: none;
}

.preview-content :deep(a:hover) {
  text-decoration: underline;
}

.preview-content :deep(hr) {
  border: none;
  border-top: 2px solid #e2e8f0;
  margin: 20px 0;
}

.quick-guide {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
}

.quick-guide h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.guide-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 16px;
}

.guide-item {
  background: white;
  border-radius: 10px;
  padding: 14px;
  border: 1px solid #e2e8f0;
}

.guide-title {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 10px;
}

.guide-item code {
  display: block;
  font-family: 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  color: #64748b;
  background: #f8fafc;
  padding: 4px 8px;
  border-radius: 4px;
  margin: 4px 0;
}

.btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-secondary {
  background: white;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

@media (max-width: 1024px) {
  .editor-container {
    grid-template-columns: 1fr;
  }

  .guide-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .tool-header {
    flex-direction: column;
    gap: 16px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }

  .guide-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

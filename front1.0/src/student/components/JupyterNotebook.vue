<template>
  <div class="jupyter-notebook">
    <div class="notebook-header">
      <h2>{{ title || '交互式文档' }}</h2>
      <div class="header-actions">
        <button class="btn" @click="saveNotebook">💾 保存</button>
        <button class="btn btn-primary" @click="runAllCells">▶ 运行全部</button>
      </div>
    </div>
    
    <div class="notebook-content">
      <!-- 状态提示 -->
      <div v-if="isLoading" class="loading-indicator">加载中...</div>
      <div v-else-if="isSaving" class="saving-indicator">保存中...</div>
      <div v-else-if="saveSuccess" class="save-success-message">
        ✅ 保存成功！
      </div>
      
      <!-- 单元格列表 -->
      <div 
        v-for="(cell, index) in cells" 
        :key="cell.id"
        class="cell"
        :class="{ 
          'selected': selectedCellIndex === index, 
          'code-cell': cell.type === 'code',
          'system-cell': cell.isSystemGenerated,
          'user-cell': !cell.isSystemGenerated
        }"
        @click="handleCellClick(index, $event)"
      >
        <!-- 单元格工具栏 -->
        <div class="cell-toolbar">
          <div class="cell-info">
            <div class="cell-source-indicator" v-if="cell.isSystemGenerated">🔒 系统内容</div>
            <div class="cell-source-indicator user-source" v-else>✏️ 用户创建</div>
            <div class="cell-type-indicator">{{ getCellTypeIcon(cell.type) }}</div>
          </div>
          <div class="cell-actions">
            <button 
              v-if="cell.type === 'code'"
              class="action-btn"
              @click="runCell(index)"
              :disabled="cell.isRunning"
              title="运行单元格"
            >
              {{ cell.isRunning ? '⏳' : '▶' }}
            </button>
            <button class="action-btn" @click="addMarkdownCellBefore(index)" title="在此单元格前添加文本单元格">
              📄⬆️
            </button>
            <button class="action-btn" @click="addCodeCellBefore(index)" title="在此单元格前添加代码单元格">
              📝⬆️
            </button>
            <button class="action-btn" @click="addMarkdownCellAfter(index)" title="在此单元格后添加文本单元格">
              📄⬇️
            </button>
            <button class="action-btn" @click="addCodeCellAfter(index)" title="在此单元格后添加代码单元格">
              📝⬇️
            </button>
            <button class="action-btn" @click="addImageCellBefore(index)" title="在此单元格前添加图片单元格">
              🖼️⬆️
            </button>
            <button class="action-btn" @click="addImageCellAfter(index)" title="在此单元格后添加图片单元格">
              🖼️⬇️
            </button>
            <button class="action-btn" @click="toggleCellType(index)" title="切换单元格类型">
              {{ getToggleCellTypeIcon(cell.type) }}
            </button>
            <button class="action-btn" @click="deleteCell(index)" title="删除单元格">
              🗑️
            </button>
          </div>
        </div>
        
        <!-- 单元格内容 -->
        <div class="cell-content">
          <!-- Markdown单元格 -->
          <div v-if="cell.type === 'markdown'" class="markdown-cell">
            <div v-if="cell.isEditing" class="markdown-editor-container" style="position: relative;">
              <textarea 
                v-model="cell.content"
                class="markdown-input"
                placeholder="输入Markdown内容..."
                @blur="toggleCellEdit(index, false)"
                @select="handleTextSelection(index, $event)"
              ></textarea>

            </div>
            <div 
              v-else
              class="markdown-preview"
              v-html="renderMarkdown(cell.content)"
              @click="(event) => {
                try {
                  const selection = window.getSelection?.()
                  if (selection && selection.rangeCount > 0) {
                    const range = selection.getRangeAt(0)
                    const preCaretRange = range.cloneRange()
                    preCaretRange.selectNodeContents(event.currentTarget)
                    preCaretRange.setEnd(range.endContainer, range.endOffset)
                    const clickOffset = preCaretRange.toString().length
                    toggleCellEdit(index, true, clickOffset)
                  } else {
                    toggleCellEdit(index, true)
                  }
                } catch (error) {
                  console.error('处理点击事件时出错:', error)
                  // 即使出错也确保切换到编辑模式
                  toggleCellEdit(index, true)
                }
              }"
              @mouseup="handlePreviewTextSelection(index, $event)"
            ></div>
          </div>
          
          <!-- 代码单元格 -->
          <div v-else-if="cell.type === 'code'" class="code-cell">
            <div class="code-editor-container" style="position: relative;">
              <MonacoCard
                v-model="cell.content"
                :language="cell.language"
                :filename="`cell_${index}.${getFileExtension(cell.language)}`"
                :readOnly="false"
                :showFooter="false"
                @run="handleCellRun(index, $event)"
                @update:modelValue="updateCellContent(index, $event)"
                @ai-interact="handleCodeSelection(index, $event)"
                @completion-request="handleCompletionRequest(index, $event)"
              />

            </div>
            
            <!-- 代码输出 -->
            <div v-if="cell.output && cell.output.length > 0" class="cell-output">
              <div class="output-header">输出</div>
              <div class="output-content">
                <div v-for="(outputLine, lineIndex) in cell.output" :key="lineIndex" class="output-line">
                  <span :class="getOutputClass(outputLine)">{{ outputLine }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 图片单元格内容 -->
          <div v-else-if="cell.type === 'image'" class="image-cell">
            <img 
              v-if="cell.imageUrl" 
              :src="cell.imageUrl" 
              :alt="cell.altText || '图片'" 
              :style="{ width: cell.width ? `${cell.width}px` : 'auto', height: cell.height ? `${cell.height}px` : 'auto' }"
              class="cell-image"
              @click="toggleCellEdit(index, true)"
            />
            <div v-if="cell.imageUrl && cell.isEditing" class="image-edit-controls">
              <input 
                type="text" 
                v-model="cell.altText" 
                placeholder="图片描述（可选）"
                class="alt-text-input"
              />
              <div class="image-size-controls">
                <label>宽度:</label>
                <input 
                  type="number" 
                  v-model.number="cell.width" 
                  placeholder="像素值"
                  class="size-input"
                  min="1"
                />
                <label>高度:</label>
                <input 
                  type="number" 
                  v-model.number="cell.height" 
                  placeholder="像素值"
                  class="size-input"
                  min="1"
                />
                <button class="btn btn-small" @click="resetImageSize(index)">重置</button>
              </div>
              <button class="btn btn-primary" @click="toggleCellEdit(index, false)">保存</button>
              <button class="btn" @click="triggerImageReupload(index)">更换图片</button>
            </div>
            <div v-if="cell.error" class="image-error">{{ cell.error }}</div>
          </div>
        </div>
      </div>
      
      <!-- 添加新单元格按钮组 -->
      <div class="add-cell-buttons">
        <button class="add-cell-btn markdown-btn" @click="addMarkdownCellAtEnd">📄 添加文本单元格</button>
        <button class="add-cell-btn code-btn" @click="addCodeCellAtEnd">📝 添加代码单元格</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import MonacoCard from './MonacoCard.vue'
import { api } from '../api/api.js'
import * as monaco from 'monaco-editor'

export default {
  name: 'JupyterNotebook',
  components: {
    MonacoCard
  },
  props: {
    title: {
      type: String,
      default: '交互式文档'
    },
    initialContent: {
      type: String,
      default: ''
    },
    documentId: {
      type: [String, null],
      default: null
    },
    isPublic: {
      type: Boolean,
      default: false
    },
    bookId: {
      type: [String, null],
      default: null
    },
    chapterId: {
      type: [String, null],
      default: null
    }
  },
  emits: ['update:title', 'contentChange', 'save', 'update:documentId', 'update:isPublic', 'text-selected'],
  setup(props, { emit }) {
    // 单元格状态管理
    const cells = ref([])
    const selectedCellIndex = ref(-1)
    const imageFileInput = ref(null)
    const imageUploadTargetIndex = ref(0)
    const imageReuploadIndex = ref(-1)
    // 文本选中状态管理
    const textSelectionState = ref({})
    // 代码选中状态管理
    const codeSelectionState = ref({})
    // 加载状态
    const isLoading = ref(false)
    // 保存状态
    const isSaving = ref(false)
    // 单元格类型枚举
    const CellType = {
      MARKDOWN: 'markdown',
      CODE: 'code'
    }
    // 监听公开状态变化
    watch(
      () => props.isPublic,
      (newValue) => {
        // 可以在这里处理公开状态变化的逻辑
        console.log('公开状态已更新:', newValue)
      }
    )
    
    // 初始化默认单元格
    const initializeDefaultCells = () => {
      cells.value = [
        {
          id: Date.now().toString(),
          type: 'markdown',
          content: '# 交互式文档\n\n欢迎使用Jupyter风格的交互式文档系统。您可以在此创建包含Markdown文本和可执行代码块的文档。',
          isEditing: false,
          isSystemGenerated: false
        },
        {
          id: (Date.now() + 1).toString(),
          type: 'code',
          language: 'python',
          content: 'print("Hello, World!")',
          output: [],
          isRunning: false,
          isSystemGenerated: false
        }
      ]
    }
    
    // 加载文档数据
    const loadDocument = async () => {
      try {
        // 日志记录当前加载方式
        console.log('🔄 加载文档:', {
          documentId: props.documentId,
          hasInitialContent: !!props.initialContent,
          bookId: props.bookId,
          chapterId: props.chapterId
        });
        
        if (!props.documentId) {
          // 新建文档或使用初始内容
          if (props.initialContent) {
            console.log('📝 使用initialContent加载文档');
            let processedContent = props.initialContent;
            
            // 尝试解析JSON内容的辅助函数
            const attemptToFixJSON = (jsonString) => {
              try {
                // 移除前后空白
                let fixed = jsonString.trim();
                
                // 修复数组末尾多余的逗号
                fixed = fixed.replace(/,\s*([}\]])/g, '$1');
                
                // 增强缺失逗号检测和修复
                // 对象间缺少逗号
                fixed = fixed.replace(/}\s*{/g, '}, {');
                // 数组元素间缺少逗号
                fixed = fixed.replace(/}\s*\[/g, '}, [');
                fixed = fixed.replace(/\]\s*{/g, '], {');
                // 属性间缺少逗号
                fixed = fixed.replace(/"\s*:\s*[^,}\]]+\s*"/g, (match) => {
                  if (!match.includes(',')) {
                    return match.replace(/"$/g, '",');
                  }
                  return match;
                });
                
                // 智能修复未转义的引号（在字符串内容中的引号）
                fixed = fixed.replace(/("[^"\\]*(?:\\.[^"\\]*)*)"([^:,\]}\s])/g, '$1\\"$2');
                
                // 计算括号平衡并添加缺失的闭合括号
                let openBraces = 0, openBrackets = 0;
                for (let i = 0; i < fixed.length; i++) {
                  if (fixed[i] === '{') openBraces++;
                  else if (fixed[i] === '}') openBraces--;
                  else if (fixed[i] === '[') openBrackets++;
                  else if (fixed[i] === ']') openBrackets--;
                }
                
                while (openBraces > 0) {
                  fixed += '}';
                  openBraces--;
                }
                while (openBrackets > 0) {
                  fixed += ']';
                  openBrackets--;
                }
                
                // 修复冒号后缺少值的情况
                fixed = fixed.replace(/"\s*:\s*(?=[,}\]])/g, '": ""');
                
                // 移除可能的首尾引号（如果整个内容被额外的引号包围）
                if (fixed.startsWith('"') && fixed.endsWith('"')) {
                  fixed = fixed.substring(1, fixed.length - 1);
                }
                
                console.log('🔧 JSON修复后内容:', fixed.substring(0, 100) + (fixed.length > 100 ? '...' : ''));
                return fixed;
              } catch (e) {
                console.error('❌ JSON修复失败:', e);
                return jsonString;
              }
            };
            
            try {
              // 尝试解析为JSON格式的单元格数据
              console.log('🔍 尝试解析JSON格式内容');
              const parsedContent = JSON.parse(processedContent);
              
              // 解析成功后的处理逻辑...
              if (Array.isArray(parsedContent)) {
                // 直接的单元格数组格式
                console.log('✅ 内容是单元格数组，包含', parsedContent.length, '个单元格');
                cells.value = parsedContent.map(cell => ({
                  id: cell.id || Date.now() + Math.random().toString(),
                  type: cell.type || 'markdown',
                  content: cell.content || '',
                  language: cell.language || 'python',
                  output: cell.output || [],
                  isRunning: cell.isRunning || false,
                  isEditing: cell.isEditing || false,
                  isSystemGenerated: cell.isSystemGenerated ?? false
                }))
              } else if (typeof parsedContent === 'object' && parsedContent !== null) {
                // 检查是否是Jupyter Notebook格式（包含cells数组）
                if (parsedContent.cells && Array.isArray(parsedContent.cells)) {
                  console.log('✅ 检测到Jupyter格式，转换为单元格数组');
                  cells.value = parsedContent.cells.map((cell, index) => ({
                    id: `cell_${index}_${Date.now()}`,
                    type: cell.cell_type === 'code' ? 'code' : 'markdown',
                    content: Array.isArray(cell.source) ? cell.source.join('\n') : cell.source || '',
                    language: parsedContent.metadata?.kernelspec?.language || 'python',
                    output: cell.outputs?.map(output => {
                      if (output.text) return Array.isArray(output.text) ? output.text.join('') : output.text;
                      if (output.data?.['text/plain']) return output.data['text/plain'];
                      return JSON.stringify(output);
                    }) || [],
                    isRunning: false,
                    isEditing: false,
                    isSystemGenerated: true
                  }))
                } else {
                  // 如果是单个单元格对象
                  if (parsedContent.cell_type && parsedContent.source) {
                    console.log('✅ 检测到单个单元格，转换为单元素数组');
                    cells.value = [{
                      id: Date.now().toString(),
                      type: parsedContent.cell_type === 'code' ? 'code' : 'markdown',
                      content: Array.isArray(parsedContent.source) ? parsedContent.source.join('\n') : parsedContent.source || '',
                      language: 'python',
                      output: parsedContent.outputs?.map(output => {
                        if (output.text) return Array.isArray(output.text) ? output.text.join('') : output.text;
                        if (output.data?.['text/plain']) return output.data['text/plain'];
                        return JSON.stringify(output);
                      }) || [],
                      isRunning: false,
                      isEditing: false,
                      isSystemGenerated: true
                    }]
                  } else {
                    // 其他对象格式，作为Markdown处理
                    console.log('ℹ️ 内容是对象但不是Jupyter格式，作为Markdown处理');
                    cells.value = parseMarkdownToCells(props.initialContent)
                  }
                }
              } else {
                // 非数组非对象，作为Markdown处理
                console.log('ℹ️ 内容不是预期格式，作为Markdown处理');
                cells.value = parseMarkdownToCells(props.initialContent)
                console.log('✅ 从Markdown解析出', cells.value.length, '个单元格');
              }
            } catch (e) {
              // 首次解析失败，尝试修复JSON格式
              console.log('⚠️ 首次解析失败，尝试修复JSON:', e.message);
              try {
                // 应用修复策略
                const fixedContent = attemptToFixJSON(processedContent);
                console.log('🔄 已应用JSON修复策略');
                
                // 尝试二次解析
                const parsedContent = JSON.parse(fixedContent);
                
                // 处理修复后的解析结果
                if (Array.isArray(parsedContent)) {
                  console.log('✅ 修复后内容是单元格数组，包含', parsedContent.length, '个单元格');
                  cells.value = parsedContent.map(cell => ({
                    id: cell.id || Date.now() + Math.random().toString(),
                    type: cell.type || 'markdown',
                    content: cell.content || '',
                    language: cell.language || 'python',
                    output: cell.output || [],
                    isRunning: cell.isRunning || false,
                    isEditing: cell.isEditing || false,
                    isSystemGenerated: cell.isSystemGenerated ?? false
                  }))
                } else if (typeof parsedContent === 'object' && parsedContent !== null) {
                  if (parsedContent.cells && Array.isArray(parsedContent.cells)) {
                    console.log('✅ 修复后检测到Jupyter格式，转换为单元格数组');
                    cells.value = parsedContent.cells.map((cell, index) => ({
                      id: `cell_${index}_${Date.now()}`,
                      type: cell.cell_type === 'code' ? 'code' : 'markdown',
                      content: Array.isArray(cell.source) ? cell.source.join('\n') : cell.source || '',
                      language: parsedContent.metadata?.kernelspec?.language || 'python',
                      output: cell.outputs?.map(output => {
                        if (output.text) return Array.isArray(output.text) ? output.text.join('') : output.text;
                        if (output.data?.['text/plain']) return output.data['text/plain'];
                        return JSON.stringify(output);
                      }) || [],
                      isRunning: false,
                      isEditing: false,
                      isSystemGenerated: true
                    }))
                  } else {
                    console.log('ℹ️ 修复后内容是对象但不是Jupyter格式，作为Markdown处理');
                    cells.value = parseMarkdownToCells(props.initialContent)
                  }
                } else {
                  console.log('ℹ️ 修复后内容不是预期格式，作为Markdown处理');
                  cells.value = parseMarkdownToCells(props.initialContent)
                }
              } catch (secondaryError) {
                console.log('📄 修复后仍无法解析JSON，作为Markdown处理', secondaryError);
                cells.value = parseMarkdownToCells(props.initialContent)
                console.log('✅ 从Markdown解析出', cells.value.length, '个单元格');
              }
            }
          } else {
            console.log('📋 没有内容，初始化默认单元格');
            initializeDefaultCells()
          }
        } else {
          try {
            isLoading.value = true
            console.log('📥 从服务器加载文档，ID:', props.documentId);
            const documentData = await api.getJupyterDocument(props.documentId)
            console.log('📤 服务器返回文档数据:', {
              hasTitle: !!documentData.title,
              hasContent: !!documentData.content,
              isPublic: documentData.is_public
            });
            
            // 更新标题
            if (documentData.title && props.title !== documentData.title) {
              emit('update:title', documentData.title)
            }
            
            // 更新公开状态
            if ('is_public' in documentData && props.isPublic !== documentData.is_public) {
              emit('update:isPublic', documentData.is_public)
            }
            
            // 解析内容
            try {
              // 尝试解析为JSON格式的单元格数据
              const parsedContent = JSON.parse(documentData.content)
              if (Array.isArray(parsedContent)) {
                console.log('✅ 成功解析JSON内容，包含', parsedContent.length, '个单元格');
                cells.value = parsedContent.map(cell => ({
                  id: cell.id || Date.now() + Math.random().toString(),
                  type: cell.type || 'markdown',
                  content: cell.content || '',
                  language: cell.language || 'python',
                  output: cell.output || [],
                  isRunning: cell.isRunning || false,
                  isEditing: cell.isEditing || false,
                  isSystemGenerated: true // 从数据库加载的内容标记为系统生成
                }))
              } else {
                console.log('ℹ️ 内容不是JSON数组，使用Markdown解析器');
                // 如果不是数组，使用Markdown解析器
                cells.value = parseMarkdownToCells(documentData.content || '')
                console.log('✅ 从Markdown解析出', cells.value.length, '个单元格');
              }
            } catch (e) {
              console.log('📄 无法解析为JSON，使用Markdown解析器', e)
              // 如果解析失败，使用Markdown解析器
              cells.value = parseMarkdownToCells(documentData.content || '')
              console.log('✅ 从Markdown解析出', cells.value.length, '个单元格');
            }
            
          } catch (error) {
            console.error('❌ 加载文档失败:', error)
            // 加载失败时显示默认内容
            if (props.initialContent) {
              console.log('💡 加载失败，使用初始内容');
              cells.value = parseMarkdownToCells(props.initialContent)
            } else {
              console.log('💡 加载失败，初始化默认单元格');
              initializeDefaultCells()
            }
            alert('加载文档失败，请重试')
          } finally {
            isLoading.value = false
          }
        }
        
        // 确保所有系统生成的单元格都有正确的标记
        if (cells.value) {
          cells.value = cells.value.map(cell => ({
            ...cell,
            isSystemGenerated: cell.isSystemGenerated ?? true
          }));
        }
        
        // 确保至少有一个单元格
        if (!cells.value || cells.value.length === 0) {
          console.log('📋 没有加载到内容，初始化默认单元格');
          initializeDefaultCells();
        }
        
        // 通知内容变化
        emitContentChange();
        console.log('🎉 文档加载完成');
        
      } catch (error) {
        console.error('❌ 加载文档处理过程中出错:', error);
        initializeDefaultCells();
        emitContentChange();
        }
      }
    
    // 计算文件扩展名
    const getFileExtension = (language) => {
      const extensionMap = {
        'javascript': 'js',
        'python': 'py',
        'java': 'java',
        'cpp': 'cpp',
        'csharp': 'cs',
        'html': 'html',
        'css': 'css',
        'markdown': 'md'
      }
      return extensionMap[language] || 'txt'
    }
    
    // 简单的Markdown渲染
    const renderMarkdown = (text) => {
      if (!text) return ''
      
      return text
        // 代码块
        .replace(/```([\s\S]*?)```/g, (match, code) => {
          const [lang, content] = code.split('\n', 2)
          return `<pre><code class="language-${lang}">${content || lang}</code></pre>`
        })
        // 图片 - 支持所有格式：简单格式和完整格式
        .replace(/!\[(.*?)\]\((.*?)\)|.*?图片\s+(image_\d+)(?:_([\w]+))?.*?/g, (match, altText, imagePath, imageName, imageId) => {
          // 如果没有匹配到imageName，尝试从altText或imagePath中提取
          if (!imageName) {
            // 从altText中提取
            const altNameMatch = (altText || '').match(/(image_\d+)(?:_([\w]+))?/);
            // 从imagePath中提取
            const pathNameMatch = (imagePath || '').match(/(image_\d+)(?:_([\w]+))?/);
            
            if (altNameMatch) {
              imageName = altNameMatch[1];
              imageId = altNameMatch[2] || '';
            } else if (pathNameMatch) {
              imageName = pathNameMatch[1];
              imageId = pathNameMatch[2] || '';
            } else {
              // 仅提取imageName
              const simpleMatch = (altText || '').match(/image_(\d+)/) || 
                               (imagePath || '').match(/image_(\d+)/);
              if (simpleMatch) {
                imageName = `image_${simpleMatch[1]}`;
                imageId = '';
              } else {
                return match; // 如果都没有匹配到，返回原内容
              }
            }
          }
          
          // 构造图片URL
          let imageUrl;
          if (imageId) {
            // 包含ID的完整格式
            imageUrl = `http://127.0.0.1:8000/media/book_images/${props.bookId || 0}/${imageName}_${imageId}.png`;
          } else {
            // 不包含ID的简单格式
            imageUrl = `http://127.0.0.1:8000/media/book_images/${props.bookId || 0}/${imageName}.png`;
          }
          
          return `<img src="${imageUrl}" alt="图片 ${imageName}" class="markdown-image">`;
        })
        // 标题
        .replace(/#{6}\s+(.*?)$/gm, '<h6>$1</h6>')
        .replace(/#{5}\s+(.*?)$/gm, '<h5>$1</h5>')
        .replace(/#{4}\s+(.*?)$/gm, '<h4>$1</h4>')
        .replace(/#{3}\s+(.*?)$/gm, '<h3>$1</h3>')
        .replace(/#{2}\s+(.*?)$/gm, '<h2>$1</h2>')
        .replace(/#{1}\s+(.*?)$/gm, '<h1>$1</h1>')
        // 粗体和斜体
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        // 行内代码
        .replace(/`(.*?)`/g, '<code>$1</code>')
        // 链接
        .replace(/\[(.*?)\]\((.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>')
        // 无序列表
        .replace(/(^-\s+(.*?)$\s*)+/gm, (match) => {
          const listItems = match.replace(/^-\s+(.*?)$/gm, '<li>$1</li>')
          return `<ul>${listItems}</ul>`
        })
        // 有序列表
        .replace(/(^\d+\.\s+(.*?)$\s*)+/gm, (match) => {
          const listItems = match.replace(/^\d+\.\s+(.*?)$/gm, '<li>$1</li>')
          return `<ol>${listItems}</ol>`
        })
        // 段落
        .replace(/^(?!<[hlu])(.*?)$/gm, (match, p1) => {
          return p1.trim() ? `<p>${p1}</p>` : ''
        })
    }
    
    // 从Markdown解析单元格
    const parseMarkdownToCells = (markdown) => {
      // 如果内容为空，返回默认单元格
      if (!markdown || markdown.trim() === '') {
        return [{
          id: Date.now().toString(),
          type: 'markdown',
          content: '# 欢迎使用Jupyter笔记本\n\n在此开始您的学习之旅！',
          output: null,
          isSystemGenerated: true,
          isEditing: false
        }];
      }

      try {
        // 尝试将markdown内容解析为JSON，如果成功则直接返回
        const jsonData = JSON.parse(markdown);
        if (Array.isArray(jsonData)) {
          return jsonData.map(cell => ({
            ...cell,
            isSystemGenerated: true
          }));
        }
      } catch (e) {
        // 不是JSON格式，继续按Markdown解析
      }

      const cells = [];
      const lines = markdown.split('\n');
      let cellId = Date.now();
      
      let currentContent = '';
      let inCodeBlock = false;
      let inTableCodeBlock = false;
      let codeLanguage = '';
      
      for (let i = 0; i < lines.length; i++) {
        // 不trim()，保持原始行内容以便匹配图片标记
        const line = lines[i];
        const trimmedLine = line.trim();
        
        // 检测特殊表格代码块开始（| #例开头）
        const tableCodeStartMatch = line.match(/^\|\s*#例/);
        if (tableCodeStartMatch && !inCodeBlock && !inTableCodeBlock) {
          // 表格代码块开始
          inTableCodeBlock = true;
          
          // 保存前面的Markdown内容
          if (currentContent.trim() !== '') {
            cells.push({
              id: (cellId++).toString(),
              type: 'markdown',
              content: currentContent.trim(),
              output: [],
              isSystemGenerated: true,
              isEditing: false
            });
            currentContent = '';
          }
          
          // 提取代码内容，去掉前后的|符号
          let codeLine = line.replace(/^\|\s*/, '').replace(/\s*\|\s*$/, '');
          currentContent = codeLine;
          continue;
        }
        
        // 检测特殊表格代码块结束（| --- |）
        if (trimmedLine === '| --- |' && inTableCodeBlock) {
          // 表格代码块结束
          inTableCodeBlock = false;
          
          // 保存代码内容为code单元格
          if (currentContent.trim() !== '') {
            cells.push({
              id: (cellId++).toString(),
              type: 'code',
              content: currentContent.trim(),
              language: 'python',
              output: [],
              isRunning: false,
              isSystemGenerated: true
            });
            currentContent = '';
          }
          continue;
        }
        
        // 收集表格代码块内容
        if (inTableCodeBlock) {
          // 提取代码内容，去掉前后的|符号
          let codeLine = line.replace(/^\|\s*/, '').replace(/\s*\|\s*$/, '');
          currentContent += (currentContent ? '\n' : '') + codeLine;
          continue;
        }
        
        // 检测标准代码块开始（```后面可能有语言标识）
        const codeBlockStartMatch = trimmedLine.match(/^```(\w*)/);
        if (codeBlockStartMatch && !inCodeBlock) {
          // 代码块开始
          inCodeBlock = true;
          codeLanguage = codeBlockStartMatch[1] || '';
          
          // 保存前面的Markdown内容
          if (currentContent.trim() !== '') {
            cells.push({
              id: (cellId++).toString(),
              type: 'markdown',
              content: currentContent.trim(),
              output: [],
              isSystemGenerated: true,
              isEditing: false
            });
            currentContent = '';
          }
          continue;
        }
        
        // 检测代码块结束
        if (trimmedLine === '```' && inCodeBlock) {
          // 代码块结束
          inCodeBlock = false;
          
          // 保存代码内容为code单元格
          if (currentContent.trim() !== '') {
            cells.push({
              id: (cellId++).toString(),
              type: 'code',
              content: currentContent.trim(),
              language: codeLanguage || 'python',
              output: [],
              isRunning: false,
              isSystemGenerated: true
            });
            currentContent = '';
          }
          continue;
        }
        
        // 收集代码块内容
        if (inCodeBlock) {
          currentContent += (currentContent ? '\n' : '') + line;
        }
        // 收集Markdown内容
        else {
          // 检查是否是图片标记（简单匹配）
          const isImageLine = line.includes('图片 image_') || line.includes('!图片');
          
          if (isImageLine) {
            // 保存当前的普通内容（如果有）
            if (currentContent.trim() !== '') {
              cells.push({
                id: (cellId++).toString(),
                type: 'markdown',
                content: currentContent.trim(),
                output: [],
                isSystemGenerated: true,
                isEditing: false
              });
              currentContent = '';
            }
            
            // 从行中提取图片的核心ID部分
            const imageIdMatch = line.match(/image_(\d+_[0-9a-f]+)/i);
            const imageId = imageIdMatch ? imageIdMatch[1] : '0_0';
            
            // 构造图片URL，支持两种格式：
            // 1. 不包含UUID前缀的格式（前端生成的）
            // 2. 包含UUID前缀的格式（后端实际存储的）
            const imageUrl = `http://127.0.0.1:8000/media/book_images/${props.bookId || 0}/image_${imageId}.png`;
            
            // 设置图片替代文本
            const altText = `图片 image_${imageId}`;
            
            // 创建图片单元格
            cells.push({
              id: (cellId++).toString(),
              type: 'image',
              imageUrl: imageUrl,
              altText: altText,
              width: null,
              height: null,
              isLoading: false,
              error: null,
              isSystemGenerated: true,
              isEditing: false
            });
          } else if (line === '' && currentContent.trim() !== '') {
            // 如果遇到空行且当前内容不为空，创建一个新的Markdown单元格
            cells.push({
              id: (cellId++).toString(),
              type: 'markdown',
              content: currentContent.trim(),
              output: [],
              isSystemGenerated: true,
              isEditing: false
            });
            currentContent = '';
          } else if (line !== '') {
            // 普通Markdown内容
            currentContent += (currentContent ? '\n' : '') + lines[i];
          }
        }
      }
      
      // 处理未关闭的代码块或最后剩余的内容
      if (currentContent.trim() !== '') {
        cells.push({
          id: (cellId++).toString(),
          type: inCodeBlock ? 'code' : 'markdown',
          content: currentContent.trim(),
          language: inCodeBlock ? codeLanguage || 'python' : undefined,
          output: [],
          isRunning: inCodeBlock ? false : undefined,
          isSystemGenerated: true,
          isEditing: false
        });
      }
      
      // 如果没有生成任何单元格，创建一个默认的markdown单元格
      if (cells.length === 0) {
        cells.push({
          id: (cellId++).toString(),
          type: 'markdown',
          content: markdown.trim(),
          output: [],
          isSystemGenerated: true,
          isEditing: false
        });
      }
      
      return cells;
    }
    
    // 将单元格转换为Markdown
    const convertCellsToMarkdown = () => {
      return cells.value.map(cell => {
        if (cell.type === 'markdown') {
          return cell.content
        } else if (cell.type === 'code') {
          return `\n\`\`\`${cell.language}\n${cell.content}\n\`\`\`\n`
        } else if (cell.type === 'image' && cell.imageUrl) {
          return `\n![${cell.altText || '图片'}](${cell.imageUrl})\n`
        }
        return ''
      }).join('\n\n')
    }
    
    // 添加文本单元格
    const addTextCell = (index) => {
      const newCell = {
        id: Date.now().toString(),
        type: 'markdown',
        content: '',
        isEditing: true,
        isSystemGenerated: false // 用户添加的单元格标记为非系统生成
      }
      
      cells.value.splice(index, 0, newCell)
      selectedCellIndex.value = index
    }
    
    // 添加代码单元格
    const addCodeCell = (index, content = '') => {
      const newCell = {
        id: Date.now().toString(),
        type: 'code',
        content: content || '',
        language: 'python',
        output: [],
        isRunning: false,
        isEditing: false,
        isSystemGenerated: false // 用户添加的单元格标记为非系统生成
      }
      
      cells.value.splice(index, 0, newCell)
      selectedCellIndex.value = index
    }
    
    // 添加图片单元格
    const addImageCell = (index, imageUrl = '', altText = '') => {
      const newCell = {
        id: Date.now().toString(),
        type: 'image',
        imageUrl: imageUrl,
        altText: altText || '',
        width: null,
        height: null,
        isLoading: false,
        error: null,
        isEditing: false,
        isSystemGenerated: false
      }
      
      cells.value.splice(index, 0, newCell)
      selectedCellIndex.value = index
    }
    
    // 添加Markdown单元格
    const addMarkdownCell = (index, content = '') => {
      const newCell = {
        id: Date.now().toString(),
        type: 'markdown',
        content: content || '',
        output: [],
        isSystemGenerated: false,
        isEditing: false
      }
      
      cells.value.splice(index, 0, newCell)
      selectedCellIndex.value = index
    }
    // 在指定位置前添加Markdown单元格
    const addMarkdownCellBefore = (index) => {
      addMarkdownCell(index)
    }
    
    // 在指定位置前添加代码单元格
    const addCodeCellBefore = (index) => {
      addCodeCell(index)
    }
    
    // 在指定位置后添加Markdown单元格
    const addMarkdownCellAfter = (index) => {
      addMarkdownCell(index + 1)
    }
    
    // 在指定位置后添加代码单元格
    const addCodeCellAfter = (index) => {
      addCodeCell(index + 1)
    }
    
    // 在指定位置前添加图片单元格
    const addImageCellBefore = (index) => {
      triggerImageUpload(index)
    }
    
    // 在指定位置后添加图片单元格
    const addImageCellAfter = (index) => {
      triggerImageUpload(index + 1)
    }
    
    // 触发图片上传
    const triggerImageUpload = (targetIndex) => {
      // 确保使用正确的目标索引，默认添加到末尾
      imageUploadTargetIndex.value = targetIndex !== undefined ? targetIndex : cells.value.length
      // 确保文件输入元素存在
      if (!imageFileInput.value) {
        const input = document.createElement('input')
        input.type = 'file'
        input.accept = 'image/*'
        input.style.display = 'none'
        input.onchange = (e) => handleImageUpload(e)
        document.body.appendChild(input)
        imageFileInput.value = input
      }
      // 重置重新上传索引，确保是新图片上传
      imageReuploadIndex.value = -1
      imageFileInput.value.click()
    }
    
    // 重置图片尺寸
    const resetImageSize = (index) => {
      const cell = cells.value[index]
      if (cell && cell.type === 'image') {
        cell.width = null
        cell.height = null
      }
    }
    
    // 触发图片重新上传
    const triggerImageReupload = (index) => {
      imageReuploadIndex.value = index
      // 确保文件输入元素存在
      if (!imageFileInput.value) {
        const input = document.createElement('input')
        input.type = 'file'
        input.accept = 'image/*'
        input.style.display = 'none'
        input.onchange = (e) => handleImageUpload(e)
        document.body.appendChild(input)
        imageFileInput.value = input
      }
      imageFileInput.value.click()
    }
    
    // 处理图片上传
    const handleImageUpload = async (event) => {
      const file = event.target.files[0]
      if (!file) return
      
      // 清除input的值，以便下次可以选择相同的文件
      event.target.value = ''
      
      try {
        // 检查是否是重新上传
          if (imageReuploadIndex.value !== -1) {
            const cell = cells.value[imageReuploadIndex.value]
            cell.error = null
            
            const response = await api.uploadImage(file)
            
            if (response.image_url) {
              cell.imageUrl = response.image_url
            } else {
            throw new Error('上传失败：未返回图片URL')
          }
          
          imageReuploadIndex.value = -1
        } else {
          // 创建新的图片单元格
          const newCell = {
            id: Date.now().toString(),
            type: 'image',
            imageUrl: '',
            altText: '',
            width: null,
            height: null,
            error: null,
            isEditing: false,
            isSystemGenerated: false
          }
          
          cells.value.splice(imageUploadTargetIndex.value, 0, newCell)
          selectedCellIndex.value = imageUploadTargetIndex.value
          
          // 上传图片
          const response = await api.uploadImage(file)
          
          if (response.image_url) {
            // 先更新imageUrl并设置为编辑模式
            newCell.imageUrl = response.image_url
            newCell.isEditing = true  // 立即设置为编辑模式，确保编辑控件显示
            
            // 强制刷新整个cells数组的引用，确保Vue重新渲染所有单元格
            cells.value = [...cells.value]
            
            // 强制Vue更新视图
            nextTick(() => {
              // 再次触发内容变更，确保所有图片都能正确显示和保存
              emitContentChange()
            })
          } else {
            throw new Error('上传失败：未返回图片URL')
          }
        }
        
        emitContentChange()
      } catch (error) {
        console.error('图片上传失败:', error)
        
        if (imageReuploadIndex.value !== -1) {
            const cell = cells.value[imageReuploadIndex.value]
            cell.error = error.message || '图片上传失败'
            imageReuploadIndex.value = -1
          } else {
            // 如果是新单元格，移除它
            cells.value.splice(imageUploadTargetIndex.value, 1)
          }
      }
    }
    
    // 获取单元格类型图标
    const getCellTypeIcon = (type) => {
      switch (type) {
        case 'code': return '📝'
        case 'markdown': return '📄'
        case 'image': return '🖼️'
        default: return '📄'
      }
    }
    
    // 获取切换单元格类型图标
    const getToggleCellTypeIcon = (type) => {
      switch (type) {
        case 'code': return '📄'
        case 'markdown': return '📝'
        case 'image': return '📄'
        default: return '📝'
      }
    }
    
    // 在末尾添加Markdown单元格
    const addMarkdownCellAtEnd = () => {
      addMarkdownCell(cells.value.length)
    }
    
    // 在末尾添加代码单元格
    const addCodeCellAtEnd = () => {
      addCodeCell(cells.value.length)
    }
    
    // 删除单元格
    const deleteCell = (index) => {
      if (cells.value.length > 1) {
        cells.value.splice(index, 1)
        selectedCellIndex.value = Math.min(index, cells.value.length - 1)
      }
    }
    
    // 切换单元格类型
    const toggleCellType = (index) => {
      const cell = cells.value[index]
      
      if (cell.type === 'code') {
        // 代码单元格 -> Markdown单元格
        cell.type = 'markdown'
        delete cell.language
        delete cell.output
        delete cell.isRunning
      } else if (cell.type === 'markdown') {
        // Markdown单元格 -> 代码单元格
        cell.type = 'code'
        cell.language = 'python'
        cell.output = []
        cell.isRunning = false
      } else if (cell.type === 'image') {
        // 图片单元格 -> Markdown单元格（保留图片链接）
        cell.type = 'markdown'
        if (cell.imageUrl) {
          cell.content = `![${cell.altText || '图片'}](${cell.imageUrl})`
        } else {
          cell.content = ''
        }
        delete cell.imageUrl
        delete cell.altText
        delete cell.isLoading
        delete cell.error
      }
      
      emitContentChange()
    }
    
    // 切换Markdown单元格编辑状态
    const handleCellClick = (index, event) => {
  // 避免在编辑模式下触发选中，或者在点击工具栏按钮时触发
  if (!event.target.closest('.cell-toolbar') && !event.target.closest('.action-btn')) {
    selectedCellIndex.value = index
  }
}

// 存储点击位置的对象
const clickPositions = ref({})

const toggleCellEdit = (index, isEditing, clickOffset = null) => {
      const cell = cells.value[index]
      if (cell.type === 'markdown') {
        cell.isEditing = isEditing
        if (isEditing) {
          selectedCellIndex.value = index
          // 存储点击位置，以便在进入编辑模式时恢复
          if (clickOffset !== null) {
            clickPositions.value[index] = clickOffset
          }
          setTimeout(() => {
            // 使用更精确的选择器，直接定位到特定索引的单元格内的textarea
            const textarea = document.querySelector(`.cell:nth-child(${index + 1}) .markdown-input`)
            if (textarea) {
              textarea.focus()
              // 如果有存储的点击位置，尝试恢复光标位置
              if (clickPositions.value[index] !== undefined) {
                try {
                  // 尝试设置光标位置到点击位置
                  const position = Math.min(clickPositions.value[index], textarea.value.length)
                  textarea.setSelectionRange(position, position)
                  // 清除存储的位置
                  delete clickPositions.value[index]
                } catch (e) {
                  console.log('无法设置光标位置:', e)
                }
              }
            }
          }, 0)
        }
      }
    }
    
    // 更新单元格内容
    const updateCellContent = (index, content) => {
      cells.value[index].content = content
      emitContentChange()
    }
    
    // 运行单个单元格
    const runCell = async (index) => {
      const cell = cells.value[index]
      if (cell.type !== 'code' || cell.isRunning) return
      
      try {
        cell.isRunning = true
        cell.output = []
        
        // 调用后端API执行代码
        const result = await api.executeCode({
          language: cell.language,
          code: cell.content
        })
        
        // 处理输出
        if (result.stdout) {
          cell.output = cell.output.concat(result.stdout.split('\n'))
        }
        
        // 处理错误信息
        if (result.error) {
          cell.output.push(`错误: ${result.error.message}`)
          if (result.error.details) {
            cell.output = cell.output.concat(result.error.details.split('\n'))
          }
        } else if (result.stderr) {
          cell.output = cell.output.concat(result.stderr.split('\n'))
        }
        
        // 添加执行信息
        cell.output.push(`[执行时间: ${result.durationMs}ms]`)
        
      } catch (error) {
        console.error('代码执行错误:', error)
        cell.output = ['执行错误:', error.message]
        // 如果有错误详细信息，也显示出来
        if (error.response?.data?.error?.details) {
          cell.output.push(error.response.data.error.details)
        }
      } finally {
        cell.isRunning = false
      }
    }
    
    // 运行所有单元格
    const runAllCells = async () => {
      for (let i = 0; i < cells.value.length; i++) {
        if (cells.value[i].type === 'code') {
          await runCell(i)
        }
      }
    }
    
    // 处理AI助手交互
    const handleAIInteract = async (cellIndex, interactData) => {
      try {
        const { code, language, context } = interactData

        // 显示加载状态
        const cell = cells.value[cellIndex]
        cell.isRunning = true

        // 构建问题文本
        const question = `请解释这段${language}代码：\n\`\`\`${language}\n${code}\n\`\`\``

        // 调用AI助手API
        const response = await api.getAIAssistantResponse(question)

        // 在当前单元格下方添加AI回答的Markdown单元格
        const aiAnswerCell = {
          id: Date.now().toString() + '_ai_answer',
          type: 'markdown',
          content: `## AI 助手回答\n\n${response.content}\n\n> **提示：** 这是基于你选中代码的AI解释，可以帮助你理解代码逻辑。`,
          output: [],
          isSystemGenerated: true,
          isEditing: false
        }

        // 插入AI回答单元格
        cells.value.splice(cellIndex + 1, 0, aiAnswerCell)

        // 通知内容变化
        emitContentChange()
      } catch (error) {
        console.error('AI助手交互失败:', error)
        // 显示错误信息
        const errorMessage = `## AI 助手错误\n\n抱歉，无法连接到AI助手。请稍后重试。`
        const errorCell = {
          id: Date.now().toString() + '_ai_error',
          type: 'markdown',
          content: errorMessage,
          output: [],
          isSystemGenerated: true,
          isEditing: false
        }
        cells.value.splice(cellIndex + 1, 0, errorCell)
        emitContentChange()
      } finally {
        // 重置运行状态
        cells.value[cellIndex].isRunning = false
      }
    }
    
    // 处理自动补全请求
    const handleCompletionRequest = async (cellIndex, event) => {
      console.log('Jupyter收到补全请求，单元格索引:', cellIndex);
      const cell = notebook.value.cells[cellIndex];
      if (!cell) {
        console.warn('Jupyter补全请求失败：找不到单元格', cellIndex);
        return;
      }
      
      // 获取当前单元格的上下文（如导入的库、定义的变量等）
      const cellContext = extractCellContext(cell, cellIndex);
      console.log('Jupyter补全上下文:', {
        language: cell.language,
        imports: cellContext.imports,
        variables: cellContext.variables,
        functions: cellContext.functions
      });
      
      try {
        // 生成上下文感知的补全建议
        const contextAwareCompletions = await generateContextAwareCompletions(
          event.code,
          cellContext,
          cell.language,
          getNotebookContext()
        );
        
        console.log('Jupyter生成的补全建议数量:', contextAwareCompletions.length);
        
        // 确保即使没有上下文感知补全，也返回基本的补全建议
        if (event.onComplete) {
          // 如果没有特定的上下文补全，提供一些基本建议
          if (contextAwareCompletions.length === 0) {
            const basicFallbackCompletions = [
              {
                label: 'print()',
                kind: monaco.languages.CompletionItemKind.Method,
                insertText: 'print($0)',
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: '基本打印函数',
                sortText: '0000'
              },
              {
                label: 'console.log()',
                kind: monaco.languages.CompletionItemKind.Method,
                insertText: 'console.log($0)',
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: '控制台输出',
                sortText: '0001'
              },
              {
                label: 'for循环',
                kind: monaco.languages.CompletionItemKind.Snippet,
                insertText: cell.language === 'python' ? 
                  'for item in $1:\n\t$0' : 
                  'for (let i = 0; i < $1; i++) {\n\t$0\n}',
                insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
                documentation: '循环结构',
                sortText: '0002'
              }
            ];
            event.onComplete(basicFallbackCompletions);
            console.log('返回基本回退补全建议');
          } else {
            event.onComplete(contextAwareCompletions);
          }
        }
      } catch (error) {
        console.error('Jupyter补全失败:', error);
        // 出错时也返回基本补全
        if (event.onComplete) {
          event.onComplete([
            {
              label: 'print()',
              kind: monaco.languages.CompletionItemKind.Method,
              insertText: 'print($0)',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: '基本打印函数',
              sortText: '0000'
            }
          ]);
        }
      }
    };
    
    // 提取单元格上下文
    const extractCellContext = (cell, cellIndex) => {
      const imports = [];
      const variables = [];
      const functions = [];
      
      // 分析当前单元格和之前所有单元格的代码
      for (let i = 0; i <= cellIndex; i++) {
        const prevCell = notebook.value.cells[i];
        if (prevCell.type === 'code') {
          const cellCode = prevCell.content;
          
          // 根据语言分析代码
          if (prevCell.language === 'python') {
            // 提取Python导入
            const importRegex = /^\s*(?:import\s+([\w\.]+)|from\s+([\w\.]+)\s+import)/gm;
            let match;
            while ((match = importRegex.exec(cellCode)) !== null) {
              if (match[1]) imports.push(match[1]);
              if (match[2]) imports.push(match[2]);
            }
            
            // 提取Python变量和函数
            const defRegex = /^\s*def\s+([\w]+)\s*\(/gm;
            while ((match = defRegex.exec(cellCode)) !== null) {
              functions.push(match[1]);
            }
            
            // 简单变量定义提取
            const varRegex = /^\s*(?:[a-zA-Z_][a-zA-Z0-9_]*)\s*=/gm;
            while ((match = varRegex.exec(cellCode)) !== null) {
              const varName = match[0].trim().split('=')[0].trim();
              if (!functions.includes(varName) && !variables.includes(varName)) {
                variables.push(varName);
              }
            }
          } else if (prevCell.language === 'javascript') {
            // 提取JavaScript函数
            const funcRegex = /^\s*(?:function\s+([\w]+)|const\s+([\w]+)\s*=\s*\(.*\)\s*=>|let\s+([\w]+)\s*=\s*\(.*\)\s*=>|var\s+([\w]+)\s*=\s*\(.*\)\s*=>)/gm;
            let match;
            while ((match = funcRegex.exec(cellCode)) !== null) {
              for (let i = 1; i <= 4; i++) {
                if (match[i]) functions.push(match[i]);
              }
            }
            
            // 提取JavaScript变量
            const varRegex = /^\s*(?:const|let|var)\s+([\w]+)/gm;
            while ((match = varRegex.exec(cellCode)) !== null) {
              if (!functions.includes(match[1]) && !variables.includes(match[1])) {
                variables.push(match[1]);
              }
            }
          }
        }
      }
      
      return {
        imports: [...new Set(imports)], // 去重
        variables: [...new Set(variables)],
        functions: [...new Set(functions)]
      };
    };
    
    // 获取笔记本整体上下文
    const getNotebookContext = () => {
      // 统计笔记本中最常用的语言
      const languageCount = {};
      notebook.value.cells.forEach(cell => {
        if (cell.type === 'code') {
          languageCount[cell.language] = (languageCount[cell.language] || 0) + 1;
        }
      });
      
      const mostUsedLanguage = Object.entries(languageCount).sort((a, b) => b[1] - a[1])[0]?.[0] || 'python';
      
      return {
        title: notebook.value.title || 'Untitled Notebook',
        cellCount: notebook.value.cells.length,
        codeCellCount: notebook.value.cells.filter(c => c.type === 'code').length,
        mostUsedLanguage
      };
    };
    
    // 生成上下文感知的补全建议
    const generateContextAwareCompletions = async (cellCode, cellContext, language, notebookContext) => {
      // 这里应该调用后端API获取智能补全
      // 现在使用模拟数据
      const completions = [];
      
      // 基于导入的库生成补全
      if (language === 'python') {
        if (cellContext.imports.includes('numpy')) {
          completions.push({
            label: 'np.array()',
            kind: monaco.languages.CompletionItemKind.Method,
            insertText: 'np.array($0)',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: '创建numpy数组',
            sortText: '0000'
          });
          completions.push({
            label: 'np.zeros()',
            kind: monaco.languages.CompletionItemKind.Method,
            insertText: 'np.zeros($0)',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: '创建全零数组',
            sortText: '0001'
          });
        }
        
        if (cellContext.imports.includes('pandas')) {
          completions.push({
            label: 'pd.DataFrame()',
            kind: monaco.languages.CompletionItemKind.Method,
            insertText: 'pd.DataFrame($0)',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: '创建DataFrame',
            sortText: '0000'
          });
          completions.push({
            label: 'pd.read_csv()',
            kind: monaco.languages.CompletionItemKind.Method,
            insertText: 'pd.read_csv("$0")',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: '读取CSV文件',
            sortText: '0001'
          });
        }
      } else if (language === 'javascript') {
        if (cellContext.imports.includes('axios') || cellCode.includes('axios')) {
          completions.push({
            label: 'axios.get()',
            kind: monaco.languages.CompletionItemKind.Method,
            insertText: 'axios.get("$0")\n  .then(response => {\n    console.log(response.data);\n  })\n  .catch(error => {\n    console.error(error);\n  });',
            insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
            documentation: '使用axios发送GET请求',
            sortText: '0000'
          });
        }
      }
      
      // 基于已定义的变量生成补全
      cellContext.variables.forEach(varName => {
        completions.push({
          label: varName,
          kind: monaco.languages.CompletionItemKind.Variable,
          insertText: varName,
          documentation: '已定义变量',
          sortText: '0010'
        });
      });
      
      // 基于已定义的函数生成补全
      cellContext.functions.forEach(funcName => {
        completions.push({
          label: funcName,
          kind: monaco.languages.CompletionItemKind.Function,
          insertText: funcName + '($0)',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: '已定义函数',
          sortText: '0011'
        });
      });
      
      // 基于笔记本上下文生成通用建议
      if (language === notebookContext.mostUsedLanguage) {
        completions.push({
          label: 'notebook专用代码模板',
          kind: monaco.languages.CompletionItemKind.Snippet,
          insertText: language === 'python' ? 
            '# ' + notebookContext.title + '\n# 创建于 ' + new Date().toLocaleDateString() + '\n\n' + 
            '# 常用设置\nimport ' + (cellContext.imports.includes('numpy') ? 'numpy as np\nimport ' : '') + 
            (cellContext.imports.includes('pandas') ? 'pandas as pd\n\n' : '\n') + '$0' :
            '// ' + notebookContext.title + '\n// 创建于 ' + new Date().toLocaleDateString() + '\n\n$0',
          insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
          documentation: '笔记本专用模板',
          sortText: '0020'
        });
      }
      
      return completions;
    };
    
    // 处理代码选中
    const handleCodeSelection = (cellIndex, event) => {
      const { code, language, context, relativePosition } = event
      if (code) {
        codeSelectionState.value[index] = {
          hasSelection: true,
          selectedText: code,
          language: language,
          position: relativePosition || { top: 0, left: 0 }
        }
      } else {
        codeSelectionState.value[index] = { hasSelection: false }
      }
    }
    
    // 获取代码AI按钮定位样式
    const getCodeAIPositionStyle = (index) => {
      const state = codeSelectionState.value[index]
      if (!state || !state.position) {
        return { top: '0px', left: '0px' }
      }
      return {
        top: `${state.position.top}px`,
        left: `${state.position.left}px`
      }
    }
    
    // 处理代码AI交互
    const handleCodeAIInteract = async (index) => {
      const state = codeSelectionState.value[index]
      if (!state || !state.hasSelection || !state.selectedText) return
      
      try {
        // 构建问题文本
        const question = `请解释这段${state.language}代码：\n\`\`\`${state.language}\n${state.selectedText}\n\`\`\``
        
        // 显示全局AI助手界面并发送问题
        window.dispatchEvent(new CustomEvent('open-ai-assistant', {
          detail: { question: question }
        }))
        
        console.log('已发送代码到AI助手:', question)
        
        // 清除选中状态
        state.hasSelection = false
      } catch (error) {
        console.error('AI助手交互失败:', error)
      } finally {
        // 重置运行状态
        cells.value[index].isRunning = false
        // 清除选中状态
        codeSelectionState.value[index] = { hasSelection: false }
      }
    }

    // 处理文本选中事件
    const handleTextSelection = (cellIndex, event) => {
      const textarea = event.target
      const start = textarea.selectionStart
      const end = textarea.selectionEnd
      const selectedText = textarea.value.substring(start, end)

      if (selectedText.length > 0) {
        // 获取选中位置信息以定位按钮
        const rect = textarea.getBoundingClientRect()
        const lineHeight = parseInt(window.getComputedStyle(textarea).lineHeight)
        const startRow = textarea.value.substring(0, start).split('\n').length - 1
        
        textSelectionState.value[cellIndex] = {
          hasSelection: true,
          selectedText: selectedText,
          position: {
            top: rect.top + (startRow * lineHeight) + 10,
            left: rect.right - 40
          }
        }
        
        // 发送文本选中事件到父组件
        emit('text-selected', {
          text: selectedText,
          rect: rect,
          cellIndex: cellIndex
        })
      } else {
        // 清除选中状态
        if (textSelectionState.value[cellIndex]) {
          textSelectionState.value[cellIndex].hasSelection = false
        }
        
        // 发送取消选中事件到父组件
        emit('text-selected', {
          text: '',
          rect: null,
          cellIndex: cellIndex
        })
      }
    }
    
    // 处理Markdown预览中的文本选中
    const handlePreviewTextSelection = (cellIndex, event) => {
      const selection = window.getSelection()
      const selectedText = selection.toString().trim()
      
      if (selectedText.length > 0) {
        // 获取选中区域的位置信息
        const range = selection.getRangeAt(0)
        const rect = range.getBoundingClientRect()
        
        textSelectionState.value[cellIndex] = {
          hasSelection: true,
          selectedText: selectedText,
          position: {
            top: rect.top + 10,
            left: rect.right - 40
          }
        }
        
        // 发送文本选中事件到父组件
        emit('text-selected', {
          text: selectedText,
          rect: rect,
          cellIndex: cellIndex
        })
      } else {
        // 清除选中状态
        if (textSelectionState.value[cellIndex]) {
          textSelectionState.value[cellIndex].hasSelection = false
        }
        
        // 发送取消选中事件到父组件
        emit('text-selected', {
          text: '',
          rect: null,
          cellIndex: cellIndex
        })
      }
    }

    // 获取文本AI按钮位置样式
    const getTextAIPositionStyle = (cellIndex) => {
      const state = textSelectionState.value[cellIndex]
      if (!state) return {}
      
      return {
        position: 'absolute',
        top: `${state.position.top}px`,
        right: '10px',
        zIndex: 1000
      }
    }

    // 处理文本AI交互
    const handleTextAIInteract = async (cellIndex) => {
      try {
        const state = textSelectionState.value[cellIndex];
        if (!state || !state.hasSelection) return;

        // 构建问题文本
        const question = `请解释这段文本：\n\`\`\`\n${state.selectedText}\n\`\`\``;

        // 显示全局AI助手界面并发送问题
        window.dispatchEvent(new CustomEvent('open-ai-assistant', {
          detail: { question: question }
        }));

        console.log('已发送文本到AI助手:', question);
        
        // 清除选中状态
        state.hasSelection = false;
      } catch (error) {
        console.error('文本AI助手交互失败:', error);
      } finally {
        emitContentChange();
        
        // 清除选中状态
        if (textSelectionState.value[cellIndex]) {
          textSelectionState.value[cellIndex].hasSelection = false;
        }
        
        // 重置运行状态
        cells.value[cellIndex].isRunning = false;
      }
    }
    
    // 处理单元格运行
    const handleCellRun = (index, event) => {
      runCell(index)
    }
    
    // 获取输出行样式类
    const getOutputClass = (line) => {
      if (line.includes('错误') || line.includes('Error') || line.startsWith('Traceback')) {
        return 'error-line'
      }
      return 'normal-line'
    }
    
    // 保存状态提示
    const saveSuccess = ref(false)
    
    // 保存笔记本
    const saveNotebook = async () => {
      try {
        isSaving.value = true
        saveSuccess.value = false
        
        // 构建文档数据
        const content = JSON.stringify(cells.value)
        const documentData = {
          title: props.title,
          content: content, // 直接保存单元格数组，而不是转换为Markdown
          is_public: props.isPublic,
          // 添加书籍和章节信息
          book_id: props.bookId,
          chapter_id: props.chapterId
        }
        
        console.log('📤 准备保存文档数据:', {
          hasId: !!props.documentId,
          title: props.title,
          hasBookId: !!props.bookId,
          hasChapterId: !!props.chapterId,
          cellCount: cells.value.length
        })
        
        let response;
        // 根据是否有bookId和chapterId选择合适的API
        if (props.bookId && props.chapterId) {
          // 如果有书籍和章节信息，使用章节相关的API
          console.log('📚 使用章节API保存内容');
          response = await api.setChapterAsJupyter(props.chapterId, {
            content: documentData.content
          });
          console.log('✅ 章节内容保存成功:', response);
        } else if (props.documentId) {
          // 更新现有文档
          console.log('📄 更新现有文档');
          response = await api.updateJupyterDocument(props.documentId, documentData);
          console.log('✅ 文档更新成功:', response);
        } else {
          // 创建新文档
          console.log('🆕 创建新文档');
          response = await api.createJupyterDocument(documentData);
          console.log('✅ 文档创建成功:', response);
          
          // 如果有返回的ID，更新documentId
          if (response.id) {
            emit('update:documentId', response.id);
          }
        }
        
        emit('save', { 
          id: props.documentId || response?.id, 
          title: props.title, 
          content: content,
          isPublic: props.isPublic 
        })
        
        // 触发内容变化事件
        emit('contentChange', content)
        
        // 显示保存成功提示
        saveSuccess.value = true
        setTimeout(() => {
          saveSuccess.value = false
        }, 3000)
        
        // 触发保存成功事件
        emit('saved', response);
        console.log('🎉 保存完成，通知父组件');
        
      } catch (error) {
        console.error('❌ 保存文档失败:', error);
        // 更友好的错误提示
        const errorMessage = error.response?.data?.message || error.message || '保存失败，请重试';
        alert(`保存失败: ${errorMessage}`);
      } finally {
        isSaving.value = false
      }
    }
    
    // 发出内容变化事件
    const emitContentChange = () => {
      emit('contentChange', convertCellsToMarkdown())
    }
    
    // 监听单元格变化
    watch(
      () => cells.value,
      () => emitContentChange(),
      { deep: true }
    )
    
    // 监听isPublic变化
    watch(
      () => props.isPublic,
      (newVal) => {
        console.log('公开状态已更新:', newVal)
      }
    )
    
    // 初始化
    onMounted(() => {
      loadDocument()
    })
    
    // 监听documentId变化
    watch(
      () => props.documentId,
      (newId) => {
        if (newId) {
          loadDocument()
        }
      }
    )
    
    return {
      cells,
      selectedCellIndex,
      imageFileInput,
      isLoading,
      isSaving,
      saveSuccess,
      textSelectionState,
      codeSelectionState,
      CellType,
      getFileExtension,
      renderMarkdown,
      addMarkdownCellBefore,
      addCodeCellBefore,
      addImageCellBefore,
      addMarkdownCellAfter,
      addCodeCellAfter,
      addImageCellAfter,
      addMarkdownCellAtEnd,
      addCodeCellAtEnd,
      triggerImageUpload,
      triggerImageReupload,
      handleImageUpload,
      getCellTypeIcon,
      getToggleCellTypeIcon,
      deleteCell,
      toggleCellType,
      toggleCellEdit,
      updateCellContent,
      runCell,
      runAllCells,
      handleCellRun,
      getOutputClass,
      handleAIInteract,
      handleTextSelection,
      handlePreviewTextSelection,
      getTextAIPositionStyle,
      handleTextAIInteract,
      handleCodeSelection,
      getCodeAIPositionStyle,
      handleCodeAIInteract,
      saveNotebook,
      loadDocument,
      handleCellClick
    }
  }
}
</script>

<style scoped>
.jupyter-notebook {
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  background: white;
  overflow: hidden;
}

.notebook-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.notebook-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #333;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 8px 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.btn:hover {
  background: #f0f0f0;
  border-color: #bbb;
}

.btn-primary {
  background: #007bff;
  color: white;
  border-color: #007bff;
}

.btn-primary:hover {
  background: #0056b3;
  border-color: #0056b3;
}

.notebook-content {
  padding: 16px;
}

.cell {
  margin-bottom: 16px;
  border-radius: 6px;
  border: 1px solid #e0e0e0;
  overflow: hidden;
  transition: all 0.2s;
}

.cell.selected {
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
  /* 确保选中时不会改变尺寸 */
  padding: 0;
  margin-bottom: 16px;
}

/* 系统生成的单元格样式 */
.cell.system-cell {
  background-color: #fafafa;
  border-left: 4px solid #2196f3;
}

.cell.system-cell .cell-toolbar {
  background: #f0f7ff;
}

/* 用户创建的单元格样式 */
.cell.user-cell {
  background-color: #ffffff;
  border-left: 4px solid #4caf50;
}

.cell.user-cell .cell-toolbar {
  background: #f1f8e9;
}

/* 确保代码单元格和Monaco编辑器在选中时不会改变尺寸 */
.cell.code-cell {
  width: 100%;
  box-sizing: border-box;
}

.cell.code-cell .cell-content {
  width: 100%;
  box-sizing: border-box;
}

/* 确保Monaco编辑器不会因为选中状态而改变大小 */
.cell-content :deep(.monaco-editor-container) {
  width: 100% !important;
  min-height: 120px;
  box-sizing: border-box;
}

/* 确保选中状态不会影响单元格内部组件 */
.cell.selected .cell-content {
  width: 100%;
  box-sizing: border-box;
}

.cell-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8f8f8;
  border-bottom: 1px solid #e0e0e0;
}

.cell-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.cell-source-indicator {
  font-size: 12px;
  padding: 2px 6px;
  background: #e3f2fd;
  color: #1565c0;
  border-radius: 3px;
  font-weight: 500;
}

.cell-source-indicator.user-source {
  background: #e8f5e9;
  color: #2e7d32;
}

.cell-type-indicator {
  font-size: 16px;
}

.cell-actions {
  display: flex;
  gap: 4px;
}

.action-btn {
  padding: 4px 8px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  border-radius: 4px;
  transition: background 0.2s;
}

.action-btn:hover {
  background: #e0e0e0;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.cell-content {
  padding: 0;
}

.markdown-cell {
  min-height: 60px;
}

.markdown-input {
  width: 100%;
  min-height: 60px;
  padding: 12px;
  border: none;
  resize: vertical;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  font-size: 16px;
  line-height: 1.6;
  outline: none;
  box-sizing: border-box;
}

.markdown-preview {
  padding: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
  font-size: 16px;
  line-height: 1.6;
  color: #333;
}

.markdown-preview h1, .markdown-preview h2, .markdown-preview h3 {
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-preview pre {
  background: #f5f5f5;
  padding: 12px;
  border-radius: 4px;
  overflow-x: auto;
}

.markdown-preview code {
  background: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.markdown-preview pre code {
  background: transparent;
  padding: 0;
}

.code-cell {
  border-top: none;
}

.cell-output {
  border-top: 1px solid #e0e0e0;
  background: #fafafa;
}

.output-header {
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #666;
  background: #f0f0f0;
}

.output-content {
  padding: 12px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  white-space: pre-wrap;
  word-break: break-all;
}

.output-line {
  margin-bottom: 4px;
  line-height: 1.5;
}

.output-line:last-child {
  margin-bottom: 0;
}

.normal-line {
  color: #333;
}

.error-line {  
  color: #e74c3c;
}

/* 加载和保存状态提示 */
.loading-indicator, .saving-indicator {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 10px 20px;
  border-radius: 4px;
  color: white;
  font-weight: 500;
  z-index: 1000;
  animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.loading-indicator {
  background-color: #2196f3;
}

.saving-indicator {
  background-color: #ff9800;
}

/* 保存成功提示 */
.save-success-message {
  background-color: #d4edda;
  color: #155724;
  padding: 10px 16px;
  border-radius: 4px;
  margin-bottom: 16px;
  text-align: center;
  font-size: 14px;
  animation: fadeOut 3s forwards;
}

@keyframes fadeOut {
  0% { opacity: 1; }
  70% { opacity: 1; }
  100% { opacity: 0; }
}

.add-cell-buttons {
  display: flex;
  gap: 12px;
  margin-top: 20px;
}

.add-cell-btn {
  flex: 1;
  padding: 12px;
  border: 2px dashed #ddd;
  border-radius: 6px;
  background: transparent;
  cursor: pointer;
  font-size: 14px;
  color: #666;
  transition: all 0.2s;
}

.add-cell-btn.markdown-btn:hover {
  border-color: #4caf50;
  color: #4caf50;
  background: #f1f8e9;
}

.add-cell-btn.code-btn:hover {
  border-color: #2196f3;
  color: #2196f3;
  background: #f0f7ff;
}

/* 响应式下按钮垂直排列 */
@media (max-width: 768px) {
  .add-cell-buttons {
    flex-direction: column;
  }
}

/* 图片单元格样式 - 移出响应式媒体查询，确保在所有屏幕尺寸下正确显示 */
.image-cell {
  margin: 10px 0;
  text-align: center;
  padding: 10px;
  border-radius: 4px;
  background-color: #f9f9f9;
}

.cell-image {
  max-width: 100%;
  max-height: 500px;
  object-fit: contain;
  cursor: pointer;
  border-radius: 4px;
  border: 1px solid #ddd;
  transition: all 0.2s ease;
}

.cell-image:hover {
  transform: scale(1.01);
  border-color: #007bff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.image-error {
  padding: 20px;
  color: #dc3545;
  font-weight: bold;
}

.image-size-controls {
  display: flex;
  align-items: center;
  margin: 10px 0;
  gap: 10px;
  flex-wrap: wrap;
}

.image-size-controls label {
  margin-right: 5px;
  font-weight: 500;
}

.size-input {
  width: 100px;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.btn-small {
  padding: 4px 8px;
  font-size: 12px;
  margin-left: 10px;
}

/* AI助手交互按钮样式 */
.ai-assist-btn {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background-color: #2196f3;
  color: white;
  border: none;
  cursor: pointer;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.3);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  position: absolute;
  z-index: 1000;
}

.ai-assist-btn:hover {
  background-color: #1976d2;
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.5);
}

.ai-assist-btn:active {
  transform: scale(0.95);
}

/* 确保markdown输入框可以显示在按钮下方 */
.markdown-editor-container {
  position: relative;
}

.image-edit-controls {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
}

.alt-text-input {
  width: 100%;
  max-width: 500px;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.image-edit-controls button {
  margin: 0 5px;
  padding: 5px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.image-edit-controls .btn-primary {
  background-color: #007bff;
  color: white;
}

.image-edit-controls .btn {
  background-color: #f0f0f0;
  color: #333;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .notebook-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .cell-toolbar {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
  
  .cell-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
}
</style>
<template>
  <div class="monaco-card">
    <div class="monaco-header">
      <div class="monaco-info">
        <span class="language-badge" :class="languageClass">{{ languageName }}</span>
        <span class="filename">{{ filename }}</span>
      </div>
      <div class="monaco-actions">
        <button 
          v-if="!readOnly" 
          class="action-btn"
          @click="runCode"
          :disabled="!canRun"
          title="运行代码"
        >
          ▶️ 运行
        </button>
        <button 
          class="action-btn"
          @click="triggerCodeCompletion"
          title="智能代码补全"
        >
          ✨ 智能补全
        </button>
        <button class="action-btn" @click="toggleFullscreen" title="全屏编辑">
          📱 全屏
        </button>
        <button class="action-btn" @click="toggleReadOnly" title="切换编辑模式">
          {{ readOnly ? '✏️ 编辑' : '👁️ 只读' }}
        </button>
        <button class="action-btn" @click="changeTheme" title="切换主题">
          🎨 主题
        </button>
      </div>
    </div>
    
    <div class="monaco-container" ref="monacoContainer">
    </div>
    
    <div class="monaco-footer" v-if="showFooter">
      <div class="footer-info">
        <span class="stats">{{ stats }}</span>
      </div>
      <div class="footer-actions">
        <button 
          v-if="allowSave" 
          class="action-btn"
          @click="saveCode"
          title="保存代码"
        >
          💾 保存
        </button>
        <button class="action-btn" @click="formatCode" title="格式化代码">
          📝 格式化
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import * as monaco from 'monaco-editor'
import { getCodeTemplate, getDefaultTemplate } from '../api/codeSandbox.js'

// 配置Monaco Environment以使用正确版本的worker
import EditorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker'
import JsonWorker from 'monaco-editor/esm/vs/language/json/json.worker?worker'
import CssWorker from 'monaco-editor/esm/vs/language/css/css.worker?worker'
import HtmlWorker from 'monaco-editor/esm/vs/language/html/html.worker?worker'
import TsWorker from 'monaco-editor/esm/vs/language/typescript/ts.worker?worker'

window.MonacoEnvironment = {
  getWorker(_, label) {
    if (label === 'json') {
      return new JsonWorker()
    }
    if (label === 'css' || label === 'scss' || label === 'less') {
      return new CssWorker()
    }
    if (label === 'html' || label === 'handlebars' || label === 'razor') {
      return new HtmlWorker()
    }
    if (label === 'typescript' || label === 'javascript') {
      return new TsWorker()
    }
    return new EditorWorker()
  }
}

export default {
  name: 'MonacoCard',
  props: {
    modelValue: {
      type: String,
      default: ''
    },
    language: {
      type: String,
      default: 'javascript'
    },
    filename: {
      type: String,
      default: 'untitled.js'
    },
    readOnly: {
      type: Boolean,
      default: false
    },
    canRun: {
      type: Boolean,
      default: true
    },
    showFooter: {
      type: Boolean,
      default: true
    },
    allowSave: {
      type: Boolean,
      default: true
    },
    theme: {
      type: String,
      default: 'vs-dark'
    },
    fontSize: {
      type: Number,
      default: 14
    },
    showLineNumbers: {
      type: Boolean,
      default: true
    },
    useVimMode: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'run', 'save', 'changeTheme', 'fullscreen', 'ai-interact', 'completion-request'],

  setup(props, { emit }) {
    const monacoContainer = ref(null)
    let editor = null
    let isFullscreen = false
    let localReadOnly = props.readOnly
    let currentTheme = props.theme
    
    // 计算语言名称显示
    const languageName = ref('')
    const languageClass = ref('')
    
    // 计算统计信息
    const stats = ref('')
    
    // AI助手互动相关状态
    const hasSelection = ref(false)
    const selectedCode = ref('')
    const aiButtonPosition = ref({ top: 0, left: 0 })
    
    // 自动补全相关状态
    const completionCache = ref(new Map())
    const isCompletionLoading = ref(false)
    
    // 初始化编辑器
    const initMonaco = () => {
      if (!monacoContainer.value || editor) return
      
      // 配置编辑器选项
      const options = {
        value: props.modelValue,
        language: props.language,
        theme: currentTheme,
        readOnly: localReadOnly,
        minimap: { enabled: true },
        fontSize: props.fontSize,
        lineNumbers: props.showLineNumbers ? 'on' : 'off',
        automaticLayout: true,
        scrollBeyondLastLine: false,
        tabSize: 2,
        wordWrap: 'on',
        cursorBlinking: 'smooth',
        contextmenu: true,
        scrollbar: {
          useShadows: false,
          verticalScrollbarSize: 10,
          horizontalScrollbarSize: 10
        },
        suggest: {
          // 确保自动显示建议
          quickSuggestions: {
            other: true,
            comments: true,
            strings: true
          },
          quickSuggestionsDelay: 0, // 立即显示建议
          // 禁用代码片段下拉列表
          showSnippets: false,
          snippetsPreventQuickSuggestions: true,
          // 保留必要的代码建议功能
          showMethods: true,
          showFunctions: true,
          showConstructors: true,
          showFields: true,
          showVariables: true,
          showClasses: true,
          showModules: true,
          showProperties: true,
          showKeywords: true,
          // 其他优化设置
          filterGraceful: true,
          maxVisibleSuggestions: 10,
          shareSuggestSelections: true,
          acceptSuggestionOnEnter: 'on'
        }
      }
      
      // 如果启用Vim模式
      if (props.useVimMode) {
        // 注意：实际使用vim模式需要引入额外的插件
        console.log('Vim模式已启用')
      }
      
      // 创建编辑器实例
      editor = monaco.editor.create(monacoContainer.value, options)
      
      // 注册自定义补全提供者
      registerCustomCompletion()
      
      // 监听内容变化
      let lastContentChangeTime = 0;
      const CONTENT_CHANGE_DEBOUNCE_TIME = 300; // 300ms延迟
      
      editor.onDidChangeModelContent(() => {
        const content = editor.getValue()
        emit('update:modelValue', content)
        updateStats(content)
        
        // 自动提供上下文感知的代码建议
        const currentTime = Date.now();
        const position = editor.getPosition();
        
        // 使用防抖确保不会频繁触发，只有在用户停止输入短暂时间后才提供建议
        if (currentTime - lastContentChangeTime >= CONTENT_CHANGE_DEBOUNCE_TIME) {
          // 检查是否应该提供上下文感知建议
          const model = editor.getModel();
          const currentLine = model.getLineContent(position.lineNumber);
          
          // 根据当前行的内容决定是否提供智能建议
          // 例如，如果用户正在输入表达式、变量名或函数调用，我们提供建议
          if (shouldProvideContextSuggestions(currentLine, position.column)) {
            // 不直接触发显示，而是预先加载上下文感知建议到缓存
            // 这样当编辑器自动显示建议列表时，上下文感知的建议也会包含在内
            preloadContextAwareSuggestions();
          }
        }
        
        lastContentChangeTime = currentTime;
      })
      
      // 判断是否应该提供上下文感知建议的辅助函数
      const shouldProvideContextSuggestions = (currentLine, column) => {
        // 获取光标前的代码片段
        const prefix = currentLine.substring(0, column);
        
        // 如果前缀太短，不提供建议
        if (prefix.length < 3) return false;
        
        // 如果正在注释或字符串中，不提供上下文建议
        const inCommentOrString = /(?:^|[^\\])(?:\/\/|\/\*|"[^"]*$|'[^']*$)/.test(prefix);
        if (inCommentOrString) return false;
        
        // 检查是否符合某些模式（如正在输入函数名、变量名等）
        // 这里可以添加更复杂的逻辑来判断是否需要提供上下文建议
        const patterns = [
          /\w\s*=\s*$/, // 变量赋值
          /\w\s*\($/, // 函数调用开始
          /\.\w*$/, // 对象属性访问
          /^\s*(?:function|def|class)\s+\w*$/, // 定义函数或类
        ];
        
        return patterns.some(pattern => pattern.test(prefix));
      };
      
      // 预加载上下文感知建议到缓存
      const preloadContextAwareSuggestions = async () => {
        if (!editor) return;
        
        try {
          // 获取当前位置和上下文
          const position = editor.getPosition();
          const model = editor.getModel();
          const currentLine = model.getLineContent(position.lineNumber);
          const prevLine = position.lineNumber > 1 ? model.getLineContent(position.lineNumber - 1) : '';
          
          // 生成缓存键
          const contextCacheKey = `${props.language}_${position.lineNumber}_${position.column}_${prevLine.substring(0, 20)}_context`;
          
          // 检查是否已有缓存
          if (getCachedCompletions(contextCacheKey)) {
            return;
          }
          
          // 这里可以异步请求上下文感知建议并缓存
          // 但不触发显示，让编辑器的自动建议机制处理显示
          const code = editor.getValue();
          
          // 简单的模拟实现 - 在实际应用中可以根据需要扩展
          const mockCompletions = generateMockContextCompletions(code, props.language, currentLine, prevLine);
          if (mockCompletions.length > 0) {
            setCachedCompletions(contextCacheKey, mockCompletions);
          }
        } catch (error) {
          console.error('预加载上下文建议错误:', error);
        }
      };
      
      // 生成模拟的上下文感知建议
      const generateMockContextCompletions = (code, language, currentLine, prevLine) => {
        const completions = [];
        
        // 这里可以根据代码上下文生成更智能的建议
        // 这只是一个简单示例
        if (language === 'javascript') {
          if (currentLine.includes('console.')) {
            completions.push({
              label: 'console.log()',
              kind: monaco.languages.CompletionItemKind.Method,
              insertText: 'log($0)',
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: '输出到控制台'
            });
          }
        }
        
        return completions;
      };
      
      // 监听选择变化
      editor.onDidChangeCursorSelection(() => {
        const selection = editor.getSelection()
        if (!selection.isEmpty()) {
          // 有选中内容
          hasSelection.value = true
          selectedCode.value = editor.getModel().getValueInRange(selection)
          
          // 计算AI按钮的位置 - 设置为单元格上方中央
          const containerPosition = monacoContainer.value?.getBoundingClientRect()
          
          if (containerPosition) {
            aiButtonPosition.value = {
              top: -30,
              left: containerPosition.width / 2
            }
          }
        } else {
          // 无选中内容
          hasSelection.value = false
          selectedCode.value = ''
        }
      })
      
      // 初始化语言信息
      updateLanguageInfo()
      updateStats(props.modelValue)
    }
    
    // 更新语言信息
    const updateLanguageInfo = () => {
      const langMap = {
        'javascript': { name: 'JavaScript', class: 'js' },
        'python': { name: 'Python', class: 'py' },
        'java': { name: 'Java', class: 'java' },
        'cpp': { name: 'C++', class: 'cpp' },
        'csharp': { name: 'C#', class: 'csharp' },
        'c': { name: 'C', class: 'c' },
        'html': { name: 'HTML', class: 'html' },
        'css': { name: 'CSS', class: 'css' },
        'markdown': { name: 'Markdown', class: 'md' }
      }
      
      const langInfo = langMap[props.language] || { name: props.language, class: 'other' }
      languageName.value = langInfo.name
      languageClass.value = langInfo.class
    }
    
    // 更新统计信息
    const updateStats = (content) => {
      const lines = content.split('\n')
      const lineCount = lines.length
      const charCount = content.length
      const wordCount = content.trim().length > 0 ? content.trim().split(/\s+/).length : 0
      
      stats.value = `${lineCount} 行 | ${wordCount} 词 | ${charCount} 字符`
    }
    
    // 自动检测代码语言
    const detectLanguage = (code) => {
      // 统计各语言特征出现次数
      const languageScores = {
        javascript: 0,
        python: 0,
        java: 0,
        c: 0,
        html: 0
      };
      
      // JavaScript特征
      const jsPatterns = [
        /\bconsole\.log\(/,
        /\bfunction\s+\w+\s*\(/,
        /\bconst\s+\w+/,
        /\blet\s+\w+/,
        /\bvar\s+\w+/,
        /=>/,
        /\bimport\s+.*\s+from\s+/,
        /\bexport\s+(default\s+)?/,
        /`[^`]*`/,
        /\.then\(/
      ];
      
      // Python特征
      const pythonPatterns = [
        /\bprint\s*\(/i,
        /\bdef\s+\w+\s*\(/i,
        /\bimport\s+\w+/i,
        /\bclass\s+\w+/i,
        /\bfor\s+\w+\s+in/i,
        /\bif\s+.+\s*:\s*$/im,
        /\bimport\s+\w+\s+as\s+\w+/i,
        /\bfrom\s+\w+\s+import/i
      ];
      
      // Java特征
      const javaPatterns = [
        /\bpublic\s+class\s+\w+/,
        /\bpublic\s+static\s+void\s+main/,
        /\bSystem\.out\.println\(/,
        /\bimport\s+java\./,
        /\bprivate\s+/,
        /\bpublic\s+/,
        /\bprotected\s+/,
        /\bString\[\] args/,
        /\bnew\s+\w+\(/
      ];
      
      // C语言特征
      const cPatterns = [
        /\b#include\s*<[^>]+>/,
        /\bint\s+main\s*\(/,
        /\bprintf\s*\(/,
        /\bscanf\s*\(/,
        /\bvoid\s+\w+\s*\(/,
        /\bint\s+\w+;/,
        /\bchar\s+\w+;/,
        /\bfloat\s+\w+;/,
        /\bdouble\s+\w+;/,
        /\breturn\s+\d+;/
      ];
      
      // HTML特征
      const htmlPatterns = [
        /<html/i,
        /<head/i,
        /<body/i,
        /<div/i,
        /<span/i,
        /<p/i,
        /<h[1-6]/i,
        /<!DOCTYPE html/i,
        /<script/i,
        /<style/i
      ];
      
      // 计算各语言特征匹配数量
      jsPatterns.forEach(pattern => {
        if (pattern.test(code)) languageScores.javascript++;
      });
      
      pythonPatterns.forEach(pattern => {
        if (pattern.test(code)) languageScores.python++;
      });
      
      javaPatterns.forEach(pattern => {
        if (pattern.test(code)) languageScores.java++;
      });
      
      cPatterns.forEach(pattern => {
        if (pattern.test(code)) languageScores.c++;
      });
      
      htmlPatterns.forEach(pattern => {
        if (pattern.test(code)) languageScores.html++;
      });
      
      // 找出得分最高的语言
      let maxScore = 0;
      let detectedLang = 'javascript'; // 默认返回JavaScript
      
      for (const [lang, score] of Object.entries(languageScores)) {
        if (score > maxScore) {
          maxScore = score;
          detectedLang = lang;
        }
      }
      
      // 只有当得分超过阈值时才返回检测到的语言
      if (maxScore >= 3) {
        return detectedLang;
      }
      
      // 默认返回JavaScript
      return 'javascript';
    };

    // 运行代码
    const runCode = () => {
      const code = editor.getValue();
      const detectedLanguage = detectLanguage(code);
      // 触发父组件的run事件，包含检测到的语言
      emit('run', { code, language: detectedLanguage })
    }
    
    // 保存代码
    const saveCode = () => {
      emit('save', {
        content: editor.getValue(),
        language: props.language,
        filename: props.filename
      })
    }
    
    // 切换全屏模式
    const toggleFullscreen = () => {
      isFullscreen = !isFullscreen
      const card = monacoContainer.value.closest('.monaco-card')
      
      if (isFullscreen) {
        card.classList.add('fullscreen')
        document.body.style.overflow = 'hidden'
      } else {
        card.classList.remove('fullscreen')
        document.body.style.overflow = 'auto'
      }
      
      // 通知父组件
      emit('fullscreen', isFullscreen)
      
      // 重新布局编辑器
      nextTick(() => {
        editor?.layout()
      })
    }
    
    // 切换只读模式
    const toggleReadOnly = () => {
      localReadOnly = !localReadOnly
      editor.updateOptions({ readOnly: localReadOnly })
    }
    
    // 切换主题
    const changeTheme = () => {
      const themes = ['vs-dark', 'vs', 'hc-black']
      const currentIndex = themes.indexOf(currentTheme)
      const nextIndex = (currentIndex + 1) % themes.length
      currentTheme = themes[nextIndex]
      
      monaco.editor.setTheme(currentTheme)
      emit('changeTheme', currentTheme)
    }
    
    // 格式化代码
    const formatCode = () => {
      const selection = editor.getSelection()
      if (selection.isEmpty()) {
        // 格式化整个文档
        monaco.editor.getModels().forEach(model => {
          monaco.languages.formatting.formatDocument(model, undefined, {})
            .then(edits => {
              const op = {
                identifier: { major: 1, minor: 1 },
                edits: edits
              }
              editor.executeEdits('format', edits)
            })
        })
      } else {
        // 格式化选中部分
        monaco.languages.formatting.format(editor.getModel(), selection, {})
          .then(edits => {
            editor.executeEdits('format', edits)
          })
      }
    }
    
    // 获取编辑器实例的方法
    const getEditor = () => {
      return editor
    }
    
    // 与AI助手互动
    const interactWithAI = () => {
      if (selectedCode.value) {
        // 获取选择的位置信息 - 设置为单元格上方中央
        const containerPosition = monacoContainer.value?.getBoundingClientRect()
        
        let relativePosition = { top: 0, left: 0 }
        if (containerPosition) {
          relativePosition = {
            top: -30,
            left: containerPosition.width / 2
          }
        }
        
        emit('ai-interact', {
          code: selectedCode.value,
          language: props.language,
          relativePosition: relativePosition,
          context: {
            filename: props.filename,
            fullContent: editor.getValue()
          }
        })
      }
    }
    
    // 监听语言变化
  watch(() => props.language, async (newLanguage, oldLanguage) => {
    console.log(`[语言切换] 从 ${oldLanguage} 切换到 ${newLanguage}`);
    
    if (editor) {
      // 设置编辑器语言
      monaco.editor.setModelLanguage(editor.getModel(), newLanguage);
      updateLanguageInfo();
      
      // 使用getDefaultTemplate获取完整模板
      try {
        console.log(`[模板获取] 使用getDefaultTemplate获取 ${newLanguage} 模板`);
        const defaultTemplate = getDefaultTemplate(newLanguage);
        console.log(`[模板获取] 获取到模板长度: ${defaultTemplate ? defaultTemplate.length : 0} 字符`);
        
        if (defaultTemplate) {
          console.log(`[模板设置] 设置 ${newLanguage} 模板到编辑器`);
          editor.setValue(defaultTemplate);
          emit('update:modelValue', defaultTemplate);
        } else {
          console.log(`[模板警告] 获取到空模板，使用基本模板`);
          const basicTemplate = `// ${newLanguage} 默认模板\n`;
          editor.setValue(basicTemplate);
          emit('update:modelValue', basicTemplate);
        }
      } catch (error) {
        console.error(`[模板错误] 设置模板失败:`, error);
        // 最基本的错误处理
        const errorTemplate = `// ${newLanguage} 模板加载失败`;
        editor.setValue(errorTemplate);
        emit('update:modelValue', errorTemplate);
      }
    }
  })
    
    // 监听主题变化
    watch(() => props.theme, (newTheme) => {
      if (editor && newTheme !== currentTheme) {
        currentTheme = newTheme
        monaco.editor.setTheme(currentTheme)
      }
    })
    
    // 监听内容变化（来自父组件）
    watch(() => props.modelValue, (newValue) => {
      if (editor && editor.getValue() !== newValue) {
        editor.setValue(newValue)
        updateStats(newValue)
      }
    })
    
    // 监听字体大小变化
    watch(() => props.fontSize, (newSize) => {
      if (editor) {
        editor.updateOptions({ fontSize: newSize })
      }
    })
    
    // 监听行号显示变化
    watch(() => props.showLineNumbers, (show) => {
      if (editor) {
        editor.updateOptions({ lineNumbers: show ? 'on' : 'off' })
      }
    })
    
    // 组件挂载后初始化
    onMounted(() => {
      nextTick(() => {
        initMonaco()
      })
    })
    
    // 注册自定义补全提供者
    const registerCustomCompletion = () => {
      // 为当前语言注册自定义补全提供者（简化版，仅提供必要的上下文感知建议）
      monaco.languages.registerCompletionItemProvider(props.language, {
        provideCompletionItems: (model, position) => {
          // 获取当前行和前一行的上下文
          const lineContent = model.getLineContent(position.lineNumber)
          const linePrefix = lineContent.substring(0, position.column)
          const prevLine = position.lineNumber > 1 ? model.getLineContent(position.lineNumber - 1) : ''
          
          // 根据语言提供特定补全（过滤掉代码片段）
          const languageSpecificCompletions = getLanguageCompletions(props.language)
            .filter(completion => completion.kind !== monaco.languages.CompletionItemKind.Snippet);
          
          // 生成增强的缓存键
          const cacheKey = `${props.language}_${position.lineNumber}_${position.column}`;
          const contextCacheKey = `${props.language}_${position.lineNumber}_${position.column}_${prevLine.substring(0, 20)}_context`;
          
          // 从缓存获取标准补全
          const standardCompletions = getCachedCompletions(cacheKey);
          
          // 从缓存获取上下文感知的补全
          const contextAwareCompletions = getCachedCompletions(contextCacheKey) || [];
          
          // 合并并过滤掉代码片段
          let finalCompletions = [...languageSpecificCompletions];
          
          // 添加标准补全缓存（过滤掉代码片段）
          if (standardCompletions) {
            finalCompletions = [...finalCompletions, ...standardCompletions.filter(c => c.kind !== monaco.languages.CompletionItemKind.Snippet)];
          }
          
          // 添加上下文感知补全并避免重复，过滤掉代码片段
          const existingLabels = new Set(finalCompletions.map(completion => completion.label));
          contextAwareCompletions.forEach(completion => {
            if (!existingLabels.has(completion.label) && completion.kind !== monaco.languages.CompletionItemKind.Snippet) {
              finalCompletions.push(completion);
              existingLabels.add(completion.label);
            }
          });
          
          // 去重（基于label）
          const uniqueCompletions = finalCompletions.filter((completion, index, self) =>
            index === self.findIndex(c => c.label === completion.label)
          );
          
          return {
            suggestions: uniqueCompletions
          };
        },
        // 精简触发字符，减少不必要的建议
        triggerCharacters: ['.', '(', '=', ' ', ';'],
        // 补全项选中后的处理
        resolveCompletionItem: (item) => {
          // 记录用户选择的补全项
          recordCompletionChoice(props.language, item);
          
          // 确保不会解析代码片段
          if (item.insertTextRules === monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet) {
            item.insertTextRules = undefined;
          }
          return item;
        }
      });
    };
    
    // 获取语言特定的补全项（移除所有代码片段）
    const getLanguageCompletions = (language) => {
      // 确保不返回任何代码片段，只提供基本的方法和函数补全
      const completionsByLanguage = {
        javascript: [
          {
            label: 'console.log',
            kind: monaco.languages.CompletionItemKind.Method,
            insertText: 'console.log()',
            insertTextRules: undefined, // 确保不使用代码片段规则
            documentation: '输出到控制台'
          },
          {
            label: 'setTimeout',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'setTimeout()',
            insertTextRules: undefined,
            documentation: '设置超时定时器'
          },
          {
            label: 'setInterval',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'setInterval()',
            insertTextRules: undefined,
            documentation: '设置间隔定时器'
          }
        ],
        python: [
          {
            label: 'print',
            kind: monaco.languages.CompletionItemKind.Function,
            insertText: 'print()',
            insertTextRules: undefined,
            documentation: '打印输出'
          }
        ],
        java: [
          {
            label: 'System.out.println',
            kind: monaco.languages.CompletionItemKind.Method,
            insertText: 'System.out.println()',
            insertTextRules: undefined,
            documentation: '输出到控制台'
          }
        ]
      }
      
      return completionsByLanguage[language] || [];
    };
    
    // 获取缓存的补全项
    const getCachedCompletions = (key) => {
      const cached = completionCache.value.get(key);
      if (cached && (Date.now() - cached.timestamp) < 300000) { // 5分钟缓存
        return cached.completions;
      }
      return null;
    };
    
    // 设置补全项缓存
    const setCachedCompletions = (key, completions) => {
      completionCache.value.set(key, {
        completions,
        timestamp: Date.now()
      });
      
      // 清理过期缓存（简单实现）
      if (completionCache.value.size > 100) {
        const oldestKey = completionCache.value.keys().next().value;
        completionCache.value.delete(oldestKey);
      }
    };
    
    // 记录用户选择的补全项
    const recordCompletionChoice = (language, completion) => {
      try {
        const history = JSON.parse(localStorage.getItem('completionHistory') || '{}');
        if (!history[language]) history[language] = {};
        
        history[language][completion.label] = (history[language][completion.label] || 0) + 1;
        localStorage.setItem('completionHistory', JSON.stringify(history));
      } catch (error) {
        console.warn('无法保存补全历史:', error);
      }
    };
    
    // 触发代码补全 - 现在专注于提供上下文感知的智能建议
  // 基础代码建议由编辑器自动提供
  const triggerCodeCompletion = () => {
    if (!editor) return;
    console.log('补全按钮被点击，提供上下文感知智能建议');
    
    // 重点是请求上下文感知的智能补全
    requestContextAwareCompletions();
    
    // 仍然可以触发一次建议显示，但现在这主要是为了立即显示上下文感知的建议
    // 而不是作为基础补全的触发机制
    editor.trigger('contextCompletion', 'editor.action.triggerSuggest', {});
  };
  
  // 请求上下文感知的补全 - 增强版本
  const requestContextAwareCompletions = async () => {
    if (!editor) return;
    console.log('请求上下文感知智能补全');
    
    // 获取当前编辑器内容和位置
    const code = editor.getValue();
    const position = editor.getPosition();
    const model = editor.getModel();
    
    // 获取当前行和前一行的代码作为上下文
    const currentLine = model.getLineContent(position.lineNumber);
    const prevLine = position.lineNumber > 1 ? model.getLineContent(position.lineNumber - 1) : '';
    
    // 基于当前编辑上下文生成增强的缓存键
    const contextCacheKey = `${props.language}_${position.lineNumber}_${position.column}_${prevLine.substring(0, 20)}_context`;
    
    try {
      // 1. 检查是否已有缓存结果
      const cachedCompletions = getCachedCompletions(contextCacheKey);
      if (cachedCompletions) {
        console.log('使用缓存的上下文感知补全结果');
        return;
      }
      
      // 2. 尝试向后端API请求补全建议
      const response = await fetch('/api/learning/code-completion/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          code,
          language: props.language,
          cursor_line: position.lineNumber,
          cursor_column: position.column,
          current_line: currentLine,
          previous_line: prevLine,
          context: '当前编辑文件'
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('收到后端智能补全结果:', data.completions?.length || 0);
        
        if (data.completions && data.completions.length > 0) {
          // 缓存后端返回的补全结果，增加缓存时间
          setCachedCompletions(contextCacheKey, data.completions);
        }
      } else {
        // 如果后端请求失败，回退到增强的前端上下文处理
        console.log('后端补全API请求失败，回退到前端上下文处理');
        requestFrontendContextCompletions(code, position, currentLine, prevLine);
      }
    } catch (error) {
      console.error('补全API请求错误:', error);
      // 请求出错时回退到增强的前端上下文处理
      requestFrontendContextCompletions(code, position, currentLine, prevLine);
    }
  };
  
  // 前端上下文补全处理（增强版本）
  const requestFrontendContextCompletions = (code, position, currentLine = '', prevLine = '') => {
    console.log('使用增强的前端上下文处理生成补全建议');
    
    // 生成更精确的缓存键
    const contextCacheKey = `${props.language}_${position.lineNumber}_${position.column}_${prevLine.substring(0, 20)}_context`;
    
    // 发送增强的completion-request事件给父组件（如JupyterNotebook）
    emit('completion-request', {
      code,
      language: props.language,
      cursorLine: position.lineNumber,
      cursorColumn: position.column,
      currentLine: currentLine,
      previousLine: prevLine,
      position,
      onComplete: (completions) => {
        console.log('收到增强的上下文感知补全结果:', completions ? completions.length : 0, '个建议');
        
        // 当收到上下文感知的补全后，将其添加到自定义补全提供者中
        if (completions && completions.length > 0) {
          // 缓存结果
          setCachedCompletions(contextCacheKey, completions);
          
          // 触发自定义补全的显示
          setTimeout(() => {
            editor.trigger('contextCompletion', 'editor.action.triggerSuggest', {});
          }, 50); // 减少延迟，提高响应速度
        } else {
          // 如果没有收到外部补全，使用内置的AI模拟生成
          provideAICompletionSuggestions();
        }
      }
    });
  };
  
  // AI辅助补全
  const provideAICompletionSuggestions = async () => {
      if (isCompletionLoading.value) return;
      
      const currentCode = editor.getValue();
      const position = editor.getPosition();
      
      try {
        isCompletionLoading.value = true;
        
        // 触发completion-request事件，让父组件（如JupyterNotebook）处理AI补全
        emit('completion-request', {
          code: currentCode,
          position: position,
          language: props.language,
          context: {
            filename: props.filename
          },
          onComplete: (aiCompletions) => {
            if (aiCompletions && aiCompletions.length > 0) {
              const cacheKey = `${props.language}_${position.lineNumber}_${position.column}_ai`;
              setCachedCompletions(cacheKey, aiCompletions);
              
              // 重新触发补全以显示AI建议
              setTimeout(() => {
                editor.trigger('autocomplete', 'editor.action.triggerSuggest', {});
              }, 100);
            }
          }
        });
        
        // 模拟AI补全建议（实际项目中应该调用后端API）
        const mockAICompletions = generateMockAICompletions(currentCode, props.language);
        if (mockAICompletions.length > 0) {
          const cacheKey = `${props.language}_${position.lineNumber}_${position.column}_ai`;
          setCachedCompletions(cacheKey, mockAICompletions);
        }
        
      } catch (error) {
        console.error('AI补全失败:', error);
      } finally {
        isCompletionLoading.value = false;
      }
    };
    
    // 生成模拟AI补全建议（完全移除代码片段，只提供简单的函数名建议）
    const generateMockAICompletions = (code, language) => {
      const completions = [];
      
      // 根据代码内容生成一些智能建议
      if (language === 'javascript') {
        if (code.includes('console.log') && !code.includes('try') && !code.includes('catch')) {
          completions.push({
            label: 'try-catch错误处理',
            kind: monaco.languages.CompletionItemKind.Method,
            insertText: 'try {\n  $0\n} catch (error) {\n  console.error("发生错误:", error);\n}',
            insertTextRules: undefined, // 确保不使用代码片段规则
            documentation: '添加错误处理',
            sortText: '0000' // 让AI建议排在前面
          });
        }
        if (code.includes('fetch(') || code.includes('axios.')) {
          completions.push({
            label: 'async-await',
            kind: monaco.languages.CompletionItemKind.Method,
            insertText: 'async function $1() {\n  try {\n    const response = await $2;\n    const data = await response.json();\n    $0\n  } catch (error) {\n    console.error(error);\n  }\n}',
            insertTextRules: undefined,
            documentation: '使用async-await简化异步代码',
            sortText: '0001'
          });
        }
      } else if (language === 'python') {
        if (code.includes('print') && !code.includes('try') && !code.includes('except')) {
          completions.push({
            label: 'try-except错误处理',
            kind: monaco.languages.CompletionItemKind.Method,
            insertText: 'try:\n  $0\nexcept Exception as e:\n  print(f"发生错误: {e}")',
            insertTextRules: undefined,
            documentation: '添加错误处理',
            sortText: '0000'
          });
        }
        if (code.includes('for') && !code.includes('import numpy')) {
          completions.push({
            label: 'numpy数组处理',
            kind: monaco.languages.CompletionItemKind.Method,
            insertText: 'import numpy as np\n\n# 使用numpy处理数组\ndata = np.array($1)\nresult = $0',
            insertTextRules: undefined,
            documentation: '使用numpy进行高效数组处理',
            sortText: '0001'
          });
        }
      }
      
      return completions;
    };
    
    // 组件卸载前清理
    onBeforeUnmount(() => {
      if (editor) {
        editor.dispose()
        editor = null
      }
      if (isFullscreen) {
        document.body.style.overflow = 'auto'
      }
    })
    
    // 处理ESC键退出全屏
    const handleEscKey = (event) => {
      if (event.key === 'Escape' && isFullscreen) {
        toggleFullscreen()
      }
    }
    
    onMounted(() => {
      document.addEventListener('keydown', handleEscKey)
    })
    
    onBeforeUnmount(() => {
      document.removeEventListener('keydown', handleEscKey)
    })
    
    return {
      monacoContainer,
      languageName,
      languageClass,
      stats,
      hasSelection,
      aiButtonPosition,
      interactWithAI,
      runCode,
      saveCode,
      toggleFullscreen,
      toggleReadOnly,
      changeTheme,
      formatCode,
      getEditor,
      triggerCodeCompletion,
      isCompletionLoading
    }
  }
}
</script>

<style scoped>
.monaco-card {
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  background: white;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 300px;
  transition: all 0.3s ease;
}

.monaco-card.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  height: 100vh;
  border-radius: 0;
  border: none;
}

/* 头部样式 */
.monaco-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
  border-radius: 8px 8px 0 0;
}

.monaco-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.language-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  text-transform: uppercase;
}

.language-badge.js {
  background: #f7df1e;
  color: #333;
}

.language-badge.py {
  background: #3776ab;
  color: white;
}

.language-badge.java {
  background: #007396;
  color: white;
}

.language-badge.c {
  background: #a8b9cc;
  color: #1e1e1e;
}

.language-badge.cpp {
  background: #00599c;
  color: white;
}

.language-badge.csharp {
  background: #239120;
  color: white;
}

.language-badge.html {
  background: #e34c26;
  color: white;
}

.language-badge.css {
  background: #1572b6;
  color: white;
}

.language-badge.md {
  background: #000000;
  color: white;
}

.language-badge.other {
  background: #999;
  color: white;
}

.filename {
  font-size: 14px;
  color: #666;
}

.monaco-actions {
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

.action-btn:hover:not(:disabled) {
  background: #f0f0f0;
  border-color: #bbb;
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 编辑器容器 */
.monaco-container {
  flex: 1;
  min-height: 200px;
  overflow: hidden;
  position: relative;
}

/* AI助手互动按钮 */
.ai-assist-btn {
  position: absolute;
  background: #4a9eff;
  color: white;
  border: none;
  border-radius: 20px;
  padding: 6px 12px;
  font-size: 12px;
  cursor: pointer;
  z-index: 1000;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  transition: all 0.2s ease;
  white-space: nowrap;
  opacity: 0.9;
  /* 定位到代码单元格上方中央 */
  top: -30px !important;
  left: 50% !important;
  transform: translateX(-50%) !important;
}

.ai-assist-btn:hover {
  background: #3584e4;
  opacity: 1;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
}

.ai-assist-btn:active {
  transform: translateY(0);
}

/* 底部样式 */
.monaco-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #f5f5f5;
  border-top: 1px solid #e0e0e0;
  border-radius: 0 0 8px 8px;
}

.footer-info {
  display: flex;
  align-items: center;
}

.stats {
  font-size: 12px;
  color: #666;
}

.footer-actions {
  display: flex;
  gap: 8px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .monaco-header {
    flex-direction: column;
    align-items: stretch;
    gap: 10px;
  }
  
  .monaco-info {
    justify-content: center;
  }
  
  .monaco-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .action-btn {
    font-size: 11px;
    padding: 5px 8px;
  }
  
  .monaco-footer {
    flex-direction: column;
    gap: 10px;
  }
  
  .footer-actions {
    width: 100%;
    justify-content: center;
  }
}

/* 暗色主题适配 */
.vs-dark .monaco-header,
.hc-black .monaco-header,
.vs-dark .monaco-footer,
.hc-black .monaco-footer {
  background: #252526;
  border-color: #3c3c3c;
}

.vs-dark .filename,
.hc-black .filename,
.vs-dark .stats,
.hc-black .stats {
  color: #ccc;
}

.vs-dark .action-btn,
.hc-black .action-btn {
  background: #3c3c3c;
  border-color: #5c5c5c;
  color: #eee;
}

.vs-dark .action-btn:hover:not(:disabled),
.hc-black .action-btn:hover:not(:disabled) {
  background: #5c5c5c;
  border-color: #7c7c7c;
}
</style>
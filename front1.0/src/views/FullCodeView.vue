<template>
  <div class="fullcode-container">
    <div class="fullcode-header">
      <div class="header-left">
        <h1>代码编辑器</h1>
        <div class="editor-info">
          <div class="language-select-container">
            <select v-if="!isLanguagesLoading && supportedLanguages.length > 0" v-model="codeLanguage" class="language-select" @change="updateLanguage">
              <option v-for="lang in supportedLanguages" :key="lang" :value="lang">
                {{ lang.charAt(0).toUpperCase() + lang.slice(1) }}
              </option>
            </select>
            <div v-else-if="isLanguagesLoading" class="language-select-loading">
              加载语言列表中...
            </div>
            <select v-else v-model="codeLanguage" class="language-select" @change="updateLanguage">
              <!-- 默认语言选项 -->
              <option value="javascript">JavaScript</option>
              <option value="python">Python</option>
              <option value="java">Java</option>
              <option value="c">C</option>
              <option value="html">HTML</option>
            </select>
          </div>
          <span class="file-name">{{ fileName }}</span>
          <span v-if="loadingTemplate" class="loading-indicator">加载模板中...</span>
        </div>
      </div>
      <div class="header-right">
        <button class="btn" @click="toggleTheme">
          {{ isDarkTheme ? '🌞' : '🌙' }}
        </button>
        <button class="btn" @click="toggleVimMode">
          {{ isVimMode ? '⌨️ Vim' : '⌨️ 正常' }}
        </button>
        <button class="btn" @click="formatCode">
          📝 格式化
        </button>
        <div class="font-size-controls">
          <button class="btn" @click="decreaseFontSize">-</button>
          <span class="font-size">{{ fontSize }}px</span>
          <button class="btn" @click="increaseFontSize">+</button>
        </div>
        <button class="btn btn-primary" @click="saveCode">💾 保存</button>
        <button class="btn btn-completion" @click="triggerCompletion">🧠 代码补全</button>
        <button class="btn" @click="backToLearn">← 返回</button>
      </div>
    </div>

    <div class="editor-container" :class="{ 'dark-theme': isDarkTheme }">
      <div class="monaco-editor">
        <div ref="monacoContainer" class="monaco-container"></div>
      </div>
    </div>

    <div class="result-drawer" :class="{ expanded: showResult }">
      <div class="drawer-handle" @click="toggleResult">
        <span>运行结果</span>
        <span class="drawer-icon">{{ showResult ? '▲' : '▼' }}</span>
      </div>
      <div class="drawer-content">
        <div class="drawer-header">
          <h3>Console</h3>
          <div class="drawer-actions">
            <button class="btn" @click="clearConsole">🗑️ 清屏</button>
            <button class="btn run-btn" @click="runCode">▶ 运行</button>
          </div>
        </div>
        <div class="stdin-input">
          <input 
            type="text" 
            v-model="stdinInput" 
            placeholder="输入标准输入..."
            class="input"
            @keyup.enter="sendStdin"
          />
          <button class="btn" @click="sendStdin">发送</button>
        </div>
        <div class="console-output">
          <div v-for="(line, index) in consoleOutput" :key="index" class="console-line" :class="getOutputClass(line)">
            {{ line }}
          </div>
          <div v-if="consoleOutput.length === 0" class="console-empty">运行代码后，结果将显示在这里</div>
        </div>
      </div>
    </div>

    <!-- 版本历史 -->
    <div class="version-history">
      <button class="btn" @click="showVersionHistory = !showVersionHistory">
        📋 版本历史 ({{ codeVersions.length }})
      </button>
      <div v-if="showVersionHistory" class="version-list">
        <div 
          v-for="(version, index) in codeVersions" 
          :key="index"
          class="version-item"
        >
          <div class="version-info">
            <span class="version-time">{{ formatTime(version.timestamp) }}</span>
            <span class="version-index">{{ index + 1 }}</span>
          </div>
          <div class="version-actions">
            <button class="btn btn-sm" @click="restoreVersion(index)">恢复</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 轻量化工具包入口 -->
    <div class="toolkit-entry">
      <router-link to="/toolkit" class="toolkit-btn">
        🛠️ 前往轻量化工具包
      </router-link>
      <p class="toolkit-desc">无需编程基础，使用现成工具解决问题</p>
    </div>
    
    <!-- AI报错翻译抽屉 -->
    <div v-if="showErrorDrawer" class="error-drawer">
      <div class="error-drawer-header">
        <h3>错误解释</h3>
        <button class="close-btn" @click="showErrorDrawer = false">×</button>
      </div>
      <div class="error-drawer-content">
        <div class="original-error">
          <h4>原始错误</h4>
          <pre>{{ errorInfo.original }}</pre>
        </div>
        <div class="translated-error">
          <h4>通俗解释</h4>
          <p>{{ errorInfo.translation }}</p>
        </div>
        <div class="error-solution">
          <h4>修复建议</h4>
          <p>{{ errorInfo.solution }}</p>
        </div>
        <button class="fix-btn" @click="applyFix">应用修复</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, onBeforeUnmount, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import * as monaco from 'monaco-editor'
import { getSupportedLanguages, getCodeTemplate } from '../api/codeSandbox'

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
  name: 'FullCodeView',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const monacoContainer = ref(null)
    
    // 编辑器配置
    const codeLanguage = ref('javascript')
    const isDarkTheme = ref(true)
    const isVimMode = ref(false)
    const fontSize = ref(14)
    const fileName = ref('untitled.js')
    const supportedLanguages = ref(['javascript', 'python'])
    const loadingTemplate = ref(false)
    const isLanguagesLoading = ref(false)
    
    // 代码片段功能已移除
    
    // 结果抽屉
    const showResult = ref(true)
    const consoleOutput = ref([])
    const stdinInput = ref('')
    
    // 版本控制
    const codeVersions = ref([])
    const showVersionHistory = ref(false)
    
    // AI错误翻译功能相关
    const showErrorDrawer = ref(false)
    const errorInfo = ref({
      original: '',
      translation: '',
      solution: '',
      fixedCode: '',
      errorLine: -1
    })
    
    // Monaco Editor实例
    let editor = null
    let model = null
    
    // 从localStorage加载代码版本
    const loadCodeVersions = () => {
      try {
        const savedVersions = localStorage.getItem('codeVersions')
        if (savedVersions) {
          codeVersions.value = JSON.parse(savedVersions)
        }
      } catch (error) {
        console.error('加载代码版本失败:', error)
      }
    }
    
    // 保存代码版本到localStorage
    const saveCodeVersions = () => {
      try {
        localStorage.setItem('codeVersions', JSON.stringify(codeVersions.value))
      } catch (error) {
        console.error('保存代码版本失败:', error)
      }
    }
    
    // 初始化Monaco编辑器
    const initMonacoEditor = async () => {
      if (!monacoContainer.value) return
      
      // 获取初始代码模板
      let initialCode = '';
      try {
        loadingTemplate.value = true;
        const templateData = await getCodeTemplate(codeLanguage.value);
        initialCode = templateData.template;
      } catch (error) {
        console.error('获取初始代码模板失败:', error);
        initialCode = '// 在这里编写你的代码';
      } finally {
        loadingTemplate.value = false;
      }
      
      // 创建模型
      model = monaco.editor.createModel(initialCode, codeLanguage.value)
      
      // 创建编辑器实例
      editor = monaco.editor.create(monacoContainer.value, {
        model: model,
        theme: isDarkTheme.value ? 'vs-dark' : 'vs',
        fontSize: fontSize.value,
        minimap: { enabled: true },
        lineNumbers: 'on',
        scrollBeyondLastLine: false,
        automaticLayout: true,
        formatOnType: true,
        formatOnPaste: true,
        suggest: {
          showMethods: true,
          showFunctions: true,
          showConstructors: true,
          showFields: true,
          showVariables: true,
          showClasses: true,
          showStructs: true,
          showInterfaces: true,
          showModules: true,
          showProperties: true,
          showEvents: true,
          showOperators: true,
          showUnits: true,
          showValues: true,
          showConstants: true,
          showEnums: true,
          showEnumMembers: true,
          showKeywords: true,
          showWords: true,
          showColors: true,
          showFiles: true,
          showReferences: true,
          showFolders: true,
          showTypeParameters: true,
          showSnippets: false,
          snippetsPreventQuickSuggestions: true,
          showFromUnimportedModules: false
        }
      })
      
      // 设置Vim模式
      if (isVimMode.value) {
        editor.updateOptions({ keybindingProvider: 'vim' })
      }
      
      // 移除代码片段功能
      registerBasicCompletionProvider()
    }
    
    // 简化的补全提供者，只提供基本函数名，不使用代码片段
    const registerBasicCompletionProvider = () => {
      // 确保编辑器配置中禁用代码片段
      if (editor) {
        editor.updateOptions({
          suggest: {
            showSnippets: false,
            snippetsPreventQuickSuggestions: true
          }
        })
      }
      
      // 为Python提供基本补全（不使用代码片段）
      monaco.languages.registerCompletionItemProvider('python', {
        provideCompletionItems: (model, position) => {
          const suggestions = [
            {
              label: 'print',
              kind: monaco.languages.CompletionItemKind.Method,
              insertText: 'print()',
              insertTextRules: undefined,
              documentation: '打印输出'
            },
            {
              label: 'def',
              kind: monaco.languages.CompletionItemKind.Keyword,
              insertText: 'def ',
              insertTextRules: undefined,
              documentation: '定义函数'
            }
          ]
          return { suggestions }
        }
      })
      
      // 为JavaScript提供基本补全（不使用代码片段）
      monaco.languages.registerCompletionItemProvider('javascript', {
        provideCompletionItems: (model, position) => {
          const suggestions = [
            {
              label: 'console.log',
              kind: monaco.languages.CompletionItemKind.Method,
              insertText: 'console.log()',
              insertTextRules: undefined,
              documentation: '控制台输出'
            },
            {
              label: 'setTimeout',
              kind: monaco.languages.CompletionItemKind.Function,
              insertText: 'setTimeout()',
              insertTextRules: undefined,
              documentation: '定时函数'
            },
            {
              label: 'fetch',
              kind: monaco.languages.CompletionItemKind.Function,
              insertText: {
                value: 'fetch(${1:url})\n  .then(response => response.json())\n  .then(data => {\n    $0\n  })\n  .catch(error => console.error(error));'
              },
              insertTextRules: monaco.languages.CompletionItemInsertTextRule.InsertAsSnippet,
              documentation: '网络请求'
            }
          ]
          return { suggestions: suggestions }
        }
      })
    }
    
    // 触发代码补全
    const triggerCompletion = () => {
      if (editor) {
        // Monaco Editor会自动处理补全，这里可以添加额外的提示
        consoleOutput.value.push('🧠 使用Ctrl+Space打开代码补全')
      }
    }
    
    // 获取当前编辑器的代码
    const getCurrentCode = () => {
      return model ? model.getValue() : ''
    }
    
    // 设置编辑器代码
    const setEditorCode = (code) => {
      if (model) {
        model.setValue(code)
      }
    }
    
    // 更新编辑器语言和代码模板
    const updateLanguage = async () => {
      // 更新文件名后缀
      updateFileName();
      
      // 先更新语言模式
      if (model) {
        monaco.editor.setModelLanguage(model, codeLanguage.value);
      }
      
      // 获取并设置对应语言的代码模板
      try {
        loadingTemplate.value = true;
        // 直接使用本地模板映射，避免API调用可能的问题
        const languageTemplates = {
          javascript: '// JavaScript 默认模板\nconsole.log("Hello, World!");',
          python: '# Python 默认模板\nprint("Hello, World!")',
          java: '// Java 默认模板\npublic class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
          cpp: '// C++ 默认模板\n#include <iostream>\n\nint main() {\n    std::cout << "Hello, World!" << std::endl;\n    return 0;\n}',
          c: '// C 默认模板\n#include <stdio.h>\n\nint main() {\n    printf("Hello, World!\n");\n    return 0;\n}',
          csharp: '// C# 默认模板\nusing System;\n\nclass Program {\n    static void Main() {\n        Console.WriteLine("Hello, World!");\n    }\n}',
          php: '<?php\n// PHP 默认模板\necho "Hello, World!";\n?>',
          ruby: '# Ruby 默认模板\nputs "Hello, World!"'
        };
        
        // 优先使用本地模板
        const template = languageTemplates[codeLanguage.value.toLowerCase()] || '// 在这里编写你的代码';
        
        if (model) {
          console.log(`更新为${codeLanguage.value}模板`);
          model.setValue(template);
        }
      } catch (error) {
        console.error(`更新${codeLanguage.value}代码模板失败:`, error);
        // 错误处理：使用基本模板
        if (model) {
          model.setValue(`// ${codeLanguage.value} 模板`);
        }
      } finally {
        loadingTemplate.value = false;
      }
    };
    
    // 更新文件名
    const updateFileName = () => {
      const extensions = {
        javascript: 'js',
        python: 'py',
        java: 'java',
        cpp: 'cpp',
        c: 'c',
        csharp: 'cs',
        php: 'php',
        ruby: 'rb',
        go: 'go',
        rust: 'rs',
        html: 'html',
        css: 'css'
      };
      
      const extension = extensions[codeLanguage.value] || 'txt';
      fileName.value = `untitled.${extension}`;
    }
    
    // 格式化代码
    const formatCode = () => {
      if (!editor) return;
      
      const selection = editor.getSelection();
      if (selection.isEmpty()) {
        // 格式化整个文档
        monaco.languages.formatting.formatDocument(editor.getModel(), undefined, {})
          .then(edits => {
            editor.executeEdits('format', edits);
          })
          .catch(err => {
            console.error('格式化失败:', err);
            consoleOutput.value.push('❌ 代码格式化失败');
          });
      } else {
        // 格式化选中部分
        monaco.languages.formatting.format(editor.getModel(), selection, {})
          .then(edits => {
            editor.executeEdits('format', edits);
          })
          .catch(err => {
            console.error('格式化失败:', err);
            consoleOutput.value.push('❌ 代码格式化失败');
          });
      }
    };
    

    

    
    // 切换主题
    const toggleTheme = () => {
      isDarkTheme.value = !isDarkTheme.value
      if (editor) {
        editor.updateOptions({
          theme: isDarkTheme.value ? 'vs-dark' : 'vs'
        })
      }
    }
    
    // 切换Vim模式
    const toggleVimMode = () => {
      isVimMode.value = !isVimMode.value
      if (editor) {
        editor.updateOptions({
          keybindingProvider: isVimMode.value ? 'vim' : undefined
        })
      }
    }
    
    // 调整字体大小
    const increaseFontSize = () => {
      if (fontSize.value < 24) {
        fontSize.value += 1
        if (editor) {
          editor.updateOptions({ fontSize: fontSize.value })
        }
      }
    }
    
    const decreaseFontSize = () => {
      if (fontSize.value > 10) {
        fontSize.value -= 1
        if (editor) {
          editor.updateOptions({ fontSize: fontSize.value })
        }
      }
    }
    
    // 切换结果抽屉
    const toggleResult = () => {
      showResult.value = !showResult.value
    }
    
    // 自动检测代码语言
    const detectLanguage = (code) => {
      // 统计各语言特征出现次数
      const languageScores = {
        javascript: 0,
        python: 0,
        java: 0,
        cpp: 0,
        c: 0,
        csharp: 0,
        php: 0,
        ruby: 0,
        go: 0,
        rust: 0,
        html: 0,
        css: 0
      };
      
      // 语言特征模式
      const languagePatterns = {
        // JavaScript特征
        javascript: [
          /`[^`]*`/,
          /\bthis\./i,
          /\bconst\s+\w+/i,
          /\blet\s+\w+/i,
          /\bvar\s+\w+/i,
          /\bconsole\.log\(/i,
          /=>/,
          /\bfunction\s+\w+\s*\(/i,
          /\bdocument\.|\bwindow\./i,
          /\.querySelector\(/i,
          /\.getElementById\(/i
        ],
        // Python特征
        python: [
          /\bprint\s*\(/i,
          /\bdef\s+\w+\s*\(/i,
          /\bimport\s+\w+/i,
          /\bclass\s+\w+/i,
          /\bfor\s+\w+\s+in/i,
          /\bif\s+.+\s*:\s*$/im,
          /\bimport\s+\w+\s+as\s+\w+/i,
          /\bfrom\s+\w+\s+import/i,
          /\bexcept\b/i,
          /\bfinally\b/i,
          /\bwith\b/i,
          /\bas\s+\w+/i
        ],
        // Java特征
        java: [
          /\bpublic\s+static\s+void\s+main/i,
          /\bpublic\s+class\s+\w+/i,
          /\bSystem\.out\.print/i,
          /\bprivate|protected\s+(\w+\s+)*\w+/i,
          /\bpackage\s+\w+(\.\w+)*/i,
          /\bextends\s+\w+/i,
          /\bimplements\s+\w+/i,
          /\bnew\s+\w+\(/i
        ],
        // C++特征
        cpp: [
          /#include\s*<\w+>/,
          /using\s+namespace\s+std;/i,
          /std::\w+/,
          /\bint\s+main\s*\(/,
          /cout\s*<<|cin\s*>>/,
          /\bstd::cout\b/,
          /\bstd::endl\b/,
          /::/i
        ],
        // C特征
        c: [
          /#include\s*<\w+\.h>/,
          /#include\s*<c\w+>/,
          /\bprintf\s*\(/,
          /\bscanf\s*\(/,
          /\bvoid\s+main\s*\(/,
          /\bmalloc\s*\(/,
          /\bnullptr\b/i,
          /\bstruct\s+\w+/i
        ],
        // C#特征
        csharp: [
          /\bpublic\s+static\s+void\s+Main/i,
          /\bpublic\s+class\s+\w+/i,
          /\bConsole\.Write/i,
          /\busing\s+System;/i,
          /\bnamespace\s+\w+/i,
          /\bprivate|protected\s+(\w+\s+)*\w+/i,
          /\bvar\s+\w+\s*=/i,
          /\bbool\b/i
        ],
        // PHP特征
        php: [
          /<\?php/,
          /\$\w+/,
          /\becho\b/i,
          /\brequire_once\b/i,
          /\bfunction\s+\w+/i,
          /\bclass\s+\w+/i,
          /\bnamespace\s+\w+/i,
          /\bpublic|private|protected\s+function/i
        ],
        // Ruby特征
        ruby: [
          /\bdef\s+\w+/i,
          /\bclass\s+\w+/i,
          /\bmodule\s+\w+/i,
          /\bend\b/i,
          /\bputs\b/i,
          /\bprint\b/i,
          /\belsif\b/i,
          /\brequire\s+['"](\w+)['"]/i
        ],
        // Go特征
        go: [
          /package\s+\w+/i,
          /import\s+\(/,
          /func\s+main\s*\(/i,
          /fmt\.Print/i,
          /\bvar\s+\w+/i,
          /\bfunc\s+\w+/i,
          /\bstruct\s*{/i,
          /\bgo\s+\w+/i
        ],
        // Rust特征
        rust: [
          /fn\s+main\s*{/i,
          /let\s+mut\s+\w+/i,
          /println!\s*\(/i,
          /let\s+\w+/i,
          /fn\s+\w+/i,
          /struct\s+\w+/i,
          /impl\s+\w+/i,
          /use\s+\w+/i
        ],
        // HTML特征
        html: [
          /<html/i,
          /<head/i,
          /<body/i,
          /<div/i,
          /<span/i,
          /<script/i,
          /<style/i,
          /<!DOCTYPE html>/i
        ],
        // CSS特征
        css: [
          /\{[^}]*\}/,
          /:\s*[^;]+;/,
          /#[a-zA-Z0-9-_]+/,
          /\.[a-zA-Z0-9-_]+/,
          /@media\s+/i,
          /@keyframes/i,
          /@import\s+/i,
          /\bdisplay:\s*(block|inline|flex|grid)/i
        ]
      };
      
      // 计算各语言特征得分
      Object.entries(languagePatterns).forEach(([language, patterns]) => {
        patterns.forEach(pattern => {
          if (pattern.test(code)) languageScores[language]++;
        });
      });
      

      
      // 找出得分最高的语言
      let highestScore = 0;
      let detectedLanguage = 'javascript'; // 默认语言
      
      Object.entries(languageScores).forEach(([language, score]) => {
        if (score > highestScore) {
          highestScore = score;
          detectedLanguage = language;
        }
      });
      
      return detectedLanguage;
    };

    // 提取错误行号
    const extractErrorLine = (errorMessage) => {
      // 尝试从错误信息中提取行号
      const lineMatch = errorMessage.match(/line (\d+)|第(\d+)行|at line (\d+)/i);
      if (lineMatch) {
        return parseInt(lineMatch[1] || lineMatch[2] || lineMatch[3], 10) - 1; // 转为0-based索引
      }
      return -1;
    }
    
    // AI错误翻译功能
    const translateError = async (errorMessage, language) => {
      try {
        // 这里我们模拟AI翻译功能，实际项目中应该调用真实的AI服务API
        let translation = '';
        let solution = '';
        let fixedCode = userCode.value;
        
        // 根据不同的语言和错误类型生成对应的中文解释和修复建议
        if (errorMessage.includes('SyntaxError') || errorMessage.includes('语法错误') || 
            errorMessage.includes('ParseError') || errorMessage.includes('解析错误')) {
          translation = '这是一个语法错误，代码中存在语法结构问题，导致解析器无法正确理解。';
          solution = '请检查代码的语法结构，确保所有括号、引号、分号等符号都正确匹配和使用。';
          
          // 语言特定的语法错误建议
          if (language === 'python') {
            if (errorMessage.includes('IndentationError')) {
              translation = '这是一个Python缩进错误，Python使用缩进来表示代码块。';
              solution = '请检查代码的缩进，确保使用一致的空格（通常是4个空格）或制表符，并且代码块的缩进级别正确。';
            }
          } else if (language === 'java' || language === 'cpp' || language === 'c' || language === 'csharp') {
            if (errorMessage.includes('expected')) {
              solution += ' 在Java/C++/C/C#中，每条语句通常需要以分号结束，检查是否缺少分号。';
            }
          } else if (language === 'html') {
            if (errorMessage.includes('unclosed')) {
              translation = 'HTML标签未正确闭合。';
              solution = '请检查所有HTML标签，确保每个开始标签都有对应的结束标签。';
            }
          }
          
          // 通用错误模式
          if (errorMessage.includes('unexpected end of input')) {
            translation += ' 看起来代码可能缺少闭合的括号或大括号。';
            solution += ' 请检查代码末尾是否缺少闭合的大括号、中括号或小括号。';
          }
        } else if (errorMessage.includes('ReferenceError') || errorMessage.includes('引用错误') ||
                   errorMessage.includes('undefined') || errorMessage.includes('未定义')) {
          translation = '这是一个引用错误，代码中引用了未定义的变量或函数。';
          solution = '请检查变量或函数名是否拼写错误，或者在使用前确保其已经被定义。';
          
          if (language === 'javascript') {
            solution += ' 在JavaScript中，请检查变量是否使用了正确的声明方式（var/let/const）。';
          } else if (language === 'python') {
            solution += ' 在Python中，变量在使用前必须赋值，并且区分大小写。';
          }
        } else if (errorMessage.includes('TypeError') || errorMessage.includes('类型错误')) {
          translation = '这是一个类型错误，对错误类型的数据执行了不支持的操作。';
          solution = '请检查数据类型，确保对正确的数据类型执行相应的操作。';
          
          if (language === 'java' || language === 'csharp') {
            solution += ' 在Java/C#中，请确保类型转换正确。';
          }
        } else if (errorMessage.includes('NameError') || errorMessage.includes('名称错误')) {
          translation = '在Python中，这表示尝试使用一个未定义的变量或函数名。';
          solution = '请检查变量名是否拼写错误，或者在使用前确保已定义。Python中变量名区分大小写。';
        } else if (errorMessage.includes('CompilationError') || errorMessage.includes('编译错误')) {
          translation = '代码在编译阶段出现错误，无法生成可执行文件。';
          solution = '请仔细检查编译器提示的错误信息，修复语法或语义错误。';
          
          if (language === 'java') {
            solution += ' 检查类名是否与文件名匹配，主方法签名是否正确。';
          } else if (language === 'cpp' || language === 'c') {
            solution += ' 检查头文件包含是否完整，函数声明和定义是否匹配。';
          }
        } else {
          translation = '代码执行时出现了错误。';
          solution = `请仔细检查${getLanguageName(language)}代码，修复其中的问题后重试。`;
        }
        
        return { translation, solution, fixedCode };
      } catch (e) {
        console.error('翻译错误失败:', e);
        return {
          translation: '无法翻译错误信息',
          solution: '请自行分析错误信息',
          fixedCode: userCode.value
        };
      }
    }
    
    // 更新编辑器错误标记（简化版）
    const updateEditorMarkers = (errorLine, errorMessage) => {
      // 在简单的textarea中，我们只记录错误信息
      editorMarkers.value = [{
        lineNumber: errorLine,
        message: errorMessage,
        severity: 8 // Error severity
      }];
      
      // 在控制台输出错误信息
      console.log(`错误在第 ${errorLine + 1} 行: ${errorMessage}`);
    }
    
    // 应用修复建议
    const applyFix = () => {
      if (errorInfo.value.fixedCode) {
        setEditorCode(errorInfo.value.fixedCode);
        showErrorDrawer.value = false;
        // 清除错误标记
        if (model) {
          monaco.editor.setModelMarkers(model, 'owner', [])
        }
      }
    }
    
    // 运行代码
    const runCode = async () => {
      try {
        const { api } = await import('../api/api.js')
        
        const code = getCurrentCode();
        const selectedLanguage = codeLanguage.value;
        
        if (!code.trim()) {
          consoleOutput.value.push('⚠️ 代码为空，无法执行');
          return;
        }
        
        consoleOutput.value = [`🚀 正在执行 ${selectedLanguage} 代码...`]
        
        // 清除之前的错误标记
        showErrorDrawer.value = false;
        
        // 清除编辑器中的错误标记
        if (model) {
          monaco.editor.setModelMarkers(model, 'owner', [])
        }
        
        const result = await api.executeCode({ language: selectedLanguage, code: code, input: '' })
        
        // 显示执行统计信息
        if (result.stats) {
          const statsInfo = `📊 统计: ${result.stats.language} | ${result.stats.codeLength}字符 | ${result.stats.executionTime}ms`;
          consoleOutput.value.push(statsInfo);
        }
        
        // 显示标准输出
        if (result.stdout) {
          consoleOutput.value.push('📋 标准输出:');
          result.stdout.split('\n').forEach(line => {
            if (line) consoleOutput.value.push(`  ${line}`);
          });
        }
        
        if (result.stderr) {
          // 处理错误信息
          const errorMessage = result.stderr;
          consoleOutput.value.push('❌ 错误输出:');
          result.stderr.split('\n').forEach(line => {
            if (line) consoleOutput.value.push(`  ${line}`);
          });
          
          // 提取错误行号
          const errorLine = extractErrorLine(errorMessage);
          
          // 翻译错误信息
          const { translation, solution, fixedCode } = await translateError(errorMessage, selectedLanguage);
          
          // 更新错误信息并显示抽屉
          errorInfo.value = {
            original: errorMessage,
            translation,
            solution,
            fixedCode,
            errorLine
          };
          
          // 更新编辑器错误标记
          if (model && errorLine >= 0) {
            monaco.editor.setModelMarkers(model, 'owner', [{
              startLineNumber: errorLine + 1,
              endLineNumber: errorLine + 1,
              startColumn: 1,
              endColumn: Number.MAX_SAFE_INTEGER,
              message: errorMessage,
              severity: monaco.MarkerSeverity.Error
            }])
            
            // 跳转到错误行
            editor.revealLineInCenter(errorLine + 1)
          }
          
          // 显示错误抽屉
          showErrorDrawer.value = true;
        }
        
        // 显示执行状态和时间
        const status = result.exitCode === 0 ? '✅ 执行成功' : '❌ 执行失败';
        const exitInfo = `🏁 ${status} (退出代码: ${result.exitCode}, 耗时: ${result.durationMs}ms)`;
        consoleOutput.value.push(exitInfo);
        
        // 自动滚动到控制台底部
        nextTick(() => {
          const consoleElement = document.querySelector('.console-output');
          if (consoleElement) {
            consoleElement.scrollTop = consoleElement.scrollHeight;
          }
        });
      } catch (e) {
        const errorMessage = e.message || '执行失败，请稍后重试';
        consoleOutput.value.push(`❌ 执行错误: ${errorMessage}`);
        
        // 处理捕获的错误
        const selectedLanguage = codeLanguage.value;
        translateError(errorMessage, selectedLanguage).then(({ translation, solution, fixedCode }) => {
          errorInfo.value = {
            original: errorMessage,
            translation,
            solution,
            fixedCode,
            errorLine: -1
          };
          
          showErrorDrawer.value = true;
        });
      }
    }
    
    // 发送标准输入
    const sendStdin = () => {
      if (stdinInput.value) {
        consoleOutput.value.push(`> ${stdinInput.value}`)
        // 这里模拟输入处理
        consoleOutput.value.push(`处理输入: ${stdinInput.value}`)
        stdinInput.value = ''
      }
    }
    
    // 清空控制台
    const clearConsole = () => {
      consoleOutput.value = []
    }
    
    // 保存代码到版本历史和本地文件
    const saveCode = () => {
      // 创建新的版本
      const newVersion = {
        code: getCurrentCode(),
        timestamp: new Date().toISOString(),
        language: codeLanguage.value
      }
      
      codeVersions.value.unshift(newVersion)
      
      // 限制版本数量为10个
      if (codeVersions.value.length > 10) {
        codeVersions.value = codeVersions.value.slice(0, 10)
      }
      
      // 保存到localStorage
      saveCodeVersions()
      
      // 保存到本地文件系统
      saveToLocalFile()
      
      consoleOutput.value.push('✅ 代码已保存')
    }
    
    // 保存代码到本地文件
    const saveToLocalFile = () => {
      try {
        // 创建Blob对象
        const blob = new Blob([getCurrentCode()], { type: 'text/plain' })
        
        // 创建下载链接
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        
        // 设置文件名，使用当前选择的语言对应的后缀
        const extensions = {
          javascript: 'js',
          python: 'py',
          java: 'java',
          cpp: 'cpp',
          c: 'c',
          csharp: 'cs',
          php: 'php',
          ruby: 'rb',
          go: 'go',
          rust: 'rs',
          html: 'html',
          css: 'css'
        }
        
        // 使用自定义文件名或默认名称
        const fileExtension = extensions[codeLanguage.value] || 'txt'
        let saveFileName = fileName.value
        
        // 如果文件名仍然是默认名称，添加时间戳使其更独特
        if (saveFileName.startsWith('untitled')) {
          const timestamp = new Date().toISOString().replace(/[:.]/g, '-')
          saveFileName = `code-${timestamp}.${fileExtension}`
        }
        
        a.href = url
        a.download = saveFileName
        
        // 触发下载
        document.body.appendChild(a)
        a.click()
        
        // 清理
        document.body.removeChild(a)
        URL.revokeObjectURL(url)
        
        consoleOutput.value.push(`📥 代码已下载为文件: ${saveFileName}`)
      } catch (error) {
        console.error('保存文件失败:', error)
        consoleOutput.value.push('❌ 下载文件失败，请重试')
      }
    }
    
    // 获取语言显示名称
    const getLanguageName = (languageCode) => {
      const languageNames = {
        javascript: 'JavaScript',
        python: 'Python',
        java: 'Java',
        cpp: 'C++',
        c: 'C',
        csharp: 'C#',
        php: 'PHP',
        ruby: 'Ruby',
        go: 'Go',
        rust: 'Rust',
        html: 'HTML',
        css: 'CSS'
      };
      return languageNames[languageCode] || languageCode;
    }
    
    // 恢复版本
    const restoreVersion = (index) => {
      const version = codeVersions.value[index]
      setEditorCode(version.code)
      codeLanguage.value = version.language
      updateLanguage()
      
      showVersionHistory.value = false
      consoleOutput.value.push(`✅ 已恢复到版本 ${index + 1}`)
    }
    
    // 返回学习页
    const backToLearn = () => {
      // 使用router.back()返回上一页，而不是硬编码跳转到特定页面
      router.back()
    }
    
    // 格式化时间
    const formatTime = (timeStr) => {
      const date = new Date(timeStr)
      return date.toLocaleString()
    }
    
    // 获取输出样式类
    const getOutputClass = (line) => {
      if (line.startsWith('Error:')) return 'error'
      if (line.startsWith('Warning:')) return 'warning'
      if (line.startsWith('✅')) return 'success'
      if (line.startsWith('>')) return 'input-line'
      return ''
    }
    
    // 监听代码语言变化，更新文件名后缀
    watch(codeLanguage, (newLanguage) => {
      const extensions = {
        javascript: 'js',
        python: 'py',
        java: 'java',
        cpp: 'cpp',
        c: 'c',
        csharp: 'cs',
        php: 'php',
        ruby: 'rb',
        go: 'go',
        rust: 'rs',
        html: 'html',
        css: 'css'
      }
      fileName.value = `untitled.${extensions[newLanguage] || 'txt'}`
    })
    
    onMounted(async () => {
      // 从路由参数获取初始语言设置
      const initialLanguage = route.query.language;
      if (initialLanguage) {
        codeLanguage.value = initialLanguage;
      }
      
      // 加载支持的编程语言列表
      isLanguagesLoading.value = true;
      try {
        console.log('开始获取支持的编程语言列表...');
        console.log('API基础URL:', import.meta.env.VITE_APP_API_BASE_URL);
        const languagesData = await getSupportedLanguages();
        console.log('获取到的语言列表数据:', languagesData);
        supportedLanguages.value = languagesData.languages;
        console.log('设置后的supportedLanguages:', supportedLanguages.value);
        if (languagesData.default && !initialLanguage) {
          codeLanguage.value = languagesData.default;
        }
        
        // 确保至少有默认语言选项
        if (!supportedLanguages.value || supportedLanguages.value.length === 0) {
          console.log('语言列表为空，使用默认语言列表');
          supportedLanguages.value = ['javascript', 'python', 'java', 'c', 'html'];
        }
      } catch (error) {
          console.error('加载支持的编程语言列表失败:', error);
          console.error('错误详情:', JSON.stringify(error, Object.getOwnPropertyNames(error)));
          // 出现错误时设置默认语言列表
          console.log('出现错误，设置默认语言列表');
          supportedLanguages.value = ['javascript', 'python', 'java', 'c', 'html'];
        } finally {
          isLanguagesLoading.value = false;
        }
      
      // 初始化文件名
      updateFileName();
      
      // 加载历史版本
      loadCodeVersions();
      
      // 初始化编辑器
      await nextTick();
      await initMonacoEditor();
      
      // 配置Vim模式
      if (isVimMode.value) {
        await import('monaco-vim')
        editor.updateOptions({ keybindingProvider: 'vim' })
      }
    })
    
    onBeforeUnmount(() => {
      // 销毁编辑器实例
      if (editor) {
        editor.dispose()
      }
      if (model) {
        model.dispose()
      }
    })
    
    return {
      monacoContainer,
      codeLanguage,
      isDarkTheme,
      isVimMode,
      fontSize,
      fileName,
      showResult,
      consoleOutput,
      stdinInput,
      codeVersions,
      showVersionHistory,
      showErrorDrawer,
      errorInfo,
      isLanguagesLoading,
      supportedLanguages,
      toggleTheme,
      toggleVimMode,
      increaseFontSize,
      decreaseFontSize,
      toggleResult,
      runCode,
      sendStdin,
      clearConsole,
      saveCode,
      restoreVersion,
      backToLearn,
      formatTime,
      getOutputClass,
      applyFix,
      triggerCompletion,
      updateLanguage,
      formatCode
    }
  }
}
</script>

<style scoped>
.fullcode-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #000;
  color: #fff;
}

.fullcode-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #1e1e1e;
  border-bottom: 1px solid #333;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 20px;
}

.header-left h1 {
  margin: 0;
  font-size: 20px;
}

.editor-info {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

.language-select-container {
  display: inline-block;
  position: relative;
}

.language-select {
  padding: 5px 10px;
  background: #2d2d2d;
  color: #fff;
  border: 1px solid #444;
  border-radius: 4px;
  min-width: 120px;
}

.language-select-loading {
  padding: 5px 10px;
  background: #2d2d2d;
  color: #999;
  border: 1px solid #444;
  border-radius: 4px;
  min-width: 120px;
  text-align: center;
  font-size: 14px;
  animation: pulse 1.5s infinite;
}

.file-name {
  color: #999;
  font-size: 14px;
  white-space: nowrap;
}

.loading-indicator {
  font-size: 12px;
  color: #4caf50;
  display: flex;
  align-items: center;
  gap: 4px;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 15px;
}

.font-size-controls {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #2d2d2d;
  padding: 5px;
  border-radius: 4px;
}

.font-size {
  min-width: 35px;
  text-align: center;
}

.editor-container {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.editor-container.dark-theme {
  background: #1e1e1e;
}

.monaco-editor {
  flex: 1;
  overflow: auto;
  position: relative;
}

.code-textarea {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  resize: none;
  padding: 16px;
  font-family: Monaco, Menlo, "Ubuntu Mono", monospace;
  font-size: 14px;
  line-height: 1.5;
  background-color: #fff;
  color: #333;
  white-space: pre-wrap;
  word-wrap: break-word;
  tab-size: 2;
}

.dark-theme .code-textarea {
  background-color: #1e1e1e;
  color: #d4d4d4;
}

/* 代码补全面板样式 */
.completion-panel {
  position: absolute;
  background-color: #fff;
  border: 1px solid #ccc;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  max-height: 300px;
  overflow-y: auto;
  min-width: 200px;
  z-index: 1000;
  font-family: Monaco, Menlo, "Ubuntu Mono", monospace;
  font-size: 14px;
}

.dark-theme .completion-panel {
  background-color: #2d2d2d;
  border-color: #555;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.completion-item {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.completion-item:hover,
.completion-item.selected {
  background-color: #f0f0f0;
}

.dark-theme .completion-item:hover,
.dark-theme .completion-item.selected {
  background-color: #3e3e42;
}

.completion-icon {
  margin-right: 8px;
  font-size: 16px;
  width: 20px;
  text-align: center;
}

.completion-label {
  flex: 1;
  font-weight: 500;
  color: #333;
}

.dark-theme .completion-label {
  color: #d4d4d4;
}

.completion-detail {
  font-size: 12px;
  color: #666;
  margin-left: 8px;
}

.dark-theme .completion-detail {
  color: #999;
}

.editor-placeholder {
  width: 100%;
  height: 100%;
  padding: 20px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  color: #d4d4d4;
  outline: none;
  white-space: pre-wrap;
  overflow-wrap: break-word;
}

.result-drawer {
  background: #1e1e1e;
  border-top: 1px solid #333;
  transition: height 0.3s ease;
  overflow: hidden;
}

.result-drawer:not(.expanded) {
  height: 40px;
}

.result-drawer.expanded {
  height: 300px;
}

.drawer-handle {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #2d2d2d;
  cursor: pointer;
  user-select: none;
}

.drawer-handle:hover {
  background: #333;
}

.drawer-icon {
  font-size: 12px;
}

.drawer-content {
  height: calc(100% - 40px);
  display: flex;
  flex-direction: column;
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background: #2d2d2d;
  border-bottom: 1px solid #333;
}

.drawer-header h3 {
  margin: 0;
  font-size: 16px;
}

.drawer-actions {
  display: flex;
  gap: 10px;
}

.run-btn {
  background: #4CAF50;
  color: white;
}

.stdin-input {
  display: flex;
  gap: 10px;
  padding: 10px 15px;
  background: #2d2d2d;
  border-bottom: 1px solid #333;
}

.stdin-input .input {
  flex: 1;
  background: #1e1e1e;
  color: #fff;
  border: 1px solid #444;
}

.console-output {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.5;
}

.console-line {
  margin-bottom: 5px;
}

.console-line.error {
  color: #f44336;
}

.console-line.warning {
  color: #ff9800;
}

.console-line.success {
  color: #4caf50;
}

.console-line.input-line {
  color: #2196F3;
  font-style: italic;
}

.console-empty {
  color: #666;
  font-style: italic;
}

.version-history {
  position: absolute;
  bottom: 40px;
  right: 20px;
  z-index: 100;
}

.version-list {
  position: absolute;
  bottom: 100%;
  right: 0;
  background: #1e1e1e;
  border: 1px solid #333;
  border-radius: 4px;
  width: 300px;
  max-height: 300px;
  overflow-y: auto;
  margin-bottom: 10px;
}

.header-right .btn-completion {
  background-color: #673ab7;
  color: white;
  border-color: #673ab7;
}

.header-right .btn-completion:hover {
  background-color: #5e35b1;
  border-color: #5e35b1;
}

/* 轻量化工具包入口样式 */
.toolkit-entry {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
  text-align: center;
}

.toolkit-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  text-decoration: none;
  transition: transform 0.3s, box-shadow 0.3s;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.toolkit-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

.toolkit-desc {
  margin-top: 10px;
  color: #666;
  font-size: 14px;
}

.version-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-bottom: 1px solid #333;
}

.version-item:last-child {
  border-bottom: none;
}

.version-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.version-time {
  font-size: 12px;
  color: #999;
}

.version-index {
  font-size: 11px;
  color: #666;
}

.version-actions {
  display: flex;
  gap: 5px;
}

.btn-sm {
  padding: 4px 10px;
  font-size: 12px;
}

/* AI报错翻译抽屉样式 */
.error-drawer {
  position: fixed;
  bottom: 0;
  right: 0;
  width: 400px;
  max-height: 70vh;
  background: #1e1e1e;
  border-radius: 12px 12px 0 0;
  box-shadow: -2px -2px 20px rgba(0,0,0,0.15);
  z-index: 900;
  display: flex;
  flex-direction: column;
  color: #fff;
  border: 1px solid #333;
}

.error-drawer-header {
  padding: 15px 20px;
  border-bottom: 1px solid #333;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #2d2d2d;
}

.error-drawer-header h3 {
  margin: 0;
  font-size: 16px;
  color: #fff;
}

.error-drawer-content {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.error-drawer-content h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #66b1ff;
  font-size: 14px;
}

.original-error pre {
  background: #0f0f0f;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  color: #ff6b6b;
  margin-bottom: 20px;
}

.translated-error p,
.error-solution p {
  margin-bottom: 20px;
  line-height: 1.6;
  color: #d4d4d4;
}

.fix-btn {
  width: 100%;
  padding: 10px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.fix-btn:hover {
  background: #45a049;
}

/* 编辑器错误行高亮 */
.error-line {
  background-color: rgba(255, 0, 0, 0.2);
  border-left: 3px solid #ff4444;
}

/* Monaco Editor样式 */
.monaco-container {
  width: 100%;
  height: 100%;
  min-height: 400px;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
}

@media (max-width: 768px) {
  .fullcode-header {
    flex-direction: column;
    gap: 15px;
    align-items: stretch;
  }
  
  .header-left,
  .header-right {
    justify-content: space-between;
  }
  
  .header-right {
    flex-wrap: wrap;
  }
  
  .result-drawer.expanded {
    height: 250px;
  }
  
  .version-list {
    width: 250px;
    right: -10px;
  }
  
  .error-drawer {
    width: 100%;
    border-radius: 12px 12px 0 0;
  }
  
  .monaco-container {
    min-height: 300px;
  }
}
</style>
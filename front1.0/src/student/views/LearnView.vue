<template>
  <div class="learn-container">
    <!-- 顶部面包屑 -->
    <div class="breadcrumb">
      <router-link to="/student/books" class="breadcrumb-item">书架</router-link>
      <span class="breadcrumb-separator">/</span>
      <router-link :to="`/student/books/${bookId}`" class="breadcrumb-item">{{ book?.title }}</router-link>
      <span class="breadcrumb-separator">/</span>
      <span class="breadcrumb-item current">{{ currentSection?.title }}</span>
    </div>

    <!-- 视频浮层 -->
    <div v-if="showVideo" class="video-overlay">
      <div class="video-container">
        <div class="video-header">
          <h3>{{ currentSection?.title }} - 讲解视频</h3>
          <button class="close-btn" @click="showVideo = false">×</button>
        </div>
        <div class="video-content">
            <video 
              ref="videoPlayer" 
              :src="currentSection?.video_url || currentSection?.videoUrl || 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4'" 
              controls 
              style="width: 100%; height: auto;"
            >
              您的浏览器不支持HTML5视频播放
            </video>
          <div class="video-controls">
            <button class="btn">⏮️</button>
            <button class="btn">⏯️</button>
            <button class="btn">⏭️</button>
            <select v-model="videoSpeed" class="speed-select">
              <option value="0.75">0.75x</option>
              <option value="1">1x</option>
              <option value="1.25">1.25x</option>
              <option value="1.5">1.5x</option>
              <option value="2">2x</option>
            </select>
            <label class="checkbox-label">
              <input type="checkbox" v-model="showSubtitles"> 字幕
            </label>
          </div>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-layout" ref="mainLayoutRef">
      <!-- 章节列表侧边栏（可拖动调整宽度） -->
      <div 
        class="chapter-list-sidebar"
        :style="{ width: sidebarWidth + 'px' }"
      >
      <ChapterList 
        :chapters="getAllSections" 
        :current-section-id="currentSection?.id"
        :bookId="bookId"
      />
    </div>

      <!-- 中间拖动手柄 -->
      <div 
        class="sidebar-resize-handle"
        @mousedown="startSidebarResize"
      ></div>

    <!-- 1. 内容区 -->
    <div class="chapter-list-container">
      <div class="content-area">
        <div class="section-header">
          <h1>{{ currentSection?.title }}</h1>
          <div class="section-actions">
            <button v-if="currentSection?.type === 'video' || currentSection?.video_url || currentSection?.hasVideo" class="btn btn-primary" @click="showVideo = true">
              🎥 视频教学
            </button>
            <button v-if="currentSection?.type === 'practice'" class="btn btn-primary" @click="showPractice = true; loadPractice()">
              💡 开始练习
            </button>
            <button class="btn btn-primary" @click="openCodeSandbox">
              ⌨️ 代码沙盒
            </button>
          </div>
        </div>

        <div class="markdown-content">
          <!-- 加载状态 -->
          <div v-if="!currentSection" class="loading-content">
            <p>正在加载章节信息...</p>
          </div>
          
          <!-- 章节内容显示 -->
          <div v-else class="content-preview" ref="contentRef">
            <!-- 移除重复的标题，只保留描述 -->
            <p class="section-description">{{ currentChapterContent?.description || currentSection.description || '本章内容' }}</p>
            
            <!-- Jupyter文档内容显示 -->
          <div class="jupyter-container">
            <div v-if="currentChapterContent">
              <!-- 使用辅助函数获取内容 -->
              <div v-if="getJupyterContent">
                <JupyterNotebook 
                  :initialContent="getJupyterContent"
                  :documentId="null"
                  :isReadOnly="false"
                  :language="codeLanguage"
                  :bookId="bookId?.toString()"
                  :chapterId="currentSection?.id?.toString()"
                  @text-selected="handleJupyterTextSelection"
                ></JupyterNotebook>
              </div>
              <!-- 如果都没有内容，显示提示信息 -->
              <div v-else>
                <div class="empty-content">
                  <p>⚠️  此章节尚未配置内容</p>
                  <p>您可以通过Jupyter笔记本界面添加文本和代码单元格。</p>
                </div>
              </div>
            </div>
            <div v-else>
              <div class="loading-content">
                <p>正在加载章节内容...</p>
              </div>
            </div>
          </div>
          
          <!-- 右键菜单 -->
          <div 
            v-if="showContextMenu" 
            class="context-menu" 
            :style="{
              left: `${contextMenuPos.x}px`,
              top: `${contextMenuPos.y}px`
            }"
          >
            <div class="menu-item" @click="handleAddHighlight" v-if="!isHighlighted">
              💡 添加高亮
            </div>
            <div class="menu-item" @click="handleRemoveHighlight" v-else>
              ❌ 取消高亮
            </div>
            <div class="menu-item" @click="handleCreateNote">
              📝 创建笔记
            </div>
          </div>
            
            <!-- 章节类型特定内容 -->
            <div v-if="currentSection.type === 'practice'" class="practice-tips">
              <h3>练习提示</h3>
              <p>请点击"开始练习"按钮进入练习界面。</p>
              <p>尝试回答题目问题，选择正确的答案。</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Jupyter笔记本已包含代码编辑和运行功能，不再需要单独的代码沙盒 -->
      <!-- 原代码区和结果区已移除 -->
      
      <!-- 可运行的Jupyter笔记本提供了完整的交互式体验 -->
      </div>
    </div>

    <!-- 练习题弹层 -->
    <div v-if="showPractice" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 1000; display: flex; align-items: center; justify-content: center;">
      <div style="background: white; padding: 40px; border-radius: 8px; max-width: 800px; width: 90%; max-height: 80vh; overflow-y: auto;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px;">
          <h3>练习题</h3>
          <button @click="showPractice = false" style="font-size: 24px; background: none; border: none; cursor: pointer;">×</button>
        </div>
        <div style="margin-bottom: 20px;">
          <div v-if="loadingPractice" class="loading-content">
            <p>正在加载练习题...</p>
          </div>
          <div v-else-if="practiceData" class="question-content">
            <!-- 简单调试显示 -->
            <div style="background: pink; padding: 10px; margin: 10px 0;">
              <p>practiceData存在: {{ !!practiceData }}</p>
              <p>题目数量: {{ practiceData.questions?.length || 0 }}</p>
              <p>第一题内容: {{ practiceData.questions?.[0]?.content }}</p>
            </div>
            <!-- 直接显示所有数据结构 -->
            <div style="background: yellow; padding: 20px; margin-bottom: 20px; font-size: 14px; white-space: pre-wrap; word-break: break-word;">
              <h3>调试数据:</h3>
              <pre>{{ debugData }}</pre>
            </div>
            
            <div class="practice-info">
              <span class="practice-type">{{ practiceData.title }}</span>
              <span class="practice-difficulty">{{ getDifficultyText(practiceData.difficulty) }}</span>
            </div>
            <p v-if="practiceData.description" class="practice-description">{{ practiceData.description }}</p>
            
            <!-- 测试硬编码题目 -->
            <div class="question-item">
              <div class="question-header">
                <span class="question-number">测试.</span>
                <span class="question-type-badge">选择题</span>
              </div>
              <p class="practice-question">这是一个测试题目，你能看到吗？</p>
              <div class="options">
                <label class="option-item">
                  <input type="radio" name="test_option" value="1">
                  <span class="option-content">测试选项1</span>
                </label>
                <label class="option-item">
                  <input type="radio" name="test_option" value="2">
                  <span class="option-content">测试选项2</span>
                </label>
              </div>
            </div>
            
            <!-- 循环显示多个问题 -->
            <div v-for="(question, index) in practiceData.questions" :key="index" style="border: 1px solid #ccc; padding: 20px; margin: 20px 0;">
              <h4>{{ index + 1 }}. {{ getQuestionTypeText(question.type) }}</h4>
              <!-- 调试信息 -->
              <div style="background: #f5f5f5; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                <p>调试信息:</p>
                <p>问题类型: {{ question.type }}</p>
                <p>问题内容: {{ question.content }}</p>
                <p>问题字段: {{ Object.keys(question).join(', ') }}</p>
                <p v-if="question.type === 'choice'">选项字段: {{ question.choice_options ? 'choice_options' : '未找到' }}</p>
                <p v-if="question.type === 'choice'">选项数量: {{ question.choice_options ? question.choice_options.length : 0 }}</p>
              </div>
              <p style="font-size: 18px; margin: 15px 0;">{{ question.content }}</p>
              
              <!-- 选择题 -->
              <div v-if="question.type === 'choice'">
                <div v-for="option in question.choice_options" :key="option.id" style="margin: 10px 0;">
                  <label>
                    <input type="radio" :name="`option_${index}`" :value="option.id" v-model="selectedOptions[index]">
                    {{ option.content }}
                  </label>
                </div>
              </div>
              
              <!-- 填空题 -->
              <div v-else-if="question.type === 'fill'" class="fill-blanks">
                <div v-for="blank in question.fill_blanks" :key="blank.id" class="blank-item">
                  <label class="blank-label">{{ blank.prompt }}</label>
                  <input 
                    type="text" 
                    class="blank-input" 
                    :placeholder="blank.placeholder || '请输入答案'" 
                    v-model="blankAnswers[index][blank.id]"
                  >
                </div>
              </div>
              
              <!-- 代码补全题 -->
              <div v-else-if="question.type === 'code_completion'" class="code-completion">
                <div class="code-template">
                  <pre><code>{{ question.code_template }}</code></pre>
                </div>
                <textarea 
                  class="code-input" 
                  v-model="userCodes[index]" 
                  :placeholder="'请补全代码...'"
                  rows="10"
                ></textarea>
              </div>
              
              <!-- 判断题 -->
              <div v-else-if="question.type === 'true_false'">
                <label style="margin: 10px;">
                  <input type="radio" :name="`option_${index}`" :value="true" v-model="selectedOptions[index]">
                  正确
                </label>
                <label style="margin: 10px;">
                  <input type="radio" :name="`option_${index}`" :value="false" v-model="selectedOptions[index]">
                  错误
                </label>
              </div>
              
              <!-- 编程题 -->
              <div v-else-if="question.type === 'programming'" class="programming">
                <div v-if="question.code_template" class="code-template">
                  <pre><code>{{ question.code_template }}</code></pre>
                </div>
                <textarea 
                  class="code-input" 
                  v-model="userCodes[index]" 
                  :placeholder="'请编写代码...'"
                  rows="15"
                ></textarea>
                <div v-if="question.test_cases && question.test_cases.length > 0" class="test-cases">
                  <h5>测试用例</h5>
                  <div v-for="(testCase, tcIndex) in question.test_cases" :key="tcIndex" class="test-case">
                    <span class="test-case-label">用例 {{ tcIndex + 1 }}:</span>
                    <span class="test-case-input">输入: {{ JSON.stringify(testCase.input_data) }}</span>
                    <span class="test-case-output">期望输出: {{ JSON.stringify(testCase.expected_output) }}</span>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="submitResult" class="submit-result" :class="{ success: submitResult.success, error: !submitResult.success }">
              <p>{{ submitResult.message }}</p>
              <div v-if="submitResult.details" class="result-details">
                <pre>{{ JSON.stringify(submitResult.details, null, 2) }}</pre>
              </div>
            </div>
          </div>
          <div v-else class="no-practice">
            <p>该章节暂无练习题</p>
          </div>
          <div class="practice-actions">
            <button class="btn" @click="submitAnswer" :disabled="!canSubmit">提交答案</button>
          </div>
        </div>
      </div>
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
      </div>
    </div>
    
    <!-- 术语词典弹窗 -->
    <div v-if="selectedTerm" class="term-tooltip" :style="termTooltipStyle">
      <div class="term-header">
        <h4>{{ selectedTerm.name }}</h4>
        <button class="term-close" @click="selectedTerm = null">×</button>
      </div>
      <div class="term-content">
        <p class="term-definition">{{ selectedTerm.definition }}</p>
        <div v-if="selectedTerm.example" class="term-example">
          <h5>示例：</h5>
          <pre>{{ selectedTerm.example }}</pre>
        </div>
      </div>
    </div>
    
    <!-- AI学习助手已移至App.vue中实现全局显示 -->

    <!-- 底部导航 -->
    <div class="bottom-nav">
      <button class="btn" @click="goToPreviousSection" :disabled="!hasPreviousSection">
        ← 上一节
      </button>
      
      <div class="progress-container">
        <div class="progress-info">
          <span>{{ currentSectionIndex + 1 }} / {{ totalSections }}</span>
          <span>{{ sectionProgress }}%</span>
        </div>
        <div class="progress-bar">
          <div class="progress-bar-fill" :style="{ width: sectionProgress + '%' }"></div>
        </div>
      </div>
      
      <button class="btn" @click="goToNextSection" :disabled="!hasNextSection">
        下一节 →
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api, API_BASE_URL } from '../api/api.js'
import JupyterNotebook from '../components/JupyterNotebook.vue'
import ChapterList from '../components/ChapterList.vue'

export default {
  name: 'LearnView',
  components: {
    JupyterNotebook,
    ChapterList
  },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const bookId = computed(() => Number(route.params.bookId))
    const sectionId = computed(() => Number(route.params.chapterId)) // 使用chapterId作为sectionId
    
    const book = ref(null)
    const currentChapter = ref(null)
    const currentSection = ref(null)
    const currentChapterContent = ref(null) // 存储从API获取的完整章节内容
    const renderedContent = ref('') // 存储渲染后的HTML内容
    const showVideo = ref(false)
    const showPractice = ref(false)
    
    // 练习题相关数据
    const practiceData = ref(null)
    const loadingPractice = ref(false)
    const selectedOptions = ref([])
    const blankAnswers = ref([])
    const userCodes = ref([])
    const submitResult = ref(null)
    
    const videoSpeed = ref('1')
    const showSubtitles = ref(true)
    const codeLanguage = ref('JavaScript')
    const consoleOutput = ref([]) // 控制台输出
    
    // 新增AI功能相关数据
    const showErrorDrawer = ref(false)
    const errorInfo = ref({
        original: '',
        translation: '',
        solution: ''
      })
    const selectedTerm = ref(null)
    const termTooltipStyle = ref({})
    // AI助手相关功能已移至App.vue中
    
    // 笔记高亮功能相关数据
    const selectedText = ref('')
    const showContextMenu = ref(false)
    const contextMenuPos = ref({ x: 0, y: 0 })
    const highlights = ref([])
    const contentRef = ref(null)
    const selectionRange = ref(null)
    const isHighlighted = ref(false)
    
    // 布局与侧边栏宽度控制
    const mainLayoutRef = ref(null)
    const sidebarWidth = ref(280) // 默认侧边栏宽度
    const isResizingSidebar = ref(false)
    const sidebarMinWidth = 180
    const sidebarMaxWidth = 480
    const sidebarResizeHandler = ref(null)
    const sidebarStopHandler = ref(null)

    const startSidebarResize = (event) => {
      // 移动端使用上下布局，不启用左右拖动
      if (window.innerWidth <= 768) {
        return
      }

      isResizingSidebar.value = true

      const moveHandler = (e) => {
        if (!isResizingSidebar.value) return
        const clientX = e.touches ? e.touches[0].clientX : e.clientX
        const layoutEl = mainLayoutRef.value
        if (!layoutEl) return
        const rect = layoutEl.getBoundingClientRect()
        const newWidth = clientX - rect.left
        if (newWidth >= sidebarMinWidth && newWidth <= sidebarMaxWidth) {
          sidebarWidth.value = newWidth
        }
      }

      const upHandler = () => {
        isResizingSidebar.value = false
        if (sidebarResizeHandler.value) {
          document.removeEventListener('mousemove', sidebarResizeHandler.value)
          document.removeEventListener('touchmove', sidebarResizeHandler.value)
        }
        if (sidebarStopHandler.value) {
          document.removeEventListener('mouseup', sidebarStopHandler.value)
          document.removeEventListener('touchend', sidebarStopHandler.value)
        }
        sidebarResizeHandler.value = null
        sidebarStopHandler.value = null
      }

      sidebarResizeHandler.value = moveHandler
      sidebarStopHandler.value = upHandler

      document.addEventListener('mousemove', moveHandler)
      document.addEventListener('mouseup', upHandler)
      document.addEventListener('touchmove', moveHandler, { passive: false })
      document.addEventListener('touchend', upHandler)

      event.preventDefault()
    }

    // 打开代码沙盒
    const openCodeSandbox = () => {
      router.push({
        name: 'StudentFullCode',
        query: {
          language: codeLanguage.value,
          bookId: bookId.value,
          chapterId: sectionId.value
        }
      })
    }
    
    // 术语词典数据
    const termDictionary = ref([
      {
        name: 'API',
        definition: '应用程序接口（Application Programming Interface），是软件系统提供给外部调用的一组定义、程序及协议的集合。',
        example: '// 使用天气API获取天气数据\nfetch("https://api.weather.com/v1/forecast")\n  .then(response => response.json())\n  .then(data => console.log(data))'
      },
      {
        name: '数据库',
        definition: '按照一定的数据结构组织、存储和管理数据的仓库，是计算机中存储、组织数据的一种方式。',
        example: '# 使用Python连接数据库\nimport sqlite3\nconn = sqlite3.connect("example.db")\ncursor = conn.cursor()'
      },
      {
        name: '循环',
        definition: '在编程中，循环是一种控制结构，允许重复执行一段代码多次，直到满足特定条件为止。',
        example: '// JavaScript中的for循环\nfor (let i = 0; i < 5; i++) {\n  console.log("这是第" + (i + 1) + "次循环");\n}'
      },
      {
        name: '函数',
        definition: '函数是一段执行特定任务的代码块，可以接受输入参数并返回结果，是程序的基本构建块。',
        example: '// 定义一个计算两数之和的函数\ndef add_numbers(a, b):\n    return a + b\n\n// 调用函数\nresult = add_numbers(3, 5)'
      },
      {
        name: '变量',
        definition: '变量是用于存储数据的命名容器，在程序执行过程中可以改变其值。',
        example: '// 在Python中定义变量\nname = "张三"\nage = 20\nheight = 1.75'
      }
    ])
    
    // Markdown渲染函数已移除，仅保留Jupyter文档支持
    
    // 代码沙盒功能已移除，不再需要复制代码功能
    
    // 获取章节详细内容 - 增强版，添加更详细的调试日志和确保content字段正确显示
    const fetchChapterContent = async (chapterId) => {
      try {
        console.log(`🔄 fetchChapterContent called for chapter: ${chapterId}`);
        
        // 修复API调用参数 - 只需要chapterId
        const chapterData = await api.getChapterContent(chapterId);
        console.log('📡 API Response received:', { 
          dataExists: !!chapterData,
          hasContent: chapterData?.content !== undefined,
          hasJupyterContent: chapterData?.jupyter_content !== undefined,
          contentType: chapterData?.content_type,
          hasDescription: chapterData?.description !== undefined
        });
        
        // 直接使用响应对象
        currentChapterContent.value = chapterData;
        
        // 详细记录content字段信息
        const contentInfo = {
          value: chapterData.content,
          type: typeof chapterData.content,
          isNull: chapterData.content === null,
          isEmpty: chapterData.content === '',
          isEmptyAfterTrim: chapterData.content?.trim() === '',
          length: chapterData.content?.length || 0
        };
        console.log('📖 Content field details:', contentInfo);
        
        // 详细记录description字段信息
        const descriptionInfo = {
          value: chapterData.description,
          type: typeof chapterData.description,
          isNull: chapterData.description === null,
          isEmpty: chapterData.description === '',
          isEmptyAfterTrim: chapterData.description?.trim() === '',
          length: chapterData.description?.length || 0
        };
        console.log('📝 Description field details:', descriptionInfo);
        
        // 直接将数据传递给JupyterNotebook组件
        // 组件会根据内容类型自动处理Markdown或JSON格式的单元格数据
        console.log('📝 章节内容已获取，准备通过JupyterNotebook组件渲染');
        console.log('📊 内容类型:', chapterData.content_type);
        console.log('📁 包含jupyter_content:', !!chapterData.jupyter_content);
        console.log('📄 包含content:', !!chapterData.content);
        
        // 设置代码语言
        codeLanguage.value = chapterData.language || 'javascript';
        console.log('🌐 设置语言:', codeLanguage.value);
        
        console.log('🎉 章节内容获取成功并渲染完成');
        return chapterData;
      } catch (error) {
        console.error('❌ 获取章节内容失败:', { 
          message: error.message,
          stack: error.stack?.slice(0, 200)
        });
        
        // 错误处理 - 增强版，提供更多诊断信息
        renderedContent.value = `<div style="color: red; padding: 20px; border: 1px solid red;">
          <h3>⚠️ 内容加载失败</h3>
          <p>错误信息: ${error.message || '未知错误'}</p>
          <p>章节ID: ${chapterId}</p>
          <p>请刷新页面重试，如果问题持续，请检查网络连接。</p>
        </div>`;
        
        return null;
      }
    }
    
    // 加载学习内容
    const loadContent = async () => {
      try {
        book.value = await api.getBookDetail(bookId.value)
        // 兼容：将章节作为小节使用
        findCurrentSection()
        
        // 获取章节详细内容
        if (currentSection.value && currentSection.value.id) {
          await fetchChapterContent(currentSection.value.id);
          
          // 检查URL查询参数，如果openPractice为true，延迟加载练习题
          // 这样可以确保章节内容已经加载完成，currentSection已经更新
          if (route.query.openPractice === 'true') {
            console.log('🔍 URL包含openPractice=true，准备加载练习题');
            // 使用setTimeout确保章节内容加载完成
            setTimeout(() => {
              showPractice.value = true;
            }, 100);
          }
        } else if (book.value) {
          // 如果没有当前章节，初始化默认数据
          await initializeDefaultData()
        }
        
      } catch (error) {
        console.error('加载内容失败:', error)
        // 即使加载失败也初始化默认数据，确保页面能正常显示
        await initializeDefaultData()
      }
    }
    
    // 确保章节存在视频URL（无则提供示例）
    const ensureVideoUrl = (chapter) => {
      if (!chapter) return
      if (!chapter.video_url && !chapter.videoUrl) {
        chapter.video_url = 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4'
      }
    }
    
    // 初始化默认数据（当API调用失败时使用）
    const initializeDefaultData = async () => {
      // 完整初始化book结构，确保有chapters数组
      if (!book.value) {
        book.value = {
          title: '默认教材',
          chapters: [
            {
              id: 1,
              title: '默认章节',
              hasVideo: true,
              video_url: 'https://sample-videos.com/video123/mp4/720/big_buck_bunny_720p_1mb.mp4',
              content: '# 欢迎使用数字教材系统\n\n这是一个默认章节内容，包含：\n\n- 基本的Markdown格式支持\n- 代码示例功能\n- 视频学习模块\n\n请尝试运行下面的示例代码：',
              code: '// 示例代码\nconsole.log("Hello, 数字教材系统!");\n\n// 尝试修改这段代码看看效果\nconst sum = (a, b) => {\n  return a + b;\n};\n\nconsole.log("5 + 3 =", sum(5, 3));',
              language: 'JavaScript'
            }
          ]
        }
      }
      
      // 设置默认章节
      if (!currentSection.value) {
        currentSection.value = book.value.chapters[0];
      }
      
      // 确保章节有详细内容
      if (currentSection.value && currentSection.value.id && book.value) {
        // 从默认book中获取章节内容
        const defaultContent = book.value.chapters.find(ch => ch.id === currentSection.value.id) || book.value.chapters[0];
        
        // 设置渲染内容
        if (defaultContent.content) {
          renderedContent.value = renderMarkdown(defaultContent.content);
        } else {
          renderedContent.value = '<p>本章暂无内容</p>';
        }
        
        // 设置语言
        if (defaultContent.language) {
          codeLanguage.value = (defaultContent.language || 'javascript');
        }
      }
    }
    
    // 聚合实际可学习的“节”列表：
    const getAllSections = computed(() => {
      const chapters = book.value?.chapters || []
      if (!chapters.length) return []
      // 若后端提供了章节下的sections，展开；否则直接把章节当作节
      if (chapters[0] && Array.isArray(chapters[0].sections)) {
        const flat = []
        chapters.forEach(ch => (ch.sections || []).forEach(sec => flat.push(sec)))
        // 按order字段升序排序
        return [...flat].sort((a, b) => (a.order || 0) - (b.order || 0))
      }
      // 按order字段升序排序
      return [...chapters].sort((a, b) => (a.order || 0) - (b.order || 0))
    })

    // 查找当前学习节
    const findCurrentSection = async () => {
      const sections = getAllSections.value
      if (!sections.length) return
      const found = sections.find(s => s.id === sectionId.value) || sections[0]
      currentSection.value = found
      ensureVideoUrl(currentSection.value)
      
      // 注意：内容获取逻辑已在 loadContent 函数中根据章节类型处理
      // 这里不再直接调用 fetchChapterContent 或 loadPractice
    }
    
    // 当前小节索引
    const currentSectionIndex = computed(() => {
      const sections = getAllSections.value
      if (!sections.length || !currentSection.value) return 0
      return sections.findIndex(s => s.id === currentSection.value.id)
    })
    
    // 总小节数
    const totalSections = computed(() => getAllSections.value.length)
    
    // 是否有上一节
    const hasPreviousSection = computed(() => {
      return currentSectionIndex.value > 0
    })
    
    // 是否有下一节
    const hasNextSection = computed(() => {
      return currentSectionIndex.value < totalSections.value - 1
    })
    
    // 小节进度
    const sectionProgress = computed(() => {
      const sections = getAllSections.value
      if (!sections.length) return 0
      const completed = sections.filter(s => s.status === 'completed').length
      return Math.round((completed / sections.length) * 100)
    })
    
    // 上一节
    const goToPreviousSection = () => {
      const sections = getAllSections.value
      if (hasPreviousSection.value) {
        const prevSection = sections[currentSectionIndex.value - 1]
        router.push({ name: 'StudentLearning', params: { bookId: bookId.value, chapterId: prevSection.id } })
      }
    }
    
    // 下一节
    const goToNextSection = () => {
      const sections = getAllSections.value
      if (hasNextSection.value) {
        const nextSection = sections[currentSectionIndex.value + 1]
        router.push({ name: 'StudentLearning', params: { bookId: bookId.value, chapterId: nextSection.id } })
      }
    }
    
    // 监听路由参数变化，重新加载内容
    watch(() => [bookId.value, sectionId.value], () => {
      loadContent();
    })
    
    // 展开代码块
    const expandCode = (event) => {
      // 实现代码块展开逻辑
      console.log('展开代码块')
    }
    
    // 运行代码 - 增强版，智能区分浏览器环境和Node.js环境代码
    // 代码沙盒功能已完全移除，用户可以直接在Jupyter笔记本中编写和运行代码
    // Jupyter笔记本提供了完整的交互式代码编辑和执行环境
    
    // 处理术语悬停
    const handleTermHover = (event, term) => {
      selectedTerm.value = term
      
      // 计算弹窗位置
      const rect = event.target.getBoundingClientRect()
      termTooltipStyle.value = {
        top: `${rect.bottom + 10}px`,
        left: `${rect.left}px`
      }
    }
    
    // AI助手消息发送功能已移至App.vue中
    
    // 清空控制台
    const clearConsole = () => {
      consoleOutput.value = []
    }
    
    // 复制控制台输出
    const copyConsole = () => {
      const text = consoleOutput.value.join('\n')
      navigator.clipboard.writeText(text).then(() => {
        consoleOutput.value.push('✅ 已复制到剪贴板')
      })
    }
    
    // 计算所有章节（用于章节列表组件）
    const allChapters = computed(() => {
      return getAllSections.value
    })
    
    // 打开全屏编辑
    const openFullCode = () => {
      router.push('/fullcode')
    }
    
    // 保存高亮
    const saveHighlight = async () => {
      if (!selectedText.value || !currentSection.value || !selectionRange.value) return
      
      try {
        // 应用高亮到DOM
        const highlightElement = document.createElement('span')
        highlightElement.className = 'highlight'
        highlightElement.dataset.highlightId = Date.now().toString()
        highlightElement.style.backgroundColor = 'rgba(255, 255, 0, 0.3)'
        
        // 复制范围以避免修改原始选择
        const range = selectionRange.value.cloneRange()
        range.surroundContents(highlightElement)
        
        // 保存高亮数据
        const highlight = {
          id: highlightElement.dataset.highlightId,
          text: selectedText.value,
          book: bookId.value,
          chapter: currentSection.value.id,
          content_location: 'content',
          created_at: new Date().toISOString(),
          element: highlightElement
        }
        
        // 添加到本地高亮列表
        highlights.value.push(highlight)
        
        // 调用API保存高亮（需要实现）
        // await api.saveHighlight(highlight)
        
        selectedText.value = ''
        selectionRange.value = null
      } catch (error) {
        console.error('保存高亮失败:', error)
      }
    }
    
    // 从高亮创建笔记
    const createNoteFromHighlight = async () => {
      if (!selectedText.value || !currentSection.value) return
      
      try {
        const note = {
          title: `来自《${book.value?.title || '未知书籍'}》的笔记`,
          content: `<blockquote>${selectedText.value}</blockquote>\n\n在章节：${currentSection.value.title}`,
          book: bookId.value,
          chapter: currentSection.value.id
        }
        
        console.log('从高亮创建笔记，发送数据:', note)
        const response = await api.createNote(note)
        console.log('从高亮创建笔记成功，返回数据:', response)
        
        selectedText.value = ''
        showContextMenu.value = false
        
        const event = new CustomEvent('open-notes-drawer', { detail: { noteId: response.id } })
        window.dispatchEvent(event)
      } catch (error) {
        console.error('创建笔记失败:', error)
        console.error('错误详情:', error.response?.data || error.message)
        alert(`创建笔记失败: ${error.response?.data?.detail || error.message || '未知错误，请重试'}`)
      }
    }
    
    // 处理来自JupyterNotebook组件的文本选中事件
    const handleJupyterTextSelection = (eventData) => {
      const { text, rect } = eventData
      
      if (text) {
        selectedText.value = text
      } else {
        selectedText.value = ''
        selectionRange.value = null
      }
    }
    
    // 提交答案
    const submitAnswer = async () => {
      if (!practiceData.value || !currentSection.value) return
      
      try {
        submitResult.value = null
        
        // 准备所有问题的答案数据
        const answerData = {
          questions: []
        }
        
        // 检查是否所有问题都已回答
        let allAnswered = true
        
        practiceData.value.questions.forEach((question, index) => {
          const questionAnswer = {
            index: index,
            type: question.type
          }
          
          // 根据题型准备答案
          switch (question.type) {
            case 'choice':
              if (selectedOptions.value[index] === null) {
                allAnswered = false
              }
              questionAnswer.option_id = selectedOptions.value[index]
              break
            
            case 'fill':
              if (!blankAnswers.value[index] || Object.keys(blankAnswers.value[index]).length === 0) {
                allAnswered = false
              }
              questionAnswer.answers = blankAnswers.value[index]
              break
            
            case 'code_completion':
            case 'programming':
              if (!userCodes.value[index] || !userCodes.value[index].trim()) {
                allAnswered = false
              }
              questionAnswer.code = userCodes.value[index]
              questionAnswer.language = practiceData.value.language
              break
          }
          
          answerData.questions.push(questionAnswer)
        })
        
        // 检查是否所有问题都已回答
        if (!allAnswered) {
          submitResult.value = {
            success: false,
            message: '请完成所有问题的回答'
          }
          return
        }
        
        // 提交答案到后端
        const response = await api.submitChapterPractice(currentSection.value.id, answerData)
        
        // 处理响应
        if (response.is_correct !== undefined) {
          // 选择题或填空题的直接结果
          submitResult.value = {
            success: response.is_correct,
            message: response.is_correct ? '🎉 恭喜你，答案正确！' : '❌ 答案不正确，请再试一次',
            details: response
          }
        } else if (response.test_results) {
          // 编程题的测试结果
          const passedCount = response.test_results.filter(t => t.passed).length
          const totalCount = response.test_results.length
          
          submitResult.value = {
            success: passedCount === totalCount,
            message: passedCount === totalCount 
              ? '🎉 所有测试用例都通过了！' 
              : `⚠️ 通过了 ${passedCount}/${totalCount} 个测试用例`,
            details: response
          }
        } else if (response.message) {
          // 其他类型的响应
          submitResult.value = {
            success: true,
            message: response.message,
            details: response
          }
        } else {
          submitResult.value = {
            success: true,
            message: '答案已提交',
            details: response
          }
        }
        
      } catch (error) {
        console.error('提交答案失败:', error)
        submitResult.value = {
          success: false,
          message: '提交失败：' + (error.message || '未知错误'),
          details: null
        }
      }
    }
    
    // 加载练习题数据
    const loadPractice = async () => {
      if (!currentSection.value) return
      
      try {
        loadingPractice.value = true
        submitResult.value = null
        selectedOptions.value = []
        blankAnswers.value = []
        userCodes.value = []
        
        // 测试：使用硬编码数据
        const mockData = {
          id: 1,
          title: '测试练习题集',
          description: '这是一个测试练习题集',
          difficulty: 2,
          questions: [
            {
              id: 1,
              type: 'choice',
              content: '计算机中最小的信息单位是？',
              choice_options: [
                { id: 1, content: '字节(Byte)', is_correct: false },
                { id: 2, content: '位(bit)', is_correct: true },
                { id: 3, content: '字(Word)', is_correct: false },
                { id: 4, content: '双字(Double Word)', is_correct: false }
              ],
              score: 2
            },
            {
              id: 2,
              type: 'true_false',
              content: '计算机的CPU主要由运算器和控制器组成。',
              correct_answer: true,
              score: 2
            }
          ]
        }
        
        // 直接将模拟数据赋值给practiceData
        practiceData.value = mockData
        console.log('✅ mockData已赋值给practiceData:', practiceData.value)
        
        // 为每个问题初始化答案数组
        if (practiceData.value && practiceData.value.questions) {
          console.log('📝 问题数组:', practiceData.value.questions)
          practiceData.value.questions.forEach((question, index) => {
            console.log(`❓ 问题${index + 1}:`, {
              type: question.type,
              content: question.content,
              hasContent: question.content !== undefined,
              fields: Object.keys(question)
            })
            
            // 选择题初始化
            if (question.type === 'choice') {
              console.log('🔘 选择题选项字段:', question.choice_options ? 'choice_options' : (question.options ? 'options' : '未找到选项字段'))
              selectedOptions.value[index] = null
            }
            // 判断题初始化
            else if (question.type === 'true_false') {
              console.log('✅ 判断题')
              selectedOptions.value[index] = null
            }
            // 填空题初始化
            else if (question.type === 'fill') {
              console.log('📝 填空题选项字段:', question.fill_blanks ? 'fill_blanks' : '未找到填空题字段')
              blankAnswers.value[index] = {}
            }
            // 代码题初始化
            else if ((question.type === 'code_completion' || question.type === 'programming') && question.code_template) {
              userCodes.value[index] = question.code_template
            } else if (question.type === 'code_completion' || question.type === 'programming') {
              userCodes.value[index] = ''
            }
          })
        }
        
        // 真实API调用（暂时注释）
        /*
        const data = await api.getChapterPractice(currentSection.value.id)
        console.log('🔍 练习题API返回数据:', JSON.stringify(data, null, 2))
        
        // 检查返回数据的结构
        console.log('📊 返回数据包含questions:', 'questions' in data)
        console.log('📊 questions类型:', Array.isArray(data.questions))
        console.log('📊 questions数量:', data.questions ? data.questions.length : 0)
        
        // 直接将数据赋值给practiceData
        practiceData.value = data
        */
        
        // 确认practiceData已更新
        console.log('✅ practiceData更新后:', {
          hasData: !!practiceData.value,
          hasQuestions: practiceData.value?.questions !== undefined,
          questionsCount: practiceData.value?.questions?.length || 0
        })
        
        // 为每个问题初始化答案数组
        if (practiceData.value && practiceData.value.questions) {
          console.log('📝 问题数组:', practiceData.value.questions)
          practiceData.value.questions.forEach((question, index) => {
            console.log(`❓ 问题${index + 1}:`, {
              type: question.type,
              content: question.content,
              hasContent: question.content !== undefined,
              fields: Object.keys(question)
            })
            
            // 选择题初始化
            if (question.type === 'choice') {
              console.log('🔘 选择题选项字段:', question.choice_options ? 'choice_options' : (question.options ? 'options' : '未找到选项字段'))
              selectedOptions.value[index] = null
            }
            // 判断题初始化
            else if (question.type === 'true_false') {
              console.log('✅ 判断题')
              selectedOptions.value[index] = null
            }
            // 填空题初始化
            else if (question.type === 'fill') {
              console.log('📝 填空题选项字段:', question.fill_blanks ? 'fill_blanks' : '未找到填空题字段')
              blankAnswers.value[index] = {}
            }
            // 代码题初始化
            else if ((question.type === 'code_completion' || question.type === 'programming') && question.code_template) {
              userCodes.value[index] = question.code_template
            } else if (question.type === 'code_completion' || question.type === 'programming') {
              userCodes.value[index] = ''
            }
          })
        }
        
        // 再次确认practiceData状态
        console.log('🎯 最终practiceData状态:', {
          data: practiceData.value,
          questions: practiceData.value?.questions
        })
        
      } catch (error) {
        console.error('加载练习题失败:', error)
        practiceData.value = null
      } finally {
        loadingPractice.value = false
      }
    }
    
    // 获取题型文本
    const getQuestionTypeText = (type) => {
      const typeMap = {
        'choice': '选择题',
        'true_false': '判断题',
        'fill': '填空题',
        'code_completion': '代码补全题',
        'programming': '编程题'
      }
      return typeMap[type] || '未知题型'
    }
    
    // 获取难度文本
    const getDifficultyText = (difficulty) => {
      const difficultyMap = {
        1: '简单',
        2: '中等',
        3: '困难'
      }
      return difficultyMap[difficulty] || '未知难度'
    }
    
    // 计算是否可以提交
    const canSubmit = computed(() => {
      if (!practiceData.value || !practiceData.value.questions) return false
      
      // 检查是否所有问题都已回答
      for (let i = 0; i < practiceData.value.questions.length; i++) {
        const question = practiceData.value.questions[i]
        
        switch (question.type) {
          case 'choice':
            if (selectedOptions.value[i] === null) return false
            break
          case 'fill':
            if (!blankAnswers.value[i] || Object.keys(blankAnswers.value[i]).length === 0) return false
            break
          case 'code_completion':
          case 'programming':
            if (!userCodes.value[i] || userCodes.value[i].trim().length === 0) return false
            break
        }
      }
      
      return true
    })
    
    // 计算调试数据的JSON字符串
    const debugData = computed(() => {
      if (!practiceData.value) return ''
      try {
        return JSON.stringify(practiceData.value, null, 2)
      } catch (error) {
        return 'JSON序列化错误: ' + error.message
      }
    })
    
    // 监听showPractice变化，自动加载练习题数据
    watch(showPractice, (newVal) => {
      if (newVal) {
        loadPractice()
      } else {
        practiceData.value = null
        submitResult.value = null
      }
    })
    
    // 监听practiceData变化，检查数据更新
    watch(practiceData, (newVal) => {
      console.log('🔄 practiceData变化监听:', {
        hasData: !!newVal,
        hasQuestions: newVal?.questions !== undefined,
        questionsCount: newVal?.questions?.length || 0,
        questions: newVal?.questions
      })
      
      if (newVal && newVal.questions) {
        // 检查每个问题的内容
        newVal.questions.forEach((question, index) => {
          console.log(`📝 问题${index + 1}内容检查:`, {
            content: question.content,
            hasContent: question.content !== undefined,
            contentLength: question.content?.length || 0,
            type: question.type,
            hasOptions: question.type === 'choice' ? (question.choice_options ? true : false) : undefined,
            optionsCount: question.type === 'choice' ? (question.choice_options ? question.choice_options.length : 0) : undefined
          })
        })
      }
    }, { deep: true })
    
    // 获取输出样式类
    const getOutputClass = (line) => {
      if (line.startsWith('Error:')) return 'error'
      if (line.startsWith('Warning:')) return 'warning'
      if (line.startsWith('✅')) return 'success'
      return ''
    }
    
    // 定义点击外部关闭菜单的事件处理函数
    const handleClickOutside = (event) => {
      if (showContextMenu.value && !event.target.closest('.context-menu')) {
        showContextMenu.value = false
      }
    }
    
    // 处理右键菜单事件
    const handleContextMenu = (event) => {
      const selection = window.getSelection()
      const text = selection.toString().trim()
      
      if (text && selection.rangeCount > 0) {
        event.preventDefault()
        selectedText.value = text
        selectionRange.value = selection.getRangeAt(0).cloneRange()
        
        // 检查选中的文本是否已经高亮
        const range = selection.getRangeAt(0)
        const startContainer = range.startContainer
        const endContainer = range.endContainer
        
        // 检查选区是否在高亮元素内
        let parentElement = startContainer.nodeType === Node.TEXT_NODE ? startContainer.parentElement : startContainer
        isHighlighted.value = parentElement.classList && parentElement.classList.contains('highlight')
        
        // 显示右键菜单
        contextMenuPos.value = {
          x: event.clientX,
          y: event.clientY
        }
        showContextMenu.value = true
      }
    }
    
    // 处理添加高亮
    const handleAddHighlight = async () => {
      await saveHighlight()
      showContextMenu.value = false
    }
    
    // 处理创建笔记
    const handleCreateNote = async () => {
      await createNoteFromHighlight()
      showContextMenu.value = false
    }
    
    // 处理取消高亮
    const handleRemoveHighlight = async () => {
      if (!selectionRange.value) return
      
      try {
        const range = selectionRange.value
        const startContainer = range.startContainer
        const endContainer = range.endContainer
        
        // 找到高亮元素
        let highlightElement = startContainer.nodeType === Node.TEXT_NODE ? startContainer.parentElement : startContainer
        
        // 如果是高亮元素，移除高亮
        if (highlightElement.classList && highlightElement.classList.contains('highlight')) {
          // 创建文档片段来移除高亮元素但保留内容
          const parent = highlightElement.parentNode
          while (highlightElement.firstChild) {
            parent.insertBefore(highlightElement.firstChild, highlightElement)
          }
          parent.removeChild(highlightElement)
          
          // 从高亮列表中移除
          const highlightId = highlightElement.dataset.highlightId
          if (highlightId) {
            highlights.value = highlights.value.filter(h => h.id !== highlightId)
          }
        }
        
        showContextMenu.value = false
        selectedText.value = ''
        selectionRange.value = null
        isHighlighted.value = false
      } catch (error) {
        console.error('取消高亮失败:', error)
      }
    }
    
    onMounted(() => {
      loadContent()
      
      // 添加点击外部关闭菜单事件
      document.addEventListener('click', handleClickOutside)
      // 添加右键菜单事件监听
      document.addEventListener('contextmenu', handleContextMenu)
    })
    
    // 监听路由查询参数变化，当openPractice参数为true时打开练习题弹窗
    watch(() => route.query.openPractice, (newVal) => {
      if (newVal === 'true') {
        showPractice.value = true
      }
    })
    
    onBeforeUnmount(() => {
      // 移除事件监听
      document.removeEventListener('click', handleClickOutside)
      document.removeEventListener('contextmenu', handleContextMenu)
    })
    
    // 获取Jupyter内容的辅助函数
    const getJupyterContent = computed(() => {
      if (currentChapterContent.value) {
        console.log('🔍 开始处理章节内容');
        
        // 优先使用merged_content字段，它已经包含了所有内容的统一表示
        const mergedContent = currentChapterContent.value.merged_content;
        
        if (mergedContent) {
          console.log('📝 优先处理merged_content字段');
          
          try {
            // 检查mergedContent的类型
            if (typeof mergedContent === 'object' && mergedContent !== null) {
              console.log('📊 merged_content已经是对象格式');
              
              // 检查是否是有效的Jupyter Notebook格式
              if (mergedContent.cells && Array.isArray(mergedContent.cells)) {
                console.log('✅ 成功识别为Jupyter Notebook格式，包含', mergedContent.cells.length, '个单元格');
                
                // 转换为JupyterNotebook组件期望的单元格数组格式
                const cellsArray = mergedContent.cells.map((cell, index) => ({
                  id: `cell_${index}_${cell.id || 0}`,
                  type: cell.cell_type === 'code' ? 'code' : 'markdown',
                  content: Array.isArray(cell.source) ? cell.source.join('\n') : cell.source || '',
                  language: mergedContent.metadata?.kernelspec?.language || currentChapterContent.value.language || 'python',
                  output: cell.outputs?.map(output => {
                    if (output.text) return Array.isArray(output.text) ? output.text.join('') : output.text;
                    if (output.data?.['text/plain']) return output.data['text/plain'];
                    return JSON.stringify(output);
                  }) || [],
                  isSystemGenerated: true
                }));
                
                console.log('✅ 转换为组件兼容格式完成');
                return JSON.stringify(cellsArray);
              } else if (Array.isArray(mergedContent)) {
                // 如果mergedContent直接是cells数组
                console.log('📊 merged_content是cells数组格式，包含', mergedContent.length, '个单元格');
                
                const cellsArray = mergedContent.map((cell, index) => ({
                  id: `cell_${index}_${cell.id || 0}`,
                  type: cell.cell_type === 'code' ? 'code' : 'markdown',
                  content: Array.isArray(cell.source) ? cell.source.join('\n') : cell.source || '',
                  language: currentChapterContent.value.language || 'python',
                  output: cell.outputs?.map(output => {
                    if (output.text) return Array.isArray(output.text) ? output.text.join('') : output.text;
                    if (output.data?.['text/plain']) return output.data['text/plain'];
                    return JSON.stringify(output);
                  }) || [],
                  isSystemGenerated: true
                }));
                
                console.log('✅ 转换为组件兼容格式完成');
                return JSON.stringify(cellsArray);
              }
            }
            
            // 如果mergedContent是字符串，尝试解析它
            if (typeof mergedContent === 'string' && mergedContent.trim()) {
              console.log('📊 merged_content是字符串格式，尝试解析');
              const parsed = JSON.parse(mergedContent);
              
              if (parsed.cells && Array.isArray(parsed.cells)) {
                console.log('✅ 成功解析为Jupyter Notebook格式，包含', parsed.cells.length, '个单元格');
                
                const cellsArray = parsed.cells.map((cell, index) => ({
                  id: `cell_${index}_${cell.id || 0}`,
                  type: cell.cell_type === 'code' ? 'code' : 'markdown',
                  content: Array.isArray(cell.source) ? cell.source.join('\n') : cell.source || '',
                  language: parsed.metadata?.kernelspec?.language || currentChapterContent.value.language || 'python',
                  output: cell.outputs?.map(output => {
                    if (output.text) return Array.isArray(output.text) ? output.text.join('') : output.text;
                    if (output.data?.['text/plain']) return output.data['text/plain'];
                    return JSON.stringify(output);
                  }) || [],
                  isSystemGenerated: true
                }));
                
                console.log('✅ 转换为组件兼容格式完成');
                return JSON.stringify(cellsArray);
              }
            }
          } catch (e) {
            console.log(`⚠️  merged_content解析失败: ${e.message}，尝试回退到旧的处理方式`);
          }
        }
        
        // 原有的内容处理逻辑保持不变，作为回退方案
        // 提取可能的内容源
        const content = currentChapterContent.value.content;
        const jupyterContent = currentChapterContent.value.jupyter_content;
        const code = currentChapterContent.value.code;
        
        console.log(`📊 内容来源检查: content=${!!content}, jupyterContent=${!!jupyterContent}, code=${!!code}`);
        
        // 增强版Unicode转义处理函数，专门解决嵌套转义、Unicode编码和控制字符问题
        const cleanUnicodeAndEscapes = (text) => {
          if (!text || typeof text !== 'string') return text;
          
          console.log('🔄 开始清理Unicode转义和嵌套转义');
          let result = text;
          let attempts = 0;
          const maxAttempts = 5; // 增加尝试次数以处理深度嵌套
          
          // 首先移除所有控制字符，这是解决Bad control character错误的关键
          // 移除ASCII控制字符（除了\t, \r, \n）
          result = result.replace(/[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]/g, '');
          // 移除零宽字符和其他Unicode控制字符
          result = result.replace(/[\u200B-\u200D\uFEFF\u0080-\u009F]/g, '');
          console.log('✅ 控制字符清理完成');
          
          while (attempts < maxAttempts) {
            try {
              // 检查是否包含需要处理的特殊字符
              if (result.includes('\\u') || result.includes('\\"') || result.includes('\\\\') || result.includes('\\n')) {
                console.log(`🔄 清理尝试 ${attempts + 1}/${maxAttempts}`);
                
                // 尝试解析JSON（这会自动处理Unicode转义和转义引号）
                const parsed = JSON.parse(`"${result.replace(/"/g, '\\"').replace(/\\/g, '\\\\')}"`);
                
                // 检查解析后的结果是否还有转义字符
                if (typeof parsed === 'string' && 
                    (parsed.includes('\\u') || parsed.includes('\\"') || parsed.includes('\\\\'))) {
                  result = parsed;
                  attempts++;
                } else {
                  // 转义已清理完成
                  result = parsed;
                  console.log('✅ Unicode转义和嵌套转义清理完成');
                  break;
                }
              } else {
                // 没有需要处理的转义字符
                console.log('✅ 无需额外清理');
                break;
              }
            } catch (e) {
              console.log(`⚠️  清理尝试 ${attempts + 1} 解析失败: ${e.message}`);
              // 尝试手动处理
              try {
                // 手动处理常见的转义序列
                result = result
                  .replace(/\\n/g, '\n')
                  .replace(/\\r/g, '\r')
                  .replace(/\\t/g, '\t')
                  .replace(/\\b/g, '') // 移除退格字符，它可能导致控制字符错误
                  .replace(/\\f/g, '') // 移除换页字符，它可能导致控制字符错误
                  .replace(/\\"/g, '"')
                  .replace(/\\'/g, "'")
                  .replace(/\\\\/g, '\\');
                
                // 尝试解码Unicode转义序列
                result = result.replace(/\\u([0-9a-fA-F]{4})/g, (_, hex) => {
                  return String.fromCharCode(parseInt(hex, 16));
                });
                
                console.log('✅ 手动清理转义字符成功');
                attempts++;
              } catch (innerE) {
                console.log(`❌ 手动清理失败: ${innerE.message}`);
                break;
              }
            }
          }
          
          return result;
        };
        
        // 尝试修复JSON格式错误的辅助函数
        const attemptToFixJSON = (jsonString) => {
          try {
            console.log('🔍 开始JSON修复流程');
            let fixed = jsonString;
            
            // 1. 移除前后空白字符
            fixed = fixed.trim();
            console.log('✂️  移除前后空白完成');
            
            // 2. 修复数组末尾多余逗号
            fixed = fixed.replace(/,\s*([}\]])/g, '$1');
            console.log('🔧 修复数组末尾多余逗号完成');
            
            // 3. 增强修复对象间缺少逗号
            // 修复类似 {"a":"b""c":"d"} 的问题
            fixed = fixed.replace(/"\s*}\s*"/g, '"},"');
            // 修复类似 {"a":"b"{"c":"d"} 的问题
            fixed = fixed.replace(/"\s*}\s*{"/g, '"},{"');
            console.log('🔧 修复对象间缺少逗号完成');
            
            // 4. 增强修复数组元素间缺少逗号
            // 修复类似 [{"a":"b""c":"d"}] 的问题
            fixed = fixed.replace(/"\s*}\s*"/g, '"},"');
            // 修复类似 [{"a":"b"{"c":"d"}] 的问题
            fixed = fixed.replace(/"\s*}\s*{"/g, '"},{"');
            // 新增: 修复数组元素之间缺少逗号，如 [1 2] 或 [{"a":1}{"b":2}]
            fixed = fixed.replace(/}\s*{/g, '},{');
            fixed = fixed.replace(/\]\s*\[/g, '],[');
            // 新增: 修复数值、布尔值、null等基本类型之间缺少逗号
            fixed = fixed.replace(/([}\]])\s+(["\d\[{])/g, '$1,$2');
            fixed = fixed.replace(/(["}\]])\s+(true|false|null|\d)/g, '$1,$2');
            // 新增: 更精确地修复数组元素间缺少逗号的情况
            // 处理类似 [123] 或 ["string"true] 的情况
            fixed = fixed.replace(/"\s+(?!\s*:)(["\d\[truefalse])/g, '",$1');
            // 处理基本类型之间缺少逗号的情况，如 [1true]、[truefalse] 等
            fixed = fixed.replace(/([0-9])(true|false|null|\{)/g, '$1,$2');
            fixed = fixed.replace(/(true|false|null)(true|false|null|\d|\{)/g, '$1,$2');
            // 处理位置22附近可能出现的特定格式问题
            fixed = fixed.replace(/\]\s*"/g, '],"');
            fixed = fixed.replace(/\}\s*"/g, '},"');
            console.log('🔧 修复数组元素间缺少逗号完成');
            
            // 5. 增强修复属性名和值之间的格式问题
            // 修复类似 {"cell_type":", "markdown" 的问题
            fixed = fixed.replace(/("[^"]*")\s*:\s*,\s*("[^"]*")/g, '$1:$2');
            // 修复类似 {"cell_type": "markdown", } 的问题
            fixed = fixed.replace(/("[^"]*")\s*:\s*([^,]+)\s*,\s*}/g, '$1:$2}');
            // 修复属性名后面缺少冒号的问题
            fixed = fixed.replace(/("[^"]*")\s+("[^"]*")/g, '$1: $2');
            console.log('🔧 修复属性名和值格式问题完成');
            
            // 6. 智能修复未转义引号
            // 只修复在字符串值中间的未转义引号，保留属性名中的引号
            fixed = fixed.replace(/(?:\{|,\s*)("[^"]*")\s*:\s*"([^"]*(?:\"|[^"\\])*?)"(?=\s*(?:,|\}))/g, 
              (match, propName, propValue) => {
                return `${propName}: "${propValue.replace(/"(?!\\")/g, '\"')}"`;
              }
            );
            console.log('🔧 修复未转义引号完成');
            
            // 7. 平衡括号计数
            const openBraces = (fixed.match(/{/g) || []).length;
            const closeBraces = (fixed.match(/}/g) || []).length;
            
            if (openBraces > closeBraces) {
              // 添加缺失的闭合括号
              fixed += '}'.repeat(openBraces - closeBraces);
              console.log('➕ 添加缺失的闭合括号完成');
            } else if (closeBraces > openBraces) {
              // 移除多余的闭合括号
              let count = 0;
              let i = 0;
              while (i < fixed.length) {
                if (fixed[i] === '{') count++;
                else if (fixed[i] === '}') {
                  if (count === 0) {
                    // 移除这个多余的括号
                    fixed = fixed.slice(0, i) + fixed.slice(i + 1);
                    continue;
                  }
                  count--;
                }
                i++;
              }
              console.log('➖ 移除多余的闭合括号完成');
            }
            
            // 8. 修复数组括号匹配
            const openBrackets = (fixed.match(/\[/g) || []).length;
            const closeBrackets = (fixed.match(/\]/g) || []).length;
            
            if (openBrackets > closeBrackets) {
              fixed += ']'.repeat(openBrackets - closeBrackets);
              console.log('➕ 添加缺失的闭合方括号完成');
            } else if (closeBrackets > openBrackets) {
              // 移除多余的方括号
              let count = 0;
              let i = 0;
              while (i < fixed.length) {
                if (fixed[i] === '[') count++;
                else if (fixed[i] === ']') {
                  if (count === 0) {
                    fixed = fixed.slice(0, i) + fixed.slice(i + 1);
                    continue;
                  }
                  count--;
                }
                i++;
              }
              console.log('➖ 移除多余的闭合方括号完成');
            }
            
            // 9. 修复冒号后缺少值的问题
            fixed = fixed.replace(/("[^"]*")\s*:\s*(,|})/g, '$1:""$2');
            console.log('🔧 修复冒号后缺少值的问题完成');
            
            // 10. 移除可能的首尾额外引号
            if (fixed.startsWith('"') && fixed.endsWith('"')) {
              fixed = fixed.slice(1, -1);
              console.log('✂️  移除首尾额外引号完成');
            }
            
            // 11. 特别处理Jupyter Notebook格式中的常见错误
            // 修复类似 {"cell_type":", "markdown" 的错误格式
            fixed = fixed.replace(/("cell_type")\s*:\s*,\s*("[^"]*")/g, '$1: $2');
            // 修复类似 {"metadata":, {} 的错误格式
            fixed = fixed.replace(/("metadata")\s*:\s*,\s*\{/g, '$1: {');
            // 修复类似 {"source":, [ 的错误格式
            fixed = fixed.replace(/("source")\s*:\s*,\s*\[/g, '$1: [');
            
            // 新增: 修复数组元素之间缺少逗号的问题（更精确的正则）
            fixed = fixed.replace(/(?!\{)(\})\s*(?!\}|\])/g, '},');
            fixed = fixed.replace(/(\])(?!,|\s*\])\s*(\[|"|\d|true|false|null)/g, '$1,$2');
            
            console.log('🔍 JSON修复流程完成');
            console.log('🔍 JSON修复后的预览:', fixed.length > 50 ? fixed.substring(0, 50) + '...' : fixed);
            return fixed;
          } catch (e) {
            console.error('❌ JSON修复过程中出错:', e);
            return jsonString;
          }
        };
        
        // 检查是否为有效的Jupyter Notebook格式
        const isJupyterNotebook = (data) => {
          return data && 
                 typeof data === 'object' && 
                 Array.isArray(data.cells) && 
                 data.cells.length > 0 &&
                 data.cells.every(cell => cell.cell_type && cell.source);
        };
        
        // 检查是否为有效的cells数组
        const isCellsArray = (data) => {
          return Array.isArray(data) && 
                 data.length > 0 && 
                 data.every(cell => cell.cell_type && cell.source);
        };
        
        // 生成组件兼容的单元格数组
        const generateCellsArray = (cells, metadata = null) => {
          const cellsArray = cells.map((cell, index) => ({
            id: `cell_${index}_${Date.now()}`,
            type: cell.cell_type === 'code' ? 'code' : 'markdown',
            content: Array.isArray(cell.source) ? cell.source.join('\n') : cell.source || '',
            language: metadata?.kernelspec?.language || 'python',
            output: cell.outputs?.map(output => {
              if (output.text) return Array.isArray(output.text) ? output.text.join('') : output.text;
              if (output.data?.['text/plain']) return output.data['text/plain'];
              return JSON.stringify(output);
            }) || [],
            isSystemGenerated: true
          }));
          
          console.log('✅ 转换为组件兼容格式完成');
          return JSON.stringify(cellsArray);
        };
        
        // 处理Jupyter Notebook内容
        const processJupyterContent = (rawContent) => {
          if (!rawContent) return null;
          
          console.log('🔍 处理可能的Jupyter内容');
          
          // 先清理内容中的Unicode转义和嵌套转义
          let cleaned = cleanUnicodeAndEscapes(rawContent);
          console.log(`📋 清理后内容类型: ${typeof cleaned}`);
          
          // 直接处理对象
          if (typeof cleaned === 'object' && cleaned !== null) {
            console.log('📊 直接处理对象类型');
            
            // 检查是否是cells数组
            if (isCellsArray(cleaned)) {
              console.log('✅ 成功识别为cells数组格式，包含', cleaned.length, '个单元格');
              
              // 转换为JupyterNotebook组件期望的单元格数组格式
              const cellsArray = cleaned.map((cell, index) => ({
                id: `cell_${index}_${Date.now()}`,
                type: cell.cell_type === 'code' ? 'code' : 'markdown',
                content: Array.isArray(cell.source) ? cell.source.join('\n') : cell.source || '',
                language: 'python', // 默认Python语言
                output: cell.outputs?.map(output => {
                  if (output.text) return Array.isArray(output.text) ? output.text.join('') : output.text;
                  if (output.data?.['text/plain']) return output.data['text/plain'];
                  return JSON.stringify(output);
                }) || [],
                isSystemGenerated: true
              }));
              
              console.log('✅ 转换为组件兼容格式完成');
              return JSON.stringify(cellsArray);
            }
          }
          
          // 确保处理的是字符串
          if (typeof cleaned !== 'string') {
            cleaned = JSON.stringify(cleaned);
          }
          
          try {
            // 尝试解析为JSON
            let jsonToParse = cleaned;
            let parsed;
            
            // 先尝试直接解析
            try {
              parsed = JSON.parse(jsonToParse);
              console.log('✅ JSON直接解析成功');
            } catch (firstParseError) {
              // 如果直接解析失败，尝试修复JSON格式
              console.log(`⚠️  首次解析失败，尝试修复JSON: ${firstParseError.message}`);
              jsonToParse = attemptToFixJSON(jsonToParse);
              console.log('🔄 已应用JSON修复策略');
              
              // 再次尝试解析修复后的JSON
              parsed = JSON.parse(jsonToParse);
              console.log('✅ 修复后JSON解析成功');
            }
            
            // 检查解析结果类型
            if (Array.isArray(parsed)) {
              console.log('📊 解析结果是数组格式');
              // 直接使用数组，不包装成对象
              if (isCellsArray(parsed)) {
                console.log('✅ 成功识别为cells数组格式，包含', parsed.length, '个单元格');
                return generateCellsArray(parsed);
              }
            } else if (typeof parsed === 'object' && parsed !== null) {
              console.log('📊 解析结果是对象格式');
            
              // 检查是否是有效的Jupyter Notebook格式
              if (isJupyterNotebook(parsed)) {
                console.log('✅ 成功识别为Jupyter Notebook格式，包含', parsed.cells.length, '个单元格');
                return generateCellsArray(parsed.cells, parsed.metadata);
              } else {
                // 检查对象中是否直接包含cell_type
                if (parsed.cell_type && parsed.source) {
                  console.log('✅ 对象本身是单个单元格，转换为单元素数组');
                  return generateCellsArray([parsed]);
                }
                console.log('❌ 解析成功但不是有效的Jupyter格式');
              }
            }
          } catch (e) {
            console.log(`❌ Jupyter内容解析失败: ${e.message}`);
            
            // 尝试直接将内容作为Markdown处理
            // 先清理可能的JSON标记
            let markdownContent = cleaned
              .replace(/^\"|\"$/g, '') // 移除首尾的引号
              .replace(/\\"/g, '"') // 修复转义引号
              .replace(/\\n/g, '\n') // 修复转义换行
              .replace(/\\r/g, '\r')
              .replace(/\\t/g, '\t')
              .replace(/\\\\/g, '\\');
              
            console.log('📄 尝试作为Markdown内容返回');
            return markdownContent;
          }
          
          return null;
        };
        
        // 优先处理jupyter_content字段
        if (jupyterContent) {
          console.log('📝 处理jupyter_content字段');
          const processed = processJupyterContent(jupyterContent);
          if (processed) {
            console.log('✅ jupyter_content处理成功');
            return processed;
          }
        }
        
        // 然后处理content字段
        if (content) {
          console.log('📝 处理content字段');
          const processed = processJupyterContent(content);
          if (processed) {
            console.log('✅ content处理成功');
            return processed;
          }
        }
        
        // 如果JSON解析都失败，尝试整合内容并确保正确处理Unicode转义
        console.log('📝 尝试整合content和code字段');
        let combinedContent = '';
        
        // 添加章节文本内容
        if (content) {
          let cleanContent = cleanUnicodeAndEscapes(content);
          if (typeof cleanContent !== 'string') {
            cleanContent = String(cleanContent);
          }
          console.log('📝 添加清理后的content内容');
          combinedContent += cleanContent;
        }
        
        // 添加章节代码内容（如果存在），作为代码块
        if (code && code.trim() !== '') {
          const language = currentChapterContent.value.language || 'python';
          // 确保在代码块前添加换行，避免与前面的内容合并
          if (combinedContent) {
            combinedContent += '\n\n';
          }
          // 添加代码块标记和语言
          combinedContent += `\n\`\`\`${language}\n${cleanUnicodeAndEscapes(code).trim()}\n\`\`\``;
          console.log('📝 添加code内容为代码块');
        }
        
        // 如果有整合的内容，返回它
        if (combinedContent.trim() !== '') {
          console.log('📤 返回整合后的内容');
          return combinedContent;
        }
      }
      
      console.log('📭 无内容可返回');
      return null;
    })

    return {
      bookId,
      sectionId,
      book,
      currentChapter,
      currentSection,
      currentChapterContent,
      renderedContent,
      showVideo,
      showPractice,
      videoSpeed,
      showSubtitles,
      codeLanguage,
      showErrorDrawer,
      errorInfo,
      selectedTerm,
      termTooltipStyle,
      termDictionary,
      currentSectionIndex,
      totalSections,
      hasPreviousSection,
      hasNextSection,
      sectionProgress,
      goToPreviousSection,
      goToNextSection,
      handleTermHover,
      initializeDefaultData,
      getJupyterContent,
      submitAnswer,
      openCodeSandbox,
      getAllSections,
      // 练习题相关变量和函数
      practiceData,
      loadingPractice,
      selectedOptions,
      blankAnswers,
      userCodes,
      submitResult,
      loadPractice,
      getQuestionTypeText,
      getDifficultyText,
      canSubmit,
      debugData,
      // 笔记高亮功能相关变量和函数
      selectedText,
      showContextMenu,
      contextMenuPos,
      isHighlighted,
      saveHighlight,
      createNoteFromHighlight,
      handleAddHighlight,
      handleCreateNote,
      handleRemoveHighlight,
      contentRef,
      handleJupyterTextSelection,
      // 布局与侧边栏拖动
      mainLayoutRef,
      sidebarWidth,
      startSidebarResize
      // AI助手相关变量已移至App.vue中
    }
  }
}
</script>

<style scoped>
.learn-container {
  padding: 20px 0;
}

/* AI助手样式已移至App.vue中 */

.assistant-input .btn:hover {
  background: #66b1ff;
}

.assistant-input .btn:active {
  background: #3a8ee6;
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

.main-layout {
  margin-bottom: 20px;
  min-height: calc(100vh - 200px);
  display: flex;
}

.chapter-list-sidebar {
  width: 280px;
  background: #f5f7fa;
  border-right: 1px solid #e4e7ed;
  padding: 20px;
  overflow-y: auto;
  flex-shrink: 0;
}

/* 章节列表与内容区之间的可拖动分隔条 */
.sidebar-resize-handle {
  width: 6px;
  cursor: col-resize;
  background: #e0e0e0;
  flex-shrink: 0;
  position: relative;
}

.sidebar-resize-handle::before {
  content: '';
  position: absolute;
  top: 20%;
  bottom: 20%;
  left: 50%;
  width: 2px;
  transform: translateX(-50%);
  background: #c0c4cc;
  border-radius: 1px;
}

.sidebar-resize-handle:hover {
  background: #d0d7e2;
}

.sidebar-resize-handle:active {
  background: #409EFF;
}

.chapter-list-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 30px;
  overflow-y: auto;
  flex: 1;
}

@media (max-width: 768px) {
  .main-layout {
    flex-direction: column;
  }
  
  .chapter-list-sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid #e4e7ed;
    max-height: 300px;
  }

  /* 移动端采用上下布局，不显示左右拖动手柄 */
  .sidebar-resize-handle {
    display: none;
  }
}

.content-area {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 30px;
  overflow-y: auto;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
}

.section-header h1 {
  font-size: 24px;
  margin: 0;
  flex: 1;
}

.section-actions {
  display: flex;
  gap: 10px;
}

.markdown-content {
  line-height: 1.8;
}

.content-preview h2 {
  margin: 25px 0 15px 0;
  font-size: 20px;
  color: #333;
}

.content-preview p {
  margin-bottom: 15px;
  color: #666;
}

.content-preview ul {
  margin-bottom: 20px;
}

/* 代码块样式已通过JupyterNotebook组件提供 */
/* 移除了所有代码沙盒相关的样式类 */

.bottom-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.progress-container {
  flex: 1;
  max-width: 400px;
  margin: 0 30px;
}

.progress-info {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  margin-bottom: 8px;
  color: #666;
}

.video-overlay,
.practice-overlay {
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
}

.video-container,
.practice-container {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.video-header,
.practice-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.video-header h3,
.practice-header h3 {
  margin: 0;
  font-size: 18px;
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
  
  .btn {
    background-color: #f5f7fa;
    color: #606266;
    border: 1px solid #dcdfe6;
    padding: 6px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    transition: all 0.3s;
  }
  
  .btn:hover {
    color: #409eff;
    border-color: #c6e2ff;
    background-color: #ecf5ff;
  }
  
  .btn.btn-primary {
    background-color: #409eff;
    color: #fff;
    border-color: #409eff;
  }
  
  /* 菜单项样式 */
  .menu-item {
    padding: 10px 15px;
    cursor: pointer;
    font-size: 14px;
    color: #606266;
    transition: all 0.3s;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  
  .menu-item:hover {
    background-color: #ecf5ff;
    color: #409eff;
  }
  
  /* 高亮样式 */
  .highlight {
    background-color: rgba(255, 255, 0, 0.3);
    border-radius: 2px;
    cursor: pointer;
    transition: background-color 0.3s;
  }
  
  .highlight:hover {
    background-color: rgba(255, 255, 0, 0.5);
  }
  
  /* 右键菜单样式 */
  .context-menu {
    position: fixed;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    z-index: 10000;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border: 1px solid #e4e7ed;
    min-width: 150px;
  }
  
  .btn.btn-primary:hover {
    background-color: #66b1ff;
    border-color: #66b1ff;
    color: #fff;
  }

.video-content {
  padding: 30px;
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: #000;
  border-radius: 8px;
  overflow: hidden;
}

video {
  border-radius: 8px;
  transition: all 0.3s ease;
}

.video-placeholder {
  width: 100%;
  height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  font-size: 24px;
  color: #666;
  border-radius: 8px;
}

.video-placeholder {
  width: 100%;
  height: 400px;
  background: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  margin-bottom: 20px;
}

.video-controls {
  display: flex;
  align-items: center;
  gap: 15px;
}

.speed-select {
  padding: 5px 10px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.practice-content {
  padding: 30px;
  flex: 1;
  overflow-y: auto;
}

.question-content h4 {
  margin-bottom: 15px;
  font-size: 18px;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 20px;
}

.option-item {
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.option-item:hover {
  background: #f5f5f5;
  border-color: #409EFF;
}

.practice-actions {
    margin-top: 30px;
    display: flex;
    justify-content: center;
  }
  
  /* 练习题样式 */
  .practice-info {
    display: flex;
    gap: 10px;
    margin-bottom: 15px;
  }
  
  .practice-type,
  .practice-difficulty {
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
  }
  
  .practice-type {
    background: #ecf5ff;
    color: #409EFF;
  }
  
  .practice-difficulty {
    background: #f0f9ff;
    color: #67c23a;
  }
  
  .practice-description {
    color: #666;
    margin-bottom: 15px;
    line-height: 1.6;
  }
  
  .practice-question {
    color: #333;
    font-size: 15px;
    line-height: 1.8;
    margin-bottom: 20px;
  }
  
  .fill-blanks {
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-top: 20px;
  }
  
  .blank-item {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  .blank-label {
    font-size: 14px;
    color: #666;
    font-weight: 500;
  }
  
  .blank-input {
    padding: 10px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 14px;
    transition: all 0.3s;
  }
  
  .blank-input:focus {
    outline: none;
    border-color: #409EFF;
    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
  }
  
  .code-completion,
  .programming {
    margin-top: 20px;
  }
  
  .code-template {
    background: #f8f8f8;
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 15px;
    margin-bottom: 15px;
  }
  
  .code-template pre {
    margin: 0;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 13px;
    line-height: 1.6;
    color: #333;
    white-space: pre-wrap;
    word-wrap: break-word;
  }
  
  .code-input {
    width: 100%;
    padding: 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 13px;
    line-height: 1.6;
    resize: vertical;
    transition: all 0.3s;
  }
  
  .code-input:focus {
    outline: none;
    border-color: #409EFF;
    box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
  }
  
  .test-cases {
    margin-top: 20px;
    padding: 15px;
    background: #f9f9f9;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
  }
  
  .test-cases h5 {
    margin: 0 0 15px 0;
    font-size: 14px;
    color: #333;
    font-weight: 600;
  }
  
  .test-case {
    padding: 10px;
    background: white;
    border-radius: 4px;
    margin-bottom: 10px;
    border: 1px solid #e0e0e0;
  }
  
  .test-case:last-child {
    margin-bottom: 0;
  }
  
  .test-case-label {
    display: inline-block;
    font-weight: 600;
    color: #409EFF;
    margin-right: 10px;
  }
  
  .test-case-input,
  .test-case-output {
    display: block;
    font-size: 13px;
    color: #666;
    margin: 5px 0;
  }
  
  .submit-result {
    margin-top: 20px;
    padding: 15px;
    border-radius: 4px;
    animation: slideDown 0.3s ease;
  }
  
  .submit-result.success {
    background: #f0f9ff;
    border: 1px solid #c2e7b0;
    color: #67c23a;
  }
  
  .submit-result.error {
    background: #fef0f0;
    border: 1px solid #fbc4c4;
    color: #f56c6c;
  }
  
  .submit-result p {
    margin: 0 0 10px 0;
    font-weight: 500;
  }
  
  .result-details {
    background: white;
    padding: 10px;
    border-radius: 4px;
    border: 1px solid #e0e0e0;
  }
  
  .result-details pre {
    margin: 0;
    font-size: 12px;
    line-height: 1.5;
    white-space: pre-wrap;
    word-wrap: break-word;
  }
  
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
  
  /* AI报错翻译抽屉 */
  .error-drawer {
    position: fixed;
    bottom: 0;
    right: 0;
    width: 400px;
    max-height: 70vh;
    background: white;
    border-radius: 12px 12px 0 0;
    box-shadow: -2px -2px 20px rgba(0,0,0,0.15);
    z-index: 900;
    display: flex;
    flex-direction: column;
  }
  
  .error-drawer-header {
    padding: 20px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .error-drawer-header h3 {
    margin: 0;
    font-size: 18px;
    color: #f56c6c;
  }
  
  .error-drawer-content {
    padding: 20px;
    overflow-y: auto;
    flex: 1;
  }
  
  .original-error,
  .translated-error,
  .error-solution {
    margin-bottom: 20px;
  }
  
  .original-error h4,
  .translated-error h4,
  .error-solution h4 {
    margin: 0 0 10px 0;
    font-size: 14px;
    color: #666;
    font-weight: 500;
  }
  
  .original-error pre {
    background: #f8f8f8;
    padding: 15px;
    border-radius: 6px;
    margin: 0;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 14px;
    overflow-x: auto;
    color: #f56c6c;
  }
  
  .translated-error p,
  .error-solution p {
    margin: 0 0 15px 0;
    line-height: 1.6;
    color: #333;
  }
  
  /* 术语词典样式 */
  .term-tooltip {
    position: fixed;
    background: white;
    border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    padding: 20px;
    max-width: 350px;
    z-index: 1001;
    border-left: 4px solid #409EFF;
  }
  
  .term-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 15px;
  }
  
  .term-header h4 {
    margin: 0;
    font-size: 16px;
    color: #333;
  }
  
  .term-close {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    color: #999;
    padding: 0;
    width: 20px;
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
  
  .term-definition {
    margin: 0 0 15px 0;
    line-height: 1.6;
    color: #666;
    font-size: 14px;
  }
  
  .term-example h5 {
    margin: 0 0 10px 0;
    font-size: 13px;
    color: #666;
    font-weight: 500;
  }
  
  .term-example pre {
    background: #f8f8f8;
    padding: 10px;
    border-radius: 4px;
    margin: 0;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 12px;
    overflow-x: auto;
  }
  
  /* AI学习助手样式 */
  .ai-assistant {
    position: fixed;
    bottom: 30px;
    right: 30px;
    z-index: 1000;
  }
  
  .assistant-toggle {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 15px 25px;
    border-radius: 30px;
    font-size: 16px;
    cursor: pointer;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    transition: transform 0.3s, box-shadow 0.3s;
  }
  
  .assistant-toggle:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
  }
  
  .assistant-chat {
    background: white;
    border-radius: 12px;
    width: 350px;
    max-height: 500px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    display: flex;
    flex-direction: column;
  }
  
  .assistant-header {
    padding: 20px;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .assistant-header h3 {
    margin: 0;
    font-size: 18px;
    color: #333;
  }
  
  .assistant-messages {
    padding: 20px;
    flex: 1;
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 15px;
  }
  
  .message {
    max-width: 80%;
    padding: 12px 16px;
    border-radius: 18px;
    word-wrap: break-word;
    line-height: 1.5;
  }
  
  .message:not(.user) {
    background: #f0f0f0;
    align-self: flex-start;
    border-bottom-left-radius: 4px;
  }
  
  .message.user {
    background: #409EFF;
    color: white;
    align-self: flex-end;
    border-bottom-right-radius: 4px;
  }
  
  .assistant-input {
    padding: 20px;
    border-top: 1px solid #eee;
    display: flex;
    gap: 10px;
  }
  
  .assistant-input .input {
    flex: 1;
    padding: 8px 12px;
    border: 1px solid #ddd;
    border-radius: 4px;
  }
  
  /* 术语高亮样式 */
  .term {
    color: #409EFF;
    font-weight: 500;
    cursor: pointer;
    border-bottom: 1px dashed #409EFF;
    transition: background-color 0.2s;
  }
  
  .term:hover {
    background-color: #ecf5ff;
  }
  
  /* 响应式调整 */
  @media (max-width: 768px) {
    .error-drawer {
      width: 100%;
      max-height: 60vh;
    }
    
    .assistant-chat {
      width: 90vw;
      max-height: 70vh;
    }
    
    .ai-assistant {
      bottom: 20px;
      right: 20px;
    }
  }

/* 响应式布局已简化，移除了对代码区域和结果区域的引用 */

@media (max-width: 768px) {
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .section-actions {
    width: 100%;
    justify-content: space-between;
  }
  
  .bottom-nav {
    flex-direction: column;
    gap: 20px;
  }
  
  .progress-container {
    margin: 0;
    width: 100%;
    max-width: none;
  }
}

/* Jupyter容器样式 */
.jupyter-container {
  margin: 20px 0;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.jupyter-container :deep(.jupyter-notebook) {
  min-height: 400px;
  width: 100%;
}

.empty-content {
  padding: 40px 20px;
  text-align: center;
  color: #666;
  background: #fafafa;
  border: 2px dashed #e0e0e0;
  border-radius: 8px;
  margin: 20px;
}

.empty-content p {
  margin: 10px 0;
  font-size: 16px;
}

.loading-content {
  padding: 40px 20px;
  text-align: center;
  color: #666;
  font-size: 16px;
  animation: pulse 1.5s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

/* 响应式调整 */
@media (max-width: 768px) {
  .jupyter-container {
    margin: 15px 0;
    border-radius: 6px;
  }
  
  .jupyter-container :deep(.jupyter-notebook) {
    min-height: 300px;
  }
}
</style>
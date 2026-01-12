<template>
  <div class="app-container">
    <!-- 全局导航栏 - 根据路由路径显示不同的导航 -->
    <nav class="global-nav" v-if="shouldShowNav">
      <div class="nav-left">
        <router-link 
          :to="navType === 'provider' ? '/provider/books' : navType === 'teacher' ? '/teacher/dashboard' : '/student/books'" 
          class="logo"
        >
          📚 CodeBook+——交互式非计算机专业计算机教育数字教材平台
        </router-link>
      </div>
      <div class="nav-right">
        <!-- 教材提供者端导航 - 只在提供者端路由显示 -->
        <template v-if="navType === 'provider'">
          <router-link to="/provider/books" class="nav-item">
            📚 书籍管理
          </router-link>
          <router-link to="/provider/categories" class="nav-item">
            🏷️ 分类与标签
          </router-link>
          <router-link to="/provider/versions" class="nav-item">
            📑 版本管理
          </router-link>
          <button class="nav-item" @click="onLogout">退出</button>
        </template>
        
        <!-- 学生端导航 - 只在学生端路由显示 -->
        <template v-else-if="navType === 'student'">
          <router-link to="/student/class" class="nav-item">
            👥 我的班级
          </router-link>
          <router-link to="/student/profile/records" class="nav-item">
              📊 学习记录
            </router-link>
          <router-link to="/student/practice" class="nav-item">
              📝 练习题
            </router-link>
          <router-link to="/student/learning-paths" class="nav-item">
              🗺️ 学习路线图
            </router-link>
          <router-link to="/student/fullcode" class="nav-item">
            💻 代码沙盒
          </router-link>
          <router-link to="/student/profile/settings" class="nav-item">
            ⚙️ 设置
          </router-link>
          <router-link to="/" class="nav-item" v-if="!isAuthed">
            ️🔑 登录
          </router-link>
          <button class="nav-item" v-else @click="onLogout">退出</button>
            <button class="notes-toggle" @click="toggleNotes">
              📝 笔记/错题本
            </button>
        </template>
        
        <!-- 教师端导航 - 只在教师端路由显示 -->
        <template v-else-if="navType === 'teacher'">
          <router-link to="/teacher/dashboard" class="nav-item">
            📊 仪表盘
          </router-link>
          <router-link to="/teacher/classes" class="nav-item">
            👥 班级管理
          </router-link>
          <router-link to="/teacher/assignments" class="nav-item">
            📝 作业管理
          </router-link>
          <router-link to="/teacher/students" class="nav-item">
            🎓 学生管理
          </router-link>
          <button class="nav-item" @click="onLogout">退出</button>
        </template>
        </div>
    </nav>

    <!-- 主内容区域 -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 笔记/讨论侧边抽屉 -->
    <div class="sidebar-drawer" :style="{ width: `${drawerWidth}px` }" :class="{ open: notesOpen }">
      <!-- 左侧拖动手柄 -->
      <div 
        class="drawer-resize-handle left"
        @mousedown="startDrawerResize"
        title="拖动调整宽度"
      ></div>
      <div class="drawer-header">
        <h3>笔记/错题本</h3>
        <button class="close-btn" @click="toggleNotes">✕</button>
      </div>
      <div class="drawer-tabs">
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'notes' }"
          @click="activeTab = 'notes'"
        >我的笔记</button>
        <button 
          class="tab-btn" 
          :class="{ active: activeTab === 'wrongQuestions' }"
          @click="activeTab = 'wrongQuestions'"
        >错题本</button>
      </div>
      <div class="drawer-content">
        <div v-if="activeTab === 'notes'" class="notes-content">
          <NotesComponent :note-id="targetNoteId" />
        </div>
        <div v-else class="wrong-questions-content">
          <WrongQuestionsComponent @review-question="handleReviewQuestion" />
        </div>
      </div>
    </div>

    <!-- 遮罩层 -->
    <div v-if="notesOpen" class="drawer-overlay" @click="toggleNotes"></div>
    
    <!-- AI学习助手（根据路由类型显示不同的AI助手） -->
    <!-- 教师端AI助手 -->
    <TeacherAIAssistant v-if="isTeacherRoute" />
    
    <!-- 其他端AI学习助手 -->
    <div class="ai-assistant" :style="chatPosition" v-else-if="showAssistant">
      <div class="assistant-chat" :class="{ minimized: isMinimized }">
        <div class="assistant-header" 
             @mousedown="handleDragStart" 
             :class="{ dragging: isDragging }"
             style="cursor: move;">
          <div class="assistant-title">
            <span class="assistant-icon">🤖</span>
            <h3>AI学习助手</h3>
          </div>
          <button class="minimize-btn" @click.stop="minimizeAssistant">
            {{ isMinimized ? '◯' : '−' }}
          </button>
        </div>
        <div class="assistant-messages">
          <div v-for="(msg, index) in assistantMessages" :key="index" class="message" :class="{ user: msg.isUser }">
            <div class="message-content">{{ msg.content }}</div>
          </div>
          <div v-if="isLoading" class="message">
            <div class="message-content">
              <span class="loading-indicator">AI正在思考...</span>
            </div>
          </div>
          
          <!-- 快速提问按钮 -->
          <div v-if="assistantMessages.length === 1" class="quick-questions">
            <p class="quick-title">快速提问:</p>
            <div class="quick-buttons">
              <button v-for="(q, i) in quickQuestions" :key="i" class="quick-btn" @click="quickAsk(q)">
                {{ q }}
              </button>
            </div>
          </div>
        </div>
        <div class="assistant-input">
          <button class="btn btn-secondary" @click="clearChatHistory">清空历史</button>
          <input 
            type="text" 
            v-model="assistantInput" 
            @keyup.enter="sendAssistantMessage"
            placeholder="输入你的问题..."
            class="input"
            :disabled="isLoading"
          />
          <button class="btn btn-primary" @click="sendAssistantMessage" :disabled="isLoading">
            {{ isLoading ? '发送中...' : '发送' }}
          </button>
        </div>
      </div>
    </div>
    
    <!-- 选中文本浮动菜单 -->
    <div 
      v-if="showSelectionMenu" 
      class="selection-menu" 
      :style="{...selectionMenuPosition, zIndex: 9999}"
      @click.stop
    >
      <button class="menu-btn" @click="askAboutSelection">
        🤖 提问AI
      </button>
      <button class="menu-btn" @click="explainSelection">
        📖 解释概念
      </button>
      <button class="menu-btn" @click="showSelectionMenu = false">
        ✕
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from './api/api.js'
import NotesComponent from './student/components/NotesComponent.vue'
import WrongQuestionsComponent from './student/components/WrongQuestionsComponent.vue'
import TeacherAIAssistant from './teacher/components/TeacherAIAssistant.vue'

export default {
  name: 'App',
  components: {
    NotesComponent,
    WrongQuestionsComponent,
    TeacherAIAssistant
  },
  setup() {
    const router = useRouter()
    const route = useRoute()
    const notesOpen = ref(false)
    const activeTab = ref('notes')
    const targetNoteId = ref(null)
    // 使用ref替代computed，避免频繁检查localStorage导致的页面抖动
    const isAuthed = ref(false)
    const userRole = ref('student')
    
    // 根据路由路径判断应该显示哪个导航栏
    const shouldShowNav = computed(() => {
      const path = route.path
      // 登录页面和404页面不显示导航栏
      if (path === '/' || route.name === 'Auth' || route.name === 'NotFound') {
        return false
      }
      return true
    })
    
    // 判断当前是否在提供者端路由
    const isProviderRoute = computed(() => {
      return route.path.startsWith('/provider/')
    })
    
    // 判断当前是否在学生端路由
    const isStudentRoute = computed(() => {
      return route.path.startsWith('/student/')
    })
    
    // 判断当前是否在教师端路由
    const isTeacherRoute = computed(() => {
      return route.path.startsWith('/teacher/')
    })
    
    // 根据路由路径决定显示的导航类型
    const navType = computed(() => {
      if (isProviderRoute.value) {
        return 'provider'
      } else if (isStudentRoute.value) {
        return 'student'
      } else if (isTeacherRoute.value) {
        return 'teacher'
      }
      return 'none' // 登录页面等不显示导航
    })
    
    // 抽屉拖动状态
    const drawerWidth = ref(400)
    const minDrawerWidth = 300
    const maxDrawerWidth = 800
    const isResizingDrawer = ref(false)
    const resizeStartX = ref(0)
    const resizeStartWidth = ref(0)
    
    // 开始拖动抽屉
    const startDrawerResize = (e) => {
      isResizingDrawer.value = true
      resizeStartX.value = e.clientX
      resizeStartWidth.value = drawerWidth.value
      
      document.addEventListener('mousemove', handleDrawerResize)
      document.addEventListener('mouseup', stopDrawerResize)
      e.preventDefault()
    }
    
    // 拖动处理
    const handleDrawerResize = (e) => {
      if (!isResizingDrawer.value) return
      const deltaX = e.clientX - resizeStartX.value
      const newWidth = resizeStartWidth.value - deltaX
      if (newWidth >= minDrawerWidth && newWidth <= maxDrawerWidth) {
        drawerWidth.value = newWidth
      }
    }
    
    // 停止拖动
    const stopDrawerResize = () => {
      isResizingDrawer.value = false
      document.removeEventListener('mousemove', handleDrawerResize)
      document.removeEventListener('mouseup', stopDrawerResize)
    }
    
    // 初始化检查认证状态和用户角色
    const checkAuthStatus = () => {
      try { 
        // 直接获取localStorage中的值
        const token = localStorage.getItem('token')
        const storedRole = localStorage.getItem('userRole')
        
        // 设置认证状态
        isAuthed.value = !!token
        
        // 设置用户角色，确保值是有效的
        if (token && storedRole && ['student', 'provider'].includes(storedRole)) {
          userRole.value = storedRole
        } else {
          userRole.value = 'student'
        }
        
        // 调试信息
        console.log('checkAuthStatus:', {
          token: !!token,
          storedRole,
          userRole: userRole.value,
          isAuthed: isAuthed.value
        })
      } catch (error) { 
        console.error('检查认证状态失败:', error)
        isAuthed.value = false 
        userRole.value = 'student'
      }
    }
    
    // 初始检查
    checkAuthStatus()
    
    // 添加window事件监听器，在登录成功后可以手动触发更新
    window.__updateAuthStatus = checkAuthStatus
    
    // 监听路由变化，更新认证状态（作为额外保障）
    watch(() => route.path, () => {
      checkAuthStatus()
    })
    
    // 监听localStorage变化，确保角色信息实时更新
    window.addEventListener('storage', (event) => {
      if (event.key === 'userRole' || event.key === 'token') {
        checkAuthStatus()
      }
    })
    
    // 监听userRole变化，添加调试信息
    watch(userRole, (newRole) => {
      console.log('User role changed:', newRole)
    })

    const toggleNotes = () => {
      // 只有学生端才显示笔记/错题本抽屉
      if (userRole.value !== 'student') {
        return
      }
      notesOpen.value = !notesOpen.value
    }

    const handleOpenNotesDrawer = (event) => {
      const noteId = event.detail?.noteId
      if (noteId) {
        targetNoteId.value = noteId
      }
      activeTab.value = 'notes'
      notesOpen.value = true
    }

    const handleKeydown = (e) => {
      if (e.key === 'N' && e.ctrlKey) {
        e.preventDefault()
        toggleNotes()
      }
    }

    const handleReviewQuestion = (question) => {
      console.log('需要复习题目:', question)
      // 这里可以实现跳转到相应的练习页面
      alert(`将跳转到「${question.bookTitle}」中的题目「${question.title}」进行复习`)
      // 实际实现时可以使用router进行跳转
      // router.push(`/learn/${question.bookId}/section/${question.sectionId}/practice`)
    }

    const onLogout = async () => {
      try { 
        await api.logout() 
      } catch {}
      finally {
        // 清除本地存储的认证信息
        try {
          localStorage.removeItem('token')
          localStorage.removeItem('userRole')
        } catch {}
        
        // 登出后立即更新认证状态
        checkAuthStatus()
        
        // 跳转到登录注册页面
        router.push('/')
      }
    }

    // AI助手相关状态变量
    const showAssistant = ref(true)
    const isDragging = ref(false)
    const dragStartX = ref(0)
    const dragStartY = ref(0)
    const chatPosition = ref({
      bottom: '50px',
      right: '50px'
    })
    const isMinimized = ref(true)
    const isLoading = ref(false)
    // 从localStorage加载对话历史或使用默认消息
    const loadMessagesFromStorage = () => {
      try {
        const saved = localStorage.getItem('assistantMessages')
        return saved ? JSON.parse(saved) : [
          {
            content: '你好！我是你的AI学习助手。请问有什么可以帮助你的吗？',
            isUser: false,
            timestamp: new Date().toISOString()
          }
        ]
      } catch {
        return [
          {
            content: '你好！我是你的AI学习助手。请问有什么可以帮助你的吗？',
            isUser: false,
            timestamp: new Date().toISOString()
          }
        ]
      }
    }
    const assistantMessages = ref(loadMessagesFromStorage())
    const assistantInput = ref('')
    // 预定义问题快捷按钮
    const quickQuestions = ref([
      '如何学习Python基础？',
      '什么是面向对象编程？',
      '如何调试我的代码？',
      '解释一下数据结构中的链表',
      '推荐一些学习资源',
      '如何提高编程效率？',
      '推荐学习路径'
    ])
    
    // 文本选择相关状态
    const showSelectionMenu = ref(false)
    const selectionMenuPosition = ref({ top: '0px', left: '0px' })
    const selectedText = ref('')

    // 拖拽开始事件处理
    const handleDragStart = (event) => {
      isDragging.value = true
      dragStartX.value = event.clientX
      dragStartY.value = event.clientY
    }

    // 拖拽移动事件处理
    const handleDragMove = (event) => {
      if (!isDragging.value) return

      const deltaX = event.clientX - dragStartX.value
      const deltaY = event.clientY - dragStartY.value

      // 获取当前位置并计算新位置
      const currentTop = parseInt(chatPosition.value.top)
      const currentRight = parseInt(chatPosition.value.right)

      // 反转X方向（因为使用right定位）
      chatPosition.value = {
        top: `${currentTop + deltaY}px`,
        right: `${currentRight - deltaX}px`
      }

      dragStartX.value = event.clientX
      dragStartY.value = event.clientY
    }

    // 拖拽结束事件处理
    const handleDragEnd = () => {
      isDragging.value = false
    }

    // 最小化功能实现
    const minimizeAssistant = () => {
      isMinimized.value = !isMinimized.value
    }

    // 保存消息到localStorage
    const saveMessagesToStorage = () => {
      try {
        localStorage.setItem('assistantMessages', JSON.stringify(assistantMessages.value))
      } catch (error) {
        console.warn('无法保存对话历史:', error)
      }
    }

    // 发送AI助手消息
    const sendAssistantMessage = async () => {
      if (!assistantInput.value.trim()) return

      // 添加用户消息
      const userMessage = {
        content: assistantInput.value,
        isUser: true,
        timestamp: new Date().toISOString()
      }
      assistantMessages.value.push(userMessage)

      const userQuestion = assistantInput.value
      assistantInput.value = ''
      
      // 保存消息
      saveMessagesToStorage()

      try {
        // 设置加载状态
        isLoading.value = true
        
        // 使用封装的API方法获取AI回复
        const response = await api.getAIAssistantResponse(userQuestion)
        
        // 添加AI回复 - 保留完整的回答内容
        // 后端现在已经在生成时就控制了字数，确保回答完整且自然
        const aiMessage = {
          content: response.answer || '抱歉，无法获取AI回复',
          isUser: false,
          timestamp: new Date().toISOString()
        }
        assistantMessages.value.push(aiMessage)
        
        // 显示学习进度提示（仅学生端）
        if (userRole.value === 'student') {
          showProgressTip()
          autoRecommendContent()
        }
      } catch (error) {
        console.error('AI助手API调用失败:', error)
        
        // 添加错误消息作为回退
        const errorMessage = {
          content: '抱歉，AI助手暂时无法响应。请稍后再试或检查网络连接。',
          isUser: false,
          timestamp: new Date().toISOString()
        }
        assistantMessages.value.push(errorMessage)
      } finally {
        // 无论成功失败，都关闭加载状态并保存消息
        isLoading.value = false
        saveMessagesToStorage()
      }
    }
    
    // 快速提问功能
    const quickAsk = (question) => {
      // 根据问题内容提供更智能的上下文
      let enhancedQuestion = question
      
      // 如果是关于学习资源的问题，添加教材上下文
      if (question.includes('学习资源')) {
        enhancedQuestion = `${question}，特别是与当前学习内容相关的`
      }
      
      // 如果是关于编程效率的问题，添加学习进度上下文
      if (question.includes('编程效率')) {
        enhancedQuestion = `${question}，考虑到我正在学习编程基础`
      }
      
      // 如果是关于学习路径的问题，添加当前进度上下文
      if (question.includes('学习路径')) {
        enhancedQuestion = `${question}，我已经学习了${learningProgress.value.conceptsLearned}个概念，完成了${learningProgress.value.exercisesCompleted}个练习`
      }
      
      assistantInput.value = enhancedQuestion
      sendAssistantMessage()
    }
    
    // 处理文本选择事件
    const handleTextSelection = (event) => {
      // 确保事件不是从输入框或编辑器触发的，避免干扰正常编辑
      const target = event.target || event.srcElement;
      // 检查target是否是有效的DOM元素并且支持closest方法
      const isEditorElement = target && target.nodeType === 1 && target.closest && 
                            (target.closest('.CodeMirror') || target.closest('.ace_editor'));
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || isEditorElement) {
        return;
      }
      
      const selection = window.getSelection()
      const text = selection.toString().trim()
      
      // 放宽文本长度限制，允许更短的文本选择
      if (text.length > 3 && text.length < 1000) {
        selectedText.value = text
        try {
          const range = selection.getRangeAt(0)
          const rect = range.getBoundingClientRect()
          
          // 计算浮动菜单位置（在选中区域下方居中）
          // 确保菜单在视口内
          const menuWidth = 150; // 菜单大致宽度
          let menuTop = rect.bottom + window.scrollY + 5
          let menuLeft = rect.left + window.scrollX + (rect.width / 2) - (menuWidth / 2)
          
          // 边界检查，确保菜单不超出视口
          if (menuLeft < 0) menuLeft = 10;
          if (menuLeft + menuWidth > window.innerWidth) menuLeft = window.innerWidth - menuWidth - 10;
          if (menuTop + 40 > window.innerHeight) menuTop = rect.top + window.scrollY - 45; // 显示在上方
          
          selectionMenuPosition.value = {
            top: `${menuTop}px`,
            left: `${menuLeft}px`
          }
          
          showSelectionMenu.value = true
        } catch (e) {
          // 处理选择范围获取失败的情况
          console.error('无法获取选择范围:', e)
        }
      } else if (showSelectionMenu.value) {
        // 如果没有有效的选择，隐藏菜单
        showSelectionMenu.value = false
      }
    }
    
    // 根据选中内容提问AI
    const askAboutSelection = () => {
      if (selectedText.value) {
        // 如果AI助手最小化了，先恢复
        if (isMinimized.value) {
          minimizeAssistant()
        }
        
        // 构建问题但不自动发送，只是放入输入框中
        const question = `请解释这段代码或概念：${selectedText.value}`
        assistantInput.value = question
        
        // 聚焦到输入框，方便用户编辑或直接按回车发送
        setTimeout(() => {
          const inputElement = document.querySelector('.assistant-input .input')
          if (inputElement) {
            inputElement.focus()
          }
        }, 100)
        
        // 隐藏菜单
        showSelectionMenu.value = false
      }
    }
    
    // 解释选中的概念
    const explainSelection = () => {
      if (selectedText.value) {
        // 如果AI助手最小化了，先恢复
        if (isMinimized.value) {
          minimizeAssistant()
        }
        
        // 构建更针对性的问题，增加学习建议和示例要求，但不自动发送
        const question = `请详细解释这个概念或代码块，并提供：
1. 通俗易懂的解释
2. 相关的学习建议
3. 一个简单的示例说明
4. 常见的应用场景

内容：${selectedText.value}`
        assistantInput.value = question
        
        // 聚焦到输入框，方便用户编辑或直接按回车发送
        setTimeout(() => {
          const inputElement = document.querySelector('.assistant-input .input')
          if (inputElement) {
            inputElement.focus()
          }
        }, 100)
        
        // 隐藏菜单
        showSelectionMenu.value = false
      }
    }
    
    // 学习进度提示（模拟）
    const learningProgress = ref({
      conceptsLearned: 15,
      exercisesCompleted: 8,
      chaptersRead: 3
    })
    
    // 显示学习进度提示
    const showProgressTip = () => {
      const progressMessage = `\n\n📚 **学习进度提示**\n- 已学习概念：${learningProgress.value.conceptsLearned}个\n- 完成练习：${learningProgress.value.exercisesCompleted}个\n- 已读章节：${learningProgress.value.chaptersRead}章`
      
      // 在适当的时机显示进度提示（例如完成一个大概念学习后）
      if (assistantMessages.value.length > 0) {
        const lastMessage = assistantMessages.value[assistantMessages.value.length - 1]
        if (lastMessage.sender === 'assistant' && (lastMessage.text.includes('完成') || lastMessage.text.includes('总结'))) {
          // 模拟添加进度提示到最后一条助手消息
          lastMessage.text += progressMessage
        }
      }
    }
    
    // 学习内容推荐（基于当前进度）
    const recommendContent = () => {
      // 根据学习进度生成推荐内容
      let recommendations = []
      
      // 基于已学习概念数推荐下一步学习内容
      if (learningProgress.value.conceptsLearned < 20) {
        recommendations.push('基础编程概念进阶')
      } else if (learningProgress.value.conceptsLearned < 30) {
        recommendations.push('中级算法与数据结构')
      } else {
        recommendations.push('高级编程技术')
      }
      
      // 基于已完成练习数推荐实践内容
      if (learningProgress.value.exercisesCompleted < 10) {
        recommendations.push('基础编程练习集')
      } else if (learningProgress.value.exercisesCompleted < 20) {
        recommendations.push('项目实战训练')
      } else {
        recommendations.push('算法挑战')
      }
      
      // 基于已读章节数推荐阅读内容
      if (learningProgress.value.chaptersRead < 5) {
        recommendations.push('接下来的章节内容')
      } else {
        recommendations.push('相关拓展阅读')
      }
      
      return recommendations
    }
    
    // 自动推荐学习内容
    const autoRecommendContent = () => {
      // 当用户完成一定学习量后自动推荐
      if (assistantMessages.value.length > 0 && !isMinimized.value) {
        // 每5条用户消息后推荐一次
        const userMessageCount = assistantMessages.value.filter(msg => msg.sender === 'user').length
        if (userMessageCount % 5 === 0 && userMessageCount > 0) {
          const recommendations = recommendContent()
          if (recommendations.length > 0) {
            setTimeout(() => {
              assistantMessages.value.push({
                id: Date.now(),
                text: `💡 **学习推荐**：根据你的学习进度，建议你接下来学习以下内容：\n- ${recommendations.join('\n- ')}`,
                sender: 'assistant',
                isRecommendation: true
              })
              saveChatToLocalStorage()
              // 自动滚动到底部
              setTimeout(() => {
                const chatContainer = document.querySelector('.chat-messages')
                if (chatContainer) {
                  chatContainer.scrollTop = chatContainer.scrollHeight
                }
              }, 100)
            }, 1000)
          }
        }
      }
    }
    
    // 清空对话历史
    const clearChatHistory = () => {
      assistantMessages.value = [
        {
          content: '你好！我是你的AI学习助手。请问有什么可以帮助你的吗？',
          isUser: false,
          timestamp: new Date().toISOString()
        }
      ]
      saveMessagesToStorage()
    }

    // 处理AI助手问题事件
    const handleOpenAIAssistant = (event) => {
      const { question } = event.detail || {}
      if (question) {
        // 确保AI助手显示且未最小化
        showAssistant.value = true
        isMinimized.value = false
        
        // 设置问题并发送
        assistantInput.value = question
        sendAssistantMessage()
      }
    }

    onMounted(() => {
      document.addEventListener('keydown', handleKeydown)
      // 添加全局鼠标移动事件
      window.addEventListener('mousemove', handleDragMove)
      window.addEventListener('mouseup', handleDragEnd)
      // 添加文本选择事件监听
      // 使用mouseup和selectionchange事件组合，确保在各种情况下都能捕获选择
      document.addEventListener('mouseup', handleTextSelection)
      document.addEventListener('selectionchange', handleTextSelection)
      
      // 添加touchend事件支持，确保在移动设备上也能工作
      document.addEventListener('touchend', handleTextSelection)
      
      // 添加AI助手问题事件监听
      window.addEventListener('open-ai-assistant', handleOpenAIAssistant)
      
      // 添加打开笔记抽屉事件监听
      window.addEventListener('open-notes-drawer', handleOpenNotesDrawer)
    })

    onUnmounted(() => {
      document.removeEventListener('keydown', handleKeydown)
      // 清理事件监听器
      window.removeEventListener('open-ai-assistant', handleOpenAIAssistant)
      window.removeEventListener('open-notes-drawer', handleOpenNotesDrawer)
      window.removeEventListener('mousemove', handleDragMove)
      window.removeEventListener('mouseup', handleDragEnd)
      document.removeEventListener('mouseup', handleTextSelection)
      document.removeEventListener('selectionchange', handleTextSelection)
      document.removeEventListener('touchend', handleTextSelection)
    })

    return {
      notesOpen,
      activeTab,
      targetNoteId,
      drawerWidth,
      toggleNotes,
      isAuthed,
      userRole,
      onLogout,
      handleReviewQuestion,
      startDrawerResize,
      // 导航栏相关
      shouldShowNav,
      navType,
      isProviderRoute,
      isStudentRoute,
      isTeacherRoute,
      // AI助手相关变量和函数
      showAssistant,
      isDragging,
      chatPosition,
      isMinimized,
      isLoading,
      assistantMessages,
      assistantInput,
      quickQuestions,
      handleDragStart,
      minimizeAssistant,
      sendAssistantMessage,
      clearChatHistory,
      quickAsk,
      // 文本选择相关
      showSelectionMenu,
      selectionMenuPosition,
      askAboutSelection,
      explainSelection,
      // 学习进度和推荐
      learningProgress,
      recommendContent,
      autoRecommendContent
    }
  }
}
</script>

<style>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.global-nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  font-size: 20px;
  font-weight: bold;
  text-decoration: none;
  color: #333;
}

.nav-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.nav-item {
  text-decoration: none;
  color: #666;
  font-size: 14px;
  padding: 8px 12px;
  border-radius: 4px;
  transition: all 0.3s;
}

.nav-item:hover {
  background-color: #f5f5f5;
  color: #333;
}

.notes-toggle {
  background: #409EFF;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.notes-toggle:hover {
  background: #66b1ff;
}

.main-content {
  flex: 1;
  padding: 20px;
}

/* 侧边抽屉样式 */
.sidebar-drawer {
  position: fixed;
  right: 0;
  transform: translateX(100%);
  top: 0;
  /* width 由动态绑定控制 */
  height: 100vh;
  background: white;
  box-shadow: -2px 0 8px rgba(0,0,0,0.15);
  transition: transform 0.3s ease, width 0.1s ease;
  z-index: 200;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-drawer.open {
  transform: translateX(0);
}

/* 抽屉左侧拖动手柄 */
.drawer-resize-handle {
  position: absolute;
  left: 0;
  top: 0;
  width: 6px;
  height: 100%;
  cursor: col-resize;
  background: transparent;
  z-index: 2;
  transition: background 0.2s;
}

.drawer-resize-handle:hover,
.drawer-resize-handle:active {
  background: rgba(64, 158, 255, 0.5);
}

.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  background: white;
  position: relative;
  z-index: 3;
  flex-shrink: 0;
}

.drawer-header h3 {
  margin: 0;
  font-size: 18px;
  flex: 1;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
  padding: 8px;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
  flex-shrink: 0;
  z-index: 10;
}

.close-btn:hover {
  background: #f5f5f5;
  color: #333;
}

.drawer-tabs {
  display: flex;
  border-bottom: 1px solid #e0e0e0;
}

.tab-btn {
  flex: 1;
  padding: 15px;
  background: none;
  border: none;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  transition: all 0.3s;
}

.tab-btn:hover {
  color: #409EFF;
}

.tab-btn.active {
  color: #409EFF;
  border-bottom: 2px solid #409EFF;
}

.drawer-content {
  flex: 1;
  overflow: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.notes-content,
.wrong-questions-content {
  flex: 1;
  overflow: auto;
  overflow-x: hidden;
  display: flex;
  flex-direction: column;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.3);
  z-index: 199;
  cursor: pointer;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 选中文本浮动菜单样式 */
.selection-menu {
  position: absolute;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  padding: 5px;
  display: flex;
  gap: 5px;
  z-index: 1001;
  /* 移除transform，因为我们在JavaScript中精确计算位置 */
  /* 添加过渡效果 */
  transition: opacity 0.2s ease, transform 0.2s ease;
  opacity: 0;
  transform: translateY(-5px);
  animation: fadeInUp 0.2s ease forwards;
}

/* 淡入上移动画 */
@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.menu-btn {
  background: #4a6cf7;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
  transition: background-color 0.2s;
}

.menu-btn:hover {
  background: #3a5ce9;
}

.menu-btn:last-child {
  background: #f5f5f5;
  color: #666;
}

.menu-btn:last-child:hover {
  background: #e0e0e0;
}

/* AI助手样式 */
.ai-assistant {
  position: fixed;
  z-index: 9999;
  max-width: 400px;
  max-height: 600px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.assistant-chat {
  background: white;
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  height: 450px;
  width: 350px;
  transition: all 0.3s ease;
}

.assistant-chat.minimized {
  height: 60px;
  width: 60px;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.assistant-chat.minimized .assistant-header {
  border-radius: 50%;
  padding: 0;
  height: 100%;
  justify-content: center;
}

.assistant-chat.minimized .assistant-title {
  display: none;
}

.assistant-chat.minimized .minimize-btn {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  font-size: 28px;
  background: linear-gradient(135deg, #409EFF, #66b1ff);
}

.assistant-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  color: white;
  user-select: none;
  border-radius: 8px 8px 0 0;
  transition: all 0.3s ease;
}

.assistant-header.dragging {
  background: linear-gradient(135deg, #66b1ff, #99ccff);
  cursor: move;
}

.assistant-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.assistant-icon {
  font-size: 20px;
  transition: transform 0.3s ease;
}

.assistant-header:hover .assistant-icon {
  transform: scale(1.1) rotate(5deg);
}

.assistant-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.minimize-btn {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.minimize-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  transform: scale(1.1);
}

.assistant-messages {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
  background: #fafafa;
}

.message {
  margin-bottom: 16px;
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.message-content {
  max-width: 80%;
  padding: 10px 14px;
  border-radius: 8px;
  word-wrap: break-word;
  font-size: 14px;
  line-height: 1.5;
}

.message:not(.user) .message-content {
  background: white;
  border: 1px solid #e0e0e0;
  margin-right: auto;
}

.message.user .message-content {
  background: #409EFF;
  color: white;
  margin-left: auto;
}

.assistant-input {
  padding: 12px 16px;
  background: white;
  border-top: 1px solid #e0e0e0;
  display: flex;
  gap: 8px;
}

.assistant-input .input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.3s;
}

.assistant-input .input:focus {
  border-color: #409EFF;
}

.assistant-input .btn {
  padding: 8px 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-secondary {
  background: #909399;
  color: white;
}

.btn-secondary:hover {
  background: #a6a9ad;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-indicator {
  display: inline-block;
  padding: 5px 10px;
  background: #f0f9ff;
  color: #409eff;
  border-radius: 4px;
}

.quick-questions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #eee;
}

.quick-title {
  font-size: 14px;
  color: #606266;
  margin-bottom: 10px;
}

.quick-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-btn {
  padding: 6px 12px;
  background: #ecf5ff;
  border: 1px solid #d9ecff;
  color: #409eff;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-btn:hover {
  background: #409eff;
  color: white;
  border-color: #409eff;
}

.assistant-input .btn-primary {
  background: #409EFF;
  color: white;
}

.assistant-input .btn-primary:hover {
  background: #66b1ff;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .ai-assistant {
    max-width: 90%;
    right: 10px !important;
    bottom: 10px !important;
    top: auto !important;
    left: auto !important;
  }
  
  .assistant-chat {
    width: 100%;
    height: 350px;
  }
}
</style>
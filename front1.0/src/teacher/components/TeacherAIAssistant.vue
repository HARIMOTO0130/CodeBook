<template>
  <div class="teacher-ai-assistant" :class="{ minimized: isMinimized }" :style="chatPosition">
    <!-- 头部区域 - 始终显示，支持拖拽和点击恢复 -->
    <div 
      class="assistant-header teacher-header" 
      @mousedown="handleDragStart"
    >
      <!-- 教师AI助手图标 - 始终显示 -->
      <div class="assistant-icon-container" @click.stop="minimizeAssistant">
        <span class="assistant-icon teacher-icon">👨‍🏫</span>
      </div>
      
      <!-- 正常状态下的标题和选择器 -->
      <div class="assistant-content" v-if="!isMinimized">
        <div class="assistant-title">
          <h3>教师AI助手</h3>
          <span class="teacher-badge">教师专用</span>
        </div>
        <div class="header-actions">
          <!-- 学生选择器 - 只在教师端显示 -->
          <select 
            v-model="selectedStudentId" 
            class="student-selector"
            @change="onStudentChange"
            v-if="students.length > 0"
          >
            <option value="">选择学生（可选）</option>
            <option v-for="student in students" :key="student.id" :value="student.id">
              {{ student.name }} ({{ student.student_no }})
            </option>
          </select>
          <!-- 班级选择器 - 只在教师端显示 -->
          <select 
            v-model="selectedClassId" 
            class="class-selector"
            @change="onClassChange"
            v-if="classes.length > 0"
          >
            <option value="">选择班级（可选）</option>
            <option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
              {{ classItem.name }}
            </option>
          </select>
        </div>
      </div>
      
      <!-- 最小化按钮 - 始终显示 -->
      <button class="minimize-btn" @click="minimizeAssistant">
        {{ isMinimized ? '◯' : '−' }}
      </button>
    </div>

    <!-- 正常状态下的消息区域和输入区域 -->
    <div v-if="!isMinimized">
      <!-- 消息区域 -->
      <div class="assistant-messages">
        <div v-for="(msg, index) in messages" :key="index" class="message" :class="{ user: msg.isUser }">
          <div class="message-content">
            <div v-if="msg.contextInfo" class="context-badge">
              <span class="context-icon">📊</span>
              <span>基于{{ msg.contextInfo }}数据</span>
            </div>
            {{ msg.content }}
          </div>
        </div>
        <div v-if="isLoading" class="message">
          <div class="message-content">
            <span class="loading-indicator">AI正在分析学生数据...</span>
          </div>
        </div>
        
        <!-- 教师端快速提问按钮 -->
        <div v-if="messages.length === 1" class="quick-questions teacher-quick">
          <p class="quick-title">教学相关快速提问:</p>
          <div class="quick-buttons">
            <button 
              v-for="(q, i) in teacherQuickQuestions" 
              :key="i" 
              class="quick-btn teacher-quick-btn" 
              @click="quickAsk(q)"
            >
              {{ q }}
            </button>
          </div>
        </div>
        
        <!-- AI分析结果解读提示 -->
        <div v-if="showAnalysisTips && messages.length > 1" class="analysis-tips teacher-analysis-tips">
          <p class="tips-title">📊 数据分析解读:</p>
          <ul class="tips-list">
            <li v-if="analysisTips.studentProgress">👨‍🎓 <strong>学生进度</strong>: {{ analysisTips.studentProgress }}</li>
            <li v-if="analysisTips.classPerformance">👥 <strong>班级表现</strong>: {{ analysisTips.classPerformance }}</li>
            <li v-if="analysisTips.strengths">✨ <strong>优势领域</strong>: {{ analysisTips.strengths }}</li>
            <li v-if="analysisTips.weaknesses">📈 <strong>待改进</strong>: {{ analysisTips.weaknesses }}</li>
            <li v-if="analysisTips.teachingSuggestions">💡 <strong>教学建议</strong>: {{ analysisTips.teachingSuggestions }}</li>
          </ul>
        </div>
        
        <!-- 操作提示 -->
        <div class="operation-tips teacher-operation-tips">
          <div class="tip-item" v-if="!selectedStudentId && !selectedClassId">
            💡 <strong>提示</strong>: 选择学生或班级可获得更精准的数据分析
          </div>
          <div class="tip-item" v-else-if="selectedStudentId">
            👨‍🎓 当前分析基于 <strong>{{ selectedStudentName }}</strong> 的数据
          </div>
          <div class="tip-item" v-else-if="selectedClassId">
            👥 当前分析基于 <strong>{{ selectedClassName }}</strong> 的数据
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="assistant-input">
        <button class="btn btn-secondary" @click="clearChatHistory">清空历史</button>
        <input 
          type="text" 
          v-model="inputText" 
          @keyup.enter="sendMessage"
          placeholder="输入问题，可结合学生数据进行分析..."
          class="input teacher-input"
          :disabled="isLoading"
        />
        <button class="btn btn-primary teacher-btn" @click="sendMessage" :disabled="isLoading">
          {{ isLoading ? '分析中...' : '发送' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { studentApi } from '../api/student.js'
import { classApi } from '../api/class.js'
import teacherAIApi from '../api/aiAssistant.js'

export default {
  name: 'TeacherAIAssistant',
  setup() {
    const route = useRoute()
    const isMinimized = ref(false)
    const messages = ref([
      {
        content: '你好！我是教师AI助手。我可以帮你分析学生学习情况、提供教学建议。你可以选择学生或班级来获取更精准的分析。',
        isUser: false
      }
    ])
    const inputText = ref('')
    const isLoading = ref(false)
    const selectedStudentId = ref('')
    const selectedClassId = ref('')
    const students = ref([])
    const classes = ref([])
    const sessionId = ref(null)
    
    // 新增：分析结果解读提示相关状态
    const showAnalysisTips = ref(false)
    const analysisTips = ref({
      studentProgress: '',
      classPerformance: '',
      strengths: '',
      weaknesses: '',
      teachingSuggestions: ''
    })
    
    // 新增：选中的学生和班级名称
    const selectedStudentName = ref('')
    const selectedClassName = ref('')

    // 教师端专用快速问题
    const teacherQuickQuestions = [
      '分析这个学生的学习情况',
      '这个班级的整体学习进度如何？',
      '哪些学生需要重点关注？',
      '推荐适合这个班级的教学方法',
      '分析学生的AI使用情况',
      '生成学生学习报告建议'
    ]

    // 加载学生和班级列表
    const loadData = async () => {
      try {
        // 加载学生列表
        const studentsRes = await studentApi.getStudents()
        if (studentsRes.data) {
          // 处理Django REST Framework的分页响应格式
          const studentsArray = Array.isArray(studentsRes.data.results) ? studentsRes.data.results : 
                               Array.isArray(studentsRes.data) ? studentsRes.data : []
          
          students.value = studentsArray.map(s => ({
            id: s.id,
            name: s.student_name,
            student_no: s.student_no
          }))
        }

        // 加载班级列表
        const classesRes = await classApi.getClasses()
        if (classesRes.data) {
          // 处理Django REST Framework的分页响应格式
          const classesArray = Array.isArray(classesRes.data.results) ? classesRes.data.results : 
                              Array.isArray(classesRes.data) ? classesRes.data : []
          
          classes.value = classesArray.map(c => ({
            id: c.id,
            name: c.name
          }))
        }
      } catch (error) {
        console.error('加载数据失败:', error)
        // 发生错误时，确保students和classes为数组
        students.value = []
        classes.value = []
      }
    }

    // 发送消息
    const sendMessage = async () => {
      if (!inputText.value.trim() || isLoading.value) return

      const question = inputText.value
      messages.value.push({
        content: question,
        isUser: true
      })

      inputText.value = ''
      isLoading.value = true

      try {
        // 调用教师端AI助手API
        const response = await teacherAIApi.getTeacherAIAssistantResponse({
          question: question,
          session_id: sessionId.value,
          student_id: selectedStudentId.value || null,
          class_id: selectedClassId.value || null
        })

        if (response.data) {
          const contextInfo = []
          if (response.data.context_used?.has_student_context) {
            const student = students.value.find(s => s.id === selectedStudentId.value)
            contextInfo.push(student ? student.name : '学生')
          }
          if (response.data.context_used?.has_class_context) {
            const classItem = classes.value.find(c => c.id === selectedClassId.value)
            contextInfo.push(classItem ? classItem.name : '班级')
          }
          
          // 新增：流式响应效果 - 逐步显示AI回复
          const answer = response.data.answer
          const aiMessage = {
            content: '',
            isUser: false,
            contextInfo: contextInfo.length > 0 ? contextInfo.join('、') : null
          }
          messages.value.push(aiMessage)
          
          // 模拟流式输出，逐步显示回复内容
          let index = 0
          const speed = 30 // 每个字符显示的毫秒数
          const interval = setInterval(() => {
            if (index < answer.length) {
              aiMessage.content += answer[index]
              index++
              // 滚动到底部
              const messagesContainer = document.querySelector('.assistant-messages')
              if (messagesContainer) {
                messagesContainer.scrollTop = messagesContainer.scrollHeight
              }
            } else {
              clearInterval(interval)
              
              // 生成AI分析结果解读提示
              showAnalysisTips.value = true
              setTimeout(() => {
                showAnalysisTips.value = false
              }, 15000) // 15秒后自动隐藏
              
              // 模拟分析解读内容，实际可以根据AI回复内容进行解析
              analysisTips.value = {
                studentProgress: selectedStudentId.value ? '该学生学习进度正常，章节1完成80%' : '',
                classPerformance: selectedClassId.value ? '班级整体进度良好，平均完成率75%' : '',
                strengths: '代码编写能力较强，理论知识掌握扎实',
                weaknesses: '算法思维需要加强，建议增加相关练习',
                teachingSuggestions: '针对薄弱环节设计个性化练习，利用小组协作提升算法能力'
              }
              
              // 保存会话历史
              saveSessionHistory()
            }
          }, speed)

          if (response.data.session_id) {
            sessionId.value = response.data.session_id
          }
        }
      } catch (error) {
        console.error('AI助手请求失败:', error)
        messages.value.push({
          content: '抱歉，AI助手暂时无法响应。请稍后再试。',
          isUser: false
        })
        // 保存会话历史，包括错误消息
        saveSessionHistory()
      } finally {
        isLoading.value = false
      }
    }

    // 快速提问
    const quickAsk = (question) => {
      inputText.value = question
      sendMessage()
    }

    // 清空历史
    const clearChatHistory = () => {
      messages.value = [{
        content: '你好！我是教师AI助手。我可以帮你分析学生学习情况、提供教学建议。',
        isUser: false
      }]
      sessionId.value = null
      // 清除本地存储的会话历史
      localStorage.removeItem('teacherAISessionHistory')
    }
    
    // 新增：会话持久化 - 保存会话到本地存储
    const saveSessionHistory = () => {
      try {
        const sessionData = {
          messages: messages.value,
          sessionId: sessionId.value,
          selectedStudentId: selectedStudentId.value,
          selectedClassId: selectedClassId.value
        }
        localStorage.setItem('teacherAISessionHistory', JSON.stringify(sessionData))
      } catch (error) {
        console.error('保存会话历史失败:', error)
      }
    }
    
    // 新增：加载会话历史
    const loadSessionHistory = () => {
      try {
        const savedSession = localStorage.getItem('teacherAISessionHistory')
        if (savedSession) {
          const sessionData = JSON.parse(savedSession)
          messages.value = sessionData.messages || messages.value
          sessionId.value = sessionData.sessionId || null
          selectedStudentId.value = sessionData.selectedStudentId || ''
          selectedClassId.value = sessionData.selectedClassId || ''
          
          // 更新选中的学生和班级名称
          if (sessionData.selectedStudentId) {
            const student = students.value.find(s => s.id === sessionData.selectedStudentId)
            if (student) {
              selectedStudentName.value = student.name
            }
          }
          if (sessionData.selectedClassId) {
            const classItem = classes.value.find(c => c.id === sessionData.selectedClassId)
            if (classItem) {
              selectedClassName.value = classItem.name
            }
          }
        }
      } catch (error) {
        console.error('加载会话历史失败:', error)
      }
    }

    // 学生选择变化
    const onStudentChange = () => {
      if (selectedStudentId.value) {
        const student = students.value.find(s => s.id === selectedStudentId.value)
        if (student) {
          selectedStudentName.value = student.name
          selectedClassName.value = '' // 清空班级选择
          messages.value.push({
            content: `已选择学生 ${student.name}，后续分析将基于该学生的学习数据。`,
            isUser: false
          })
        }
      } else {
        selectedStudentName.value = ''
      }
    }

    // 班级选择变化
    const onClassChange = () => {
      if (selectedClassId.value) {
        const classItem = classes.value.find(c => c.id === selectedClassId.value)
        if (classItem) {
          selectedClassName.value = classItem.name
          selectedStudentName.value = '' // 清空学生选择
          messages.value.push({
            content: `已选择班级 ${classItem.name}，后续分析将基于该班级的整体数据。`,
            isUser: false
          })
        }
      } else {
        selectedClassName.value = ''
      }
    }

    // 拖拽功能
    const isDragging = ref(false)
    const dragStartX = ref(0)
    const dragStartY = ref(0)
    const chatPosition = ref({ bottom: '50px', right: '50px' })

    const handleDragStart = (e) => {
      isDragging.value = true
      dragStartX.value = e.clientX
      dragStartY.value = e.clientY
      document.addEventListener('mousemove', handleDragMove)
      document.addEventListener('mouseup', handleDragEnd)
    }

    const handleDragMove = (e) => {
      if (!isDragging.value) return
      const deltaX = e.clientX - dragStartX.value
      const deltaY = e.clientY - dragStartY.value
      const currentRight = parseInt(chatPosition.value.right) || 50
      const currentBottom = parseInt(chatPosition.value.bottom) || 50
      chatPosition.value = {
        right: `${currentRight - deltaX}px`,
        bottom: `${currentBottom + deltaY}px`
      }
      dragStartX.value = e.clientX
      dragStartY.value = e.clientY
    }

    const handleDragEnd = () => {
      isDragging.value = false
      document.removeEventListener('mousemove', handleDragMove)
      document.removeEventListener('mouseup', handleDragEnd)
    }

    const minimizeAssistant = () => {
      isMinimized.value = !isMinimized.value
    }

    onMounted(() => {
      loadData().then(() => {
        // 加载数据后，再加载会话历史
        loadSessionHistory()
      })
    })
    


    return {
      isMinimized,
      messages,
      inputText,
      isLoading,
      selectedStudentId,
      selectedClassId,
      selectedStudentName,
      selectedClassName,
      students,
      classes,
      teacherQuickQuestions,
      sendMessage,
      quickAsk,
      clearChatHistory,
      onStudentChange,
      onClassChange,
      handleDragStart,
      minimizeAssistant,
      chatPosition,
      showAnalysisTips,
      analysisTips
    }
  }
}
</script>

<style scoped>
/* 教师端AI助手专用样式 - 只在教师端显示 */
.teacher-ai-assistant {
  position: fixed;
  bottom: 50px;
  right: 50px;
  width: 450px;
  max-height: 600px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
  z-index: 1000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.3s ease;
}

/* 最小化状态样式 */
.teacher-ai-assistant.minimized {
  width: 60px;
  max-height: 60px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
}

/* 教师端头部样式 - 始终显示 */
.teacher-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px;
  cursor: move;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 10px;
  transition: all 0.3s ease;
}

/* 最小化状态下的头部样式 */
.teacher-ai-assistant.minimized .teacher-header {
  padding: 0;
  border-bottom: none;
  justify-content: center;
  height: 60px;
}

/* 助手图标容器 - 始终显示 */
.assistant-icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  flex-shrink: 0;
}

/* 最小化状态下的图标容器 */
.teacher-ai-assistant.minimized .assistant-icon-container {
  width: 50px;
  height: 50px;
  background: transparent;
}

/* 助手内容区域 - 正常状态显示 */
.assistant-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  transition: all 0.3s ease;
}

/* 最小化状态下隐藏内容 */
.teacher-ai-assistant.minimized .assistant-content {
  display: none;
}

/* 最小化按钮 - 始终显示 */
.teacher-ai-assistant .minimize-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 最小化状态下的最小化按钮 */
.teacher-ai-assistant.minimized .minimize-btn {
  display: none;
}

.assistant-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.teacher-icon {
  font-size: 24px;
  background: rgba(255, 255, 255, 0.2);
  padding: 8px;
  border-radius: 8px;
}

.teacher-badge {
  background: rgba(255, 255, 255, 0.3);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  margin-left: auto;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

/* 学生和班级选择器 - 教师端专用 */
.student-selector,
.class-selector {
  flex: 1;
  padding: 6px 12px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.student-selector:hover,
.class-selector:hover {
  background: rgba(255, 255, 255, 0.3);
}

.student-selector option,
.class-selector option {
  background: #667eea;
  color: white;
}

/* 消息区域 */
.assistant-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: white;
  max-height: 400px;
}

.message {
  margin-bottom: 16px;
  padding: 12px;
  border-radius: 8px;
}

.message.user {
  background: #f0f4ff;
  margin-left: 20%;
}

.message:not(.user) {
  background: #f8f9fa;
  margin-right: 20%;
}

.context-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: #e3f2fd;
  color: #1976d2;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  margin-bottom: 8px;
  font-weight: 500;
}

/* 教师端快速问题 */
.teacher-quick {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px dashed #e0e0e0;
}

.teacher-quick-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  margin: 4px;
}

.teacher-quick-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

/* 输入区域 */
.assistant-input {
  display: flex;
  gap: 8px;
  padding: 16px;
  background: white;
  border-top: 1px solid #e0e0e0;
}

.teacher-input {
  flex: 1;
  padding: 10px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.teacher-input:focus {
  outline: none;
  border-color: #667eea;
}

.teacher-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.teacher-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.teacher-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* AI分析结果解读提示样式 */
.teacher-analysis-tips {
  margin-top: 20px;
  padding: 16px;
  background: #e3f2fd;
  border: 2px solid #bbdefb;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(187, 222, 251, 0.3);
  transition: all 0.3s ease;
}

.tips-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1976d2;
  display: flex;
  align-items: center;
  gap: 6px;
}

.tips-list {
  margin: 0;
  padding-left: 20px;
  list-style: none;
  font-size: 13px;
  line-height: 1.6;
}

.tips-list li {
  margin-bottom: 8px;
  color: #333;
  position: relative;
}

.tips-list li::before {
  content: "•";
  color: #42a5f5;
  font-weight: bold;
  display: inline-block;
  width: 1em;
  margin-left: -1em;
  font-size: 16px;
}

/* 操作提示样式 */
.teacher-operation-tips {
  margin-top: 12px;
  padding: 12px;
  background: #fff3cd;
  border: 1px solid #ffeeba;
  border-radius: 8px;
  font-size: 12px;
  color: #856404;
  transition: all 0.3s ease;
}

.tip-item {
  margin: 0;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .teacher-ai-assistant {
    width: calc(100% - 20px);
    right: 10px;
    bottom: 10px;
  }
}
</style>

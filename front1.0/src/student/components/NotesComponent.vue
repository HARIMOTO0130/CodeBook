<template>
  <div class="notes-component">
    <!-- 笔记列表 -->
    <div 
      class="notes-sidebar"
      :style="{ width: `${sidebarWidth}px` }"
    >
      <!-- 右侧拖动手柄 -->
      <div 
        class="resize-handle right"
        @mousedown="startResize($event, 'right')"
        @touchstart="startResize($event, 'right', true)"
        title="拖动调整宽度"
      ></div>
      <div class="sidebar-header">
        <h3>我的笔记</h3>
        <button class="new-note-btn" @click="createNewNote" :disabled="isLoading">
          <span v-if="isLoading">✍️ 创建中...</span>
          <span v-else>+ 新建笔记</span>
        </button>
      </div>
      <div class="notes-filter">
        <input 
          v-model="searchQuery" 
          placeholder="搜索笔记..." 
          class="notes-search-input"
          @input="handleSearch"
        />
        <select v-model="selectedTag" @change="handleFilter" class="notes-filter-select">
          <option value="">所有标签</option>
          <option v-for="tag in tags" :key="tag.id" :value="tag.id">
            {{ tag.name }}
          </option>
        </select>
      </div>
      <div class="notes-list">
        <div 
          v-for="(note, index) in filteredNotes" 
          :key="note.id"
          :class="['note-item', { active: activeNoteIndex === index }]"
          @click="selectNote(index)"
        >
          <div class="note-title">{{ note?.title || '无标题笔记' }}</div>
          <div class="note-meta">
            <span class="note-date">{{ formatDate(note?.created_at) }}</span>
            <span v-if="note.is_favorite" class="note-favorite">★</span>
          </div>
          <div class="note-tags">
            <span 
              v-for="tag in (note.tags_data || note.tags || [])" 
              :key="tag.id"
              class="note-tag"
              :style="{ backgroundColor: tag.color }"
            >
              {{ tag.name }}
            </span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 笔记编辑器 -->
    <div class="notes-editor">
      <div v-if="activeNote" class="editor-content">
        <div class="editor-content-scrollable">
          <input 
            type="text" 
            v-model="activeNote.title" 
            class="note-title-input" 
            placeholder="笔记标题" 
            @input="autoSave"
            @focus="saveStatus.value = '正在编辑...'"
            @blur="autoSave"
            ref="titleInput"
          />
          
          <!-- 笔记工具栏 -->
          <div class="note-toolbar">
            <div class="toolbar-group">
              <button @click="format('bold')" class="toolbar-btn" title="加粗">B</button>
              <button @click="format('italic')" class="toolbar-btn" title="斜体">I</button>
              <button @click="format('underline')" class="toolbar-btn" title="下划线">U</button>
              <button @click="format('strike')" class="toolbar-btn" title="删除线">S</button>
            </div>
            <div class="toolbar-group">
              <button @click="format('list', 'ordered')" class="toolbar-btn" title="有序列表">1.</button>
              <button @click="format('list', 'bullet')" class="toolbar-btn" title="无序列表">•</button>
              <button @click="format('code-block')" class="toolbar-btn" title="代码块">{ }</button>
              <button @click="insertImage" class="toolbar-btn" title="插入图片">📷</button>
            </div>
            <div class="toolbar-group">
              <button @click="toggleFavorite" class="toolbar-btn" :class="{ active: activeNote.is_favorite }" title="收藏">★</button>
              <button @click="showVersions" class="toolbar-btn" title="版本历史">⏱</button>
              <button @click="showTagsPanel" class="toolbar-btn" title="标签管理">🏷</button>
            </div>
          </div>
          
          <!-- 富文本编辑器 -->
          <div ref="editor" class="note-content-editor"></div>
        </div>
        
        <div class="editor-footer">
          <div class="footer-left">
            <span class="note-status" :class="{ 'status-success': saveStatus === '已保存', 'status-error': saveStatus === '保存失败' }">
              {{ saveStatus || '未保存' }}
            </span>
            <span v-if="activeNote?.id" class="note-id-hint">笔记ID: {{ activeNote.id }}</span>
          </div>
          <div class="editor-actions">
            <button 
              class="btn btn-danger" 
              @click="deleteNote"
              :disabled="!activeNote || !activeNote.id || isLoading"
              title="删除当前笔记"
            >
              <span v-if="isLoading && deleting">删除中...</span>
              <span v-else>🗑️ 删除笔记</span>
            </button>
            <button 
              class="btn btn-primary btn-save" 
              @click="saveNote"
              :disabled="!activeNote || isLoading"
              title="保存当前笔记"
            >
              <span v-if="isLoading && saving">保存中...</span>
              <span v-else>💾 保存笔记</span>
            </button>
          </div>
        </div>
      </div>
      <div v-else class="no-note-selected">
        <div class="empty-note-icon">📝</div>
        <h3>没有选中笔记</h3>
        <p>请从左侧选择一个现有笔记或创建新笔记开始编辑</p>
        <button class="btn btn-primary create-note-btn" @click="createNewNote" :disabled="isLoading">
          <span v-if="isLoading">✍️ 创建中...</span>
          <span v-else>+ 创建新笔记</span>
        </button>
      </div>
    </div>
    
    <!-- 标签面板 -->
    <div v-if="showTags" class="tags-panel">
      <div class="tags-panel-header">
        <h4>标签管理</h4>
        <button class="close-btn" @click="showTags = false">×</button>
      </div>
      <div class="tags-panel-content">
        <div class="tags-list">
          <div 
            v-for="tag in tags" 
            :key="tag.id"
            class="tag-item"
            :class="{ active: isTagSelected(tag.id) }"
            @click="toggleTag(tag.id)"
          >
            <span class="tag-color" :style="{ backgroundColor: tag.color }"></span>
            <span class="tag-name">{{ tag.name }}</span>
            <span class="tag-count">{{ getTagCount(tag.id) }}</span>
          </div>
        </div>
        <div class="tags-add">
          <input 
            v-model="newTagName" 
            placeholder="输入标签名" 
            class="tag-input"
            @keydown.enter="addTag"
          />
          <input 
            type="color" 
            v-model="newTagColor" 
            class="tag-color-picker"
          />
          <button class="btn btn-primary btn-sm" @click="addTag">添加标签</button>
        </div>
      </div>
    </div>
    
    <!-- 版本历史面板 -->
    <div v-if="showVersionHistory" class="versions-panel">
      <div class="versions-panel-header">
        <h4>版本历史</h4>
        <button class="close-btn" @click="showVersionHistory = false">×</button>
      </div>
      <div class="versions-list">
        <div 
          v-for="version in versions" 
          :key="version.id"
          class="version-item"
        >
          <div class="version-info">
            <span class="version-number">v{{ version.version_number }}</span>
            <span class="version-date">{{ formatDate(version.created_at) }}</span>
          </div>
          <button 
            class="btn btn-sm btn-primary"
            @click="restoreVersion(version.id)"
          >
            恢复
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import Quill from 'quill'
import 'quill/dist/quill.snow.css'
import Prism from 'prismjs'
import 'prismjs/themes/prism.css'
import { api } from '../api/api.js'

// 设置Quill编辑器的主题和模块
const quillOptions = {
  theme: 'snow',
  modules: {
    toolbar: false,
    // 添加性能优化配置
    history: {
      delay: 2000, // 延迟记录历史记录，提高输入性能
      maxStack: 50, // 最大历史记录数量
      userOnly: true // 只记录用户操作
    }
  },
  placeholder: '开始记录你的学习笔记...',
  // 性能优化：禁用不必要的格式检测
  formats: [
    'bold', 'italic', 'underline', 'strike',
    'list', 'bullet', 'code-block', 'image'
  ]
}

export default {
  name: 'NotesComponent',
  props: {
    // 从父组件传递的上下文信息
    bookId: {
      type: [Number, String],
      default: null
    },
    chapterId: {
      type: [Number, String],
      default: null
    },
    // 从外部传入的笔记ID，用于打开特定笔记
    noteId: {
      type: [Number, String],
      default: null
    }
  },
  setup(props) {
    // 编辑器引用
    const editor = ref(null)
    const titleInput = ref(null)
    let quill = null
    let saveTimer = null
    
    // 状态管理
    const notes = ref([])
    const filteredNotes = ref([])
    const tags = ref([])
    const activeNoteIndex = ref(-1)
    const activeNote = ref(null)
    const saveStatus = ref('')
    const isLoading = ref(false)
    const saving = ref(false)
    const deleting = ref(false)
    
    // 搜索和过滤
    const searchQuery = ref('')
    const selectedTag = ref('')
    
    // 标签面板
    const showTags = ref(false)
    const newTagName = ref('')
    const newTagColor = ref('#409EFF')
    
    // 版本历史
    const showVersionHistory = ref(false)
    const versions = ref([])
    
    // 拖动调整大小
    const isResizing = ref(false)
    const resizeData = ref({})
    const sidebarWidth = ref(300) // 默认宽度
    const minSidebarWidth = ref(250) // 最小宽度
    const maxSidebarWidth = ref(500) // 最大宽度
    
    // API配置
    const API_BASE_URL = '/api/learning'
    
    // 获取笔记列表
    const fetchNotes = async () => {
      // 检查是否已登录
      const token = localStorage.getItem('token')
      console.log('获取笔记列表 - Token存在:', !!token)
      if (!token) {
        // 未登录时静默处理，不显示错误
        console.log('获取笔记列表 - 未登录，清空笔记列表')
        notes.value = []
        filteredNotes.value = []
        return
      }
      
      try {
        isLoading.value = true
        console.log('获取笔记列表 - 发送请求')
        const response = await api.getNotes()
        console.log('获取笔记列表 - 收到响应:', response)
        console.log('获取笔记列表 - 响应类型:', typeof response)
        console.log('获取笔记列表 - 是否为数组:', Array.isArray(response))
        
        // 处理分页响应：如果响应有 results 字段，使用 results 数组；否则直接使用响应
        const notesData = response.results || response;
        // 确保获取到的数据是数组格式
        notes.value = Array.isArray(notesData) ? notesData : []
        filteredNotes.value = [...notes.value]
        console.log('获取笔记列表 - 更新后的笔记数量:', notes.value.length)
      } catch (error) {
        // 401错误表示未授权，静默处理
        console.error('获取笔记列表 - 请求失败:', error)
        if (error.message && error.message.includes('AUTH 401')) {
          notes.value = []
          filteredNotes.value = []
        } else {
          console.error('获取笔记失败:', error)
          notes.value = []
          filteredNotes.value = []
        }
      } finally {
        isLoading.value = false
      }
    }
    
    // 获取标签列表
    const fetchTags = async () => {
      // 检查是否已登录
      const token = localStorage.getItem('token')
      if (!token) {
        // 未登录时静默处理，不显示错误
        tags.value = []
        return
      }
      
      try {
        const response = await api.getNoteTags()
        // 确保获取到的数据是数组格式
        tags.value = Array.isArray(response) ? response : []
      } catch (error) {
        // 401错误表示未授权，静默处理
        if (error.message && error.message.includes('AUTH 401')) {
          tags.value = []
        } else {
          console.error('获取标签失败:', error)
          tags.value = []
        }
      }
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }
    
    // 创建新笔记
    const createNewNote = async () => {
      try {
        isLoading.value = true
        const newNote = {
          title: '无标题笔记',
          content: ' '
        }
        
        // 只有在bookId和chapterId有值时才添加
        if (props.bookId) {
          newNote.book = props.bookId
        }
        if (props.chapterId) {
          newNote.chapter = props.chapterId
        }
        
        console.log('创建笔记，发送数据:', newNote)
        const response = await api.createNote(newNote)
        console.log('创建笔记成功，返回数据:', response)
        console.log('返回数据的ID:', response.id)
        console.log('返回数据类型:', typeof response)
        
        notes.value.unshift(response)
        filteredNotes.value = [...notes.value]
        
        console.log('更新后的notes数组:', notes.value)
        console.log('更新后的filteredNotes数组:', filteredNotes.value)
        
        // 使用 nextTick 确保 DOM 更新后再选择笔记
        await nextTick()
        selectNote(0)
        
        saveStatus.value = '笔记已创建'
        setTimeout(() => {
          saveStatus.value = ''
        }, 2000)
      } catch (error) {
        console.error('创建笔记失败:', error)
        console.error('错误详情:', error.response?.data || error.message)
        alert(`创建笔记失败: ${error.response?.data?.detail || error.message || '未知错误，请重试'}`)
      } finally {
        isLoading.value = false
      }
    }
    
    // 选择笔记
    const selectNote = (index) => {
      console.log('选择笔记 - 索引:', index)
      console.log('选择笔记 - filteredNotes数组:', filteredNotes.value)
      
      // 验证索引和数组有效性
      if (index < 0 || index >= filteredNotes.value.length) {
        console.error('选择笔记 - 无效索引:', index)
        return
      }
      
      const noteToSelect = filteredNotes.value[index]
      if (!noteToSelect) {
        console.error('选择笔记 - 笔记不存在:', noteToSelect)
        return
      }
      
      console.log('选择笔记 - 要选择的笔记:', noteToSelect)
      
      activeNoteIndex.value = index
      activeNote.value = { ...noteToSelect } // 深拷贝，避免直接修改
      
      console.log('选择笔记 - activeNote:', activeNote.value)
      console.log('选择笔记 - activeNote.id:', activeNote.value.id)
      
      // 确保content字段存在
      if (!activeNote.value.content) {
        activeNote.value.content = ''
      }
      
      // 初始化编辑器内容
      if (quill && activeNote.value) {
        quill.root.innerHTML = activeNote.value.content
      }
      
      // 获取版本历史
      if (activeNote.value.id) {
        fetchVersions(activeNote.value.id)
      }
    }
    
    // 保存笔记
    const saveNote = async () => {
      console.log('保存笔记 - 开始')
      console.log('保存笔记 - activeNote:', activeNote.value)
      console.log('保存笔记 - activeNote.id:', activeNote.value?.id)
      console.log('保存笔记 - activeNoteIndex:', activeNoteIndex.value)
      
      if (!activeNote.value) {
        alert('请先创建或选择笔记')
        return
      }
      
      try {
        isLoading.value = true
        saving.value = true
        const content = quill ? quill.root.innerHTML : activeNote.value.content
        
        const noteData = {
          title: activeNote.value.title || '无标题笔记',
          content: content
        }
        
        // 只有在bookId和chapterId有值时才添加
        if (props.bookId) {
          noteData.book = props.bookId
        }
        if (props.chapterId) {
          noteData.chapter = props.chapterId
        }
        
        console.log('保存笔记 - 要发送的数据:', noteData)
        console.log('保存笔记 - 笔记ID:', activeNote.value.id)
        
        // 更严格地检查笔记ID：确保ID存在且有效（不为null、undefined或0）
        const noteId = activeNote.value.id
        const hasValidId = noteId != null && noteId !== undefined && noteId !== ''
        
        let response
        // 如果笔记有有效ID，使用更新接口；否则使用创建接口
        if (hasValidId) {
          console.log('保存笔记 - 使用更新接口，ID:', noteId)
          response = await api.updateNote(noteId, noteData)
          console.log('保存笔记 - 更新成功，返回数据:', response)
          
          // 确保返回的响应包含ID
          if (!response.id) {
            console.warn('更新接口返回的数据缺少ID，使用原始ID')
            response.id = noteId
          }
          
          // 更新本地笔记列表
          const noteIndex = notes.value.findIndex(n => n.id === noteId)
          if (noteIndex !== -1) {
            notes.value[noteIndex] = response
            filteredNotes.value = [...notes.value]
            activeNote.value = { ...response }
          } else {
            // 如果在列表中找不到，直接更新activeNote
            activeNote.value = { ...response }
          }
        } else {
          // 新笔记，使用创建接口
          console.log('保存笔记 - 使用创建接口（ID无效或不存在）')
          response = await api.createNote(noteData)
          console.log('保存笔记 - 创建成功，返回数据:', response)
          
          // 确保返回的响应包含ID
          if (!response.id) {
            console.error('创建接口返回的数据缺少ID')
            throw new Error('创建笔记后未能获取笔记ID')
          }
          
          // 更新本地笔记列表和activeNote
          notes.value.unshift(response)
          filteredNotes.value = [...notes.value]
          activeNote.value = { ...response }
          activeNoteIndex.value = 0
        }
        
        saveStatus.value = '已保存'
        setTimeout(() => {
          saveStatus.value = ''
        }, 2000)
      } catch (error) {
        console.error('保存笔记失败:', error)
        console.error('错误详情:', error.response?.data || error.message)
        saveStatus.value = '保存失败'
        
        // 显示详细错误信息
        const errorMsg = error.response?.data?.error || error.response?.data?.detail || error.message || '未知错误'
        alert(`保存笔记失败: ${errorMsg}`)
        
        // 5秒后自动清除失败状态
        setTimeout(() => {
          saveStatus.value = ''
        }, 5000)
      } finally {
        isLoading.value = false
        saving.value = false
      }
    }
    
    // 删除笔记
    const deleteNote = async () => {
      if (!activeNote.value || activeNoteIndex.value < 0) return
      
      const noteId = activeNote.value.id
      if (!isValidNoteId(noteId)) {
        alert('笔记ID无效，无法删除')
        return
      }
      
      if (confirm(`确定要删除笔记"${activeNote.value.title || '无标题'}"吗？此操作不可恢复！`)) {
        try {
          isLoading.value = true
          deleting.value = true
          await api.deleteNote(noteId)
          
          // 从列表中移除
          const noteIndex = notes.value.findIndex(n => n.id === noteId)
          if (noteIndex !== -1) {
            notes.value.splice(noteIndex, 1)
            filteredNotes.value = [...notes.value]
          }
          
          if (filteredNotes.value.length > 0) {
            selectNote(Math.min(activeNoteIndex.value, filteredNotes.value.length - 1))
          } else {
            activeNoteIndex.value = -1
            activeNote.value = null
            if (quill) {
              quill.root.innerHTML = ''
            }
          }
          
          saveStatus.value = '笔记已删除'
          setTimeout(() => {
            saveStatus.value = ''
          }, 2000)
        } catch (error) {
          console.error('删除笔记失败:', error)
          const errorMsg = error.response?.data?.error || error.response?.data?.detail || error.message || '未知错误'
          alert(`删除笔记失败: ${errorMsg}`)
        } finally {
          isLoading.value = false
          deleting.value = false
        }
      }
    }
    
    // 格式化文本
    const format = (format, value = null) => {
      if (!quill) return
      
      if (value) {
        quill.format(format, value)
      } else {
        const currentFormat = quill.getFormat()
        quill.format(format, !currentFormat[format])
      }
      
      // 自动保存
      autoSave()
    }
    
    // 插入图片
    const insertImage = () => {
      if (!activeNote.value) {
        alert('请先创建或选择笔记')
        return
      }
      
      const noteId = activeNote.value.id
      if (!isValidNoteId(noteId)) {
        alert('笔记ID无效，请先保存笔记')
        return
      }
      
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = 'image/*'
      input.onchange = async (e) => {
        const file = e.target.files[0]
        if (file) {
          try {
            // 再次检查ID，确保在异步操作时仍然有效
            const currentNoteId = activeNote.value?.id
            if (!currentNoteId || currentNoteId === undefined || currentNoteId === null || currentNoteId === '') {
              alert('笔记ID无效，请先保存笔记')
              return
            }
            
            const response = await api.addNoteAttachment(currentNoteId, file)
            
            // 在编辑器中插入图片
            const attachment = response[0]
            const imageUrl = attachment.file
            if (quill) {
              quill.insertEmbed(quill.getSelection().index, 'image', imageUrl)
            }
            
            autoSave()
          } catch (error) {
            console.error('上传图片失败:', error)
            alert('上传图片失败，请重试')
          }
        }
      }
      input.click()
    }
    
    // 自动保存
    const autoSave = () => {
      clearTimeout(saveTimer)
      saveTimer = setTimeout(async () => {
        // 优化体验：添加保存状态提示
        if (activeNote.value) {
          saveStatus.value = '正在保存...'
          try {
            await saveNote()
          } catch (error) {
            console.error('自动保存失败:', error)
            saveStatus.value = '保存失败'
            setTimeout(() => {
              saveStatus.value = ''
            }, 3000)
          }
        }
      }, 3000) // 3秒后自动保存，减少API请求频率
    }
    
    // 检查笔记ID是否有效
    const isValidNoteId = (noteId) => {
      return noteId != null && noteId !== undefined && noteId !== ''
    }
    
    // 开始调整大小
    const startResize = (e, direction = 'right', isTouch = false) => {
      if (isTouch && e.touches) {
        e = e.touches[0]
      }
      
      isResizing.value = true
      
      // 创建带方向参数的事件处理函数
      const resizeHandler = isTouch 
        ? (e) => resize(e.touches ? e.touches[0] : e, direction)
        : (e) => resize(e, direction)
      
      const stopHandler = isTouch ? stopResize : stopResize
      
      document.addEventListener(isTouch ? 'touchmove' : 'mousemove', resizeHandler)
      document.addEventListener(isTouch ? 'touchend' : 'mouseup', stopHandler)
      
      // 保存当前方向和处理函数，以便在stopResize中移除
      resizeData.value = {
        direction,
        resizeHandler,
        isTouch
      }
      
      e.preventDefault()
    }
    
    // 调整大小
    const resize = (e, direction = 'right') => {
      if (!isResizing.value) return
      
      const sidebar = document.querySelector('.notes-sidebar')
      if (!sidebar) return
      
      const rect = sidebar.getBoundingClientRect()
      const component = document.querySelector('.notes-component')
      if (!component) return
      
      const componentRect = component.getBoundingClientRect()
      
      if (direction === 'right') {
        // 右侧手柄：调整侧边栏宽度
        const newWidth = e.clientX - rect.left
        // 限制最小和最大宽度
        const minWidth = Math.min(minSidebarWidth.value, 200)
        // 使用父容器宽度来限制最大宽度，确保不超出父容器边界
        const maxWidth = Math.min(maxSidebarWidth.value, componentRect.width - 100) // 预留100px给编辑器
        if (newWidth >= minWidth && newWidth <= maxWidth) {
          sidebarWidth.value = newWidth
        }
      }
    }
    
    // 停止调整大小
    const stopResize = () => {
      isResizing.value = false
      
      // 移除事件监听器
      if (resizeData.value.resizeHandler) {
        document.removeEventListener('mousemove', resizeData.value.resizeHandler)
        document.removeEventListener('touchmove', resizeData.value.resizeHandler)
        resizeData.value = {}
      }
      
      document.removeEventListener('mouseup', stopResize)
      document.removeEventListener('touchend', stopResize)
    }
    
    // 切换收藏状态
    const toggleFavorite = async () => {
      if (!activeNote.value) return
      
      const noteId = activeNote.value.id
      if (!isValidNoteId(noteId)) {
        alert('笔记ID无效，请先保存笔记')
        return
      }
      
      try {
        const response = await api.toggleNoteFavorite(noteId)
        activeNote.value.is_favorite = response.is_favorite
        
        // 更新本地笔记列表
        const noteIndex = notes.value.findIndex(n => n.id === noteId)
        if (noteIndex !== -1) {
          notes.value[noteIndex].is_favorite = response.is_favorite
          filteredNotes.value = [...notes.value]
        }
      } catch (error) {
        console.error('切换收藏状态失败:', error)
        alert('切换收藏状态失败，请重试')
      }
    }
    
    // 添加标签
    const addTag = async () => {
      if (!newTagName.value.trim()) return
      
      try {
        const response = await api.createNoteTag({
          name: newTagName.value.trim(),
          color: newTagColor.value
        })
        
        tags.value.push(response)
        newTagName.value = ''
        newTagColor.value = '#409EFF'
      } catch (error) {
        console.error('创建标签失败:', error)
        alert('创建标签失败，请重试')
      }
    }
    
    // 切换标签显示
    const showTagsPanel = () => {
      showTags.value = !showTags.value
    }
    
    // 切换标签选择
    const toggleTag = async (tagId) => {
      if (!activeNote.value) return
      
      const noteId = activeNote.value.id
      if (!isValidNoteId(noteId)) {
        alert('笔记ID无效，请先保存笔记')
        return
      }
      
      try {
        const isSelected = isTagSelected(tagId)
        if (isSelected) {
          // 移除标签
          await api.removeNoteTag(noteId, tagId)
        } else {
          // 添加标签
          await api.addNoteTag(noteId, tagId)
        }
        
        // 刷新笔记数据
        const response = await api.updateNote(noteId, {}) // 获取最新笔记数据
        if (!response.id) {
          response.id = noteId // 确保响应包含ID
        }
        activeNote.value = response
        
        // 更新本地笔记列表
        const noteIndex = notes.value.findIndex(n => n.id === noteId)
        if (noteIndex !== -1) {
          notes.value[noteIndex] = response
          filteredNotes.value = [...notes.value]
        }
      } catch (error) {
        console.error('更新标签失败:', error)
        alert('更新标签失败，请重试')
      }
    }
    
    // 检查标签是否被选中
    const isTagSelected = (tagId) => {
      if (!activeNote.value || !activeNote.value.tags) return false
      return activeNote.value.tags.some(tag => tag.id === tagId)
    }
    
    // 获取标签使用数量
    const getTagCount = (tagId) => {
      return notes.value.filter(note => 
        note.tags.some(tag => tag.id === tagId)
      ).length
    }
    
    // 搜索笔记
    const handleSearch = () => {
      filterNotes()
    }
    
    // 过滤笔记
    const handleFilter = () => {
      filterNotes()
    }
    
    // 过滤笔记列表
    const filterNotes = () => {
      let result = [...notes.value]
      
      // 搜索过滤
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(note => 
          note.title.toLowerCase().includes(query) ||
          note.content.toLowerCase().includes(query)
        )
      }
      
      // 标签过滤
      if (selectedTag.value) {
        result = result.filter(note => 
          note.tags.some(tag => tag.id === parseInt(selectedTag.value))
        )
      }
      
      filteredNotes.value = result
    }
    
    // 获取版本历史
    const fetchVersions = async (noteId) => {
      if (!isValidNoteId(noteId)) {
        versions.value = []
        return
      }
      
      try {
        const response = await api.getNoteVersions(noteId)
        versions.value = response
      } catch (error) {
        console.error('获取版本历史失败:', error)
        versions.value = []
      }
    }
    
    // 显示版本历史
    const showVersions = () => {
      showVersionHistory.value = !showVersionHistory.value
    }
    
    // 恢复版本
    const restoreVersion = async (versionId) => {
      if (!activeNote.value) return
      
      const noteId = activeNote.value.id
      if (!isValidNoteId(noteId)) {
        alert('笔记ID无效，请先保存笔记')
        return
      }
      
      try {
        await api.restoreNoteVersion(noteId, versionId)
        
        // 重新获取笔记数据
        const response = await api.updateNote(noteId, {}) // 获取最新笔记数据
        if (!response.id) {
          response.id = noteId // 确保响应包含ID
        }
        activeNote.value = response
        
        // 更新编辑器内容
        if (quill) {
          quill.root.innerHTML = activeNote.value.content
        }
        
        // 更新本地笔记列表
        const noteIndex = notes.value.findIndex(n => n.id === noteId)
        if (noteIndex !== -1) {
          notes.value[noteIndex] = response
          filteredNotes.value = [...notes.value]
        }
        
        // 关闭版本历史面板
        showVersionHistory.value = false
        
        saveStatus.value = '版本已恢复'
        setTimeout(() => {
          saveStatus.value = ''
        }, 2000)
      } catch (error) {
        console.error('恢复版本失败:', error)
        alert('恢复版本失败，请重试')
      }
    }
    
    // 组件挂载时初始化
    onMounted(() => {
      // 获取笔记列表和标签
      fetchNotes()
      fetchTags()
    })
    
    // 监听外部传入的noteId，用于打开特定笔记
    watch(() => props.noteId, async (newNoteId) => {
      if (newNoteId) {
        // 等待笔记列表加载完成
        await fetchNotes()
        
        // 查找对应的笔记索引
        const noteIndex = filteredNotes.value.findIndex(note => note.id === Number(newNoteId))
        
        if (noteIndex !== -1) {
          // 选中该笔记
          selectNote(noteIndex)
        }
      }
    }, { immediate: true })
    
    // 监听编辑器引用变化，确保DOM元素存在后再初始化
    watch(editor, (newValue) => {
      if (newValue && !quill) {
        try {
          // 初始化Quill编辑器
          quill = new Quill(newValue, quillOptions)
          
          // 监听编辑器内容变化，自动保存
          quill.on('text-change', autoSave)
          
          // 如果当前有选中的笔记，设置编辑器内容
          if (activeNote.value) {
            quill.root.innerHTML = activeNote.value.content
          }
        } catch (error) {
          console.error('初始化Quill编辑器失败:', error)
        }
      } else if (!newValue && quill) {
        // 如果编辑器元素被移除，清理Quill实例
        quill = null
      }
    })
    
    // 监听activeNote变化，当有笔记被选中时确保编辑器已初始化
    watch(() => activeNote.value, (newValue) => {
      // 当有笔记被选中时，更新编辑器内容
      if (newValue && quill) {
        quill.root.innerHTML = newValue.content
      }
    })
    
    // 组件卸载前清理
    onBeforeUnmount(() => {
      clearTimeout(saveTimer)
    })
    
    // 监听笔记标题变化，自动保存
    watch(() => activeNote.value?.title, () => {
      autoSave()
    })
    
    return {
      editor,
      titleInput,
      notes,
      filteredNotes,
      tags,
      activeNoteIndex,
      activeNote,
      saveStatus,
      isLoading,
      searchQuery,
      selectedTag,
      showTags,
      newTagName,
      newTagColor,
      showVersionHistory,
      versions,
      sidebarWidth,
      
      formatDate,
      createNewNote,
      selectNote,
      saveNote,
      deleteNote,
      format,
      insertImage,
      toggleFavorite,
      showTagsPanel,
      addTag,
      toggleTag,
      isTagSelected,
      getTagCount,
      handleSearch,
      handleFilter,
      showVersions,
      restoreVersion,
      startResize
    }
  }
}
</script>

<style scoped>
/* 引入Quill样式 */
@import 'quill/dist/quill.snow.css';
@import 'prismjs/themes/prism.css';

/* 现代设计变量 */
:root {
  --primary-color: #409EFF;
  --success-color: #67C23A;
  --danger-color: #F56C6C;
  --warning-color: #E6A23C;
  --info-color: #909399;
  --border-color: #E4E7ED;
  --background-color: #F5F7FA;
  --text-color: #303133;
  --text-color-secondary: #606266;
  --text-color-placeholder: #C0C4CC;
  --border-radius: 8px;
  --box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  --transition: all 0.3s cubic-bezier(0.645, 0.045, 0.355, 1);
}

.notes-component {
  display: flex;
  flex-direction: row;
  height: 100%;
  max-height: 100%;
  width: 100%;
  max-width: 100%;
  position: relative;
  overflow: hidden;
  box-sizing: border-box;
  background-color: #fff;
  padding: 0;
  margin: 0;
}

/* 笔记侧边栏 */
.notes-sidebar {
  width: 300px;
  height: 100%;
  max-width: 100%;
  border-right: 1px solid var(--border-color);
  border-bottom: none;
  display: flex;
  flex-direction: column;
  background-color: var(--background-color);
  transition: width 0.1s ease;
  position: relative;
  box-sizing: border-box;
  overflow: hidden;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.05);
}

.sidebar-header {
  padding: 20px 15px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  color: var(--text-color);
  font-weight: 600;
}

.new-note-btn {
  background: var(--primary-color);
  color: white;
  border: 2px solid var(--primary-color);
  padding: 8px 16px;
  border-radius: var(--border-radius);
  font-size: 14px;
  cursor: pointer;
  transition: var(--transition);
  box-shadow: 0 2px 4px rgba(64, 158, 255, 0.2);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
}

.new-note-btn:hover {
  background: #66b1ff;
  border-color: #66b1ff;
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.3);
  transform: translateY(-1px);
}

.new-note-btn:disabled {
  background: var(--info-color);
  border-color: var(--info-color);
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
  box-shadow: none;
}

/* 笔记过滤 */
.notes-filter {
  padding: 15px;
  border-bottom: 1px solid var(--border-color);
  background-color: #fff;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.notes-search-input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 14px;
  margin-bottom: 0;
  transition: var(--transition);
  background-color: #fff;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.notes-search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.notes-filter-select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 14px;
  background-color: #fff;
  transition: var(--transition);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  cursor: pointer;
}

.notes-filter-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

/* 笔记列表 */
.notes-list {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 10px 15px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.note-item {
  padding: 15px;
  margin-bottom: 0;
  border-radius: var(--border-radius);
  cursor: pointer;
  transition: var(--transition);
  border: 1px solid transparent;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow: hidden;
}

.note-item:hover {
  background-color: #fafafa;
  border-color: var(--primary-color);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.note-item.active {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.note-item.active .note-title,
.note-item.active .note-date {
  color: #fff;
}

.note-item.active .note-favorite {
  color: #fff;
}

.note-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-color);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  line-height: 1.4;
}

.note-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-size: 12px;
  color: var(--text-color-secondary);
}

.note-date {
  font-size: 12px;
  color: var(--text-color-secondary);
}

.note-favorite {
  color: #f7ba2a;
  margin-left: 6px;
  font-size: 14px;
}

.note-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 8px;
}

.note-tag {
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 11px;
  color: #fff;
  background-color: var(--primary-color);
  font-weight: 500;
  opacity: 0.9;
  transition: opacity 0.2s;
}

.note-tag:hover {
  opacity: 1;
}

/* 可拖动边框 */
.resize-handle {
  position: absolute;
  z-index: 100;
  transition: background-color 0.2s;
  cursor: col-resize;
}

.resize-handle.right {
  background-color: transparent;
  right: -3px;
  top: 0;
  bottom: 0;
  width: 6px;
}

.resize-handle:hover {
  background-color: rgba(64, 158, 255, 0.5);
}

.resize-handle:active {
  background-color: var(--primary-color);
}

/* 笔记编辑器 */
.notes-editor {
  flex: 1;
  display: flex;
  flex-direction: column;
  background-color: #fff;
  overflow: hidden;
  width: 100%;
  max-width: 100%;
  height: 100%;
  max-height: 100%;
  box-sizing: border-box;
  background-color: #fafafa;
}

.editor-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  max-height: 100%;
  padding: 15px 20px 0;
  overflow: hidden;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  background-color: #fff;
  margin: 10px;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
}

.editor-content-scrollable {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding-bottom: 20px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

/* 确保滚动条样式美观 */
.editor-content-scrollable::-webkit-scrollbar {
  width: 8px;
}

.editor-content-scrollable::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.editor-content-scrollable::-webkit-scrollbar-thumb {
  background: var(--primary-color);
  border-radius: 4px;
}

.editor-content-scrollable::-webkit-scrollbar-thumb:hover {
  background: #66b1ff;
}

.note-title-input {
  width: 100%;
  max-width: 100%;
  border: none;
  font-size: 28px;
  font-weight: 600;
  padding: 15px 0;
  margin-bottom: 20px;
  border-bottom: 2px solid var(--border-color);
  outline: none;
  color: var(--text-color);
  box-sizing: border-box;
  background-color: transparent;
  transition: border-color 0.3s;
}

.note-title-input:focus {
  border-bottom-color: var(--primary-color);
}

/* 笔记工具栏 */
.note-toolbar {
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 12px 16px;
  margin-bottom: 20px;
  background-color: #fff;
  border-radius: var(--border-radius);
  border: 1px solid var(--border-color);
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  flex-wrap: wrap;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.toolbar-group {
  display: flex;
  gap: 8px;
  padding: 4px;
  background-color: var(--background-color);
  border-radius: var(--border-radius);
}

.toolbar-btn {
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: calc(var(--border-radius) - 2px);
  background-color: #fff;
  cursor: pointer;
  font-size: 14px;
  transition: var(--transition);
  color: var(--text-color-secondary);
  min-width: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toolbar-btn:hover {
  background-color: var(--background-color);
  border-color: var(--primary-color);
  color: var(--primary-color);
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.toolbar-btn.active {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  color: #fff;
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.toolbar-btn:disabled:hover {
  background-color: #fff;
  border-color: var(--border-color);
  color: var(--text-color-secondary);
  box-shadow: none;
}

/* 富文本编辑器内容区域 */

/* 没有选中笔记时的空状态 */
.no-note-selected {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  max-height: 100%;
  text-align: center;
  padding: 20px;
  background-color: #fff;
  margin: 10px;
  border-radius: var(--border-radius);
  box-shadow: var(--box-shadow);
  color: var(--text-color-secondary);
}

.empty-note-icon {
  font-size: 64px;
  margin-bottom: 20px;
  opacity: 0.6;
}

.no-note-selected h3 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 10px;
  color: var(--text-color);
}

.no-note-selected p {
  font-size: 16px;
  margin-bottom: 30px;
  max-width: 500px;
  line-height: 1.6;
}

.create-note-btn {
  background: var(--primary-color);
  color: white;
  border: 2px solid var(--primary-color);
  padding: 12px 24px;
  border-radius: var(--border-radius);
  font-size: 16px;
  cursor: pointer;
  transition: var(--transition);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.create-note-btn:hover {
  background: #66b1ff;
  border-color: #66b1ff;
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.3);
  transform: translateY(-1px);
}

.create-note-btn:disabled {
  background: var(--info-color);
  border-color: var(--info-color);
  cursor: not-allowed;
  opacity: 0.7;
  transform: none;
  box-shadow: none;
}
.note-content-editor {
  flex: 1;
  min-height: 150px;
  max-height: calc(100% - 150px); /* 增加减去的高度，确保有足够空间 */
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  overflow: hidden;
  background-color: #fff;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

/* Quill编辑器自定义样式 */
.note-content-editor :deep(.ql-container) {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.note-content-editor :deep(.ql-editor) {
  font-size: 15px;
  line-height: 1.8;
  color: var(--text-color);
  min-height: 400px;
  padding: 20px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  overflow-wrap: break-word;
  word-wrap: break-word;
  word-break: break-word;
  background-color: #fff;
}

.note-content-editor :deep(.ql-editor h1) {
  font-size: 24px;
  font-weight: 600;
  margin: 16px 0;
  color: #333;
}

.note-content-editor :deep(.ql-editor h2) {
  font-size: 20px;
  font-weight: 600;
  margin: 14px 0;
  color: #333;
}

.note-content-editor :deep(.ql-editor h3) {
  font-size: 18px;
  font-weight: 500;
  margin: 12px 0;
  color: #333;
}

.note-content-editor :deep(.ql-editor p) {
  margin: 8px 0;
}

.note-content-editor :deep(.ql-editor ul),
.note-content-editor :deep(.ql-editor ol) {
  margin: 8px 0 8px 20px;
}

.note-content-editor :deep(.ql-editor li) {
  margin: 4px 0;
}

.note-content-editor :deep(.ql-editor pre) {
  background-color: #f5f7fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 12px;
  overflow-x: auto;
  margin: 8px 0;
  max-width: 100%;
  box-sizing: border-box;
  width: 100%;
}

.note-content-editor :deep(.ql-editor code) {
  background-color: #f5f7fa;
  border-radius: 3px;
  padding: 2px 4px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

.note-content-editor :deep(.ql-editor pre code) {
  background-color: transparent;
  padding: 0;
}

.note-content-editor :deep(.ql-editor img) {
  max-width: 100%;
  width: auto;
  height: auto;
  margin: 8px 0;
  display: block;
  box-sizing: border-box;
}

/* 确保 Quill 编辑器的所有容器都适配宽度 */
.note-content-editor :deep(.ql-snow) {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

.note-content-editor :deep(.ql-toolbar) {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

/* 编辑器底部 */
.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0 0;
  border-top: 1px solid var(--border-color);
  margin-top: 20px;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  flex-wrap: wrap;
  gap: 15px;
}

.footer-left {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.note-status {
  font-size: 13px;
  color: var(--text-color-secondary);
  font-weight: 500;
}

.note-status.status-success {
  color: var(--success-color);
}

.note-status.status-error {
  color: var(--danger-color);
}

.note-id-hint {
  font-size: 12px;
  color: var(--text-color-placeholder);
}

.editor-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: var(--border-radius);
  font-size: 14px;
  cursor: pointer;
  transition: var(--transition);
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 120px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.btn-primary {
  background-color: var(--primary-color);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #66b1ff;
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.3);
  transform: translateY(-1px);
}

.btn-primary:active:not(:disabled) {
  background-color: #3a8ee6;
  transform: translateY(0);
}

.btn-primary.btn-save {
  background-color: var(--success-color);
}

.btn-primary.btn-save:hover:not(:disabled) {
  background-color: #85ce61;
  box-shadow: 0 4px 8px rgba(103, 194, 58, 0.3);
  transform: translateY(-1px);
}

.btn-primary.btn-save:active:not(:disabled) {
  background-color: #5daf34;
  transform: translateY(0);
}

.btn-danger {
  background-color: var(--danger-color);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #f78989;
  box-shadow: 0 4px 8px rgba(245, 108, 108, 0.3);
  transform: translateY(-1px);
}

.btn-danger:active:not(:disabled) {
  background-color: #f56c6c;
  transform: translateY(0);
}

.no-note-selected {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-size: 16px;
  background-color: #fafafa;
}

/* 标签面板 */
.tags-panel {
  position: absolute;
  top: 0;
  left: 300px;
  right: 0;
  height: 100%;
  background-color: #fff;
  border-left: 1px solid var(--border-color);
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  width: calc(100% - 300px);
  max-width: calc(100% - 300px);
  box-sizing: border-box;
  border-radius: 0 var(--border-radius) var(--border-radius) 0;
}

.tags-panel-header {
  padding: 20px 15px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--background-color);
}

.tags-panel-header h4 {
  margin: 0;
  font-size: 18px;
  color: var(--text-color);
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-color-secondary);
  cursor: pointer;
  padding: 0;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: var(--transition);
}

.close-btn:hover {
  background-color: var(--primary-color);
  color: #fff;
  transform: rotate(90deg);
}

.tags-panel-content {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .notes-sidebar {
    width: 250px;
  }
  
  .tags-panel,
  .versions-panel {
    left: 250px;
    width: calc(100% - 250px);
    max-width: calc(100% - 250px);
  }
  
  .editor-content {
    margin: 15px;
    padding: 20px;
  }
}

@media (max-width: 768px) {
  .notes-component {
    flex-direction: column;
  }
  
  .notes-sidebar {
    width: 100%;
    height: 250px;
    border-right: none;
    border-bottom: 1px solid var(--border-color);
  }
  
  .resize-handle {
    cursor: row-resize;
  }
  
  .resize-handle.right {
    top: auto;
    bottom: -3px;
    left: 0;
    right: 0;
    width: 100%;
    height: 6px;
  }
  
  .editor-content {
    padding: 15px;
    margin: 10px;
  }
  
  .editor-footer {
    padding: 15px 0 0;
    flex-direction: column;
    align-items: stretch;
  }
  
  .editor-actions {
    width: 100%;
    justify-content: stretch;
  }
  
  .editor-actions .btn {
    flex: 1;
    min-width: 0;
  }
  
  .note-toolbar {
    flex-wrap: wrap;
    gap: 10px;
  }
  
  .toolbar-group {
    margin-bottom: 10px;
    flex-wrap: wrap;
  }
  
  .note-title-input {
    font-size: 24px;
  }
  
  .tags-panel,
  .versions-panel {
    left: 0;
    width: 100%;
    max-width: 100%;
    border-radius: 0;
  }
}

@media (max-width: 480px) {
  .sidebar-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    padding: 15px;
  }
  
  .notes-filter {
    padding: 10px 15px;
  }
  
  .editor-content {
    padding: 15px;
    margin: 5px;
  }
  
  .note-title-input {
    font-size: 20px;
    padding: 12px 0;
  }
  
  .toolbar-btn {
    padding: 6px 10px;
    font-size: 13px;
  }
  
  .editor-actions {
    flex-direction: column;
    gap: 10px;
    width: 100%;
  }
  
  .editor-actions .btn {
    width: 100%;
    padding: 10px;
    font-size: 14px;
  }
  
  .footer-left {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .note-content-editor {
    min-height: 300px;
  }
  
  .note-content-editor :deep(.ql-editor) {
    min-height: 300px;
    padding: 15px;
  }
}

/* 元素间距和排版优化 */
.note-item {
  margin-bottom: 8px;
  padding: 12px 14px;
  transition: all 0.2s;
}

.note-title {
  margin-bottom: 6px;
  font-size: 14px;
  font-weight: 500;
  line-height: 1.4;
}

.note-meta {
  margin-bottom: 6px;
  font-size: 12px;
  color: #909399;
  line-height: 1.3;
}

.note-tags {
  margin-top: 8px;
  gap: 4px;
  display: flex;
  flex-wrap: wrap;
}

.note-tag {
  padding: 2px 6px;
  font-size: 10px;
  border-radius: 3px;
  color: #fff;
  font-weight: 500;
}

.note-content-editor {
  min-height: 300px;
  margin-top: 15px;
  line-height: 1.6;
  font-size: 14px;
}

/* 滚动条样式优化 */
.editor-content-scrollable::-webkit-scrollbar,
.notes-list::-webkit-scrollbar {
  width: 6px;
}

.editor-content-scrollable::-webkit-scrollbar-track,
.notes-list::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.editor-content-scrollable::-webkit-scrollbar-thumb,
.notes-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.editor-content-scrollable::-webkit-scrollbar-thumb:hover,
.notes-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 增强可访问性 */
.note-item:focus-within {
  outline: 2px solid #409EFF;
  outline-offset: -2px;
}

.toolbar-btn:focus,
.btn:focus {
  outline: 2px solid #409EFF;
  outline-offset: 2px;
}

.tags-list {
  margin-bottom: 20px;
}

.tag-item {
  display: flex;
  align-items: center;
  padding: 10px;
  margin-bottom: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid #e4e7ed;
  background-color: #fff;
}

.tag-item:hover {
  background-color: #ecf5ff;
  border-color: #c6e2ff;
}

.tag-item.active {
  background-color: #ecf5ff;
  border-color: #409EFF;
}

.tag-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  margin-right: 10px;
}

.tag-name {
  flex: 1;
  font-size: 14px;
  color: #333;
}

.tag-count {
  font-size: 12px;
  color: #999;
  background-color: #f5f7fa;
  padding: 2px 8px;
  border-radius: 10px;
}

.tags-add {
  display: flex;
  gap: 8px;
  align-items: center;
}

.tag-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 13px;
  transition: border-color 0.3s;
}

.tag-input:focus {
  outline: none;
  border-color: #409EFF;
}

.tag-color-picker {
  width: 40px;
  height: 34px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  padding: 0;
  background: none;
}

/* 版本历史面板 */
.versions-panel {
  position: absolute;
  top: 0;
  left: 300px;
  right: 0;
  height: 100%;
  background-color: #fff;
  border-left: 1px solid var(--border-color);
  box-shadow: 2px 0 12px rgba(0, 0, 0, 0.1);
  z-index: 100;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
  width: calc(100% - 300px);
  max-width: calc(100% - 300px);
  box-sizing: border-box;
  border-radius: 0 var(--border-radius) var(--border-radius) 0;
}

.versions-panel-header {
  padding: 20px 15px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--background-color);
}

.versions-panel-header h4 {
  margin: 0;
  font-size: 18px;
  color: var(--text-color);
  font-weight: 600;
}

.versions-list {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.version-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  margin-bottom: 0;
  border-radius: var(--border-radius);
  border: 1px solid var(--border-color);
  background-color: #fff;
  transition: var(--transition);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.version-item:hover {
  background-color: var(--background-color);
  border-color: var(--primary-color);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.version-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.version-number {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.version-date {
  font-size: 12px;
  color: #999;
}

/* 按钮样式 */
.btn {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  border: none;
  transition: all 0.3s;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.btn-primary {
  background: #409EFF;
  color: white;
}

.btn-primary:hover {
  background: #66b1ff;
}

.btn-secondary {
  background: #f5f5f5;
  color: #666;
}

.btn-secondary:hover {
  background: #e0e0e0;
}
</style>
<template>
  <div class="notes-component">
    <!-- 笔记列表 -->
    <div class="notes-sidebar">
      <div class="sidebar-header">
        <h3>我的笔记</h3>
        <button class="new-note-btn" @click="createNewNote">
          + 新建笔记
        </button>
      </div>
      <div class="notes-list">
        <div 
          v-for="(note, index) in notes" 
          :key="note.id"
          :class="['note-item', { active: activeNoteIndex === index }]"
          @click="selectNote(index)"
        >
          <div class="note-title">{{ note?.title || '无标题笔记' }}</div>
        <div class="note-date">{{ note?.createdAt ? formatDate(note.createdAt) : '' }}</div>
        </div>
      </div>
    </div>
    
    <!-- 笔记编辑器 -->
    <div class="notes-editor">
      <div v-if="activeNote" class="editor-content">
        <input 
          type="text" 
          v-model="activeNote.title" 
          class="note-title-input"
          placeholder="笔记标题"
          @input="saveNote"
        />
        <textarea 
          v-model="activeNote.content"
          class="note-content-input"
          placeholder="开始记录你的学习笔记..."
          @input="saveNote"
          @keydown.ctrl.enter="saveNote"
        ></textarea>
        <div class="editor-footer">
          <span class="note-status">{{ saveStatus }}</span>
          <div class="editor-actions">
            <button class="btn btn-secondary btn-sm" @click="deleteNote">删除笔记</button>
            <button class="btn btn-primary btn-sm" @click="saveNote">保存笔记</button>
          </div>
        </div>
      </div>
      <div v-else class="no-note-selected">
        <p>选择一个笔记或创建新笔记开始编辑</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'NotesComponent',
  setup() {
    const notes = ref([])
    const activeNoteIndex = ref(-1)
    const saveStatus = ref('')
    
    // 当前激活的笔记
    const activeNote = ref(null)
    
    // 本地存储键名
    const NOTES_STORAGE_KEY = 'local_notes'
    
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
    
    // 保存笔记到本地存储
    const saveNotesToStorage = () => {
      try {
        localStorage.setItem(NOTES_STORAGE_KEY, JSON.stringify(notes.value))
      } catch (error) {
        console.error('保存笔记到本地存储失败:', error)
      }
    }
    
    // 从本地存储加载笔记
    const loadNotesFromStorage = () => {
      try {
        const storedNotes = localStorage.getItem(NOTES_STORAGE_KEY)
        if (storedNotes) {
          notes.value = JSON.parse(storedNotes)
        }
      } catch (error) {
        console.error('从本地存储加载笔记失败:', error)
        notes.value = []
      }
    }
    
    // 创建新笔记
    const createNewNote = () => {
      try {
        // 添加时间戳前缀，避免创建多个相同标题的笔记
        const timestamp = new Date().toLocaleTimeString()
        const newNote = {
          id: Date.now().toString(), // 使用时间戳作为唯一ID
          title: `无标题笔记 (${timestamp})`,
          content: '',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString()
        }
        
        notes.value.unshift(newNote)
        saveNotesToStorage()
        selectNote(0)
      } catch (error) {
        console.error('创建笔记失败:', error)
        alert('创建笔记失败，请重试')
      }
    }
    
    // 选择笔记
    const selectNote = (index) => {
      activeNoteIndex.value = index
      activeNote.value = { ...notes.value[index] } // 深拷贝，避免直接修改
    }
    
    // 保存笔记
    const saveNote = () => {
      if (!activeNote.value || activeNoteIndex.value < 0) return
      
      try {
        // 更新笔记内容
        const updatedNote = {
          ...activeNote.value,
          title: activeNote.value.title || '无标题笔记',
          content: activeNote.value.content || '',
          updatedAt: new Date().toISOString()
        }
        
        notes.value[activeNoteIndex.value] = updatedNote
        saveNotesToStorage()
        
        saveStatus.value = '已保存'
        setTimeout(() => {
          saveStatus.value = ''
        }, 2000)
      } catch (error) {
        console.error('保存笔记失败:', error)
        saveStatus.value = '保存失败'
        
        // 5秒后自动清除失败状态
        setTimeout(() => {
          saveStatus.value = ''
        }, 5000)
      }
    }
    
    // 删除笔记
    const deleteNote = () => {
      if (activeNoteIndex.value >= 0 && confirm('确定要删除这条笔记吗？')) {
        try {
          notes.value.splice(activeNoteIndex.value, 1)
          saveNotesToStorage()
          
          if (notes.value.length > 0) {
            selectNote(Math.min(activeNoteIndex.value, notes.value.length - 1))
          } else {
            activeNoteIndex.value = -1
            activeNote.value = null
          }
        } catch (error) {
          console.error('删除笔记失败:', error)
          alert('删除笔记失败，请重试')
        }
      }
    }
    
    // 组件挂载时加载笔记
    onMounted(() => {
      loadNotesFromStorage()
      if (notes.value.length > 0) {
        selectNote(0)
      }
    })
    
    return {
      notes,
      activeNoteIndex,
      activeNote,
      saveStatus,
      formatDate,
      createNewNote,
      selectNote,
      saveNote,
      deleteNote
    }
  }
}
</script>

<style scoped>
.notes-component {
  display: flex;
  height: 100%;
  overflow: hidden;
}

/* 笔记侧边栏 */
.notes-sidebar {
  width: 250px;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.sidebar-header {
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.new-note-btn {
  background: #409EFF;
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.new-note-btn:hover {
  background: #66b1ff;
}

.notes-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

.note-item {
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  border: 1px solid transparent;
}

.note-item:hover {
  background-color: #f5f5f5;
}

.note-item.active {
  background-color: #ecf5ff;
  border-color: #409EFF;
}

.note-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.note-date {
  font-size: 12px;
  color: #999;
}

/* 笔记编辑器 */
.notes-editor {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.editor-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 20px;
}

.note-title-input {
  width: 100%;
  border: none;
  font-size: 20px;
  font-weight: 500;
  padding: 10px 0;
  margin-bottom: 10px;
  border-bottom: 1px solid #e0e0e0;
  outline: none;
}

.note-content-input {
  flex: 1;
  border: none;
  font-size: 14px;
  line-height: 1.6;
  padding: 10px 0;
  resize: none;
  outline: none;
  font-family: inherit;
}

.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
  margin-top: 10px;
}

.note-status {
  font-size: 12px;
  color: #67C23A;
}

.editor-actions {
  display: flex;
  gap: 10px;
}

.no-note-selected {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-size: 16px;
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
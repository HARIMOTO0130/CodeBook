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
        <input 
          type="text" 
          v-model="activeNote.title" 
          class="note-title-input"
          placeholder="笔记标题"
          @input="saveNote"
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
        <p>调试信息: activeNote = {{ activeNote }}, activeNoteIndex = {{ activeNoteIndex }}</p>
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
    toolbar: false
  },
  placeholder: '开始记录你的学习笔记...'
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
    
    // API配置
    const API_BASE_URL = '/api/learning'
    
    // 获取笔记列表
    const fetchNotes = async () => {
      try {
        isLoading.value = true
        const response = await api.getNotes()
        // 确保获取到的数据是数组格式
        notes.value = Array.isArray(response) ? response : []
        filteredNotes.value = [...notes.value]
      } catch (error) {
        console.error('获取笔记失败:', error)
        notes.value = []
        filteredNotes.value = []
      } finally {
        isLoading.value = false
      }
    }
    
    // 获取标签列表
    const fetchTags = async () => {
      try {
        const response = await api.getNoteTags()
        // 确保获取到的数据是数组格式
        tags.value = Array.isArray(response) ? response : []
      } catch (error) {
        console.error('获取标签失败:', error)
        tags.value = []
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
      console.log('选择笔记 - 要选择的笔记:', filteredNotes.value[index])
      
      activeNoteIndex.value = index
      activeNote.value = { ...filteredNotes.value[index] } // 深拷贝，避免直接修改
      
      console.log('选择笔记 - activeNote:', activeNote.value)
      console.log('选择笔记 - activeNote.id:', activeNote.value.id)
      
      // 初始化编辑器内容
      if (quill) {
        quill.root.innerHTML = activeNote.value.content
      }
      
      // 获取版本历史
      fetchVersions(activeNote.value.id)
    }
    
    // 保存笔记
    const saveNote = async () => {
      console.log('保存笔记 - 开始')
      console.log('保存笔记 - activeNote:', activeNote.value)
      console.log('保存笔记 - activeNote.id:', activeNote.value?.id)
      console.log('保存笔记 - activeNoteIndex:', activeNoteIndex.value)
      
      if (!activeNote.value || activeNoteIndex.value < 0) return
      
      try {
        isLoading.value = true
        const content = quill ? quill.root.innerHTML : activeNote.value.content
        
        const updatedNote = {
          ...activeNote.value,
          title: activeNote.value.title || '无标题笔记',
          content: content
        }
        
        console.log('保存笔记 - 要发送的数据:', updatedNote)
        console.log('保存笔记 - 笔记ID:', activeNote.value.id)
        
        const response = await api.updateNote(activeNote.value.id, updatedNote)
        
        console.log('保存笔记 - 成功，返回数据:', response)
        
        // 更新本地笔记列表
        const noteIndex = notes.value.findIndex(n => n.id === activeNote.value.id)
        if (noteIndex !== -1) {
          notes.value[noteIndex] = response
          filteredNotes.value = [...notes.value]
          activeNote.value = { ...response }
        }
        
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
      } finally {
        isLoading.value = false
      }
    }
    
    // 删除笔记
    const deleteNote = async () => {
      if (activeNoteIndex.value >= 0 && confirm('确定要删除这条笔记吗？')) {
        try {
          isLoading.value = true
          await api.deleteNote(activeNote.value.id)
          
          // 从列表中移除
          const noteIndex = notes.value.findIndex(n => n.id === activeNote.value.id)
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
          alert('删除笔记失败，请重试')
        } finally {
          isLoading.value = false
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
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = 'image/*'
      input.onchange = async (e) => {
        const file = e.target.files[0]
        if (file) {
          try {
            const response = await api.addNoteAttachment(activeNote.value.id, file)
            
            // 在编辑器中插入图片
            const attachment = response[0]
            const imageUrl = attachment.file
            quill.insertEmbed(quill.getSelection().index, 'image', imageUrl)
            
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
      saveTimer = setTimeout(() => {
        saveNote()
      }, 2000) // 2秒后自动保存
    }
    
    // 切换收藏状态
    const toggleFavorite = async () => {
      if (!activeNote.value) return
      
      try {
        const response = await api.toggleNoteFavorite(activeNote.value.id)
        activeNote.value.is_favorite = response.is_favorite
        
        // 更新本地笔记列表
        const noteIndex = notes.value.findIndex(n => n.id === activeNote.value.id)
        if (noteIndex !== -1) {
          notes.value[noteIndex].is_favorite = response.is_favorite
          filteredNotes.value = [...notes.value]
        }
      } catch (error) {
        console.error('切换收藏状态失败:', error)
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
      
      try {
        const isSelected = isTagSelected(tagId)
        if (isSelected) {
          // 移除标签
          await api.removeNoteTag(activeNote.value.id, tagId)
        } else {
          // 添加标签
          await api.addNoteTag(activeNote.value.id, tagId)
        }
        
        // 刷新笔记数据
        const response = await api.updateNote(activeNote.value.id, {}) // 获取最新笔记数据
        activeNote.value = response
        
        // 更新本地笔记列表
        const noteIndex = notes.value.findIndex(n => n.id === activeNote.value.id)
        if (noteIndex !== -1) {
          notes.value[noteIndex] = response
          filteredNotes.value = [...notes.value]
        }
      } catch (error) {
        console.error('更新标签失败:', error)
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
      try {
        const response = await api.getNoteVersions(noteId)
        versions.value = response
      } catch (error) {
        console.error('获取版本历史失败:', error)
      }
    }
    
    // 显示版本历史
    const showVersions = () => {
      showVersionHistory.value = !showVersionHistory.value
    }
    
    // 恢复版本
    const restoreVersion = async (versionId) => {
      if (!activeNote.value) return
      
      try {
        await api.restoreNoteVersion(activeNote.value.id, versionId)
        
        // 重新获取笔记数据
        const response = await api.updateNote(activeNote.value.id, {}) // 获取最新笔记数据
        activeNote.value = response
        
        // 更新编辑器内容
        if (quill) {
          quill.root.innerHTML = activeNote.value.content
        }
        
        // 更新本地笔记列表
        const noteIndex = notes.value.findIndex(n => n.id === activeNote.value.id)
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
      restoreVersion
    }
  }
}
</script>

<style scoped>
/* 引入Quill样式 */
@import 'quill/dist/quill.snow.css';
@import 'prismjs/themes/prism.css';

.notes-component {
  display: flex;
  height: 100%;
  overflow: hidden;
  position: relative;
}

/* 笔记侧边栏 */
.notes-sidebar {
  width: 300px;
  border-right: 1px solid #e0e0e0;
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #fafafa;
}

.sidebar-header {
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
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

/* 笔记过滤 */
.notes-filter {
  padding: 10px 15px;
  border-bottom: 1px solid #e0e0e0;
  background-color: #fff;
}

.notes-search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 13px;
  margin-bottom: 8px;
  transition: border-color 0.3s;
}

.notes-search-input:focus {
  outline: none;
  border-color: #409EFF;
}

.notes-filter-select {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 13px;
  background-color: #fff;
  transition: border-color 0.3s;
}

.notes-filter-select:focus {
  outline: none;
  border-color: #409EFF;
}

/* 笔记列表 */
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
  background-color: #fff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.note-item:hover {
  background-color: #f5f7fa;
  border-color: #c6e2ff;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
}

.note-item.active {
  background-color: #ecf5ff;
  border-color: #409EFF;
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.2);
}

.note-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 6px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.note-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 6px;
  font-size: 12px;
  color: #999;
}

.note-date {
  font-size: 12px;
  color: #999;
}

.note-favorite {
  color: #f7ba2a;
  margin-left: 4px;
}

.note-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.note-tag {
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 11px;
  color: #fff;
  background-color: #409EFF;
}

/* 笔记编辑器 */
.notes-editor {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: #fff;
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
  font-size: 24px;
  font-weight: 600;
  padding: 10px 0;
  margin-bottom: 15px;
  border-bottom: 2px solid #f0f0f0;
  outline: none;
  color: #333;
}

.note-title-input:focus {
  border-bottom-color: #409EFF;
}

/* 笔记工具栏 */
.note-toolbar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  margin-bottom: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border: 1px solid #e4e7ed;
}

.toolbar-group {
  display: flex;
  gap: 5px;
}

.toolbar-btn {
  padding: 6px 10px;
  border: 1px solid #dcdfe6;
  border-radius: 3px;
  background-color: #fff;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
  color: #606266;
}

.toolbar-btn:hover {
  background-color: #ecf5ff;
  border-color: #c6e2ff;
  color: #409EFF;
}

.toolbar-btn.active {
  background-color: #409EFF;
  border-color: #409EFF;
  color: #fff;
}

.toolbar-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 富文本编辑器内容区域 */
.note-content-editor {
  flex: 1;
  min-height: 300px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
  background-color: #fff;
}

/* Quill编辑器自定义样式 */
.note-content-editor :deep(.ql-editor) {
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  min-height: 300px;
  padding: 15px;
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
  height: auto;
  margin: 8px 0;
}

/* 编辑器底部 */
.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 15px;
  border-top: 1px solid #e0e0e0;
  margin-top: 15px;
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
  background-color: #fafafa;
}

/* 标签面板 */
.tags-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: 300px;
  height: 100%;
  background-color: #fff;
  border-left: 1px solid #e0e0e0;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 100;
  display: flex;
  flex-direction: column;
}

.tags-panel-header {
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tags-panel-header h4 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: all 0.3s;
}

.close-btn:hover {
  background-color: #f5f7fa;
  color: #666;
}

.tags-panel-content {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
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
  right: 300px;
  width: 300px;
  height: 100%;
  background-color: #fff;
  border-left: 1px solid #e0e0e0;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 100;
  display: flex;
  flex-direction: column;
}

.versions-panel-header {
  padding: 15px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.versions-panel-header h4 {
  margin: 0;
  font-size: 16px;
  color: #333;
}

.versions-list {
  flex: 1;
  padding: 15px;
  overflow-y: auto;
}

.version-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
  background-color: #fff;
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
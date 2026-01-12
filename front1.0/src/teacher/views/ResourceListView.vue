<template>
  <div class="resource-management">
    <div class="page-header">
      <div class="header-left">
        <h1>教学资源</h1>
        <p>管理教学资源，上传和分享学习资料</p>
      </div>
      <div class="header-right">
        <button class="btn btn-secondary" @click="showFolderModal = true">
          <span>📁</span> 新建文件夹
        </button>
        <button class="btn btn-primary" @click="openUploadModal">
          <span>⬆️</span> 上传资源
        </button>
      </div>
    </div>

    <div class="stats-row">
      <div class="stat-item">
        <div class="stat-icon blue">📚</div>
        <div class="stat-content">
          <span class="stat-value">{{ totalResources }}</span>
          <span class="stat-label">资源总数</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon green">💾</div>
        <div class="stat-content">
          <span class="stat-value">{{ totalSize }}</span>
          <span class="stat-label">存储空间</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon purple">📥</div>
        <div class="stat-content">
          <span class="stat-value">{{ totalDownloads }}</span>
          <span class="stat-label">下载次数</span>
        </div>
      </div>
      <div class="stat-item">
        <div class="stat-icon orange">👁️</div>
        <div class="stat-content">
          <span class="stat-value">{{ totalViews }}</span>
          <span class="stat-label">浏览次数</span>
        </div>
      </div>
    </div>

    <div class="filter-section">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input
          type="text"
          v-model="searchQuery"
          placeholder="搜索资源名称..."
        />
      </div>
      <div class="filter-options">
        <select v-model="typeFilter">
          <option value="all">全部类型</option>
          <option value="document">文档</option>
          <option value="video">视频</option>
          <option value="image">图片</option>
          <option value="audio">音频</option>
          <option value="archive">压缩包</option>
          <option value="other">其他</option>
        </select>
        <select v-model="classFilter">
          <option value="all">全部班级</option>
          <option v-for="cls in classes" :key="cls.id" :value="cls.id">
            {{ cls.name }}
          </option>
        </select>
        <select v-model="sortBy">
          <option value="time">按时间排序</option>
          <option value="name">按名称排序</option>
          <option value="downloads">按下载量排序</option>
          <option value="size">按大小排序</option>
        </select>
        <div class="view-toggle">
          <button
            class="view-btn"
            :class="{ active: viewMode === 'grid' }"
            @click="viewMode = 'grid'"
          >
            ⊞
          </button>
          <button
            class="view-btn"
            :class="{ active: viewMode === 'list' }"
            @click="viewMode = 'list'"
          >
            ☰
          </button>
        </div>
      </div>
    </div>

    <div class="quick-folders">
      <div
        v-for="folder in quickFolders"
        :key="folder.id"
        class="folder-card"
        @click="selectFolder(folder)"
        :class="{ active: selectedFolder?.id === folder.id }"
      >
        <div class="folder-icon" :style="{ background: folder.color }">
          {{ folder.icon }}
        </div>
        <div class="folder-info">
          <h4>{{ folder.name }}</h4>
          <p>{{ folder.count }} 个文件</p>
        </div>
      </div>
      <div class="folder-card add-folder" @click="showFolderModal = true">
        <div class="folder-icon add">
          ➕
        </div>
        <div class="folder-info">
          <h4>新建文件夹</h4>
          <p>整理资源</p>
        </div>
      </div>
    </div>

    <div v-if="viewMode === 'grid'" class="resources-grid">
      <div
        v-for="resource in filteredResources"
        :key="resource.id"
        class="resource-card"
        @click="viewResource(resource)"
      >
        <div class="resource-preview" :class="resource.type">
          <div class="preview-icon">
            {{ getTypeIcon(resource.type) }}
          </div>
          <div class="resource-type-badge">
            {{ getTypeName(resource.type) }}
          </div>
        </div>
        <div class="resource-body">
          <h3>{{ resource.name }}</h3>
          <p class="resource-meta">
            {{ formatSize(resource.size) }} · {{ formatDate(resource.uploadTime) }}
          </p>
          <div class="resource-stats">
            <span class="stat">👁️ {{ resource.views }}</span>
            <span class="stat">📥 {{ resource.downloads }}</span>
          </div>
        </div>
        <div class="resource-actions">
          <button class="action-btn" @click.stop="downloadResource(resource)" title="下载">
            ⬇️
          </button>
          <button class="action-btn" @click.stop="shareResource(resource)" title="分享">
            🔗
          </button>
          <button class="action-btn" @click.stop="moreOptions(resource)" title="更多">
            ⋯
          </button>
        </div>
      </div>
    </div>

    <div v-else class="resources-list">
      <table>
        <thead>
          <tr>
            <th>资源名称</th>
            <th>类型</th>
            <th>大小</th>
            <th>上传时间</th>
            <th>浏览</th>
            <th>下载</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="resource in filteredResources"
            :key="resource.id"
            @click="viewResource(resource)"
          >
            <td>
              <div class="resource-info">
                <div class="resource-icon" :class="resource.type">
                  {{ getTypeIcon(resource.type) }}
                </div>
                <span>{{ resource.name }}</span>
              </div>
            </td>
            <td>
              <span class="type-badge" :class="resource.type">
                {{ getTypeName(resource.type) }}
              </span>
            </td>
            <td>{{ formatSize(resource.size) }}</td>
            <td>{{ formatDate(resource.uploadTime) }}</td>
            <td>{{ resource.views }}</td>
            <td>{{ resource.downloads }}</td>
            <td>
              <div class="table-actions">
                <button class="action-btn small" @click.stop="downloadResource(resource)">
                  ⬇️
                </button>
                <button class="action-btn small" @click.stop="shareResource(resource)">
                  🔗
                </button>
                <button class="action-btn small" @click.stop="moreOptions(resource)">
                  ⋯
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div class="pagination">
      <button
        class="page-btn"
        :disabled="currentPage === 1"
        @click="currentPage--"
      >
        ← 上一页
      </button>
      <span class="page-info">
        第 {{ currentPage }} 页 / 共 {{ totalPages }} 页
      </span>
      <button
        class="page-btn"
        :disabled="currentPage === totalPages"
        @click="currentPage++"
      >
        下一页 →
      </button>
    </div>

    <div v-if="showUploadModal" class="modal-overlay" @click.self="closeUploadModal">
      <div class="modal upload-modal">
        <div class="modal-header">
          <h2>上传资源</h2>
          <button class="close-btn" @click="closeUploadModal">×</button>
        </div>
        <form @submit.prevent="uploadResource" class="modal-body">
          <div class="upload-zone" @drop.prevent="handleDrop" @dragover.prevent>
            <div class="upload-content">
              <div class="upload-icon">📤</div>
              <p>拖拽文件到此处，或 <label for="fileInput" class="upload-link">点击选择文件</label></p>
              <input
                type="file"
                id="fileInput"
                multiple
                @change="handleFileSelect"
                hidden
              />
              <span class="upload-hint">支持 PDF、Word、PPT、视频、图片等格式</span>
            </div>
          </div>

          <div v-if="uploadFiles.length > 0" class="selected-files">
            <div
              v-for="(file, index) in uploadFiles"
              :key="index"
              class="file-item"
            >
              <div class="file-icon">{{ getTypeIcon(getFileType(file)) }}</div>
              <div class="file-info">
                <span class="file-name">{{ file.name }}</span>
                <span class="file-size">{{ formatSize(file.size) }}</span>
              </div>
              <button type="button" class="remove-btn" @click="removeFile(index)">
                ×
              </button>
            </div>
          </div>

          <div class="form-group">
            <label>资源分类</label>
            <select v-model="uploadData.folderId">
              <option value="">根目录</option>
              <option v-for="folder in folders" :key="folder.id" :value="folder.id">
                {{ folder.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>适用班级</label>
            <select v-model="uploadData.classId">
              <option value="">所有班级</option>
              <option v-for="cls in classes" :key="cls.id" :value="cls.id">
                {{ cls.name }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>资源描述</label>
            <textarea
              v-model="uploadData.description"
              rows="3"
              placeholder="请输入资源描述..."
            ></textarea>
          </div>

          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="closeUploadModal">
              取消
            </button>
            <button type="submit" class="btn btn-primary" :disabled="uploadFiles.length === 0">
              ⬆️ 上传资源
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="showFolderModal" class="modal-overlay" @click.self="closeFolderModal">
      <div class="modal">
        <div class="modal-header">
          <h2>新建文件夹</h2>
          <button class="close-btn" @click="closeFolderModal">×</button>
        </div>
        <form @submit.prevent="createFolder" class="modal-body">
          <div class="form-group">
            <label>文件夹名称 *</label>
            <input type="text" v-model="newFolder.name" required />
          </div>
          <div class="form-group">
            <label>选择图标</label>
            <div class="icon-picker">
              <div
                v-for="icon in folderIcons"
                :key="icon"
                class="icon-option"
                :class="{ active: newFolder.icon === icon }"
                @click="newFolder.icon = icon"
              >
                {{ icon }}
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>选择颜色</label>
            <div class="color-picker">
              <div
                v-for="color in folderColors"
                :key="color"
                class="color-option"
                :style="{ background: color }"
                :class="{ active: newFolder.color === color }"
                @click="newFolder.color = color"
              ></div>
            </div>
          </div>
          <div class="form-actions">
            <button type="button" class="btn btn-secondary" @click="closeFolderModal">
              取消
            </button>
            <button type="submit" class="btn btn-primary">
              创建文件夹
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { classApi } from '../api/class'
import { resourceApi } from '../api/resource'

export default {
  name: 'ResourceListView',
  data() {
    return {
      searchQuery: '',
      typeFilter: 'all',
      classFilter: 'all',
      sortBy: 'time',
      viewMode: 'grid',
      currentPage: 1,
      pageSize: 16,
      showUploadModal: false,
      showFolderModal: false,
      selectedFolder: null,
      uploadFiles: [],
      uploadData: {
        folderId: '',
        classId: '',
        description: ''
      },
      newFolder: {
        name: '',
        icon: '📁',
        color: '#3b82f6'
      },
      folderIcons: ['📁', '📚', '📖', '📋', '🎓', '💻', '🖥️', '🔬'],
      folderColors: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16'],
      folders: [
        { id: 1, name: '课程课件', icon: '📚', color: '#3b82f6', count: 12 },
        { id: 2, name: '实验报告', icon: '📋', color: '#10b981', count: 8 },
        { id: 3, name: '参考资料', icon: '📖', color: '#f59e0b', count: 15 },
        { id: 4, name: '视频教程', icon: '🎬', color: '#ef4444', count: 6 }
      ],
      classes: [],
      resources: []
    }
  },
  computed: {
    filteredResources() {
      let result = [...this.resources]

      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        result = result.filter(r => r.name.toLowerCase().includes(query))
      }

      if (this.typeFilter !== 'all') {
        result = result.filter(r => r.type === this.typeFilter)
      }

      if (this.classFilter !== 'all') {
        result = result.filter(r => r.classId === parseInt(this.classFilter))
      }

      if (this.selectedFolder && this.selectedFolder.id !== 'all') {
        if (this.selectedFolder.id === 'recent') {
          const weekAgo = new Date()
          weekAgo.setDate(weekAgo.getDate() - 7)
          result = result.filter(r => new Date(r.uploadTime) >= weekAgo)
        } else if (this.selectedFolder.id !== 'favorite' && this.selectedFolder.id !== 'downloaded') {
          result = result.filter(r => r.folderId === this.selectedFolder.id)
        }
      }

      switch (this.sortBy) {
        case 'name':
          result.sort((a, b) => a.name.localeCompare(b.name))
          break
        case 'downloads':
          result.sort((a, b) => b.downloads - a.downloads)
          break
        case 'size':
          result.sort((a, b) => b.size - a.size)
          break
        case 'time':
        default:
          result.sort((a, b) => new Date(b.uploadTime) - new Date(a.uploadTime))
      }

      return result
    },
    totalPages() {
      return Math.ceil(this.filteredResources.length / this.pageSize)
    },
    totalResources() {
      return this.resources.length
    },
    totalSize() {
      const total = this.resources.reduce((sum, r) => sum + r.size, 0)
      return this.formatSize(total)
    },
    totalDownloads() {
      return this.resources.reduce((sum, r) => sum + r.downloads, 0)
    },
    totalViews() {
      return this.resources.reduce((sum, r) => sum + r.views, 0)
    },
    quickFolders() {
      // 计算最近一周上传的资源数量
      const weekAgo = new Date()
      weekAgo.setDate(weekAgo.getDate() - 7)
      const recentCount = this.resources.filter(r => new Date(r.uploadTime) >= weekAgo).length
      
      // 这里需要根据实际情况计算收藏和下载数量
      // 暂时使用固定值，后续可以根据实际数据调整
      const favoriteCount = 0
      const downloadedCount = 0
      
      return [
        { id: 'all', name: '全部资源', icon: '📂', color: '#64748b', count: this.resources.length },
        { id: 'recent', name: '最近上传', icon: '🕐', color: '#3b82f6', count: recentCount },
        { id: 'favorite', name: '我的收藏', icon: '⭐', color: '#f59e0b', count: favoriteCount },
        { id: 'downloaded', name: '已下载', icon: '⬇️', color: '#10b981', count: downloadedCount }
      ]
    }
  },
  mounted() {
    this.loadClasses()
    this.loadResources()
  },
  methods: {
    getTypeIcon(type) {
      const iconMap = {
        document: '📄',
        video: '🎬',
        image: '🖼️',
        audio: '🎵',
        archive: '📦',
        other: '📎'
      }
      return iconMap[type] || '📎'
    },
    getTypeName(type) {
      const nameMap = {
        document: '文档',
        video: '视频',
        image: '图片',
        audio: '音频',
        archive: '压缩包',
        other: '其他'
      }
      return nameMap[type] || '其他'
    },
    getFileType(file) {
      const ext = file.name.split('.').pop().toLowerCase()
      const typeMap = {
        pdf: 'document',
        doc: 'document',
        docx: 'document',
        ppt: 'document',
        pptx: 'document',
        mp4: 'video',
        avi: 'video',
        mov: 'video',
        jpg: 'image',
        jpeg: 'image',
        png: 'image',
        gif: 'image',
        mp3: 'audio',
        wav: 'audio',
        zip: 'archive',
        rar: 'archive'
      }
      return typeMap[ext] || 'other'
    },
    formatSize(bytes) {
      if (bytes < 1024) return bytes + ' B'
      if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
      if (bytes < 1024 * 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
      return (bytes / (1024 * 1024 * 1024)).toFixed(1) + ' GB'
    },
    formatDate(dateStr) {
      const date = new Date(dateStr)
      return date.toLocaleDateString('zh-CN')
    },
    selectFolder(folder) {
      this.selectedFolder = folder
    },
    viewResource(resource) {
      console.log('Viewing resource:', resource.name)
    },
    downloadResource(resource) {
      console.log('Downloading resource:', resource.name)
    },
    shareResource(resource) {
      console.log('Sharing resource:', resource.name)
    },
    moreOptions(resource) {
      console.log('More options for:', resource.name)
    },
    handleFileSelect(event) {
      const files = Array.from(event.target.files)
      this.uploadFiles.push(...files)
    },
    handleDrop(event) {
      const files = Array.from(event.dataTransfer.files)
      this.uploadFiles.push(...files)
    },
    removeFile(index) {
      this.uploadFiles.splice(index, 1)
    },
    async uploadResource() {
      if (this.uploadFiles.length === 0) {
        alert('请选择要上传的文件')
        return
      }

      try {
        // 为每个文件创建FormData并上传
        for (const file of this.uploadFiles) {
          const formData = new FormData()
          formData.append('file', file)
          formData.append('title', file.name)
          formData.append('description', this.uploadData.description || '')
          formData.append('resource_type', this.getResourceType(file))
          formData.append('is_public', true)
          formData.append('category', this.uploadData.folderId || '')
          
          // 使用正确的API方法上传教学资源
          await resourceApi.uploadTeachingResource(formData)
        }

        alert('文件上传成功！')
        this.closeUploadModal()
        // 刷新资源列表
        this.loadResources()
      } catch (error) {
        console.error('上传失败:', error)
        console.error('错误详情:', error.response?.data)
        let errorMessage = '上传失败，请重试'
        
        if (error.response?.data) {
          const errorData = error.response.data
          
          // 优先使用message字段
          if (errorData.message) {
            errorMessage = errorData.message
          } else if (errorData.error) {
            errorMessage = errorData.error
          }
          
          // 如果有details，添加详细信息
          if (errorData.details) {
            const detailsStr = typeof errorData.details === 'string' 
              ? errorData.details 
              : JSON.stringify(errorData.details, null, 2)
            errorMessage += '\n\n详细信息:\n' + detailsStr
          }
          
          // 如果有resource_data（调试信息），也显示
          if (errorData.resource_data) {
            console.log('资源数据:', errorData.resource_data)
          }
        } else if (error.message) {
          errorMessage = error.message
        }
        
        // 显示更友好的错误提示
        alert(`上传资源失败:\n${errorMessage}`)
      }
    },
    getResourceType(file) {
      const ext = file.name.split('.').pop().toLowerCase()
      if (['pdf', 'doc', 'docx', 'txt'].includes(ext)) return 'document'
      if (['ppt', 'pptx'].includes(ext)) return 'ppt'
      if (['mp4', 'avi', 'mov', 'wmv'].includes(ext)) return 'video'
      if (['jpg', 'jpeg', 'png', 'gif'].includes(ext)) return 'image'
      return 'other'
    },
    async loadClasses() {
      try {
        const response = await classApi.getClasses()
        // 处理不同的响应格式
        let classesData = []
        if (response.data) {
          if (Array.isArray(response.data)) {
            classesData = response.data
          } else if (Array.isArray(response.data.results)) {
            classesData = response.data.results
          }
        }
        
        if (classesData.length > 0) {
          this.classes = classesData.map(cls => ({
            id: cls.id,
            name: cls.name
          }))
        }
      } catch (error) {
        console.error('加载班级列表失败:', error)
      }
    },
    async loadResources() {
      try {
        // 获取教学资源列表
        const response = await resourceApi.getTeachingResources()
        // 处理不同的数据格式
        let resourcesList = []
        if (response.data) {
          if (Array.isArray(response.data)) {
            resourcesList = response.data
          } else if (Array.isArray(response.data.results)) {
            resourcesList = response.data.results
          } else if (Array.isArray(response.data.data)) {
            resourcesList = response.data.data
          }
        }
        
        // 映射资源数据，使用新的字段名称
        this.resources = resourcesList.map(item => ({
          id: item.id,
          name: item.title || '未命名资源',
          type: item.resource_type || 'other',
          size: item.file_size || 0, // 使用file_size字段获取文件大小
          uploadTime: item.created_at || new Date().toISOString(), // 使用created_at字段
          views: 0, // 后端未返回浏览次数
          downloads: 0, // 后端未返回下载次数
          folderId: item.category || '', // 使用category字段作为分类
          classId: '' // 教学资源不属于特定班级
        }))
        
        // 确保分页数据正确
        this.currentPage = 1
        this.totalPages = Math.max(1, Math.ceil(this.resources.length / this.pageSize))
        
        console.log('加载的资源数据:', this.resources)
      } catch (error) {
        console.error('加载资源失败:', error)
        // 出错时显示空数组
        this.resources = []
      }
    },
    openUploadModal() {
      console.log('打开上传模态框')
      this.showUploadModal = true
    },
    closeUploadModal() {
      this.showUploadModal = false
      this.uploadFiles = []
      this.uploadData = { folderId: '', classId: '', description: '' }
    },
    createFolder() {
      console.log('Creating folder:', this.newFolder)
      this.closeFolderModal()
    },
    closeFolderModal() {
      this.showFolderModal = false
      this.newFolder = { name: '', icon: '📁', color: '#3b82f6' }
    }
  }
}
</script>

<style scoped>
.resource-management {
  padding: 24px;
  background: #f8fafc;
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-left h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.header-left p {
  color: #64748b;
  margin: 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: white;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #f1f5f9;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-item {
  background: white;
  border-radius: 16px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.stat-icon.blue { background: #dbeafe; }
.stat-icon.green { background: #dcfce7; }
.stat-icon.purple { background: #f3e8ff; }
.stat-icon.orange { background: #ffedd5; }

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 13px;
  color: #64748b;
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-box .search-icon {
  position: absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
}

.search-box input {
  width: 100%;
  padding: 12px 16px 12px 44px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  background: white;
}

.search-box input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.filter-options {
  display: flex;
  gap: 12px;
  align-items: center;
}

.filter-options select {
  padding: 10px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.view-toggle {
  display: flex;
  background: white;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid #e2e8f0;
}

.view-btn {
  padding: 10px 14px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 16px;
  transition: all 0.2s;
}

.view-btn.active {
  background: #3b82f6;
  color: white;
}

.quick-folders {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  overflow-x: auto;
  padding-bottom: 8px;
}

.folder-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
  flex-shrink: 0;
}

.folder-card:hover {
  border-color: #3b82f6;
}

.folder-card.active {
  border-color: #3b82f6;
  background: #eff6ff;
}

.folder-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.folder-icon.add {
  background: #f1f5f9;
  font-size: 20px;
}

.folder-info h4 {
  margin: 0 0 2px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
}

.folder-info p {
  margin: 0;
  font-size: 12px;
  color: #64748b;
}

.resources-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.resource-card {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.resource-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.resource-preview {
  height: 140px;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.resource-preview.document { background: #fef3c7; }
.resource-preview.video { background: #dbeafe; }
.resource-preview.image { background: #dcfce7; }
.resource-preview.audio { background: #f3e8ff; }
.resource-preview.archive { background: #ffedd5; }
.resource-preview.other { background: #f1f5f9; }

.preview-icon {
  font-size: 48px;
}

.resource-type-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #475569;
}

.resource-body {
  padding: 16px;
}

.resource-body h3 {
  margin: 0 0 8px 0;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.resource-meta {
  font-size: 12px;
  color: #94a3b8;
  margin: 0 0 12px 0;
}

.resource-stats {
  display: flex;
  gap: 16px;
}

.resource-stats .stat {
  font-size: 12px;
  color: #64748b;
}

.resource-actions {
  display: flex;
  gap: 8px;
  padding: 0 16px 16px;
}

.action-btn {
  padding: 8px;
  border: none;
  background: #f1f5f9;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #e2e8f0;
}

.action-btn.small {
  padding: 6px;
  font-size: 14px;
}

.resources-list {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  margin-bottom: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.resources-list table {
  width: 100%;
  border-collapse: collapse;
}

.resources-list th,
.resources-list td {
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
}

.resources-list th {
  background: #f8fafc;
  font-weight: 600;
  color: #475569;
  font-size: 13px;
}

.resources-list td {
  color: #1e293b;
  font-size: 14px;
}

.resources-list tbody tr {
  cursor: pointer;
  transition: background 0.2s;
}

.resources-list tbody tr:hover {
  background: #f8fafc;
}

.resource-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.resource-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.resource-icon.document { background: #fef3c7; }
.resource-icon.video { background: #dbeafe; }
.resource-icon.image { background: #dcfce7; }
.resource-icon.audio { background: #f3e8ff; }
.resource-icon.archive { background: #ffedd5; }
.resource-icon.other { background: #f1f5f9; }

.type-badge {
  padding: 4px 10px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.type-badge.document { background: #fef3c7; color: #d97706; }
.type-badge.video { background: #dbeafe; color: #2563eb; }
.type-badge.image { background: #dcfce7; color: #16a34a; }
.type-badge.audio { background: #f3e8ff; color: #9333ea; }
.type-badge.archive { background: #ffedd5; color: #ea580c; }
.type-badge.other { background: #f1f5f9; color: #64748b; }

.table-actions {
  display: flex;
  gap: 8px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

.page-btn {
  padding: 10px 20px;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: #f1f5f9;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #64748b;
  font-size: 14px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 20px;
  width: 100%;
  max-width: 480px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal.upload-modal {
  max-width: 560px;
}

.modal-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  font-size: 20px;
  color: #1e293b;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f1f5f9;
  border-radius: 8px;
  cursor: pointer;
  font-size: 20px;
  color: #64748b;
}

.modal-body {
  padding: 24px;
}

.upload-zone {
  border: 2px dashed #e2e8f0;
  border-radius: 12px;
  padding: 40px;
  text-align: center;
  margin-bottom: 20px;
  transition: all 0.2s;
  cursor: pointer;
}

.upload-zone:hover {
  border-color: #3b82f6;
  background: #f8fafc;
}

.upload-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.upload-content p {
  margin: 0 0 8px 0;
  color: #475569;
}

.upload-link {
  color: #3b82f6;
  cursor: pointer;
  font-weight: 500;
}

.upload-hint {
  font-size: 12px;
  color: #94a3b8;
}

.selected-files {
  margin-bottom: 20px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 10px;
  margin-bottom: 8px;
}

.file-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.file-info {
  flex: 1;
}

.file-name {
  display: block;
  font-weight: 500;
  color: #1e293b;
}

.file-size {
  font-size: 12px;
  color: #64748b;
}

.remove-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: #fee2e2;
  border-radius: 6px;
  cursor: pointer;
  font-size: 16px;
  color: #dc2626;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group textarea {
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.icon-picker,
.color-picker {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.icon-option {
  width: 40px;
  height: 40px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 20px;
  transition: all 0.2s;
}

.icon-option:hover,
.icon-option.active {
  border-color: #3b82f6;
  background: #eff6ff;
}

.color-option {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.color-option:hover,
.color-option.active {
  transform: scale(1.1);
  border-color: #1e293b;
}
</style>

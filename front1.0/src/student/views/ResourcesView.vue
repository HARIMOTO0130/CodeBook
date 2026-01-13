<template>
  <div class="student-resources-view">
    <h2>学习资源</h2>
    
    <!-- 搜索和筛选区域 -->
    <div class="filters-container">
      <!-- 搜索框 -->
      <div class="search-box">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="搜索资源..." 
          @input="onSearch"
        />
      </div>
      
      <!-- 筛选条件 -->
      <div class="filters-row">
        <div class="filter-group">
          <label>课程</label>
          <select v-model="classFilter" @change="applyFilters" :disabled="classesLoading">
            <option value="">所有课程</option>
            <option v-for="classItem in classes" :key="classItem.id" :value="classItem.id">
              {{ classItem.name }}
            </option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>资源类型</label>
          <select v-model="resourceTypeFilter" @change="applyFilters">
            <option value="">所有类型</option>
            <option value="document">文档</option>
            <option value="ppt">PPT</option>
            <option value="video">视频</option>
            <option value="image">图片</option>
            <option value="other">其他</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>日期</label>
          <select v-model="dateFilter" @change="applyFilters">
            <option value="">所有日期</option>
            <option value="today">今天</option>
            <option value="week">本周</option>
            <option value="month">本月</option>
            <option value="year">本年</option>
          </select>
        </div>
        
        <div class="filter-actions">
          <button class="btn btn-secondary" @click="resetFilters">
            重置筛选
          </button>
        </div>
        
        <!-- 排序选项 -->
        <div class="filter-group">
          <label>排序方式</label>
          <select v-model="sortBy" @change="onSortChange">
            <option value="latest">最新优先</option>
            <option value="downloads">下载最多</option>
            <option value="alphabetical">字母顺序</option>
          </select>
        </div>
      </div>
    </div>
    
    <!-- 资源列表 -->
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="resources.length > 0" class="resources-list">
      <div v-for="resource in resources" :key="resource.id" class="resource-card">
        <div class="resource-header">
          <div class="resource-icon" :class="getResourceIconClass(resource.resource_type)">
            {{ getResourceIcon(resource.resource_type) }}
          </div>
          <div class="resource-info">
            <h3>{{ resource.resource_name }}</h3>
            <div class="resource-type">{{ resource.resource_type }}</div>
          </div>
          <div class="resource-stats">
            <span class="download-count">下载: {{ resource.download_count }}次</span>
            <span class="file-size">{{ formatFileSize(resource.file_size) }}</span>
          </div>
        </div>
        <div class="resource-meta">
          <div class="resource-teacher">
            <span class="meta-label">上传教师:</span>
            <span class="meta-value">{{ resource.teacher?.teacher_name || '未知教师' }}</span>
          </div>
          <div class="resource-date">
            <span class="meta-label">上传时间:</span>
            <span class="meta-value">{{ formatDate(resource.upload_time) }}</span>
          </div>
          <div class="resource-subject" v-if="resource.subject">
            <span class="meta-label">学科:</span>
            <span class="meta-value">{{ resource.subject }}</span>
          </div>
          <div class="resource-grade" v-if="resource.grade">
            <span class="meta-label">年级:</span>
            <span class="meta-value">{{ resource.grade }}</span>
          </div>
        </div>
        <div class="resource-tags" v-if="resource.tags && resource.tags.length">
          <span class="meta-label">标签:</span>
          <div class="tags-list">
            <span v-for="tag in resource.tags" :key="tag" class="tag">
              {{ tag }}
            </span>
          </div>
        </div>
        <div class="resource-description" v-if="resource.resource_desc">
          <p>{{ resource.resource_desc }}</p>
        </div>
        <div class="resource-actions">
          <button 
            class="btn btn-secondary" 
            @click="openPreview(resource)"
            v-if="getPreviewType(resource) !== 'other'"
          >
            预览
          </button>
          <button class="btn btn-primary" @click="downloadResource(resource)">
            下载资源
          </button>
        </div>
      </div>
    </div>
    <div v-else class="no-resources">
      <p>暂无学习资源</p>
    </div>
    
    <!-- 分页控件 -->
    <div v-if="totalPages > 1" class="pagination">
      <button 
        class="page-btn" 
        @click="previousPage"
        :disabled="currentPage === 1"
      >
        上一页
      </button>
      <span class="page-info">
        第 {{ currentPage }} / {{ totalPages }} 页 (共 {{ totalResources }} 个资源)
      </span>
      <button 
        class="page-btn" 
        @click="nextPage"
        :disabled="currentPage === totalPages"
      >
        下一页
      </button>
    </div>
    
    <!-- 预览模态框 -->
    <div v-if="showPreviewModal && previewResource" class="modal-overlay" @click="closePreview">
      <div class="preview-modal" @click.stop>
        <div class="modal-header">
          <h3>{{ previewResource.resource_name }}</h3>
          <button class="close-btn" @click="closePreview">&times;</button>
        </div>
        <div class="modal-body">
          <!-- 图片预览 -->
          <div v-if="previewType === 'image'" class="preview-content image-preview">
            <img :src="previewResource.temp_url" alt="资源预览" />
          </div>
          
          <!-- 视频预览 -->
          <div v-else-if="previewType === 'video'" class="preview-content video-preview">
            <video controls>
              <source :src="previewResource.temp_url" type="video/mp4">
              您的浏览器不支持视频预览。
            </video>
          </div>
          
          <!-- 文档预览（提示下载） -->
          <div v-else-if="previewType === 'document'" class="preview-content document-preview">
            <div class="document-info">
              <div class="document-icon">📄</div>
              <h4>文档预览</h4>
              <p>此资源为文档类型，无法直接在浏览器中预览。</p>
              <button class="btn btn-primary" @click="downloadResource(previewResource)">
                下载文档
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closePreview">关闭</button>
          <button class="btn btn-primary" @click="downloadResource(previewResource)">下载</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '../api/api';

export default {
  name: 'StudentResourcesView',
  data() {
    return {
      resources: [],
      loading: true,
      error: null,
      // 分页相关
      currentPage: 1,
      pageSize: 10,
      totalPages: 1,
      totalResources: 0,
      // 筛选和搜索相关
      searchQuery: '',
      resourceTypeFilter: '',
      dateFilter: '',
      classFilter: '',
      // 班级列表
      classes: [],
      classesLoading: false,
      // 排序相关
      sortBy: 'latest', // 默认按最新优先排序
      // 预览相关
      showPreviewModal: false,
      previewResource: null,
      previewType: ''
    };
  },
  async mounted() {
    // 获取班级列表
    await this.fetchClasses();
    // 获取资源列表
    await this.fetchResources();
  },
  methods: {
    async fetchResources() {
      try {
        this.loading = true;
        
        // 确定排序参数
        let orderBy = '';
        switch (this.sortBy) {
          case 'latest':
            orderBy = '-upload_time'; // 按上传时间降序（最新优先）
            break;
          case 'downloads':
            orderBy = '-download_count'; // 按下载次数降序（下载最多）
            break;
          case 'alphabetical':
            orderBy = 'resource_name'; // 按资源名称升序（字母顺序）
            break;
          default:
            orderBy = '-upload_time';
        }
        
        const params = {
          // 分页参数
          page: this.currentPage,
          page_size: this.pageSize,
          // 搜索和筛选参数
          search: this.searchQuery,
          resource_type: this.resourceTypeFilter,
          date: this.dateFilter,
          class_id: this.classFilter,
          // 排序参数
          order_by: orderBy
        };
        
        const response = await api.getStudentResources(params);
        
        // 处理API响应
        if (Array.isArray(response)) {
          // 直接返回资源数组
          this.resources = response;
          this.totalResources = response.length;
          this.totalPages = Math.ceil(this.totalResources / this.pageSize);
        } else if (response.data) {
          if (Array.isArray(response.data)) {
            // 处理未分页的响应（兼容旧版本）
            this.resources = response.data;
            this.totalResources = response.data.length;
            this.totalPages = Math.ceil(this.totalResources / this.pageSize);
          } else if (response.data.results) {
            // 处理分页响应
            this.resources = response.data.results;
            this.totalResources = response.data.count || 0;
            this.totalPages = Math.ceil(this.totalResources / this.pageSize);
          }
        }
        
        this.error = null;
      } catch (err) {
        this.error = '获取学习资源失败：' + err.message;
        console.error('获取学习资源失败:', err);
      } finally {
        this.loading = false;
      }
    },
    
    // 上一页
    previousPage() {
      if (this.currentPage > 1) {
        this.currentPage--;
        this.fetchResources();
      }
    },
    
    // 下一页
    nextPage() {
      if (this.currentPage < this.totalPages) {
        this.currentPage++;
        this.fetchResources();
      }
    },
    
    // 应用搜索和筛选条件
    applyFilters() {
      // 重置到第一页
      this.currentPage = 1;
      this.fetchResources();
    },
    
    // 重置所有筛选条件
    resetFilters() {
      this.searchQuery = '';
      this.resourceTypeFilter = '';
      this.dateFilter = '';
      this.classFilter = '';
      this.currentPage = 1;
      this.fetchResources();
    },
    
    // 获取班级列表
    async fetchClasses() {
      try {
        this.classesLoading = true;
        const classes = await api.getStudentClasses();
        if (Array.isArray(classes)) {
          this.classes = classes;
        } else if (classes && Array.isArray(classes.results)) {
          this.classes = classes.results;
        } else {
          this.classes = [];
        }
      } catch (err) {
        console.error('获取班级列表失败:', err);
        this.classes = [];
      } finally {
        this.classesLoading = false;
      }
    },
    
    // 搜索输入处理
    onSearch() {
      this.currentPage = 1;
      this.fetchResources();
    },
    
    // 排序处理
    onSortChange() {
      this.currentPage = 1;
      this.fetchResources();
    },
    
    // 确定资源的预览类型
    getPreviewType(resource) {
      const resourceType = resource.resource_type;
      if (resourceType === 'image') {
        return 'image';
      } else if (resourceType === 'video') {
        return 'video';
      } else if (resourceType === 'document' || resourceType === 'ppt') {
        // 对于文档和PPT，我们可以提供下载或提示无法直接预览
        return 'document';
      } else {
        return 'other';
      }
    },
    
    // 打开预览模态框
    async openPreview(resource) {
      this.previewResource = resource;
      this.previewType = this.getPreviewType(resource);
      
      // 如果是图片或视频，通过API获取资源内容
      if (this.previewType === 'image' || this.previewType === 'video') {
        try {
          const response = await api.downloadStudentResource(resource.id);
          // 创建临时URL用于预览
          this.previewResource.temp_url = window.URL.createObjectURL(new Blob([response.data]));
        } catch (error) {
          console.error('预览资源获取失败:', error);
          alert('预览资源获取失败: ' + error.message);
          return;
        }
      }
      
      this.showPreviewModal = true;
    },
    
    // 关闭预览模态框
    closePreview() {
      // 释放临时URL
      if (this.previewResource && this.previewResource.temp_url) {
        window.URL.revokeObjectURL(this.previewResource.temp_url);
      }
      
      this.showPreviewModal = false;
      this.previewResource = null;
      this.previewType = '';
    },
    async downloadResource(resource) {
      try {
        // 调用API获取文件blob
        const response = await api.downloadStudentResource(resource.id);
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', resource.resource_name || '未命名资源');
        document.body.appendChild(link);
        link.click();
        
        // 清理
        window.URL.revokeObjectURL(url);
        document.body.removeChild(link);
        
        // 更新本地UI显示的下载次数
        resource.download_count = (resource.download_count || 0) + 1;
        console.log('下载成功:', resource.resource_name);
      } catch (error) {
        console.error('下载资源失败:', error);
        alert('下载资源失败: ' + (error.response?.data?.error || error.message || '未知错误'));
      }
    },
    getResourceIcon(type) {
      const typeMap = {
        '文档': '📄',
        '视频': '🎬',
        '音频': '🎵',
        '图片': '🖼️',
        '压缩包': '📦',
        '代码': '💻',
        'PDF': '📄',
        'PPT': '📊',
        'Excel': '📈',
        'Word': '📝'
      };
      return typeMap[type] || '📁';
    },
    getResourceIconClass(type) {
      const typeMap = {
        '文档': 'icon-document',
        '视频': 'icon-video',
        '音频': 'icon-audio',
        '图片': 'icon-image',
        '压缩包': 'icon-archive',
        '代码': 'icon-code',
        'PDF': 'icon-pdf',
        'PPT': 'icon-ppt',
        'Excel': 'icon-excel',
        'Word': 'icon-word'
      };
      return typeMap[type] || 'icon-other';
    },
    formatFileSize(size) {
      if (!size) return '0 B';
      const units = ['B', 'KB', 'MB', 'GB'];
      let i = 0;
      while (size >= 1024 && i < units.length - 1) {
        size /= 1024;
        i++;
      }
      return `${size.toFixed(1)} ${units[i]}`;
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    }
  }
};
</script>

<style scoped>
.student-resources-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  color: #333;
  margin-bottom: 20px;
}

.loading, .error, .no-resources {
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 20px;
}

.loading {
  background-color: #e3f2fd;
  color: #1976d2;
}

.error {
  background-color: #ffebee;
  color: #d32f2f;
}

.no-resources {
  background-color: #fff3e0;
  color: #f57c00;
}

.resources-list {
  display: grid;
  gap: 20px;
}

.resource-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.resource-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.resource-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.resource-icon {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: white;
}

.icon-document { background-color: #2196F3; }
.icon-video { background-color: #FF5722; }
.icon-audio { background-color: #9C27B0; }
.icon-image { background-color: #4CAF50; }
.icon-archive { background-color: #607D8B; }
.icon-code { background-color: #795548; }
.icon-pdf { background-color: #F44336; }
.icon-ppt { background-color: #FFC107; }
.icon-excel { background-color: #8BC34A; }
.icon-word { background-color: #2196F3; }
.icon-other { background-color: #9E9E9E; }

.resource-info {
  flex: 1;
}

.resource-info h3 {
  margin: 0 0 5px 0;
  color: #333;
  font-size: 18px;
}

.resource-type {
  color: #888;
  font-size: 14px;
}

.resource-stats {
  display: flex;
  flex-direction: column;
  gap: 5px;
  align-items: flex-end;
}

.download-count, .file-size {
  font-size: 14px;
  color: #666;
}

.resource-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 15px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.resource-tags {
  margin-bottom: 15px;
  color: #666;
  font-size: 14px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 5px;
}

.tag {
  display: inline-block;
  padding: 4px 8px;
  background-color: #e3f2fd;
  color: #1976d2;
  border-radius: 12px;
  font-size: 12px;
  white-space: nowrap;
}

.resource-teacher, .resource-date, .resource-subject, .resource-grade {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  flex-wrap: wrap;
}

.meta-label {
  color: #888;
}

.meta-value {
  color: #666;
  font-weight: 500;
}

.resource-description {
  margin-bottom: 20px;
  color: #666;
  line-height: 1.5;
}

.resource-actions {
  display: flex;
  justify-content: flex-end;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #1976d2;
  color: white;
}

.btn-primary:hover {
  background-color: #1565c0;
}

/* 筛选和搜索样式 */
.filters-container {
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f5f5f5;
  border-radius: 8px;
}

.search-box {
  margin-bottom: 15px;
}

.search-box input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.filters-row {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: flex-end;
}

.filter-group {
  flex: 1;
  min-width: 150px;
}

.filter-group label {
  display: block;
  margin-bottom: 5px;
  font-size: 14px;
  color: #666;
}

.filter-group select {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.filter-actions {
  margin-left: auto;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #545b62;
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
  padding: 10px 0;
}

.page-btn {
  padding: 8px 16px;
  margin: 0 10px;
  border: 1px solid #1976d2;
  border-radius: 4px;
  background-color: white;
  color: #1976d2;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background-color: #1976d2;
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
}

/* 预览模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 20px;
}

.preview-modal {
  background-color: white;
  border-radius: 8px;
  max-width: 95%;
  max-height: 95%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: #f5f5f5;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
  flex: 1;
}

.preview-content {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.image-preview img {
  max-width: 100%;
  max-height: 85vh;
  object-fit: contain;
}

.video-preview video {
  max-width: 100%;
  max-height: 85vh;
  object-fit: contain;
}

.document-preview {
  text-align: center;
  padding: 40px 20px;
}

.document-info {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.document-icon {
  font-size: 60px;
  margin-bottom: 20px;
}

.document-info h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.document-info p {
  margin: 0 0 20px 0;
  color: #666;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.modal-footer .btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background-color 0.2s;
}
</style>
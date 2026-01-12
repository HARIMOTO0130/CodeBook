<template>
  <div class="student-resources-view">
    <h2>学习资源</h2>
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
        </div>
        <div class="resource-description" v-if="resource.resource_desc">
          <p>{{ resource.resource_desc }}</p>
        </div>
        <div class="resource-actions">
          <button class="btn btn-primary" @click="downloadResource(resource)">
            下载资源
          </button>
        </div>
      </div>
    </div>
    <div v-else class="no-resources">
      <p>暂无学习资源</p>
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
      error: null
    };
  },
  async mounted() {
    await this.fetchResources();
  },
  methods: {
    async fetchResources() {
      try {
        this.loading = true;
        this.resources = await api.getStudentResources();
        this.error = null;
      } catch (err) {
        this.error = '获取学习资源失败：' + err.message;
        console.error('获取学习资源失败:', err);
      } finally {
        this.loading = false;
      }
    },
    downloadResource(resource) {
      // 这里需要实现资源下载功能，暂时使用简单的方式
      if (resource.resource_url) {
        window.open(resource.resource_url, '_blank');
      } else {
        alert('资源地址无效，无法下载');
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
  gap: 20px;
  margin-bottom: 15px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.resource-teacher, .resource-date {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
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
</style>
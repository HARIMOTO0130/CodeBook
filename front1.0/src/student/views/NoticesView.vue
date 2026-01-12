<template>
  <div class="student-notices-view">
    <h2>通知消息</h2>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="notices.length > 0" class="notices-list">
      <div v-for="notice in notices" :key="notice.id" class="notice-card" :class="{ 'read': notice.is_read }">
        <div class="notice-header">
          <div class="notice-type" :class="getNoticeTypeClass(notice.type)">
            {{ notice.type }}
          </div>
          <h3>{{ notice.notice_title }}</h3>
          <div class="notice-actions">
            <button v-if="!notice.is_read" class="btn btn-sm btn-primary" @click="markAsRead(notice.id)">
              标记已读
            </button>
          </div>
        </div>
        <div class="notice-meta">
          <div class="meta-item">
            <span class="meta-label">发布教师:</span>
            <span class="meta-value">{{ notice.teacher?.teacher_name || '未知教师' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">发布时间:</span>
            <span class="meta-value">{{ formatDate(notice.publish_time) }}</span>
          </div>
          <div v-if="notice.class_obj" class="meta-item">
            <span class="meta-label">所属班级:</span>
            <span class="meta-value">{{ notice.class_obj.name }}</span>
          </div>
          <div v-else class="meta-item">
            <span class="meta-label">范围:</span>
            <span class="meta-value">全体学生</span>
          </div>
        </div>
        <div class="notice-content">
          <p>{{ truncateText(notice.notice_content, 200) }}</p>
        </div>
        <div class="notice-footer">
          <button class="btn btn-link" @click="viewNoticeDetail(notice)">
            查看详情
          </button>
          <div class="notice-stats">
            <span class="read-count">已读: {{ notice.read_count }}人</span>
            <span v-if="notice.is_important" class="important">重要</span>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="no-notices">
      <p>暂无通知消息</p>
    </div>
  </div>
</template>

<script>
import { api } from '../api/api';

export default {
  name: 'StudentNoticesView',
  data() {
    return {
      notices: [],
      loading: true,
      error: null
    };
  },
  async mounted() {
    await this.fetchNotices();
  },
  methods: {
    async fetchNotices() {
      try {
        this.loading = true;
        const noticesData = await api.getStudentNotices();
        // 添加is_read字段，暂时假设所有通知都未读
        this.notices = noticesData.map(notice => ({
          ...notice,
          is_read: false
        }));
        this.error = null;
      } catch (err) {
        this.error = '获取通知消息失败：' + err.message;
        console.error('获取通知消息失败:', err);
      } finally {
        this.loading = false;
      }
    },
    async markAsRead(noticeId) {
      try {
        await api.markNoticeAsRead(noticeId);
        // 更新本地状态
        const notice = this.notices.find(n => n.id === noticeId);
        if (notice) {
          notice.is_read = true;
        }
      } catch (err) {
        alert('标记已读失败：' + err.message);
        console.error('标记已读失败:', err);
      }
    },
    viewNoticeDetail(notice) {
      // 这里可以实现查看详情的功能，暂时用alert代替
      alert(`通知详情：\n标题：${notice.notice_title}\n内容：${notice.notice_content}`);
      // 如果未读，自动标记为已读
      if (!notice.is_read) {
        this.markAsRead(notice.id);
      }
    },
    getNoticeTypeClass(type) {
      const typeMap = {
        'system': 'type-system',
        'assignment': 'type-assignment',
        'student': 'type-student',
        'announcement': 'type-announcement'
      };
      return typeMap[type] || 'type-other';
    },
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    },
    truncateText(text, maxLength) {
      if (!text) return '';
      if (text.length <= maxLength) return text;
      return text.substring(0, maxLength) + '...';
    }
  }
};
</script>

<style scoped>
.student-notices-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  color: #333;
  margin-bottom: 20px;
}

.loading, .error, .no-notices {
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

.no-notices {
  background-color: #fff3e0;
  color: #f57c00;
}

.notices-list {
  display: grid;
  gap: 20px;
}

.notice-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  transition: transform 0.2s, box-shadow 0.2s;
  border-left: 4px solid #2196F3;
}

.notice-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.notice-card.read {
  opacity: 0.7;
  background-color: #f9f9f9;
}

.notice-header {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
  flex-wrap: wrap;
}

.notice-type {
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.type-system { background-color: #2196F3; }
.type-assignment { background-color: #FF5722; }
.type-student { background-color: #4CAF50; }
.type-announcement { background-color: #FFC107; }
.type-other { background-color: #9E9E9E; }

.notice-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
  flex: 1;
}

.notice-actions {
  display: flex;
  gap: 10px;
}

.btn-sm {
  padding: 4px 12px;
  font-size: 12px;
}

.notice-meta {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
  margin-bottom: 15px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.meta-item {
  display: flex;
  gap: 5px;
  align-items: center;
  font-size: 14px;
}

.meta-label {
  color: #888;
}

.meta-value {
  color: #666;
  font-weight: 500;
}

.notice-content {
  margin-bottom: 15px;
}

.notice-content p {
  margin: 0;
  color: #666;
  line-height: 1.6;
}

.notice-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.btn-link {
  background: none;
  border: none;
  color: #2196F3;
  cursor: pointer;
  font-size: 14px;
  padding: 0;
  text-decoration: underline;
}

.btn-link:hover {
  color: #1976D2;
}

.notice-stats {
  display: flex;
  gap: 15px;
  align-items: center;
}

.read-count {
  font-size: 14px;
  color: #666;
}

.important {
  padding: 4px 10px;
  border-radius: 15px;
  font-size: 12px;
  font-weight: bold;
  color: white;
  background-color: #F44336;
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
<template>
  <div class="notification-page">
    <div class="page-header">
      <div class="header-left">
        <h1>消息通知</h1>
        <p>查看和管理您的教学通知、作业提醒和系统消息</p>
      </div>
      <div class="header-right">
        <button class="btn btn-secondary" @click="markAllRead" :disabled="unreadCount === 0">
          <span>✓</span> 全部已读
        </button>
        <button class="btn btn-primary" @click="showCreateModal = true">
          <span>➕</span> 发送通知
        </button>
      </div>
    </div>

    <div class="stats-row">
      <div class="stat-item" @click="filterType = 'all'" :class="{ active: filterType === 'all' }">
        <div class="stat-icon blue">📬</div>
        <div class="stat-content">
          <span class="stat-value">{{ notifications.length }}</span>
          <span class="stat-label">全部消息</span>
        </div>
      </div>
      <div class="stat-item" @click="filterType = 'unread'" :class="{ active: filterType === 'unread' }">
        <div class="stat-icon red">🔴</div>
        <div class="stat-content">
          <span class="stat-value">{{ unreadCount }}</span>
          <span class="stat-label">未读消息</span>
        </div>
      </div>
      <div class="stat-item" @click="filterType = 'system'" :class="{ active: filterType === 'system' }">
        <div class="stat-icon purple">⚙️</div>
        <div class="stat-content">
          <span class="stat-value">{{ systemCount }}</span>
          <span class="stat-label">系统通知</span>
        </div>
      </div>
      <div class="stat-item" @click="filterType = 'assignment'" :class="{ active: filterType === 'assignment' }">
        <div class="stat-icon green">📝</div>
        <div class="stat-content">
          <span class="stat-value">{{ assignmentCount }}</span>
          <span class="stat-label">作业提醒</span>
        </div>
      </div>
    </div>

    <div class="filter-section">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input
          type="text"
          v-model="searchQuery"
          placeholder="搜索通知内容..."
        />
      </div>
      <div class="filter-options">
        <select v-model="filterType">
          <option value="all">全部类型</option>
          <option value="unread">未读消息</option>
          <option value="system">系统通知</option>
          <option value="assignment">作业提醒</option>
          <option value="student">学生消息</option>
        </select>
        <select v-model="sortBy">
          <option value="newest">最新优先</option>
          <option value="oldest">最早优先</option>
          <option value="unread-first">未读优先</option>
        </select>
      </div>
    </div>

    <div class="notification-list">
      <div
        v-for="notification in filteredNotifications"
        :key="notification.id"
        class="notification-item"
        :class="{ unread: !notification.isRead, expanding: expandedId === notification.id }"
        @click="toggleNotification(notification)"
      >
        <div class="notification-icon" :class="notification.type">
          <span v-if="notification.type === 'system'">⚙️</span>
          <span v-else-if="notification.type === 'assignment'">📝</span>
          <span v-else-if="notification.type === 'student'">👨‍🎓</span>
          <span v-else>📢</span>
        </div>
        <div class="notification-content">
          <div class="notification-header">
            <h3>{{ notification.title }}</h3>
            <span class="notification-badge" v-if="!notification.isRead">未读</span>
            <span class="notification-time">{{ formatTime(notification.createdAt) }}</span>
          </div>
          <p class="notification-preview">{{ notification.preview }}</p>
          <div class="notification-meta">
            <span class="meta-item">
              <span>📅</span> {{ formatDate(notification.createdAt) }}
            </span>
            <span class="meta-item" v-if="notification.targetClass">
              <span>📚</span> {{ notification.targetClass }}
            </span>
          </div>
          <div class="notification-expanded" v-if="expandedId === notification.id">
            <div class="expanded-content">
              <p>{{ notification.content }}</p>
              <div class="expanded-actions" v-if="notification.actionUrl">
                <button class="btn btn-primary btn-sm" @click.stop="handleAction(notification)">
                  查看详情
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="notification-actions">
          <button
            class="action-btn"
            :class="{ read: notification.isRead }"
            @click.stop="toggleRead(notification)"
            :title="notification.isRead ? '标记为未读' : '标记为已读'"
          >
            {{ notification.isRead ? '📧' : '✓' }}
          </button>
          <button class="action-btn delete" @click.stop="deleteNotification(notification)" title="删除">
            🗑️
          </button>
        </div>
      </div>

      <div v-if="filteredNotifications.length === 0" class="empty-state">
        <div class="empty-icon">📭</div>
        <h3>暂无通知</h3>
        <p>您当前没有符合筛选条件的通知</p>
      </div>
    </div>

    <div class="pagination" v-if="totalPages > 1">
      <button
        class="page-btn"
        :disabled="currentPage === 1"
        @click="currentPage--"
      >
        ← 上一页
      </button>
      <span class="page-info">第 {{ currentPage }} 页 / 共 {{ totalPages }} 页</span>
      <button
        class="page-btn"
        :disabled="currentPage === totalPages"
        @click="currentPage++"
      >
        下一页 →
      </button>
    </div>

    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal create-notification-modal">
        <div class="modal-header">
          <h2>发送通知</h2>
          <button class="close-btn" @click="showCreateModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>通知标题</label>
            <input type="text" v-model="newNotification.title" placeholder="输入通知标题" />
          </div>
          <div class="form-group">
            <label>通知类型</label>
            <select v-model="newNotification.type">
              <option value="system">系统通知</option>
              <option value="assignment">作业提醒</option>
              <option value="student">学生消息</option>
              <option value="announcement">公告</option>
            </select>
          </div>
          <div class="form-group">
            <label>目标班级</label>
            <select v-model="newNotification.targetClass">
              <option value="">全部班级</option>
              <option v-for="cls in classes" :key="cls.id" :value="cls.id">
                {{ cls.name }}
              </option>
            </select>
          </div>
          <div class="form-group">
            <label>通知内容</label>
            <textarea v-model="newNotification.content" rows="5" placeholder="输入通知详细内容"></textarea>
          </div>
          <div class="form-group">
            <label>
              <input type="checkbox" v-model="newNotification.isImportant" />
              标记为重要通知
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="showCreateModal = false">取消</button>
          <button class="btn btn-primary" @click="sendNotification">发送通知</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { notificationApi } from '../api/notification'
import { classApi } from '../api/class'

export default {
  name: 'NotificationListView',
  data() {
    return {
      searchQuery: '',
      filterType: 'all',
      sortBy: 'newest',
      expandedId: null,
      currentPage: 1,
      pageSize: 10,
      showCreateModal: false,
      loading: false,
      classes: [],
      newNotification: {
        title: '',
        type: 'announcement',
        targetClass: '',
        content: '',
        isImportant: false
      },
      notifications: []
    }
  },
  mounted() {
    this.loadClasses()
    this.loadNotifications()
  },
  computed: {
    filteredNotifications() {
      let result = [...this.notifications]

      if (this.searchQuery) {
        const query = this.searchQuery.toLowerCase()
        result = result.filter(n =>
          n.title.toLowerCase().includes(query) ||
          n.content.toLowerCase().includes(query)
        )
      }

      if (this.filterType === 'unread') {
        result = result.filter(n => !n.isRead)
      } else if (this.filterType !== 'all') {
        result = result.filter(n => n.type === this.filterType)
      }

      if (this.sortBy === 'newest') {
        result.sort((a, b) => b.createdAt - a.createdAt)
      } else if (this.sortBy === 'oldest') {
        result.sort((a, b) => a.createdAt - b.createdAt)
      } else if (this.sortBy === 'unread-first') {
        result.sort((a, b) => (a.isRead === b.isRead ? b.createdAt - a.createdAt : a.isRead ? 1 : -1))
      }

      const start = (this.currentPage - 1) * this.pageSize
      return result.slice(start, start + this.pageSize)
    },
    totalPages() {
      let filtered = [...this.notifications]
      if (this.filterType === 'unread') {
        filtered = filtered.filter(n => !n.isRead)
      } else if (this.filterType !== 'all') {
        filtered = filtered.filter(n => n.type === this.filterType)
      }
      return Math.ceil(filtered.length / this.pageSize)
    },
    unreadCount() {
      return this.notifications.filter(n => !n.isRead).length
    },
    systemCount() {
      return this.notifications.filter(n => n.type === 'system').length
    },
    assignmentCount() {
      return this.notifications.filter(n => n.type === 'assignment').length
    }
  },
  methods: {
    async loadClasses() {
      try {
        const response = await classApi.getClasses()
        // 处理不同的数据格式
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
        console.error('加载班级失败:', error)
      }
    },
    async loadNotifications() {
      this.loading = true
      try {
        const response = await notificationApi.getNotifications()
        if (response.data && Array.isArray(response.data)) {
          this.notifications = response.data.map(notif => ({
            id: notif.id,
            title: notif.notice_title,
            preview: notif.notice_content ? (notif.notice_content.substring(0, 50) + '...') : '',
            content: notif.notice_content || '',
            type: notif.type,
            isRead: notif.status === 1 ? false : true, // 假设status=1表示未读
            isImportant: notif.is_important,
            createdAt: new Date(notif.publish_time),
            targetClass: notif.class_obj || '',
            class_name: notif.class_name || '',
            actionUrl: null
          }))
        }
      } catch (error) {
        console.error('加载通知失败:', error)
        alert('加载通知失败: ' + (error.response?.data?.error || error.message))
      } finally {
        this.loading = false
      }
    },
    markAllRead() {
      // 前端临时标记为已读，实际标记已读功能需要后端支持
      this.notifications.forEach(n => n.isRead = true)
      alert('全部标记为已读（仅前端显示）')
    },
    toggleNotification(notification) {
      if (this.expandedId === notification.id) {
        this.expandedId = null
      } else {
        this.expandedId = notification.id
        if (!notification.isRead) {
          this.toggleRead(notification)
        }
      }
    },
    toggleRead(notification) {
      // 前端临时标记为已读，实际标记已读功能需要后端支持
      notification.isRead = !notification.isRead
    },
    async deleteNotification(notification) {
      if (confirm('确定要删除这条通知吗？')) {
        try {
          // 注意：后端可能没有delete接口，这里先只从前端移除
        const index = this.notifications.findIndex(n => n.id === notification.id)
        if (index !== -1) {
          this.notifications.splice(index, 1)
          }
        } catch (error) {
          console.error('删除失败:', error)
          alert('删除失败: ' + (error.response?.data?.error || error.message))
        }
      }
    },
    handleAction(notification) {
      if (notification.actionUrl) {
        this.$router.push(notification.actionUrl)
      }
    },
    async sendNotification() {
      if (!this.newNotification.title || !this.newNotification.content) {
        alert('请填写通知标题和内容')
        return
      }

      try {
        // 准备符合后端API期望格式的通知数据
        const notificationData = {
          notice_title: this.newNotification.title,
          notice_content: this.newNotification.content,
          class_obj: this.newNotification.targetClass || null, // 后端期望的是class_obj，不是class_id
          type: this.newNotification.type,
          is_important: this.newNotification.isImportant,
          expire_time: null // 可以设置默认过期时间，如7天后
        }
        
        await notificationApi.createNotification(notificationData)
        alert('通知发送成功！')
        this.showCreateModal = false
        this.newNotification = {
          title: '',
          type: 'announcement',
          targetClass: '',
          content: '',
          isImportant: false
        }
        await this.loadNotifications()
      } catch (error) {
        console.error('发送失败:', error)
        alert('发送失败: ' + (error.response?.data?.error || error.message || error))
      }
    },
    formatTime(date) {
      if (!date) return ''
      const now = new Date()
      const dateObj = date instanceof Date ? date : new Date(date)
      const diff = now - dateObj
      const minutes = Math.floor(diff / 60000)
      const hours = Math.floor(diff / 3600000)
      const days = Math.floor(diff / 86400000)

      if (minutes < 1) return '刚刚'
      if (minutes < 60) return `${minutes}分钟前`
      if (hours < 24) return `${hours}小时前`
      if (days < 7) return `${days}天前`
      return dateObj.toLocaleDateString()
    },
    formatDate(date) {
      if (!date) return ''
      const dateObj = date instanceof Date ? date : new Date(date)
      return dateObj.toLocaleDateString('zh-CN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }
  }
}
</script>

<style scoped>
.notification-page {
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
  font-size: 24px;
  font-weight: 600;
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
  padding: 10px 16px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #e2e8f0;
  color: #475569;
}

.btn-secondary:hover {
  background: #cbd5e1;
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 13px;
}

.stats-row {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.stat-item {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  padding: 16px 20px;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
  border: 2px solid transparent;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.stat-item.active {
  border-color: #3b82f6;
  background: #eff6ff;
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
.stat-icon.red { background: #fee2e2; }
.stat-icon.purple { background: #ede9fe; }
.stat-icon.green { background: #dcfce7; }

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
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
  margin-bottom: 20px;
  gap: 16px;
}

.search-box {
  flex: 1;
  max-width: 400px;
  position: relative;
}

.search-box input {
  width: 100%;
  padding: 10px 16px 10px 42px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
}

.search-box input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}

.filter-options {
  display: flex;
  gap: 12px;
}

.filter-options select {
  padding: 10px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.notification-list {
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 20px;
  border-bottom: 1px solid #f1f5f9;
  cursor: pointer;
  transition: all 0.2s;
}

.notification-item:hover {
  background: #f8fafc;
}

.notification-item.unread {
  background: #fefce8;
}

.notification-item.unread:hover {
  background: #fef9c3;
}

.notification-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
}

.notification-icon.system { background: #ede9fe; }
.notification-icon.assignment { background: #dcfce7; }
.notification-icon.student { background: #dbeafe; }
.notification-icon.announcement { background: #fef3c7; }

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.notification-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.notification-badge {
  background: #ef4444;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.notification-time {
  font-size: 12px;
  color: #94a3b8;
  margin-left: auto;
}

.notification-preview {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 8px 0;
  line-height: 1.5;
}

.notification-meta {
  display: flex;
  gap: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #94a3b8;
}

.notification-expanded {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed #e2e8f0;
}

.expanded-content p {
  font-size: 14px;
  color: #475569;
  line-height: 1.6;
  white-space: pre-wrap;
  margin: 0 0 12px 0;
}

.expanded-actions {
  display: flex;
  gap: 8px;
}

.notification-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.action-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: #f1f5f9;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #e2e8f0;
}

.action-btn.read {
  background: #dcfce7;
}

.action-btn.delete:hover {
  background: #fee2e2;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 18px;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.empty-state p {
  color: #64748b;
  margin: 0;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
}

.page-btn {
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
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
  font-size: 14px;
  color: #64748b;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f1f5f9;
}

.modal-header h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 6px;
  background: #f1f5f9;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #e2e8f0;
}

.modal-body {
  padding: 24px;
  max-height: 60vh;
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.form-group input[type="text"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-group input[type="text"]:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.form-group input[type="checkbox"] {
  margin-right: 8px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #f1f5f9;
  background: #f8fafc;
}
</style>
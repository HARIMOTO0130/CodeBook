import api from './index'

// 通知管理API - 基于notice和student_notice_read表结构
export const notificationApi = {
  // 获取通知列表
  getNotifications(params) {
    // params: { class_id, status }
    return api.get('/notices/', { params })
  },
  
  // 获取通知详情
  getNotificationDetail(noticeId) {
    return api.get(`/notices/${noticeId}/`)
  },
  
  // 创建通知
  createNotification(data) {
    // data: { class_id, notice_title, notice_content, expire_time }
    return api.post('/notices/', data)
  },
  
  // 更新通知
  updateNotification(noticeId, data) {
    return api.put(`/notices/${noticeId}/`, data)
  },
  
  // 删除通知
  deleteNotification(noticeId) {
    return api.delete(`/notices/${noticeId}/`)
  },
  
  // 获取通知阅读状态
  getReadStatus(noticeId) {
    return api.get(`/notices/${noticeId}/read_status/`)
  },
  
  // 获取未读通知数量
  getUnreadCount() {
    return api.get('/notices/unread_count/')
  }
}

export default notificationApi

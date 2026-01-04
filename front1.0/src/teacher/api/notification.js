import api from './index'

export const notificationApi = {
  getNotifications(params) {
    return api.get('/notifications/', { params })
  },
  getNotificationDetail(id) {
    return api.get(`/notifications/${id}/`)
  },
  createNotification(data) {
    return api.post('/notifications/', data)
  },
  markAsRead(id) {
    return api.put(`/notifications/${id}/`, { is_read: true })
  },
  markAllAsRead() {
    return api.post('/notifications/mark_all_read/')
  }
}

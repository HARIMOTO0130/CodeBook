import api from './index'

export const analyticsApi = {
  getOverview() {
    return api.get('/analytics/')
  }
}

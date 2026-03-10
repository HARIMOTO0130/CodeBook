<template>
  <div class="dashboard">
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon pending">📋</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待审核</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon in-review">🔍</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.in_review }}</div>
          <div class="stat-label">审核中</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon approved">✅</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.approved }}</div>
          <div class="stat-label">已通过</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon rejected">❌</div>
        <div class="stat-info">
          <div class="stat-value">{{ stats.rejected }}</div>
          <div class="stat-label">已驳回</div>
        </div>
      </div>
    </div>

    <div class="dashboard-row">
      <div class="card my-tasks">
        <h3 class="card-title">我的任务</h3>
        <div class="my-stats">
          <div class="my-stat">
            <span class="my-stat-value">{{ stats.my_pending }}</span>
            <span class="my-stat-label">待处理</span>
          </div>
          <div class="my-stat">
            <span class="my-stat-value">{{ stats.today_reviewed }}</span>
            <span class="my-stat-label">今日已审核</span>
          </div>
          <div class="my-stat">
            <span class="my-stat-value">{{ stats.my_completed }}</span>
            <span class="my-stat-label">累计审核</span>
          </div>
        </div>
        <router-link to="/review/pending" class="btn-primary" style="display: inline-block; margin-top: 16px;">
          查看待审核任务
        </router-link>
      </div>

      <div class="card recent-tasks">
        <h3 class="card-title">最近任务</h3>
        <div v-if="recentTasks.length === 0" class="empty">暂无任务</div>
        <table v-else>
          <thead>
            <tr>
              <th>教材名称</th>
              <th>状态</th>
              <th>提交时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="task in recentTasks" :key="task.id">
              <td>{{ task.book_title }}</td>
              <td>
                <span :class="['status-badge', `status-${task.status}`]">
                  {{ task.status_display }}
                </span>
              </td>
              <td>{{ formatDate(task.created_at) }}</td>
              <td>
                <router-link :to="`/review/review/${task.id}`" class="btn-default" style="padding: 4px 12px;">
                  查看
                </router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { taskApi } from '../api/review'

const stats = ref({
  total: 0,
  pending: 0,
  in_review: 0,
  approved: 0,
  rejected: 0,
  today_reviewed: 0,
  my_pending: 0,
  my_completed: 0
})

const recentTasks = ref([])

const loadStats = async () => {
  try {
    const data = await taskApi.getStats()
    stats.value = data
  } catch (err) {
    console.error('加载统计失败', err)
  }
}

const loadRecentTasks = async () => {
  try {
    const data = await taskApi.getList({ page_size: 5 })
    recentTasks.value = data.results || data
  } catch (err) {
    console.error('加载最近任务失败', err)
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

onMounted(() => {
  loadStats()
  loadRecentTasks()
})
</script>

<style scoped>
.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  background: var(--white);
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  box-shadow: var(--shadow);
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin-right: 16px;
}

.stat-icon.pending { background: #fff7e6; }
.stat-icon.in-review { background: #e6f7ff; }
.stat-icon.approved { background: #f6ffed; }
.stat-icon.rejected { background: #fff2f0; }

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: var(--text-color);
}

.stat-label {
  color: var(--text-secondary);
  margin-top: 4px;
}

.dashboard-row {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 24px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.my-stats {
  display: flex;
  justify-content: space-around;
  padding: 16px 0;
}

.my-stat {
  text-align: center;
}

.my-stat-value {
  display: block;
  font-size: 24px;
  font-weight: bold;
  color: var(--primary-color);
}

.my-stat-label {
  color: var(--text-secondary);
  font-size: 12px;
  margin-top: 4px;
}
</style>

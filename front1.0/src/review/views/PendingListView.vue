<template>
  <div class="pending-list">
    <div class="filter-bar card">
      <div class="filter-item">
        <label>状态：</label>
        <select v-model="filters.status" @change="loadTasks">
          <option value="">全部</option>
          <option value="pending">待审核</option>
          <option value="in_review">审核中</option>
        </select>
      </div>
      <div class="filter-item">
        <label>类型：</label>
        <select v-model="filters.task_type" @change="loadTasks">
          <option value="">全部</option>
          <option value="new_submission">新提交</option>
          <option value="edit_review">修改审核</option>
        </select>
      </div>
      <div class="filter-item">
        <label>搜索：</label>
        <input 
          v-model="filters.search" 
          placeholder="教材名称/作者"
          @keyup.enter="loadTasks"
        />
      </div>
      <button class="btn-primary" @click="loadTasks">搜索</button>
    </div>

    <div class="card">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="tasks.length === 0" class="empty">暂无待审核任务</div>
      <table v-else>
        <thead>
          <tr>
            <th>教材名称</th>
            <th>作者</th>
            <th>类型</th>
            <th>优先级</th>
            <th>状态</th>
            <th>提交时间</th>
            <th>审核人</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in tasks" :key="task.id">
            <td>
              <router-link :to="`/review/review/${task.id}`">{{ task.book_title }}</router-link>
            </td>
            <td>{{ task.book_author }}</td>
            <td>{{ task.task_type_display }}</td>
            <td>
              <span :class="['priority-badge', `priority-${task.priority}`]">
                {{ task.priority_display }}
              </span>
            </td>
            <td>
              <span :class="['status-badge', `status-${task.status}`]">
                {{ task.status_display }}
              </span>
            </td>
            <td>{{ formatDate(task.created_at) }}</td>
            <td>{{ task.assigned_reviewer_name || '-' }}</td>
            <td>
              <router-link :to="`/review/review/${task.id}`" class="btn-primary" style="padding: 4px 12px;">
                审核
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="totalPages > 1" class="pagination">
        <button 
          class="btn-default" 
          :disabled="currentPage === 1"
          @click="changePage(currentPage - 1)"
        >
          上一页
        </button>
        <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
        <button 
          class="btn-default" 
          :disabled="currentPage === totalPages"
          @click="changePage(currentPage + 1)"
        >
          下一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { taskApi } from '../api/review'

const tasks = ref([])
const loading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)

const filters = ref({
  status: 'pending',
  task_type: '',
  search: ''
})

const loadTasks = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      ...filters.value
    }
    const data = await taskApi.getList(params)
    tasks.value = data.results || data
    totalCount.value = data.count || tasks.value.length
    totalPages.value = Math.ceil(totalCount.value / 20)
  } catch (err) {
    console.error('加载任务失败', err)
  } finally {
    loading.value = false
  }
}

const changePage = (page) => {
  currentPage.value = page
  loadTasks()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

onMounted(() => {
  loadTasks()
})
</script>

<style scoped>
.filter-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-item label {
  color: var(--text-secondary);
  white-space: nowrap;
}

.filter-item input,
.filter-item select {
  width: 150px;
}

.priority-badge {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.priority-0 { background: #f5f5f5; color: #666; }
.priority-1 { background: #fff7e6; color: #fa8c16; }
.priority-2 { background: #ffe7ba; color: #d46b08; }
.priority-3 { background: #fff2f0; color: #f5222d; }

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}
</style>

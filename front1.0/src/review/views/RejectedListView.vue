<template>
  <div class="rejected-list">
    <div class="card">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="tasks.length === 0" class="empty">暂无已驳回的任务</div>
      <table v-else>
        <thead>
          <tr>
            <th>教材名称</th>
            <th>作者</th>
            <th>类型</th>
            <th>审核人</th>
            <th>驳回时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="task in tasks" :key="task.id">
            <td>{{ task.book_title }}</td>
            <td>{{ task.book_author }}</td>
            <td>{{ task.task_type_display }}</td>
            <td>{{ task.assigned_reviewer_name || '-' }}</td>
            <td>{{ formatDate(task.updated_at) }}</td>
            <td>
              <router-link :to="`/review/review/${task.id}`" class="btn-default" style="padding: 4px 12px;">
                查看
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="totalPages > 1" class="pagination">
        <button class="btn-default" :disabled="currentPage === 1" @click="changePage(currentPage - 1)">上一页</button>
        <span>第 {{ currentPage }} / {{ totalPages }} 页</span>
        <button class="btn-default" :disabled="currentPage === totalPages" @click="changePage(currentPage + 1)">下一页</button>
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

const loadTasks = async () => {
  loading.value = true
  try {
    const data = await taskApi.getList({ status: 'rejected', page: currentPage.value })
    tasks.value = data.results || data
    const count = data.count || tasks.value.length
    totalPages.value = Math.ceil(count / 20)
  } catch (err) {
    console.error('加载失败', err)
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
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => loadTasks())
</script>

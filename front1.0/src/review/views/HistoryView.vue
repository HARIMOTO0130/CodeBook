<template>
  <div class="history-view">
    <div class="card">
      <h3 class="card-title">审核历史记录</h3>
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="records.length === 0" class="empty">暂无审核记录</div>
      <table v-else>
        <thead>
          <tr>
            <th>教材名称</th>
            <th>审核决定</th>
            <th>平均评分</th>
            <th>审核时间</th>
            <th>耗时</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="record in records" :key="record.id">
            <td>{{ record.task?.book_title || '-' }}</td>
            <td>
              <span :class="['status-badge', `status-${record.decision}`]">
                {{ record.decision_display }}
              </span>
            </td>
            <td>{{ record.average_score?.toFixed(1) || '-' }}</td>
            <td>{{ formatDate(record.completed_at) }}</td>
            <td>{{ record.review_duration ? `${record.review_duration}分钟` : '-' }}</td>
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
import { reviewApi } from '../api/review'

const records = ref([])
const loading = ref(false)
const currentPage = ref(1)
const totalPages = ref(1)

const loadRecords = async () => {
  loading.value = true
  try {
    const data = await reviewApi.getManualReviewList({ page: currentPage.value })
    records.value = data.results || data
    const count = data.count || records.value.length
    totalPages.value = Math.ceil(count / 20)
  } catch (err) {
    console.error('加载失败', err)
  } finally {
    loading.value = false
  }
}

const changePage = (page) => {
  currentPage.value = page
  loadRecords()
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

onMounted(() => loadRecords())
</script>

<style scoped>
.card-title {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--border-color);
}

.status-approved { background: #f6ffed; color: #52c41a; }
.status-rejected { background: #fff2f0; color: #f5222d; }
.status-needs_revision { background: #fff7e6; color: #fa8c16; }
</style>

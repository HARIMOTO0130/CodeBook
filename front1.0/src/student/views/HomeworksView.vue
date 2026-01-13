<template>
  <div class="student-homeworks-view">
    <div class="page-header">
      <h2>我的作业</h2>
      <div class="filter-section">
        <select v-model="statusFilter" class="filter-select">
          <option value="">全部状态</option>
          <option value="active">进行中</option>
          <option value="overdue">已过期</option>
          <option value="submitted">已提交</option>
        </select>
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="fetchHomeworks">重试</button>
    </div>
    
    <div v-else-if="filteredHomeworks.length > 0" class="homeworks-list">
      <div v-for="homework in filteredHomeworks" :key="homework.id" class="homework-card">
        <div class="homework-header">
          <div class="course-info">
            <span class="course-badge">{{ homework.class_obj?.name || '未知班级' }}</span>
          </div>
          <div class="homework-title-section">
            <h3>{{ homework.homework_name }}</h3>
            <div class="homework-status" :class="getStatusClass(homework)">
              {{ getStatusText(homework) }}
            </div>
          </div>
        </div>
        
        <div class="homework-meta">
          <div class="meta-item">
            <span class="meta-icon">📖</span>
            <span>{{ homework.chapter?.title || '未知章节' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-icon">👨‍🏫</span>
            <span>{{ homework.teacher?.teacher_name || '未知教师' }}</span>
          </div>
          <div class="meta-item">
            <span class="meta-icon">⭐</span>
            <span>总分: {{ homework.total_score }}分</span>
          </div>
        </div>
        
        <div class="homework-dates">
          <div class="date-item">
            <span class="date-label">发布时间:</span>
            <span class="date-value">{{ formatDate(homework.start_time) }}</span>
          </div>
          <div class="date-item">
            <span class="date-label">截止时间:</span>
            <span class="date-value" :class="isOverdue(homework) ? 'overdue' : ''">
              {{ formatDate(homework.end_time) }}
              <span v-if="isOverdue(homework)" class="overdue-tag">已过期</span>
            </span>
          </div>
        </div>
        
        <div class="homework-description">
          <p>{{ truncateText(homework.homework_content, 150) }}</p>
        </div>
        
        <div class="homework-actions">
          <button class="btn btn-primary" @click="viewHomeworkDetail(homework.id)">
            查看详情
          </button>
          <button v-if="!isOverdue(homework) && !hasSubmitted(homework)" class="btn btn-success" @click="viewHomeworkDetail(homework.id)">
            提交作业
          </button>
          <button v-else-if="hasSubmitted(homework)" class="btn btn-secondary">
            已提交
            <span v-if="homework.submission?.score" class="submission-score">
              ({{ homework.submission.score }}分)
            </span>
          </button>
          <button v-else class="btn btn-disabled" disabled>
            已过期
          </button>
        </div>
      </div>
    </div>
    
    <div v-else class="no-homeworks">
      <div class="empty-state">
        <div class="empty-icon">📝</div>
        <p>暂无作业</p>
        <p class="empty-hint">老师还没有发布作业</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { api } from '../api/api';

export default {
  name: 'StudentHomeworksView',
  setup() {
    const router = useRouter();
    const homeworks = ref([]);
    const loading = ref(true);
    const error = ref(null);
    const statusFilter = ref('');
    
    const fetchHomeworks = async () => {
      try {
        loading.value = true;
        const response = await api.getStudentHomeworks();
        console.log('API返回的作业数据:', response);
        homeworks.value = response;
        console.log('homeworks.value:', homeworks.value);
        error.value = null;
      } catch (err) {
        error.value = '获取作业列表失败：' + err.message;
        console.error('获取作业列表失败:', err);
        homeworks.value = [];
      } finally {
        loading.value = false;
        console.log('filteredHomeworks:', filteredHomeworks.value);
      }
    };
    
    const viewHomeworkDetail = (homeworkId) => {
      router.push(`/student/homeworks/${homeworkId}`);
    };
    
    const getStatusClass = (homework) => {
      if (isOverdue(homework)) {
        return 'status-overdue';
      }
      return 'status-active';
    };
    
    const getStatusText = (homework) => {
      if (isOverdue(homework)) {
        return '已过期';
      }
      return '进行中';
    };
    
    const isOverdue = (homework) => {
      const now = new Date();
      const endTime = new Date(homework.end_time);
      return now > endTime;
    };
    
    const hasSubmitted = (homework) => {
      // 检查作业是否已提交
      // 兼容不同的字段结构
      return !!homework.submission?.status && homework.submission.status >= 1;
    };
    
    const formatDate = (dateString) => {
      const date = new Date(dateString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    };
    
    const truncateText = (text, maxLength) => {
      if (!text) return '';
      if (text.length <= maxLength) return text;
      return text.substring(0, maxLength) + '...';
    };
    
    const filteredHomeworks = computed(() => {
      let filtered = homeworks.value;
      
      if (statusFilter.value) {
        if (statusFilter.value === 'active') {
          filtered = filtered.filter(homework => !isOverdue(homework) && !hasSubmitted(homework));
        } else if (statusFilter.value === 'overdue') {
          filtered = filtered.filter(homework => isOverdue(homework));
        } else if (statusFilter.value === 'submitted') {
          filtered = filtered.filter(hasSubmitted);
        }
      }
      
      // 按截止时间排序，近的在前
      return filtered.sort((a, b) => {
        return new Date(a.end_time) - new Date(b.end_time);
      });
    });
    
    onMounted(() => {
      fetchHomeworks();
    });
    
    return {
      homeworks,
      loading,
      error,
      statusFilter,
      filteredHomeworks,
      fetchHomeworks,
      viewHomeworkDetail,
      getStatusClass,
      getStatusText,
      isOverdue,
      hasSubmitted,
      formatDate,
      truncateText
    };
  }
};
</script>

<style scoped>
.student-homeworks-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-header h2 {
  color: #2c3e50;
  margin: 0;
  font-size: 28px;
  font-weight: 600;
}

.filter-section {
  display: flex;
  align-items: center;
}

.filter-select {
  padding: 8px 12px;
  border: 1px solid #e1e8ed;
  border-radius: 6px;
  font-size: 14px;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.2s;
}

.filter-select:hover {
  border-color: #3498db;
}

.loading, .error, .no-homeworks {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  border-radius: 12px;
  text-align: center;
  margin-bottom: 20px;
}

.loading {
  background-color: #e8f4f8;
  color: #3498db;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e3f2fd;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error {
  background-color: #fff2f2;
  color: #e74c3c;
}

.error button {
  margin-top: 15px;
}

.no-homeworks {
  background-color: #f9f9f9;
  color: #95a5a6;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 10px;
}

.empty-hint {
  font-size: 14px;
  color: #bdc3c7;
}

.homeworks-list {
  display: grid;
  gap: 24px;
}

.homework-card {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 24px;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  border: 1px solid #e1e8ed;
}

.homework-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
  border-color: #d5e4f0;
}

.homework-header {
  margin-bottom: 16px;
}

.course-info {
  margin-bottom: 8px;
}

.course-badge {
  display: inline-block;
  padding: 4px 12px;
  background-color: #e3f2fd;
  color: #1976d2;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.homework-title-section {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.homework-title-section h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 20px;
  font-weight: 600;
  line-height: 1.4;
}

.homework-status {
  padding: 6px 12px;
  border-radius: 18px;
  font-size: 13px;
  font-weight: bold;
  margin-left: 12px;
  white-space: nowrap;
}

.status-active {
  background-color: #e8f5e8;
  color: #2e7d32;
}

.status-overdue {
  background-color: #ffebee;
  color: #d32f2f;
}

.homework-meta {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
  font-size: 14px;
  color: #666;
  flex-wrap: wrap;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.meta-icon {
  font-size: 16px;
}

.homework-dates {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  font-size: 14px;
  color: #666;
  flex-wrap: wrap;
}

.date-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-label {
  font-weight: 600;
  color: #333;
}

.date-value {
  display: flex;
  align-items: center;
  gap: 6px;
}

.date-value.overdue {
  color: #d32f2f;
  font-weight: 500;
}

.overdue-tag {
  padding: 2px 8px;
  background-color: #ffebee;
  color: #d32f2f;
  border-radius: 12px;
  font-size: 11px;
  font-weight: bold;
}

.homework-description {
  margin-bottom: 24px;
  color: #555;
  line-height: 1.6;
  font-size: 14px;
}

.homework-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover {
  background-color: #2980b9;
  transform: translateY(-1px);
}

.btn-success {
  background-color: #2ecc71;
  color: white;
}

.btn-success:hover {
  background-color: #27ae60;
  transform: translateY(-1px);
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.btn-disabled {
  background-color: #bdc3c7;
  color: white;
  cursor: not-allowed;
}

.submission-score {
  font-size: 13px;
  opacity: 0.9;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .student-homeworks-view {
    padding: 12px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .homework-meta {
    gap: 16px;
  }
  
  .homework-dates {
    gap: 16px;
  }
  
  .homework-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
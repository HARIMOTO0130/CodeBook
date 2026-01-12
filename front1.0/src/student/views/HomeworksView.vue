<template>
  <div class="student-homeworks-view">
    <h2>我的作业</h2>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="homeworks.length > 0" class="homeworks-list">
      <div v-for="homework in homeworks" :key="homework.id" class="homework-card">
        <div class="homework-header">
          <h3>{{ homework.homework_name }}</h3>
          <div class="homework-status" :class="getStatusClass(homework)">
            {{ getStatusText(homework) }}
          </div>
        </div>
        <div class="homework-meta">
          <span class="chapter">{{ homework.chapter?.title || '未知章节' }}</span>
          <span class="teacher">{{ homework.teacher?.teacher_name || '未知教师' }}</span>
          <span class="score">总分: {{ homework.total_score }}分</span>
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
            </span>
          </div>
        </div>
        <div class="homework-content">
          <p>{{ truncateText(homework.homework_content, 150) }}</p>
        </div>
        <div class="homework-actions">
          <button class="btn btn-primary" @click="viewHomeworkDetail(homework.id)">
            查看详情
          </button>
          <button v-if="!hasSubmitted(homework)" class="btn btn-success" @click="submitHomework(homework.id)">
            提交作业
          </button>
          <button v-else class="btn btn-secondary" disabled>
            已提交
          </button>
        </div>
      </div>
    </div>
    <div v-else class="no-homeworks">
      <p>暂无作业</p>
    </div>
  </div>
</template>

<script>
import { api } from '../api/api';

export default {
  name: 'StudentHomeworksView',
  data() {
    return {
      homeworks: [],
      loading: true,
      error: null
    };
  },
  async mounted() {
    await this.fetchHomeworks();
  },
  methods: {
    async fetchHomeworks() {
      try {
        this.loading = true;
        this.homeworks = await api.getStudentHomeworks();
        this.error = null;
      } catch (err) {
        this.error = '获取作业列表失败：' + err.message;
        console.error('获取作业列表失败:', err);
      } finally {
        this.loading = false;
      }
    },
    viewHomeworkDetail(homeworkId) {
      // 跳转到作业详情页
      this.$router.push(`/student/homeworks/${homeworkId}`);
    },
    submitHomework(homeworkId) {
      // 跳转到作业提交页
      this.$router.push(`/student/homeworks/${homeworkId}/submit`);
    },
    getStatusClass(homework) {
      if (this.isOverdue(homework)) {
        return 'status-overdue';
      }
      return 'status-active';
    },
    getStatusText(homework) {
      if (this.isOverdue(homework)) {
        return '已过期';
      }
      return '进行中';
    },
    isOverdue(homework) {
      const now = new Date();
      const endTime = new Date(homework.end_time);
      return now > endTime;
    },
    hasSubmitted(homework) {
      // 这里需要根据实际的提交状态判断，暂时假设所有作业都未提交
      return false;
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
.student-homeworks-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  color: #333;
  margin-bottom: 20px;
}

.loading, .error, .no-homeworks {
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

.no-homeworks {
  background-color: #fff3e0;
  color: #f57c00;
}

.homeworks-list {
  display: grid;
  gap: 20px;
}

.homework-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.homework-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.homework-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.homework-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.homework-status {
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 14px;
  font-weight: bold;
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
  gap: 15px;
  flex-wrap: wrap;
  margin-bottom: 15px;
}

.homework-meta span {
  background-color: #f5f5f5;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 14px;
  color: #666;
}

.homework-dates {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.date-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
}

.date-label {
  color: #888;
}

.date-value {
  color: #666;
  font-weight: 500;
}

.date-value.overdue {
  color: #d32f2f;
  font-weight: bold;
}

.homework-content {
  margin-bottom: 20px;
}

.homework-content p {
  margin: 0;
  color: #666;
  line-height: 1.5;
}

.homework-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
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

.btn-success {
  background-color: #4caf50;
  color: white;
}

.btn-success:hover {
  background-color: #45a049;
}

.btn-secondary {
  background-color: #9e9e9e;
  color: white;
  cursor: not-allowed;
}
</style>
<template>
  <div class="student-homework-detail-view">
    <h2>作业详情</h2>
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="homework" class="homework-detail">
      <div class="homework-header">
        <h3>{{ homework.homework_name }}</h3>
        <div class="homework-status" :class="getStatusClass(homework)">
          {{ getStatusText(homework) }}
        </div>
      </div>
      <div class="homework-meta">
        <div class="meta-item">
          <span class="meta-label">关联章节:</span>
          <span class="meta-value">{{ homework.chapter?.title || '未知章节' }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">授课教师:</span>
          <span class="meta-value">{{ homework.teacher?.teacher_name || '未知教师' }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">总分:</span>
          <span class="meta-value">{{ homework.total_score }}分</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">班级:</span>
          <span class="meta-value">{{ homework.class_obj?.name || '未知班级' }}</span>
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
          </span>
        </div>
      </div>
      <div class="homework-content">
        <h4>作业内容</h4>
        <div class="content-body" v-html="homework.homework_content"></div>
      </div>
      
      <div v-if="!isOverdue(homework) && !hasSubmitted" class="submit-section">
        <h4>提交作业</h4>
        <div class="submit-form">
          <textarea 
            v-model="submitContent" 
            class="submit-textarea" 
            placeholder="请输入作业内容..."
            rows="10"
          ></textarea>
          <div class="submit-actions">
            <button class="btn btn-primary" @click="submitHomework" :disabled="submitting">
              {{ submitting ? '提交中...' : '提交作业' }}
            </button>
          </div>
        </div>
      </div>
      
      <div v-else-if="hasSubmitted" class="submitted-section">
        <h4>已提交作业</h4>
        <div class="submitted-content">
          <p>{{ submittedContent || '暂无提交内容' }}</p>
        </div>
      </div>
      
      <div v-else class="overdue-section">
        <h4>作业已过期</h4>
        <p>作业已超过截止时间，无法提交。</p>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '../api/api';

export default {
  name: 'StudentHomeworkDetailView',
  props: {
    homeworkId: {
      type: Number,
      required: true
    }
  },
  data() {
    return {
      homework: null,
      loading: true,
      error: null,
      submitContent: '',
      submitting: false,
      hasSubmitted: false,
      submittedContent: ''
    };
  },
  async mounted() {
    await this.fetchHomeworkDetail();
  },
  methods: {
    async fetchHomeworkDetail() {
      try {
        this.loading = true;
        this.homework = await api.getStudentHomeworkDetail(this.homeworkId);
        this.error = null;
        // 这里需要检查是否已提交作业，暂时假设未提交
        this.hasSubmitted = false;
      } catch (err) {
        this.error = '获取作业详情失败：' + err.message;
        console.error('获取作业详情失败:', err);
      } finally {
        this.loading = false;
      }
    },
    async submitHomework() {
      if (!this.submitContent.trim()) {
        alert('请输入作业内容');
        return;
      }
      
      try {
        this.submitting = true;
        await api.submitStudentHomework(this.homeworkId, this.submitContent);
        this.hasSubmitted = true;
        this.submittedContent = this.submitContent;
        alert('作业提交成功');
      } catch (err) {
        alert('作业提交失败：' + err.message);
        console.error('作业提交失败:', err);
      } finally {
        this.submitting = false;
      }
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
    formatDate(dateString) {
      const date = new Date(dateString);
      return date.toLocaleString();
    }
  }
};
</script>

<style scoped>
.student-homework-detail-view {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  color: #333;
  margin-bottom: 20px;
}

.loading, .error {
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

.homework-detail {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.homework-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.homework-header h3 {
  margin: 0;
  color: #333;
  font-size: 20px;
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
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.meta-item {
  display: flex;
  gap: 5px;
  align-items: center;
  font-size: 14px;
}

.meta-label {
  color: #888;
}

.meta-value {
  color: #666;
  font-weight: 500;
}

.homework-dates {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
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

.homework-content h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
}

.content-body {
  color: #666;
  line-height: 1.6;
  background-color: #f9f9f9;
  padding: 15px;
  border-radius: 8px;
  white-space: pre-wrap;
}

.submit-section, .submitted-section, .overdue-section {
  margin-top: 20px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.submit-section h4, .submitted-section h4, .overdue-section h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
}

.submit-form {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.submit-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  min-height: 200px;
}

.submit-actions {
  display: flex;
  justify-content: flex-end;
}

.submitted-content {
  background-color: #e8f5e8;
  padding: 15px;
  border-radius: 4px;
  color: #666;
  line-height: 1.6;
}

.overdue-section {
  background-color: #ffebee;
}

.overdue-section p {
  margin: 0;
  color: #d32f2f;
}

.btn {
  padding: 10px 20px;
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

.btn-primary:disabled {
  background-color: #90caf9;
  cursor: not-allowed;
}
</style>
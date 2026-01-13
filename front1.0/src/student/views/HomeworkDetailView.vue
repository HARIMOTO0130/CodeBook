<template>
  <div class="student-homework-detail-view">
    <div class="page-header">
      <h2>作业详情</h2>
      <button class="btn btn-secondary" @click="$router.back()">
        返回列表
      </button>
    </div>
    
    <div v-if="loading" class="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button class="btn btn-primary" @click="fetchHomeworkDetail">重试</button>
    </div>
    
    <div v-else-if="homework" class="homework-detail">
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
        <div v-if="homework.submission?.submit_time" class="date-item">
          <span class="date-label">提交时间:</span>
          <span class="date-value">{{ formatDate(homework.submission.submit_time) }}</span>
        </div>
      </div>
      
      <div class="homework-content">
        <h4>作业内容</h4>
        <div class="content-body" v-html="homework.homework_content"></div>
      </div>
      
      <!-- 作业作答区域 -->
      <div v-if="!isOverdue(homework)" class="submit-section">
        <div class="section-header">
          <h4>提交作业</h4>
          <div v-if="lastSavedTime" class="last-saved">
            <span class="save-status">
              <span v-if="saving" class="saving-indicator">💾</span>
              {{ saving ? '保存中...' : `最后保存: ${formatDate(lastSavedTime)}` }}
            </span>
          </div>
        </div>
        
        <div class="submit-form">
          <textarea 
            v-model="submitContent" 
            class="submit-textarea" 
            placeholder="请输入作业内容..."
            rows="12"
            @input="debouncedSaveDraft"
          ></textarea>
          
          <!-- 文件上传区域 -->
          <div class="file-upload-section">
            <h5>上传文件（可选）</h5>
            <div class="file-upload-area" @click="triggerFileInput" @dragover.prevent="isDragging = true" @dragleave.prevent="isDragging = false" @drop.prevent="handleDrop">
              <div v-if="isDragging" class="file-upload-area-dragging">
                <span class="file-icon">📁</span>
                <p>松开鼠标上传文件</p>
              </div>
              <div v-else>
                <span class="file-icon">📁</span>
                <p>点击选择文件或拖拽文件到此处</p>
                <p class="file-upload-hint">支持 PDF、Word、PPT、图片等格式，单个文件最大500MB</p>
              </div>
              <input ref="fileInput" type="file" multiple @change="handleFileSelect" style="display: none;" accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.md,.jpg,.jpeg,.png,.gif,.webp,.mp4,.avi,.mov,.webm,.mp3,.wav,.ogg">
            </div>
            
            <!-- 已上传文件列表 -->
            <div class="uploaded-files" v-if="uploadedFiles.length > 0">
              <h5>已上传文件</h5>
              <div class="file-list">
                <div v-for="file in uploadedFiles" :key="file.id || file.tempId" class="file-item">
                  <div class="file-info">
                    <span class="file-icon">{{ getFileIcon(file.mime_type || file.type) }}</span>
                    <div class="file-details">
                      <p class="file-name">{{ file.file_name || file.name }}</p>
                      <p class="file-size">{{ formatFileSize(file.file_size || file.size) }}</p>
                    </div>
                  </div>
                  <div class="file-actions">
                    <button v-if="file.id" class="file-action-btn download" @click="downloadFile(file)">下载</button>
                    <button class="file-action-btn remove" @click="removeFile(file)">删除</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div class="submit-actions">
            <button 
              class="btn btn-secondary" 
              @click="saveDraft" 
              :disabled="saving"
            >
              {{ saving ? '保存中...' : '保存草稿' }}
            </button>
            <button 
              class="btn btn-primary" 
              @click="submitHomework" 
              :disabled="submitting || !canSubmit"
            >
              {{ submitting ? '提交中...' : '提交作业' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- 已提交作业区域 -->
      <div v-else-if="homework.submission" class="submitted-section">
        <div class="section-header">
          <h4>已提交作业</h4>
          <div v-if="homework.submission.score !== null" class="score-badge" :class="getScoreClass(homework.submission.score)">
            {{ homework.submission.score }}分
          </div>
        </div>
        
        <div class="submitted-content">
          <div class="content-body" v-html="homework.submission.submit_content || '<p>暂无提交内容</p>'"></div>
          <div class="submission-meta">
            <div class="meta-item">
              <span class="meta-label">提交时间:</span>
              <span class="meta-value">{{ formatDate(homework.submission.submit_time) }}</span>
            </div>
            <div v-if="homework.submission.score !== null" class="meta-item">
              <span class="meta-label">批改时间:</span>
              <span class="meta-value">{{ formatDate(homework.submission.graded_time) }}</span>
            </div>
          </div>
          
          <!-- 教师评语 -->
          <div v-if="homework.submission.comment" class="teacher-comment">
            <h5>教师评语</h5>
            <div class="comment-content">
              {{ homework.submission.comment }}
            </div>
          </div>
        </div>
        
        <!-- 查看历史记录 -->
        <div class="history-section">
          <button class="btn btn-link" @click="showHistory = !showHistory">
            {{ showHistory ? '收起历史记录' : '查看提交历史' }}
          </button>
          <div v-if="showHistory" class="history-list">
            <div v-if="submissionHistory.length === 0" class="no-history">
              <p>暂无历史记录</p>
            </div>
            <div v-else class="history-items">
              <div v-for="record in submissionHistory" :key="record.id" class="history-item">
                <div class="history-header">
                  <span class="history-time">{{ formatDate(record.submit_time) }}</span>
                  <span class="history-status" :class="record.status === 1 ? 'status-submitted' : (record.status === 2 ? 'status-graded' : 'status-draft')">
                    {{ record.status === 1 ? '已提交' : (record.status === 2 ? '已批改' : '草稿') }}
                  </span>
                </div>
                <div class="history-content" v-html="record.submit_content || '<p>暂无内容</p>'"></div>
                <!-- 批改信息 -->
                <div v-if="record.status === 2 && (record.score !== null || record.feedback)" class="grading-info">
                  <div class="grading-header">
                    <span class="grading-time">{{ formatDate(record.grade_time) }}</span>
                    <span class="grading-score" :class="getScoreClass(record.score)">
                      得分: {{ record.score }}/{{ homework.total_score }}
                    </span>
                  </div>
                  <div v-if="record.feedback" class="grading-feedback">
                    <h6>教师反馈:</h6>
                    <div v-html="record.feedback"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 作业过期区域 -->
      <div v-else class="overdue-section">
        <h4>作业已过期</h4>
        <p>作业已超过截止时间，无法提交。</p>
        
        <div v-if="homework.submission" class="submitted-section">
          <h5>已提交内容</h5>
          <div class="submitted-content">
            <div class="content-body" v-html="homework.submission.submit_content || '<p>暂无提交内容</p>'"></div>
            <div class="submission-meta">
              <div class="meta-item">
                <span class="meta-label">提交时间:</span>
                <span class="meta-value">{{ formatDate(homework.submission.submit_time) }}</span>
              </div>
            </div>
          </div>
          
          <!-- 批改信息 -->
          <div v-if="homework.submission.status === 2 && (homework.submission.score !== null || homework.submission.feedback)" class="grading-info">
            <div class="grading-header">
              <span class="grading-time">{{ formatDate(homework.submission.grade_time) }}</span>
              <span class="grading-score" :class="getScoreClass(homework.submission.score)">
                得分: {{ homework.submission.score }}/{{ homework.total_score }}
              </span>
            </div>
            <div v-if="homework.submission.feedback" class="grading-feedback">
              <h6>教师反馈:</h6>
              <div v-html="homework.submission.feedback"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 提交成功提示 -->
    <div v-if="showSuccessModal" class="modal-overlay" @click="showSuccessModal = false">
      <div class="modal-content" @click.stop>
        <div class="success-icon">✅</div>
        <h4>提交成功</h4>
        <p>您的作业已成功提交！</p>
        <button class="btn btn-primary" @click="showSuccessModal = false">确定</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { api } from '../api/api';

export default {
  name: 'StudentHomeworkDetailView',
  setup() {
    const router = useRouter();
    const route = useRoute();
    const homeworkId = computed(() => parseInt(route.params.homeworkId));
    
    const homework = ref(null);
    const loading = ref(true);
    const error = ref(null);
    const submitContent = ref('');
    const submitting = ref(false);
    const saving = ref(false);
    const lastSavedTime = ref(null);
    const showHistory = ref(false);
    const submissionHistory = ref([]);
    const showSuccessModal = ref(false);
    
    // 文件上传相关状态
    const isDragging = ref(false);
    const uploadedFiles = ref([]);
    const fileInput = ref(null);
    
    let saveTimeout = null;
    
    // 防抖保存草稿函数
    const debouncedSaveDraft = () => {
      if (saveTimeout) {
        clearTimeout(saveTimeout);
      }
      saveTimeout = setTimeout(() => {
        saveDraft();
      }, 3000); // 3秒防抖
    };
    
    // 清理定时器
    onBeforeUnmount(() => {
      if (saveTimeout) {
        clearTimeout(saveTimeout);
      }
    });
    
    // 获取作业详情
    const fetchHomeworkDetail = async () => {
      try {
        loading.value = true;
        const [homeworkData, historyData] = await Promise.all([
          api.getStudentHomeworkDetail(homeworkId.value),
          api.getHomeworkSubmissionHistory(homeworkId.value)
        ]);
        
        homework.value = homeworkData;
        submissionHistory.value = historyData;
        error.value = null;
        
        // 如果有已提交的作业，使用提交的内容
        if (homeworkData.submission) {
          submitContent.value = homeworkData.submission.submit_content || '';
        } else {
          // 尝试从本地存储加载草稿
          const savedDraft = localStorage.getItem(`homework_draft_${homeworkId.value}`);
          if (savedDraft) {
            submitContent.value = savedDraft;
          }
        }
      } catch (err) {
        error.value = '获取作业详情失败：' + err.message;
        console.error('获取作业详情失败:', err);
      } finally {
        loading.value = false;
      }
    };
    
    // 保存草稿
    const saveDraft = async () => {
      if (!submitContent.value.trim()) return;
      
      try {
        saving.value = true;
        // 先保存到本地存储
        localStorage.setItem(`homework_draft_${homeworkId.value}`, submitContent.value);
        lastSavedTime.value = new Date();
        
        // 然后尝试保存到服务器
        await api.saveHomeworkDraft(homeworkId.value, submitContent.value);
      } catch (err) {
        console.error('保存草稿失败:', err);
        // 本地存储已经保存，所以不显示错误
      } finally {
        saving.value = false;
      }
    };
    
    // 提交作业
    const submitHomework = async () => {
      if (!submitContent.value.trim()) {
        alert('请输入作业内容');
        return;
      }
      
      try {
        submitting.value = true;
        await api.submitStudentHomework(homeworkId.value, submitContent.value);
        
        // 清除本地草稿
        localStorage.removeItem(`homework_draft_${homeworkId.value}`);
        
        // 刷新作业详情
        await fetchHomeworkDetail();
        
        // 显示提交成功提示
        showSuccessModal.value = true;
      } catch (err) {
        alert('作业提交失败：' + err.message);
        console.error('作业提交失败:', err);
      } finally {
        submitting.value = false;
      }
    };
    
    // 获取状态样式类
    const getStatusClass = (homework) => {
      if (isOverdue(homework)) {
        return 'status-overdue';
      }
      return 'status-active';
    };
    
    // 获取状态文本
    const getStatusText = (homework) => {
      if (isOverdue(homework)) {
        return '已过期';
      }
      return '进行中';
    };
    
    // 判断是否过期
    const isOverdue = (homework) => {
      const now = new Date();
      const endTime = new Date(homework.end_time);
      return now > endTime;
    };
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    };
    
    // 获取评分样式类
    const getScoreClass = (score) => {
      if (score >= 90) return 'score-excellent';
      if (score >= 80) return 'score-good';
      if (score >= 60) return 'score-pass';
      return 'score-fail';
    };
    
    // 文件上传相关函数
    const triggerFileInput = () => {
      fileInput.value?.click();
    };
    
    const handleFileSelect = (event) => {
      const files = Array.from(event.target.files);
      uploadFiles(files);
      // 清空输入，以便可以重新选择相同的文件
      event.target.value = '';
    };
    
    const handleDrop = (event) => {
      isDragging.value = false;
      const files = Array.from(event.dataTransfer.files);
      uploadFiles(files);
    };
    
    const uploadFiles = async (files) => {
      for (const file of files) {
        try {
          // 为临时文件生成一个ID
          const tempFile = {
            tempId: Date.now() + Math.random(),
            name: file.name,
            size: file.size,
            type: file.type,
            file: file, // 保存实际文件对象以便上传
            uploading: true
          };
          
          uploadedFiles.value.push(tempFile);
          
          // 上传文件到服务器
          const result = await api.uploadHomeworkFile(homeworkId.value, file);
          
          // 替换临时文件为服务器返回的文件信息
          const index = uploadedFiles.value.findIndex(f => f.tempId === tempFile.tempId);
          if (index !== -1) {
            uploadedFiles.value[index] = result;
          }
        } catch (err) {
          console.error('文件上传失败:', err);
          alert(`文件上传失败: ${file.name}\n${err.message}`);
          
          // 移除上传失败的文件
          const index = uploadedFiles.value.findIndex(f => f.name === file.name);
          if (index !== -1) {
            uploadedFiles.value.splice(index, 1);
          }
        }
      }
    };
    
    const removeFile = (file) => {
      const index = uploadedFiles.value.findIndex(f => f.id === file.id || f.tempId === file.tempId);
      if (index !== -1) {
        uploadedFiles.value.splice(index, 1);
      }
    };
    
    const downloadFile = (file) => {
      // 创建下载链接
      const link = document.createElement('a');
      link.href = file.file_url || file.path;
      link.download = file.file_name || file.name;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    };
    
    const formatFileSize = (bytes) => {
      if (!bytes) return '0 B';
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };
    
    const getFileIcon = (mime_type) => {
      if (!mime_type) return '📄';
      
      if (mime_type.startsWith('image/')) return '🖼️';
      if (mime_type.startsWith('application/pdf')) return '📄';
      if (mime_type.startsWith('application/msword') || mime_type.startsWith('application/vnd.openxmlformats-officedocument.wordprocessingml.document')) return '📝';
      if (mime_type.startsWith('application/vnd.ms-powerpoint') || mime_type.startsWith('application/vnd.openxmlformats-officedocument.presentationml.presentation')) return '📊';
      if (mime_type.startsWith('application/vnd.ms-excel') || mime_type.startsWith('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')) return '📈';
      if (mime_type.startsWith('text/')) return '📄';
      if (mime_type.startsWith('audio/')) return '🎵';
      if (mime_type.startsWith('video/')) return '🎬';
      
      return '📁';
    };
    
    // 判断是否可以提交
    const canSubmit = computed(() => {
      return (submitContent.value.trim().length > 0 || uploadedFiles.value.length > 0) && !submitting.value;
    });
    
    // 组件挂载时获取作业详情
    onMounted(() => {
      fetchHomeworkDetail();
    });
    
    return {
      homework,
      loading,
      error,
      submitContent,
      submitting,
      saving,
      lastSavedTime,
      showHistory,
      submissionHistory,
      showSuccessModal,
      isDragging,
      uploadedFiles,
      fileInput,
      fetchHomeworkDetail,
      saveDraft,
      submitHomework,
      getStatusClass,
      getStatusText,
      isOverdue,
      formatDate,
      getScoreClass,
      canSubmit,
      debouncedSaveDraft,
      triggerFileInput,
      handleFileSelect,
      handleDrop,
      removeFile,
      downloadFile,
      formatFileSize,
      getFileIcon
    };
  }
};
</script>

<style scoped>
.student-homework-detail-view {
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

.loading, .error {
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

.homework-detail {
  background-color: #fff;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  padding: 24px;
  border: 1px solid #e1e8ed;
}

.homework-header {
  margin-bottom: 20px;
}

.course-info {
  margin-bottom: 10px;
}

.course-badge {
  display: inline-block;
  padding: 5px 12px;
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
  flex-wrap: wrap;
  gap: 12px;
}

.homework-title-section h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
  line-height: 1.4;
}

.homework-status {
  padding: 6px 14px;
  border-radius: 18px;
  font-size: 13px;
  font-weight: bold;
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
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.meta-item {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 14px;
}

.meta-label {
  color: #666;
  font-weight: 500;
}

.meta-value {
  color: #333;
  font-weight: 600;
}

.homework-dates {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  padding: 16px;
  background-color: #f9f9f9;
  border-radius: 8px;
  flex-wrap: wrap;
}

.date-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.date-label {
  color: #666;
  font-weight: 500;
}

.date-value {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #333;
  font-weight: 600;
}

.date-value.overdue {
  color: #d32f2f;
}

.overdue-tag {
  padding: 2px 8px;
  background-color: #ffebee;
  color: #d32f2f;
  border-radius: 12px;
  font-size: 11px;
  font-weight: bold;
}

.homework-content {
  margin-bottom: 24px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.homework-content h4 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.content-body {
  color: #555;
  line-height: 1.7;
  background-color: #fff;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid #e1e8ed;
  white-space: pre-wrap;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h4 {
  margin: 0;
  color: #333;
  font-size: 20px;
  font-weight: 600;
}

.last-saved {
  font-size: 13px;
  color: #666;
}

.save-status {
  display: flex;
  align-items: center;
  gap: 6px;
}

.saving-indicator {
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0% { opacity: 0.6; }
  50% { opacity: 1; }
  100% { opacity: 0.6; }
}

.submit-section, .submitted-section, .overdue-section {
  margin-top: 24px;
  padding: 24px;
  background-color: #f9f9f9;
  border-radius: 12px;
  border: 1px solid #e1e8ed;
}

.submit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.submit-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.7;
  resize: vertical;
  min-height: 250px;
  background-color: #fff;
  font-family: inherit;
  transition: border-color 0.2s;
}

.submit-textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
}

.submit-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

.submitted-content {
  background-color: #fff;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e1e8ed;
}

.submission-meta {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e1e8ed;
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.score-badge {
  padding: 6px 14px;
  border-radius: 18px;
  font-size: 14px;
  font-weight: bold;
  white-space: nowrap;
}

.score-excellent {
  background-color: #e8f5e8;
  color: #2e7d32;
}

.score-good {
  background-color: #e3f2fd;
  color: #1976d2;
}

.score-pass {
  background-color: #fff8e1;
  color: #f57f17;
}

.score-fail {
  background-color: #ffebee;
  color: #d32f2f;
}

.teacher-comment {
  margin-top: 20px;
  padding: 16px;
  background-color: #e3f2fd;
  border-radius: 8px;
  border-left: 4px solid #1976d2;
}

.teacher-comment h5 {
  margin: 0 0 8px 0;
  color: #1976d2;
  font-size: 16px;
  font-weight: 600;
}

.comment-content {
  color: #333;
  line-height: 1.6;
}

.history-section {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid #e1e8ed;
}

.btn-link {
  background: none;
  border: none;
  color: #3498db;
  font-size: 14px;
  cursor: pointer;
  padding: 0;
  text-decoration: underline;
  transition: color 0.2s;
}

.btn-link:hover {
  color: #2980b9;
}

.history-list {
  margin-top: 16px;
}

.no-history {
  padding: 20px;
  text-align: center;
  color: #95a5a6;
}

.history-items {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.history-item {
  padding: 16px;
  background-color: #fff;
  border-radius: 8px;
  border: 1px solid #e1e8ed;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-size: 13px;
}

.history-time {
  color: #666;
  font-weight: 500;
}

.history-status {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: bold;
}

.status-draft {
  background-color: #fff8e1;
  color: #f57f17;
}

.status-submitted {
  background-color: #e8f5e8;
  color: #2e7d32;
}

.status-graded {
  background-color: #e1f5fe;
  color: #0277bd;
}

/* 批改信息样式 */
.grading-info {
  margin-top: 15px;
  padding: 15px;
  background-color: #f8f9fa;
  border-left: 4px solid #28a745;
  border-radius: 0 4px 4px 0;
}

.grading-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.grading-time {
  font-size: 12px;
  color: #6c757d;
}

.grading-score {
  font-size: 14px;
  font-weight: bold;
}

.grading-feedback {
  margin-top: 10px;
}

.grading-feedback h6 {
  margin-bottom: 5px;
  color: #343a40;
}

/* 分数样式 */
.score-excellent {
  color: #28a745;
}

.score-good {
  color: #17a2b8;
}

.score-passing {
  color: #ffc107;
}

.score-failing {
  color: #dc3545;
}

.history-content {
  color: #555;
  line-height: 1.6;
  font-size: 14px;
  white-space: pre-wrap;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  padding: 40px;
  border-radius: 12px;
  text-align: center;
  max-width: 400px;
  width: 90%;
}

.success-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.modal-content h4 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 20px;
}

.modal-content p {
  margin: 0 0 24px 0;
  color: #666;
}

.overdue-section {
  background-color: #fff;
  border: 1px solid #ffebee;
}

.overdue-section h4 {
  color: #d32f2f;
}

.overdue-section p {
  margin: 0;
  color: #d32f2f;
  font-weight: 500;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
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
  box-shadow: 0 4px 12px rgba(52, 152, 219, 0.3);
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover {
  background-color: #7f8c8d;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .student-homework-detail-view {
    padding: 12px;
  }
  
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }
  
  .homework-title-section {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .homework-dates {
    flex-direction: column;
    gap: 12px;
  }
  
  .submit-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
  
  .submission-meta {
    flex-direction: column;
    gap: 12px;
  }
}

/* 文件上传样式 */
.file-upload-section {
  margin-top: 24px;
  margin-bottom: 24px;
}

.file-upload-section h5 {
  margin-bottom: 12px;
  color: #333;
  font-size: 16px;
  font-weight: 600;
}

.file-upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background-color: #f9f9f9;
}

.file-upload-area:hover {
  border-color: #3498db;
  background-color: #f0f7ff;
}

.file-upload-area-dragging {
  border-color: #3498db;
  background-color: #e3f2fd;
  transform: scale(1.02);
}

.file-upload-area .file-icon {
  font-size: 48px;
  margin-bottom: 12px;
  display: block;
}

.file-upload-area p {
  margin: 0 0 4px 0;
  color: #666;
  font-size: 14px;
}

.file-upload-hint {
  font-size: 12px !important;
  color: #999 !important;
}

.uploaded-files {
  margin-top: 20px;
}

.file-list {
  border: 1px solid #eee;
  border-radius: 8px;
  overflow: hidden;
}

.file-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #eee;
  transition: background-color 0.2s ease;
}

.file-item:last-child {
  border-bottom: none;
}

.file-item:hover {
  background-color: #f9f9f9;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-info .file-icon {
  font-size: 24px;
  min-width: 24px;
}

.file-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.file-name {
  margin: 0;
  font-size: 14px;
  color: #333;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 300px;
}

.file-size {
  margin: 0;
  font-size: 12px;
  color: #999;
}

.file-actions {
  display: flex;
  gap: 8px;
}

.file-action-btn {
  padding: 4px 12px;
  font-size: 12px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.file-action-btn.download {
  background-color: #3498db;
  color: white;
}

.file-action-btn.download:hover {
  background-color: #2980b9;
}

.file-action-btn.remove {
  background-color: #e74c3c;
  color: white;
}

.file-action-btn.remove:hover {
  background-color: #c0392b;
}

/* 响应式设计 - 文件上传 */
@media (max-width: 768px) {
  .file-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .file-actions {
    align-self: stretch;
    justify-content: flex-start;
  }
  
  .file-name {
    max-width: 200px;
  }
}
</style>
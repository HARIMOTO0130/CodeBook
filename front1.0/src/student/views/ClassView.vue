<template>
  <div class="student-class-view">
    <div class="page-header">
      <h2>我的班级</h2>
      <button class="btn btn-primary" @click="showJoinClassModal = true">
        <span class="icon">+</span> 加入新班级
      </button>
    </div>
    
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else class="class-content-container">
      <!-- 错误提示 -->
      <div v-if="error" class="error-card">
        <div class="error-icon">⚠️</div>
        <div class="error-message">
          <p>获取班级信息失败</p>
          <p class="error-details" v-if="showDetails">{{ error }}</p>
        </div>
        <div class="error-actions">
          <button class="btn btn-primary" @click="fetchClassInfo">重试</button>
          <button class="btn btn-secondary" @click="toggleDetails">
            {{ showDetails ? '隐藏详情' : '显示详情' }}
          </button>
        </div>
      </div>
      
      <!-- 班级列表 -->
      <div v-if="classes.length > 0" class="classes-list">
        <div v-for="classItem in classes" :key="classItem.id" class="class-card">
          <div class="class-header">
            <h3>{{ classItem.name }}</h3>
            <div class="class-meta">
              <span class="major">{{ classItem.major }}</span>
              <span class="grade">{{ classItem.grade }}</span>
              <span class="student-count">学生: {{ classItem.student_count }}</span>
            </div>
          </div>
          <div class="class-content">
            <div class="class-description">
              <h4>班级描述</h4>
              <p>{{ classItem.description || '暂无描述' }}</p>
            </div>
            <div class="class-teacher">
              <h4>授课教师</h4>
              <p>{{ classItem.teacher_name || '未知教师' }}</p>
            </div>
            <div class="class-book">
              <h4>关联教材</h4>
              <p>{{ classItem.book_title || '暂无关联教材' }}</p>
            </div>
            <div class="class-actions">
              <button class="btn btn-danger" @click="confirmLeaveClass(classItem.id, classItem.name)">
                <span class="icon">×</span> 退出班级
              </button>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 未分配班级 -->
      <div v-else-if="!error" class="no-class-card">
        <div class="no-class-icon">📚</div>
        <div class="no-class-message">
          <h3>您尚未加入任何班级</h3>
          <p>请使用上方的"加入新班级"按钮搜索并加入班级</p>
        </div>
      </div>
      
      <!-- 功能入口区域（始终显示） -->
      <div class="class-features">
        <h4>班级功能</h4>
        <div class="features-grid">
          <router-link to="/student/homeworks" class="feature-card">
            <div class="feature-icon">📝</div>
            <div class="feature-name">我的作业</div>
            <div class="feature-desc">查看和提交作业</div>
          </router-link>
          <router-link to="/student/resources" class="feature-card">
            <div class="feature-icon">📚</div>
            <div class="feature-name">学习资源</div>
            <div class="feature-desc">下载和查看学习资源</div>
          </router-link>
          <router-link to="/student/notices" class="feature-card">
            <div class="feature-icon">🔔</div>
            <div class="feature-name">通知消息</div>
            <div class="feature-desc">查看班级通知</div>
          </router-link>
        </div>
      </div>
    </div>
    
    <!-- 加入班级弹窗 -->
    <div v-if="showJoinClassModal" class="modal-overlay" @click="closeJoinClassModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>加入班级</h3>
          <button class="close-btn" @click="closeJoinClassModal">×</button>
        </div>
        <div class="modal-body">
          <!-- 课程码加入 -->
          <div class="join-by-code-section">
            <h4>通过课程码加入</h4>
            <div class="code-input-section">
              <input 
                type="text" 
                v-model="courseCode"
                placeholder="输入课程码..."
                class="code-input"
                maxlength="20"
              />
              <button 
                class="btn btn-primary code-join-btn" 
                @click="joinClassByCode"
                :disabled="joiningByCode"
              >
                <span v-if="joiningByCode">加入中...</span>
                <span v-else>加入</span>
              </button>
            </div>
            <div v-if="codeError" class="code-error">{{ codeError }}</div>
          </div>
          
          <!-- 分割线 -->
          <div class="divider">或</div>
          
          <!-- 搜索加入 -->
          <div class="search-section">
            <h4>搜索班级加入</h4>
            <div class="search-input-section">
              <input 
                type="text" 
                v-model="searchKeyword" 
                placeholder="输入班级名称或专业搜索班级..."
                @input="handleSearch"
                class="search-input"
              />
              <button class="btn btn-primary" @click="searchClasses">搜索</button>
            </div>
          </div>
          
          <div v-if="searchLoading" class="modal-loading">搜索中...</div>
          <div v-else-if="searchResults.length > 0" class="search-results">
            <h4>搜索结果</h4>
            <div class="search-results-list">
              <div 
                v-for="classItem in searchResults" 
                :key="classItem.id"
                class="search-result-item"
              >
                <div class="search-result-info">
                  <h5>{{ classItem.name }}</h5>
                  <p>{{ classItem.major }} - {{ classItem.teacher_name }}</p>
                  <p class="student-count">学生: {{ classItem.student_count }}</p>
                  <p class="course-code" v-if="classItem.course_code">
                    课程码: <span class="code">{{ classItem.course_code }}</span>
                  </p>
                </div>
                <button 
                  class="btn btn-primary join-btn" 
                  @click="joinSelectedClass(classItem.id)"
                  :disabled="joiningClassId === classItem.id"
                >
                  <span v-if="joiningClassId === classItem.id">加入中...</span>
                  <span v-else>加入</span>
                </button>
              </div>
            </div>
          </div>
          <div v-else-if="searchKeyword" class="no-results">
            <p>未找到匹配的班级</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { api } from '../api/api';

export default {
  name: 'StudentClassView',
  data() {
    return {
      classes: [],
      loading: true,
      error: null,
      showDetails: false,
      showJoinClassModal: false,
      searchKeyword: '',
      searchResults: [],
      searchLoading: false,
      joiningClassId: null,
      courseCode: '',
      joiningByCode: false,
      codeError: ''
    };
  },
  async mounted() {
    await this.fetchClassInfo();
  },
  methods: {
    async fetchClassInfo() {
      try {
        this.loading = true;
        const response = await api.getStudentClasses();
        
        // 处理响应
        if (Array.isArray(response)) {
          this.classes = response;
        } else {
          // 兼容旧的单班级响应格式
          this.classes = response ? [response] : [];
        }
        
        this.error = null;
      } catch (err) {
        // 提供更详细的错误提示
        console.error('获取班级信息失败:', err);
        if (err.response && err.response.data && err.response.data.error) {
          this.error = `获取班级信息失败: ${err.response.data.error}`;
        } else if (err.message) {
          this.error = `获取班级信息失败: ${err.message}`;
        } else {
          this.error = '获取班级信息失败，请检查网络连接或稍后重试';
        }
      } finally {
        this.loading = false;
      }
    },
    toggleDetails() {
      this.showDetails = !this.showDetails;
    },
    closeJoinClassModal() {
      this.showJoinClassModal = false;
      this.searchKeyword = '';
      this.searchResults = [];
      this.courseCode = '';
      this.codeError = '';
      this.joiningByCode = false;
    },
    handleSearch() {
      if (this.searchKeyword.trim()) {
        this.searchClasses();
      } else {
        this.searchResults = [];
      }
    },
    async searchClasses() {
      try {
        this.searchLoading = true;
        this.searchResults = await api.searchClasses(this.searchKeyword);
      } catch (err) {
        console.error('搜索班级失败:', err);
        this.searchResults = [];
        alert('搜索班级失败，请稍后重试');
      } finally {
        this.searchLoading = false;
      }
    },
    async joinSelectedClass(classId) {
      try {
        this.joiningClassId = classId;
        await api.joinClass(classId);
        alert('成功加入班级');
        this.closeJoinClassModal();
        await this.fetchClassInfo(); // 刷新班级列表
      } catch (err) {
        console.error('加入班级失败:', err);
        alert('加入班级失败，请稍后重试');
      } finally {
        this.joiningClassId = null;
      }
    },
    
    async joinClassByCode() {
      try {
        this.codeError = '';
        if (!this.courseCode.trim()) {
          this.codeError = '请输入课程码';
          return;
        }
        
        this.joiningByCode = true;
        await api.joinClassByCode(this.courseCode.trim());
        alert('成功通过课程码加入班级');
        this.closeJoinClassModal();
        await this.fetchClassInfo(); // 刷新班级列表
      } catch (err) {
        console.error('通过课程码加入班级失败:', err);
        this.codeError = err.message || '加入班级失败，请稍后重试';
      } finally {
        this.joiningByCode = false;
      }
    },
    
    async confirmLeaveClass(classId, className) {
      if (confirm(`确定要退出班级 "${className}" 吗？`)) {
        try {
          await api.leaveClass(classId);
          alert('成功退出班级');
          await this.fetchClassInfo(); // 刷新班级列表
        } catch (err) {
          console.error('退出班级失败:', err);
          alert(err.message || '退出班级失败，请稍后重试');
        }
      }
    }
  }
};
</script>

<style scoped>
.student-class-view {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

h2 {
  color: #333;
  margin: 0;
}

.loading {
  padding: 20px;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 20px;
  background-color: #e3f2fd;
  color: #1976d2;
}

.class-content-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Error Card Styles */
.error-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 20px;
  border-radius: 8px;
  background-color: #ffebee;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.error-icon {
  font-size: 48px;
  flex-shrink: 0;
}

.error-message {
  flex-grow: 1;
}

.error-message p {
  margin: 0 0 10px 0;
  color: #d32f2f;
  font-weight: bold;
}

.error-details {
  font-size: 14px;
  color: #9d2424;
  margin-top: 5px;
  word-break: break-word;
}

.error-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex-shrink: 0;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.btn-primary {
  background-color: #1976d2;
  color: white;
}

.btn-primary:hover {
  background-color: #1565c0;
}

.btn-secondary {
  background-color: #e0e0e0;
  color: #333;
}

.btn-secondary:hover {
  background-color: #bdbdbd;
}

/* Classes List Styles */
.classes-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* Class Card Styles */
.class-card {
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.class-header {
  margin-bottom: 20px;
}

.class-header h3 {
  margin: 0 0 10px 0;
  color: #333;
}

.class-meta {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

.class-meta span {
  background-color: #f5f5f5;
  padding: 5px 10px;
  border-radius: 15px;
  font-size: 14px;
  color: #666;
}

.student-count {
  background-color: #e3f2fd !important;
  color: #1976d2 !important;
}

.class-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.class-content h4 {
  margin: 0 0 10px 0;
  color: #555;
  font-size: 16px;
}

.class-content p {
  margin: 0;
  color: #666;
  line-height: 1.5;
}

/* Class Actions Styles */
.class-actions {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.btn-danger {
  background-color: #d32f2f;
  color: white;
}

.btn-danger:hover {
  background-color: #b71c1c;
}

/* No Class Card Styles */
.no-class-card {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 30px;
  border-radius: 8px;
  background-color: #fff3e0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  text-align: center;
}

.no-class-icon {
  font-size: 64px;
  flex-shrink: 0;
}

.no-class-message h3 {
  margin: 0 0 10px 0;
  color: #f57c00;
}

.no-class-message p {
  margin: 0;
  color: #f9a825;
}

/* Class Features Styles */
.class-features {
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.class-features h4 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 15px;
}

.feature-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  text-decoration: none;
  color: #333;
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.feature-name {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}

.feature-desc {
  text-align: center;
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #999;
}

.close-btn:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
}

.search-section {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-input {
  flex-grow: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.search-input:focus {
  outline: none;
  border-color: #1976d2;
}

.modal-loading {
  text-align: center;
  padding: 20px;
  color: #1976d2;
  font-weight: bold;
}

.search-results {
  margin-top: 20px;
}

.join-by-code-section {
  margin-bottom: 20px;
}

.join-by-code-section h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.code-input-section {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
}

.code-input {
  flex-grow: 1;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.code-join-btn {
  padding: 10px 20px;
}

.code-error {
  color: #d32f2f;
  font-size: 14px;
  margin-top: 5px;
}

.divider {
  text-align: center;
  margin: 20px 0;
  color: #999;
  position: relative;
}

.divider::before,
.divider::after {
  content: '';
  position: absolute;
  top: 50%;
  width: 40%;
  height: 1px;
  background-color: #eee;
}

.divider::before {
  left: 0;
}

.divider::after {
  right: 0;
}

.search-section h4 {
  margin: 0 0 10px 0;
  color: #333;
}

.search-input-section {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-results h4 {
  margin: 0 0 15px 0;
  color: #555;
}

.search-results-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.search-result-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 8px;
}

.search-result-info {
  flex-grow: 1;
}

.search-result-info h5 {
  margin: 0 0 5px 0;
  color: #333;
}

.search-result-info p {
  margin: 0 0 5px 0;
  color: #666;
  font-size: 14px;
}

.course-code {
  margin-top: 5px;
  font-weight: bold;
  color: #1976d2;
}

.course-code .code {
  background-color: #e3f2fd;
  padding: 2px 8px;
  border-radius: 4px;
  font-family: monospace;
  letter-spacing: 1px;
}

.join-btn {
  padding: 8px 16px;
}

.no-results {
  text-align: center;
  padding: 20px;
  color: #999;
  font-style: italic;
}
</style>
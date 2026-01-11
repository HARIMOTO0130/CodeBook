<template>
  <div class="course-design-page">
    <div class="page-header">
      <div class="header-left">
        <h1>课程设计</h1>
        <p>设计和管理您的教学课程内容</p>
      </div>
      <div class="header-right">
        <button class="btn btn-primary" @click="showCreateModal = true">
          <span>➕</span> 创建课程
        </button>
      </div>
    </div>

    <div class="filter-section">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input
          type="text"
          v-model="searchQuery"
          placeholder="搜索课程..."
        />
      </div>
      <div class="filter-options">
        <select v-model="filterStatus">
          <option value="all">全部状态</option>
          <option value="draft">草稿</option>
          <option value="published">已发布</option>
          <option value="archived">已归档</option>
        </select>
        <select v-model="sortBy">
          <option value="newest">最新创建</option>
          <option value="oldest">最早创建</option>
          <option value="name">按名称</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else class="courses-grid">
      <div
        v-for="course in filteredCourses"
        :key="course.id"
        class="course-card"
        @click="editCourse(course)"
      >
        <div class="course-header">
          <div class="course-icon" :style="{ background: course.color }">
            {{ (course.name || '课').charAt(0) }}
          </div>
          <div class="course-status" :class="course.status">
            {{ getStatusText(course.status) }}
          </div>
        </div>
        <div class="course-content">
          <h3>{{ course.name }}</h3>
          <p class="course-description">{{ course.description || '暂无描述' }}</p>
          <div class="course-meta">
            <span class="meta-item">
              <span>📚</span> {{ course.chapterCount || 0 }} 章节
            </span>
            <span class="meta-item">
              <span>📝</span> {{ course.lessonCount || 0 }} 课时
            </span>
            <span class="meta-item">
              <span>👥</span> {{ course.studentCount || 0 }} 学生
            </span>
          </div>
          <div class="course-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{ width: course.completionRate + '%' }"></div>
            </div>
            <span class="progress-text">完成度 {{ course.completionRate }}%</span>
          </div>
        </div>
        <div class="course-actions" @click.stop>
          <button class="action-btn" @click="editCourse(course)" title="编辑">
            ✏️
          </button>
          <button class="action-btn" @click="duplicateCourse(course)" title="复制">
            📋
          </button>
          <button class="action-btn delete" @click="deleteCourse(course)" title="删除">
            🗑️
          </button>
        </div>
      </div>

      <div v-if="filteredCourses.length === 0" class="empty-state">
        <div class="empty-icon">📚</div>
        <h3>暂无课程</h3>
        <p>点击"创建课程"开始设计您的教学内容</p>
      </div>
    </div>

    <!-- 创建/编辑课程模态框 -->
    <div v-if="showCreateModal || editingCourse" class="modal-overlay" @click.self="closeModal">
      <div class="modal course-modal">
        <div class="modal-header">
          <h2>{{ editingCourse ? '编辑课程' : '创建课程' }}</h2>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>课程名称 <span class="required">*</span></label>
            <input
              type="text"
              v-model="courseForm.name"
              placeholder="输入课程名称"
            />
          </div>
          <div class="form-group">
            <label>课程描述</label>
            <textarea
              v-model="courseForm.description"
              rows="4"
              placeholder="输入课程描述和教学目标..."
            ></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>课程类型</label>
              <select v-model="courseForm.type">
                <option value="programming">编程开发</option>
                <option value="algorithm">算法设计</option>
                <option value="database">数据库</option>
                <option value="web">Web开发</option>
                <option value="mobile">移动开发</option>
                <option value="other">其他</option>
              </select>
            </div>
            <div class="form-group">
              <label>难度等级</label>
              <select v-model="courseForm.difficulty">
                <option value="beginner">入门</option>
                <option value="intermediate">中级</option>
                <option value="advanced">高级</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>课程大纲</label>
            <div class="chapters-list">
              <div
                v-for="(chapter, index) in courseForm.chapters"
                :key="index"
                class="chapter-item"
              >
                <div class="chapter-header">
                  <input
                    type="text"
                    v-model="chapter.title"
                    placeholder="章节标题"
                    class="chapter-input"
                  />
                  <button class="btn-icon" @click="removeChapter(index)">🗑️</button>
                </div>
                <div class="lessons-list">
                  <div
                    v-for="(lesson, lessonIndex) in chapter.lessons"
                    :key="lessonIndex"
                    class="lesson-item"
                  >
                    <input
                      type="text"
                      v-model="lesson.title"
                      placeholder="课时标题"
                      class="lesson-input"
                    />
                    <input
                      type="number"
                      v-model.number="lesson.duration"
                      placeholder="时长(分钟)"
                      class="duration-input"
                    />
                    <button class="btn-icon" @click="removeLesson(index, lessonIndex)">×</button>
                  </div>
                  <button class="btn-add-lesson" @click="addLesson(index)">
                    + 添加课时
                  </button>
                </div>
              </div>
              <button class="btn-add-chapter" @click="addChapter">
                + 添加章节
              </button>
            </div>
          </div>
          <div class="form-group">
            <label>课程状态</label>
            <select v-model="courseForm.status">
              <option value="draft">草稿</option>
              <option value="published">已发布</option>
              <option value="archived">已归档</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="closeModal">取消</button>
          <button class="btn btn-primary" @click="saveCourse">
            {{ editingCourse ? '保存修改' : '创建课程' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'CourseDesignView',
  setup() {
    const loading = ref(false)
    const searchQuery = ref('')
    const filterStatus = ref('all')
    const sortBy = ref('newest')
    const showCreateModal = ref(false)
    const editingCourse = ref(null)

    const courses = ref([])

    const courseForm = ref({
      name: '',
      description: '',
      type: 'programming',
      difficulty: 'beginner',
      status: 'draft',
      chapters: []
    })

    const colors = [
      'linear-gradient(135deg, #667eea, #764ba2)',
      'linear-gradient(135deg, #f093fb, #f5576c)',
      'linear-gradient(135deg, #4facfe, #00f2fe)',
      'linear-gradient(135deg, #43e97b, #38f9d7)',
      'linear-gradient(135deg, #fa709a, #fee140)',
    ]

    const loadCourses = () => {
      // 模拟数据，实际应从API加载
      courses.value = [
        {
          id: 1,
          name: 'Python基础编程',
          description: '从零开始学习Python编程语言',
          type: 'programming',
          difficulty: 'beginner',
          status: 'published',
          chapterCount: 8,
          lessonCount: 32,
          studentCount: 45,
          completionRate: 75,
          color: colors[0],
          chapters: []
        },
        {
          id: 2,
          name: '数据结构与算法',
          description: '深入学习常用数据结构和算法',
          type: 'algorithm',
          difficulty: 'intermediate',
          status: 'published',
          chapterCount: 10,
          lessonCount: 40,
          studentCount: 38,
          completionRate: 60,
          color: colors[1],
          chapters: []
        },
        {
          id: 3,
          name: 'Web前端开发',
          description: 'HTML、CSS、JavaScript全栈开发',
          type: 'web',
          difficulty: 'beginner',
          status: 'draft',
          chapterCount: 6,
          lessonCount: 24,
          studentCount: 0,
          completionRate: 30,
          color: colors[2],
          chapters: []
        }
      ]
    }

    const filteredCourses = computed(() => {
      let result = [...courses.value]

      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        result = result.filter(c =>
          c.name.toLowerCase().includes(query) ||
          c.description.toLowerCase().includes(query)
        )
      }

      if (filterStatus.value !== 'all') {
        result = result.filter(c => c.status === filterStatus.value)
      }

      if (sortBy.value === 'newest') {
        result.sort((a, b) => b.id - a.id)
      } else if (sortBy.value === 'oldest') {
        result.sort((a, b) => a.id - b.id)
      } else if (sortBy.value === 'name') {
        result.sort((a, b) => a.name.localeCompare(b.name))
      }

      return result
    })

    const getStatusText = (status) => {
      const statusMap = {
        draft: '草稿',
        published: '已发布',
        archived: '已归档'
      }
      return statusMap[status] || status
    }

    const editCourse = (course) => {
      editingCourse.value = course
      courseForm.value = {
        name: course.name,
        description: course.description,
        type: course.type,
        difficulty: course.difficulty,
        status: course.status,
        chapters: course.chapters.length > 0 ? JSON.parse(JSON.stringify(course.chapters)) : []
      }
    }

    const duplicateCourse = (course) => {
      if (confirm(`确定要复制课程"${course.name}"吗？`)) {
        const newCourse = {
          ...course,
          id: Date.now(),
          name: course.name + ' (副本)',
          status: 'draft',
          studentCount: 0
        }
        courses.value.push(newCourse)
        alert('课程复制成功！')
      }
    }

    const deleteCourse = (course) => {
      if (confirm(`确定要删除课程"${course.name}"吗？此操作不可恢复。`)) {
        const index = courses.value.findIndex(c => c.id === course.id)
        if (index !== -1) {
          courses.value.splice(index, 1)
          alert('课程已删除')
        }
      }
    }

    const addChapter = () => {
      courseForm.value.chapters.push({
        title: '',
        lessons: []
      })
    }

    const removeChapter = (index) => {
      courseForm.value.chapters.splice(index, 1)
    }

    const addLesson = (chapterIndex) => {
      courseForm.value.chapters[chapterIndex].lessons.push({
        title: '',
        duration: 45
      })
    }

    const removeLesson = (chapterIndex, lessonIndex) => {
      courseForm.value.chapters[chapterIndex].lessons.splice(lessonIndex, 1)
    }

    const saveCourse = () => {
      if (!courseForm.value.name.trim()) {
        alert('请输入课程名称')
        return
      }

      if (editingCourse.value) {
        // 更新现有课程
        const index = courses.value.findIndex(c => c.id === editingCourse.value.id)
        if (index !== -1) {
          courses.value[index] = {
            ...courses.value[index],
            ...courseForm.value,
            chapterCount: courseForm.value.chapters.length,
            lessonCount: courseForm.value.chapters.reduce((sum, ch) => sum + ch.lessons.length, 0)
          }
        }
        alert('课程更新成功！')
      } else {
        // 创建新课程
        const newCourse = {
          id: Date.now(),
          ...courseForm.value,
          chapterCount: courseForm.value.chapters.length,
          lessonCount: courseForm.value.chapters.reduce((sum, ch) => sum + ch.lessons.length, 0),
          studentCount: 0,
          completionRate: 0,
          color: colors[courses.value.length % colors.length]
        }
        courses.value.push(newCourse)
        alert('课程创建成功！')
      }

      closeModal()
    }

    const closeModal = () => {
      showCreateModal.value = false
      editingCourse.value = null
      courseForm.value = {
        name: '',
        description: '',
        type: 'programming',
        difficulty: 'beginner',
        status: 'draft',
        chapters: []
      }
    }

    onMounted(() => {
      loadCourses()
    })

    return {
      loading,
      searchQuery,
      filterStatus,
      sortBy,
      showCreateModal,
      editingCourse,
      courses,
      courseForm,
      filteredCourses,
      getStatusText,
      editCourse,
      duplicateCourse,
      deleteCourse,
      addChapter,
      removeChapter,
      addLesson,
      removeLesson,
      saveCourse,
      closeModal
    }
  }
}
</script>

<style scoped>
.course-design-page {
  padding: 24px;
  background: #f8fafc;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-left h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.header-left p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 20px;
  border: none;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.btn-secondary {
  background: #e2e8f0;
  color: #475569;
}

.btn-secondary:hover {
  background: #cbd5e1;
}

.filter-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  gap: 16px;
}

.search-box {
  flex: 1;
  max-width: 400px;
  position: relative;
}

.search-box input {
  width: 100%;
  padding: 12px 16px 12px 42px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  transition: all 0.2s;
}

.search-box input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 16px;
}

.filter-options {
  display: flex;
  gap: 12px;
}

.filter-options select {
  padding: 10px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.loading-container {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  border: 4px solid #f3f4f6;
  border-top: 4px solid #667eea;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;
}

.course-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  position: relative;
}

.course-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.course-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
  font-weight: 700;
}

.course-status {
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.course-status.draft {
  background: #fef3c7;
  color: #d97706;
}

.course-status.published {
  background: #dcfce7;
  color: #16a34a;
}

.course-status.archived {
  background: #f3f4f6;
  color: #6b7280;
}

.course-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.course-description {
  font-size: 14px;
  color: #64748b;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.course-meta {
  display: flex;
  gap: 16px;
  margin-bottom: 16px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #64748b;
}

.course-progress {
  margin-bottom: 12px;
}

.progress-bar {
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 6px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea, #764ba2);
  border-radius: 3px;
  transition: width 0.3s;
}

.progress-text {
  font-size: 12px;
  color: #94a3b8;
}

.course-actions {
  display: flex;
  gap: 8px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}

.action-btn {
  flex: 1;
  padding: 8px;
  border: none;
  background: #f8fafc;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 16px;
}

.action-btn:hover {
  background: #f1f5f9;
}

.action-btn.delete:hover {
  background: #fee2e2;
}

.empty-state {
  grid-column: 1 / -1;
  text-align: center;
  padding: 80px 20px;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty-state h3 {
  font-size: 20px;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.empty-state p {
  color: #64748b;
  margin: 0;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow: hidden;
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px;
  border-bottom: 1px solid #f1f5f9;
}

.modal-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.close-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: #f1f5f9;
  border-radius: 10px;
  font-size: 24px;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #e2e8f0;
}

.modal-body {
  padding: 28px;
  max-height: calc(90vh - 160px);
  overflow-y: auto;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  margin-bottom: 8px;
}

.required {
  color: #ef4444;
}

.form-group input[type="text"],
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.form-group textarea {
  resize: vertical;
  font-family: inherit;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.chapters-list {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 16px;
  background: #f8fafc;
}

.chapter-item {
  background: white;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 12px;
}

.chapter-header {
  display: flex;
  gap: 12px;
  margin-bottom: 12px;
}

.chapter-input {
  flex: 1;
  padding: 10px 14px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
}

.btn-icon {
  width: 36px;
  height: 36px;
  border: none;
  background: #fee2e2;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: #fecaca;
}

.lessons-list {
  padding-left: 20px;
}

.lesson-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}

.lesson-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 13px;
}

.duration-input {
  width: 100px;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 13px;
}

.btn-add-lesson {
  width: 100%;
  padding: 8px;
  border: 1px dashed #cbd5e1;
  background: transparent;
  border-radius: 6px;
  color: #667eea;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 8px;
}

.btn-add-lesson:hover {
  background: #f8fafc;
  border-color: #667eea;
}

.btn-add-chapter {
  width: 100%;
  padding: 12px;
  border: 2px dashed #cbd5e1;
  background: transparent;
  border-radius: 10px;
  color: #667eea;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add-chapter:hover {
  background: white;
  border-color: #667eea;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 28px;
  border-top: 1px solid #f1f5f9;
  background: #f8fafc;
}
</style>

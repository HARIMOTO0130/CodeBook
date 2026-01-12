<template>
  <div class="assignment-create">
    <div class="back-header">
      <button class="btn-back" @click="$router.back()">
        ← 返回
      </button>
    </div>

    <div class="page-header">
      <h1>创建作业</h1>
    </div>

    <div v-if="loading" class="loading-container">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else class="form-container">
      <form @submit.prevent="submitAssignment" class="assignment-form">
        <!-- 基本信息 -->
        <div class="form-section">
          <h2>基本信息</h2>
          
          <div class="form-group">
            <label for="title">作业标题 <span class="required">*</span></label>
            <input
              id="title"
              v-model="formData.title"
              type="text"
              placeholder="请输入作业标题"
              required
              class="form-input"
            />
          </div>

          <div class="form-group">
            <label for="description">作业说明</label>
            <textarea
              id="description"
              v-model="formData.description"
              rows="5"
              placeholder="请输入作业说明和要求..."
              class="form-textarea"
            ></textarea>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="total_score">总分 <span class="required">*</span></label>
              <input
                id="total_score"
                v-model.number="formData.total_score"
                type="number"
                min="1"
                max="1000"
                placeholder="100"
                required
                class="form-input"
              />
            </div>

            <div class="form-group">
              <label for="due_date">截止时间 <span class="required">*</span></label>
              <input
                id="due_date"
                v-model="formData.due_date"
                type="datetime-local"
                required
                class="form-input"
              />
            </div>
          </div>
        </div>

        <!-- 分配班级 -->
        <div class="form-section">
          <h2>分配班级</h2>
          <div v-if="classes.length === 0" class="empty-state">
            <p>暂无班级，请先创建班级</p>
          </div>
          <div v-else class="classes-selection">
            <div
              v-for="classItem in classes"
              :key="classItem.id"
              class="class-checkbox-item"
            >
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  :value="classItem.id"
                  v-model="formData.classes"
                  class="checkbox-input"
                />
                <span class="checkbox-custom"></span>
                <div class="class-info">
                  <span class="class-name">{{ classItem.name }}</span>
                  <span class="class-meta">{{ classItem.student_count || 0 }} 名学生</span>
                </div>
              </label>
            </div>
          </div>
          <p v-if="formData.classes.length === 0" class="error-text">请至少选择一个班级</p>
        </div>

        <!-- 操作按钮 -->
        <div class="form-actions">
          <button type="button" class="btn btn-secondary" @click="$router.back()">
            取消
          </button>
          <button type="submit" class="btn btn-primary" :disabled="submitting || formData.classes.length === 0">
            <span v-if="submitting">创建中...</span>
            <span v-else>创建作业</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { assignmentApi } from '../api/assignment'
import { classApi } from '../api/class'

export default {
  name: 'AssignmentCreateView',
  setup() {
    const router = useRouter()
    const loading = ref(true)
    const submitting = ref(false)
    const classes = ref([])
    const formData = ref({
      title: '',
      description: '',
      total_score: 100,
      due_date: '',
      classes: []
    })

    const loadClasses = async () => {
      try {
        const response = await classApi.getClasses()
        let data = response.data
        if (Array.isArray(data)) {
          classes.value = data
        } else if (data && Array.isArray(data.results)) {
          classes.value = data.results
        } else if (data && Array.isArray(data.data)) {
          classes.value = data.data
        } else {
          classes.value = []
        }
      } catch (error) {
        console.error('加载班级失败:', error)
        alert('加载班级失败: ' + (error.response?.data?.error || error.message))
      } finally {
        loading.value = false
      }
    }

    const submitAssignment = async () => {
      if (!formData.value.title.trim()) {
        alert('请输入作业标题')
        return
      }

      if (formData.value.classes.length === 0) {
        alert('请至少选择一个班级')
        return
      }

      if (!formData.value.due_date) {
        alert('请选择截止时间')
        return
      }

      submitting.value = true
      try {
        // 格式化截止时间
        const dueDate = new Date(formData.value.due_date)
        const formattedDueDate = dueDate.toISOString()

        // 注意：后端目前只支持创建单个班级的作业，所以只使用第一个选中的班级
        const selectedClassId = formData.value.classes[0]
        
        // 验证班级是否被正确选择
        if (!selectedClassId) {
          alert('请选择一个班级')
          return
        }
        
        const data = {
          homework_name: formData.value.title,
          homework_content: formData.value.description || '',
          total_score: formData.value.total_score || 100,
          start_time: new Date().toISOString(),  // 当前时间作为开始时间
          end_time: formattedDueDate,
          class_obj: selectedClassId,
          // 暂时使用固定的chapter_id，实际应该添加章节选择功能
          chapter: 4  // 使用数据库中存在的第一个章节ID
        }

        console.log('创建作业请求数据:', data)
        console.log('选中的班级ID:', selectedClassId)
        console.log('班级列表:', classes.value)
        console.log('班级列表长度:', classes.value.length)
        console.log('第一个班级:', classes.value[0])

        await assignmentApi.createAssignment(data)
        alert('作业创建成功！')
        router.push('/teacher/assignments')
      } catch (error) {
        console.error('创建作业失败:', error)
        console.error('错误响应数据:', error.response?.data)
        console.error('请求配置:', error.config)
        alert('创建失败: ' + (error.response?.data?.error || error.response?.data?.non_field_errors?.[0] || error.message))
      } finally {
        submitting.value = false
      }
    }

    onMounted(() => {
      loadClasses()
      // 设置默认截止时间为明天
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      tomorrow.setHours(23, 59, 0, 0)
      formData.value.due_date = tomorrow.toISOString().slice(0, 16)
    })

    return {
      loading,
      submitting,
      classes,
      formData,
      submitAssignment
    }
  }
}
</script>

<style scoped>
.assignment-create {
  padding: 24px;
  max-width: 900px;
  margin: 0 auto;
  background: #f8fafc;
  min-height: 100vh;
}

.back-header {
  margin-bottom: 24px;
}

.btn-back {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  font-size: 14px;
  padding: 8px 0;
  transition: color 0.2s;
}

.btn-back:hover {
  color: #3b82f6;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 32px 0;
}

.loading-container {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  border: 4px solid #f3f4f6;
  border-top: 4px solid #3b82f6;
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

.form-container {
  background: white;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.form-section {
  margin-bottom: 32px;
}

.form-section h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #e2e8f0;
}

.form-group {
  margin-bottom: 20px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
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

.form-input,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
}

.form-textarea {
  resize: vertical;
  font-family: inherit;
}

.classes-selection {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.class-checkbox-item {
  border: 2px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s;
}

.class-checkbox-item:hover {
  border-color: #3b82f6;
  background: #f0f9ff;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  gap: 12px;
}

.checkbox-input {
  display: none;
}

.checkbox-custom {
  width: 20px;
  height: 20px;
  border: 2px solid #cbd5e1;
  border-radius: 4px;
  position: relative;
  transition: all 0.2s;
  flex-shrink: 0;
}

.checkbox-input:checked + .checkbox-custom {
  background: #3b82f6;
  border-color: #3b82f6;
}

.checkbox-input:checked + .checkbox-custom::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 14px;
  font-weight: bold;
}

.class-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.class-name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.class-meta {
  font-size: 14px;
  color: #64748b;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #64748b;
}

.error-text {
  color: #ef4444;
  font-size: 14px;
  margin-top: 8px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 24px;
  border-top: 2px solid #e2e8f0;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea, #764ba2);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
}

.btn-secondary:hover {
  background: #e5e7eb;
}
</style>

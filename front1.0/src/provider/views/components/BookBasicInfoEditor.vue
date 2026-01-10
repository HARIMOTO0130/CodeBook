<template>
  <div class="book-basic-info-editor">
    <form @submit.prevent="handleSubmit" class="info-editor-form">
      <!-- 封面上传与预览 -->
      <div class="form-section cover-section">
        <label class="form-label">封面图片</label>
        <div class="cover-upload-area">
          <div class="cover-preview" :style="{ backgroundColor: coverColor }">
            <img v-if="formData.cover && !coverFile" :src="formData.cover" alt="封面预览" class="cover-image">
            <img v-else-if="coverFile" :src="coverPreviewUrl" alt="封面预览" class="cover-image">
            <span v-else>{{ (formData.title || '书').charAt(0) }}</span>
          </div>
          <div class="cover-upload-controls">
            <input
              type="file"
              id="cover-upload"
              accept="image/*"
              class="cover-input"
              @change="handleCoverUpload"
            />
            <label for="cover-upload" class="btn btn-secondary btn-sm">选择封面</label>
            <button
              type="button"
              class="btn btn-danger btn-sm"
              @click="removeCover"
              v-if="formData.cover || coverFile"
            >
              删除封面
            </button>
          </div>
          <p class="form-help">支持JPG/PNG格式，最大2MB</p>
        </div>
      </div>

      <!-- 基本信息字段 -->
      <div class="form-section basic-fields">
        <!-- 标题 -->
        <div class="form-group">
          <label for="title" class="form-label required">标题</label>
          <input
            type="text"
            id="title"
            v-model="formData.title"
            class="form-input"
            placeholder="请输入书籍标题"
            :class="{ 'input-error': errors.title }"
          />
          <p v-if="errors.title" class="error-message">{{ errors.title }}</p>
        </div>

        <!-- 副标题 -->
        <div class="form-group">
          <label for="subtitle" class="form-label">副标题</label>
          <input
            type="text"
            id="subtitle"
            v-model="formData.subtitle"
            class="form-input"
            placeholder="请输入书籍副标题（可选）"
          />
        </div>

        <!-- 作者 -->
        <div class="form-group">
          <label for="author" class="form-label required">作者</label>
          <input
            type="text"
            id="author"
            v-model="formData.author"
            class="form-input"
            placeholder="请输入作者姓名"
            :class="{ 'input-error': errors.author }"
          />
          <p v-if="errors.author" class="error-message">{{ errors.author }}</p>
        </div>

        <!-- ISBN -->
        <div class="form-group">
          <label for="isbn" class="form-label">ISBN</label>
          <input
            type="text"
            id="isbn"
            v-model="formData.isbn"
            class="form-input"
            placeholder="请输入ISBN号（可选）"
          />
        </div>

        <!-- 语言 -->
        <div class="form-group">
          <label for="language" class="form-label">编程语言</label>
          <select
            id="language"
            v-model="formData.language"
            class="form-input"
          >
            <option value="">请选择编程语言</option>
            <option value="Python">Python</option>
            <option value="JavaScript">JavaScript</option>
            <option value="Java">Java</option>
            <option value="C++">C++</option>
            <option value="C#">C#</option>
            <option value="Go">Go</option>
            <option value="TypeScript">TypeScript</option>
            <option value="PHP">PHP</option>
            <option value="Ruby">Ruby</option>
            <option value="其他">其他</option>
          </select>
        </div>
      </div>

      <!-- 分类与标签 -->
      <div class="form-section category-tag-section">
        <!-- 分类 -->
        <div class="form-group">
          <label for="categories" class="form-label">分类</label>
          <div class="checkbox-group">
            <label 
              v-for="category in availableCategories" 
              :key="category.id"
              class="checkbox-label"
            >
              <input
                type="checkbox"
                :value="category.name"
                v-model="selectedCategories"
                class="checkbox-input"
              />
              <span class="checkbox-text">{{ category.name }}</span>
            </label>
          </div>
          <p class="form-help">可选择多个分类</p>
        </div>

        <!-- 标签 -->
        <div class="form-group">
          <label for="tags" class="form-label">标签</label>
          <div class="checkbox-group tags-group">
            <label 
              v-for="tag in availableTags" 
              :key="tag.id"
              class="checkbox-label tag-checkbox"
            >
              <input
                type="checkbox"
                :value="tag.name"
                v-model="selectedTags"
                class="checkbox-input"
              />
              <span class="checkbox-text">{{ tag.name }}</span>
            </label>
          </div>
          <p class="form-help">可选择多个标签</p>
        </div>
      </div>

      <!-- 描述与简介 -->
      <div class="form-section description-section">
        <!-- 描述 -->
        <div class="form-group">
          <label for="description" class="form-label">描述</label>
          <textarea
            id="description"
            v-model="formData.description"
            class="form-textarea"
            rows="3"
            placeholder="简要描述书籍内容"
          ></textarea>
        </div>

        <!-- 详细介绍 -->
        <div class="form-group">
          <label for="introduction" class="form-label">详细介绍</label>
          <div class="rich-text-editor">
            <!-- 简化版富文本编辑器 -->
            <div class="editor-toolbar">
              <button type="button" class="toolbar-btn" @click="formatText('bold')"><strong>B</strong></button>
              <button type="button" class="toolbar-btn" @click="formatText('italic')"><em>I</em></button>
              <button type="button" class="toolbar-btn" @click="formatText('underline')"><u>U</u></button>
              <button type="button" class="toolbar-btn" @click="insertLink">🔗</button>
            </div>
            <textarea
              id="introduction"
              v-model="formData.introduction"
              class="form-textarea rich-text-area"
              rows="8"
              placeholder="书籍的详细介绍（支持基本格式化）"
            ></textarea>
          </div>
        </div>
      </div>

      <!-- 表单操作按钮 -->
      <div class="form-actions">
        <button type="button" class="btn" @click="handleCancel">取消</button>
        <button type="submit" class="btn btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? '保存中...' : '保存修改' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { providerApi } from '../../api/index.js'

// 定义组件属性
const props = defineProps({
  bookData: {
    type: Object,
    required: true
  },
  isSubmitting: {
    type: Boolean,
    default: false
  }
})

// 定义事件
const emit = defineEmits(['submit', 'cancel'])

// 表单数据
const formData = ref({})

// 封面文件相关
const coverFile = ref(null)
const coverPreviewUrl = ref('')

// 表单验证错误
const errors = ref({})

// 分类和标签选项
const availableCategories = ref([])
const availableTags = ref([])
const selectedCategories = ref([])
const selectedTags = ref([])
const loadingCategories = ref(false)
const loadingTags = ref(false)

// 封面颜色
const coverColor = computed(() => {
  const colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0', '#FF5722']
  const id = formData.value.id || Math.random()
  return colors[Math.abs(id) % colors.length]
})

// 加载分类列表
const loadCategories = async () => {
  loadingCategories.value = true
  try {
    const data = await providerApi.listCategories()
    availableCategories.value = Array.isArray(data) ? data : (data?.results || [])
  } catch (e) {
    console.error('加载分类失败', e)
    availableCategories.value = []
  } finally {
    loadingCategories.value = false
  }
}

// 加载标签列表
const loadTags = async () => {
  loadingTags.value = true
  try {
    const data = await providerApi.listTags()
    availableTags.value = Array.isArray(data) ? data : (data?.results || [])
  } catch (e) {
    console.error('加载标签失败', e)
    availableTags.value = []
  } finally {
    loadingTags.value = false
  }
}

// 监听bookData变化，更新表单数据
watch(() => props.bookData, (newData) => {
  if (newData) {
    formData.value = {
      ...newData
    }
    
    // 处理分类选择
    if (Array.isArray(newData.categories)) {
      // 如果categories是对象数组，提取name
      selectedCategories.value = newData.categories.map(c => {
        if (typeof c === 'string') {
          return c
        } else if (c && typeof c === 'object') {
          return c.name || c
        }
        return ''
      }).filter(name => name)
    } else if (typeof newData.categories === 'string') {
      // 如果是逗号分隔的字符串
      selectedCategories.value = newData.categories.split(',').map(s => s.trim()).filter(s => s)
    } else {
      selectedCategories.value = []
    }
    
    // 确保选中的分类名称在可用分类列表中（防止名称不匹配）
    if (availableCategories.value.length > 0) {
      const validCategoryNames = availableCategories.value.map(c => c.name)
      selectedCategories.value = selectedCategories.value.filter(name => 
        validCategoryNames.includes(name)
      )
    }
    
    // 处理标签选择
    if (Array.isArray(newData.tag_list)) {
      selectedTags.value = newData.tag_list.map(t => typeof t === 'string' ? t : (t.name || t))
    } else if (typeof newData.tag_list === 'string') {
      selectedTags.value = newData.tag_list.split(',').map(s => s.trim()).filter(s => s)
    } else {
      selectedTags.value = []
    }
  }
}, { deep: true, immediate: true })

// 处理封面上传
const handleCoverUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    // 验证文件大小（最大2MB）
    if (file.size > 2 * 1024 * 1024) {
      alert('封面图片大小不能超过2MB')
      return
    }
    
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      alert('请选择有效的图片文件（JPG/PNG）')
      return
    }
    
    coverFile.value = file
    coverPreviewUrl.value = URL.createObjectURL(file)
  }
}

// 移除封面
const removeCover = () => {
  coverFile.value = null
  coverPreviewUrl.value = ''
  formData.value.cover = ''
}

// 处理表单提交
const handleSubmit = () => {
  // 表单验证
  if (!validateForm()) return
  
  // 准备提交数据
  const submitData = new FormData()
  
  // 添加基本字段
  submitData.append('title', formData.value.title)
  submitData.append('subtitle', formData.value.subtitle || '')
  submitData.append('author', formData.value.author)
  submitData.append('isbn', formData.value.isbn || '')
  submitData.append('language', formData.value.language || '')
  submitData.append('description', formData.value.description || '')
  submitData.append('introduction', formData.value.introduction || '')
  
  // 处理分类（使用选中的分类）
  if (selectedCategories.value && selectedCategories.value.length > 0) {
    selectedCategories.value.forEach(categoryName => {
      submitData.append('categories_write', categoryName)
    })
  }
  
  // 处理标签（使用选中的标签）
  if (selectedTags.value && selectedTags.value.length > 0) {
    // 发送旧版标签格式（作为JSON数组字符串）
    submitData.append('tag_list', JSON.stringify(selectedTags.value))
    // 同时发送新版标签格式（用于多对多关系）
    selectedTags.value.forEach(tagName => {
      submitData.append('tags_write', tagName)
    })
  }
  
  // 添加封面文件（如果有）
  if (coverFile.value) {
    submitData.append('cover', coverFile.value)
  }
  
  // 发送提交事件
  emit('submit', submitData)
}

// 表单验证
const validateForm = () => {
  errors.value = {}
  let isValid = true
  
  // 必填字段验证
  if (!formData.value.title || formData.value.title.trim() === '') {
    errors.value.title = '请输入书籍标题'
    isValid = false
  }
  
  if (!formData.value.author || formData.value.author.trim() === '') {
    errors.value.author = '请输入作者姓名'
    isValid = false
  }
  
  return isValid
}

// 处理取消操作
const handleCancel = () => {
  emit('cancel')
}

// 简化的富文本格式化功能
const formatText = (command) => {
  // 这里可以扩展为真正的富文本格式化
  // 目前仅做提示
  alert(`格式化功能：${command}（预留）`)
}

// 插入链接
const insertLink = () => {
  const url = prompt('请输入链接地址：')
  if (url) {
    formData.value.introduction += `[链接](${url})`
  }
}

// 组件挂载时加载分类和标签
onMounted(() => {
  loadCategories()
  loadTags()
})

// 暴露方法供父组件调用
defineExpose({
  submitForm: handleSubmit
})
</script>

<style scoped>
.book-basic-info-editor {
  max-width: 800px;
  margin: 0 auto;
}

.info-editor-form {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.form-section {
  background: #fafafa;
  padding: 20px;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
  font-size: 14px;
}

.form-label.required::after {
  content: ' *';
  color: #e74c3c;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  transition: border-color 0.3s;
}

.form-input:focus,
.form-textarea:focus {
  border-color: #2196f3;
  outline: none;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.input-error {
  border-color: #e74c3c;
}

.error-message {
  color: #e74c3c;
  font-size: 12px;
  margin-top: 4px;
}

.form-help {
  color: #666;
  font-size: 12px;
  margin: 5px 0 0 0;
}

/* 封面上传区域 */
.cover-section {
  text-align: center;
}

.cover-upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.cover-preview {
  width: 180px;
  height: 240px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 48px;
  font-weight: bold;
  overflow: hidden;
  border: 2px solid #ddd;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-upload-controls {
  display: flex;
  gap: 10px;
  align-items: center;
}

.cover-input {
  display: none;
}

/* 分类与标签区域 */
.category-tag-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: #fafafa;
}

.tags-group {
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  max-height: 150px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.checkbox-label:hover {
  background-color: #f0f0f0;
}

.tag-checkbox {
  display: inline-flex;
  margin-right: 8px;
  margin-bottom: 4px;
}

.checkbox-input {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.checkbox-text {
  font-size: 14px;
  color: #333;
  user-select: none;
}

/* 描述与简介区域 */
.rich-text-editor {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.editor-toolbar {
  display: flex;
  gap: 5px;
  background: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
  border: 1px solid #ddd;
}

.toolbar-btn {
  background: white;
  border: 1px solid #ddd;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.toolbar-btn:hover {
  background-color: #e9e9e9;
}

.rich-text-area {
  min-height: 120px;
  font-family: inherit;
}

/* 表单操作按钮 */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  padding: 20px 0;
  border-top: 1px solid #e0e0e0;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.btn-primary {
  background-color: #2196f3;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1976d2;
}

.btn-primary:disabled {
  background-color: #90caf9;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #e0e0e0;
  color: #333;
}

.btn-secondary:hover {
  background-color: #bdbdbd;
}

.btn-danger {
  background-color: #e74c3c;
  color: white;
}

.btn-danger:hover {
  background-color: #c0392b;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .category-tag-section {
    grid-template-columns: 1fr;
  }
  
  .cover-preview {
    width: 150px;
    height: 200px;
  }
  
  .cover-upload-controls {
    flex-direction: column;
  }
}
</style>
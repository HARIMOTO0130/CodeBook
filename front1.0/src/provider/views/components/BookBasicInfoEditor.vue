<template>
  <div class="book-basic-info-editor">
    <form @submit.prevent="handleSubmit" class="info-editor-form">
      <!-- 封面上传与预览 -->
      <div class="form-section cover-section">
        <label class="form-label">封面图片</label>
        <div class="cover-upload-area">
          <div class="cover-preview" :style="{ backgroundColor: coverColor }" role="img" aria-label="封面预览">
            <img v-if="formData.cover && !coverFile" :src="formData.cover" alt="封面预览" class="cover-image" aria-hidden="true">
            <img v-else-if="coverFile" :src="coverPreviewUrl" alt="封面预览" class="cover-image" aria-hidden="true">
            <span v-else>{{ (formData.title || '书').charAt(0) }}</span>
          </div>
          <div class="cover-upload-controls">
            <input
              type="file"
              id="cover-upload"
              accept="image/*"
              class="cover-input"
              @change="coverHandler.handleCoverUpload"
              aria-describedby="cover-upload-description"
            />
            <label for="cover-upload" class="btn btn-secondary btn-sm" tabIndex="0">选择封面</label>
            <button
              type="button"
              class="btn btn-danger btn-sm"
              @click="coverHandler.removeCover"
              v-if="formData.cover || coverFile"
              aria-label="删除当前封面"
              tabIndex="0"
            >
              删除封面
            </button>
          </div>
          <p id="cover-upload-description" class="form-help">支持JPG/PNG格式，最大2MB</p>
          
          <!-- 上传进度条 -->
          <div v-if="uploadProgress > 0" class="upload-progress-container">
            <div class="progress-bar">
              <div class="progress" :style="{ width: `${uploadProgress}%` }"></div>
            </div>
            <span class="progress-text">{{ uploadProgress }}%</span>
          </div>
          
          <!-- 上传错误提示 -->
          <p v-if="uploadError" class="error-message">
            <span class="error-icon">⚠️</span> {{ uploadError }}
          </p>
          
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
            :aria-invalid="!!errors.title"
            :aria-describedby="errors.title ? 'title-error' : undefined"
          />
          <p v-if="errors.title" id="title-error" class="error-message">{{ errors.title }}</p>
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
            :aria-invalid="!!errors.author"
            :aria-describedby="errors.author ? 'author-error' : undefined"
          />
          <p v-if="errors.author" id="author-error" class="error-message">{{ errors.author }}</p>
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
            :class="{ 'input-error': errors.isbn }"
            :aria-invalid="!!errors.isbn"
            :aria-describedby="errors.isbn ? 'isbn-error' : undefined"
          />
          <p v-if="errors.isbn" id="isbn-error" class="error-message">{{ errors.isbn }}</p>
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
          <div 
            class="checkbox-group"
            role="group"
            aria-labelledby="categories"
            aria-describedby="categories-help"
            @focus="loadCategoriesIfNeeded"
            @mouseenter="loadCategoriesIfNeeded"
          >
            <!-- 加载中状态 -->
            <div v-if="loadingCategories" class="loading-content" role="status">
              <div class="loading-spinner" aria-hidden="true"></div>
              <span>加载分类中...</span>
            </div>
            
            <!-- 无数据状态 -->
            <div v-else-if="availableCategories.length === 0" class="empty-content" role="status">
              <span>暂无分类数据</span>
            </div>
            
            <!-- 分类列表 -->
            <template v-else>
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
                  :id="`category-${category.id}`"
                  aria-label="选择分类: {{ category.name }}"
                />
                <span class="checkbox-text" :for="`category-${category.id}`">{{ category.name }}</span>
              </label>
            </template>
          </div>
          <p id="categories-help" class="form-help">可选择多个分类</p>
        </div>

        <!-- 标签 -->
        <div class="form-group">
          <label for="tags" class="form-label">标签</label>
          <div 
            class="checkbox-group tags-group"
            role="group"
            aria-labelledby="tags"
            aria-describedby="tags-help"
            @focus="loadTagsIfNeeded"
            @mouseenter="loadTagsIfNeeded"
          >
            <!-- 加载中状态 -->
            <div v-if="loadingTags" class="loading-content" role="status">
              <div class="loading-spinner" aria-hidden="true"></div>
              <span>加载标签中...</span>
            </div>
            
            <!-- 无数据状态 -->
            <div v-else-if="availableTags.length === 0" class="empty-content" role="status">
              <span>暂无标签数据</span>
            </div>
            
            <!-- 标签列表 -->
            <template v-else>
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
                  :id="`tag-${tag.id}`"
                  aria-label="选择标签: {{ tag.name }}"
                />
                <span class="checkbox-text" :for="`tag-${tag.id}`">{{ tag.name }}</span>
              </label>
            </template>
          </div>
          <p id="tags-help" class="form-help">可选择多个标签</p>
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
          <div class="jupyter-editor-wrapper">
            <JupyterNotebook 
              :initialContent="getJupyterContent()"
              :documentId="null"
              :isReadOnly="false"
              :language="codeLanguage"
              :bookId="bookId?.toString()"
              :chapterId="null"
              @contentChange="handleContentChange"
            ></JupyterNotebook>
          </div>
        </div>
      </div>

      <!-- 表单操作按钮 -->
      <div class="form-actions">
        <button type="button" class="btn" @click="handleCancel" aria-label="取消编辑并返回">取消</button>
        <button type="submit" class="btn btn-primary" :disabled="isSubmitting" :aria-busy="isSubmitting">
          <span v-if="isSubmitting" aria-hidden="true">
            <div class="loading-spinner" style="width: 16px; height: 16px; margin: 0 8px; display: inline-block;"></div>
            保存中...
          </span>
          <span v-else>保存修改</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { providerApi } from '../../api/index.js'
import JupyterNotebook from '../../../student/components/JupyterNotebook.vue'

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
const uploadProgress = ref(0)
const uploadError = ref('')

// 表单验证错误
const errors = ref({})

// 分类和标签选项
const availableCategories = ref([])
const availableTags = ref([])
const selectedCategories = ref([])
const selectedTags = ref([])
const loadingCategories = ref(false)
const loadingTags = ref(false)

// JupyterNotebook组件相关
const codeLanguage = ref('Python')
const bookId = computed(() => props.bookData.id)

// 获取Jupyter内容的辅助函数（与学生端保持一致）
const getJupyterContent = () => {
  console.log('🔄 getJupyterContent被调用');
  console.log('🔍 formData.value.chapters:', {
    exists: !!formData.value.chapters,
    type: typeof formData.value.chapters,
    length: Array.isArray(formData.value.chapters) ? formData.value.chapters.length : 0
  });
  
  // 首先检查是否有chapters字段（来自书籍章节）
  if (Array.isArray(formData.value.chapters) && formData.value.chapters.length > 0) {
    console.log('🔍 开始处理书籍章节内容');
    
    // 获取第一个章节的内容（可根据需求选择特定章节）
    const firstChapter = formData.value.chapters[0];
    console.log('📝 处理第一个章节:', firstChapter?.title);
    
    // 尝试获取章节的merged_content、content或jupyter_content
    let mergedContent = null;
    
    if (firstChapter?.merged_content) {
      mergedContent = firstChapter.merged_content;
      console.log('📊 使用章节的merged_content字段');
    } else if (firstChapter?.content) {
      mergedContent = firstChapter.content;
      console.log('📊 使用章节的content字段');
    } else if (firstChapter?.jupyter_content) {
      mergedContent = firstChapter.jupyter_content;
      console.log('📊 使用章节的jupyter_content字段');
    }
    
    if (mergedContent) {
      console.log('📊 mergedContent详情:', {
        type: typeof mergedContent,
        isObject: typeof mergedContent === 'object' && mergedContent !== null,
        isString: typeof mergedContent === 'string',
        hasCells: typeof mergedContent === 'object' && mergedContent !== null && mergedContent.cells
      });
      
      try {
        // 检查mergedContent的类型
        if (typeof mergedContent === 'object' && mergedContent !== null) {
          console.log('📊 content已经是对象格式');
          
          // 检查是否是有效的Jupyter Notebook格式
          if (mergedContent.cells && Array.isArray(mergedContent.cells)) {
            console.log('✅ 成功识别为Jupyter Notebook格式，包含', mergedContent.cells.length, '个单元格');
            
            // 转换为JupyterNotebook组件期望的单元格数组格式
            const cellsArray = mergedContent.cells.map((cell, index) => ({
              id: `cell_${index}_${Date.now()}`,
              type: cell.cell_type === 'code' ? 'code' : 'markdown',
              content: Array.isArray(cell.source) ? cell.source.join('\n') : cell.source || '',
              language: mergedContent.metadata?.kernelspec?.language || firstChapter?.language || codeLanguage.value || 'python',
              output: cell.outputs?.map(output => {
                if (output.text) return Array.isArray(output.text) ? output.text.join('') : output.text;
                if (output.data?.['text/plain']) return output.data['text/plain'];
                return JSON.stringify(output);
              }) || [],
              isSystemGenerated: true
            }));
            
            console.log('✅ 转换为组件兼容格式完成');
            return JSON.stringify(cellsArray);
          } else if (Array.isArray(mergedContent)) {
            // 如果mergedContent直接是cells数组
            console.log('📊 content是cells数组格式，包含', mergedContent.length, '个单元格');
            
            const cellsArray = mergedContent.map((cell, index) => ({
              id: `cell_${index}_${Date.now()}`,
              type: cell.cell_type === 'code' ? 'code' : 'markdown',
              content: Array.isArray(cell.source) ? cell.source.join('\n') : cell.source || '',
              language: firstChapter?.language || codeLanguage.value || 'python',
              output: cell.outputs?.map(output => {
                if (output.text) return Array.isArray(output.text) ? output.text.join('') : output.text;
                if (output.data?.['text/plain']) return output.data['text/plain'];
                return JSON.stringify(output);
              }) || [],
              isSystemGenerated: true
            }));
            
            console.log('✅ 转换为组件兼容格式完成');
            return JSON.stringify(cellsArray);
          } else {
            // 如果是普通对象，将其转换为Markdown单元格
            console.log('📊 content是普通对象，转换为Markdown单元格');
            const cellsArray = [{
              id: `cell_0_${Date.now()}`,
              type: 'markdown',
              content: JSON.stringify(mergedContent, null, 2),
              language: firstChapter?.language || codeLanguage.value || 'python',
              output: [],
              isSystemGenerated: true
            }];
            return JSON.stringify(cellsArray);
          }
        }
        
        // 如果mergedContent是字符串，尝试解析它
        if (typeof mergedContent === 'string' && mergedContent.trim()) {
          console.log('📊 content是字符串格式，尝试解析');
          try {
            const parsed = JSON.parse(mergedContent);
            
            if (parsed.cells && Array.isArray(parsed.cells)) {
              console.log('✅ 成功解析为Jupyter Notebook格式，包含', parsed.cells.length, '个单元格');
              
              const cellsArray = parsed.cells.map((cell, index) => ({
                id: `cell_${index}_${Date.now()}`,
                type: cell.cell_type === 'code' ? 'code' : 'markdown',
                content: Array.isArray(cell.source) ? cell.source.join('\n') : cell.source || '',
                language: parsed.metadata?.kernelspec?.language || firstChapter?.language || codeLanguage.value || 'python',
                output: cell.outputs?.map(output => {
                  if (output.text) return Array.isArray(output.text) ? output.text.join('') : output.text;
                  if (output.data?.['text/plain']) return output.data['text/plain'];
                  return JSON.stringify(output);
                }) || [],
                isSystemGenerated: true
              }));
              
              console.log('✅ 转换为组件兼容格式完成');
              return JSON.stringify(cellsArray);
            } else if (Array.isArray(parsed)) {
              // 如果解析后直接是cells数组
              console.log('📊 解析后是cells数组格式，包含', parsed.length, '个单元格');
              
              const cellsArray = parsed.map((cell, index) => ({
                id: `cell_${index}_${Date.now()}`,
                type: cell.cell_type === 'code' ? 'code' : 'markdown',
                content: Array.isArray(cell.source) ? cell.source.join('\n') : cell.source || '',
                language: firstChapter?.language || codeLanguage.value || 'python',
                output: cell.outputs?.map(output => {
                  if (output.text) return Array.isArray(output.text) ? output.text.join('') : output.text;
                  if (output.data?.['text/plain']) return output.data['text/plain'];
                  return JSON.stringify(output);
                }) || [],
                isSystemGenerated: true
              }));
              
              console.log('✅ 转换为组件兼容格式完成');
              return JSON.stringify(cellsArray);
            } else {
              // 如果是普通对象，将其转换为Markdown单元格
              console.log('📊 解析后是普通对象，转换为Markdown单元格');
              const cellsArray = [{
                id: `cell_0_${Date.now()}`,
                type: 'markdown',
                content: JSON.stringify(parsed, null, 2),
                language: firstChapter?.language || codeLanguage.value || 'python',
                output: [],
                isSystemGenerated: true
              }];
              return JSON.stringify(cellsArray);
            }
          } catch (e) {
            // 如果解析失败，将字符串作为普通Markdown内容
            console.log(`⚠️ JSON解析失败，将内容作为普通Markdown处理: ${e.message}`);
            const cellsArray = [{
              id: `cell_0_${Date.now()}`,
              type: 'markdown',
              content: mergedContent,
              language: firstChapter?.language || codeLanguage.value || 'python',
              output: [],
              isSystemGenerated: true
            }];
            return JSON.stringify(cellsArray);
          }
        }
      } catch (e) {
        console.log(`⚠️ content处理失败: ${e.message}`);
        // 创建默认内容
        const defaultContent = [{
          id: `cell_0_${Date.now()}`,
          type: 'markdown',
          content: '# 欢迎使用交互式文档\n\n这是一个默认的Markdown单元格。',
          language: firstChapter?.language || codeLanguage.value || 'python',
          output: [],
          isSystemGenerated: true
        }];
        return JSON.stringify(defaultContent);
      }
    }
  }
  
  console.log('❌ 没有找到有效的Jupyter内容，创建默认内容');
  // 创建默认内容
  const defaultContent = [{
    id: `cell_0_${Date.now()}`,
    type: 'markdown',
    content: '# 欢迎使用交互式文档\n\n这是一个默认的Markdown单元格。',
    language: codeLanguage.value || 'python',
    output: [],
    isSystemGenerated: true
  }];
  return JSON.stringify(defaultContent);
}

// 处理内容变化
const handleContentChange = (content) => {
  // 更新表单数据 - content已经是Markdown字符串，不需要再JSON.stringify
  formData.value.introduction = content;
}

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

// 延迟加载分类（只在需要时加载）
const loadCategoriesIfNeeded = () => {
  if (!loadingCategories.value && availableCategories.value.length === 0) {
    loadCategories()
  }
}

// 延迟加载标签（只在需要时加载）
const loadTagsIfNeeded = () => {
  if (!loadingTags.value && availableTags.value.length === 0) {
    loadTags()
  }
}

// 监听bookData变化，更新表单数据
watch(() => props.bookData, (newData) => {
  if (newData) {
    console.log('📚 接收到新的bookData:', {
      hasIntroduction: !!newData.introduction,
      introductionType: typeof newData.introduction,
      introductionLength: newData.introduction?.length || 0,
      introductionPreview: newData.introduction?.substring(0, 100) + '...' || 'null'
    });
    
    formData.value = {
      ...newData
    }
    
    console.log('📝 表单数据更新后:', {
      hasIntroduction: !!formData.value.introduction,
      introductionType: typeof formData.value.introduction,
      introductionLength: formData.value.introduction?.length || 0
    });
    
    // Jupyter内容现在直接通过formData.value.introduction与组件交互
    
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

// 封面处理模块
const coverHandler = {
  // 压缩图片
  compressImage: (file, maxWidth = 800, maxHeight = 1200, quality = 0.8) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      
      reader.onload = (e) => {
        const img = new Image()
        
        img.onload = () => {
          // 计算缩放比例
          let width = img.width
          let height = img.height
          
          if (width > maxWidth || height > maxHeight) {
            const ratio = Math.min(maxWidth / width, maxHeight / height)
            width *= ratio
            height *= ratio
          }
          
          // 创建canvas并绘制压缩后的图片
          const canvas = document.createElement('canvas')
          canvas.width = width
          canvas.height = height
          
          const ctx = canvas.getContext('2d')
          ctx.drawImage(img, 0, 0, width, height)
          
          // 将canvas转换为Blob
          canvas.toBlob(
            (blob) => {
              if (blob) {
                // 创建新的文件对象
                const compressedFile = new File(
                  [blob],
                  file.name,
                  { type: file.type, lastModified: Date.now() }
                )
                resolve(compressedFile)
              } else {
                reject(new Error('图片压缩失败'))
              }
            },
            file.type,
            quality
          )
        }
        
        img.onerror = () => {
          reject(new Error('图片加载失败'))
        }
        
        img.src = e.target.result
      }
      
      reader.onerror = () => {
        reject(new Error('文件读取失败'))
      }
      
      reader.readAsDataURL(file)
    })
  },
  
  // 处理封面上传
  handleCoverUpload: async (event) => {
    const file = event.target.files[0]
    if (!file) return
    
    uploadError.value = ''
    
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
      uploadError.value = '请选择有效的图片文件（JPG/PNG）'
      return
    }
    
    // 开始上传进度模拟
    uploadProgress.value = 0
    const progressInterval = setInterval(() => {
      uploadProgress.value += 10
      if (uploadProgress.value >= 100) {
        clearInterval(progressInterval)
        uploadProgress.value = 0
      }
    }, 100)
    
    try {
      // 压缩图片
      const compressedFile = await coverHandler.compressImage(file)
      
      // 验证压缩后的文件大小（最大2MB）
      if (compressedFile.size > 2 * 1024 * 1024) {
        throw new Error('图片大小超过2MB，请选择更小的图片')
      }
      
      // 使用object URL创建预览，更高效
      if (coverPreviewUrl.value) {
        URL.revokeObjectURL(coverPreviewUrl.value)
      }
      
      coverPreviewUrl.value = URL.createObjectURL(compressedFile)
      coverFile.value = compressedFile
      
      clearInterval(progressInterval)
      uploadProgress.value = 0
    } catch (error) {
      uploadError.value = error.message || '图片处理失败，请重试'
      clearInterval(progressInterval)
      uploadProgress.value = 0
    }
  },
  
  // 移除封面
  removeCover: () => {
    // 释放object URL，避免内存泄漏
    if (coverPreviewUrl.value) {
      URL.revokeObjectURL(coverPreviewUrl.value)
    }
    
    coverFile.value = null
    coverPreviewUrl.value = ''
    formData.value.cover = ''
    uploadProgress.value = 0
    uploadError.value = ''
  }
}

// 表单验证逻辑
const formValidation = {
  // 验证单个字段
  validateField: (field, value) => {
    if (!errors.value) errors.value = {}
    
    switch (field) {
      case 'title':
        if (!value || value.trim() === '') {
          errors.value.title = '请输入书籍标题'
        } else if (value.length > 200) {
          errors.value.title = '标题不能超过200个字符'
        } else {
          delete errors.value.title
        }
        break
      case 'author':
        if (!value || value.trim() === '') {
          errors.value.author = '请输入作者姓名'
        } else if (value.length > 100) {
          errors.value.author = '作者姓名不能超过100个字符'
        } else {
          delete errors.value.author
        }
        break
      case 'isbn':
        if (value && value.length > 20) {
          errors.value.isbn = 'ISBN号不能超过20个字符'
        } else {
          delete errors.value.isbn
        }
        break
    }
  },
  
  // 完整表单验证
  validateForm: () => {
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
}

// 监听表单字段变化，实时验证
watch(() => formData.value.title, (newVal) => {
  formValidation.validateField('title', newVal)
})

watch(() => formData.value.author, (newVal) => {
  formValidation.validateField('author', newVal)
})

watch(() => formData.value.isbn, (newVal) => {
  formValidation.validateField('isbn', newVal)
})

// 处理表单提交
const handleSubmit = () => {
  // 表单验证
  if (!formValidation.validateForm()) return
  
  // 如果当前在Jupyter编辑模式，保存编辑器内容
  if (isJupyterEditing.value) {
    if (editorInstance.value) {
      jupyterContent.value = editorInstance.value.getValue()
    }
    // 将Jupyter内容保存到introduction字段
    formData.value.introduction = jupyterContent.value
  }
  
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

// 处理取消操作
const handleCancel = () => {
  emit('cancel')
}



// 组件挂载时不自动加载分类和标签，改为按需加载
onMounted(() => {
  // 分类和标签现在在用户与相应区域交互时才加载
})

// 组件卸载时的清理工作
onUnmounted(() => {
  // 清理工作已在JupyterNotebook组件内部处理
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

/* 上传进度条 */
.upload-progress-container {
  width: 100%;
  margin-top: 15px;
  display: flex;
  align-items: center;
  gap: 10px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background-color: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
}

.progress {
  height: 100%;
  background-color: #2196f3;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 12px;
  color: #666;
  min-width: 40px;
  text-align: right;
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

/* 加载中状态 */
.loading-content {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  color: #666;
}

.loading-content .loading-spinner {
  width: 20px;
  height: 20px;
  margin-bottom: 0;
}

/* 空数据状态 */
.empty-content {
  padding: 10px;
  color: #999;
  text-align: center;
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

/* Jupyter编辑器包装器（合并了rich-text-editor和jupyter-container的样式） */
.jupyter-editor-wrapper {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 20px 0;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.jupyter-editor-wrapper :deep(.jupyter-notebook) {
  min-height: 400px;
  width: 100%;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .jupyter-editor-wrapper {
    margin: 15px 0;
    border-radius: 6px;
  }
  
  .jupyter-editor-wrapper :deep(.jupyter-notebook) {
    min-height: 300px;
  }
}

/* 保留原有jupyter-container样式以确保兼容性 */
.jupyter-container {
  margin: 20px 0;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.jupyter-container :deep(.jupyter-notebook) {
  min-height: 400px;
  width: 100%;
}

@media (max-width: 768px) {
  .jupyter-container {
    margin: 15px 0;
    border-radius: 6px;
  }
  
  .jupyter-container :deep(.jupyter-notebook) {
    min-height: 300px;
  }
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

/* Jupyter编辑器样式 */
.jupyter-editor-container {
  position: relative;
}

.editor-notice {
  background-color: #fff3cd;
  border: 1px solid #ffeaa7;
  border-radius: 4px;
  padding: 10px 15px;
  margin-bottom: 15px;
  color: #856404;
}

.jupyter-editor {
  width: 100%;
  height: 100%;
  min-height: 300px;
  max-height: 800px;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  background-color: #fafafa;
  overflow: auto;
}

/* 编辑器加载状态 */
.editor-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  max-height: 800px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #fafafa;
  color: #666;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid rgba(33, 150, 243, 0.2);
  border-left-color: #2196f3;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 15px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .book-basic-info-editor {
    padding: 0 15px;
  }
}

@media (max-width: 768px) {
  .book-basic-info-editor {
    padding: 0 10px;
  }
  
  .form-section {
    padding: 15px;
  }
  
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
  
  /* 优化编辑器工具栏 */
  .editor-toolbar {
    flex-wrap: wrap;
  }
  
  /* 优化按钮大小和间距 */
  .toolbar-btn {
    padding: 4px 8px;
    font-size: 12px;
  }
  
  /* 优化表单操作按钮 */
  .form-actions {
    flex-direction: column-reverse;
  }
  
  .form-actions .btn {
    width: 100%;
  }
  
  /* 优化Jupyter编辑器在移动设备上的显示 */
  .jupyter-editor {
    min-height: 200px;
    max-height: 500px;
  }
  
  .editor-loading {
    min-height: 200px;
    max-height: 500px;
  }
  
  /* 优化文本区域大小 */
  .form-textarea {
    min-height: 60px;
  }
  
  .rich-text-area {
    min-height: 100px;
  }
}

@media (max-width: 480px) {
  .book-basic-info-editor {
    padding: 0 5px;
  }
  
  .form-section {
    padding: 12px;
  }
  
  .cover-preview {
    width: 120px;
    height: 160px;
  }
  
  /* 优化分类和标签选择区域 */
  .checkbox-group {
    max-height: 150px;
  }
  
  .tags-group {
    max-height: 120px;
  }
  
  /* 优化表单标签和输入框间距 */
  .form-label {
    font-size: 13px;
  }
  
  .form-input, 
  .form-textarea {
    padding: 8px 10px;
    font-size: 14px;
  }
}
</style>
<template>
  <ProviderLayout>
    <div class="provider-categories">
      <div class="layout">
        <!-- 左侧：分类管理 -->
        <div class="panel">
          <div class="panel-header">
            <h3>分类管理</h3>
            <div class="header-right">
              <select class="select" v-model="selectedCategory" @change="onCategoryChange">
                <option disabled value="">请选择分类...</option>
                <option v-for="(cat, index) in categories" :key="cat?.id || index" :value="cat?.id || index">
                  {{ cat?.name || '未知' }}
                </option>
              </select>
              <button class="btn btn-primary" @click="openCategoryDialog">＋ 新建分类</button>
            </div>
          </div>

          <div v-if="loadingCategories" class="empty-tip">正在加载分类...</div>
          <div v-else-if="categories.length === 0" class="empty-tip">暂无分类。</div>

          <div v-else-if="selectedCategory" class="category-details">
            <div class="category-info">
              <p><strong>分类名称：</strong>{{ getCategoryById(selectedCategory)?.name || '未知' }}</p>
              <p><strong>标识：</strong>{{ getCategoryById(selectedCategory)?.slug || 'N/A' }}</p>
              <p v-if="getCategoryById(selectedCategory)?.parent"><strong>父级分类：</strong>{{ getCategoryName(getCategoryById(selectedCategory)?.parent) }}</p>
            </div>
          </div>
        </div>

        <!-- 右侧：标签管理 -->
        <div class="panel">
          <div class="panel-header">
            <h3>标签管理</h3>
            <button class="btn btn-primary" @click="openTagDialog">＋ 新建标签</button>
          </div>

          <div v-if="loadingTags" class="empty-tip">正在加载标签...</div>
          <div v-else-if="tags.length === 0" class="empty-tip">暂无标签。</div>

          <div class="tag-list">
            <span 
              v-for="(tag, index) in tags" 
              :key="tag?.id || index" 
              class="tag-chip"
              :class="{ 'active': selectedTag === (tag?.id || index) }"
              @click="selectTag(tag?.id || index, tag?.name || '未知')"
              style="cursor: pointer;"
            >
              {{ tag?.name || '未知' }}
            </span>
          </div>
        </div>
      </div>

      <!-- 顶部：四个主要分类展示 -->
      <div class="main-categories-section">
        <h2 class="section-title">主要分类</h2>
        <div class="main-categories-grid">
          <div 
            v-for="mainCat in mainCategories" 
            :key="mainCat.slug"
            class="main-category-card"
            :class="{ 'active': selectedMainCategory === mainCat.slug }"
            @click="selectMainCategory(mainCat.slug)"
          >
            <div class="category-icon">{{ mainCat.icon }}</div>
            <div class="category-title">{{ mainCat.name }}</div>
            <div class="category-desc">{{ mainCat.description }}</div>
            <div class="category-count" v-if="mainCat.bookCount > 0">
              {{ mainCat.bookCount }} 本书
            </div>
          </div>
        </div>
      </div>

      <!-- 书籍列表区域 -->
      <div v-if="showBooksList" class="books-list-section">
        <div class="books-list-header">
          <h2 class="section-title">{{ currentCategoryName }}</h2>
          <button class="btn" @click="closeBooksList">关闭</button>
        </div>
        <div v-if="loadingBooks || loadingTagBooks" class="empty-tip">正在加载书籍...</div>
        <div v-else-if="books.length === 0 && tagBooks.length === 0" class="empty-tip">该分类或标签下暂无书籍。</div>
        <div v-else class="books-grid">
          <div 
            v-for="book in selectedTag ? tagBooks : books" 
            :key="book.id"
            class="book-card"
            @click="goToBookDetail(book.id)"
          >
            <div class="book-cover" :style="{ backgroundColor: book.cover_color || '#4CAF50' }">
              <span v-if="!book.cover">{{ book.title?.charAt(0) || '书' }}</span>
              <img v-else :src="book.cover" :alt="book.title" />
            </div>
            <div class="book-info">
              <h3 class="book-title">{{ book.title }}</h3>
              <p class="book-author">{{ book.author }}</p>
              <div class="book-meta">
                <span v-if="book.total_chapters" class="meta-item">{{ book.total_chapters }} 章</span>
                <span v-if="book.current_version" class="meta-item">v{{ book.current_version }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 分类弹窗 -->
      <div v-if="showCategoryDialog" class="modal-overlay" @click.self="showCategoryDialog = false">
        <div class="modal">
          <div class="modal-header">
            <h3>新建分类</h3>
            <button class="close-btn" @click="showCategoryDialog = false">×</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">名称</label>
              <input v-model="categoryForm.name" type="text" class="input" placeholder="例如：计算机基础" />
            </div>
            <div class="form-group">
              <label class="form-label">标识 (slug)</label>
              <input v-model="categoryForm.slug" type="text" class="input" placeholder="例如：cs-basic" />
            </div>
            <div class="form-group">
              <label class="form-label">描述</label>
              <textarea v-model="categoryForm.description" class="input" rows="3" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn" @click="showCategoryDialog = false">取消</button>
            <button class="btn btn-primary" @click="submitCategory">保存</button>
          </div>
        </div>
      </div>

      <!-- 标签弹窗 -->
      <div v-if="showTagDialog" class="modal-overlay" @click.self="showTagDialog = false">
        <div class="modal">
          <div class="modal-header">
            <h3>新建标签</h3>
            <button class="close-btn" @click="showTagDialog = false">×</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">名称</label>
              <input v-model="tagForm.name" type="text" class="input" placeholder="例如：Python 入门" />
            </div>
            <div class="form-group">
              <label class="form-label">描述</label>
              <textarea v-model="tagForm.description" class="input" rows="3" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn" @click="showTagDialog = false">取消</button>
            <button class="btn btn-primary" @click="submitTag">保存</button>
          </div>
        </div>
      </div>
    </div>
  </ProviderLayout>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ProviderLayout from './ProviderLayout.vue'
import { providerApi } from '../api/index.js'

const router = useRouter()

const categories = ref([])
const tags = ref([])
const loadingCategories = ref(false)
const loadingTags = ref(false)

const showCategoryDialog = ref(false)
const showTagDialog = ref(false)
const selectedMainCategory = ref('')
const selectedCategory = ref('')
const selectedTag = ref('')
const tagBooks = ref([])
const loadingTagBooks = ref(false)

// 四个主要分类
const mainCategories = ref([
  {
    name: '经管',
    slug: 'economics-management',
    icon: '💰',
    description: '经济学与管理学相关教材',
    bookCount: 0
  },
  {
    name: '艺术',
    slug: 'arts',
    icon: '🎨',
    description: '艺术类教材',
    bookCount: 0
  },
  {
    name: '文史',
    slug: 'literature-history',
    icon: '📚',
    description: '文学与历史类教材',
    bookCount: 0
  },
  {
    name: '理工',
    slug: 'science-engineering',
    icon: '🔬',
    description: '理工科教材',
    bookCount: 0
  }
])

// 书籍列表相关
const books = ref([])
const loadingBooks = ref(false)
const showBooksList = ref(false)
const currentCategoryName = ref('')

// 选择主要分类
const selectMainCategory = async (slug) => {
  if (selectedMainCategory.value === slug) {
    // 如果已经选中，则取消选中
    selectedMainCategory.value = ''
    showBooksList.value = false
    books.value = []
  } else {
    selectedMainCategory.value = slug
    selectedTag.value = ''
    const mainCat = mainCategories.value.find(c => c.slug === slug)
    if (mainCat) {
      currentCategoryName.value = mainCat.name
      await loadBooksByCategory(slug)
    }
  }
}

// 根据分类加载书籍
const loadBooksByCategory = async (categorySlug) => {
  loadingBooks.value = true
  showBooksList.value = true
  try {
    // 先找到分类ID
    const category = categories.value.find(c => c.slug === categorySlug)
    if (!category) {
      books.value = []
      return
    }
    
    // 加载该分类下的书籍 - 使用分类名称过滤
    const data = await providerApi.listBooks({ categories: category.name })
    books.value = Array.isArray(data) ? data : (data?.results || [])
  } catch (e) {
    console.error('加载书籍失败', e)
    books.value = []
  } finally {
    loadingBooks.value = false
  }
}

// 跳转到书籍详情页
const goToBookDetail = (bookId) => {
  router.push({ name: 'ProviderBookDetail', params: { id: bookId } })
}

const closeBooksList = () => {
  showBooksList.value = false
  selectedMainCategory.value = ''
  selectedTag.value = ''
  tagBooks.value = []
  currentCategoryName.value = ''
}

const categoryForm = ref({
  name: '',
  slug: '',
  description: '',
})

const tagForm = ref({
  name: '',
  description: '',
})

const loadCategories = async () => {
  loadingCategories.value = true
  try {
    const data = await providerApi.listCategories()
    categories.value = Array.isArray(data) ? data : (data?.results || [])
    
    // 更新主要分类的书籍数量
    mainCategories.value.forEach(mainCat => {
      const cat = categories.value.find(c => c.slug === mainCat.slug)
      if (cat) {
        mainCat.bookCount = cat.book_count || 0
      }
    })
  } catch (e) {
    console.error('加载分类失败', e)
    categories.value = []
  } finally {
    loadingCategories.value = false
  }
}

const loadTags = async () => {
  loadingTags.value = true
  try {
    const data = await providerApi.listTags()
    tags.value = Array.isArray(data) ? data : (data?.results || [])
  } catch (e) {
    console.error('加载标签失败', e)
    tags.value = []
  } finally {
    loadingTags.value = false
  }
}

const getCategoryName = (id) => {
  const c = categories.value.find(c => c.id === id)
  return c ? c.name : ''
}

const getCategoryById = (categoryId) => {
  return categories.value.find(cat => cat.id === categoryId) || categories.value[parseInt(categoryId)] || null
}

const onCategoryChange = () => {
  console.log('Selected category:', selectedCategory.value)
  // 可以在这里添加其他逻辑，比如加载该分类下的书籍等
}

const selectTag = async (tagId, tagName) => {
  selectedTag.value = tagId
  selectedMainCategory.value = ''
  showBooksList.value = false
  
  console.log('Selected tag:', tagId, tagName)
  
  // 加载该标签下的书籍
  loadingTagBooks.value = true
  try {
    // 这里需要调用API获取该标签下的书籍
    // 假设API端点为 /api/provider/books/?tag=tagId
    const params = { tag: tagName }
    const data = await providerApi.listBooks(params)
    tagBooks.value = data.results || data || []
    showBooksList.value = true
    currentCategoryName.value = `${tagName} - 书籍列表`
  } catch (e) {
    console.error('加载标签下的书籍失败', e)
    tagBooks.value = []
  } finally {
    loadingTagBooks.value = false
  }
}

const openCategoryDialog = () => {
  categoryForm.value = { name: '', slug: '', description: '' }
  showCategoryDialog.value = true
}

const openTagDialog = () => {
  tagForm.value = { name: '', description: '' }
  showTagDialog.value = true
}

const submitCategory = async () => {
  if (!categoryForm.value.name || !categoryForm.value.slug) return
  try {
    await providerApi.createCategory(categoryForm.value)
    showCategoryDialog.value = false
    await loadCategories()
  } catch (e) {
    console.error('创建分类失败', e)
  }
}

const submitTag = async () => {
  if (!tagForm.value.name) return
  try {
    await providerApi.createTag(tagForm.value)
    showTagDialog.value = false
    await loadTags()
  } catch (e) {
    console.error('创建标签失败', e)
  }
}

onMounted(() => {
  loadCategories()
  loadTags()
})
</script>

<style scoped>
.provider-categories {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

/* 主要分类区域 */
.main-categories-section {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.main-categories-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.main-category-card {
  padding: 20px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
}

.main-category-card:hover {
  border-color: #409eff;
  background: #f0f7ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
}

.main-category-card.active {
  border-color: #409eff;
  background: #ecf5ff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.category-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.category-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.category-desc {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.category-count {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

.layout {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.select {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  min-width: 150px;
}

.category-details {
  padding: 15px;
  background: #f9fafc;
  border-radius: 4px;
  margin-top: 10px;
}

.category-info {
  line-height: 1.5;
}

.category-info p {
  margin: 5px 0;
}

.category-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.category-item {
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}

.category-main {
  display: flex;
  gap: 8px;
  align-items: center;
}

.category-name {
  font-weight: 500;
}

.category-parent {
  font-size: 12px;
  color: #999;
}

.category-meta {
  font-size: 12px;
  color: #999;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 15px;
}

.tag-chip {
  padding: 8px 16px;
  border-radius: 999px;
  background: #f5f7fa;
  font-size: 14px;
  margin-right: 10px;
  margin-bottom: 10px;
  display: inline-block;
  border: 1px solid #e4e7ed;
  transition: all 0.3s;
}

.tag-chip:hover {
  background: #ecf5ff;
  border-color: #c6e2ff;
}

.tag-chip.active {
  background: #409eff;
  color: #fff;
  border-color: #409eff;
}

.empty-tip {
  font-size: 13px;
  color: #999;
  margin: 8px 0;
}

.btn {
  padding: 6px 12px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  background: #fff;
  font-size: 13px;
  cursor: pointer;
}

.btn-primary {
  background: #409eff;
  border-color: #409eff;
  color: #fff;
}

/* 弹窗复用 ProviderBooksView 的样式 */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: #fff;
  border-radius: 8px;
  width: 420px;
  max-width: 90%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.modal-header,
.modal-footer {
  padding: 12px 16px;
  border-bottom: 1px solid #f0f0f0;
}

.modal-footer {
  border-top: 1px solid #f0f0f0;
  border-bottom: none;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.modal-body {
  padding: 16px;
}

.close-btn {
  border: none;
  background: none;
  font-size: 20px;
  cursor: pointer;
}

.form-group {
  margin-bottom: 12px;
}

.form-label {
  display: block;
  margin-bottom: 4px;
  font-size: 13px;
}

.input {
  width: 100%;
  padding: 8px 10px;
  border-radius: 4px;
  border: 1px solid #dcdfe6;
  font-size: 13px;
  box-sizing: border-box;
}

@media (max-width: 960px) {
  .layout {
    grid-template-columns: 1fr;
  }
  
  .main-categories-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .main-categories-grid {
    grid-template-columns: 1fr;
  }
}

/* 书籍列表区域 */
.books-list-section {
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-top: 24px;
}

.books-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.book-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  background: #fff;
}

.book-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.2);
  transform: translateY(-2px);
}

.book-cover {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48px;
  color: white;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.book-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.book-info {
  padding: 12px;
}

.book-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-author {
  font-size: 13px;
  color: #666;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.book-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #999;
}

.meta-item {
  display: inline-block;
}
</style>



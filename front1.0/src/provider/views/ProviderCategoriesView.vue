<template>
  <ProviderLayout>
    <div class="provider-categories">
      <div class="layout">
        <!-- 左侧：分类管理 -->
        <div class="panel">
          <div class="panel-header">
            <h3>分类管理</h3>
            <button class="btn btn-primary" @click="openCategoryDialog">＋ 新建分类</button>
          </div>

          <div v-if="loadingCategories" class="empty-tip">正在加载分类...</div>
          <div v-else-if="categories.length === 0" class="empty-tip">暂无分类。</div>

          <ul class="category-list">
            <li v-for="cat in categories" :key="cat.id" class="category-item">
              <div class="category-main">
                <span class="category-name">{{ cat.name }}</span>
                <span v-if="cat.parent" class="category-parent">父级：{{ getCategoryName(cat.parent) }}</span>
              </div>
              <div class="category-meta">
                <span class="slug">标识：{{ cat.slug }}</span>
              </div>
            </li>
          </ul>
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
            <span v-for="tag in tags" :key="tag.id" class="tag-chip">
              {{ tag.name }}
            </span>
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
import ProviderLayout from './ProviderLayout.vue'
import { providerApi } from '../api/index.js'

const categories = ref([])
const tags = ref([])
const loadingCategories = ref(false)
const loadingTags = ref(false)

const showCategoryDialog = ref(false)
const showTagDialog = ref(false)

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
    categories.value = await providerApi.listCategories()
  } catch (e) {
    console.error('加载分类失败', e)
  } finally {
    loadingCategories.value = false
  }
}

const loadTags = async () => {
  loadingTags.value = true
  try {
    tags.value = await providerApi.listTags()
  } catch (e) {
    console.error('加载标签失败', e)
  } finally {
    loadingTags.value = false
  }
}

const getCategoryName = (id) => {
  const c = categories.value.find(c => c.id === id)
  return c ? c.name : ''
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
  gap: 16px;
}

.layout {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 20px;
}

.panel {
  background: #fff;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
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
  gap: 6px;
}

.tag-chip {
  padding: 4px 10px;
  border-radius: 999px;
  background: #f5f7fa;
  font-size: 12px;
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
}
</style>



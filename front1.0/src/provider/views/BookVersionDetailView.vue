<template>
  <ProviderLayout>
    <div class="version-detail-container">
      <!-- 顶部操作栏 -->
      <div class="detail-header">
        <div class="header-left">
          <button class="btn btn-back" @click="goBack">
            ← 返回版本管理
          </button>
          <h1 class="version-title">版本详情 - v{{ versionData?.version_number || '加载中...' }}</h1>
          <p class="version-meta" v-if="versionData">
            创建时间：{{ formatTime(versionData.created_at) }} | 
            创建人：{{ versionData.created_by || '未知' }}
          </p>
        </div>
        <div class="header-right">
          <button class="btn btn-secondary" @click="goToCurrentBook">
            查看当前版本
          </button>
        </div>
      </div>

      <!-- 加载状态 -->
      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>正在加载版本详情...</p>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="error-container">
        <p class="error-message">{{ error }}</p>
        <button class="btn" @click="loadVersionDetail">重新加载</button>
      </div>

      <!-- 版本详情内容 -->
      <div v-else-if="versionData" class="detail-content">
        <!-- 左侧：版本基本信息 -->
        <div class="basic-info-section">
          <div class="info-card">
            <div class="cover-section">
              <div class="book-cover-large" :style="{ backgroundColor: getCoverColor(versionData.book) }">
                <img v-if="versionData.cover" :src="versionData.cover" alt="封面" class="cover-image">
                <span v-else>{{ (versionData.title || '书').charAt(0) }}</span>
              </div>
            </div>
            
            <div class="info-main">
              <div class="info-row">
                <label>版本号：</label>
                <span class="version-badge">v{{ versionData.version_number }}</span>
              </div>
              <div class="info-row">
                <label>标题：</label>
                <span>{{ versionData.title }}</span>
              </div>
              <div class="info-row" v-if="versionData.subtitle">
                <label>副标题：</label>
                <span>{{ versionData.subtitle }}</span>
              </div>
              <div class="info-row">
                <label>作者：</label>
                <span>{{ versionData.author }}</span>
              </div>
              <div class="info-row" v-if="versionData.isbn">
                <label>ISBN：</label>
                <span>{{ versionData.isbn }}</span>
              </div>
              <div class="info-row" v-if="versionData.language">
                <label>语言：</label>
                <span>{{ versionData.language }}</span>
              </div>
              <div class="info-row">
                <label>创建时间：</label>
                <span>{{ formatTime(versionData.created_at) }}</span>
              </div>
              <div class="info-row" v-if="versionData.created_by">
                <label>创建人：</label>
                <span>{{ versionData.created_by }}</span>
              </div>
              <div class="info-row" v-if="versionData.comment">
                <label>版本说明：</label>
                <span>{{ versionData.comment }}</span>
              </div>
            </div>
          </div>
          
          <!-- 描述和简介 -->
          <div class="description-section">
            <h3>描述</h3>
            <p>{{ versionData.description || '暂无描述' }}</p>
            
            <h3 v-if="versionData.introduction">详细介绍</h3>
            <div class="introduction-content" v-if="versionData.introduction" v-html="versionData.introduction"></div>
          </div>
          
          <!-- 分类和标签 -->
          <div class="categories-tags-section">
            <div class="tags-group" v-if="versionData.categories && versionData.categories.length > 0">
              <h3>分类</h3>
              <div class="tag-list">
                <span v-for="category in versionData.categories" :key="category" class="tag category-tag">
                  {{ category }}
                </span>
              </div>
            </div>
            
            <div class="tags-group" v-if="versionData.tag_list && versionData.tag_list.length > 0">
              <h3>标签</h3>
              <div class="tag-list">
                <span v-for="tag in versionData.tag_list" :key="tag" class="tag">
                  {{ tag }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧：版本操作 -->
        <div class="sidebar-section">
          <div class="sidebar-card">
            <h3>版本信息</h3>
            <div class="version-info">
              <p><strong>版本号：</strong>v{{ versionData.version_number }}</p>
              <p><strong>创建时间：</strong>{{ formatTime(versionData.created_at) }}</p>
              <p v-if="versionData.created_by"><strong>创建人：</strong>{{ versionData.created_by }}</p>
              <p v-if="versionData.comment"><strong>说明：</strong>{{ versionData.comment }}</p>
            </div>
          </div>

          <div class="sidebar-card">
            <h3>操作</h3>
            <div class="action-buttons">
              <button class="btn btn-primary" @click="goToCurrentBook">
                查看当前版本
              </button>
              <button class="btn btn-secondary" @click="goBack">
                返回版本管理
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </ProviderLayout>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ProviderLayout from './ProviderLayout.vue'
import { providerApi } from '../api/index.js'

const route = useRoute()
const router = useRouter()

// 基本状态
const loading = ref(true)
const error = ref('')
const versionData = ref(null)

// 获取路由参数
const bookId = computed(() => route.params.bookId)
const versionId = computed(() => route.params.versionId)

// 加载版本详情数据
const loadVersionDetail = async () => {
  loading.value = true
  error.value = ''
  try {
    const versionDetail = await providerApi.getVersionDetail(versionId.value)
    versionData.value = versionDetail
  } catch (e) {
    console.error('加载版本详情失败:', e)
    error.value = e.message || '加载版本详情失败，请重试'
  } finally {
    loading.value = false
  }
}

// 根据书籍ID生成封面颜色
const getCoverColor = (bookId) => {
  const colors = ['#4CAF50', '#2196F3', '#FF9800', '#E91E63', '#9C27B0', '#FF5722']
  return colors[Math.abs(bookId) % colors.length]
}

// 返回版本管理页面
const goBack = () => {
  router.push({ name: 'ProviderVersions' })
}

// 跳转到当前版本（书籍详情页）
const goToCurrentBook = () => {
  if (bookId.value) {
    router.push({ name: 'ProviderBookDetail', params: { id: bookId.value } })
  }
}

// 格式化时间
const formatTime = (timeString) => {
  if (!timeString) return '未设置'
  const date = new Date(timeString)
  return date.toLocaleString()
}

// 组件挂载时加载数据
onMounted(() => {
  loadVersionDetail()
})
</script>

<style scoped>
.version-detail-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.header-left .version-title {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: bold;
  color: #333;
}

.header-left .version-meta {
  margin: 0;
  color: #666;
  font-size: 14px;
}

.header-right {
  display: flex;
  gap: 10px;
}

.loading-container,
.error-container {
  text-align: center;
  padding: 60px 20px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 20px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #3498db;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-message {
  color: #e74c3c;
  margin-bottom: 20px;
}

.detail-content {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
}

/* 基本信息区域 */
.basic-info-section {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.info-card {
  display: flex;
  gap: 20px;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.cover-section {
  flex-shrink: 0;
}

.book-cover-large {
  width: 180px;
  height: 240px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 48px;
  font-weight: bold;
  border-radius: 8px;
  overflow: hidden;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.info-main {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.info-row {
  display: flex;
  flex-direction: column;
}

.info-row label {
  font-weight: bold;
  color: #555;
  margin-bottom: 5px;
  font-size: 14px;
}

.info-row span {
  color: #333;
}

.version-badge {
  display: inline-block;
  background: #4caf50;
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-weight: bold;
}

.description-section {
  margin-bottom: 30px;
}

.description-section h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 18px;
}

.description-section p {
  color: #666;
  line-height: 1.6;
}

.introduction-content {
  color: #666;
  line-height: 1.6;
  white-space: pre-wrap;
}

.categories-tags-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}

.tags-group h3 {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag {
  background: #f0f0f0;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  color: #666;
}

.category-tag {
  background: #e3f2fd;
  color: #1976d2;
}

/* 侧边栏区域 */
.sidebar-section {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.sidebar-card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.sidebar-card h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.version-info p {
  margin: 10px 0;
  color: #666;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s;
}

.btn-back {
  background: #f5f5f5;
  color: #333;
  margin-bottom: 10px;
}

.btn-back:hover {
  background: #e0e0e0;
}

.btn-primary {
  background-color: #2196f3;
  color: white;
}

.btn-primary:hover {
  background-color: #1976d2;
}

.btn-secondary {
  background-color: #e0e0e0;
  color: #333;
}

.btn-secondary:hover {
  background-color: #bdbdbd;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .detail-content {
    grid-template-columns: 1fr;
  }
  
  .info-card {
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
  
  .categories-tags-section {
    grid-template-columns: 1fr;
  }
  
  .detail-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
}
</style>


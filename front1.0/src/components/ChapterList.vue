<template>
  <div class="chapter-list-container">
    <div class="chapter-list-header">
      <h3>章节列表</h3>
      <div class="chapter-count">{{ chapterCount }} 章节</div>
    </div>
    <div class="chapter-list-content">
      <div
        v-for="chapter in chapters"
        :key="chapter.id"
        class="chapter-item"
        :class="{ active: isActiveChapter(chapter.id) }"
        @click="navigateToChapter(chapter.id)"
      >
        <div class="chapter-title">{{ chapter.title }}</div>
        <div v-if="chapter.status" class="chapter-status" :class="`status-${chapter.status}`">
          {{ getStatusText(chapter.status) }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'

export default {
  name: 'ChapterList',
  props: {
    chapters: {
      type: Array,
      default: () => []
    },
    bookId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const router = useRouter()
    const route = useRoute()
    const currentSectionId = computed(() => Number(route.params.chapterId))

    // 计算章节数量
    const chapterCount = computed(() => props.chapters.length)

    // 检查是否为当前活跃章节
    const isActiveChapter = (chapterId) => {
      return chapterId === currentSectionId.value
    }

    // 跳转到指定章节
    const navigateToChapter = (chapterId) => {
      router.push({
        path: `/books/${props.bookId}/chapter/${chapterId}`
      })
    }

    // 获取状态文本
    const getStatusText = (status) => {
      const statusMap = {
        completed: '已完成',
        in_progress: '进行中',
        not_started: '未开始'
      }
      return statusMap[status] || ''
    }

    return {
      chapterCount,
      isActiveChapter,
      navigateToChapter,
      getStatusText
    }
  }
}
</script>

<style scoped>
.chapter-list-container {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chapter-list-header {
  padding: 20px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.chapter-list-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
}

.chapter-count {
  font-size: 14px;
  color: #909399;
}

.chapter-list-content {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.chapter-item {
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chapter-item:hover {
  background-color: #f5f7fa;
  border-left-color: #e6f7ff;
}

.chapter-item.active {
  background-color: #ecf5ff;
  border-left-color: #409eff;
}

.chapter-title {
  font-size: 14px;
  color: #303133;
  line-height: 1.5;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-right: 12px;
}

.chapter-item.active .chapter-title {
  color: #409eff;
  font-weight: 500;
}

.chapter-status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 10px;
  flex-shrink: 0;
}

.status-completed {
  background-color: #f0f9eb;
  color: #67c23a;
}

.status-in_progress {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.status-not_started {
  background-color: #f4f4f5;
  color: #909399;
}

/* 自定义滚动条 */
.chapter-list-content::-webkit-scrollbar {
  width: 6px;
}

.chapter-list-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.chapter-list-content::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.chapter-list-content::-webkit-scrollbar-thumb:hover {
  background: #909399;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chapter-list-container {
    width: 100%;
    height: auto;
    max-height: 300px;
  }
  
  .chapter-list-header {
    padding: 16px;
  }
  
  .chapter-list-header h3 {
    font-size: 16px;
  }
  
  .chapter-item {
    padding: 10px 16px;
  }
  
  .chapter-title {
    font-size: 13px;
  }
}
</style>
<template>
  <div class="tools-page">
    <div class="page-header">
      <div class="header-left">
        <h1>教学工具箱</h1>
        <p>常用教学辅助工具，提高工作效率</p>
      </div>
      <div class="header-right">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input
            type="text"
            v-model="searchQuery"
            placeholder="搜索工具..."
          />
        </div>
      </div>
    </div>

    <div class="tools-grid">
      <div
        v-for="category in filteredCategories"
        :key="category.id"
        class="tool-category"
      >
        <div class="category-header">
          <span class="category-icon">{{ category.icon }}</span>
          <h3>{{ category.name }}</h3>
          <span class="tool-count">{{ category.tools.length }}</span>
        </div>
        <div class="tools-list">
          <div
            v-for="tool in category.tools"
            :key="tool.id"
            class="tool-card"
            :class="{ active: activeTool === tool.id }"
            @click="openTool(tool)"
          >
            <div class="tool-icon">{{ tool.icon }}</div>
            <div class="tool-info">
              <h4>{{ tool.name }}</h4>
              <p>{{ tool.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="activeTool" class="tool-modal-overlay" @click.self="closeTool">
      <div class="tool-modal">
        <div class="modal-header">
          <h2>{{ currentTool?.name }}</h2>
          <button class="close-btn" @click="closeTool">×</button>
        </div>
        <div class="modal-body">
          <component :is="currentTool.component" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

import GradeCalculator from './tools/GradeCalculator.vue'
import AttendanceTracker from './tools/AttendanceTracker.vue'
import CodePlayground from './tools/CodePlayground.vue'
import MarkdownEditor from './tools/MarkdownEditor.vue'
import TimerTool from './tools/TimerTool.vue'
import CalendarTool from './tools/CalendarTool.vue'
import UnitConverter from './tools/UnitConverter.vue'
import ColorPicker from './tools/ColorPicker.vue'
import PasswordGenerator from './tools/PasswordGenerator.vue'
import QRCodeGenerator from './tools/QRCodeGenerator.vue'

export default {
  name: 'TeachingToolsView',
  components: {
    GradeCalculator,
    AttendanceTracker,
    CodePlayground,
    MarkdownEditor,
    TimerTool,
    CalendarTool,
    UnitConverter,
    ColorPicker,
    PasswordGenerator,
    QRCodeGenerator
  },
  setup() {
    const searchQuery = ref('')
    const activeTool = ref(null)

    const categories = ref([
      {
        id: 'calculation',
        name: '计算工具',
        icon: '🧮',
        tools: [
          { id: 'grade-calculator', name: '成绩计算器', description: '快速计算学生成绩和统计', icon: '📊', component: 'GradeCalculator' },
          { id: 'attendance', name: '考勤记录', description: '记录和管理学生考勤', icon: '📋', component: 'AttendanceTracker' },
          { id: 'unit-converter', name: '单位换算', description: '常用单位换算工具', icon: '📐', component: 'UnitConverter' }
        ]
      },
      {
        id: 'development',
        name: '编程开发',
        icon: '💻',
        tools: [
          { id: 'code-playground', name: '代码实验室', description: '在线编写和测试代码', icon: '🔧', component: 'CodePlayground' },
          { id: 'password-generator', name: '密码生成器', description: '生成安全密码', icon: '🔐', component: 'PasswordGenerator' }
        ]
      },
      {
        id: 'writing',
        name: '文档写作',
        icon: '📝',
        tools: [
          { id: 'markdown', name: 'Markdown编辑器', description: '编写格式文档', icon: '✍️', component: 'MarkdownEditor' }
        ]
      },
      {
        id: 'productivity',
        name: '效率工具',
        icon: '⚡',
        tools: [
          { id: 'timer', name: '计时器', description: '课堂计时和倒计时', icon: '⏱️', component: 'TimerTool' },
          { id: 'calendar', name: '日历工具', description: '日期计算和日程管理', icon: '📅', component: 'CalendarTool' }
        ]
      },
      {
        id: 'utility',
        name: '实用工具',
        icon: '🛠️',
        tools: [
          { id: 'color-picker', name: '颜色选择器', description: '选取和管理颜色', icon: '🎨', component: 'ColorPicker' },
          { id: 'qrcode', name: '二维码生成', description: '生成教学相关二维码', icon: '📱', component: 'QRCodeGenerator' }
        ]
      }
    ])

    const filteredCategories = computed(() => {
      if (!searchQuery.value) return categories.value
      
      return categories.value
        .map(category => ({
          ...category,
          tools: category.tools.filter(tool =>
            tool.name.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
            tool.description.toLowerCase().includes(searchQuery.value.toLowerCase())
          )
        }))
        .filter(category => category.tools.length > 0)
    })

    const currentTool = computed(() => {
      if (!activeTool.value) return null
      
      for (const category of categories.value) {
        const tool = category.tools.find(t => t.id === activeTool.value)
        if (tool) return tool
      }
      return null
    })

    const openTool = (tool) => {
      activeTool.value = tool.id
    }

    const closeTool = () => {
      activeTool.value = null
    }

    return {
      searchQuery,
      activeTool,
      categories,
      filteredCategories,
      currentTool,
      openTool,
      closeTool
    }
  }
}
</script>

<style scoped>
.tools-page {
  padding: 24px;
  background: #f8fafc;
  min-height: 100vh;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.header-left h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.header-left p {
  font-size: 14px;
  color: #64748b;
}

.search-box {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 10px 16px;
  width: 280px;
  transition: all 0.3s ease;
}

.search-box:focus-within {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.search-icon {
  margin-right: 8px;
  font-size: 16px;
}

.search-box input {
  border: none;
  outline: none;
  font-size: 14px;
  width: 100%;
  color: #1e293b;
}

.search-box input::placeholder {
  color: #94a3b8;
}

.tools-grid {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.tool-category {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.tool-category:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.category-header {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f1f5f9;
}

.category-icon {
  font-size: 28px;
  margin-right: 12px;
}

.category-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.tool-count {
  background: #f1f5f9;
  color: #64748b;
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 20px;
  margin-left: auto;
}

.tools-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.tool-card {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid transparent;
}

.tool-card:hover {
  background: #f1f5f9;
  border-color: #e2e8f0;
  transform: translateY(-2px);
}

.tool-card.active {
  background: #eff6ff;
  border-color: #3b82f6;
}

.tool-icon {
  font-size: 32px;
  margin-right: 14px;
  flex-shrink: 0;
}

.tool-info h4 {
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.tool-info p {
  font-size: 13px;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

.tool-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(15, 23, 42, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.2s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.tool-modal {
  background: white;
  border-radius: 20px;
  width: 90%;
  max-width: 900px;
  max-height: 85vh;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
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
  padding: 20px 28px;
  border-bottom: 1px solid #f1f5f9;
  background: #f8fafc;
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
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #e2e8f0;
  color: #1e293b;
}

.modal-body {
  padding: 28px;
  max-height: calc(85vh - 80px);
  overflow-y: auto;
}

@media (max-width: 768px) {
  .tools-page {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .search-box {
    width: 100%;
  }

  .tools-list {
    grid-template-columns: 1fr;
  }

  .tool-modal {
    width: 95%;
    max-height: 90vh;
  }
}
</style>

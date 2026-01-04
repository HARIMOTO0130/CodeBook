<template>
  <Teleport to="body">
    <transition name="drawer">
      <div v-if="visible" class="drawer-overlay" @click.self="closeDrawer">
        <div class="drawer-container" :class="{ 'right': position === 'right', 'left': position === 'left' }">
          <div class="drawer-header">
            <h3 class="drawer-title">{{ title || '侧边抽屉' }}</h3>
            <button class="close-btn" @click="closeDrawer">×</button>
          </div>
          
          <!-- 标签页导航 -->
          <div v-if="tabs && tabs.length > 0" class="drawer-tabs">
            <button 
              v-for="tab in tabs" 
              :key="tab.key"
              class="tab-btn"
              :class="{ active: activeTab === tab.key }"
              @click="activeTab = tab.key"
            >
              <span class="tab-icon">{{ tab.icon }}</span>
              <span class="tab-label">{{ tab.label }}</span>
            </button>
          </div>
          
          <div class="drawer-content">
            <!-- 标签页内容插槽 -->
            <template v-if="tabs && tabs.length > 0">
              <div v-for="tab in tabs" :key="tab.key" v-show="activeTab === tab.key" class="tab-content">
                <slot :name="tab.key">
                  <!-- 默认内容 -->
                  <div class="empty-tab-content">
                    {{ tab.emptyText || '暂无内容' }}
                  </div>
                </slot>
              </div>
            </template>
            
            <!-- 无标签页时的默认内容 -->
            <slot v-else>
              <div class="empty-drawer-content">
                暂无内容
              </div>
            </slot>
          </div>
          
          <!-- 底部操作区 -->
          <div v-if="hasFooter" class="drawer-footer">
            <slot name="footer">
              <!-- 默认底部操作 -->
              <div class="footer-actions">
                <button class="btn btn-secondary" @click="closeDrawer">关闭</button>
              </div>
            </slot>
          </div>
        </div>
      </div>
    </transition>
  </Teleport>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

export default {
  name: 'SidebarDrawer',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: ''
    },
    position: {
      type: String,
      default: 'right',
      validator: (value) => ['left', 'right'].includes(value)
    },
    width: {
      type: String,
      default: '400px'
    },
    height: {
      type: String,
      default: '100vh'
    },
    tabs: {
      type: Array,
      default: () => []
    },
    hasFooter: {
      type: Boolean,
      default: false
    },
    keyboard: {
      type: Boolean,
      default: true
    },
    escToClose: {
      type: Boolean,
      default: true
    },
    closeOnClickOverlay: {
      type: Boolean,
      default: true
    }
  },
  emits: ['update:visible', 'close', 'tabChange'],
  setup(props, { emit }) {
    const activeTab = ref(props.tabs.length > 0 ? props.tabs[0].key : '')
    
    // 关闭抽屉
    const closeDrawer = () => {
      if (props.closeOnClickOverlay || !props.closeOnClickOverlay) {
        emit('update:visible', false)
        emit('close')
      }
    }
    
    // 处理键盘事件
    const handleKeyDown = (event) => {
      if (!props.keyboard) return
      
      // ESC键关闭
      if (props.escToClose && event.key === 'Escape') {
        closeDrawer()
      }
      
      // 其他快捷键处理可以在这里添加
      // 例如 N 键切换可见性（如果作为全局笔记抽屉）
      if (event.key.toLowerCase() === 'n' && event.ctrlKey && props.title === '笔记/讨论') {
        event.preventDefault()
        emit('update:visible', !props.visible)
      }
    }
    
    // 处理标签切换
    watch(activeTab, (newTab) => {
      emit('tabChange', newTab)
    })
    
    // 监听可见性变化，更新body样式
    watch(() => props.visible, (visible) => {
      if (visible) {
        // 禁止背景滚动
        document.body.style.overflow = 'hidden'
        // 防止点击抽屉外部区域时抽屉关闭的延迟问题
        setTimeout(() => {
          document.addEventListener('keydown', handleKeyDown)
        }, 100)
      } else {
        document.body.style.overflow = 'auto'
        document.removeEventListener('keydown', handleKeyDown)
      }
    }, { immediate: true })
    
    onMounted(() => {
      // 如果初始可见，添加事件监听
      if (props.visible) {
        document.body.style.overflow = 'hidden'
        document.addEventListener('keydown', handleKeyDown)
      }
    })
    
    onBeforeUnmount(() => {
      // 清理事件监听和样式
      document.body.style.overflow = 'auto'
      document.removeEventListener('keydown', handleKeyDown)
    })
    
    return {
      activeTab,
      closeDrawer
    }
  }
}
</script>

<style scoped>
/* 遮罩层 */
.drawer-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  z-index: 1000;
  overflow: hidden;
}

/* 抽屉容器 */
.drawer-container {
  position: relative;
  width: v-bind(width);
  height: v-bind(height);
  background: white;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease;
}

.drawer-container.right {
  transform: translateX(0);
}

.drawer-container.left {
  transform: translateX(0);
  order: -1;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
}

/* 头部 */
.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.drawer-title {
  margin: 0;
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #909399;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: #f5f5f5;
  color: #303133;
}

/* 标签页 */
.drawer-tabs {
  display: flex;
  border-bottom: 1px solid #f0f0f0;
  background: #fafafa;
}

.tab-btn {
  flex: 1;
  padding: 12px 16px;
  border: none;
  background: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #409eff;
  background: #ecf5ff;
}

.tab-btn.active {
  color: #409eff;
  border-bottom-color: #409eff;
  background: white;
}

.tab-icon {
  font-size: 16px;
}

.tab-label {
  font-weight: 500;
}

/* 内容区域 */
.drawer-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: white;
}

.tab-content {
  height: 100%;
  overflow-y: auto;
}

.empty-tab-content,
.empty-drawer-content {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #909399;
  font-size: 14px;
}

/* 底部操作区 */
.drawer-footer {
  padding: 16px 24px;
  border-top: 1px solid #f0f0f0;
  background: #fafafa;
}

.footer-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 过渡动画 */
.drawer-enter-active,
.drawer-leave-active {
  transition: all 0.3s ease;
}

.drawer-enter-from .drawer-container.right,
.drawer-leave-to .drawer-container.right {
  transform: translateX(100%);
}

.drawer-enter-from .drawer-container.left,
.drawer-leave-to .drawer-container.left {
  transform: translateX(-100%);
}

.drawer-enter-from .drawer-overlay,
.drawer-leave-to .drawer-overlay {
  opacity: 0;
}

/* 按钮样式 */
.btn {
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.btn-primary {
  background: #409eff;
  color: white;
  border-color: #409eff;
}

.btn-primary:hover {
  background: #66b1ff;
  border-color: #66b1ff;
}

.btn-secondary {
  background: white;
  color: #606266;
  border-color: #dcdfe6;
}

.btn-secondary:hover {
  color: #409eff;
  border-color: #c6e2ff;
  background: #ecf5ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .drawer-container {
    width: 100% !important;
    max-width: 100%;
  }
  
  .drawer-header {
    padding: 16px 20px;
  }
  
  .drawer-title {
    font-size: 16px;
  }
  
  .drawer-content {
    padding: 16px;
  }
  
  .drawer-footer {
    padding: 16px;
  }
  
  .tab-btn {
    padding: 10px 8px;
    font-size: 13px;
    flex-direction: column;
    gap: 4px;
  }
  
  .tab-label {
    font-size: 12px;
  }
  
  .footer-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .drawer-container {
    height: 100vh;
  }
}

/* 自定义滚动条 */
.drawer-content::-webkit-scrollbar {
  width: 6px;
}

.drawer-content::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.drawer-content::-webkit-scrollbar-thumb {
  background: #c0c4cc;
  border-radius: 3px;
}

.drawer-content::-webkit-scrollbar-thumb:hover {
  background: #909399;
}
</style>
<template>
  <div class="progress-bar-container" :class="containerClass">
    <div 
      class="progress-bar" 
      :style="barStyle"
    >
      <!-- 进度填充 -->
      <div 
        class="progress-fill" 
        :style="fillStyle"
      >
        <!-- 进度文本（在进度条内部） -->
        <div v-if="showText && position === 'inside'" class="progress-text">
          {{ progressText }}
        </div>
      </div>
    </div>
    
    <!-- 进度文本（在进度条外部） -->
    <div 
      v-if="showText && position !== 'inside'" 
      class="progress-text external"
      :class="`text-${position}`"
    >
      {{ progressText }}
    </div>
    
    <!-- 进度点标记 -->
    <div v-if="markers && markers.length > 0" class="progress-markers">
      <div 
        v-for="(marker, index) in markers" 
        :key="index"
        class="marker"
        :style="{ left: `${marker.position}%` }"
        :title="marker.label || ''"
      >
        <div class="marker-dot" :class="marker.className"></div>
        <div v-if="marker.label" class="marker-label" :class="marker.className">
          {{ marker.label }}
        </div>
      </div>
    </div>
    
    <!-- 状态指示器 -->
    <div v-if="status" class="status-indicator" :class="`status-${status}`">
      <span class="status-icon">{{ statusIcon }}</span>
      <span class="status-text">{{ statusText }}</span>
    </div>
  </div>
</template>

<script>
import { computed, watch, ref } from 'vue'

export default {
  name: 'ProgressBar',
  props: {
    value: {
      type: Number,
      default: 0,
      validator: (val) => val >= 0 && val <= 100
    },
    max: {
      type: Number,
      default: 100
    },
    height: {
      type: String,
      default: '8px'
    },
    color: {
      type: String,
      default: '#409EFF'
    },
    backgroundColor: {
      type: String,
      default: '#f0f0f0'
    },
    borderRadius: {
      type: String,
      default: '4px'
    },
    showText: {
      type: Boolean,
      default: false
    },
    textFormat: {
      type: String,
      default: 'percentage', // 'percentage', 'value', 'custom'
      validator: (val) => ['percentage', 'value', 'custom'].includes(val)
    },
    customText: {
      type: String,
      default: ''
    },
    position: {
      type: String,
      default: 'inside', // 'inside', 'above', 'below', 'left', 'right'
      validator: (val) => ['inside', 'above', 'below', 'left', 'right'].includes(val)
    },
    animated: {
      type: Boolean,
      default: true
    },
    animationDuration: {
      type: String,
      default: '0.6s'
    },
    striped: {
      type: Boolean,
      default: false
    },
    markers: {
      type: Array,
      default: () => []
    },
    status: {
      type: String,
      default: '',
      validator: (val) => ['success', 'warning', 'error', 'info', ''].includes(val)
    },
    size: {
      type: String,
      default: 'medium', // 'small', 'medium', 'large'
      validator: (val) => ['small', 'medium', 'large'].includes(val)
    },
    indeterminate: {
      type: Boolean,
      default: false
    },
    reverse: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:value'],
  setup(props) {
    // 用于动画效果的内部值
    const animatedValue = ref(props.value)
    
    // 监听外部值变化，更新动画值
    watch(() => props.value, (newVal) => {
      if (props.animated) {
        // 使用requestAnimationFrame确保动画流畅
        requestAnimationFrame(() => {
          animatedValue.value = newVal
        })
      } else {
        animatedValue.value = newVal
      }
    }, { immediate: true })
    
    // 计算进度百分比
    const percentage = computed(() => {
      return Math.min(100, Math.max(0, (animatedValue.value / props.max) * 100))
    })
    
    // 计算容器样式类
    const containerClass = computed(() => {
      const classes = []
      
      if (props.size) {
        classes.push(`size-${props.size}`)
      }
      
      if (props.indeterminate) {
        classes.push('indeterminate')
      }
      
      if (props.striped) {
        classes.push('striped')
      }
      
      if (props.showText) {
        classes.push(`has-text`)
      }
      
      if (props.reverse) {
        classes.push('reverse')
      }
      
      return classes
    })
    
    // 计算进度条样式
    const barStyle = computed(() => ({
      height: props.height,
      backgroundColor: props.backgroundColor,
      borderRadius: props.borderRadius
    }))
    
    // 计算填充样式
    const fillStyle = computed(() => {
      const baseStyle = {
        width: props.indeterminate ? '100%' : `${percentage.value}%`,
        backgroundColor: props.color,
        borderRadius: props.borderRadius,
        transition: props.animated ? `width ${props.animationDuration} ease` : 'none'
      }
      
      if (props.reverse) {
        baseStyle.marginLeft = props.indeterminate ? '0' : `${100 - percentage.value}%`
      }
      
      return baseStyle
    })
    
    // 计算进度文本
    const progressText = computed(() => {
      if (props.textFormat === 'custom' && props.customText) {
        return props.customText
      }
      
      if (props.textFormat === 'value') {
        return `${animatedValue.value}/${props.max}`
      }
      
      // 默认百分比
      return `${Math.round(percentage.value)}%`
    })
    
    // 状态图标
    const statusIcon = computed(() => {
      const iconMap = {
        success: '✅',
        warning: '⚠️',
        error: '❌',
        info: 'ℹ️'
      }
      return iconMap[props.status] || ''
    })
    
    // 状态文本
    const statusText = computed(() => {
      const textMap = {
        success: '已完成',
        warning: '进行中',
        error: '出错',
        info: '信息'
      }
      return textMap[props.status] || ''
    })
    
    return {
      percentage,
      containerClass,
      barStyle,
      fillStyle,
      progressText,
      statusIcon,
      statusText
    }
  }
}
</script>

<style scoped>
.progress-bar-container {
  position: relative;
  width: 100%;
  display: inline-flex;
  flex-direction: column;
}

/* 进度条容器尺寸变体 */
.progress-bar-container.size-small .progress-bar {
  height: 4px !important;
  border-radius: 2px !important;
}

.progress-bar-container.size-large .progress-bar {
  height: 16px !important;
  border-radius: 8px !important;
}

/* 进度条基础样式 */
.progress-bar {
  width: 100%;
  background-color: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

/* 进度填充 */
.progress-fill {
  height: 100%;
  background-color: #409EFF;
  border-radius: inherit;
  transition: width 0.6s ease;
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* 反向进度条 */
.progress-bar-container.reverse .progress-fill {
  margin-left: auto;
}

/* 条纹效果 */
.progress-bar-container.striped .progress-fill {
  background-image: 
    linear-gradient(
      45deg,
      rgba(255, 255, 255, 0.15) 25%,
      transparent 25%,
      transparent 50%,
      rgba(255, 255, 255, 0.15) 50%,
      rgba(255, 255, 255, 0.15) 75%,
      transparent 75%,
      transparent
    );
  background-size: 1rem 1rem;
}

/* 不确定进度条动画 */
.progress-bar-container.indeterminate .progress-fill {
  animation: indeterminate-progress 1.5s ease-in-out infinite;
}

@keyframes indeterminate-progress {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* 进度文本样式 */
.progress-text {
  color: white;
  font-size: 12px;
  font-weight: 500;
  text-align: center;
  text-shadow: 0 0 2px rgba(0, 0, 0, 0.5);
  white-space: nowrap;
  padding: 0 8px;
}

/* 外部文本样式 */
.progress-text.external {
  color: #606266;
  text-shadow: none;
  margin-top: 4px;
}

.progress-text.text-above {
  order: -1;
  margin-bottom: 4px;
  margin-top: 0;
}

.progress-text.text-left {
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  margin-right: 8px;
  margin-top: 0;
}

.progress-text.text-right {
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  margin-left: 8px;
  margin-top: 0;
}

/* 带文本的进度条容器间距 */
.progress-bar-container.has-text {
  gap: 4px;
}

/* 标记点样式 */
.progress-markers {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  pointer-events: none;
}

.marker {
  position: absolute;
  top: 0;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  height: 100%;
}

.marker-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #909399;
  margin-top: -4px;
  border: 2px solid white;
  z-index: 1;
}

.marker-label {
  position: absolute;
  top: 100%;
  margin-top: 8px;
  font-size: 12px;
  color: #606266;
  white-space: nowrap;
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: center;
}

/* 状态指示器 */
.status-indicator {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  font-size: 14px;
  padding: 6px 12px;
  border-radius: 4px;
  align-self: flex-start;
}

.status-success {
  background-color: #f0f9eb;
  color: #67c23a;
}

.status-warning {
  background-color: #fdf6ec;
  color: #e6a23c;
}

.status-error {
  background-color: #fef0f0;
  color: #f56c6c;
}

.status-info {
  background-color: #edf2fc;
  color: #909399;
}

.status-icon {
  font-size: 16px;
}

.status-text {
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .marker-label {
    font-size: 11px;
    max-width: 60px;
  }
  
  .status-indicator {
    font-size: 13px;
    padding: 4px 8px;
  }
  
  .progress-text {
    font-size: 11px;
  }
  
  .progress-bar-container.size-large .progress-bar {
    height: 12px !important;
  }
}

@media (max-width: 480px) {
  .progress-text.text-left,
  .progress-text.text-right {
    position: static;
    transform: none;
    margin: 4px 0;
  }
  
  .marker-label {
    display: none;
  }
}
</style>
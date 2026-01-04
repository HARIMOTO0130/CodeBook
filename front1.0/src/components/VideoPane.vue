<template>
  <div class="video-pane" :class="{ 'expanded': expanded, 'float-mode': isFloatMode }">
    <div class="video-header">
      <div class="video-title">{{ title || '视频讲解' }}</div>
      <div class="video-actions">
        <button class="action-btn" @click="toggleSubtitles" title="开关字幕">
          📝 {{ subtitlesEnabled ? '关闭字幕' : '开启字幕' }}
        </button>
        <button class="action-btn" @click="showSpeedMenu = !showSpeedMenu" title="播放速度">
          ⏱️ {{ playbackSpeed }}x
        </button>
        <button class="action-btn" @click="toggleFloatMode" title="浮动模式">
          🖥️ {{ isFloatMode ? '嵌入模式' : '浮动模式' }}
        </button>
        <button class="action-btn" @click="toggleExpanded" title="全屏显示">
          📱 {{ expanded ? '收起' : '展开' }}
        </button>
        <button class="action-btn close-btn" @click="handleClose" v-if="showClose">
          ✕ 关闭
        </button>
      </div>
    </div>
    
    <div class="video-container">
      <video 
        ref="videoElement" 
        :src="src" 
        controls 
        @timeupdate="handleTimeUpdate" 
        @ended="handleEnded"
        @play="handlePlay"
        @pause="handlePause"
        @loadedmetadata="handleLoadedMetadata"
      >
        <!-- 字幕轨道 -->
        <track 
          v-if="subtitlesUrl" 
          kind="subtitles" 
          :src="subtitlesUrl" 
          srclang="zh-CN" 
          label="中文"
          :default="subtitlesEnabled"
        >
      </video>
      
      <!-- 视频加载占位 -->
      <div v-if="!src" class="video-placeholder">
        <div class="placeholder-icon">🎬</div>
        <p>暂无视频讲解</p>
      </div>
    </div>
    
    <!-- 字幕显示区域 -->
    <div v-if="subtitlesEnabled && currentSubtitle" class="subtitle-display">
      {{ currentSubtitle.text }}
    </div>
    
    <!-- 播放速率菜单 -->
    <div v-if="showSpeedMenu" class="speed-menu">
      <button 
        v-for="speed in playbackSpeeds" 
        :key="speed"
        class="speed-option"
        :class="{ active: playbackSpeed === speed }"
        @click="setPlaybackSpeed(speed)"
      >
        {{ speed }}x
      </button>
    </div>
    
    <!-- 进度条 -->
    <div class="video-progress">
      <div 
        class="progress-bar" 
        @click="seekVideo"
      >
        <div 
          class="progress-fill" 
          :style="{ width: `${progressPercentage}%` }"
        ></div>
        <div 
          class="progress-handle" 
          :style="{ left: `${progressPercentage}%` }"
          @mousedown="startDragging"
        ></div>
      </div>
      <div class="time-display">
        <span>{{ formatTime(currentTime) }}</span>
        <span>/</span>
        <span>{{ formatTime(duration) }}</span>
      </div>
    </div>
    
    <!-- 代码联动提示 -->
    <div v-if="showCodeHint" class="code-hint">
      <div class="hint-content">
        <span class="hint-icon">💡</span>
        <span>{{ codeHintText }}</span>
        <button class="hint-btn" @click="handleCodeHintClick">跳转代码</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

export default {
  name: 'VideoPane',
  props: {
    src: {
      type: String,
      default: ''
    },
    title: {
      type: String,
      default: ''
    },
    subtitlesUrl: {
      type: String,
      default: ''
    },
    subtitlesEnabled: {
      type: Boolean,
      default: true
    },
    playbackSpeed: {
      type: Number,
      default: 1.0
    },
    expanded: {
      type: Boolean,
      default: false
    },
    showClose: {
      type: Boolean,
      default: true
    },
    isFloatMode: {
      type: Boolean,
      default: false
    },
    linkedCodeBlocks: {
      type: Array,
      default: () => []
    }
  },
  emits: ['update:playbackSpeed', 'update:subtitlesEnabled', 'update:expanded', 'update:isFloatMode', 'timeUpdate', 'ended', 'play', 'pause', 'close', 'codeBlockLinked'],
  setup(props, { emit }) {
    const videoElement = ref(null)
    const showSpeedMenu = ref(false)
    const currentTime = ref(0)
    const duration = ref(0)
    const progressPercentage = ref(0)
    const isDragging = ref(false)
    const currentSubtitle = ref(null)
    const showCodeHint = ref(false)
    const codeHintText = ref('')
    
    // 可用的播放速率
    const playbackSpeeds = [0.75, 1.0, 1.25, 1.5, 2.0]
    
    // 处理视频时间更新
    const handleTimeUpdate = () => {
      if (!videoElement.value) return
      
      currentTime.value = videoElement.value.currentTime
      duration.value = videoElement.value.duration || 0
      progressPercentage.value = duration.value > 0 ? (currentTime.value / duration.value) * 100 : 0
      
      // 检查是否有代码联动点
      checkCodeLink(currentTime.value)
      
      // 检查字幕
      if (props.subtitlesEnabled) {
        checkSubtitle(currentTime.value)
      }
      
      emit('timeUpdate', currentTime.value)
    }
    
    // 处理视频结束
    const handleEnded = () => {
      emit('ended')
    }
    
    // 处理视频播放
    const handlePlay = () => {
      emit('play')
    }
    
    // 处理视频暂停
    const handlePause = () => {
      emit('pause')
    }
    
    // 处理视频加载完成
    const handleLoadedMetadata = () => {
      if (videoElement.value) {
        duration.value = videoElement.value.duration || 0
        videoElement.value.playbackRate = props.playbackSpeed
        
        // 启用/禁用字幕
        toggleSubtitlesTrack(props.subtitlesEnabled)
      }
    }
    
    // 切换字幕
    const toggleSubtitles = () => {
      const newValue = !props.subtitlesEnabled
      emit('update:subtitlesEnabled', newValue)
      toggleSubtitlesTrack(newValue)
    }
    
    // 切换字幕轨道显示
    const toggleSubtitlesTrack = (enabled) => {
      if (!videoElement.value) return
      
      const tracks = videoElement.value.textTracks
      for (let i = 0; i < tracks.length; i++) {
        tracks[i].mode = enabled ? 'showing' : 'hidden'
      }
      
      if (!enabled) {
        currentSubtitle.value = null
      }
    }
    
    // 设置播放速率
    const setPlaybackSpeed = (speed) => {
      if (videoElement.value) {
        videoElement.value.playbackRate = speed
      }
      emit('update:playbackSpeed', speed)
      showSpeedMenu.value = false
    }
    
    // 切换展开/收起
    const toggleExpanded = () => {
      emit('update:expanded', !props.expanded)
    }
    
    // 切换浮动模式
    const toggleFloatMode = () => {
      emit('update:isFloatMode', !props.isFloatMode)
    }
    
    // 关闭视频面板
    const handleClose = () => {
      emit('close')
    }
    
    // 跳转到指定时间
    const seekVideo = (event) => {
      if (!videoElement.value || isDragging.value) return
      
      const rect = event.currentTarget.getBoundingClientRect()
      const pos = (event.clientX - rect.left) / rect.width
      const newTime = pos * duration.value
      
      videoElement.value.currentTime = newTime
      currentTime.value = newTime
      progressPercentage.value = pos * 100
    }
    
    // 开始拖动进度条
    const startDragging = (event) => {
      isDragging.value = true
      event.stopPropagation()
      
      const handleMouseMove = (e) => {
        if (!videoElement.value || !isDragging.value) return
        
        const rect = videoElement.value.closest('.progress-bar').getBoundingClientRect()
        let pos = (e.clientX - rect.left) / rect.width
        pos = Math.max(0, Math.min(1, pos))
        
        progressPercentage.value = pos * 100
      }
      
      const handleMouseUp = () => {
        if (!videoElement.value || !isDragging.value) return
        
        const newTime = (progressPercentage.value / 100) * duration.value
        videoElement.value.currentTime = newTime
        currentTime.value = newTime
        
        isDragging.value = false
        document.removeEventListener('mousemove', handleMouseMove)
        document.removeEventListener('mouseup', handleMouseUp)
      }
      
      document.addEventListener('mousemove', handleMouseMove)
      document.addEventListener('mouseup', handleMouseUp)
    }
    
    // 检查是否有代码联动
    const checkCodeLink = (time) => {
      if (!props.linkedCodeBlocks || props.linkedCodeBlocks.length === 0) {
        showCodeHint.value = false
        return
      }
      
      // 查找当前时间点的代码联动
      const currentLink = props.linkedCodeBlocks.find(link => 
        time >= link.startTime && time <= link.endTime
      )
      
      if (currentLink) {
        codeHintText.value = currentLink.description || '相关代码块'
        showCodeHint.value = true
      } else {
        showCodeHint.value = false
      }
    }
    
    // 处理代码提示点击
    const handleCodeHintClick = () => {
      const currentLink = props.linkedCodeBlocks.find(link => 
        currentTime.value >= link.startTime && currentTime.value <= link.endTime
      )
      
      if (currentLink) {
        emit('codeBlockLinked', currentLink)
      }
    }
    
    // 检查字幕
    const checkSubtitle = (time) => {
      // 简单的字幕模拟，实际应用中可能需要解析字幕文件
      // 这里只是演示
      if (time >= 5 && time <= 10) {
        currentSubtitle.value = { text: '欢迎学习本章节内容' }
      } else if (time >= 15 && time <= 20) {
        currentSubtitle.value = { text: '接下来我们将讲解核心概念' }
      } else if (time >= 30 && time <= 40) {
        currentSubtitle.value = { text: '请查看右侧的代码示例' }
      } else {
        currentSubtitle.value = null
      }
    }
    
    // 格式化时间
    const formatTime = (seconds) => {
      if (!seconds || isNaN(seconds)) return '0:00'
      
      const mins = Math.floor(seconds / 60)
      const secs = Math.floor(seconds % 60)
      return `${mins}:${secs.toString().padStart(2, '0')}`
    }
    
    // 监听播放速率变化
    watch(() => props.playbackSpeed, (newSpeed) => {
      if (videoElement.value) {
        videoElement.value.playbackRate = newSpeed
      }
    })
    
    // 监听浮动模式变化，调整视频大小
    watch(() => props.isFloatMode, () => {
      // 可以在这里添加特定于浮动模式的逻辑
    })
    
    // 点击外部关闭速度菜单
    const handleClickOutside = (event) => {
      const speedMenu = document.querySelector('.speed-menu')
      const speedBtn = document.querySelector('.action-btn[title="播放速度"]')
      
      if (speedMenu && !speedMenu.contains(event.target) && speedBtn && !speedBtn.contains(event.target)) {
        showSpeedMenu.value = false
      }
    }
    
    onMounted(() => {
      document.addEventListener('click', handleClickOutside)
    })
    
    onBeforeUnmount(() => {
      document.removeEventListener('click', handleClickOutside)
    })
    
    return {
      videoElement,
      showSpeedMenu,
      currentTime,
      duration,
      progressPercentage,
      currentSubtitle,
      showCodeHint,
      codeHintText,
      playbackSpeeds,
      handleTimeUpdate,
      handleEnded,
      handlePlay,
      handlePause,
      handleLoadedMetadata,
      toggleSubtitles,
      setPlaybackSpeed,
      toggleExpanded,
      toggleFloatMode,
      handleClose,
      seekVideo,
      startDragging,
      handleCodeHintClick,
      formatTime
    }
  }
}
</script>

<style scoped>
.video-pane {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
  overflow: hidden;
  transition: all 0.3s ease;
}

.video-pane.expanded {
  flex: 1;
  min-height: 400px;
}

.video-pane.float-mode {
  position: fixed;
  top: 100px;
  right: 30px;
  width: 400px;
  max-height: 600px;
  z-index: 100;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}

/* 头部样式 */
.video-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f5f5;
  border-bottom: 1px solid #e0e0e0;
}

.video-title {
  font-weight: 500;
  color: #333;
  font-size: 14px;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.video-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.action-btn {
  padding: 6px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 4px;
}

.action-btn:hover {
  background: #f0f0f0;
  border-color: #bbb;
}

.close-btn {
  color: #f56c6c;
  border-color: #f56c6c;
}

.close-btn:hover {
  background: #f56c6c;
  color: white;
}

/* 视频容器 */
.video-container {
  position: relative;
  width: 100%;
  background: #000;
}

video {
  width: 100%;
  height: auto;
  display: block;
}

.video-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #999;
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

/* 字幕显示 */
.subtitle-display {
  padding: 12px 16px;
  background: rgba(0,0,0,0.7);
  color: white;
  text-align: center;
  font-size: 14px;
  line-height: 1.5;
}

/* 速度菜单 */
.speed-menu {
  position: absolute;
  top: 45px;
  right: 100px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  z-index: 10;
  overflow: hidden;
}

.speed-option {
  display: block;
  width: 100%;
  padding: 8px 16px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 14px;
  text-align: center;
  transition: background 0.2s;
}

.speed-option:hover {
  background: #f5f5f5;
}

.speed-option.active {
  background: #409EFF;
  color: white;
}

/* 进度条 */
.video-progress {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  background: #f5f5f5;
  border-top: 1px solid #e0e0e0;
}

.progress-bar {
  flex: 1;
  height: 6px;
  background: #ddd;
  border-radius: 3px;
  position: relative;
  cursor: pointer;
}

.progress-fill {
  height: 100%;
  background: #409EFF;
  border-radius: 3px;
  position: absolute;
  top: 0;
  left: 0;
}

.progress-handle {
  width: 12px;
  height: 12px;
  background: white;
  border: 2px solid #409EFF;
  border-radius: 50%;
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  cursor: pointer;
  transition: scale 0.2s;
}

.progress-handle:hover {
  scale: 1.2;
}

.time-display {
  font-size: 12px;
  color: #666;
  min-width: 80px;
  text-align: center;
}

/* 代码提示 */
.code-hint {
  padding: 12px 16px;
  background: #ecf5ff;
  border-top: 1px solid #d9ecff;
}

.hint-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.hint-icon {
  font-size: 16px;
}

.hint-btn {
  margin-left: auto;
  padding: 4px 12px;
  background: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
}

.hint-btn:hover {
  background: #66b1ff;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .video-pane.float-mode {
    width: calc(100vw - 40px);
    max-width: none;
    right: 20px;
    left: 20px;
  }
  
  .video-header {
    flex-direction: column;
    gap: 10px;
    align-items: stretch;
  }
  
  .video-actions {
    justify-content: center;
    flex-wrap: wrap;
  }
  
  .video-title {
    text-align: center;
  }
  
  .action-btn {
    font-size: 11px;
    padding: 5px 8px;
  }
  
  .speed-menu {
    position: static;
    margin-top: 10px;
    box-shadow: none;
    border-top: 1px solid #ddd;
    border-bottom: 1px solid #ddd;
  }
  
  .video-progress {
    flex-direction: column;
    gap: 8px;
  }
  
  .time-display {
    min-width: auto;
  }
}
</style>
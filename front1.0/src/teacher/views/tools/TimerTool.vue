<template>
  <div class="timer-tool">
    <div class="timer-mode-selector">
      <button
        class="mode-btn"
        :class="{ active: timerMode === 'countdown' }"
        @click="timerMode = 'countdown'"
      >
        ⏱️ 倒计时
      </button>
      <button
        class="mode-btn"
        :class="{ active: timerMode === 'stopwatch' }"
        @click="timerMode = 'stopwatch'"
      >
        ⏱️ 秒表
      </button>
      <button
        class="mode-btn"
        :class="{ active: timerMode === 'alarm' }"
        @click="timerMode = 'alarm'"
      >
        🔔 闹钟
      </button>
    </div>

    <div v-if="timerMode === 'countdown'" class="countdown-section">
      <div class="time-display">
        <div class="time-circle" :class="{ warning: remainingTime <= 60 && remainingTime > 10, danger: remainingTime <= 10 }">
          <svg viewBox="0 0 200 200">
            <circle class="time-bg" cx="100" cy="100" r="90" />
            <circle
              class="time-progress"
              cx="100"
              cy="100"
              r="90"
              :stroke-dasharray="565.48"
              :stroke-dashoffset="565.48 - (remainingTime / totalTime) * 565.48"
            />
          </svg>
          <div class="time-text">
            <span class="hours">{{ formatTime(Math.floor(remainingTime / 3600)) }}</span>
            <span class="separator">:</span>
            <span class="minutes">{{ formatTime(Math.floor((remainingTime % 3600) / 60)) }}</span>
            <span class="separator">:</span>
            <span class="seconds">{{ formatTime(remainingTime % 60) }}</span>
          </div>
        </div>
      </div>

      <div class="preset-buttons">
        <button class="preset-btn" @click="setPreset(5)">5分钟</button>
        <button class="preset-btn" @click="setPreset(10)">10分钟</button>
        <button class="preset-btn" @click="setPreset(15)">15分钟</button>
        <button class="preset-btn" @click="setPreset(30)">30分钟</button>
        <button class="preset-btn" @click="setPreset(45)">45分钟</button>
        <button class="preset-btn" @click="setPreset(60)">60分钟</button>
      </div>

      <div class="custom-time">
        <label>自定义时间</label>
        <div class="time-inputs">
          <div class="input-group">
            <input type="number" v-model.number="customHours" min="0" max="23" />
            <span class="unit">时</span>
          </div>
          <span class="separator">:</span>
          <div class="input-group">
            <input type="number" v-model.number="customMinutes" min="0" max="59" />
            <span class="unit">分</span>
          </div>
          <span class="separator">:</span>
          <div class="input-group">
            <input type="number" v-model.number="customSeconds" min="0" max="59" />
            <span class="unit">秒</span>
          </div>
          <button class="set-btn" @click="setCustomTime">设置</button>
        </div>
      </div>

      <div class="control-buttons">
        <button v-if="!isRunning" class="control-btn start" @click="startTimer">
          <span>▶️</span> 开始
        </button>
        <button v-else class="control-btn pause" @click="pauseTimer">
          <span>⏸️</span> 暂停
        </button>
        <button class="control-btn reset" @click="resetTimer">
          <span>🔄</span> 重置
        </button>
      </div>
    </div>

    <div v-if="timerMode === 'stopwatch'" class="stopwatch-section">
      <div class="time-display">
        <div class="time-circle">
          <svg viewBox="0 0 200 200">
            <circle class="time-bg" cx="100" cy="100" r="90" />
            <circle
              class="time-progress stopwatch"
              cx="100"
              cy="100" r="90"
              :stroke-dasharray="565.48"
              :stroke-dashoffset="565.48 - ((elapsedTime % 60) / 60) * 565.48"
            />
          </svg>
          <div class="time-text">
            <span class="hours">{{ formatTime(Math.floor(elapsedTime / 3600)) }}</span>
            <span class="separator">:</span>
            <span class="minutes">{{ formatTime(Math.floor((elapsedTime % 3600) / 60)) }}</span>
            <span class="separator">:</span>
            <span class="seconds">{{ formatTime(elapsedTime % 60) }}</span>
            <span class="milliseconds">.{{ formatMilliseconds(elapsedMs) }}</span>
          </div>
        </div>
      </div>

      <div class="lap-times" v-if="lapTimes.length > 0">
        <h4>圈数记录</h4>
        <div class="lap-list">
          <div
            v-for="(lap, index) in lapTimes.slice().reverse()"
            :key="index"
            class="lap-item"
          >
            <span class="lap-number">#{{ lapTimes.length - index }}</span>
            <span class="lap-time">{{ formatLapTime(lap) }}</span>
          </div>
        </div>
      </div>

      <div class="control-buttons">
        <button v-if="!isRunning" class="control-btn start" @click="startStopwatch">
          <span>▶️</span> 开始
        </button>
        <button v-else class="control-btn pause" @click="pauseStopwatch">
          <span>⏸️</span> 暂停
        </button>
        <button class="control-btn lap" @click="recordLap" :disabled="!isRunning">
          <span>🏁</span> 计次
        </button>
        <button class="control-btn reset" @click="resetStopwatch">
          <span>🔄</span> 重置
        </button>
      </div>
    </div>

    <div v-if="timerMode === 'alarm'" class="alarm-section">
      <div class="alarm-icon">🔔</div>
      <div class="alarm-form">
        <div class="form-group">
          <label>设置时间</label>
          <input type="time" v-model="alarmTime" />
        </div>
        <div class="form-group">
          <label>重复</label>
          <select v-model="alarmRepeat">
            <option value="once">仅一次</option>
            <option value="daily">每天</option>
            <option value="weekday">工作日</option>
          </select>
        </div>
        <div class="form-group">
          <label>铃声</label>
          <select v-model="alarmSound">
            <option value="bell">清脆铃声</option>
            <option value="beep">蜂鸣声</option>
            <option value="melody">柔和旋律</option>
          </select>
        </div>
        <div class="form-group">
          <label>备注</label>
          <input type="text" v-model="alarmLabel" placeholder="输入提醒内容..." />
        </div>
      </div>
      <button class="set-alarm-btn" @click="setAlarm">
        <span>🔔</span> 设置闹钟
      </button>
      <div v-if="alarmSet" class="alarm-status">
        <span class="alarm-info">闹钟已设置: {{ alarmTime }}</span>
        <button class="cancel-alarm" @click="cancelAlarm">取消</button>
      </div>
    </div>

    <div v-if="isRunning" class="timer-sound-control">
      <button class="sound-btn" @click="toggleSound">
        <span>{{ soundEnabled ? '🔊' : '🔇' }}</span>
        {{ soundEnabled ? '声音已开启' : '声音已关闭' }}
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onUnmounted } from 'vue'

export default {
  name: 'TimerTool',
  setup() {
    const timerMode = ref('countdown')
    const isRunning = ref(false)
    const soundEnabled = ref(true)
    
    const totalTime = ref(300)
    const remainingTime = ref(300)
    
    const customHours = ref(0)
    const customMinutes = ref(5)
    const customSeconds = ref(0)
    
    const elapsedTime = ref(0)
    const elapsedMs = ref(0)
    const lapTimes = ref([])
    
    const alarmTime = ref('08:00')
    const alarmRepeat = ref('once')
    const alarmSound = ref('bell')
    const alarmLabel = ref('')
    const alarmSet = ref(false)

    let timerInterval = null
    let stopwatchInterval = null

    const formatTime = (num) => num.toString().padStart(2, '0')
    const formatMilliseconds = (num) => Math.floor(num / 10).toString().padStart(2, '0')

    const formatLapTime = (seconds) => {
      const mins = Math.floor(seconds / 60)
      const secs = seconds % 60
      return `${formatTime(mins)}:${formatTime(secs)}`
    }

    const setPreset = (minutes) => {
      totalTime.value = minutes * 60
      remainingTime.value = totalTime.value
      resetTimer()
    }

    const setCustomTime = () => {
      totalTime.value = customHours.value * 3600 + customMinutes.value * 60 + customSeconds.value
      remainingTime.value = totalTime.value
      resetTimer()
    }

    const startTimer = () => {
      isRunning.value = true
      timerInterval = setInterval(() => {
        if (remainingTime.value > 0) {
          remainingTime.value--
          if (remainingTime.value === 0 && soundEnabled.value) {
            alert('时间到！')
          }
        } else {
          pauseTimer()
        }
      }, 1000)
    }

    const pauseTimer = () => {
      isRunning.value = false
      if (timerInterval) {
        clearInterval(timerInterval)
        timerInterval = null
      }
    }

    const resetTimer = () => {
      pauseTimer()
      remainingTime.value = totalTime.value
    }

    const startStopwatch = () => {
      isRunning.value = true
      stopwatchInterval = setInterval(() => {
        elapsedMs.value += 10
        if (elapsedMs.value >= 1000) {
          elapsedMs.value = 0
          elapsedTime.value++
        }
      }, 10)
    }

    const pauseStopwatch = () => {
      isRunning.value = false
      if (stopwatchInterval) {
        clearInterval(stopwatchInterval)
        stopwatchInterval = null
      }
    }

    const recordLap = () => {
      lapTimes.value.push(elapsedTime.value)
    }

    const resetStopwatch = () => {
      pauseStopwatch()
      elapsedTime.value = 0
      elapsedMs.value = 0
      lapTimes.value = []
    }

    const setAlarm = () => {
      alarmSet.value = true
      alert('闹钟设置成功！')
    }

    const cancelAlarm = () => {
      alarmSet.value = false
    }

    const toggleSound = () => {
      soundEnabled.value = !soundEnabled.value
    }

    onUnmounted(() => {
      if (timerInterval) clearInterval(timerInterval)
      if (stopwatchInterval) clearInterval(stopwatchInterval)
    })

    return {
      timerMode,
      isRunning,
      soundEnabled,
      totalTime,
      remainingTime,
      customHours,
      customMinutes,
      customSeconds,
      elapsedTime,
      elapsedMs,
      lapTimes,
      alarmTime,
      alarmRepeat,
      alarmSound,
      alarmLabel,
      alarmSet,
      formatTime,
      formatMilliseconds,
      formatLapTime,
      setPreset,
      setCustomTime,
      startTimer,
      pauseTimer,
      resetTimer,
      startStopwatch,
      pauseStopwatch,
      recordLap,
      resetStopwatch,
      setAlarm,
      cancelAlarm,
      toggleSound
    }
  }
}
</script>

<style scoped>
.timer-tool {
  padding: 20px;
}

.timer-mode-selector {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-bottom: 32px;
}

.mode-btn {
  padding: 12px 28px;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
}

.mode-btn:hover {
  border-color: #3b82f6;
}

.mode-btn.active {
  background: #eff6ff;
  border-color: #3b82f6;
  color: #3b82f6;
}

.time-display {
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
}

.time-circle {
  position: relative;
  width: 280px;
  height: 280px;
}

.time-circle svg {
  transform: rotate(-90deg);
  width: 100%;
  height: 100%;
}

.time-bg {
  fill: none;
  stroke: #f1f5f9;
  stroke-width: 12;
}

.time-progress {
  fill: none;
  stroke: #3b82f6;
  stroke-width: 12;
  stroke-linecap: round;
  transition: stroke-dashoffset 0.5s ease, stroke 0.3s ease;
}

.time-progress.stopwatch {
  stroke: #22c55e;
}

.time-circle.warning .time-progress {
  stroke: #f59e0b;
}

.time-circle.danger .time-progress {
  stroke: #ef4444;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

.time-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.time-text .hours,
.time-text .minutes,
.time-text .seconds {
  font-size: 48px;
  font-weight: 700;
  color: #1e293b;
  font-family: 'SF Mono', 'Consolas', monospace;
}

.time-text .separator {
  font-size: 36px;
  color: #94a3b8;
  margin: 0 2px;
}

.time-text .milliseconds {
  font-size: 24px;
  color: #64748b;
  font-family: 'SF Mono', 'Consolas', monospace;
}

.preset-buttons {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.preset-btn {
  padding: 10px 20px;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 10px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.preset-btn:hover {
  background: #f8fafc;
  border-color: #3b82f6;
}

.custom-time {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.custom-time label {
  display: block;
  font-size: 14px;
  color: #64748b;
  margin-bottom: 12px;
}

.time-inputs {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.input-group {
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.input-group input {
  width: 50px;
  border: none;
  padding: 10px;
  font-size: 18px;
  text-align: center;
  outline: none;
}

.input-group .unit {
  padding: 10px;
  background: #f1f5f9;
  color: #64748b;
  font-size: 13px;
}

.time-inputs .separator {
  font-size: 24px;
  color: #94a3b8;
}

.set-btn {
  margin-left: 16px;
  padding: 10px 24px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.set-btn:hover {
  background: #2563eb;
}

.control-buttons {
  display: flex;
  justify-content: center;
  gap: 16px;
}

.control-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.control-btn.start {
  background: linear-gradient(135deg, #22c55e, #16a34a);
  color: white;
}

.control-btn.start:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(34, 197, 94, 0.4);
}

.control-btn.pause {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: white;
}

.control-btn.lap {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
}

.control-btn.lap:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-btn.reset {
  background: white;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.control-btn.reset:hover {
  background: #f8fafc;
}

.lap-times {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.lap-times h4 {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 12px;
}

.lap-list {
  max-height: 200px;
  overflow-y: auto;
}

.lap-item {
  display: flex;
  justify-content: space-between;
  padding: 10px 14px;
  background: white;
  border-radius: 8px;
  margin-bottom: 8px;
}

.lap-number {
  color: #64748b;
  font-size: 14px;
}

.lap-time {
  font-family: 'SF Mono', 'Consolas', monospace;
  font-weight: 500;
  color: #1e293b;
}

.alarm-section {
  text-align: center;
  padding: 20px;
}

.alarm-icon {
  font-size: 80px;
  margin-bottom: 24px;
}

.alarm-form {
  max-width: 400px;
  margin: 0 auto 24px;
  background: #f8fafc;
  border-radius: 12px;
  padding: 24px;
}

.form-group {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.form-group:last-child {
  margin-bottom: 0;
}

.form-group label {
  width: 80px;
  text-align: left;
  font-size: 14px;
  color: #64748b;
}

.form-group input[type="time"],
.form-group input[type="text"],
.form-group select {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}

.form-group input:focus,
.form-group select:focus {
  border-color: #3b82f6;
}

.set-alarm-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 14px 32px;
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.set-alarm-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
}

.alarm-status {
  margin-top: 24px;
  padding: 16px 24px;
  background: #dcfce7;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  gap: 16px;
}

.alarm-info {
  color: #166534;
  font-size: 14px;
}

.cancel-alarm {
  padding: 6px 14px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 13px;
  cursor: pointer;
}

.timer-sound-control {
  margin-top: 24px;
  text-align: center;
}

.sound-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  color: #64748b;
  cursor: pointer;
}

@media (max-width: 768px) {
  .timer-mode-selector {
    flex-direction: column;
  }

  .time-circle {
    width: 220px;
    height: 220px;
  }

  .time-text .hours,
  .time-text .minutes,
  .time-text .seconds {
    font-size: 36px;
  }

  .control-buttons {
    flex-wrap: wrap;
  }
}
</style>

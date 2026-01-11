<template>
  <div class="password-generator">
    <div class="tool-header">
      <h2>密码生成器</h2>
      <p>生成安全密码，支持多种字符组合和密码强度检测</p>
    </div>

    <div class="generator-container">
      <div class="main-panel">
        <div class="generated-password">
          <div class="password-display">
            <input
              type="text"
              :value="generatedPassword"
              readonly
              ref="passwordInput"
            />
            <button class="toggle-visibility" @click="toggleVisibility">
              {{ showPassword ? '👁️' : '👁️‍🗨️' }}
            </button>
          </div>
          <div class="password-actions">
            <button class="action-btn" @click="copyPassword">
              <span>{{ copied ? '✓ 已复制' : '📋 复制' }}</span>
            </button>
            <button class="action-btn" @click="generatePassword">
              <span>🔄 重新生成</span>
            </button>
          </div>
        </div>

        <div class="strength-indicator">
          <div class="strength-bar">
            <div
              class="strength-fill"
              :class="strengthClass"
              :style="{ width: strengthPercentage + '%' }"
            ></div>
          </div>
          <div class="strength-info">
            <span class="strength-label">密码强度: {{ strengthLabel }}</span>
            <span class="strength-detail">{{ strengthDetail }}</span>
          </div>
        </div>

        <div class="configuration-section">
          <h3>密码设置</h3>

          <div class="config-group">
            <label>密码长度</label>
            <div class="length-control">
              <input
                type="range"
                v-model.number="passwordLength"
                min="4"
                max="64"
                @input="generatePassword"
              />
              <span class="length-value">{{ passwordLength }} 位</span>
            </div>
          </div>

          <div class="config-group">
            <label>字符类型</label>
            <div class="char-types">
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="includeUppercase"
                  @change="generatePassword"
                />
                <span class="checkbox-custom"></span>
                <span>大写字母 (A-Z)</span>
                <span class="char-sample">ABC</span>
              </label>
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="includeLowercase"
                  @change="generatePassword"
                />
                <span class="checkbox-custom"></span>
                <span>小写字母 (a-z)</span>
                <span class="char-sample">abc</span>
              </label>
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="includeNumbers"
                  @change="generatePassword"
                />
                <span class="checkbox-custom"></span>
                <span>数字 (0-9)</span>
                <span class="char-sample">123</span>
              </label>
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="includeSymbols"
                  @change="generatePassword"
                />
                <span class="checkbox-custom"></span>
                <span>特殊符号 (!@#$)</span>
                <span class="char-sample">!@#</span>
              </label>
            </div>
          </div>

          <div class="config-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="avoidAmbiguous" @change="generatePassword" />
              <span class="checkbox-custom"></span>
              <span>避免歧义字符 (如 0/O, 1/l)</span>
            </label>
          </div>

          <div class="config-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="includeSpaces" @change="generatePassword" />
              <span class="checkbox-custom"></span>
              <span>包含空格</span>
            </label>
          </div>

          <div class="config-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="memorableMode" @change="generatePassword" />
              <span class="checkbox-custom"></span>
              <span>易记模式 (使用常用单词)</span>
            </label>
          </div>
        </div>

        <div class="preset-passwords">
          <h3>常用密码类型</h3>
          <div class="preset-grid">
            <button class="preset-btn" @click="usePreset('simple')">
              <span class="preset-icon">🔑</span>
              <span class="preset-name">简单密码</span>
              <span class="preset-desc">8位，仅字母数字</span>
            </button>
            <button class="preset-btn" @click="usePreset('medium')">
              <span class="preset-icon">🔐</span>
              <span class="preset-name">中等强度</span>
              <span class="preset-desc">12位，含大小写数字</span>
            </button>
            <button class="preset-btn" @click="usePreset('strong')">
              <span class="preset-icon">🛡️</span>
              <span class="preset-name">高强度</span>
              <span class="preset-desc">16位，含特殊符号</span>
            </button>
            <button class="preset-btn" @click="usePreset('pin')">
              <span class="preset-icon">🔢</span>
              <span class="preset-name">数字PIN码</span>
              <span class="preset-desc">纯数字，4-6位</span>
            </button>
          </div>
        </div>
      </div>

      <div class="side-panel">
        <div class="entropy-section">
          <h3>密码熵值</h3>
          <div class="entropy-display">
            <div class="entropy-circle" :class="entropyClass">
              <span class="entropy-value">{{ entropyValue.toFixed(1) }}</span>
              <span class="entropy-label">bits</span>
            </div>
            <div class="entropy-info">
              <p>熵值越高，密码越安全</p>
              <div class="entropy-legend">
                <div class="legend-item">
                  <span class="legend-dot weak"></span>
                  <span>弱 (&lt; 40)</span>
                </div>
                <div class="legend-item">
                  <span class="legend-dot medium"></span>
                  <span>中等 (40-60)</span>
                </div>
                <div class="legend-item">
                  <span class="legend-dot strong"></span>
                  <span>强 (60-80)</span>
                </div>
                <div class="legend-item">
                  <span class="legend-dot excellent"></span>
                  <span>极强 (&gt; 80)</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="crack-time-section">
          <h3>破解时间估算</h3>
          <div class="crack-time-display">
            <div class="time-item">
              <span class="time-icon">⚡</span>
              <span class="time-value">{{ crackTime.fast }}</span>
              <span class="time-label">快速攻击</span>
            </div>
            <div class="time-item">
              <span class="time-icon">🐢</span>
              <span class="time-value">{{ crackTime.slow }}</span>
              <span class="time-label">慢速攻击</span>
            </div>
          </div>
        </div>

        <div class="password-history">
          <div class="history-header">
            <h3>生成历史</h3>
            <button
              v-if="passwordHistory.length > 0"
              class="clear-btn"
              @click="clearHistory"
            >
              清空
            </button>
          </div>
          <div class="history-list">
            <div v-if="passwordHistory.length === 0" class="empty-history">
              <span>📝</span>
              <p>暂无生成记录</p>
            </div>
            <div
              v-for="(item, index) in passwordHistory"
              :key="index"
              class="history-item"
            >
              <div class="history-password">
                <span class="masked" v-if="!item.show">{{ maskPassword(item.password) }}</span>
                <span v-else>{{ item.password }}</span>
                <button class="toggle-btn" @click="toggleShowHistory(index)">
                  {{ item.show ? '👁️' : '👁️‍🗨️' }}
                </button>
                <button class="copy-history-btn" @click="copyHistoryPassword(item.password)">
                  📋
                </button>
              </div>
              <div class="history-meta">
                <span class="history-strength" :class="getStrengthClass(item.strength)">
                  {{ item.strength }}
                </span>
                <span class="history-time">{{ formatTime(item.time) }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="tips-section">
          <h3>安全建议</h3>
          <ul class="tips-list">
            <li>使用12位以上的密码</li>
            <li>混合大小写、数字和符号</li>
            <li>避免使用个人信息</li>
            <li>定期更换重要密码</li>
            <li>不同网站使用不同密码</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'

export default {
  name: 'PasswordGenerator',
  setup() {
    const passwordLength = ref(16)
    const includeUppercase = ref(true)
    const includeLowercase = ref(true)
    const includeNumbers = ref(true)
    const includeSymbols = ref(true)
    const avoidAmbiguous = ref(false)
    const includeSpaces = ref(false)
    const memorableMode = ref(false)
    const showPassword = ref(true)
    const generatedPassword = ref('')
    const copied = ref(false)
    const passwordHistory = ref([])
    const passwordInput = ref(null)

    const uppercaseChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    const lowercaseChars = 'abcdefghijklmnopqrstuvwxyz'
    const numberChars = '0123456789'
    const symbolChars = '!@#$%^&*()_+-=[]{}|;:,.<>?'
    const ambiguousChars = '0O1lI'

    const commonWords = [
      'apple', 'brave', 'cloud', 'dance', 'eagle', 'flame', 'green', 'happy',
      'image', 'jolly', 'knight', 'lemon', 'music', 'night', 'ocean', 'piano',
      'queen', 'river', 'sunny', 'tiger', 'unity', 'voice', 'water', 'xray',
      'young', 'zebra', 'beach', 'crane', 'dream', 'earth', 'frost', 'grace',
      'heart', 'index', 'joker', 'kite', 'light', 'magic', 'north', 'orbit',
      'power', 'quest', 'radio', 'storm', 'train', 'ultra', 'vivid', 'world'
    ]

    const strengthClass = computed(() => {
      const strength = calculateStrength()
      if (strength < 2) return 'weak'
      if (strength < 3) return 'fair'
      if (strength < 4) return 'good'
      return 'strong'
    })

    const strengthLabel = computed(() => {
      const strength = calculateStrength()
      if (strength < 2) return '弱'
      if (strength < 3) return '一般'
      if (strength < 4) return '良好'
      return '强'
    })

    const strengthDetail = computed(() => {
      const strength = calculateStrength()
      if (strength < 2) return '容易被破解'
      if (strength < 3) return '建议增加长度或字符类型'
      if (strength < 4) return '较为安全'
      return '安全性高'
    })

    const strengthPercentage = computed(() => {
      return Math.min(100, calculateStrength() * 25)
    })

    const entropyValue = computed(() => {
      let charsetSize = 0
      if (includeLowercase.value) charsetSize += 26
      if (includeUppercase.value) charsetSize += 26
      if (includeNumbers.value) charsetSize += 10
      if (includeSymbols.value) charsetSize += 32
      if (includeSpaces.value) charsetSize += 1

      if (charsetSize === 0) return 0

      let entropy = passwordLength.value * Math.log2(charsetSize)
      if (avoidAmbiguous.value) {
        entropy *= 0.9
      }
      return entropy
    })

    const entropyClass = computed(() => {
      const entropy = entropyValue.value
      if (entropy < 40) return 'weak'
      if (entropy < 60) return 'medium'
      if (entropy < 80) return 'strong'
      return 'excellent'
    })

    const crackTime = computed(() => {
      const entropy = entropyValue.value
      const combinations = Math.pow(2, entropy)

      const fastRate = 1e10
      const slowRate = 1e6

      const fastSeconds = combinations / fastRate
      const slowSeconds = combinations / slowRate

      return {
        fast: formatDuration(fastSeconds),
        slow: formatDuration(slowSeconds)
      }
    })

    const formatDuration = (seconds) => {
      if (seconds < 0.000001) return '瞬间'
      if (seconds < 0.001) return '毫秒级'
      if (seconds < 1) return '不足1秒'
      if (seconds < 60) return `${Math.round(seconds)} 秒`
      if (seconds < 3600) return `${Math.round(seconds / 60)} 分钟`
      if (seconds < 86400) return `${Math.round(seconds / 3600)} 小时`
      if (seconds < 2592000) return `${Math.round(seconds / 86400)} 天`
      if (seconds < 31536000) return `${Math.round(seconds / 2592000)} 月`
      if (seconds < 31536000000) return `${Math.round(seconds / 31536000)} 年`
      return `${Math.round(seconds / 31536000000)} 万年`
    }

    const calculateStrength = () => {
      let strength = 0
      const len = passwordLength.value

      if (len >= 8) strength += 0.5
      if (len >= 12) strength += 0.5
      if (len >= 16) strength += 0.5
      if (len >= 20) strength += 0.5

      if (includeUppercase.value) strength += 0.5
      if (includeLowercase.value) strength += 0.5
      if (includeNumbers.value) strength += 0.5
      if (includeSymbols.value) strength += 0.5

      if (includeUppercase.value && includeLowercase.value) strength += 0.5
      if (includeNumbers.value && (includeUppercase.value || includeLowercase.value)) strength += 0.5
      if (includeSymbols.value) strength += 0.5

      if (avoidAmbiguous.value) strength += 0.25

      return Math.min(4, strength)
    }

    const getCharacterPool = () => {
      let pool = ''
      if (includeLowercase.value) pool += lowercaseChars
      if (includeUppercase.value) pool += uppercaseChars
      if (includeNumbers.value) pool += numberChars
      if (includeSymbols.value) pool += symbolChars
      if (includeSpaces.value) pool += ' '

      if (avoidAmbiguous.value) {
        pool = pool.split('').filter(c => !ambiguousChars.includes(c)).join('')
      }

      return pool
    }

    const generatePassword = () => {
      if (memorableMode.value) {
        generatedPassword.value = generateMemorablePassword()
      } else {
        const pool = getCharacterPool()
        if (pool === '') {
          generatedPassword.value = '请选择字符类型'
          return
        }

        let password = ''
        const array = new Uint32Array(passwordLength.value)
        crypto.getRandomValues(array)

        for (let i = 0; i < passwordLength.value; i++) {
          password += pool[array[i] % pool.length]
        }

        generatedPassword.value = password
      }

      addToHistory()
    }

    const generateMemorablePassword = () => {
      let password = ''
      const words = []

      for (let i = 0; i < 4; i++) {
        const randomIndex = Math.floor(Math.random() * commonWords.length)
        words.push(commonWords[randomIndex])
      }

      const separators = ['-', '.', '_', '+', '=', '#']
      const separator = separators[Math.floor(Math.random() * separators.length)]

      const useCamelCase = Math.random() > 0.5
      const useNumber = Math.random() > 0.7

      password = words.map((word, index) => {
        let formatted = word
        if (index === 0 && useCamelCase) {
          formatted = (word || '').charAt(0).toUpperCase() + (word || '').slice(1)
        }
        if (useNumber && index === 0) {
          formatted += Math.floor(Math.random() * 10)
        }
        return formatted
      }).join(separator)

      if (Math.random() > 0.5) {
        const randomSymbol = symbolChars[Math.floor(Math.random() * symbolChars.length)]
        password += randomSymbol + Math.floor(Math.random() * 100)
      }

      return password
    }

    const usePreset = (preset) => {
      switch (preset) {
        case 'simple':
          passwordLength.value = 8
          includeUppercase.value = true
          includeLowercase.value = true
          includeNumbers.value = true
          includeSymbols.value = false
          break
        case 'medium':
          passwordLength.value = 12
          includeUppercase.value = true
          includeLowercase.value = true
          includeNumbers.value = true
          includeSymbols.value = false
          break
        case 'strong':
          passwordLength.value = 16
          includeUppercase.value = true
          includeLowercase.value = true
          includeNumbers.value = true
          includeSymbols.value = true
          break
        case 'pin':
          passwordLength.value = 6
          includeUppercase.value = false
          includeLowercase.value = false
          includeNumbers.value = true
          includeSymbols.value = false
          break
      }
      generatePassword()
    }

    const toggleVisibility = () => {
      showPassword.value = !showPassword.value
    }

    const copyPassword = () => {
      navigator.clipboard.writeText(generatedPassword.value).then(() => {
        copied.value = true
        setTimeout(() => {
          copied.value = false
        }, 2000)
      })
    }

    const addToHistory = () => {
      const strength = strengthLabel.value
      const historyItem = {
        password: generatedPassword.value,
        strength: strength,
        time: new Date(),
        show: false
      }

      passwordHistory.value.unshift(historyItem)
      if (passwordHistory.value.length > 10) {
        passwordHistory.value.pop()
      }
    }

    const clearHistory = () => {
      passwordHistory.value = []
    }

    const toggleShowHistory = (index) => {
      passwordHistory.value[index].show = !passwordHistory.value[index].show
    }

    const copyHistoryPassword = (password) => {
      navigator.clipboard.writeText(password)
    }

    const maskPassword = (password) => {
      if (password.length <= 4) return '*'.repeat(password.length)
      return password.substring(0, 2) + '*'.repeat(password.length - 4) + password.substring(password.length - 2)
    }

    const getStrengthClass = (strength) => {
      const classes = {
        '弱': 'weak',
        '一般': 'fair',
        '良好': 'good',
        '强': 'strong'
      }
      return classes[strength] || ''
    }

    const formatTime = (date) => {
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    onMounted(() => {
      generatePassword()
    })

    return {
      passwordLength,
      includeUppercase,
      includeLowercase,
      includeNumbers,
      includeSymbols,
      avoidAmbiguous,
      includeSpaces,
      memorableMode,
      showPassword,
      generatedPassword,
      copied,
      passwordHistory,
      passwordInput,
      strengthClass,
      strengthLabel,
      strengthDetail,
      strengthPercentage,
      entropyValue,
      entropyClass,
      crackTime,
      generatePassword,
      usePreset,
      toggleVisibility,
      copyPassword,
      clearHistory,
      toggleShowHistory,
      copyHistoryPassword,
      maskPassword,
      getStrengthClass,
      formatTime
    }
  }
}
</script>

<style scoped>
.password-generator {
  background: #fff;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.tool-header {
  text-align: center;
  margin-bottom: 24px;
}

.tool-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0 0 8px;
}

.tool-header p {
  color: #888;
  font-size: 14px;
  margin: 0;
}

.generator-container {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
}

.main-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.generated-password {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
}

.password-display {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.password-display input {
  flex: 1;
  padding: 16px 20px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 18px;
  font-family: 'Courier New', monospace;
  font-weight: 500;
  background: #fff;
  letter-spacing: 2px;
}

.password-display input:focus {
  outline: none;
  border-color: #2196f3;
}

.toggle-visibility {
  width: 52px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  background: #fff;
  cursor: pointer;
  font-size: 20px;
  transition: all 0.2s;
}

.toggle-visibility:hover {
  background: #f5f5f5;
}

.password-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  flex: 1;
  padding: 12px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.action-btn:first-child {
  background: #e3f2fd;
  color: #1976d2;
}

.action-btn:first-child:hover {
  background: #bbdefb;
}

.action-btn:last-child {
  background: #f5f5f5;
  color: #333;
}

.action-btn:last-child:hover {
  background: #e8e8e8;
}

.strength-indicator {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px 20px;
}

.strength-bar {
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 12px;
}

.strength-fill {
  height: 100%;
  border-radius: 4px;
  transition: all 0.3s ease;
}

.strength-fill.weak {
  background: linear-gradient(90deg, #f44336, #ff5722);
  width: 25%;
}

.strength-fill.fair {
  background: linear-gradient(90deg, #ff9800, #ffc107);
  width: 50%;
}

.strength-fill.good {
  background: linear-gradient(90deg, #2196f3, #4caf50);
  width: 75%;
}

.strength-fill.strong {
  background: linear-gradient(90deg, #4caf50, #8bc34a);
  width: 100%;
}

.strength-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.strength-label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.strength-detail {
  font-size: 13px;
  color: #888;
}

.configuration-section {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
}

.configuration-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px;
}

.config-group {
  margin-bottom: 20px;
}

.config-group > label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #333;
  margin-bottom: 12px;
}

.length-control {
  display: flex;
  align-items: center;
  gap: 16px;
}

.length-control input[type="range"] {
  flex: 1;
  height: 8px;
  border-radius: 4px;
  background: #e0e0e0;
  appearance: none;
  cursor: pointer;
}

.length-control input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: #2196f3;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.4);
}

.length-value {
  min-width: 60px;
  font-size: 16px;
  font-weight: 600;
  color: #2196f3;
  text-align: right;
}

.char-types {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 10px 12px;
  background: #fff;
  border-radius: 8px;
  font-size: 13px;
  color: #333;
  transition: background 0.2s;
}

.checkbox-label:hover {
  background: #f0f0f0;
}

.checkbox-label input {
  display: none;
}

.checkbox-custom {
  width: 20px;
  height: 20px;
  border: 2px solid #d0d0d0;
  border-radius: 4px;
  position: relative;
  flex-shrink: 0;
  transition: all 0.2s;
}

.checkbox-label input:checked + .checkbox-custom {
  background: #2196f3;
  border-color: #2196f3;
}

.checkbox-label input:checked + .checkbox-custom::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: #fff;
  font-size: 12px;
  font-weight: bold;
}

.char-sample {
  margin-left: auto;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: #888;
  background: #f5f5f5;
  padding: 2px 8px;
  border-radius: 4px;
}

.preset-passwords {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
}

.preset-passwords h3 {
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0 0 16px;
}

.preset-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.preset-btn {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 16px;
  border: 2px solid #e0e0e0;
  background: #fff;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.preset-btn:hover {
  border-color: #2196f3;
  background: #e3f2fd;
}

.preset-icon {
  font-size: 24px;
  margin-bottom: 8px;
}

.preset-name {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.preset-desc {
  font-size: 12px;
  color: #888;
}

.side-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.side-panel > div {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
}

.side-panel h3 {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px;
}

.entropy-display {
  display: flex;
  align-items: center;
  gap: 16px;
}

.entropy-circle {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s;
}

.entropy-circle.weak {
  background: linear-gradient(135deg, #f44336, #ff5722);
}

.entropy-circle.medium {
  background: linear-gradient(135deg, #ff9800, #ffc107);
}

.entropy-circle.strong {
  background: linear-gradient(135deg, #2196f3, #4caf50);
}

.entropy-circle.excellent {
  background: linear-gradient(135deg, #4caf50, #8bc34a);
}

.entropy-value {
  font-size: 24px;
  font-weight: 700;
  color: #fff;
}

.entropy-label {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.9);
}

.entropy-info {
  flex: 1;
}

.entropy-info p {
  font-size: 13px;
  color: #666;
  margin: 0 0 12px;
}

.entropy-legend {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: #666;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.legend-dot.weak {
  background: #f44336;
}

.legend-dot.medium {
  background: #ff9800;
}

.legend-dot.strong {
  background: #4caf50;
}

.legend-dot.excellent {
  background: #8bc34a;
}

.crack-time-display {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.time-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fff;
  border-radius: 8px;
}

.time-icon {
  font-size: 20px;
}

.time-value {
  flex: 1;
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.time-label {
  font-size: 12px;
  color: #888;
}

.password-history {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.history-header h3 {
  margin: 0;
}

.clear-btn {
  padding: 4px 10px;
  border: none;
  background: #ffebee;
  color: #f44336;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: #ffcdd2;
}

.history-list {
  max-height: 300px;
  overflow-y: auto;
}

.empty-history {
  text-align: center;
  padding: 30px 20px;
  color: #888;
}

.empty-history span {
  font-size: 32px;
  display: block;
  margin-bottom: 8px;
}

.empty-history p {
  margin: 0;
  font-size: 13px;
}

.history-item {
  background: #fff;
  border-radius: 8px;
  padding: 12px;
  margin-bottom: 8px;
}

.history-password {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.masked {
  flex: 1;
  letter-spacing: 2px;
}

.toggle-btn,
.copy-history-btn {
  width: 28px;
  height: 28px;
  border: none;
  background: #f5f5f5;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.toggle-btn:hover,
.copy-history-btn:hover {
  background: #e8e8e8;
}

.history-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.history-strength {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.history-strength.weak {
  background: #ffebee;
  color: #f44336;
}

.history-strength.fair {
  background: #fff3e0;
  color: #ff9800;
}

.history-strength.good {
  background: #e3f2fd;
  color: #2196f3;
}

.history-strength.strong {
  background: #e8f5e9;
  color: #4caf50;
}

.history-time {
  font-size: 11px;
  color: #888;
}

.tips-section {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
}

.tips-section h3 {
  margin: 0 0 12px;
}

.tips-list {
  margin: 0;
  padding-left: 20px;
}

.tips-list li {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.tips-list li:last-child {
  margin-bottom: 0;
}

@media (max-width: 1000px) {
  .generator-container {
    grid-template-columns: 1fr;
  }

  .char-types {
    grid-template-columns: 1fr;
  }

  .preset-grid {
    grid-template-columns: 1fr;
  }
}
</style>

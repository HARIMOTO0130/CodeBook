<template>
  <div class="qrcode-generator">
    <div class="tool-header">
      <h2>二维码生成器</h2>
      <p>快速生成教学资源二维码，支持多种自定义选项</p>
    </div>

    <div class="generator-container">
      <div class="generator-main">
        <div class="input-section">
          <div class="section-card">
            <h3>内容输入</h3>
            <div class="content-type-selector">
              <button
                v-for="type in contentTypes"
                :key="type.id"
                class="type-btn"
                :class="{ active: contentType === type.id }"
                @click="contentType = type.id"
              >
                <span class="type-icon">{{ type.icon }}</span>
                <span class="type-name">{{ type.name }}</span>
              </button>
            </div>

            <div v-if="contentType === 'text'" class="form-group">
              <label>文本内容</label>
              <textarea
                v-model="qrContent.text"
                placeholder="输入要转换的文本内容"
                rows="4"
              ></textarea>
            </div>

            <div v-if="contentType === 'url'" class="form-group">
              <label>网址链接</label>
              <input
                type="url"
                v-model="qrContent.url"
                placeholder="https://example.com"
              />
            </div>

            <div v-if="contentType === 'wifi'" class="wifi-form">
              <div class="form-group">
                <label>网络名称（SSID）</label>
                <input
                  type="text"
                  v-model="qrContent.wifi.ssid"
                  placeholder="输入WiFi名称"
                />
              </div>
              <div class="form-group">
                <label>密码</label>
                <input
                  type="password"
                  v-model="qrContent.wifi.password"
                  placeholder="输入WiFi密码"
                />
              </div>
              <div class="form-group">
                <label>加密类型</label>
                <select v-model="qrContent.wifi.encryption">
                  <option value="WPA">WPA/WPA2</option>
                  <option value="WEP">WEP</option>
                  <option value="nopass">无密码</option>
                </select>
              </div>
              <div class="form-group checkbox-group">
                <label>
                  <input type="checkbox" v-model="qrContent.wifi.hidden" />
                  隐藏网络
                </label>
              </div>
            </div>

            <div v-if="contentType === 'vcard'" class="vcard-form">
              <div class="form-row">
                <div class="form-group">
                  <label>姓名</label>
                  <input
                    type="text"
                    v-model="qrContent.vcard.lastName"
                    placeholder="姓"
                  />
                </div>
                <div class="form-group">
                  <label>名字</label>
                  <input
                    type="text"
                    v-model="qrContent.vcard.firstName"
                    placeholder="名"
                  />
                </div>
              </div>
              <div class="form-group">
                <label>手机</label>
                <input
                  type="tel"
                  v-model="qrContent.vcard.phone"
                  placeholder="138xxxxxxxx"
                />
              </div>
              <div class="form-group">
                <label>邮箱</label>
                <input
                  type="email"
                  v-model="qrContent.vcard.email"
                  placeholder="email@example.com"
                />
              </div>
              <div class="form-group">
                <label>职位</label>
                <input
                  type="text"
                  v-model="qrContent.vcard.title"
                  placeholder="教师/教授"
                />
              </div>
              <div class="form-group">
                <label>学校/机构</label>
                <input
                  type="text"
                  v-model="qrContent.vcard.org"
                  placeholder="学校名称"
                />
              </div>
              <div class="form-group">
                <label>个人网站</label>
                <input
                  type="url"
                  v-model="qrContent.vcard.url"
                  placeholder="https://"
                />
              </div>
            </div>

            <div v-if="contentType === 'email'" class="form-group">
              <label>邮箱地址</label>
              <input
                type="email"
                v-model="qrContent.email"
                placeholder="recipient@example.com"
              />
              <div class="form-group">
                <label>主题</label>
                <input
                  type="text"
                  v-model="qrContent.emailSubject"
                  placeholder="邮件主题"
                />
              </div>
              <div class="form-group">
                <label>内容</label>
                <textarea
                  v-model="qrContent.emailBody"
                  placeholder="邮件正文"
                  rows="3"
                ></textarea>
              </div>
            </div>

            <div v-if="contentType === 'phone'" class="form-group">
              <label>电话号码</label>
              <input
                type="tel"
                v-model="qrContent.phone"
                placeholder="138xxxxxxxx"
              />
            </div>
          </div>

          <div class="section-card">
            <h3>样式设置</h3>
            <div class="style-controls">
              <div class="form-group">
                <label>二维码尺寸</label>
                <div class="size-slider">
                  <input
                    type="range"
                    v-model.number="qrSettings.size"
                    min="100"
                    max="500"
                    step="10"
                  />
                  <span class="size-value">{{ qrSettings.size }}px</span>
                </div>
              </div>

              <div class="form-group">
                <label>纠错等级</label>
                <div class="error-level-selector">
                  <button
                    v-for="level in errorLevels"
                    :key="level.level"
                    class="level-btn"
                    :class="{ active: qrSettings.errorLevel === level.level }"
                    @click="qrSettings.errorLevel = level.level"
                    :title="level.description"
                  >
                    <span class="level-name">{{ level.level }}</span>
                    <span class="level-info">{{ level.info }}</span>
                  </button>
                </div>
              </div>

              <div class="color-row">
                <div class="form-group">
                  <label>前景色</label>
                  <div class="color-picker-wrapper">
                    <input
                      type="color"
                      v-model="qrSettings.foreground"
                      class="color-input"
                    />
                    <input
                      type="text"
                      v-model="qrSettings.foreground"
                      class="color-text"
                    />
                  </div>
                </div>
                <div class="form-group">
                  <label>背景色</label>
                  <div class="color-picker-wrapper">
                    <input
                      type="color"
                      v-model="qrSettings.background"
                      class="color-input"
                    />
                    <input
                      type="text"
                      v-model="qrSettings.background"
                      class="color-text"
                    />
                  </div>
                </div>
              </div>

              <div class="form-group checkbox-group">
                <label>
                  <input type="checkbox" v-model="qrSettings.includeMargin" />
                  包含白色边距
                </label>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="generator-sidebar">
        <div class="preview-card">
          <h4>预览效果</h4>
          <div class="qr-preview">
            <canvas ref="qrCanvas" v-show="generatedQR"></canvas>
            <div v-if="!generatedQR" class="placeholder">
              <span>输入内容后生成二维码</span>
            </div>
          </div>
          <div class="preview-actions">
            <button
              class="generate-btn"
              @click="generateQRCode"
              :disabled="!canGenerate"
            >
              <span>🔄 生成二维码</span>
            </button>
          </div>
        </div>

        <div class="download-card">
          <h4>下载选项</h4>
          <div class="download-options">
            <div class="format-selector">
              <label>图片格式</label>
              <select v-model="downloadFormat">
                <option value="png">PNG（推荐）</option>
                <option value="jpeg">JPEG</option>
                <option value="svg">SVG（矢量图）</option>
              </select>
            </div>
            <button
              class="download-btn"
              @click="downloadQRCode"
              :disabled="!generatedQR"
            >
              <span>📥 下载二维码</span>
            </button>
          </div>
        </div>

        <div class="history-card">
          <div class="history-header">
            <h4>生成历史</h4>
            <button
              v-if="history.length > 0"
              class="clear-history-btn"
              @click="clearHistory"
            >
              清空
            </button>
          </div>
          <div class="history-list">
            <div
              v-for="item in history"
              :key="item.id"
              class="history-item"
              @click="loadFromHistory(item)"
            >
              <div class="history-icon">
                {{ getTypeIcon(item.type) }}
              </div>
              <div class="history-info">
                <span class="history-content">{{ truncateContent(item.content) }}</span>
                <span class="history-time">{{ formatTime(item.time) }}</span>
              </div>
            </div>
            <div v-if="history.length === 0" class="no-history">
              <p>暂无生成记录</p>
            </div>
          </div>
        </div>

        <div class="tips-card">
          <h4>使用提示</h4>
          <div class="tips-list">
            <div class="tip-item">
              <span class="tip-icon">📚</span>
              <span class="tip-text">可将课程资料链接生成二维码，分享给学生扫描访问</span>
            </div>
            <div class="tip-item">
              <span class="tip-icon">👥</span>
              <span class="tip-text">生成个人名片二维码，方便学生和家长联系</span>
            </div>
            <div class="tip-item">
              <span class="tip-icon">📶</span>
              <span class="tip-text">生成WiFi二维码，教室接入网络更便捷</span>
            </div>
            <div class="tip-item">
              <span class="tip-icon">💡</span>
              <span class="tip-text">建议使用高纠错等级，便于印刷和扫描</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'

export default {
  name: 'QRCodeGenerator',
  setup() {
    const qrCanvas = ref(null)
    const generatedQR = ref(false)
    const downloadFormat = ref('png')
    const history = ref([])

    const contentType = ref('url')

    const qrContent = ref({
      text: '',
      url: '',
      email: '',
      emailSubject: '',
      emailBody: '',
      phone: '',
      wifi: {
        ssid: '',
        password: '',
        encryption: 'WPA',
        hidden: false
      },
      vcard: {
        lastName: '',
        firstName: '',
        phone: '',
        email: '',
        title: '',
        org: '',
        url: ''
      }
    })

    const qrSettings = ref({
      size: 256,
      errorLevel: 'H',
      foreground: '#000000',
      background: '#ffffff',
      includeMargin: true
    })

    const contentTypes = [
      { id: 'url', name: '网址', icon: '🔗' },
      { id: 'text', name: '文本', icon: '📝' },
      { id: 'wifi', name: 'WiFi', icon: '📶' },
      { id: 'vcard', name: '名片', icon: '👤' },
      { id: 'email', name: '邮箱', icon: '📧' },
      { id: 'phone', name: '电话', icon: '📞' }
    ]

    const errorLevels = [
      { level: 'L', info: '7%', description: '低纠错，适合清晰打印' },
      { level: 'M', info: '15%', description: '中等纠错，日常使用' },
      { level: 'Q', info: '25%', description: '较高纠错，部分遮挡可用' },
      { level: 'H', info: '30%', description: '最高纠错，可损坏30%' }
    ]

    const getQRContent = computed(() => {
      switch (contentType.value) {
        case 'text':
          return qrContent.value.text
        case 'url':
          return qrContent.value.url
        case 'wifi':
          return `WIFI:T:${qrContent.value.wifi.encryption};S:${qrContent.value.wifi.ssid};P:${qrContent.value.wifi.password};${qrContent.value.wifi.hidden ? 'H:true;' : ''};`
        case 'vcard':
          return `BEGIN:VCARD
VERSION:3.0
N:${qrContent.value.vcard.lastName};${qrContent.value.vcard.firstName};;;
FN:${qrContent.value.vcard.lastName} ${qrContent.value.vcard.firstName}
ORG:${qrContent.value.vcard.org}
TITLE:${qrContent.value.vcard.title}
TEL:${qrContent.value.vcard.phone}
EMAIL:${qrContent.value.vcard.vcard?.email}
URL:${qrContent.value.vcard.url}
END:VCARD`
        case 'email':
          let mailto = `mailto:${qrContent.value.email}`
          const params = []
          if (qrContent.value.emailSubject) params.push(`subject=${encodeURIComponent(qrContent.value.emailSubject)}`)
          if (qrContent.value.emailBody) params.push(`body=${encodeURIComponent(qrContent.value.emailBody)}`)
          if (params.length > 0) mailto += '?' + params.join('&')
          return mailto
        case 'phone':
          return `tel:${qrContent.value.phone}`
        default:
          return ''
      }
    })

    const canGenerate = computed(() => {
      switch (contentType.value) {
        case 'text':
          return qrContent.value.text.trim().length > 0
        case 'url':
          return qrContent.value.url.trim().length > 0
        case 'wifi':
          return qrContent.value.wifi.ssid.trim().length > 0
        case 'vcard':
          return qrContent.value.vcard.lastName.trim().length > 0 ||
                 qrContent.value.vcard.firstName.trim().length > 0
        case 'email':
          return qrContent.value.email.trim().length > 0
        case 'phone':
          return qrContent.value.phone.trim().length > 0
        default:
          return false
      }
    })

    const generateQRCode = () => {
      if (!canGenerate.value) return

      const content = getQRContent.value
      if (!content) return

      try {
        const canvas = qrCanvas.value
        if (!canvas) return

        const ctx = canvas.getContext('2d')
        const size = qrSettings.value.size
        const errorLevelMap = { L: 1, M: 0, Q: 3, H: 2 }

        canvas.width = size
        canvas.height = size

        const qr = generateQRMatrix(content, errorLevelMap[qrSettings.value.errorLevel])

        const moduleCount = qr.length
        const moduleSize = size / moduleCount
        const margin = qrSettings.value.includeMargin ? moduleCount * 0.2 : 0
        const totalSize = size + margin * 2

        canvas.width = totalSize
        canvas.height = totalSize

        ctx.fillStyle = qrSettings.value.background
        ctx.fillRect(0, 0, totalSize, totalSize)

        ctx.fillStyle = qrSettings.value.foreground

        for (let row = 0; row < moduleCount; row++) {
          for (let col = 0; col < moduleCount; col++) {
            if (qr[row][col]) {
              const x = col * moduleSize + margin
              const y = row * moduleSize + margin
              ctx.fillRect(x, y, moduleSize, moduleSize)
            }
          }
        }

        drawFinderPatterns(ctx, moduleSize, margin, qrSettings.value.foreground)

        generatedQR.value = true
        addToHistory(content)
      } catch (error) {
        console.error('QR code generation failed:', error)
      }
    }

    const generateQRMatrix = (data, errorLevel) => {
      const version = calculateVersion(data.length, errorLevel)
      const size = version * 4 + 17
      const matrix = Array(size).fill(null).map(() => Array(size).fill(false))

      const addFinderPattern = (row, col) => {
        for (let r = 0; r < 7; r++) {
          for (let c = 0; c < 7; c++) {
            const isEdge = r === 0 || r === 6 || c === 0 || c === 6
            const isInner = r >= 2 && r <= 4 && c >= 2 && c <= 4
            if (isEdge && !isInner) {
              matrix[row + r][col + c] = true
            } else if (!isEdge && !isInner) {
              matrix[row + r][col + c] = false
            } else {
              matrix[row + r][col + c] = true
            }
          }
        }
        for (let i = 0; i < 8; i++) {
          if (i !== 0 && i !== 6) {
            matrix[row + i][col] = true
            matrix[row + i][col + 6] = true
            matrix[row][col + i] = true
            matrix[row + 6][col + i] = true
          }
        }
      }

      addFinderPattern(0, 0)
      addFinderPattern(0, size - 7)
      addFinderPattern(size - 7, 0)

      const timingPattern = (pos) => {
        for (let i = 8; i < size - 8; i++) {
          const value = i % 2 === 0
          matrix[pos][i] = value
          matrix[i][pos] = value
        }
      }
      timingPattern(6)
      timingPattern(size - 7)

      const reservedArea = (row, col, height, width) => {
        for (let r = 0; r < height; r++) {
          for (let c = 0; c < width; c++) {
            if (matrix[row + r] && matrix[row + r][col + c] !== undefined) {
              matrix[row + r][col + c] = null
            }
          }
        }
      }
      reservedArea(0, size - 8, 9, 8)
      reservedArea(size - 8, 0, 8, 9)

      const dataBits = encodeData(data, version, errorLevel)
      let bitIndex = 0
      const direction = -1
      let col = size - 1
      let row = size - 1

      for (let i = 0; i < dataBits.length; i++) {
        const bit = dataBits[i] === '1'
        while (matrix[row][col] !== false) {
          col += direction
          if (col < 0) {
            col = size - 1
            row += direction
          }
          if (row < 0 || row >= size) {
            return matrix
          }
        }
        matrix[row][col] = bit
        if (i < dataBits.length - 1) {
          col += direction
          if (col < 0 || (matrix[row][col] !== false && matrix[row][col] !== null)) {
            col += direction
            row += direction
          }
        }
      }

      return matrix
    }

    const calculateVersion = (dataLength, errorLevel) => {
      const capacity = {
        1: [19, 16, 13, 9],
        2: [34, 28, 22, 16],
        3: [55, 44, 34, 26],
        4: [80, 64, 48, 36]
      }
      const errorIndex = ['L', 'M', 'Q', 'H'].indexOf(errorLevel)

      for (let v = 1; v <= 40; v++) {
        const cap = capacity[v] || [0, 0, 0, 0]
        const maxCapacity = v <= 4 ? cap[errorIndex] : Math.floor(cap[errorIndex] * (1 + (v - 4) * 0.2))
        if (dataLength <= maxCapacity) {
          return v
        }
      }
      return 40
    }

    const encodeData = (data, version, errorLevel) => {
      const modeIndicator = '0100'
      const charCountIndicator = data.length.toString(2).padStart(8, '0')
      let binaryData = modeIndicator + charCountIndicator

      for (let i = 0; i < data.length; i++) {
        binaryData += data.charCodeAt(i).toString(2).padStart(8, '0')
      }

      const capacity = {
        1: [19, 16, 13, 9],
        2: [34, 28, 22, 16]
      }
      const errorIndex = ['L', 'M', 'Q', 'H'].indexOf(errorLevel)
      const maxBits = (capacity[Math.min(version, 2)] || [152, 128, 104, 72])[errorIndex]

      while (binaryData.length < maxBits) {
        binaryData += '11101100'
        if (binaryData.length > maxBits) {
          binaryData = binaryData.substring(0, maxBits)
        }
      }

      return binaryData
    }

    const drawFinderPatterns = (ctx, moduleSize, margin, color) => {
      ctx.fillStyle = color
    }

    const downloadQRCode = () => {
      if (!generatedQR.value || !qrCanvas.value) return

      const canvas = qrCanvas.value
      let dataUrl
      let filename

      if (downloadFormat.value === 'svg') {
        const svg = generateSVG()
        const blob = new Blob([svg], { type: 'image/svg+xml' })
        dataUrl = URL.createObjectURL(blob)
        filename = `qrcode_${Date.now()}.svg`
      } else {
        dataUrl = canvas.toDataURL(`image/${downloadFormat.value}`)
        filename = `qrcode_${Date.now()}.${downloadFormat.value}`
      }

      const a = document.createElement('a')
      a.href = dataUrl
      a.download = filename
      a.click()

      if (downloadFormat.value === 'svg') {
        URL.revokeObjectURL(dataUrl)
      }
    }

    const generateSVG = () => {
      const size = qrSettings.value.size
      const qr = generateQRMatrix(getQRContent.value, ['L', 'M', 'Q', 'H'].indexOf(qrSettings.value.errorLevel))

      let paths = ''
      const moduleCount = qr.length
      const moduleSize = size / moduleCount

      for (let row = 0; row < moduleCount; row++) {
        for (let col = 0; col < moduleCount; col++) {
          if (qr[row][col]) {
            paths += `<rect x="${col * moduleSize}" y="${row * moduleSize}" width="${moduleSize}" height="${moduleSize}" fill="${qrSettings.value.foreground}"/>`
          }
        }
      }

      return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
        <rect width="100%" height="100%" fill="${qrSettings.value.background}"/>
        ${paths}
      </svg>`
    }

    const addToHistory = (content) => {
      const item = {
        id: Date.now(),
        type: contentType.value,
        content: content.substring(0, 50),
        fullContent: content,
        time: Date.now()
      }

      history.value.unshift(item)
      if (history.value.length > 10) {
        history.value = history.value.slice(0, 10)
      }

      saveHistory()
    }

    const loadFromHistory = (item) => {
      contentType.value = item.type
      qrContent.value.text = item.fullContent
      qrContent.value.url = item.fullContent
      generateQRCode()
    }

    const clearHistory = () => {
      history.value = []
      localStorage.removeItem('qrCodeHistory')
    }

    const saveHistory = () => {
      const historyData = history.value.map(item => ({
        id: item.id,
        type: item.type,
        content: item.fullContent,
        time: item.time
      }))
      localStorage.setItem('qrCodeHistory', JSON.stringify(historyData))
    }

    const loadHistory = () => {
      const saved = localStorage.getItem('qrCodeHistory')
      if (saved) {
        try {
          const data = JSON.parse(saved)
          history.value = data.map(item => ({
            ...item,
            fullContent: item.content
          }))
        } catch (e) {
          console.error('Failed to load history')
        }
      }
    }

    const getTypeIcon = (type) => {
      const icons = {
        url: '🔗',
        text: '📝',
        wifi: '📶',
        vcard: '👤',
        email: '📧',
        phone: '📞'
      }
      return icons[type] || '📱'
    }

    const truncateContent = (content) => {
      if (content.length > 20) {
        return content.substring(0, 20) + '...'
      }
      return content
    }

    const formatTime = (timestamp) => {
      const date = new Date(timestamp)
      return date.toLocaleString('zh-CN', {
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    watch(contentType, () => {
      generatedQR.value = false
    })

    onMounted(() => {
      loadHistory()
    })

    return {
      qrCanvas,
      generatedQR,
      downloadFormat,
      history,
      contentType,
      qrContent,
      qrSettings,
      contentTypes,
      errorLevels,
      canGenerate,
      getQRContent,
      generateQRCode,
      downloadQRCode,
      clearHistory,
      loadFromHistory,
      getTypeIcon,
      truncateContent,
      formatTime
    }
  }
}
</script>

<style scoped>
.qrcode-generator {
  padding: 24px;
  background: #f8fafc;
  min-height: calc(100vh - 60px);
}

.tool-header {
  margin-bottom: 24px;
}

.tool-header h2 {
  font-size: 24px;
  color: #1e293b;
  margin-bottom: 8px;
}

.tool-header p {
  color: #64748b;
  font-size: 14px;
}

.generator-container {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 24px;
}

.generator-main {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.section-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-card h3 {
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.content-type-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 20px;
}

.type-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.type-btn:hover {
  border-color: #3b82f6;
  background: #eff6ff;
}

.type-btn.active {
  border-color: #3b82f6;
  background: #dbeafe;
}

.type-icon {
  font-size: 18px;
}

.type-name {
  font-size: 13px;
  color: #475569;
  font-weight: 500;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  color: #475569;
  margin-bottom: 6px;
  font-weight: 500;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 100px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.checkbox-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-weight: normal;
}

.checkbox-group input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #3b82f6;
}

.wifi-form,
.vcard-form {
  display: flex;
  flex-direction: column;
}

.style-controls {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.size-slider {
  display: flex;
  align-items: center;
  gap: 16px;
}

.size-slider input[type="range"] {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #e2e8f0;
  appearance: none;
}

.size-slider input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  transition: all 0.2s;
}

.size-slider input[type="range"]::-webkit-slider-thumb:hover {
  transform: scale(1.1);
}

.size-value {
  min-width: 60px;
  font-size: 14px;
  color: #1e293b;
  font-weight: 500;
}

.error-level-selector {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
}

.level-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  border: 2px solid #e2e8f0;
  background: white;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.level-btn:hover {
  border-color: #3b82f6;
}

.level-btn.active {
  border-color: #3b82f6;
  background: #dbeafe;
}

.level-name {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.level-info {
  font-size: 11px;
  color: #64748b;
  margin-top: 4px;
}

.color-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.color-picker-wrapper {
  display: flex;
  align-items: center;
  gap: 10px;
}

.color-input {
  width: 40px;
  height: 40px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  padding: 0;
}

.color-text {
  flex: 1;
  font-family: monospace;
  font-size: 13px;
}

.generator-sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.preview-card,
.download-card,
.history-card,
.tips-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.preview-card h4,
.download-card h4,
.history-card h4,
.tips-card h4 {
  font-size: 14px;
  color: #1e293b;
  margin-bottom: 12px;
}

.qr-preview {
  background: #f8fafc;
  border-radius: 8px;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
  margin-bottom: 16px;
}

.qr-preview canvas {
  max-width: 100%;
  height: auto;
}

.placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 13px;
}

.preview-actions {
  display: flex;
  justify-content: center;
}

.generate-btn {
  width: 100%;
  padding: 12px;
  border: none;
  background: #3b82f6;
  color: white;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.generate-btn:hover:not(:disabled) {
  background: #2563eb;
}

.generate-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.download-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.format-selector {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.format-selector label {
  font-size: 12px;
  color: #64748b;
}

.format-selector select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
}

.download-btn {
  width: 100%;
  padding: 12px;
  border: none;
  background: #22c55e;
  color: white;
  border-radius: 10px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.download-btn:hover:not(:disabled) {
  background: #16a34a;
}

.download-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.history-header h4 {
  margin: 0;
}

.clear-history-btn {
  padding: 4px 10px;
  border: none;
  background: #fee2e2;
  color: #ef4444;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.clear-history-btn:hover {
  background: #fecaca;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 200px;
  overflow-y: auto;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: #f8fafc;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  background: #e2e8f0;
}

.history-icon {
  font-size: 20px;
}

.history-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.history-content {
  font-size: 12px;
  color: #1e293b;
}

.history-time {
  font-size: 10px;
  color: #94a3b8;
}

.no-history {
  text-align: center;
  padding: 20px;
  color: #94a3b8;
  font-size: 13px;
}

.tips-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.tip-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.tip-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.tip-text {
  font-size: 12px;
  color: #64748b;
  line-height: 1.5;
}

@media (max-width: 1200px) {
  .generator-container {
    grid-template-columns: 1fr;
  }

  .generator-sidebar {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16px;
  }

  .tips-card {
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .generator-sidebar {
    grid-template-columns: 1fr;
  }

  .tips-card {
    grid-column: span 1;
  }

  .form-row {
    grid-template-columns: 1fr;
  }

  .color-row {
    grid-template-columns: 1fr;
  }

  .error-level-selector {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

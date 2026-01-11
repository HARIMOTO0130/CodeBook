<template>
  <div class="color-picker-tool">
    <div class="tool-header">
      <h2>颜色选择器</h2>
      <p>支持多种颜色格式，提供配色建议和对比度检测</p>
    </div>

    <div class="picker-container">
      <div class="color-main-panel">
        <div class="current-color-display">
          <div
            class="color-preview"
            :style="{ backgroundColor: hexColor }"
          ></div>
          <div class="color-info">
            <span class="color-name">{{ colorName }}</span>
            <span class="color-hex">{{ hexColor }}</span>
          </div>
          <button class="copy-btn" @click="copyColor">
            <span>{{ copied ? '✓ 已复制' : '📋 复制' }}</span>
          </button>
        </div>

        <div class="color-spectrum">
          <div class="spectrum-container">
            <div
              class="spectrum-area"
              ref="spectrumArea"
              @mousedown="startDragSaturation"
              @touchstart="startDragSaturation"
            >
              <div class="saturation-gradient"></div>
              <div class="lightness-gradient"></div>
              <div
                class="spectrum-cursor"
                :style="saturationCursorStyle"
              ></div>
            </div>
            <div class="hue-slider">
              <div
                class="hue-gradient"
                @mousedown="startDragHue"
                @touchstart="startDragHue"
              >
                <div
                  class="hue-cursor"
                  :style="{ left: hueCursorLeft }"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div class="color-adjustments">
          <div class="adjustment-group">
            <label>色相 (H)</label>
            <input
              type="range"
              v-model.number="hue"
              min="0"
              max="360"
              @input="updateColorFromHSL"
            />
            <span class="adjust-value">{{ hue }}°</span>
          </div>
          <div class="adjustment-group">
            <label>饱和度 (S)</label>
            <input
              type="range"
              v-model.number="saturation"
              min="0"
              max="100"
              @input="updateColorFromHSL"
            />
            <span class="adjust-value">{{ saturation }}%</span>
          </div>
          <div class="adjustment-group">
            <label>亮度 (L)</label>
            <input
              type="range"
              v-model.number="lightness"
              min="0"
              max="100"
              @input="updateColorFromHSL"
            />
            <span class="adjust-value">{{ lightness }}%</span>
          </div>
        </div>

        <div class="color-inputs">
          <div class="input-group">
            <label>HEX</label>
            <div class="input-with-prefix">
              <span class="prefix">#</span>
              <input
                type="text"
                v-model="hexInput"
                @blur="updateFromHex"
                @keyup.enter="updateFromHex"
                maxlength="7"
              />
            </div>
          </div>
          <div class="input-group">
            <label>RGB</label>
            <div class="rgb-inputs">
              <input
                type="number"
                v-model.number="rgb.r"
                min="0"
                max="255"
                @input="updateFromRGB"
              />
              <input
                type="number"
                v-model.number="rgb.g"
                min="0"
                max="255"
                @input="updateFromRGB"
              />
              <input
                type="number"
                v-model.number="rgb.b"
                min="0"
                max="255"
                @input="updateFromRGB"
              />
            </div>
          </div>
          <div class="input-group">
            <label>HSL</label>
            <div class="hsl-inputs">
              <input
                type="number"
                v-model.number="hue"
                min="0"
                max="360"
                @input="updateColorFromHSL"
              />
              <input
                type="number"
                v-model.number="saturation"
                min="0"
                max="100"
                @input="updateColorFromHSL"
              />
              <input
                type="number"
                v-model.number="lightness"
                min="0"
                max="100"
                @input="updateColorFromHSL"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="color-palette-panel">
        <div class="panel-section">
          <h3>预设配色</h3>
          <div class="preset-colors">
            <div
              v-for="(preset, index) in presetColors"
              :key="index"
              class="preset-group"
            >
              <span class="preset-name">{{ preset.name }}</span>
              <div class="preset-swatches">
                <div
                  v-for="color in preset.colors"
                  :key="color"
                  class="preset-swatch"
                  :style="{ backgroundColor: color }"
                  @click="setColorFromHex(color)"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div class="panel-section">
          <h3>颜色变体</h3>
          <div class="color-variants">
            <div
              v-for="variant in colorVariants"
              :key="variant.name"
              class="variant-row"
            >
              <span class="variant-name">{{ variant.name }}</span>
              <div class="variant-swatches">
                <div
                  v-for="color in variant.colors"
                  :key="color.hex"
                  class="variant-swatch"
                  :style="{ backgroundColor: color.hex }"
                  @click="setColorFromHex(color.hex)"
                  :title="color.hex"
                ></div>
              </div>
            </div>
          </div>
        </div>

        <div class="panel-section">
          <h3>颜色历史</h3>
          <div class="color-history">
            <div
              v-if="colorHistory.length === 0"
              class="empty-history"
            >
              <p>暂无颜色历史</p>
            </div>
            <div
              v-for="(color, index) in colorHistory"
              :key="index"
              class="history-swatch"
              :style="{ backgroundColor: color }"
              @click="setColorFromHex(color)"
              :title="color"
            ></div>
          </div>
          <button
            v-if="colorHistory.length > 0"
            class="clear-history-btn"
            @click="clearColorHistory"
          >
            清空历史
          </button>
        </div>

        <div class="panel-section accessibility-check">
          <h3>对比度检测</h3>
          <div class="contrast-preview">
            <div
              class="contrast-box"
              :style="{
                backgroundColor: hexColor,
                color: checkContrast(hexColor) > 4.5 ? '#ffffff' : '#000000'
              }"
            >
              <span>文字示例</span>
              <small>这是对比度测试文本</small>
            </div>
          </div>
          <div class="contrast-result">
            <div class="contrast-ratio">
              <span class="ratio-label">对比度</span>
              <span class="ratio-value">{{ contrastRatio.toFixed(2) }}:1</span>
            </div>
            <div class="contrast-levels">
              <div class="level-item" :class="{ pass: checkContrast(hexColor) >= 4.5 }">
                <span class="level-name">AA 大字</span>
                <span class="level-status">{{ checkContrast(hexColor) >= 4.5 ? '✓ 通过' : '✗ 失败' }}</span>
              </div>
              <div class="level-item" :class="{ pass: checkContrast(hexColor) >= 3 }">
                <span class="level-name">AA 小字</span>
                <span class="level-status">{{ checkContrast(hexColor) >= 3 ? '✓ 通过' : '✗ 失败' }}</span>
              </div>
              <div class="level-item" :class="{ pass: checkContrast(hexColor) >= 7 }">
                <span class="level-name">AAA 大字</span>
                <span class="level-status">{{ checkContrast(hexColor) >= 7 ? '✓ 通过' : '✗ 失败' }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="panel-section complementary-colors">
          <h3>互补配色</h3>
          <div class="complementary-display">
            <div
              class="comp-color main"
              :style="{ backgroundColor: hexColor }"
              @click="setColorFromHex(hexColor)"
            >
              <span>当前</span>
            </div>
            <div
              class="comp-color"
              :style="{ backgroundColor: complementaryColor }"
              @click="setColorFromHex(complementaryColor)"
            >
              <span>互补</span>
            </div>
            <div
              class="comp-color"
              :style="{ backgroundColor: analogous1Color }"
              @click="setColorFromHex(analogous1Color)"
            >
              <span>类似1</span>
            </div>
            <div
              class="comp-color"
              :style="{ backgroundColor: analogous2Color }"
              @click="setColorFromHex(analogous2Color)"
            >
              <span>类似2</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

export default {
  name: 'ColorPicker',
  setup() {
    const hue = ref(210)
    const saturation = ref(70)
    const lightness = ref(50)
    const hexInput = ref('2d7dd2')
    const colorHistory = ref([])
    const copied = ref(false)

    const spectrumArea = ref(null)
    const isDraggingSaturation = ref(false)
    const isDraggingHue = ref(false)

    const rgb = ref({ r: 45, g: 125, b: 210 })
    const hsl = ref({ h: 210, s: 70, l: 50 })

    const presetColors = ref([
      {
        name: '教学主题',
        colors: ['#2196f3', '#4caf50', '#ff9800', '#9c27b0', '#00bcd4']
      },
      {
        name: '温暖色调',
        colors: ['#f44336', '#ff5722', '#ff9800', '#ffc107', '#ffeb3b']
      },
      {
        name: '冷色调',
        colors: ['#03a9f4', '#00bcd4', '#009688', '#3f51b5', '#673ab7']
      },
      {
        name: '自然色调',
        colors: ['#8bc34a', '#4caf50', '#009688', '#795548', '#607d8b']
      },
      {
        name: '中性色调',
        colors: ['#9e9e9e', '#607d8b', '#795548', '#424242', '#212121']
      }
    ])

    const colorName = computed(() => {
      const names = {
        0: '红色', 15: '浅红', 30: '橙红', 45: '橙色', 60: '橙黄',
        75: '黄色', 90: '浅黄', 120: '黄绿', 150: '绿色', 180: '青绿',
        210: '青色', 240: '蓝色', 270: '靛蓝', 300: '紫色', 330: '品红',
        345: '浅品红', 360: '红色'
      }
      const hueKey = Math.round(hue.value / 15) * 15
      return names[hueKey] || '未知颜色'
    })

    const hexColor = computed(() => {
      const toHex = (n) => {
        const hex = Math.round(n).toString(16)
        return hex.length === 1 ? '0' + hex : hex
      }
      return `#${toHex(rgb.value.r)}${toHex(rgb.value.g)}${toHex(rgb.value.b)}`
    })

    const saturationCursorStyle = computed(() => {
      return {
        left: `${saturation.value}%`,
        top: `${100 - lightness.value}%`
      }
    })

    const hueCursorLeft = computed(() => {
      return `${(hue.value / 360) * 100}%`
    })

    const complementaryColor = computed(() => {
      const newHue = (hue.value + 180) % 360
      return hslToHex(newHue, saturation.value, lightness.value)
    })

    const analogous1Color = computed(() => {
      const newHue = (hue.value + 30) % 360
      return hslToHex(newHue, saturation.value, lightness.value)
    })

    const analogous2Color = computed(() => {
      const newHue = (hue.value - 30 + 360) % 360
      return hslToHex(newHue, saturation.value, lightness.value)
    })

    const colorVariants = computed(() => {
      const variants = []

      const addVariants = (name, hueDelta, satDelta, lightDelta) => {
        const newHue = (hue.value + hueDelta + 360) % 360
        const newSat = Math.max(0, Math.min(100, saturation.value + satDelta))
        const newLight = Math.max(0, Math.min(100, lightness.value + lightDelta))
        variants.push({
          name,
          colors: [
            { hex: hslToHex(newHue, newSat, newLight) },
            { hex: hslToHex(newHue, newSat, Math.max(0, newLight - 20)) },
            { hex: hslToHex(newHue, newSat, Math.min(100, newLight + 20)) }
          ]
        })
      }

      addVariants('更浅', 0, -20, 30)
      addVariants('更深', 0, 0, -30)
      addVariants('更饱和', 0, 30, 0)
      addVariants('更灰暗', 0, -30, 0)

      return variants
    })

    const contrastRatio = computed(() => {
      const lum1 = getLuminance(rgb.value.r, rgb.value.g, rgb.value.b)
      const whiteLum = getLuminance(255, 255, 255)
      const blackLum = getLuminance(0, 0, 0)
      const lighter = Math.max(whiteLum, blackLum)
      const darker = Math.min(whiteLum, blackLum)
      return (lighter + 0.05) / (darker + 0.05)
    })

    const hslToHex = (h, s, l) => {
      s /= 100
      l /= 100
      const a = s * Math.min(l, 1 - l)
      const f = n => {
        const k = (n + h / 30) % 12
        const color = l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1)
        return Math.round(255 * color).toString(16).padStart(2, '0')
      }
      return `#${f(0)}${f(8)}${f(4)}`
    }

    const hexToRgb = (hex) => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex)
      return result ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16)
      } : null
    }

    const rgbToHsl = (r, g, b) => {
      r /= 255
      g /= 255
      b /= 255
      const max = Math.max(r, g, b)
      const min = Math.min(r, g, b)
      let h, s
      const l = (max + min) / 2

      if (max === min) {
        h = s = 0
      } else {
        const d = max - min
        s = l > 0.5 ? d / (2 - max - min) : d / (max + min)
        switch (max) {
          case r: h = ((g - b) / d + (g < b ? 6 : 0)) / 6; break
          case g: h = ((b - r) / d + 2) / 6; break
          case b: h = ((r - g) / d + 4) / 6; break
        }
      }

      return {
        h: Math.round(h * 360),
        s: Math.round(s * 100),
        l: Math.round(l * 100)
      }
    }

    const getLuminance = (r, g, b) => {
      const a = [r, g, b].map(v => {
        v /= 255
        return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4)
      })
      return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722
    }

    const checkContrast = (color) => {
      const rgbColor = hexToRgb(color)
      if (!rgbColor) return 0
      const lum1 = getLuminance(rgbColor.r, rgbColor.g, rgbColor.b)
      const whiteLum = getLuminance(255, 255, 255)
      const blackLum = getLuminance(0, 0, 0)
      const lighter = Math.max(whiteLum, blackLum)
      const darker = Math.min(whiteLum, blackLum)
      return (lighter + 0.05) / (darker + 0.05)
    }

    const updateColorFromHSL = () => {
      const hex = hslToHex(hue.value, saturation.value, lightness.value)
      const rgbColor = hexToRgb(hex)
      if (rgbColor) {
        rgb.value = rgbColor
        hexInput.value = hex.replace('#', '')
      }
    }

    const updateFromRGB = () => {
      const hslColor = rgbToHsl(rgb.value.r, rgb.value.g, rgb.value.b)
      hue.value = hslColor.h
      saturation.value = hslColor.s
      lightness.value = hslColor.l
      hexInput.value = hslToHex(hslColor.h, hslColor.s, hslColor.l).replace('#', '')
    }

    const updateFromHex = () => {
      let hex = hexInput.value
      if (!hex.startsWith('#')) {
        hex = '#' + hex
      }
      const rgbColor = hexToRgb(hex)
      if (rgbColor) {
        rgb.value = rgbColor
        const hslColor = rgbToHsl(rgbColor.r, rgbColor.g, rgbColor.b)
        hue.value = hslColor.h
        saturation.value = hslColor.s
        lightness.value = hslColor.l
        addToHistory(hex)
      }
    }

    const setColorFromHex = (hex) => {
      if (!hex.startsWith('#')) {
        hex = '#' + hex
      }
      hexInput.value = hex.replace('#', '')
      updateFromHex()
    }

    const startDragSaturation = (event) => {
      isDraggingSaturation.value = true
      updateSaturationFromEvent(event)
      document.addEventListener('mousemove', onDragSaturation)
      document.addEventListener('mouseup', stopDragSaturation)
      document.addEventListener('touchmove', onDragSaturation)
      document.addEventListener('touchend', stopDragSaturation)
    }

    const onDragSaturation = (event) => {
      if (isDraggingSaturation.value) {
        updateSaturationFromEvent(event)
      }
    }

    const updateSaturationFromEvent = (event) => {
      if (!spectrumArea.value) return
      const rect = spectrumArea.value.getBoundingClientRect()
      const clientX = event.touches ? event.touches[0].clientX : event.clientX
      const clientY = event.touches ? event.touches[0].clientY : event.clientY

      let x = (clientX - rect.left) / rect.width * 100
      let y = (clientY - rect.top) / rect.height * 100

      x = Math.max(0, Math.min(100, x))
      y = Math.max(0, Math.min(100, y))

      saturation.value = Math.round(x)
      lightness.value = Math.round(100 - y)
      updateColorFromHSL()
    }

    const stopDragSaturation = () => {
      isDraggingSaturation.value = false
      document.removeEventListener('mousemove', onDragSaturation)
      document.removeEventListener('mouseup', stopDragSaturation)
      document.removeEventListener('touchmove', onDragSaturation)
      document.removeEventListener('touchend', stopDragSaturation)
      addToHistory(hexColor.value)
    }

    const startDragHue = (event) => {
      isDraggingHue.value = true
      updateHueFromEvent(event)
      document.addEventListener('mousemove', onDragHue)
      document.addEventListener('mouseup', stopDragHue)
      document.addEventListener('touchmove', onDragHue)
      document.addEventListener('touchend', stopDragHue)
    }

    const onDragHue = (event) => {
      if (isDraggingHue.value) {
        updateHueFromEvent(event)
      }
    }

    const updateHueFromEvent = (event) => {
      const target = event.target.closest('.hue-gradient')
      if (!target) return
      const rect = target.getBoundingClientRect()
      const clientX = event.touches ? event.touches[0].clientX : event.clientX
      const x = (clientX - rect.left) / rect.width * 100
      hue.value = Math.round(Math.max(0, Math.min(100, x)) / 100 * 360)
      updateColorFromHSL()
    }

    const stopDragHue = () => {
      isDraggingHue.value = false
      document.removeEventListener('mousemove', onDragHue)
      document.removeEventListener('mouseup', stopDragHue)
      document.removeEventListener('touchmove', onDragHue)
      document.removeEventListener('touchend', stopDragHue)
      addToHistory(hexColor.value)
    }

    const addToHistory = (color) => {
      if (!colorHistory.value.includes(color)) {
        colorHistory.value.unshift(color)
        if (colorHistory.value.length > 12) {
          colorHistory.value.pop()
        }
      }
    }

    const clearColorHistory = () => {
      colorHistory.value = []
    }

    const copyColor = () => {
      navigator.clipboard.writeText(hexColor.value).then(() => {
        copied.value = true
        setTimeout(() => {
          copied.value = false
        }, 2000)
      })
    }

    onMounted(() => {
      updateColorFromHSL()
    })

    onUnmounted(() => {
      document.removeEventListener('mousemove', onDragSaturation)
      document.removeEventListener('mouseup', stopDragSaturation)
      document.removeEventListener('touchmove', onDragSaturation)
      document.removeEventListener('touchend', stopDragSaturation)
      document.removeEventListener('mousemove', onDragHue)
      document.removeEventListener('mouseup', stopDragHue)
      document.removeEventListener('touchmove', onDragHue)
      document.removeEventListener('touchend', stopDragHue)
    })

    return {
      hue,
      saturation,
      lightness,
      hexInput,
      colorHistory,
      copied,
      spectrumArea,
      rgb,
      colorName,
      hexColor,
      saturationCursorStyle,
      hueCursorLeft,
      complementaryColor,
      analogous1Color,
      analogous2Color,
      colorVariants,
      presetColors,
      contrastRatio,
      updateColorFromHSL,
      updateFromRGB,
      updateFromHex,
      setColorFromHex,
      startDragSaturation,
      startDragHue,
      checkContrast,
      addToHistory,
      clearColorHistory,
      copyColor
    }
  }
}
</script>

<style scoped>
.color-picker-tool {
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

.picker-container {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 24px;
}

.color-main-panel {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
}

.current-color-display {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  padding: 16px;
  background: #fff;
  border-radius: 12px;
}

.color-preview {
  width: 64px;
  height: 64px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.color-info {
  flex: 1;
}

.color-name {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin-bottom: 4px;
}

.color-hex {
  display: block;
  font-size: 14px;
  color: #666;
  font-family: 'Courier New', monospace;
}

.copy-btn {
  padding: 10px 16px;
  border: none;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s;
}

.copy-btn:hover {
  background: #bbdefb;
}

.color-spectrum {
  margin-bottom: 20px;
}

.spectrum-container {
  display: flex;
  gap: 12px;
}

.spectrum-area {
  flex: 1;
  height: 200px;
  border-radius: 12px;
  position: relative;
  cursor: crosshair;
  overflow: hidden;
}

.saturation-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(to right, #fff, rgba(255, 255, 255, 0));
}

.lightness-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, #000, transparent);
}

.spectrum-cursor {
  position: absolute;
  width: 16px;
  height: 16px;
  border: 3px solid #fff;
  border-radius: 50%;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  transform: translate(-50%, -50%);
  pointer-events: none;
}

.hue-slider {
  width: 24px;
  display: flex;
  flex-direction: column;
}

.hue-gradient {
  flex: 1;
  border-radius: 12px;
  background: linear-gradient(to bottom,
    #ff0000, #ffff00, #00ff00, #00ffff, #0000ff, #ff00ff, #ff0000
  );
  position: relative;
  cursor: pointer;
}

.hue-cursor {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 3px solid #fff;
  border-radius: 50%;
  background: transparent;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  transform: translateX(-50%);
  top: 50%;
  margin-top: -10px;
  pointer-events: none;
}

.color-adjustments {
  margin-bottom: 20px;
}

.adjustment-group {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.adjustment-group label {
  width: 80px;
  font-size: 13px;
  color: #666;
}

.adjustment-group input[type="range"] {
  flex: 1;
  height: 6px;
  border-radius: 3px;
  background: #e0e0e0;
  appearance: none;
  cursor: pointer;
}

.adjustment-group input[type="range"]::-webkit-slider-thumb {
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: #2196f3;
  cursor: pointer;
  box-shadow: 0 2px 6px rgba(33, 150, 243, 0.4);
}

.adjust-value {
  width: 50px;
  font-size: 13px;
  color: #333;
  text-align: right;
}

.color-inputs {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.input-group {
  display: flex;
  align-items: center;
  gap: 12px;
}

.input-group label {
  width: 50px;
  font-size: 13px;
  font-weight: 500;
  color: #333;
}

.input-with-prefix {
  flex: 1;
  display: flex;
  align-items: center;
  background: #fff;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
}

.prefix {
  padding: 10px 12px;
  background: #f5f5f5;
  color: #666;
  font-size: 14px;
  border-right: 1px solid #e0e0e0;
}

.input-with-prefix input {
  flex: 1;
  border: none;
  padding: 10px 12px;
  font-size: 14px;
  font-family: 'Courier New', monospace;
}

.input-with-prefix input:focus {
  outline: none;
}

.rgb-inputs,
.hsl-inputs {
  flex: 1;
  display: flex;
  gap: 8px;
}

.rgb-inputs input,
.hsl-inputs input {
  flex: 1;
  padding: 10px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
}

.rgb-inputs input:focus,
.hsl-inputs input:focus {
  outline: none;
  border-color: #2196f3;
}

.color-palette-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-section {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
}

.panel-section h3 {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin: 0 0 12px;
}

.preset-colors {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preset-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preset-name {
  font-size: 12px;
  color: #666;
}

.preset-swatches {
  display: flex;
  gap: 6px;
}

.preset-swatch {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.preset-swatch:hover {
  transform: scale(1.1);
}

.color-variants {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.variant-row {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.variant-name {
  font-size: 12px;
  color: #666;
}

.variant-swatches {
  display: flex;
  gap: 6px;
}

.variant-swatch {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  cursor: pointer;
  transition: transform 0.2s;
}

.variant-swatch:hover {
  transform: scale(1.15);
}

.color-history {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-height: 40px;
}

.empty-history {
  width: 100%;
  text-align: center;
  padding: 20px;
  color: #888;
}

.empty-history p {
  margin: 0;
  font-size: 13px;
}

.history-swatch {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.history-swatch:hover {
  transform: scale(1.1);
}

.clear-history-btn {
  margin-top: 12px;
  padding: 6px 12px;
  border: none;
  background: #ffebee;
  color: #f44336;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.clear-history-btn:hover {
  background: #ffcdd2;
}

.contrast-preview {
  margin-bottom: 16px;
}

.contrast-box {
  padding: 20px;
  border-radius: 10px;
  text-align: center;
}

.contrast-box span {
  font-size: 18px;
  font-weight: 600;
  display: block;
  margin-bottom: 8px;
}

.contrast-box small {
  font-size: 13px;
  opacity: 0.9;
}

.contrast-result {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.contrast-ratio {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #fff;
  border-radius: 8px;
}

.ratio-label {
  font-size: 13px;
  color: #666;
}

.ratio-value {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.contrast-levels {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.level-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  background: #fff;
  border-radius: 8px;
  border-left: 3px solid #f44336;
}

.level-item.pass {
  border-left-color: #4caf50;
}

.level-name {
  font-size: 13px;
  color: #333;
}

.level-status {
  font-size: 12px;
  font-weight: 500;
}

.level-item.pass .level-status {
  color: #4caf50;
}

.level-item:not(.pass) .level-status {
  color: #f44336;
}

.complementary-display {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.comp-color {
  aspect-ratio: 1;
  border-radius: 10px;
  cursor: pointer;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding-bottom: 8px;
  transition: transform 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.comp-color:hover {
  transform: scale(1.05);
}

.comp-color span {
  font-size: 11px;
  font-weight: 500;
  color: inherit;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.comp-color.main {
  grid-row: span 2;
}

@media (max-width: 900px) {
  .picker-container {
    grid-template-columns: 1fr;
  }
}
</style>

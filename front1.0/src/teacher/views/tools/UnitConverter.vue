<template>
  <div class="unit-converter">
    <div class="tool-header">
      <h2>单位换算器</h2>
      <p>支持长度、重量、体积、面积、温度、时间、数据等多种单位换算</p>
    </div>

    <div class="converter-container">
      <div class="category-selector">
        <div class="category-grid">
          <button
            v-for="cat in categories"
            :key="cat.id"
            class="category-btn"
            :class="{ active: selectedCategory === cat.id }"
            @click="selectedCategory = cat.id"
          >
            <span class="category-icon">{{ cat.icon }}</span>
            <span class="category-name">{{ cat.name }}</span>
          </button>
        </div>
      </div>

      <div class="conversion-panel">
        <div class="conversion-type">
          <span class="from-label">从</span>
          <span class="to-label">换算到</span>
        </div>

        <div class="input-section">
          <div class="input-group">
            <input
              type="number"
              v-model.number="inputValue"
              @input="convertFromInput"
              placeholder="输入数值"
            />
            <select v-model="fromUnit" @change="convert">
              <option v-for="unit in currentUnits" :key="unit.id" :value="unit.id">
                {{ unit.name }}
              </option>
            </select>
          </div>

          <button class="swap-btn" @click="swapUnits">
            <span>⇅</span>
          </button>

          <div class="input-group">
            <input
              type="number"
              :value="outputValue"
              readonly
              class="output-input"
            />
            <select v-model="toUnit" @change="convert">
              <option v-for="unit in currentUnits" :key="unit.id" :value="unit.id">
                {{ unit.name }}
              </option>
            </select>
          </div>
        </div>

        <div class="quick-convert">
          <span class="quick-label">快速换算:</span>
          <div class="quick-values">
            <button
              v-for="quickValue in quickValues"
              :key="quickValue"
              class="quick-btn"
              @click="setQuickValue(quickValue)"
            >
              {{ quickValue }}
            </button>
          </div>
        </div>

        <div class="formula-display">
          <div class="formula-header">换算公式</div>
          <div class="formula-content">
            <span v-if="fromUnit && toUnit">
              1 {{ getUnitName(fromUnit) }} = {{ getConversionRate() }} {{ getUnitName(toUnit) }}
            </span>
          </div>
        </div>

        <div class="reference-table">
          <div class="table-header">单位参考</div>
          <div class="table-content">
            <div
              v-for="unit in currentUnits"
              :key="unit.id"
              class="reference-row"
              @click="setFromUnit(unit.id)"
            >
              <span class="ref-name">{{ unit.name }}</span>
              <span class="ref-symbol">{{ unit.symbol }}</span>
              <span class="ref-value">{{ formatNumber(getBaseValue(1, unit.id)) }} {{ currentCategory.base }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="history-section">
        <div class="history-header">
          <h3>换算历史</h3>
          <button v-if="history.length > 0" class="clear-btn" @click="clearHistory">
            清空
          </button>
        </div>
        <div class="history-list">
          <div v-if="history.length === 0" class="empty-history">
            <span>📝</span>
            <p>暂无换算记录</p>
          </div>
          <div
            v-for="(item, index) in history"
            :key="index"
            class="history-item"
            @click="loadFromHistory(item)"
          >
            <div class="history-conversion">
              {{ item.input }} {{ item.fromName }} = {{ formatNumber(item.result) }} {{ item.toName }}
            </div>
            <div class="history-time">{{ formatTime(item.time) }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'

export default {
  name: 'UnitConverter',
  setup() {
    const selectedCategory = ref('length')
    const inputValue = ref(1)
    const outputValue = ref(0)
    const fromUnit = ref('m')
    const toUnit = ref('km')
    const history = ref([])

    const categories = ref([
      { id: 'length', name: '长度', icon: '📏' },
      { id: 'weight', name: '重量', icon: '⚖️' },
      { id: 'volume', name: '体积', icon: '🧪' },
      { id: 'area', name: '面积', icon: '📐' },
      { id: 'temperature', name: '温度', icon: '🌡️' },
      { id: 'time', name: '时间', icon: '⏰' },
      { id: 'data', name: '数据', icon: '💾' },
      { id: 'speed', name: '速度', icon: '🚀' },
      { id: 'pressure', name: '压强', icon: '🔧' },
      { id: 'energy', name: '能量', icon: '⚡' }
    ])

    const unitData = {
      length: {
        base: '米 (m)',
        units: [
          { id: 'mm', name: '毫米', symbol: 'mm', toBase: 0.001 },
          { id: 'cm', name: '厘米', symbol: 'cm', toBase: 0.01 },
          { id: 'dm', name: '分米', symbol: 'dm', toBase: 0.1 },
          { id: 'm', name: '米', symbol: 'm', toBase: 1 },
          { id: 'km', name: '千米', symbol: 'km', toBase: 1000 },
          { id: 'in', name: '英寸', symbol: 'in', toBase: 0.0254 },
          { id: 'ft', name: '英尺', symbol: 'ft', toBase: 0.3048 },
          { id: 'yd', name: '码', symbol: 'yd', toBase: 0.9144 },
          { id: 'mi', name: '英里', symbol: 'mi', toBase: 1609.344 },
          { id: 'nmi', name: '海里', symbol: 'nmi', toBase: 1852 }
        ]
      },
      weight: {
        base: '克 (g)',
        units: [
          { id: 'mg', name: '毫克', symbol: 'mg', toBase: 0.001 },
          { id: 'g', name: '克', symbol: 'g', toBase: 1 },
          { id: 'kg', name: '千克', symbol: 'kg', toBase: 1000 },
          { id: 't', name: '吨', symbol: 't', toBase: 1000000 },
          { id: 'oz', name: '盎司', symbol: 'oz', toBase: 28.3495 },
          { id: 'lb', name: '磅', symbol: 'lb', toBase: 453.592 },
          { id: 'st', name: '英石', symbol: 'st', toBase: 6350.29 }
        ]
      },
      volume: {
        base: '升 (L)',
        units: [
          { id: 'ml', name: '毫升', symbol: 'mL', toBase: 0.001 },
          { id: 'cl', name: '厘升', symbol: 'cL', toBase: 0.01 },
          { id: 'dl', name: '分升', symbol: 'dL', toBase: 0.1 },
          { id: 'l', name: '升', symbol: 'L', toBase: 1 },
          { id: 'dal', name: '十升', symbol: 'daL', toBase: 10 },
          { id: 'hl', name: '百升', symbol: 'hL', toBase: 100 },
          { id: 'm3', name: '立方米', symbol: 'm³', toBase: 1000 },
          { id: 'gal', name: '加仑(美)', symbol: 'gal', toBase: 3.78541 },
          { id: 'qt', name: '夸脱(美)', symbol: 'qt', toBase: 0.946353 },
          { id: 'pt', name: '品脱(美)', symbol: 'pt', toBase: 0.473176 }
        ]
      },
      area: {
        base: '平方米 (m²)',
        units: [
          { id: 'mm2', name: '平方毫米', symbol: 'mm²', toBase: 0.000001 },
          { id: 'cm2', name: '平方厘米', symbol: 'cm²', toBase: 0.0001 },
          { id: 'dm2', name: '平方分米', symbol: 'dm²', toBase: 0.01 },
          { id: 'm2', name: '平方米', symbol: 'm²', toBase: 1 },
          { id: 'km2', name: '平方千米', symbol: 'km²', toBase: 1000000 },
          { id: 'ha', name: '公顷', symbol: 'ha', toBase: 10000 },
          { id: 'acre', name: '英亩', symbol: 'acre', toBase: 4046.86 },
          { id: 'sqft', name: '平方英尺', symbol: 'ft²', toBase: 0.092903 },
          { id: 'sqin', name: '平方英寸', symbol: 'in²', toBase: 0.00064516 }
        ]
      },
      temperature: {
        base: '摄氏度 (°C)',
        special: true,
        units: [
          { id: 'c', name: '摄氏度', symbol: '°C' },
          { id: 'f', name: '华氏度', symbol: '°F' },
          { id: 'k', name: '开尔文', symbol: 'K' }
        ]
      },
      time: {
        base: '秒 (s)',
        units: [
          { id: 'ms', name: '毫秒', symbol: 'ms', toBase: 0.001 },
          { id: 's', name: '秒', symbol: 's', toBase: 1 },
          { id: 'min', name: '分钟', symbol: 'min', toBase: 60 },
          { id: 'h', name: '小时', symbol: 'h', toBase: 3600 },
          { id: 'd', name: '天', symbol: 'd', toBase: 86400 },
          { id: 'wk', name: '周', symbol: 'wk', toBase: 604800 },
          { id: 'mo', name: '月(30天)', symbol: 'mo', toBase: 2592000 },
          { id: 'yr', name: '年(365天)', symbol: 'yr', toBase: 31536000 }
        ]
      },
      data: {
        base: '字节 (B)',
        units: [
          { id: 'bit', name: '比特', symbol: 'bit', toBase: 0.125 },
          { id: 'byte', name: '字节', symbol: 'B', toBase: 1 },
          { id: 'kb', name: '千字节', symbol: 'KB', toBase: 1024 },
          { id: 'mb', name: '兆字节', symbol: 'MB', toBase: 1048576 },
          { id: 'gb', name: '吉字节', symbol: 'GB', toBase: 1073741824 },
          { id: 'tb', name: '太字节', symbol: 'TB', toBase: 1099511627776 },
          { id: 'kib', name: '千比特', symbol: 'Kib', toBase: 128 },
          { id: 'mib', name: '兆比特', symbol: 'Mib', toBase: 131072 }
        ]
      },
      speed: {
        base: '米/秒 (m/s)',
        units: [
          { id: 'mps', name: '米/秒', symbol: 'm/s', toBase: 1 },
          { id: 'kmh', name: '千米/小时', symbol: 'km/h', toBase: 0.277778 },
          { id: 'mph', name: '英里/小时', symbol: 'mph', toBase: 0.44704 },
          { id: 'fps', name: '英尺/秒', symbol: 'ft/s', toBase: 0.3048 },
          { id: 'kn', name: '节', symbol: 'kn', toBase: 0.514444 },
          { id: 'mach', name: '马赫', symbol: 'Ma', toBase: 340.29 }
        ]
      },
      pressure: {
        base: '帕斯卡 (Pa)',
        units: [
          { id: 'pa', name: '帕斯卡', symbol: 'Pa', toBase: 1 },
          { id: 'kpa', name: '千帕', symbol: 'kPa', toBase: 1000 },
          { id: 'mpa', name: '兆帕', symbol: 'MPa', toBase: 1000000 },
          { id: 'bar', name: '巴', symbol: 'bar', toBase: 100000 },
          { id: 'atm', name: '标准大气压', symbol: 'atm', toBase: 101325 },
          { id: 'mmhg', name: '毫米汞柱', symbol: 'mmHg', toBase: 133.322 },
          { id: 'psi', name: '磅/平方英寸', symbol: 'psi', toBase: 6894.76 }
        ]
      },
      energy: {
        base: '焦耳 (J)',
        units: [
          { id: 'j', name: '焦耳', symbol: 'J', toBase: 1 },
          { id: 'kj', name: '千焦', symbol: 'kJ', toBase: 1000 },
          { id: 'cal', name: '卡路里', symbol: 'cal', toBase: 4.184 },
          { id: 'kcal', name: '千卡', symbol: 'kcal', toBase: 4184 },
          { id: 'wh', name: '瓦时', symbol: 'Wh', toBase: 3600 },
          { id: 'kwh', name: '千瓦时', symbol: 'kWh', toBase: 3600000 },
          { id: 'ev', name: '电子伏特', symbol: 'eV', toBase: 1.60218e-19 },
          { id: 'btu', name: '英热单位', symbol: 'BTU', toBase: 1055.06 }
        ]
      }
    }

    const currentCategory = computed(() => unitData[selectedCategory.value])
    const currentUnits = computed(() => currentCategory.value.units)

    const quickValues = computed(() => {
      if (selectedCategory.value === 'temperature') {
        return [-40, 0, 25, 100, 212]
      }
      return [0.001, 0.01, 0.1, 1, 10, 100, 1000]
    })

    const convertFromInput = () => {
      convert()
      addToHistory()
    }

    const convert = () => {
      if (isNaN(inputValue.value)) {
        outputValue.value = 0
        return
      }

      if (currentCategory.value.special && selectedCategory.value === 'temperature') {
        outputValue.value = convertTemperature(inputValue.value, fromUnit.value, toUnit.value)
      } else {
        const fromRate = getConversionRateValue(fromUnit.value)
        const toRate = getConversionRateValue(toUnit.value)
        outputValue.value = inputValue.value * (fromRate / toRate)
      }
    }

    const convertTemperature = (value, from, to) => {
      let celsius
      switch (from) {
        case 'c': celsius = value; break
        case 'f': celsius = (value - 32) * 5 / 9; break
        case 'k': celsius = value - 273.15; break
      }

      switch (to) {
        case 'c': return celsius
        case 'f': return celsius * 9 / 5 + 32
        case 'k': return celsius + 273.15
      }
      return value
    }

    const getConversionRateValue = (unitId) => {
      const unit = currentUnits.value.find(u => u.id === unitId)
      return unit ? unit.toBase : 1
    }

    const getUnitName = (unitId) => {
      const unit = currentUnits.value.find(u => u.id === unitId)
      return unit ? unit.symbol : unitId
    }

    const getConversionRate = () => {
      if (currentCategory.value.special && selectedCategory.value === 'temperature') {
        const celsiusFrom = convertTemperature(1, fromUnit.value, 'c')
        const celsiusTo = convertTemperature(1, toUnit.value, 'c')
        return formatNumber(celsiusFrom / celsiusTo)
      }
      const fromRate = getConversionRateValue(fromUnit.value)
      const toRate = getConversionRateValue(toUnit.value)
      return formatNumber(fromRate / toRate)
    }

    const getBaseValue = (value, unitId) => {
      const unit = currentUnits.value.find(u => u.id === unitId)
      if (!unit) return value
      return value * unit.toBase
    }

    const formatNumber = (num) => {
      if (Math.abs(num) < 0.0001 || Math.abs(num) >= 10000000) {
        return num.toExponential(4)
      }
      return parseFloat(num.toPrecision(8)).toString()
    }

    const swapUnits = () => {
      const temp = fromUnit.value
      fromUnit.value = toUnit.value
      toUnit.value = temp
      convert()
      addToHistory()
    }

    const setQuickValue = (value) => {
      inputValue.value = value
      convert()
      addToHistory()
    }

    const setFromUnit = (unitId) => {
      fromUnit.value = unitId
      convert()
    }

    const addToHistory = () => {
      if (isNaN(inputValue.value) || inputValue.value === 0) return

      const historyItem = {
        input: inputValue.value,
        from: fromUnit.value,
        fromName: getUnitName(fromUnit.value),
        result: outputValue.value,
        to: toUnit.value,
        toName: getUnitName(toUnit.value),
        time: new Date()
      }

      history.value.unshift(historyItem)
      if (history.value.length > 20) {
        history.value.pop()
      }
    }

    const clearHistory = () => {
      history.value = []
    }

    const loadFromHistory = (item) => {
      inputValue.value = item.input
      fromUnit.value = item.from
      toUnit.value = item.to
      convert()
    }

    const formatTime = (date) => {
      return date.toLocaleTimeString('zh-CN', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    watch(selectedCategory, () => {
      fromUnit.value = currentUnits.value[0]?.id || ''
      toUnit.value = currentUnits.value[1]?.id || ''
      inputValue.value = 1
      convert()
    })

    return {
      selectedCategory,
      inputValue,
      outputValue,
      fromUnit,
      toUnit,
      history,
      categories,
      currentUnits,
      currentCategory,
      quickValues,
      convertFromInput,
      convert,
      getUnitName,
      getConversionRate,
      getBaseValue,
      formatNumber,
      swapUnits,
      setQuickValue,
      setFromUnit,
      clearHistory,
      loadFromHistory,
      formatTime
    }
  }
}
</script>

<style scoped>
.unit-converter {
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

.converter-container {
  display: grid;
  grid-template-columns: 200px 1fr 280px;
  gap: 24px;
}

.category-selector {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 16px;
}

.category-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: 2px solid transparent;
  background: #fff;
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
  text-align: left;
}

.category-btn:hover {
  background: #e8f4fd;
}

.category-btn.active {
  background: #e3f2fd;
  border-color: #2196f3;
}

.category-icon {
  font-size: 20px;
}

.category-name {
  font-size: 14px;
  font-weight: 500;
  color: #333;
}

.conversion-panel {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
}

.conversion-type {
  display: flex;
  justify-content: space-between;
  padding: 0 12px;
  margin-bottom: 12px;
}

.from-label,
.to-label {
  font-size: 13px;
  font-weight: 500;
  color: #666;
}

.input-section {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.input-group {
  flex: 1;
  display: flex;
  gap: 8px;
}

.input-group input {
  flex: 1;
  padding: 14px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 500;
  transition: all 0.2s;
}

.input-group input:focus {
  outline: none;
  border-color: #2196f3;
}

.output-input {
  background: #e8f4fd;
  border-color: #b3d9ff !important;
  color: #1976d2;
  font-weight: 600 !important;
}

.input-group select {
  padding: 14px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 14px;
  background: #fff;
  cursor: pointer;
  min-width: 100px;
}

.swap-btn {
  width: 44px;
  height: 44px;
  border: 2px solid #e0e0e0;
  background: #fff;
  border-radius: 50%;
  cursor: pointer;
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.swap-btn:hover {
  background: #e8f4fd;
  border-color: #2196f3;
  transform: rotate(180deg);
}

.quick-convert {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding: 12px;
  background: #fff;
  border-radius: 10px;
}

.quick-label {
  font-size: 13px;
  color: #666;
  white-space: nowrap;
}

.quick-values {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.quick-btn {
  padding: 6px 12px;
  border: 1px solid #e0e0e0;
  background: #fff;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.quick-btn:hover {
  background: #e8f4fd;
  border-color: #2196f3;
}

.formula-display {
  background: #fff;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 20px;
}

.formula-header {
  font-size: 12px;
  font-weight: 500;
  color: #888;
  margin-bottom: 8px;
}

.formula-content {
  font-size: 14px;
  color: #333;
  font-family: 'Courier New', monospace;
}

.reference-table {
  background: #fff;
  border-radius: 10px;
  overflow: hidden;
}

.table-header {
  padding: 12px 16px;
  background: #f5f5f5;
  font-size: 13px;
  font-weight: 600;
  color: #333;
}

.table-content {
  max-height: 200px;
  overflow-y: auto;
}

.reference-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.2s;
}

.reference-row:hover {
  background: #f8f9fa;
}

.reference-row:last-child {
  border-bottom: none;
}

.ref-name {
  font-size: 13px;
  color: #333;
}

.ref-symbol {
  font-size: 12px;
  color: #888;
  font-family: 'Courier New', monospace;
}

.ref-value {
  font-size: 12px;
  color: #666;
}

.history-section {
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
  font-size: 16px;
  font-weight: 600;
  color: #333;
  margin: 0;
}

.clear-btn {
  padding: 4px 12px;
  border: none;
  background: #ffebee;
  color: #f44336;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.clear-btn:hover {
  background: #ffcdd2;
}

.history-list {
  max-height: 400px;
  overflow-y: auto;
}

.empty-history {
  text-align: center;
  padding: 40px 20px;
  color: #888;
}

.empty-history span {
  font-size: 40px;
  display: block;
  margin-bottom: 12px;
}

.empty-history p {
  font-size: 14px;
  margin: 0;
}

.history-item {
  padding: 12px;
  background: #fff;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  background: #e8f4fd;
}

.history-conversion {
  font-size: 13px;
  color: #333;
  margin-bottom: 4px;
}

.history-time {
  font-size: 11px;
  color: #888;
}

@media (max-width: 1200px) {
  .converter-container {
    grid-template-columns: 1fr;
  }

  .category-selector {
    order: 1;
  }

  .category-grid {
    flex-direction: row;
    flex-wrap: wrap;
  }

  .category-btn {
    flex: 1;
    min-width: 120px;
  }

  .history-section {
    order: 2;
  }
}
</style>

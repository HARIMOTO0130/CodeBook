<template>
  <div class="grade-calculator">
    <div class="config-section">
      <h3>评分规则配置</h3>
      <div class="weight-inputs">
        <div class="weight-item">
          <label>平时成绩占比</label>
          <div class="input-group">
            <input type="number" v-model.number="weights.usual" min="0" max="100" />
            <span class="unit">%</span>
          </div>
        </div>
        <div class="weight-item">
          <label>期中成绩占比</label>
          <div class="input-group">
            <input type="number" v-model.number="weights.midterm" min="0" max="100" />
            <span class="unit">%</span>
          </div>
        </div>
        <div class="weight-item">
          <label>期末成绩占比</label>
          <div class="input-group">
            <input type="number" v-model.number="weights.final" min="0" max="100" />
            <span class="unit">%</span>
          </div>
        </div>
        <div class="weight-item">
          <label>作业成绩占比</label>
          <div class="input-group">
            <input type="number" v-model.number="weights.homework" min="0" max="100" />
            <span class="unit">%</span>
          </div>
        </div>
      </div>
      <div class="total-check" :class="{ valid: totalWeight === 100, invalid: totalWeight !== 100 }">
        <span>总权重：{{ totalWeight }}%</span>
        <span v-if="totalWeight !== 100" class="warning">权重必须等于100%</span>
      </div>
    </div>

    <div class="student-section">
      <div class="section-header">
        <h3>学生成绩录入</h3>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="addStudent">
            <span>➕</span> 添加学生
          </button>
          <button class="btn btn-primary" @click="importScores">
            <span>📥</span> 批量导入
          </button>
        </div>
      </div>

      <div class="students-table">
        <div class="table-header">
          <div class="col col-name">学生姓名</div>
          <div class="col col-usual">平时 ({{ weights.usual }}%)</div>
          <div class="col col-midterm">期中 ({{ weights.midterm }}%)</div>
          <div class="col col-final">期末 ({{ weights.final }}%)</div>
          <div class="col col-homework">作业 ({{ weights.homework }}%)</div>
          <div class="col col-total">总成绩</div>
          <div class="col col-actions">操作</div>
        </div>

        <div
          v-for="(student, index) in students"
          :key="index"
          class="table-row"
          :class="{ highScore: calculateTotal(student) >= 90, passScore: calculateTotal(student) >= 60 && calculateTotal(student) < 90, failScore: calculateTotal(student) < 60 }"
        >
          <div class="col col-name">
            <input type="text" v-model="student.name" placeholder="输入姓名" />
          </div>
          <div class="col col-usual">
            <input type="number" v-model.number="student.usual" min="0" max="100" @input="updateTotal(index)" />
          </div>
          <div class="col col-midterm">
            <input type="number" v-model.number="student.midterm" min="0" max="100" @input="updateTotal(index)" />
          </div>
          <div class="col col-final">
            <input type="number" v-model.number="student.final" min="0" max="100" @input="updateTotal(index)" />
          </div>
          <div class="col col-homework">
            <input type="number" v-model.number="student.homework" min="0" max="100" @input="updateTotal(index)" />
          </div>
          <div class="col col-total">
            <span class="total-score" :class="{ high: calculateTotal(student) >= 90, pass: calculateTotal(student) >= 60 && calculateTotal(student) < 90, fail: calculateTotal(student) < 60 }">
              {{ calculateTotal(student).toFixed(1) }}
            </span>
          </div>
          <div class="col col-actions">
            <button class="action-btn delete" @click="removeStudent(index)" title="删除">
              🗑️
            </button>
          </div>
        </div>
      </div>

      <div v-if="students.length === 0" class="empty-state">
        <span class="empty-icon">📊</span>
        <p>暂无学生数据，点击"添加学生"开始录入</p>
      </div>
    </div>

    <div v-if="students.length > 0" class="statistics-section">
      <h3>成绩统计分析</h3>
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-icon blue">👥</div>
          <div class="stat-info">
            <span class="stat-value">{{ students.length }}</span>
            <span class="stat-label">学生人数</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon green">📈</div>
          <div class="stat-info">
            <span class="stat-value">{{ averageScore.toFixed(1) }}</span>
            <span class="stat-label">平均分</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon purple">🏆</div>
          <div class="stat-info">
            <span class="stat-value">{{ highestScore }}</span>
            <span class="stat-label">最高分</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon orange">📉</div>
          <div class="stat-info">
            <span class="stat-value">{{ lowestScore }}</span>
            <span class="stat-label">最低分</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon red">✅</div>
          <div class="stat-info">
            <span class="stat-value">{{ passRate }}%</span>
            <span class="stat-label">及格率</span>
          </div>
        </div>
        <div class="stat-card">
          <div class="stat-icon cyan">⭐</div>
          <div class="stat-info">
            <span class="stat-value">{{ excellentRate }}%</span>
            <span class="stat-label">优秀率</span>
          </div>
        </div>
      </div>

      <div class="grade-distribution">
        <h4>成绩分布</h4>
        <div class="distribution-bars">
          <div class="bar-item">
            <span class="bar-label">优秀 (90-100)</span>
            <div class="bar-container">
              <div class="bar-fill excellent" :style="{ width: excellentCount / students.length * 100 + '%' }"></div>
            </div>
            <span class="bar-count">{{ excellentCount }}人</span>
          </div>
          <div class="bar-item">
            <span class="bar-label">良好 (80-89)</span>
            <div class="bar-container">
              <div class="bar-fill good" :style="{ width: goodCount / students.length * 100 + '%' }"></div>
            </div>
            <span class="bar-count">{{ goodCount }}人</span>
          </div>
          <div class="bar-item">
            <span class="bar-label">中等 (70-79)</span>
            <div class="bar-container">
              <div class="bar-fill medium" :style="{ width: mediumCount / students.length * 100 + '%' }"></div>
            </div>
            <span class="bar-count">{{ mediumCount }}人</span>
          </div>
          <div class="bar-item">
            <span class="bar-label">及格 (60-69)</span>
            <div class="bar-container">
              <div class="bar-fill pass" :style="{ width: passCount / students.length * 100 + '%' }"></div>
            </div>
            <span class="bar-count">{{ passCount }}人</span>
          </div>
          <div class="bar-item">
            <span class="bar-label">不及格 (&lt;60)</span>
            <div class="bar-container">
              <div class="bar-fill fail" :style="{ width: failCount / students.length * 100 + '%' }"></div>
            </div>
            <span class="bar-count">{{ failCount }}人</span>
          </div>
        </div>
      </div>
    </div>

    <div class="action-bar">
      <button class="btn btn-secondary" @click="clearAll">
        <span>🗑️</span> 清空数据
      </button>
      <button class="btn btn-secondary" @click="exportData">
        <span>📤</span> 导出成绩
      </button>
      <button class="btn btn-primary" @click="saveData">
        <span>💾</span> 保存数据
      </button>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'GradeCalculator',
  setup() {
    const weights = ref({
      usual: 20,
      midterm: 30,
      final: 40,
      homework: 10
    })

    const students = ref([
      { name: '张三', usual: 85, midterm: 78, final: 92, homework: 88 },
      { name: '李四', usual: 90, midterm: 85, final: 88, homework: 92 },
      { name: '王五', usual: 72, midterm: 68, final: 75, homework: 70 },
      { name: '赵六', usual: 88, midterm: 82, final: 90, homework: 85 },
      { name: '孙七', usual: 95, midterm: 91, final: 94, homework: 96 }
    ])

    const totalWeight = computed(() => {
      return weights.value.usual + weights.value.midterm + weights.value.final + weights.value.homework
    })

    const calculateTotal = (student) => {
      const { usual, midterm, final, homework } = student
      const total = 
        (usual * weights.value.usual / 100) +
        (midterm * weights.value.midterm / 100) +
        (final * weights.value.final / 100) +
        (homework * weights.value.homework / 100)
      return Math.round(total * 10) / 10
    }

    const updateTotal = (index) => {}

    const averageScore = computed(() => {
      if (students.value.length === 0) return 0
      const total = students.value.reduce((sum, student) => sum + calculateTotal(student), 0)
      return total / students.value.length
    })

    const highestScore = computed(() => {
      if (students.value.length === 0) return 0
      return Math.max(...students.value.map(s => calculateTotal(s)))
    })

    const lowestScore = computed(() => {
      if (students.value.length === 0) return 0
      return Math.min(...students.value.map(s => calculateTotal(s)))
    })

    const passCount = computed(() => {
      return students.value.filter(s => calculateTotal(s) >= 60).length
    })

    const passRate = computed(() => {
      if (students.value.length === 0) return 0
      return Math.round(passCount.value / students.value.length * 100)
    })

    const excellentCount = computed(() => {
      return students.value.filter(s => calculateTotal(s) >= 90).length
    })

    const excellentRate = computed(() => {
      if (students.value.length === 0) return 0
      return Math.round(excellentCount.value / students.value.length * 100)
    })

    const goodCount = computed(() => {
      return students.value.filter(s => calculateTotal(s) >= 80 && calculateTotal(s) < 90).length
    })

    const mediumCount = computed(() => {
      return students.value.filter(s => calculateTotal(s) >= 70 && calculateTotal(s) < 80).length
    })

    const failCount = computed(() => {
      return students.value.filter(s => calculateTotal(s) < 60).length
    })

    const addStudent = () => {
      students.value.push({
        name: '',
        usual: 0,
        midterm: 0,
        final: 0,
        homework: 0
      })
    }

    const removeStudent = (index) => {
      students.value.splice(index, 1)
    }

    const importScores = () => {
      alert('批量导入功能开发中...')
    }

    const clearAll = () => {
      if (confirm('确定要清空所有学生数据吗？')) {
        students.value = []
      }
    }

    const exportData = () => {
      alert('导出功能开发中...')
    }

    const saveData = () => {
      alert('数据已保存！')
    }

    return {
      weights,
      students,
      totalWeight,
      calculateTotal,
      updateTotal,
      averageScore,
      highestScore,
      lowestScore,
      passRate,
      excellentRate,
      excellentCount,
      goodCount,
      mediumCount,
      passCount,
      failCount,
      addStudent,
      removeStudent,
      importScores,
      clearAll,
      exportData,
      saveData
    }
  }
}
</script>

<style scoped>
.grade-calculator {
  padding: 20px;
}

.config-section {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.config-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.weight-inputs {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.weight-item label {
  display: block;
  font-size: 13px;
  color: #64748b;
  margin-bottom: 6px;
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
  flex: 1;
  border: none;
  padding: 10px 12px;
  font-size: 15px;
  text-align: center;
  outline: none;
}

.input-group .unit {
  padding: 10px 12px;
  background: #f1f5f9;
  color: #64748b;
  font-size: 14px;
}

.total-check {
  margin-top: 12px;
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.total-check.valid {
  background: #dcfce7;
  color: #166534;
}

.total-check.invalid {
  background: #fef2f2;
  color: #dc2626;
}

.warning {
  font-size: 13px;
}

.student-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.students-table {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 180px repeat(4, 100px) 100px 60px;
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
}

.col {
  padding: 14px 12px;
  font-size: 13px;
  color: #64748b;
  text-align: center;
  display: flex;
  align-items: center;
  justify-content: center;
}

.col-name {
  justify-content: flex-start;
  font-weight: 500;
  color: #1e293b;
}

.table-row {
  display: grid;
  grid-template-columns: 180px repeat(4, 100px) 100px 60px;
  border-bottom: 1px solid #f1f5f9;
  transition: background 0.2s ease;
}

.table-row:hover {
  background: #f8fafc;
}

.table-row.highScore {
  background: #f0fdf4;
}

.table-row.passScore {
  background: #fefce8;
}

.table-row.failScore {
  background: #fef2f2;
}

.table-row .col input {
  width: 100%;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 8px 10px;
  font-size: 14px;
  text-align: center;
  outline: none;
  transition: border-color 0.2s ease;
}

.table-row .col input:focus {
  border-color: #3b82f6;
}

.table-row .col-name input {
  text-align: left;
}

.total-score {
  font-weight: 600;
  font-size: 16px;
}

.total-score.high {
  color: #16a34a;
}

.total-score.pass {
  color: #ca8a04;
}

.total-score.fail {
  color: #dc2626;
}

.action-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: background 0.2s ease;
}

.action-btn:hover {
  background: #f1f5f9;
}

.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: #94a3b8;
}

.empty-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 12px;
}

.statistics-section {
  background: #f8fafc;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.statistics-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);
  gap: 12px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 10px;
  padding: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.stat-icon.blue { background: #eff6ff; }
.stat-icon.green { background: #f0fdf4; }
.stat-icon.purple { background: #faf5ff; }
.stat-icon.orange { background: #fff7ed; }
.stat-icon.red { background: #fef2f2; }
.stat-icon.cyan { background: #ecfeff; }

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #1e293b;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
}

.grade-distribution h4 {
  font-size: 14px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 12px;
}

.distribution-bars {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.bar-item {
  display: grid;
  grid-template-columns: 100px 1fr 60px;
  align-items: center;
  gap: 12px;
}

.bar-label {
  font-size: 13px;
  color: #64748b;
}

.bar-container {
  height: 24px;
  background: #f1f5f9;
  border-radius: 6px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  border-radius: 6px;
  transition: width 0.5s ease;
}

.bar-fill.excellent { background: linear-gradient(90deg, #22c55e, #16a34a); }
.bar-fill.good { background: linear-gradient(90deg, #3b82f6, #2563eb); }
.bar-fill.medium { background: linear-gradient(90deg, #eab308, #ca8a04); }
.bar-fill.pass { background: linear-gradient(90deg, #f97316, #ea580c); }
.bar-fill.fail { background: linear-gradient(90deg, #ef4444, #dc2626); }

.bar-count {
  font-size: 13px;
  color: #64748b;
  text-align: right;
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-secondary {
  background: white;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #f8fafc;
  border-color: #cbd5e1;
}

@media (max-width: 1200px) {
  .weight-inputs {
    grid-template-columns: repeat(2, 1fr);
  }

  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (max-width: 768px) {
  .weight-inputs {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .table-header,
  .table-row {
    grid-template-columns: 1fr;
  }

  .col {
    justify-content: flex-start;
    border-bottom: 1px solid #f1f5f9;
  }

  .col:last-child {
    border-bottom: none;
  }
}
</style>

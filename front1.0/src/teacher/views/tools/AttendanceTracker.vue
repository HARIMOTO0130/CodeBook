<template>
  <div class="attendance-tracker">
    <div class="tool-header">
      <div class="class-selector">
        <label>选择班级</label>
        <select v-model="selectedClass">
          <option value="">请选择班级</option>
          <option v-for="cls in classes" :key="cls.id" :value="cls.id">
            {{ cls.name }}
          </option>
        </select>
      </div>
      <div class="date-selector">
        <label>考勤日期</label>
        <input type="date" v-model="attendanceDate" />
      </div>
      <div class="session-selector">
        <label>课程节次</label>
        <select v-model="selectedSession">
          <option value="1">第1-2节</option>
          <option value="2">第3-4节</option>
          <option value="3">第5-6节</option>
          <option value="4">第7-8节</option>
          <option value="5">全天</option>
        </select>
      </div>
    </div>

    <div v-if="selectedClass" class="attendance-section">
      <div class="section-header">
        <h3>考勤记录</h3>
        <div class="header-actions">
          <button class="btn btn-secondary" @click="markAllPresent">
            <span>✅</span> 全部出勤
          </button>
          <button class="btn btn-secondary" @click="resetAll">
            <span>🔄</span> 重置
          </button>
        </div>
      </div>

      <div class="attendance-summary">
        <div class="summary-item present">
          <span class="summary-icon">✅</span>
          <span class="summary-value">{{ presentCount }}</span>
          <span class="summary-label">出勤</span>
        </div>
        <div class="summary-item absent">
          <span class="summary-icon">❌</span>
          <span class="summary-value">{{ absentCount }}</span>
          <span class="summary-label">缺勤</span>
        </div>
        <div class="summary-item late">
          <span class="summary-icon">⏰</span>
          <span class="summary-value">{{ lateCount }}</span>
          <span class="summary-label">迟到</span>
        </div>
        <div class="summary-item leave">
          <span class="summary-icon">📝</span>
          <span class="summary-value">{{ leaveCount }}</span>
          <span class="summary-label">请假</span>
        </div>
        <div class="summary-item early">
          <span class="summary-icon">🏃</span>
          <span class="summary-value">{{ earlyCount }}</span>
          <span class="summary-label">早退</span>
        </div>
      </div>

      <div class="students-list">
        <div
          v-for="student in students"
          :key="student.id"
          class="student-item"
          :class="{ expanded: expandedStudent === student.id }"
        >
          <div class="student-row" @click="toggleStudent(student.id)">
            <div class="student-info">
              <div class="student-avatar" :style="{ background: student.avatar }">
                {{ (student.name || 'S').charAt(0) }}
              </div>
              <div class="student-details">
                <span class="student-name">{{ student.name }}</span>
                <span class="student-id">{{ student.studentId }}</span>
              </div>
            </div>
            <div class="attendance-status">
              <span
                class="status-badge"
                :class="student.status"
              >
                {{ getStatusText(student.status) }}
              </span>
              <span class="expand-icon">{{ expandedStudent === student.id ? '▲' : '▼' }}</span>
            </div>
          </div>
          <div v-if="expandedStudent === student.id" class="student-expanded">
            <div class="status-buttons">
              <button
                v-for="status in statusOptions"
                :key="status.value"
                class="status-btn"
                :class="{ active: student.status === status.value }"
                @click="setStatus(student.id, status.value)"
              >
                <span class="status-icon">{{ status.icon }}</span>
                <span>{{ status.label }}</span>
              </button>
            </div>
            <div v-if="student.status === 'absent'" class="reason-input">
              <label>缺勤原因</label>
              <select v-model="student.reason">
                <option value="">请选择原因</option>
                <option value="sick">病假</option>
                <option value="personal">事假</option>
                <option value="unknown">未知原因</option>
              </select>
            </div>
            <div v-if="student.status === 'late'" class="time-input">
              <label>迟到时长</label>
              <input type="number" v-model.number="student.lateMinutes" min="0" max="120" placeholder="分钟" />
            </div>
            <div class="remark-input">
              <label>备注</label>
              <input type="text" v-model="student.remark" placeholder="添加备注..." />
            </div>
          </div>
        </div>
      </div>

      <div class="action-bar">
        <button class="btn btn-secondary" @click="exportAttendance">
          <span>📤</span> 导出考勤表
        </button>
        <button class="btn btn-primary" @click="saveAttendance">
          <span>💾</span> 保存考勤
        </button>
      </div>
    </div>

    <div v-else class="empty-state">
      <span class="empty-icon">📋</span>
      <p>请选择班级开始考勤记录</p>
    </div>

    <div class="history-section">
      <h3>考勤历史</h3>
      <div class="history-list">
        <div
          v-for="record in attendanceHistory"
          :key="record.id"
          class="history-item"
          @click="loadRecord(record)"
        >
          <div class="history-date">
            <span class="date-day">{{ formatDateDay(record.date) }}</span>
            <span class="date-month">{{ formatDateMonth(record.date) }}</span>
          </div>
          <div class="history-info">
            <span class="history-class">{{ record.className }}</span>
            <span class="history-stats">
              出勤 {{ record.present }}/{{ record.total }} ({{ record.rate }}%)
            </span>
          </div>
          <div class="history-status">
            <span
              class="status-indicator"
              :class="{ good: record.rate >= 95, ok: record.rate >= 85 && record.rate < 95, bad: record.rate < 85 }"
            ></span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'AttendanceTracker',
  setup() {
    const selectedClass = ref('')
    const attendanceDate = ref(new Date().toISOString().split('T')[0])
    const selectedSession = ref('1')
    const expandedStudent = ref(null)

    const classes = ref([
      { id: 1, name: '计算机科学1班' },
      { id: 2, name: '软件工程2班' },
      { id: 3, name: '数据科学1班' }
    ])

    const statusOptions = [
      { value: 'present', label: '出勤', icon: '✅' },
      { value: 'absent', label: '缺勤', icon: '❌' },
      { value: 'late', label: '迟到', icon: '⏰' },
      { value: 'leave', label: '请假', icon: '📝' },
      { value: 'early', label: '早退', icon: '🏃' }
    ]

    const students = ref([
      { id: 1, name: '张三', studentId: '2023001', status: 'present', avatar: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', lateMinutes: 0, reason: '', remark: '' },
      { id: 2, name: '李四', studentId: '2023002', status: 'present', avatar: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', lateMinutes: 0, reason: '', remark: '' },
      { id: 3, name: '王五', studentId: '2023003', status: 'absent', avatar: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', lateMinutes: 0, reason: 'personal', remark: '' },
      { id: 4, name: '赵六', studentId: '2023004', status: 'present', avatar: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', lateMinutes: 0, reason: '', remark: '' },
      { id: 5, name: '孙七', studentId: '2023005', status: 'late', avatar: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', lateMinutes: 15, reason: '', remark: '路上堵车' },
      { id: 6, name: '周八', studentId: '2023006', status: 'present', avatar: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)', lateMinutes: 0, reason: '', remark: '' },
      { id: 7, name: '吴九', studentId: '2023007', status: 'leave', avatar: 'linear-gradient(135deg, #d299c2 0%, #fef9d7 100%)', lateMinutes: 0, reason: '', remark: '病假' },
      { id: 8, name: '郑十', studentId: '2023008', status: 'present', avatar: 'linear-gradient(135deg, #89f7fe 0%, #66a6ff 100%)', lateMinutes: 0, reason: '', remark: '' }
    ])

    const attendanceHistory = ref([
      { id: 1, date: '2026-01-03', className: '计算机科学1班', present: 28, total: 30, rate: 93.3 },
      { id: 2, date: '2026-01-02', className: '计算机科学1班', present: 29, total: 30, rate: 96.7 },
      { id: 3, date: '2026-01-02', className: '软件工程2班', present: 25, total: 28, rate: 89.3 }
    ])

    const presentCount = computed(() => students.value.filter(s => s.status === 'present').length)
    const absentCount = computed(() => students.value.filter(s => s.status === 'absent').length)
    const lateCount = computed(() => students.value.filter(s => s.status === 'late').length)
    const leaveCount = computed(() => students.value.filter(s => s.status === 'leave').length)
    const earlyCount = computed(() => students.value.filter(s => s.status === 'early').length)

    const getStatusText = (status) => {
      const option = statusOptions.find(s => s.value === status)
      return option ? option.label : '未知'
    }

    const toggleStudent = (id) => {
      expandedStudent.value = expandedStudent.value === id ? null : id
    }

    const setStatus = (id, status) => {
      const student = students.value.find(s => s.id === id)
      if (student) {
        student.status = status
      }
    }

    const markAllPresent = () => {
      students.value.forEach(s => s.status = 'present')
    }

    const resetAll = () => {
      students.value.forEach(s => {
        s.status = 'present'
        s.lateMinutes = 0
        s.reason = ''
        s.remark = ''
      })
    }

    const formatDateDay = (dateStr) => {
      const date = new Date(dateStr)
      return date.getDate()
    }

    const formatDateMonth = (dateStr) => {
      const date = new Date(dateStr)
      return `${date.getMonth() + 1}月`
    }

    const loadRecord = (record) => {
      selectedClass.value = record.classId || 1
      attendanceDate.value = record.date
    }

    const exportAttendance = () => {
      alert('导出功能开发中...')
    }

    const saveAttendance = () => {
      alert('考勤记录已保存！')
    }

    return {
      selectedClass,
      attendanceDate,
      selectedSession,
      expandedStudent,
      classes,
      statusOptions,
      students,
      attendanceHistory,
      presentCount,
      absentCount,
      lateCount,
      leaveCount,
      earlyCount,
      getStatusText,
      toggleStudent,
      setStatus,
      markAllPresent,
      resetAll,
      formatDateDay,
      formatDateMonth,
      loadRecord,
      exportAttendance,
      saveAttendance
    }
  }
}
</script>

<style scoped>
.attendance-tracker {
  padding: 20px;
}

.tool-header {
  display: flex;
  gap: 20px;
  margin-bottom: 24px;
  background: #f8fafc;
  padding: 20px;
  border-radius: 12px;
}

.tool-header > div {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tool-header label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.tool-header select,
.tool-header input {
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  background: white;
  min-width: 180px;
}

.tool-header select:focus,
.tool-header input:focus {
  border-color: #3b82f6;
}

.attendance-section {
  margin-bottom: 32px;
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

.attendance-summary {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.summary-item {
  flex: 1;
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  border: 1px solid #e2e8f0;
}

.summary-icon {
  font-size: 28px;
}

.summary-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
}

.summary-label {
  font-size: 14px;
  color: #64748b;
}

.summary-item.present { border-left: 4px solid #22c55e; }
.summary-item.absent { border-left: 4px solid #ef4444; }
.summary-item.late { border-left: 4px solid #f59e0b; }
.summary-item.leave { border-left: 4px solid #3b82f6; }
.summary-item.early { border-left: 4px solid #8b5cf6; }

.students-list {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 24px;
}

.student-item {
  border-bottom: 1px solid #f1f5f9;
}

.student-item:last-child {
  border-bottom: none;
}

.student-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  cursor: pointer;
  transition: background 0.2s ease;
}

.student-row:hover {
  background: #f8fafc;
}

.student-item.expanded .student-row {
  background: #f1f5f9;
}

.student-info {
  display: flex;
  align-items: center;
  gap: 14px;
}

.student-avatar {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 18px;
}

.student-details {
  display: flex;
  flex-direction: column;
}

.student-name {
  font-size: 15px;
  font-weight: 500;
  color: #1e293b;
}

.student-id {
  font-size: 13px;
  color: #94a3b8;
}

.attendance-status {
  display: flex;
  align-items: center;
  gap: 12px;
}

.status-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

.status-badge.present { background: #dcfce7; color: #166534; }
.status-badge.absent { background: #fef2f2; color: #dc2626; }
.status-badge.late { background: #fef3c7; color: #d97706; }
.status-badge.leave { background: #dbeafe; color: #2563eb; }
.status-badge.early { background: #f3e8ff; color: #7c3aed; }

.expand-icon {
  color: #94a3b8;
  font-size: 12px;
}

.student-expanded {
  padding: 20px;
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
}

.status-buttons {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.status-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  background: white;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.status-btn:hover {
  border-color: #3b82f6;
}

.status-btn.active {
  background: #eff6ff;
  border-color: #3b82f6;
  color: #3b82f6;
}

.reason-input,
.time-input,
.remark-input {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.reason-input label,
.time-input label,
.remark-input label {
  font-size: 14px;
  color: #64748b;
  min-width: 80px;
}

.reason-input select,
.time-input input,
.remark-input input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
}

.action-bar {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.empty-state {
  padding: 80px 20px;
  text-align: center;
  background: #f8fafc;
  border-radius: 12px;
  margin-bottom: 32px;
}

.empty-icon {
  font-size: 64px;
  display: block;
  margin-bottom: 16px;
}

.empty-state p {
  color: #94a3b8;
  font-size: 16px;
}

.history-section h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 16px;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px 20px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.history-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);
}

.history-date {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 16px;
  background: #f8fafc;
  border-radius: 10px;
}

.date-day {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.date-month {
  font-size: 13px;
  color: #64748b;
}

.history-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-class {
  font-size: 15px;
  font-weight: 500;
  color: #1e293b;
}

.history-stats {
  font-size: 13px;
  color: #64748b;
}

.history-status {
  display: flex;
  align-items: center;
}

.status-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.status-indicator.good { background: #22c55e; }
.status-indicator.ok { background: #f59e0b; }
.status-indicator.bad { background: #ef4444; }

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

@media (max-width: 768px) {
  .tool-header {
    flex-direction: column;
  }

  .attendance-summary {
    flex-wrap: wrap;
  }

  .summary-item {
    min-width: calc(50% - 8px);
  }
}
</style>

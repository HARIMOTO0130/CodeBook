<template>
  <div class="calendar-tool">
    <div class="tool-header">
      <h2>教学日历</h2>
      <p>管理教学日程、课程安排和重要事件</p>
    </div>

    <div class="calendar-container">
      <div class="calendar-main">
        <div class="calendar-header">
          <button class="nav-btn" @click="previousMonth">
            <span>‹</span>
          </button>
          <h3>{{ currentYear }}年 {{ currentMonth + 1 }}月</h3>
          <button class="nav-btn" @click="nextMonth">
            <span>›</span>
          </button>
          <button class="today-btn" @click="goToToday">今天</button>
        </div>

        <div class="calendar-weekdays">
          <span v-for="day in weekDays" :key="day">{{ day }}</span>
        </div>

        <div class="calendar-grid">
          <div
            v-for="(day, index) in calendarDays"
            :key="index"
            class="calendar-day"
            :class="{
              'other-month': !day.isCurrentMonth,
              'today': day.isToday,
              'selected': day.date === selectedDate,
              'has-event': day.events.length > 0,
              'holiday': day.isHoliday
            }"
            @click="selectDate(day)"
          >
            <span class="day-number">{{ day.dayNumber }}</span>
            <div class="day-events">
              <span
                v-for="event in day.events.slice(0, 2)"
                :key="event.id"
                class="event-dot"
                :class="event.type"
                :title="event.title"
              ></span>
              <span v-if="day.events.length > 2" class="more-events">
                +{{ day.events.length - 2 }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="calendar-sidebar">
        <div class="selected-date-panel">
          <h4>{{ formattedSelectedDate }}</h4>
          <div class="date-info">
            <span v-if="selectedDayInfo?.lunar" class="lunar-date">
              农历: {{ selectedDayInfo.lunar }}
            </span>
            <span v-if="selectedDayInfo?.zodiac" class="zodiac">
              生肖: {{ selectedDayInfo.zodiac }}
            </span>
          </div>
        </div>

        <div class="events-panel">
          <div class="panel-header">
            <h4>日程安排</h4>
            <button class="add-event-btn" @click="showAddEventModal = true">
              + 添加
            </button>
          </div>
          <div class="events-list">
            <div
              v-for="event in selectedDateEvents"
              :key="event.id"
              class="event-item"
              :class="event.type"
            >
              <div class="event-time">{{ event.time }}</div>
              <div class="event-content">
                <span class="event-title">{{ event.title }}</span>
                <span class="event-desc">{{ event.description }}</span>
              </div>
              <button class="delete-event-btn" @click="deleteEvent(event.id)">
                ×
              </button>
            </div>
            <div v-if="selectedDateEvents.length === 0" class="no-events">
              <p>暂无日程安排</p>
              <button class="quick-add-btn" @click="showAddEventModal = true">
                快速添加
              </button>
            </div>
          </div>
        </div>

        <div class="holidays-panel">
          <h4>本月节假日</h4>
          <div class="holidays-list">
            <div
              v-for="holiday in currentMonthHolidays"
              :key="holiday.date"
              class="holiday-item"
            >
              <span class="holiday-date">{{ holiday.date }}日</span>
              <span class="holiday-name">{{ holiday.name }}</span>
            </div>
            <div v-if="currentMonthHolidays.length === 0" class="no-holidays">
              <p>本月无节假日</p>
            </div>
          </div>
        </div>

        <div class="quick-actions">
          <h4>快捷操作</h4>
          <div class="action-buttons">
            <button class="action-btn" @click="addCourseEvent">
              📚 添加课程
            </button>
            <button class="action-btn" @click="addExamEvent">
              📝 添加考试
            </button>
            <button class="action-btn" @click="addMeetingEvent">
              👥 添加会议
            </button>
            <button class="action-btn" @click="exportCalendar">
              📤 导出日历
            </button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showAddEventModal" class="modal-overlay" @click.self="showAddEventModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ editingEvent ? '编辑日程' : '添加日程' }}</h3>
          <button class="close-btn" @click="closeModal">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>标题</label>
            <input type="text" v-model="newEvent.title" placeholder="输入日程标题" />
          </div>
          <div class="form-group">
            <label>时间</label>
            <input type="time" v-model="newEvent.time" />
          </div>
          <div class="form-group">
            <label>类型</label>
            <select v-model="newEvent.type">
              <option value="course">课程</option>
              <option value="exam">考试</option>
              <option value="meeting">会议</option>
              <option value="assignment">作业</option>
              <option value="other">其他</option>
            </select>
          </div>
          <div class="form-group">
            <label>描述</label>
            <textarea v-model="newEvent.description" placeholder="输入详细描述"></textarea>
          </div>
          <div class="form-group">
            <label>重复</label>
            <select v-model="newEvent.repeat">
              <option value="none">不重复</option>
              <option value="daily">每天</option>
              <option value="weekly">每周</option>
              <option value="monthly">每月</option>
            </select>
          </div>
          <div class="form-group">
            <label>提醒</label>
            <select v-model="newEvent.reminder">
              <option value="none">无提醒</option>
              <option value="15">15分钟前</option>
              <option value="30">30分钟前</option>
              <option value="60">1小时前</option>
              <option value="1440">1天前</option>
            </select>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeModal">取消</button>
          <button class="save-btn" @click="saveEvent">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'

export default {
  name: 'CalendarTool',
  setup() {
    const currentDate = new Date()
    const currentYear = ref(currentDate.getFullYear())
    const currentMonth = ref(currentDate.getMonth())
    const selectedDate = ref(currentDate.toISOString().split('T')[0])
    const showAddEventModal = ref(false)
    const editingEvent = ref(null)
    const events = ref([])

    const weekDays = ['日', '一', '二', '三', '四', '五', '六']

    const newEvent = ref({
      title: '',
      time: '09:00',
      type: 'course',
      description: '',
      repeat: 'none',
      reminder: 'none'
    })

    const lunarCalendar = {
      1: { 1: { lunar: '正月初一', name: '春节' }, 15: { lunar: '正月十五', name: '元宵节' } },
      2: { 2: { lunar: '二月初二', name: '龙抬头' } },
      3: { 8: { lunar: '三月初八', name: '妇女节' } },
      4: { 4: { lunar: '四月初四', name: '清明节' }, 5: { lunar: '四月初五' } },
      5: { 1: { lunar: '五月初一', name: '劳动节' }, 5: { lunar: '五月初五', name: '端午节' } },
      6: { 1: { lunar: '六月初一', name: '儿童节' } },
      7: { 1: { lunar: '七月初一', name: '建党节' }, 7: { lunar: '七月初七', name: '七夕节' } },
      8: { 1: { lunar: '八月初一', name: '建军节' }, 15: { lunar: '八月十五', name: '中秋节' } },
      9: { 10: { lunar: '九月初十', name: '重阳节' }, 1: { lunar: '九月初一', name: '国庆节' } },
      10: { 1: { lunar: '十月初一' } },
      11: { 24: { lunar: '十一月二十四', name: '感恩节' } },
      12: { 8: { lunar: '十二月初八', name: '腊八节' }, 24: { lunar: '十二月二十四', name: '小年' }, 30: { lunar: '十二月三十', name: '除夕' } }
    }

    const zodiacs = ['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']

    const holidays = {
      '1-1': { name: '元旦' },
      '2-14': { name: '情人节' },
      '3-8': { name: '妇女节' },
      '4-1': { name: '愚人节' },
      '4-4': { name: '清明节' },
      '5-1': { name: '劳动节' },
      '5-4': { name: '青年节' },
      '6-1': { name: '儿童节' },
      '7-1': { name: '建党节' },
      '8-1': { name: '建军节' },
      '9-10': { name: '教师节' },
      '10-1': { name: '国庆节' },
      '11-24': { name: '感恩节' },
      '12-25': { name: '圣诞节' }
    }

    const calendarDays = computed(() => {
      const days = []
      const firstDay = new Date(currentYear.value, currentMonth.value, 1)
      const lastDay = new Date(currentYear.value, currentMonth.value + 1, 0)
      const startDate = new Date(firstDay)
      startDate.setDate(startDate.getDate() - firstDay.getDay())

      for (let i = 0; i < 42; i++) {
        const date = new Date(startDate)
        date.setDate(startDate.getDate() + i)
        const dateStr = date.toISOString().split('T')[0]
        const monthKey = date.getMonth() + 1
        const dayKey = date.getDate()

        const lunarInfo = lunarCalendar[monthKey]?.[dayKey] || {}
        const holidayKey = `${date.getMonth() + 1}-${date.getDate()}`
        const holidayInfo = holidays[holidayKey] || {}

        days.push({
          date: dateStr,
          dayNumber: date.getDate(),
          isCurrentMonth: date.getMonth() === currentMonth.value,
          isToday: dateStr === new Date().toISOString().split('T')[0],
          isHoliday: !!holidayInfo.name,
          lunar: lunarInfo.lunar || '',
          zodiac: date.getMonth() === 0 ? zodiacs[(date.getFullYear() - 1900) % 12] : '',
          events: events.value.filter(e => e.date === dateStr)
        })
      }

      return days
    })

    const formattedSelectedDate = computed(() => {
      if (!selectedDate.value) return '选择日期'
      const date = new Date(selectedDate.value)
      const options = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'long' }
      return date.toLocaleDateString('zh-CN', options)
    })

    const selectedDayInfo = computed(() => {
      const day = calendarDays.value.find(d => d.date === selectedDate.value)
      return day || {}
    })

    const selectedDateEvents = computed(() => {
      return events.value
        .filter(e => e.date === selectedDate.value)
        .sort((a, b) => a.time.localeCompare(b.time))
    })

    const currentMonthHolidays = computed(() => {
      const monthHolidays = []
      const monthKey = currentMonth.value + 1
      Object.entries(holidays).forEach(([key, value]) => {
        const [month, day] = key.split('-').map(Number)
        if (month === monthKey) {
          monthHolidays.push({ date: day, ...value })
        }
      })
      return monthHolidays.sort((a, b) => a.date - b.date)
    })

    const previousMonth = () => {
      if (currentMonth.value === 0) {
        currentMonth.value = 11
        currentYear.value--
      } else {
        currentMonth.value--
      }
    }

    const nextMonth = () => {
      if (currentMonth.value === 11) {
        currentMonth.value = 0
        currentYear.value++
      } else {
        currentMonth.value++
      }
    }

    const goToToday = () => {
      const today = new Date()
      currentYear.value = today.getFullYear()
      currentMonth.value = today.getMonth()
      selectedDate.value = today.toISOString().split('T')[0]
    }

    const selectDate = (day) => {
      selectedDate.value = day.date
    }

    const closeModal = () => {
      showAddEventModal.value = false
      editingEvent.value = null
      newEvent.value = {
        title: '',
        time: '09:00',
        type: 'course',
        description: '',
        repeat: 'none',
        reminder: 'none'
      }
    }

    const saveEvent = () => {
      if (!newEvent.value.title.trim()) {
        alert('请输入日程标题')
        return
      }

      const event = {
        id: editingEvent.value?.id || Date.now(),
        date: selectedDate.value,
        ...newEvent.value
      }

      if (editingEvent.value) {
        const index = events.value.findIndex(e => e.id === editingEvent.value.id)
        if (index !== -1) {
          events.value[index] = event
        }
      } else {
        events.value.push(event)
      }

      saveToLocalStorage()
      closeModal()
    }

    const deleteEvent = (eventId) => {
      const index = events.value.findIndex(e => e.id === eventId)
      if (index !== -1) {
        events.value.splice(index, 1)
        saveToLocalStorage()
      }
    }

    const addCourseEvent = () => {
      selectedDate.value = new Date().toISOString().split('T')[0]
      newEvent.value.type = 'course'
      newEvent.value.title = '新课程'
      newEvent.value.time = '09:00'
      showAddEventModal.value = true
    }

    const addExamEvent = () => {
      selectedDate.value = new Date().toISOString().split('T')[0]
      newEvent.value.type = 'exam'
      newEvent.value.title = '考试'
      newEvent.value.time = '14:00'
      showAddEventModal.value = true
    }

    const addMeetingEvent = () => {
      selectedDate.value = new Date().toISOString().split('T')[0]
      newEvent.value.type = 'meeting'
      newEvent.value.title = '会议'
      newEvent.value.time = '10:00'
      showAddEventModal.value = true
    }

    const exportCalendar = () => {
      const data = JSON.stringify(events.value, null, 2)
      const blob = new Blob([data], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `calendar_${currentYear.value}_${currentMonth.value + 1}.json`
      a.click()
      URL.revokeObjectURL(url)
    }

    const saveToLocalStorage = () => {
      localStorage.setItem('teacherCalendarEvents', JSON.stringify(events.value))
    }

    const loadFromLocalStorage = () => {
      const saved = localStorage.getItem('teacherCalendarEvents')
      if (saved) {
        try {
          events.value = JSON.parse(saved)
        } catch (e) {
          console.error('Failed to load calendar events')
        }
      }
    }

    onMounted(() => {
      loadFromLocalStorage()
    })

    return {
      currentYear,
      currentMonth,
      selectedDate,
      showAddEventModal,
      editingEvent,
      newEvent,
      weekDays,
      calendarDays,
      formattedSelectedDate,
      selectedDayInfo,
      selectedDateEvents,
      currentMonthHolidays,
      previousMonth,
      nextMonth,
      goToToday,
      selectDate,
      closeModal,
      saveEvent,
      deleteEvent,
      addCourseEvent,
      addExamEvent,
      addMeetingEvent,
      exportCalendar
    }
  }
}
</script>

<style scoped>
.calendar-tool {
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

.calendar-container {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
}

.calendar-main {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.calendar-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.calendar-header h3 {
  font-size: 20px;
  color: #1e293b;
  min-width: 180px;
  text-align: center;
}

.nav-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: #f1f5f9;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #64748b;
  transition: all 0.2s;
}

.nav-btn:hover {
  background: #e2e8f0;
  color: #1e293b;
}

.today-btn {
  padding: 8px 16px;
  border: none;
  background: #3b82f6;
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  margin-left: auto;
  transition: all 0.2s;
}

.today-btn:hover {
  background: #2563eb;
}

.calendar-weekdays {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 8px;
}

.calendar-weekdays span {
  text-align: center;
  padding: 12px;
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, 1fr);
  gap: 4px;
}

.calendar-day {
  aspect-ratio: 1;
  min-height: 80px;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
  border: 1px solid transparent;
}

.calendar-day:hover {
  background: #f1f5f9;
}

.calendar-day.other-month {
  opacity: 0.4;
}

.calendar-day.today {
  border-color: #3b82f6;
  background: #eff6ff;
}

.calendar-day.selected {
  background: #dbeafe;
  border-color: #3b82f6;
}

.calendar-day.has-event {
  background: #fef3c7;
}

.calendar-day.holiday {
  background: #fee2e2;
}

.day-number {
  font-size: 14px;
  font-weight: 500;
  color: #1e293b;
}

.calendar-day.other-month .day-number {
  color: #94a3b8;
}

.day-events {
  display: flex;
  flex-wrap: wrap;
  gap: 3px;
  margin-top: 4px;
}

.event-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
}

.event-dot.course {
  background: #3b82f6;
}

.event-dot.exam {
  background: #ef4444;
}

.event-dot.meeting {
  background: #22c55e;
}

.event-dot.assignment {
  background: #f59e0b;
}

.event-dot.other {
  background: #8b5cf6;
}

.more-events {
  font-size: 10px;
  color: #64748b;
}

.calendar-sidebar {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.selected-date-panel,
.events-panel,
.holidays-panel,
.quick-actions {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.selected-date-panel h4 {
  font-size: 16px;
  color: #1e293b;
  margin-bottom: 8px;
}

.date-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.lunar-date,
.zodiac {
  font-size: 12px;
  color: #64748b;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.panel-header h4 {
  font-size: 14px;
  color: #1e293b;
  margin: 0;
}

.add-event-btn {
  padding: 4px 12px;
  border: none;
  background: #3b82f6;
  color: white;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.add-event-btn:hover {
  background: #2563eb;
}

.events-list {
  max-height: 200px;
  overflow-y: auto;
}

.event-item {
  display: flex;
  gap: 8px;
  padding: 8px;
  border-radius: 8px;
  margin-bottom: 8px;
  background: #f8fafc;
  position: relative;
}

.event-item.course {
  border-left: 3px solid #3b82f6;
}

.event-item.exam {
  border-left: 3px solid #ef4444;
}

.event-item.meeting {
  border-left: 3px solid #22c55e;
}

.event-item.assignment {
  border-left: 3px solid #f59e0b;
}

.event-item.other {
  border-left: 3px solid #8b5cf6;
}

.event-time {
  font-size: 12px;
  color: #64748b;
  min-width: 50px;
}

.event-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.event-title {
  font-size: 13px;
  color: #1e293b;
  font-weight: 500;
}

.event-desc {
  font-size: 11px;
  color: #94a3b8;
}

.delete-event-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  width: 20px;
  height: 20px;
  border: none;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
  opacity: 0;
  transition: opacity 0.2s;
}

.event-item:hover .delete-event-btn {
  opacity: 1;
}

.no-events {
  text-align: center;
  padding: 16px;
  color: #94a3b8;
}

.quick-add-btn {
  margin-top: 8px;
  padding: 6px 12px;
  border: none;
  background: #f1f5f9;
  color: #64748b;
  border-radius: 6px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
}

.quick-add-btn:hover {
  background: #e2e8f0;
}

.holidays-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.holiday-item {
  display: flex;
  justify-content: space-between;
  padding: 8px;
  background: #fef2f2;
  border-radius: 6px;
}

.holiday-date {
  font-size: 13px;
  color: #64748b;
}

.holiday-name {
  font-size: 13px;
  color: #ef4444;
  font-weight: 500;
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.action-btn {
  padding: 10px 12px;
  border: none;
  background: #f1f5f9;
  color: #475569;
  border-radius: 8px;
  cursor: pointer;
  font-size: 12px;
  transition: all 0.2s;
  text-align: center;
}

.action-btn:hover {
  background: #e2e8f0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 90%;
  max-width: 480px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  font-size: 18px;
  color: #1e293b;
  margin: 0;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f1f5f9;
  border-radius: 8px;
  cursor: pointer;
  font-size: 20px;
  color: #64748b;
  transition: all 0.2s;
}

.close-btn:hover {
  background: #e2e8f0;
  color: #1e293b;
}

.modal-body {
  padding: 24px;
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
  min-height: 80px;
  resize: vertical;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid #e2e8f0;
}

.cancel-btn {
  padding: 10px 20px;
  border: none;
  background: #f1f5f9;
  color: #475569;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: #e2e8f0;
}

.save-btn {
  padding: 10px 20px;
  border: none;
  background: #3b82f6;
  color: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
}

.save-btn:hover {
  background: #2563eb;
}

@media (max-width: 1024px) {
  .calendar-container {
    grid-template-columns: 1fr;
  }
}
</style>

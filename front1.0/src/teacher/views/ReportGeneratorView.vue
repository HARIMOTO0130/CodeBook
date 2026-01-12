<template>
  <div class="report-generator">
    <div class="page-header">
      <div class="header-left">
        <h1>学习报告生成</h1>
        <p>生成学生学习数据分析报告</p>
      </div>
      <div class="header-right">
        <button class="btn btn-secondary" @click="showTemplateModal = true">
          <span>📋</span> 报告模板
        </button>
        <button class="btn btn-primary" @click="generateReport" :disabled="!canGenerate || loading">
          <span v-if="loading">⏳</span>
          <span v-else>📊</span> {{ loading ? '生成中...' : '生成报告' }}
        </button>
      </div>
    </div>

    <div class="report-config">
      <div class="config-section">
        <h2>报告配置</h2>
        
        <div class="form-group">
          <label>报告类型 *</label>
          <div class="radio-group">
            <label class="radio-option">
              <input type="radio" v-model="config.type" value="student" />
              <span>学生个人报告</span>
            </label>
            <label class="radio-option">
              <input type="radio" v-model="config.type" value="class" />
              <span>班级整体报告</span>
            </label>
            <label class="radio-option">
              <input type="radio" v-model="config.type" value="comparison" />
              <span>对比分析报告</span>
            </label>
          </div>
        </div>

        <div class="form-group">
          <label>选择班级 *</label>
          <select v-model="config.classId" @change="onClassChange">
            <option value="">请选择班级</option>
            <option v-for="cls in classes" :key="cls.id" :value="cls.id">
              {{ cls.name }}
            </option>
          </select>
        </div>

        <div v-if="config.type === 'student'" class="form-group">
          <label>选择学生 *</label>
          <select v-model="config.studentId" :disabled="config.classId === '' || config.classId === undefined || config.classId === null">
            <option value="">请先选择班级</option>
            <option v-for="student in students" :key="student.id" :value="student.id">
              {{ student.student_name }} ({{ student.student_no }})
            </option>
          </select>
        </div>

        <div class="form-group">
          <label>时间范围 *</label>
          <div class="date-range">
            <input type="date" v-model="config.startDate" />
            <span>至</span>
            <input type="date" v-model="config.endDate" />
          </div>
        </div>

        <div class="form-group">
          <label>报告内容</label>
          <div class="checkbox-group">
            <label class="checkbox-option">
              <input type="checkbox" v-model="config.includeProgress" />
              <span>学习进度</span>
            </label>
            <label class="checkbox-option">
              <input type="checkbox" v-model="config.includeHomework" />
              <span>作业完成情况</span>
            </label>
            <label class="checkbox-option">
              <input type="checkbox" v-model="config.includeAttendance" />
              <span>出勤统计</span>
            </label>
            <label class="checkbox-option">
              <input type="checkbox" v-model="config.includePerformance" />
              <span>成绩分析</span>
            </label>
          </div>
        </div>

        <div class="form-group">
          <label>导出格式</label>
          <div class="radio-group">
            <label class="radio-option">
              <input type="radio" v-model="config.format" value="pdf" />
              <span>📄 PDF</span>
            </label>
            <label class="radio-option">
              <input type="radio" v-model="config.format" value="excel" />
              <span>📊 Excel</span>
            </label>
            <label class="radio-option">
              <input type="radio" v-model="config.format" value="word" />
              <span>📝 Word</span>
            </label>
          </div>
        </div>
      </div>

      <div class="preview-section">
        <h2>报告预览</h2>
        <div v-if="!reportData" class="preview-placeholder">
          <div class="placeholder-icon">📊</div>
          <p>配置完成后点击"生成报告"查看预览</p>
        </div>
        <div v-else class="report-preview">
          <div class="report-header">
            <h3>{{ reportData.title }}</h3>
            <p class="report-meta">
              生成时间: {{ reportData.generatedAt }} | 
              报告类型: {{ getReportTypeName(config.type) }}
            </p>
          </div>

          <div class="report-body">
            <div v-if="config.includeProgress" class="report-section">
              <h4>📈 学习进度</h4>
              <div class="progress-stats">
                <div class="stat-item">
                  <span class="stat-label">总章节数</span>
                  <span class="stat-value">{{ reportData.progress?.totalChapters || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">已完成</span>
                  <span class="stat-value">{{ reportData.progress?.completedChapters || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">完成率</span>
                  <span class="stat-value">{{ reportData.progress?.completionRate || 0 }}%</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">学习时长</span>
                  <span class="stat-value">{{ reportData.progress?.totalTime || 0 }}小时</span>
                </div>
              </div>
            </div>

            <div v-if="config.includeHomework" class="report-section">
              <h4>📝 作业完成情况</h4>
              <div class="homework-stats">
                <div class="stat-item">
                  <span class="stat-label">总作业数</span>
                  <span class="stat-value">{{ reportData.homework?.total || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">已提交</span>
                  <span class="stat-value">{{ reportData.homework?.submitted || 0 }}</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">平均分</span>
                  <span class="stat-value">{{ reportData.homework?.avgScore || 0 }}分</span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">提交率</span>
                  <span class="stat-value">{{ reportData.homework?.submissionRate || 0 }}%</span>
                </div>
              </div>
            </div>

            <div v-if="config.includePerformance" class="report-section">
              <h4>🎯 成绩分析</h4>
              <div class="performance-chart">
                <p class="chart-placeholder">成绩趋势图表将在此显示</p>
              </div>
            </div>
          </div>

          <div class="report-footer">
            <p>报告生成人: {{ teacherName }}</p>
            <p>数据来源: CodeBook教学平台</p>
          </div>
        </div>
      </div>
    </div>

    <div class="history-section">
      <h2>历史报告</h2>
      <div v-if="historyReports.length === 0" class="empty-state">
        <p>暂无历史报告</p>
      </div>
      <div v-else class="history-list">
        <div v-for="report in historyReports" :key="report.id" class="history-item">
          <div class="history-icon">📊</div>
          <div class="history-info">
            <h4>{{ report.title }}</h4>
            <p>{{ report.start_date || report.created_at || report.generated_at }} · {{ report.report_type || '报告' }}</p>
          </div>
          <div class="history-actions">
            <button class="action-btn" @click="viewReport(report)">查看</button>
            <button class="action-btn" @click="downloadReport(report)">下载</button>
            <button class="action-btn danger" @click="deleteReport(report)">删除</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { classApi } from '../api/class'
import { studentApi } from '../api/student'
import api from '../api/index'

export default {
  name: 'ReportGeneratorView',
  data() {
    return {
      showTemplateModal: false,
      loading: false,
      config: {
        type: 'class',
        classId: '',
        studentId: '',
        startDate: '',
        endDate: '',
        includeProgress: true,
        includeHomework: true,
        includeAttendance: false,
        includePerformance: true,
        format: 'pdf'
      },
      classes: [],
      students: [],
      reportData: null,
      historyReports: [],
      teacherName: '教师'
    }
  },
  computed: {
    canGenerate() {
      if (!this.config.classId || !this.config.startDate || !this.config.endDate) {
        return false
      }
      if (this.config.type === 'student' && !this.config.studentId) {
        return false
      }
      return true
    }
  },
  watch: {
    // 当报告类型切换为学生个人报告时，检查是否已选择班级，如果已选择则加载学生列表
    'config.type': function(newType, oldType) {
      if (newType === 'student' && this.config.classId !== '' && this.config.classId !== undefined && this.config.classId !== null) {
        this.onClassChange()
      }
    },
    // 当班级ID变化时，自动加载学生列表
    'config.classId': function(newClassId, oldClassId) {
      console.log('班级ID变化:', { newClassId, oldClassId })
      if (this.config.type === 'student' && newClassId !== '' && newClassId !== undefined && newClassId !== null) {
        this.onClassChange()
      }
    }
  },
  mounted() {
    this.loadClasses()
    this.loadTeacherInfo()
    this.setDefaultDates()
    this.loadHistoryReports()
  },
  methods: {
    async loadHistoryReports() {
      try {
        this.loading = true
        // 调用后端API获取历史报告列表
        const response = await api.get('/reports/')
        // 确保historyReports是数组，并且过滤掉null值
        this.historyReports = Array.isArray(response.data) 
          ? response.data.filter(report => report && report.id) 
          : []
      } catch (error) {
        console.error('加载历史报告失败:', error)
        this.historyReports = []
      } finally {
        this.loading = false
      }
    },
    loadTeacherInfo() {
      const userFullName = localStorage.getItem('userFullName') || '教师'
      this.teacherName = userFullName
    },
    setDefaultDates() {
      const today = new Date()
      const oneMonthAgo = new Date(today)
      oneMonthAgo.setMonth(today.getMonth() - 1)
      
      this.config.endDate = today.toISOString().split('T')[0]
      this.config.startDate = oneMonthAgo.toISOString().split('T')[0]
    },
    async loadClasses() {
      try {
        const response = await classApi.getClasses()
        // 处理不同的数据格式
        let classesData = []
        if (response.data) {
          if (Array.isArray(response.data)) {
            classesData = response.data
          } else if (Array.isArray(response.data.results)) {
            classesData = response.data.results
          }
        }
        
        // 确保classesData是数组，并且过滤掉null值
        this.classes = Array.isArray(classesData) 
          ? classesData.filter(cls => cls && cls.id) 
          : []
      } catch (error) {
        console.error('加载班级失败:', error)
        this.classes = []
      }
    },
    async onClassChange() {
      console.log('onClassChange被调用:', {
        classId: this.config.classId,
        classIdType: typeof this.config.classId,
        classIdEmpty: this.config.classId === '',
        classIdFalsy: !this.config.classId
      })
      
      // 确保classId是有效的（非空字符串、包括0在内的数字）
      const classId = this.config.classId
      // 只有当classId是空字符串或undefined或null时，才返回
      if (classId === '' || classId === undefined || classId === null) {
        this.students = []
        return
      }
      
      try {
        console.log('准备调用API获取学生列表，class_id:', classId)
        const response = await studentApi.getStudents({ class_id: classId })
        console.log('API响应:', response.data)
        
        let studentsData = []
        if (response.data) {
          if (Array.isArray(response.data)) {
            studentsData = response.data
          } else if (Array.isArray(response.data.results)) {
            studentsData = response.data.results
          }
        }
        
        console.log('处理后的学生数据:', studentsData)
        
        // 确保studentsData是数组，并且过滤掉null值
        this.students = Array.isArray(studentsData) 
          ? studentsData.filter(student => student && student.id) 
          : []
        
        console.log('最终学生列表:', this.students)
      } catch (error) {
        console.error('加载学生失败:', error)
        this.students = []
      }
    },
    getReportTypeName(type) {
      const typeMap = {
        student: '学生个人报告',
        class: '班级整体报告',
        comparison: '对比分析报告'
      }
      return typeMap[type] || '未知类型'
    },
    async generateReport() {
      if (!this.canGenerate) {
        alert('请完善报告配置')
        return
      }

      try {
        // 显示加载状态
        this.loading = true
        
        // 准备报告参数
        const reportParams = {
          report_type: this.config.type,
          class_id: this.config.classId,
          student_id: this.config.studentId,
          start_date: this.config.startDate,
          end_date: this.config.endDate,
          include_progress: this.config.includeProgress,
          include_homework: this.config.includeHomework,
          include_attendance: this.config.includeAttendance,
          include_performance: this.config.includePerformance,
          export_format: this.config.format
        }
        
        // 调用后端API生成报告
        const response = await api.post('/reports/', reportParams)
        
        // 获取报告预览数据
        const previewResponse = await api.get(`/reports/${response.data.id}/preview/`)
        
        // 更新报告数据
        this.reportData = previewResponse.data
        this.reportData.generatedAt = new Date().toLocaleString('zh-CN')
        
        // 更新历史报告列表
        await this.loadHistoryReports()
        
        alert('报告生成成功！')
      } catch (error) {
        console.error('生成报告失败:', error)
        alert('生成报告失败: ' + (error.response?.data?.error || error.message || error))
      } finally {
        this.loading = false
      }
    },
    getClassName() {
      const cls = this.classes.find(c => c.id === parseInt(this.config.classId))
      return cls ? cls.name : '未知班级'
    },
    getStudentName() {
      const student = this.students.find(s => s.id === parseInt(this.config.studentId))
      return student ? student.student_name : '未知学生'
    },
    viewReport(report) {
      console.log('查看报告:', report)
    },
    downloadReport(report) {
      console.log('下载报告:', report)
    },
    deleteReport(report) {
      if (confirm('确定要删除这份报告吗？')) {
        console.log('删除报告:', report)
      }
    }
  }
}
</script>

<style scoped>
.report-generator {
  padding: 24px;
  background: #f8fafc;
  min-height: 100%;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-left h1 {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
  margin: 0 0 4px 0;
}

.header-left p {
  color: #64748b;
  margin: 0;
}

.header-right {
  display: flex;
  gap: 12px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: white;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #f1f5f9;
}

.report-config {
  display: grid;
  grid-template-columns: 400px 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.config-section,
.preview-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.config-section h2,
.preview-section h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 20px 0;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.form-group select,
.form-group input[type="date"] {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
}

.form-group select:focus,
.form-group input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.radio-group,
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.radio-option,
.checkbox-option {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.radio-option:hover,
.checkbox-option:hover {
  background: #f8fafc;
  border-color: #3b82f6;
}

.radio-option input,
.checkbox-option input {
  cursor: pointer;
}

.date-range {
  display: flex;
  align-items: center;
  gap: 12px;
}

.date-range input {
  flex: 1;
}

.date-range span {
  color: #64748b;
}

.preview-placeholder {
  text-align: center;
  padding: 60px 20px;
  color: #94a3b8;
}

.placeholder-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.report-preview {
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 24px;
  background: #fafbfc;
}

.report-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e2e8f0;
}

.report-header h3 {
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 8px 0;
}

.report-meta {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

.report-body {
  margin-bottom: 24px;
}

.report-section {
  margin-bottom: 24px;
  padding: 20px;
  background: white;
  border-radius: 10px;
}

.report-section h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 16px 0;
}

.progress-stats,
.homework-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
}

.stat-label {
  display: block;
  font-size: 12px;
  color: #64748b;
  margin-bottom: 8px;
}

.stat-value {
  display: block;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

.performance-chart {
  padding: 40px;
  background: #f8fafc;
  border-radius: 8px;
  text-align: center;
}

.chart-placeholder {
  color: #94a3b8;
  margin: 0;
}

.report-footer {
  padding-top: 16px;
  border-top: 1px solid #e2e8f0;
  font-size: 12px;
  color: #64748b;
}

.report-footer p {
  margin: 4px 0;
}

.history-section {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.history-section h2 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 20px 0;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #94a3b8;
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
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  transition: all 0.2s;
}

.history-item:hover {
  background: #f1f5f9;
}

.history-icon {
  width: 48px;
  height: 48px;
  background: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.history-info {
  flex: 1;
}

.history-info h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.history-info p {
  margin: 0;
  font-size: 13px;
  color: #64748b;
}

.history-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background: #f1f5f9;
}

.action-btn.danger {
  color: #dc2626;
  border-color: #fecaca;
}

.action-btn.danger:hover {
  background: #fef2f2;
}

@media (max-width: 1200px) {
  .report-config {
    grid-template-columns: 1fr;
  }
  
  .progress-stats,
  .homework-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>

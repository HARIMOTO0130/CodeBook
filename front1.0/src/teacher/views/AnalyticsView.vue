<template>
  <div class="analytics-dashboard">
    <div class="page-header">
      <div class="header-left">
        <h1>数据分析</h1>
        <p>全面了解班级和学生学习情况，生成分析报告</p>
      </div>
      <div class="header-right">
        <select v-model="selectedClass" class="class-selector">
          <option value="all">全部班级</option>
          <option v-for="cls in classes" :key="cls.id" :value="cls.id">
            {{ cls.name }}
          </option>
        </select>
        <select v-model="timeRange" class="time-selector">
          <option value="week">最近一周</option>
          <option value="month">最近一月</option>
          <option value="semester">本学期</option>
          <option value="year">本学年</option>
        </select>
        <button class="btn btn-secondary" @click="exportReport">
          <span>📊</span> 导出报告
        </button>
      </div>
    </div>

    <div class="overview-stats">
      <div class="stat-card">
        <div class="stat-header">
          <span class="stat-icon">👥</span>
          <span class="stat-trend up">↑ 12%</span>
        </div>
        <div class="stat-value">{{ stats.totalStudents }}</div>
        <div class="stat-label">学生总数</div>
        <div class="stat-comparison">较上月增加 12 人</div>
      </div>
      <div class="stat-card">
        <div class="stat-header">
          <span class="stat-icon">📚</span>
          <span class="stat-trend up">↑ 8%</span>
        </div>
        <div class="stat-value">{{ stats.avgProgress }}%</div>
        <div class="stat-label">平均学习进度</div>
        <div class="stat-comparison">领先学期目标 5%</div>
      </div>
      <div class="stat-card">
        <div class="stat-header">
          <span class="stat-icon">📝</span>
          <span class="stat-trend down">↓ 3%</span>
        </div>
        <div class="stat-value">{{ stats.avgScore }}</div>
        <div class="stat-label">平均成绩</div>
        <div class="stat-comparison">优秀率 {{ stats.excellentRate }}%</div>
      </div>
      <div class="stat-card">
        <div class="stat-header">
          <span class="stat-icon">⏱️</span>
          <span class="stat-trend up">↑ 15%</span>
        </div>
        <div class="stat-value">{{ stats.avgStudyTime }}</div>
        <div class="stat-label">平均学习时长</div>
        <div class="stat-comparison">每日 {{ stats.dailyStudyTime }} 小时</div>
      </div>
    </div>

    <div class="charts-section">
      <div class="chart-card large">
        <div class="card-header">
          <h3>学习进度趋势</h3>
          <div class="chart-legend">
            <span class="legend-item"><span class="dot blue"></span> 平均进度</span>
            <span class="legend-item"><span class="dot green"></span> 目标进度</span>
          </div>
        </div>
        <div class="chart-container">
          <div class="chart-area">
            <div class="y-axis">
              <span>100%</span>
              <span>75%</span>
              <span>50%</span>
              <span>25%</span>
              <span>0%</span>
            </div>
            <div class="chart-bars">
              <div v-for="(data, index) in progressTrend" :key="index" class="bar-group">
                <div class="bar target" :style="{ height: data.target + '%' }"></div>
                <div class="bar actual" :style="{ height: data.actual + '%' }"></div>
                <span class="bar-label">{{ data.week }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-card">
        <div class="card-header">
          <h3>成绩分布</h3>
        </div>
        <div class="chart-container">
          <div class="donut-chart">
            <div class="donut-center">
              <span class="donut-value">{{ stats.avgScore }}</span>
              <span class="donut-label">平均分</span>
            </div>
            <svg viewBox="0 0 36 36" class="donut">
              <circle cx="18" cy="18" r="15.91549430918954" fill="transparent" stroke="#e2e8f0" stroke-width="3" />
              <circle cx="18" cy="18" r="15.91549430918954" fill="transparent" stroke="#ef4444" stroke-width="3" :stroke-dasharray="`${scoreDistribution.excellent} 100`" stroke-dashoffset="25" transform="rotate(-90 18 18)" />
              <circle cx="18" cy="18" r="15.91549430918954" fill="transparent" stroke="#f59e0b" stroke-width="3" :stroke-dasharray="`${scoreDistribution.good} 100`" stroke-dashoffset="75" transform="rotate(-90 18 18)" />
              <circle cx="18" cy="18" r="15.91549430918954" fill="transparent" stroke="#3b82f6" stroke-width="3" :stroke-dasharray="`${scoreDistribution.average} 100`" stroke-dashoffset="125" transform="rotate(-90 18 18)" />
              <circle cx="18" cy="18" r="15.91549430918954" fill="transparent" stroke="#64748b" stroke-width="3" :stroke-dasharray="`${scoreDistribution.pass} 100`" stroke-dashoffset="175" transform="rotate(-90 18 18)" />
            </svg>
          </div>
          <div class="chart-legend-vertical">
            <div class="legend-row">
              <span class="legend-color" style="background: #ef4444"></span>
              <span>优秀 (90-100)</span>
              <span class="legend-value">{{ scoreDistribution.excellent }}%</span>
            </div>
            <div class="legend-row">
              <span class="legend-color" style="background: #f59e0b"></span>
              <span>良好 (80-89)</span>
              <span class="legend-value">{{ scoreDistribution.good }}%</span>
            </div>
            <div class="legend-row">
              <span class="legend-color" style="background: #3b82f6"></span>
              <span>中等 (70-79)</span>
              <span class="legend-value">{{ scoreDistribution.average }}%</span>
            </div>
            <div class="legend-row">
              <span class="legend-color" style="background: #64748b"></span>
              <span>及格 (60-69)</span>
              <span class="legend-value">{{ scoreDistribution.pass }}%</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="data-section">
      <div class="section-card">
        <div class="card-header">
          <h3>班级排名</h3>
          <router-link to="/teacher/classes" class="view-all">查看全部 →</router-link>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>排名</th>
              <th>班级</th>
              <th>学生数</th>
              <th>平均进度</th>
              <th>平均成绩</th>
              <th>学习时长</th>
              <th>趋势</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(cls, index) in classRankings" :key="cls.id">
              <td>
                <span class="rank-badge" :class="getRankClass(index)">{{ index + 1 }}</span>
              </td>
              <td>
                <div class="class-info">
                  <span class="class-name">{{ cls.name }}</span>
                  <span class="class-teacher">{{ cls.teacher }}</span>
                </div>
              </td>
              <td>{{ cls.students }} 人</td>
              <td>
                <div class="progress-cell">
                  <div class="progress-bar">
                    <div class="progress-fill" :style="{ width: cls.progress + '%' }"></div>
                  </div>
                  <span>{{ cls.progress }}%</span>
                </div>
              </td>
              <td>
                <span class="score-badge" :class="getScoreClass(cls.score)">{{ cls.score }}</span>
              </td>
              <td>{{ cls.studyTime }} 小时</td>
              <td>
                <span class="trend-badge" :class="cls.trend > 0 ? 'up' : 'down'">
                  {{ cls.trend > 0 ? '↑' : '↓' }} {{ Math.abs(cls.trend) }}%
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="section-card">
        <div class="card-header">
          <h3>学习活跃度</h3>
        </div>
        <div class="activity-heatmap">
          <div class="heatmap-header">
            <span></span>
            <span v-for="day in weekDays" :key="day">{{ day }}</span>
          </div>
          <div v-for="hour in studyHours" :key="hour" class="heatmap-row">
            <span class="hour-label">{{ hour }}:00</span>
            <div
              v-for="(value, dayIndex) in getActivityData(hour)"
              :key="dayIndex"
              class="heatmap-cell"
              :style="{ background: getActivityColor(value) }"
              :title="`${hour}:00 - ${value}人在线`"
            ></div>
          </div>
        </div>
        <div class="activity-summary">
          <div class="summary-item">
            <span class="summary-label">最活跃时段</span>
            <span class="summary-value">{{ activitySummary.peak_period }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">日均在线</span>
            <span class="summary-value">{{ activitySummary.daily_avg_online }} 人</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">峰值在线</span>
            <span class="summary-value">{{ activitySummary.peak_online }} 人</span>
          </div>
        </div>
      </div>
    </div>

    <div class="students-section">
      <div class="section-header">
        <h3>学生表现分析</h3>
        <div class="section-actions">
          <select v-model="studentFilter">
            <option value="all">全部学生</option>
            <option value="excellent">优秀学生</option>
            <option value="improving">进步学生</option>
            <option value="struggling">需要关注</option>
          </select>
        </div>
      </div>
      <div class="students-grid">
        <div
          v-for="student in filteredStudents"
          :key="student.id"
          class="student-card"
          @click="viewStudentDetail(student)"
        >
          <div class="student-header">
            <div class="student-avatar" :style="{ background: student.avatarColor }">
              {{ (student.name || 'S').charAt(0) }}
            </div>
            <div class="student-badges">
              <span v-if="student.isExcellent" class="badge excellent">优秀</span>
              <span v-if="student.isImproving" class="badge improving">进步</span>
              <span v-if="student.needsAttention" class="badge warning">关注</span>
            </div>
          </div>
          <div class="student-info">
            <h4>{{ student.name }}</h4>
            <p>{{ student.studentId }} · {{ student.className }}</p>
          </div>
          <div class="student-metrics">
            <div class="metric">
              <span class="metric-label">进度</span>
              <div class="metric-bar">
                <div class="metric-fill" :style="{ width: student.progress + '%' }"></div>
              </div>
              <span class="metric-value">{{ student.progress }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">成绩</span>
              <span class="metric-score" :class="getScoreClass(student.score)">
                {{ student.score }}
              </span>
            </div>
          </div>
          <div class="student-footer">
            <span class="study-time">📚 {{ student.studyTime }} 小时</span>
            <span class="assignment-rate">📝 {{ student.completionRate }}% 完成率</span>
          </div>
        </div>
      </div>
    </div>

    <div class="content-analysis">
      <div class="section-card full-width">
        <div class="card-header">
          <h3>内容学习统计</h3>
        </div>
        <div class="content-stats-grid">
          <div class="content-stat-item" v-for="content in contentStats" :key="content.id">
            <div class="content-icon" :class="content.type">{{ getContentIcon(content.type) }}</div>
            <div class="content-info">
              <h4>{{ content.title }}</h4>
              <p>{{ content.description }}</p>
            </div>
            <div class="content-metrics">
              <div class="content-metric">
                <span class="metric-num">{{ content.views }}</span>
                <span class="metric-lbl">浏览</span>
              </div>
              <div class="content-metric">
                <span class="metric-num">{{ content.completion }}</span>
                <span class="metric-lbl">完成率</span>
              </div>
              <div class="content-metric">
                <span class="metric-num">{{ content.avgScore }}</span>
                <span class="metric-lbl">平均分</span>
              </div>
            </div>
            <div class="content-trend">
              <span :class="content.trend > 0 ? 'up' : 'down'">
                {{ content.trend > 0 ? '↑' : '↓' }} {{ Math.abs(content.trend) }}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="recommendations-section">
      <div class="section-card full-width">
        <div class="card-header">
          <h3>教学建议</h3>
          <span class="ai-badge">AI 智能分析</span>
        </div>
        <div class="recommendations-list">
          <div class="recommendation-item" v-for="rec in recommendations" :key="rec.id">
            <div class="rec-icon" :class="rec.type">{{ rec.icon }}</div>
            <div class="rec-content">
              <h4>{{ rec.title }}</h4>
              <p>{{ rec.description }}</p>
              <div class="rec-meta">
                <span class="rec-impact">影响: {{ rec.impact }}</span>
                <span class="rec-priority" :class="rec.priority">{{ rec.priority }}</span>
              </div>
            </div>
            <button class="rec-action btn btn-primary">{{ rec.action }}</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { analyticsApi } from '../api/analytics'
import { classApi } from '../api/class'
import { studentApi } from '../api/student'
import { resourceApi } from '../api/resource'

export default {
  name: 'AnalyticsView',
  data() {
    return {
      selectedClass: 'all',
      timeRange: 'week',
      studentFilter: 'all',
      loading: false,
      weekDays: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      studyHours: ['08', '10', '12', '14', '16', '18', '20', '22'],
      classes: [],
      stats: {
        totalStudents: 0,
        avgProgress: 0,
        avgScore: 0,
        excellentRate: 0,
        avgStudyTime: '0',
        dailyStudyTime: '0'
      },
      scoreDistribution: {
        excellent: 32,
        good: 45,
        average: 18,
        pass: 5
      },
      progressTrend: [],
      classRankings: [],
      students: [],
      contentStats: [],
      recommendations: [],
      activityData: {},
      activitySummary: {
        peak_period: '19:00 - 21:00',
        daily_avg_online: 156,
        peak_online: 89
      }
    }
  },
  mounted() {
    this.loadData()
  },
  methods: {
    async loadData() {
      this.loading = true
      try {
        // 加载班级列表
        const classesRes = await classApi.getClasses()
        const classesData = classesRes.data.results || classesRes.data
        if (classesData && Array.isArray(classesData)) {
          this.classes = classesData.map(cls => ({
            id: cls.id,
            name: cls.name
          }))
          
          // 加载班级排名数据
          this.classRankings = await Promise.all(classesData.map(async (cls) => {
            const analyticsRes = await classApi.getClassAnalytics(cls.id)
            return {
              id: cls.id,
              name: cls.name,
              teacher: cls.teacher?.username || '',
              students: cls.student_count || 0,
              progress: 0,
              score: 0,
              studyTime: analyticsRes.data?.avg_learning_time || 0,
              trend: 0
            }
          }))
        }
        
        // 加载统计信息
        const analyticsRes = await analyticsApi.getOverview()
        if (analyticsRes.data) {
          this.stats.totalStudents = analyticsRes.data.total_students || 0
          this.stats.totalClasses = analyticsRes.data.total_classes || 0
        }
        
        // 加载学习进度趋势数据
        try {
          const params = this.selectedClass !== 'all' ? { class_id: this.selectedClass } : {}
          const trendRes = await analyticsApi.getProgressTrend(params)
          if (trendRes.data) {
            this.progressTrend = trendRes.data
          }
        } catch (e) {
          console.log('加载学习进度趋势失败:', e)
        }
        
        // 加载学生表现分析数据
        try {
          const params = this.selectedClass !== 'all' ? { class_id: this.selectedClass } : {}
          const studentAnalyticsRes = await analyticsApi.getStudentAnalyticsSummary(params)
          if (studentAnalyticsRes.data && studentAnalyticsRes.data.students) {
            this.students = studentAnalyticsRes.data.students.slice(0, 20).map((student, index) => ({
              id: student.id,
              name: student.name,
              studentId: student.student_id,
              className: '',
              progress: student.progress,
              totalChapters: student.total_chapters,
              avgScore: student.avg_score,
              studyTime: student.learn_time,
              completionRate: student.total_chapters > 0 ? Math.round((student.progress / student.total_chapters) * 100) : 0,
              avatarColor: this.getAvatarColor(index),
              isExcellent: student.performance_level === 'excellent',
              isImproving: student.trend === 'up',
              needsAttention: student.performance_level === 'needs_improvement'
            }))
          }
        } catch (e) {
          console.log('加载学生表现分析失败:', e)
        }
        
        // 加载资源统计数据
        try {
          const resourcesRes = await resourceApi.getResources()
          if (resourcesRes.data && Array.isArray(resourcesRes.data)) {
            this.contentStats = resourcesRes.data.slice(0, 10).map(resource => ({
              id: resource.id,
              type: resource.resource_type,
              title: resource.title,
              description: resource.description || '',
              views: 0,
              completion: 0,
              avgScore: 0,
              trend: 0
            }))
          }
        } catch (e) {
          console.log('加载资源统计失败:', e)
        }
        
        // 加载学习活跃度数据
        try {
          const params = this.selectedClass !== 'all' ? { class_id: this.selectedClass } : {}
          const activityRes = await analyticsApi.getActivity(params)
          if (activityRes.data) {
            this.activityData = activityRes.data.activity_data || {}
            if (activityRes.data.summary) {
              this.activitySummary = activityRes.data.summary
            }
          }
        } catch (e) {
          console.log('加载学习活跃度失败:', e)
        }
        
        // 加载AI教学建议
        try {
          const params = this.selectedClass !== 'all' ? { class_id: this.selectedClass } : {}
          const recommendationsRes = await analyticsApi.getRecommendations(params)
          if (recommendationsRes.data && recommendationsRes.data.recommendations) {
            this.recommendations = recommendationsRes.data.recommendations
          }
        } catch (e) {
          console.log('加载教学建议失败:', e)
        }
      } catch (error) {
        console.error('加载数据失败:', error)
      } finally {
        this.loading = false
      }
    },
    getAvatarColor(index) {
      const colors = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
      return colors[index % colors.length]
    },
    getRankClass(index) {
      if (index === 0) return 'gold'
      if (index === 1) return 'silver'
      if (index === 2) return 'bronze'
      return ''
    },
    getScoreClass(score) {
      if (score >= 90) return 'excellent'
      if (score >= 80) return 'good'
      if (score >= 70) return 'average'
      return 'pass'
    },
    getActivityData(hour) {
      // 从API获取的数据
      if (this.activityData[hour]) {
        return this.activityData[hour]
      }
      // 如果没有数据，返回空数组
      return [0, 0, 0, 0, 0, 0, 0]
    },
    getActivityColor(value) {
      if (value >= 80) return '#10b981'
      if (value >= 60) return '#3b82f6'
      if (value >= 40) return '#f59e0b'
      if (value >= 20) return '#f97316'
      return '#e2e8f0'
    },
    getContentIcon(type) {
      const icons = {
        video: '🎬',
        document: '📄',
        assignment: '📝',
        quiz: '📋'
      }
      return icons[type] || '📚'
    },
    viewStudentDetail(student) {
      this.$router.push(`/teacher/students/${student.id}`)
    },
    exportReport() {
      console.log('Exporting analytics report...')
    }
  }
}
</script>

<style scoped>
.analytics-dashboard {
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
  align-items: center;
}

.class-selector,
.time-selector {
  padding: 10px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  background: white;
  cursor: pointer;
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

.btn-secondary {
  background: white;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.btn-secondary:hover {
  background: #f1f5f9;
}

.overview-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.stat-icon {
  font-size: 24px;
}

.stat-trend {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 6px;
}

.stat-trend.up {
  background: #dcfce7;
  color: #16a34a;
}

.stat-trend.down {
  background: #fee2e2;
  color: #dc2626;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
  margin-bottom: 8px;
}

.stat-comparison {
  font-size: 12px;
  color: #94a3b8;
}

.charts-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card,
.section-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-card.large {
  grid-column: span 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.chart-legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #64748b;
}

.dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot.blue { background: #3b82f6; }
.dot.green { background: #10b981; }

.chart-container {
  display: flex;
  gap: 24px;
  align-items: center;
}

.chart-area {
  display: flex;
  flex: 1;
  height: 200px;
}

.y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding-right: 12px;
  font-size: 11px;
  color: #94a3b8;
}

.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  flex: 1;
  height: 100%;
  border-bottom: 1px solid #e2e8f0;
  border-left: 1px solid #e2e8f0;
  padding: 0 16px;
}

.bar-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  flex: 1;
}

.bar {
  width: 20px;
  border-radius: 4px 4px 0 0;
  transition: height 0.3s;
}

.bar.target {
  background: #10b981;
  opacity: 0.5;
}

.bar.actual {
  background: #3b82f6;
}

.bar-label {
  font-size: 11px;
  color: #64748b;
  margin-top: 8px;
}

.donut-chart {
  position: relative;
  width: 160px;
  height: 160px;
}

.donut-center {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.donut-value {
  display: block;
  font-size: 28px;
  font-weight: 700;
  color: #1e293b;
}

.donut-label {
  font-size: 12px;
  color: #64748b;
}

.donut {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.chart-legend-vertical {
  flex: 1;
}

.legend-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid #f1f5f9;
}

.legend-row:last-child {
  border-bottom: none;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 3px;
}

.legend-value {
  margin-left: auto;
  font-weight: 600;
  color: #1e293b;
}

.data-section {
  display: grid;
  grid-template-columns: 1.5fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.view-all {
  font-size: 13px;
  color: #3b82f6;
  text-decoration: none;
}

.view-all:hover {
  text-decoration: underline;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #f1f5f9;
}

.data-table th {
  font-size: 12px;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
}

.data-table td {
  font-size: 14px;
  color: #1e293b;
}

.rank-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 13px;
  background: #f1f5f9;
}

.rank-badge.gold {
  background: linear-gradient(135deg, #fef3c7, #fcd34d);
  color: #92400e;
}

.rank-badge.silver {
  background: linear-gradient(135deg, #f1f5f9, #cbd5e1);
  color: #475569;
}

.rank-badge.bronze {
  background: linear-gradient(135deg, #fed7aa, #fb923c);
  color: #9a3412;
}

.class-info {
  display: flex;
  flex-direction: column;
}

.class-name {
  font-weight: 500;
}

.class-teacher {
  font-size: 12px;
  color: #64748b;
}

.progress-cell {
  display: flex;
  align-items: center;
  gap: 8px;
}

.progress-bar {
  width: 60px;
  height: 6px;
  background: #f1f5f9;
  border-radius: 3px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: #3b82f6;
  border-radius: 3px;
}

.score-badge {
  display: inline-block;
  padding: 4px 10px;
  border-radius: 6px;
  font-weight: 600;
  font-size: 13px;
}

.score-badge.excellent {
  background: #dcfce7;
  color: #16a34a;
}

.score-badge.good {
  background: #dbeafe;
  color: #2563eb;
}

.score-badge.average {
  background: #fef3c7;
  color: #d97706;
}

.score-badge.pass {
  background: #fee2e2;
  color: #dc2626;
}

.trend-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
}

.trend-badge.up {
  background: #dcfce7;
  color: #16a34a;
}

.trend-badge.down {
  background: #fee2e2;
  color: #dc2626;
}

.activity-heatmap {
  margin-top: 16px;
}

.heatmap-header,
.heatmap-row {
  display: grid;
  grid-template-columns: 60px repeat(7, 1fr);
  gap: 4px;
  margin-bottom: 4px;
}

.heatmap-header span {
  text-align: center;
  font-size: 11px;
  color: #64748b;
}

.hour-label {
  font-size: 11px;
  color: #64748b;
  padding: 4px 0;
}

.heatmap-cell {
  aspect-ratio: 1;
  border-radius: 4px;
  cursor: pointer;
  transition: transform 0.2s;
}

.heatmap-cell:hover {
  transform: scale(1.1);
}

.activity-summary {
  display: flex;
  gap: 24px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f1f5f9;
}

.summary-item {
  display: flex;
  flex-direction: column;
}

.summary-label {
  font-size: 12px;
  color: #64748b;
}

.summary-value {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.students-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.section-actions select {
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 13px;
  background: white;
}

.students-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
}

.student-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.student-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.student-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
}

.student-avatar {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  color: white;
}

.student-badges {
  display: flex;
  gap: 4px;
}

.badge {
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
}

.badge.excellent {
  background: #dcfce7;
  color: #16a34a;
}

.badge.improving {
  background: #dbeafe;
  color: #2563eb;
}

.badge.warning {
  background: #fef3c7;
  color: #d97706;
}

.student-info h4 {
  margin: 0 0 4px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.student-info p {
  margin: 0;
  font-size: 12px;
  color: #64748b;
}

.student-metrics {
  margin: 16px 0;
}

.metric {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.metric:last-child {
  margin-bottom: 0;
}

.metric-label {
  width: 40px;
  font-size: 12px;
  color: #64748b;
}

.metric-bar {
  flex: 1;
  height: 8px;
  background: #f1f5f9;
  border-radius: 4px;
  overflow: hidden;
}

.metric-fill {
  height: 100%;
  background: linear-gradient(90deg, #3b82f6, #2563eb);
  border-radius: 4px;
}

.metric-value,
.metric-score {
  width: 40px;
  text-align: right;
  font-size: 13px;
  font-weight: 600;
  color: #1e293b;
}

.student-footer {
  display: flex;
  justify-content: space-between;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
  font-size: 12px;
  color: #64748b;
}

.content-analysis,
.recommendations-section {
  margin-bottom: 24px;
}

.section-card.full-width {
  width: 100%;
}

.content-stats-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.content-stat-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
}

.content-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.content-icon.video { background: #dbeafe; }
.content-icon.document { background: #fef3c7; }
.content-icon.assignment { background: #dcfce7; }
.content-icon.quiz { background: #f3e8ff; }

.content-info {
  flex: 1;
}

.content-info h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.content-info p {
  margin: 0;
  font-size: 13px;
  color: #64748b;
}

.content-metrics {
  display: flex;
  gap: 24px;
}

.content-metric {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.metric-num {
  font-size: 18px;
  font-weight: 700;
  color: #1e293b;
}

.metric-lbl {
  font-size: 11px;
  color: #64748b;
}

.content-trend {
  padding: 8px 16px;
}

.content-trend span {
  font-size: 14px;
  font-weight: 600;
}

.content-trend span.up { color: #16a34a; }
.content-trend span.down { color: #dc2626; }

.ai-badge {
  padding: 4px 10px;
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
  color: white;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recommendation-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: #f8fafc;
  border-radius: 12px;
  border-left: 4px solid;
}

.recommendation-item.warning { border-color: #f59e0b; }
.recommendation-item.info { border-color: #3b82f6; }
.recommendation-item.success { border-color: #10b981; }
.recommendation-item.tip { border-color: #8b5cf6; }

.rec-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
}

.recommendation-item.warning .rec-icon { background: #fef3c7; }
.recommendation-item.info .rec-icon { background: #dbeafe; }
.recommendation-item.success .rec-icon { background: #dcfce7; }
.recommendation-item.tip .rec-icon { background: #f3e8ff; }

.rec-content {
  flex: 1;
}

.rec-content h4 {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
}

.rec-content p {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #64748b;
}

.rec-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
}

.rec-impact {
  color: #64748b;
}

.rec-priority {
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 500;
}

.rec-priority.紧急 { background: #fee2e2; color: #dc2626; }
.rec-priority.建议 { background: #dbeafe; color: #2563eb; }
.rec-priority.普通 { background: #f1f5f9; color: #64748b; }

.rec-action {
  padding: 8px 16px;
  font-size: 13px;
}
</style>

import { createRouter, createWebHistory } from 'vue-router'

const DashboardView = () => import('../views/DashboardView.vue')
const StudentListView = () => import('../views/StudentListView.vue')
const StudentDetailView = () => import('../views/StudentDetailView.vue')
const ClassListView = () => import('../views/ClassListView.vue')
const ClassDetailView = () => import('../views/ClassDetailView.vue')
const AssignmentListView = () => import('../views/AssignmentListView.vue')
const AssignmentCreateView = () => import('../views/AssignmentCreateView.vue')
const AssignmentDetailView = () => import('../views/AssignmentDetailView.vue')
const AssignmentGradeView = () => import('../views/AssignmentGradeView.vue')
const AnalyticsView = () => import('../views/AnalyticsView.vue')
const ResourceListView = () => import('../views/ResourceListView.vue')
const NotificationListView = () => import('../views/NotificationListView.vue')
const SettingsView = () => import('../views/SettingsView.vue')

const routes = [
  {
    path: '/teacher/dashboard',
    name: 'TeacherDashboard',
    component: DashboardView,
    meta: { title: '教师工作台', requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/students',
    name: 'StudentList',
    component: StudentListView,
    meta: { title: '学生管理', requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/students/:id',
    name: 'StudentDetail',
    component: StudentDetailView,
    meta: { title: '学生详情', requiresAuth: true, role: 'teacher' },
    props: true
  },
  {
    path: '/teacher/classes',
    name: 'ClassList',
    component: ClassListView,
    meta: { title: '班级管理', requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/classes/:id',
    name: 'ClassDetail',
    component: ClassDetailView,
    meta: { title: '班级详情', requiresAuth: true, role: 'teacher' },
    props: true
  },
  {
    path: '/teacher/assignments',
    name: 'AssignmentList',
    component: AssignmentListView,
    meta: { title: '作业管理', requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/assignments/create',
    name: 'AssignmentCreate',
    component: AssignmentCreateView,
    meta: { title: '创建作业', requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/assignments/:id',
    name: 'AssignmentDetail',
    component: AssignmentDetailView,
    meta: { title: '作业详情', requiresAuth: true, role: 'teacher' },
    props: true
  },
  {
    path: '/teacher/assignments/:id/grade',
    name: 'AssignmentGrade',
    component: AssignmentGradeView,
    meta: { title: '批改作业', requiresAuth: true, role: 'teacher' },
    props: true
  },
  {
    path: '/teacher/analytics',
    name: 'Analytics',
    component: AnalyticsView,
    meta: { title: '数据分析', requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/resources',
    name: 'ResourceList',
    component: ResourceListView,
    meta: { title: '教学资源', requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/notifications',
    name: 'NotificationList',
    component: NotificationListView,
    meta: { title: '消息通知', requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/settings',
    name: 'TeacherSettings',
    component: SettingsView,
    meta: { title: '教师设置', requiresAuth: true, role: 'teacher' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router

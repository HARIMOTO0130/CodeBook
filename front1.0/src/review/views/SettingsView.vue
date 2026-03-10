<template>
  <div class="settings-view">
    <div class="card">
      <h3 class="card-title">个人信息</h3>
      <div class="info-list">
        <div class="info-item">
          <label>用户名</label>
          <span>{{ user.username }}</span>
        </div>
        <div class="info-item">
          <label>昵称</label>
          <span>{{ user.nickname || '-' }}</span>
        </div>
        <div class="info-item">
          <label>邮箱</label>
          <span>{{ user.email }}</span>
        </div>
        <div class="info-item">
          <label>角色</label>
          <span>{{ user.role_display }}</span>
        </div>
        <div class="info-item">
          <label>部门</label>
          <span>{{ user.department || '-' }}</span>
        </div>
      </div>
    </div>

    <div class="card">
      <h3 class="card-title">修改密码</h3>
      <form @submit.prevent="changePassword" class="password-form">
        <div class="form-group">
          <label>原密码</label>
          <input v-model="passwordForm.old_password" type="password" required />
        </div>
        <div class="form-group">
          <label>新密码</label>
          <input v-model="passwordForm.new_password" type="password" required />
        </div>
        <div class="form-group">
          <label>确认密码</label>
          <input v-model="passwordForm.confirm_password" type="password" required />
        </div>
        <div v-if="passwordError" class="error-message">{{ passwordError }}</div>
        <div v-if="passwordSuccess" class="success-message">{{ passwordSuccess }}</div>
        <button type="submit" class="btn-primary" :disabled="passwordLoading">
          {{ passwordLoading ? '修改中...' : '修改密码' }}
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authApi } from '../api/review'

const user = ref({})
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})
const passwordError = ref('')
const passwordSuccess = ref('')
const passwordLoading = ref(false)

const loadUser = async () => {
  try {
    const data = await authApi.getProfile()
    user.value = data
  } catch (err) {
    console.error('加载用户信息失败', err)
  }
}

const changePassword = async () => {
  passwordError.value = ''
  passwordSuccess.value = ''
  
  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    passwordError.value = '两次密码输入不一致'
    return
  }
  
  passwordLoading.value = true
  try {
    await authApi.changePassword(passwordForm.value)
    passwordSuccess.value = '密码修改成功'
    passwordForm.value = { old_password: '', new_password: '', confirm_password: '' }
  } catch (err) {
    passwordError.value = err.response?.data?.error || '修改失败'
  } finally {
    passwordLoading.value = false
  }
}

onMounted(() => loadUser())
</script>

<style scoped>
.info-list {
  display: grid;
  gap: 12px;
}

.info-item {
  display: flex;
  gap: 12px;
}

.info-item label {
  width: 80px;
  color: var(--text-secondary);
}

.password-form {
  max-width: 400px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
}

.error-message {
  color: var(--error-color);
  margin-bottom: 12px;
}

.success-message {
  color: var(--success-color);
  margin-bottom: 12px;
}
</style>

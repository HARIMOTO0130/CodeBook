<template>
  <div class="register-container">
    <div class="register-box">
      <h1 class="register-title">教材审核系统</h1>
      <h2 class="register-subtitle">注册审核员账号</h2>
      
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label>账号 <span class="required">*</span></label>
          <input 
            v-model="form.username" 
            type="text" 
            placeholder="请输入账号（4-20位字母数字）"
            required
            minlength="4"
            maxlength="20"
          />
        </div>
        
        <div class="form-group">
          <label>密码 <span class="required">*</span></label>
          <input 
            v-model="form.password" 
            type="password" 
            placeholder="请输入密码（至少8位）"
            required
            minlength="8"
          />
        </div>
        
        <div class="form-group">
          <label>确认密码 <span class="required">*</span></label>
          <input 
            v-model="form.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            required
          />
        </div>
        
        <div class="form-group">
          <label>姓名 <span class="required">*</span></label>
          <input 
            v-model="form.name" 
            type="text" 
            placeholder="请输入真实姓名"
            required
          />
        </div>
        
        <div class="form-group">
          <label>邮箱 <span class="required">*</span></label>
          <input 
            v-model="form.email" 
            type="email" 
            placeholder="请输入邮箱地址"
            required
          />
        </div>
        
        <div class="form-group">
          <label>手机号</label>
          <input 
            v-model="form.phone" 
            type="tel" 
            placeholder="请输入手机号（选填）"
          />
        </div>
        
        <div class="form-group">
          <label>审核领域</label>
          <div class="checkbox-group">
            <label v-for="field in reviewFields" :key="field.value" class="checkbox-label">
              <input 
                type="checkbox" 
                :value="field.value"
                v-model="form.reviewFields"
              />
              {{ field.label }}
            </label>
          </div>
        </div>
        
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">{{ success }}</div>
        
        <button type="submit" class="btn-primary register-btn" :disabled="loading">
          {{ loading ? '注册中...' : '注册' }}
        </button>
        
        <div class="form-footer">
          <router-link to="/review/login" class="link">已有账号？去登录</router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { authApi } from '../api/review'

const router = useRouter()

const reviewFields = [
  { value: 'programming', label: '编程开发' },
  { value: 'algorithm', label: '算法与数据结构' },
  { value: 'ai', label: '人工智能' },
  { value: 'database', label: '数据库' },
  { value: 'web', label: 'Web开发' },
  { value: 'mobile', label: '移动开发' },
  { value: 'security', label: '网络安全' },
  { value: 'cloud', label: '云计算' }
]

const form = reactive({
  username: '',
  password: '',
  confirmPassword: '',
  name: '',
  email: '',
  phone: '',
  reviewFields: []
})

const error = ref('')
const success = ref('')
const loading = ref(false)

const validateForm = () => {
  if (form.password !== form.confirmPassword) {
    error.value = '两次输入的密码不一致'
    return false
  }
  
  if (form.password.length < 8) {
    error.value = '密码长度至少为8位'
    return false
  }
  
  const usernameRegex = /^[a-zA-Z0-9_]{4,20}$/
  if (!usernameRegex.test(form.username)) {
    error.value = '账号只能包含字母、数字和下划线，长度为4-20位'
    return false
  }
  
  return true
}

const handleRegister = async () => {
  error.value = ''
  success.value = ''
  
  if (!validateForm()) {
    return
  }
  
  loading.value = true
  
  try {
    const registerData = {
      username: form.username,
      password: form.password,
      name: form.name,
      email: form.email,
      phone: form.phone || null,
      review_fields: form.reviewFields
    }
    
    await authApi.register(registerData)
    
    success.value = '注册成功！正在跳转到登录页面...'
    
    setTimeout(() => {
      router.push('/review/login')
    }, 2000)
  } catch (err) {
    error.value = err.response?.data?.detail || 
                  err.response?.data?.username?.[0] || 
                  err.response?.data?.email?.[0] || 
                  '注册失败，请检查输入信息'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-box {
  background: var(--white);
  padding: 40px;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 450px;
  max-height: 90vh;
  overflow-y: auto;
}

.register-title {
  text-align: center;
  font-size: 24px;
  color: var(--text-color);
  margin-bottom: 8px;
}

.register-subtitle {
  text-align: center;
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 30px;
  font-weight: normal;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

.form-group .required {
  color: var(--danger-color);
}

.form-group input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
}

.checkbox-group {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: var(--text-color);
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: auto;
  margin: 0;
}

.error-message {
  background: #fee;
  color: var(--danger-color);
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 14px;
}

.success-message {
  background: #efe;
  color: var(--success-color);
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 14px;
}

.register-btn {
  width: 100%;
  padding: 14px;
  font-size: 16px;
  margin-bottom: 20px;
}

.form-footer {
  text-align: center;
}

.link {
  color: var(--primary-color);
  text-decoration: none;
  font-size: 14px;
}

.link:hover {
  text-decoration: underline;
}
</style>

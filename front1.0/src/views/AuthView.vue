<template>
  <div class="auth-container">
    <div class="auth-card">
      <h1>欢迎使用 CodeBook+</h1>
      <p class="subtitle">请选择您的身份</p>
      
      <!-- 角色选择 -->
      <div v-if="!selectedRole" class="role-selection">
        <div class="role-options">
          <div class="role-card" @click="selectRole('student')">
            <div class="role-icon">👨‍🎓</div>
            <h3>学生端</h3>
            <p>学习教材、完成练习、查看学习记录</p>
            <button class="role-button" @click.stop="selectRole('student')">
              选择学生端
            </button>
          </div>
          
          <div class="role-card" @click="selectRole('teacher')">
            <div class="role-icon">👨‍🏫</div>
            <h3>教师端</h3>
            <p>管理班级、布置作业、查看学生数据</p>
            <button class="role-button" @click.stop="selectRole('teacher')">
              选择教师端
            </button>
          </div>
          
          <div class="role-card" @click="selectRole('provider')">
            <div class="role-icon">📚</div>
            <h3>教材提供者端</h3>
            <p>管理教材、创建版本、审核内容</p>
            <button class="role-button" @click.stop="selectRole('provider')">
              选择提供者端
            </button>
          </div>
        </div>
      </div>
      
      <!-- 登录/注册表单 -->
      <div v-else class="auth-forms">
        <div class="auth-tabs">
          <button 
            class="tab-button" 
            :class="{ active: isLogin }"
            @click="isLogin = true"
          >
            登录
          </button>
          <button 
            class="tab-button" 
            :class="{ active: !isLogin }"
            @click="isLogin = false"
          >
            注册
          </button>
        </div>
        
        <div class="role-info" v-if="!isLogin">
          <span class="role-badge">{{ getRoleName(selectedRole) }}</span>
          <button class="change-role-btn" @click="selectedRole = null">切换身份</button>
        </div>
        
        <!-- 登录表单 -->
        <form v-if="isLogin" @submit.prevent="handleLogin" class="auth-form">
          <div>
            <label>用户名</label>
            <input v-model="loginForm.username" type="text" required placeholder="用户名">
          </div>
          <div>
            <label>密码</label>
            <input v-model="loginForm.password" type="password" required placeholder="密码">
          </div>
          <button type="submit" :disabled="loading">{{ loading ? '登录中...' : '登录' }}</button>
          <p v-if="error" class="error-message">{{ error }}</p>
          <p class="login-hint">提示：登录后将根据您的账号角色自动跳转</p>
        </form>
        
        <!-- 注册表单 -->
        <form v-else @submit.prevent="handleRegister" class="auth-form">
          <div>
            <label>用户名</label>
            <input v-model="registerForm.username" type="text" required placeholder="用户名" minlength="3">
          </div>
          <div>
            <label>邮箱</label>
            <input v-model="registerForm.email" type="email" required placeholder="邮箱">
          </div>
          <div>
            <label>密码</label>
            <input v-model="registerForm.password" type="password" required placeholder="密码" minlength="6">
          </div>
          <div>
            <label>确认密码</label>
            <input v-model="registerForm.confirmPassword" type="password" required placeholder="确认密码" minlength="6">
          </div>
          <button type="submit" :disabled="loading">{{ loading ? '注册中...' : '注册' }}</button>
          <p v-if="error" class="error-message">{{ error }}</p>
          <p v-if="success" class="success-message">{{ success }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { api } from '../student/api/api.js'

export default {
  name: 'AuthView',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const selectedRole = ref(null)
    const isLogin = ref(true)
    const loading = ref(false)
    const error = ref('')
    const success = ref('')
    
    const loginForm = reactive({ username: '', password: '' })
    const registerForm = reactive({ username: '', email: '', password: '', confirmPassword: '' })
    
    const getRoleName = (role) => {
      const names = {
        student: '学生端',
        teacher: '教师端',
        provider: '教材提供者端'
      }
      return names[role] || role
    }
    
    const selectRole = (role) => {
      selectedRole.value = role
      error.value = ''
      success.value = ''
    }
    
    const getRedirectPath = (role) => {
      const paths = {
        student: '/student/books',
        teacher: '/teacher/dashboard',
        provider: '/provider/books'
      }
      return paths[role] || '/student/books'
    }
    
    const handleLogin = async () => {
      if (!loginForm.username || !loginForm.password) {
        error.value = '请填写用户名和密码'
        return
      }
      
      loading.value = true
      error.value = ''
      
      try {
        const result = await api.login(loginForm)
        
        if (result && result.token) {
          localStorage.setItem('token', result.token)
          
          // 保存用户角色（优先使用后端返回的角色）
          let userRole = result.role || 'student'
          localStorage.setItem('userRole', userRole)
          
          // 更新App.vue中的认证状态
          if (window.__updateAuthStatus) {
            window.__updateAuthStatus()
          }
          
          // 根据角色跳转（如果有redirect参数则使用，否则根据角色跳转）
          const redirect = route.query.redirect || getRedirectPath(userRole)
          router.push(redirect)
        } else {
          error.value = '登录失败，未收到token'
        }
      } catch (e) {
        console.error('登录请求错误:', e)
        if (e.response && e.response.data) {
          if (e.response.data.error) {
            error.value = e.response.data.error
          } else if (e.response.data.debug_info) {
            error.value = `登录失败: ${e.response.data.debug_info}`
          } else {
            error.value = '登录失败，请检查用户名和密码'
          }
        } else {
          error.value = '登录失败，请检查用户名和密码'
        }
      } finally {
        loading.value = false
      }
    }
    
    const handleRegister = async () => {
      // 检查是否选择了角色
      if (!selectedRole.value) {
        error.value = '请先选择身份'
        return
      }
      
      if (!registerForm.username || !registerForm.email || !registerForm.password || !registerForm.confirmPassword) {
        error.value = '请填写所有字段'
        return
      }
      
      if (registerForm.username.length < 3) {
        error.value = '用户名至少3个字符'
        return
      }
      
      if (registerForm.password.length < 6) {
        error.value = '密码至少6个字符'
        return
      }
      
      if (registerForm.password !== registerForm.confirmPassword) {
        error.value = '两次密码不一致'
        return
      }
      
      loading.value = true
      error.value = ''
      success.value = ''
      
      try {
        const result = await api.register({
          username: registerForm.username,
          email: registerForm.email,
          password: registerForm.password,
          role: selectedRole.value
        })
        
        if (result && result.token) {
          localStorage.setItem('token', result.token)
          // 使用后端返回的角色（应该和选择的角色一致）
          const userRole = result.role || selectedRole.value
          localStorage.setItem('userRole', userRole)
          
          // 更新App.vue中的认证状态
          if (window.__updateAuthStatus) {
            window.__updateAuthStatus()
          }
          
          success.value = '注册成功！正在跳转...'
          
          setTimeout(() => {
            router.push(getRedirectPath(userRole))
          }, 1000)
        } else {
          error.value = '注册失败，未收到token'
        }
      } catch (e) {
        console.error('注册请求错误:', e)
        console.error('错误详情:', e.response)
        
        // 尝试从错误对象中提取详细信息
        if (e.response && e.response.data) {
          const errors = e.response.data
          console.log('后端返回的错误:', errors)
          
          if (typeof errors === 'string') {
            error.value = errors
          } else if (Array.isArray(errors)) {
            // 如果错误是数组
            error.value = errors.join(', ')
          } else if (errors.username) {
            error.value = `用户名错误: ${Array.isArray(errors.username) ? errors.username[0] : errors.username}`
          } else if (errors.email) {
            error.value = `邮箱错误: ${Array.isArray(errors.email) ? errors.email[0] : errors.email}`
          } else if (errors.password) {
            error.value = `密码错误: ${Array.isArray(errors.password) ? errors.password[0] : errors.password}`
          } else if (errors.role) {
            error.value = `角色错误: ${Array.isArray(errors.role) ? errors.role[0] : errors.role}`
          } else if (errors.non_field_errors) {
            error.value = Array.isArray(errors.non_field_errors) ? errors.non_field_errors[0] : errors.non_field_errors
          } else {
            // 显示所有错误
            const errorMessages = Object.keys(errors).map(key => {
              const value = errors[key]
              return `${key}: ${Array.isArray(value) ? value[0] : value}`
            })
            error.value = errorMessages.join('; ') || '注册失败，请检查输入信息'
          }
        } else {
          error.value = `注册失败: ${e.message || '请稍后重试'}`
        }
      } finally {
        loading.value = false
      }
    }
    
    return {
      selectedRole,
      isLogin,
      loading,
      error,
      success,
      loginForm,
      registerForm,
      selectRole,
      getRoleName,
      handleLogin,
      handleRegister
    }
  }
}
</script>

<style scoped>
.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.auth-card {
  background: white;
  border-radius: 16px;
  padding: 3rem;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.auth-card h1 {
  text-align: center;
  color: #333;
  margin-bottom: 0.5rem;
  font-size: 2rem;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 2rem;
  font-size: 1rem;
}

.role-selection {
  margin-top: 1rem;
}

.role-options {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.role-card {
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 1.5rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fafafa;
}

.role-card:hover {
  border-color: #667eea;
  transform: translateY(-3px);
  box-shadow: 0 5px 15px rgba(102, 126, 234, 0.2);
  background: white;
}

.role-icon {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.role-card h3 {
  color: #333;
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.role-card p {
  color: #666;
  margin-bottom: 1rem;
  font-size: 0.9rem;
  line-height: 1.4;
}

.role-button {
  width: 100%;
  padding: 0.75rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.3s;
}

.role-button:hover {
  background: #5568d3;
}

.auth-forms {
  margin-top: 1rem;
}

.auth-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid #e0e0e0;
}

.tab-button {
  flex: 1;
  padding: 0.75rem;
  background: none;
  border: none;
  border-bottom: 3px solid transparent;
  cursor: pointer;
  font-size: 1rem;
  color: #666;
  transition: all 0.3s;
}

.tab-button:hover {
  color: #667eea;
}

.tab-button.active {
  color: #667eea;
  border-bottom-color: #667eea;
  font-weight: 500;
}

.role-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  padding: 0.75rem;
  background: #f0f7ff;
  border-radius: 8px;
}

.role-badge {
  font-weight: 500;
  color: #667eea;
}

.change-role-btn {
  padding: 0.5rem 1rem;
  background: white;
  border: 1px solid #667eea;
  color: #667eea;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.3s;
}

.change-role-btn:hover {
  background: #667eea;
  color: white;
}

.auth-form {
  margin-top: 1rem;
}

.auth-form > div {
  margin-bottom: 1rem;
}

.auth-form label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
  font-weight: 500;
}

.auth-form input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  box-sizing: border-box;
  font-size: 14px;
}

.auth-form input:focus {
  outline: none;
  border-color: #667eea;
}

.auth-form button {
  width: 100%;
  padding: 0.75rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 500;
  margin-top: 1rem;
}

.auth-form button:hover {
  background: #5568d3;
}

.auth-form button:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}

.error-message {
  color: #f56c6c;
  margin-top: 1rem;
  text-align: center;
  font-size: 14px;
}

.login-hint {
  margin-top: 0.75rem;
  text-align: center;
  font-size: 12px;
  color: #999;
}

.success-message {
  color: #67c23a;
  margin-top: 1rem;
  text-align: center;
  font-size: 14px;
}

@media (max-width: 768px) {
  .auth-card {
    padding: 2rem 1.5rem;
  }
  
  .auth-card h1 {
    font-size: 1.5rem;
  }
}
</style>



<template>
  <div class="register-container">
    <div class="register-card">
      <h2>注册</h2>
      <form @submit.prevent="register">
        <div>
          <label>选择身份</label>
          <div class="role-selection">
            <label class="role-option" :class="{ active: form.role === 'student' }">
              <input type="radio" v-model="form.role" value="student" required>
              <span>👨‍🎓 学生端</span>
            </label>
            <label class="role-option" :class="{ active: form.role === 'teacher' }">
              <input type="radio" v-model="form.role" value="teacher" required>
              <span>👨‍🏫 教师端</span>
            </label>
            <label class="role-option" :class="{ active: form.role === 'provider' }">
              <input type="radio" v-model="form.role" value="provider" required>
              <span>📚 教材提供者端</span>
            </label>
          </div>
        </div>
        <div>
          <label>用户名</label>
          <input v-model="form.username" type="text" required placeholder="用户名" minlength="3">
        </div>
        <div>
          <label>邮箱</label>
          <input v-model="form.email" type="email" required placeholder="邮箱">
        </div>
        <div>
          <label>密码</label>
          <input v-model="form.password" type="password" required placeholder="密码" minlength="6">
        </div>
        <div>
          <label>确认密码</label>
          <input v-model="form.confirmPassword" type="password" required placeholder="确认密码" minlength="6">
        </div>
        <button type="submit" :disabled="loading">{{ loading ? '注册中...' : '注册' }}</button>
        <p v-if="error" class="error-message">{{ error }}</p>
        <p v-if="success" class="success-message">{{ success }}</p>
      </form>
      <div class="login-link">
        已有账号？<router-link to="/student/login">立即登录</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api/api.js'

export default {
  name: 'RegisterView',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const error = ref('')
    const success = ref('')
    const form = reactive({ role: 'student', username: '', email: '', password: '', confirmPassword: '' })

    const register = async () => {
      if (!form.role || !form.username || !form.email || !form.password || !form.confirmPassword) {
        error.value = '请填写所有字段并选择身份'
        return
      }

      if (form.username.length < 3) {
        error.value = '用户名至少3个字符'
        return
      }

      if (form.password.length < 6) {
        error.value = '密码至少6个字符'
        return
      }

      if (form.password !== form.confirmPassword) {
        error.value = '两次密码不一致'
        return
      }

      loading.value = true
      error.value = ''
      success.value = ''

      try {
        console.log('注册表单数据:', { role: form.role, username: form.username, email: form.email });
        const result = await api.register({
          username: form.username,
          email: form.email,
          password: form.password,
          role: form.role
        });
        console.log('注册结果:', result);
        
        if (result && result.token) {
          localStorage.setItem('token', result.token);
          // 保存用户角色
          localStorage.setItem('userRole', form.role);
          success.value = '注册成功！正在跳转...';
          
          // 根据角色跳转到相应路由
          setTimeout(() => {
            let redirectPath = '/student/books';
            if (form.role === 'teacher') {
              redirectPath = '/teacher/dashboard';
            } else if (form.role === 'provider') {
              redirectPath = '/provider/books';
            }
            router.push(redirectPath);
          }, 1000);
        }
      } catch (e) {
        console.error('注册请求错误:', e);
        console.error('错误详情:', e.response ? e.response.data : '无响应数据');
        
        if (e.response && e.response.data) {
          const errors = e.response.data;
          if (typeof errors === 'string') {
            error.value = errors;
          } else if (errors.username) {
            error.value = `用户名错误: ${Array.isArray(errors.username) ? errors.username[0] : errors.username}`;
          } else if (errors.email) {
            error.value = `邮箱错误: ${Array.isArray(errors.email) ? errors.email[0] : errors.email}`;
          } else if (errors.password) {
            error.value = `密码错误: ${Array.isArray(errors.password) ? errors.password[0] : errors.password}`;
          } else {
            error.value = '注册失败，请检查输入信息';
          }
        } else {
          error.value = '注册失败，请稍后重试';
        }
      } finally {
        loading.value = false;
      }
    }

    return { form, loading, error, success, register }
  }
}
</script>

<style>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f0f0;
}
.register-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}
.register-card h2 {
  text-align: center;
  margin-bottom: 1.5rem;
  color: #333;
}
.register-card > form > div {
  margin-bottom: 1rem;
}
.register-card label {
  display: block;
  margin-bottom: 0.5rem;
  color: #666;
  font-weight: 500;
}
.register-card input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
  font-size: 14px;
}
.register-card input:focus {
  outline: none;
  border-color: #409EFF;
}
.register-card button {
  width: 100%;
  padding: 0.75rem;
  background: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
  font-size: 16px;
  font-weight: 500;
}
.register-card button:hover {
  background: #66b1ff;
}
.register-card button:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}
.error-message {
  color: #f56c6c;
  margin-top: 1rem;
  text-align: center;
  font-size: 14px;
}
.success-message {
  color: #67c23a;
  margin-top: 1rem;
  text-align: center;
  font-size: 14px;
}
.login-link {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 14px;
  color: #666;
}
.login-link a {
  color: #409EFF;
  text-decoration: none;
}
.login-link a:hover {
  text-decoration: underline;
}
.role-selection {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 0.5rem;
}
.role-option {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  border: 2px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
}
.role-option:hover {
  border-color: #409EFF;
  background: #f0f7ff;
}
.role-option input[type="radio"] {
  margin-right: 0.75rem;
  cursor: pointer;
}
.role-option input[type="radio"]:checked + span {
  color: #409EFF;
  font-weight: 500;
}
.role-option input[type="radio"]:checked {
  accent-color: #409EFF;
}
.role-option.active {
  border-color: #409EFF;
  background: #e6f4ff;
}
.role-option span {
  font-size: 14px;
  user-select: none;
}
</style>

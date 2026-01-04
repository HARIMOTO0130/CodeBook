<template>
  <div class="login-container">
    <div class="login-card">
      <h2>登录</h2>
      <form @submit.prevent="login">
        <div>
          <label>用户名</label>
          <input v-model="form.username" type="text" required placeholder="用户名">
        </div>
        <div>
          <label>密码</label>
          <input v-model="form.password" type="password" required placeholder="密码">
        </div>
        <button type="submit" :disabled="loading">{{ loading ? '登录中...' : '登录' }}</button>
        <p v-if="error" style="color:red;">{{ error }}</p>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api/api.js'

export default {
  name: 'LoginView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const loading = ref(false)
    const error = ref('')
    const form = reactive({ username: '', password: '' })

    const login = async () => {
      if (!form.username || !form.password) {
        error.value = '请填写用户名和密码'
        return
      }

      loading.value = true
      error.value = ''

      try {
        console.log('登录表单数据:', form);
        const result = await api.login(form);
        console.log('登录结果:', result);
        // 确保token已保存
        if (result && result.token) {
          try {
            localStorage.setItem('token', result.token);
            console.log('Token已手动保存到localStorage');
          } catch (e) {
            console.error('手动保存token失败:', e);
          }
        }
        // 登录成功后更新认证状态
        if (window.__updateAuthStatus) {
          window.__updateAuthStatus()
        }
        const redirect = route.query.redirect || '/books'
        router.push(redirect)
      } catch (e) {
        console.error('登录请求错误:', e);
        console.error('错误详情:', e.response ? e.response.data : '无响应数据');
        console.error('错误状态码:', e.response ? e.response.status : '未知');
        
        // 显示后端返回的详细错误信息
        if (e.response && e.response.data && e.response.data.debug_info) {
          console.log('后端调试信息:', e.response.data.debug_info);
          error.value = `登录失败: ${e.response.data.debug_info}`;
        } else {
          error.value = '登录失败'
        }
      } finally {
        loading.value = false
      }
    }

    return { form, loading, error, login }
  }
}
</script>

<style>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f0f0f0;
}
.login-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
}
.login-card h2 {
  text-align: center;
  margin-bottom: 1.5rem;
}
.login-card > form > div {
  margin-bottom: 1rem;
}
.login-card label {
  display: block;
  margin-bottom: 0.5rem;
}
.login-card input {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  box-sizing: border-box;
}
.login-card button {
  width: 100%;
  padding: 0.75rem;
  background: #409EFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 1rem;
}
.login-card button:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}
</style>



<template>
  <div class="role-selection-container">
    <div class="role-selection-card">
      <h1>欢迎使用 CodeBook+</h1>
      <p class="subtitle">请选择您的身份</p>
      
      <div class="role-options">
        <div class="role-card" @click="selectRole('student')">
          <div class="role-icon">👨‍🎓</div>
          <h3>学生端</h3>
          <p>学习教材、完成练习、查看学习记录</p>
          <button class="role-button" @click.stop="selectRole('student')">
            进入学生端
          </button>
        </div>
        
        <div class="role-card" @click="selectRole('teacher')">
          <div class="role-icon">👨‍🏫</div>
          <h3>教师端</h3>
          <p>管理班级、布置作业、查看学生数据</p>
          <button class="role-button" @click.stop="selectRole('teacher')">
            进入教师端
          </button>
        </div>
        
        <div class="role-card" @click="selectRole('provider')">
          <div class="role-icon">📚</div>
          <h3>教材提供者端</h3>
          <p>管理教材、创建版本、审核内容</p>
          <button class="role-button" @click.stop="selectRole('provider')">
            进入提供者端
          </button>
        </div>
      </div>
      
      <div class="auth-links">
        <router-link to="/student/login" class="auth-link">已有账号？登录</router-link>
        <span class="separator">|</span>
        <router-link to="/student/register" class="auth-link">注册新账号</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import { useRouter } from 'vue-router'

export default {
  name: 'RoleSelectionView',
  setup() {
    const router = useRouter()
    
    const selectRole = (role) => {
      // 保存选择的角色
      localStorage.setItem('userRole', role)
      
      // 根据角色跳转到对应的入口页面
      switch (role) {
        case 'student':
          router.push('/student/books')
          break
        case 'teacher':
          router.push('/teacher/dashboard')
          break
        case 'provider':
          router.push('/provider/books')
          break
        default:
          router.push('/student/books')
      }
    }
    
    return { selectRole }
  }
}
</script>

<style scoped>
.role-selection-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 2rem;
}

.role-selection-card {
  background: white;
  border-radius: 16px;
  padding: 3rem;
  max-width: 1000px;
  width: 100%;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.role-selection-card h1 {
  text-align: center;
  color: #333;
  margin-bottom: 0.5rem;
  font-size: 2.5rem;
}

.subtitle {
  text-align: center;
  color: #666;
  margin-bottom: 3rem;
  font-size: 1.1rem;
}

.role-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
  margin-bottom: 2rem;
}

.role-card {
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
  background: #fafafa;
}

.role-card:hover {
  border-color: #667eea;
  transform: translateY(-5px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.2);
  background: white;
}

.role-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.role-card h3 {
  color: #333;
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
}

.role-card p {
  color: #666;
  margin-bottom: 1.5rem;
  font-size: 0.95rem;
  line-height: 1.5;
}

.role-button {
  width: 100%;
  padding: 0.75rem;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.3s;
}

.role-button:hover {
  background: #5568d3;
}

.auth-links {
  text-align: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e0e0e0;
}

.auth-link {
  color: #667eea;
  text-decoration: none;
  font-size: 0.95rem;
  transition: color 0.3s;
}

.auth-link:hover {
  color: #5568d3;
  text-decoration: underline;
}

.separator {
  margin: 0 1rem;
  color: #ccc;
}

@media (max-width: 768px) {
  .role-options {
    grid-template-columns: 1fr;
  }
  
  .role-selection-card {
    padding: 2rem 1.5rem;
  }
  
  .role-selection-card h1 {
    font-size: 2rem;
  }
}
</style>



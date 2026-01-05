<template>
  <div class="not-found">
    <div class="not-found-content">
      <h1>404</h1>
      <p>页面未找到</p>
      <router-link to="/student/books" class="back-link">返回首页</router-link>
    </div>
  </div>
</template>

<script setup>
</script>

<style scoped>
.not-found {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f5f5f5;
}

.not-found-content {
  text-align: center;
}

.not-found-content h1 {
  font-size: 120px;
  margin: 0;
  color: #333;
}

.not-found-content p {
  font-size: 24px;
  color: #666;
  margin: 20px 0;
}

.back-link {
  display: inline-block;
  margin-top: 30px;
  padding: 12px 24px;
  background: #007bff;
  color: white;
  text-decoration: none;
  border-radius: 4px;
  transition: background 0.3s;
}

.back-link:hover {
  background: #0056b3;
}
</style>


import { createApp } from 'vue'
import App from './App.vue'
// 恢复全局样式
import './styles/global.css'
// 恢复路由
import router from './router'

const app = createApp(App)
app.use(router)

app.mount('#app')
import { createApp } from 'vue'
import 'element-plus/dist/index.css'
import ElementPlus from 'element-plus'
import App from './App.vue'
import router from './router/index.js'

// 创建Vue应用实例
const app = createApp(App)

// 使用路由
app.use(router)

// 全局注册 Element Plus
app.use(ElementPlus)

// 挂载应用
app.mount('#app')
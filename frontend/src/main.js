import { createApp } from 'vue'
import TestView from './views/TestView.vue'

// 创建Vue应用实例
const app = createApp(TestView)

// 挂载应用到DOM
app.mount('#app')
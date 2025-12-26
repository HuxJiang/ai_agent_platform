<template>
  <el-config-provider>
    <router-view />
  </el-config-provider>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
/* 全局样式重置 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html, body {
  height: 100%;
  font-family: 'Arial', 'Helvetica', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f8fafc;
  color: #2d3748;
}

#app {
  height: 100%;
}

/* 全局链接样式 */
a {
  color: #667eea;
  text-decoration: none;
  transition: color 0.2s;
}

a:hover {
  color: #5a67d8;
}

/* 通用布局类 */
.container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 16px;
}

/* 响应式断点 */
@media (max-width: 768px) {
  .container {
    padding: 0 12px;
  }
}

/* Element Plus 样式覆盖和增强 */
.el-button {
  font-family: inherit;
}

.el-input__inner {
  font-family: inherit;
}

.el-menu {
  border-right: none !important;
}

.el-card {
  border-radius: 12px !important;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06) !important;
  transition: all 0.3s ease;
}

.el-card:hover {
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05) !important;
  transform: translateY(-2px);
}

.el-dialog {
  border-radius: 16px !important;
}

.el-message {
  border-radius: 10px !important;
}
</style>

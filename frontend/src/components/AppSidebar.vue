<template>
  <el-aside class="sidebar">
    <el-menu
      :default-active="activeMenu"
      class="sidebar-menu"
      @select="handleMenuSelect"
    >
      <el-menu-item index="/home">
        <el-icon><house /></el-icon>
        <span>MCP广场</span>
      </el-menu-item>

      <el-menu-item index="/mymcp">
        <el-icon><tools /></el-icon>
        <span>我的MCP</span>
      </el-menu-item>

      <el-menu-item index="/workflow">
        <el-icon><refresh /></el-icon>
        <span>工作流</span>
      </el-menu-item>

      <el-menu-item index="/knowledge">
        <el-icon><notebook /></el-icon>
        <span>知识库</span>
      </el-menu-item>

      <el-menu-item index="/conversation">
        <el-icon><chat-dot-round /></el-icon>
        <span>会话管理</span>
      </el-menu-item>
    </el-menu>
  </el-aside>
</template>

<script>
import {
  House,
  Tools,
  Refresh,
  Notebook,
  ChatDotRound
} from '@element-plus/icons-vue'

export default {
  name: 'AppSidebar',
  components: {
    House,
    Tools,
    Refresh,
    Notebook,
    ChatDotRound
  },
  computed: {
    activeMenu() {
      return this.$route.path;
    }
  },
  methods: {
    handleMenuSelect(index) {
      if (this.$route.path !== index) {
        this.$router.push(index);
      }
    }
  }
}
</script>

<style scoped>
.sidebar {
  width: 240px !important;
  background-color: #ffffff;
  border-right: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.sidebar-menu {
  border-right: none;
  padding: 16px 8px;
}

:deep(.el-menu-item) {
  height: 48px;
  line-height: 48px;
  margin-bottom: 4px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #4b5563;
  transition: all 0.2s;
}

:deep(.el-menu-item:hover) {
  background-color: #f3f4f6;
  color: #111827;
}

:deep(.el-menu-item.is-active) {
  background-color: #e0e7ff;
  color: #4f46e5;
  font-weight: 600;
}

:deep(.el-menu-item .el-icon) {
  font-size: 18px;
  margin-right: 12px;
}
</style>

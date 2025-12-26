<template>
  <el-header class="navbar">
    <div class="navbar-brand">
      <div class="logo-icon">
        <el-icon size="24">
          <svg viewBox="0 0 1024 1024" width="1em" height="1em" fill="currentColor">
            <path d="M512 128c-212.8 0-384 171.2-384 384s171.2 384 384 384 384-171.2 384-384-171.2-384-384-384z m0 704c-176.8 0-320-143.2-320-320s143.2-320 320-320 320 143.2 320 320-143.2 320-320 320z m160-480c0-8.8-7.2-16-16-16s-16 7.2-16 16v256c0 8.8 7.2 16 16 16s16-7.2 16-16v-256z m-320 0c0-8.8-7.2-16-16-16s-16 7.2-16 16v256c0 8.8 7.2 16 16 16s16-7.2 16-16v-256z m160 128c0-8.8-7.2-16-16-16s-16 7.2-16 16v128c0 8.8 7.2 16 16 16s16-7.2 16-16v-128z"></path>
          </svg>
        </el-icon>
      </div>
      <h1 class="brand-name">智能体管理系统</h1>
    </div>
    <div class="navbar-user">
      <el-dropdown trigger="click" @command="handleCommand">
        <div class="user-info">
          <el-avatar :size="32" :style="{ backgroundColor: '#e0e7ff', color: '#4f46e5' }">
            {{ userInitial }}
          </el-avatar>
          <span class="username">{{ userName }}</span>
          <el-icon><arrow-down /></el-icon>
        </div>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="profile">个人资料</el-dropdown-item>
            <el-dropdown-item command="settings">系统设置</el-dropdown-item>
            <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </el-header>
</template>

<script>
import { ArrowDown } from '@element-plus/icons-vue'

export default {
  name: 'AppNavbar',
  components: {
    ArrowDown
  },
  props: {
    user: {
      type: Object,
      default: null
    }
  },
  computed: {
    userInitial() {
      return this.user?.nickname?.[0] || this.user?.username?.[0] || 'U';
    },
    userName() {
      return this.user?.nickname || this.user?.username || '用户';
    }
  },
  methods: {
    handleCommand(command) {
      if (command === 'logout') {
        this.$emit('logout');
      } else if (command === 'profile') {
        this.$message.info('个人资料功能开发中');
      } else if (command === 'settings') {
        this.$message.info('系统设置功能开发中');
      }
    }
  }
}
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
  height: 70px;
  background-color: #ffffff;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  z-index: 50;
  border-bottom: 1px solid #e5e7eb;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: #4f46e5;
  color: white;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.brand-name {
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
  margin: 0;
  letter-spacing: -0.025em;
}

.navbar-user {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 8px 12px;
  border-radius: 8px;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: #f3f4f6;
}

.username {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

:deep(.el-dropdown-menu__item) {
  font-size: 14px;
}

:deep(.el-dropdown-menu__item--divided) {
  border-top: 1px solid #e5e7eb;
}
</style>

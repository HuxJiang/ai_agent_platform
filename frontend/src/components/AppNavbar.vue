<template>
  <header class="navbar">
    <div class="navbar-brand">
      <div class="logo-icon">🤖</div>
      <h1 class="brand-name">智能体管理系统</h1>
    </div>
    <div class="navbar-user">
      <div class="user-info">
        <span class="avatar">{{ userInitial }}</span>
        <span class="username">{{ userName }}</span>
      </div>
      <button class="btn-logout" @click="$emit('logout')" title="退出登录">
        <span class="icon">⏻</span>
      </button>
    </div>
  </header>
</template>

<script>
export default {
  name: 'AppNavbar',
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
  gap: 20px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}
.avatar {
  width: 32px;
  height: 32px;
  background-color: #e0e7ff;
  color: #4f46e5;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}
.username {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}
.btn-logout {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: white;
  color: #6b7280;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.btn-logout:hover {
  background-color: #fef2f2;
  color: #ef4444;
  border-color: #fecaca;
}
</style>

<template>
  <div class="home-container">
    <!-- 导航栏 -->
    <header class="navbar">
      <div class="navbar-brand">
        <h1 class="brand-name">智能体管理系统</h1>
      </div>
      
      <div class="navbar-user">
        <div class="user-info">
          <span class="username">{{ user?.nickname || user?.username || '用户' }}</span>
        </div>
        <button class="btn-logout" @click="handleLogout">
          <span>退出登录</span>
        </button>
      </div>
    </header>
    
    <div class="main-content">
      <!-- 左侧菜单栏 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h3>功能菜单</h3>
        </div>
        <nav class="sidebar-nav">
          <!-- 暂时为空，待后续实现 -->
          <div class="placeholder-message">
            功能菜单正在开发中...
          </div>
        </nav>
      </aside>
      
      <!-- 中间内容区 -->
      <main class="content">
        <div class="content-header">
          <h2>欢迎使用智能体管理系统</h2>
          <p class="content-subtitle">这是系统的主页面，更多功能即将上线</p>
        </div>
        
        <div class="dashboard-overview">
          <div class="welcome-card">
            <div class="welcome-icon">👋</div>
            <div class="welcome-text">
              <h3>你好，{{ user?.nickname || user?.username || '用户' }}</h3>
              <p>欢迎回到智能体管理系统</p>
              <p class="current-time">当前时间: {{ currentTime }}</p>
            </div>
          </div>
          
          <div class="features-section">
            <h3>系统功能</h3>
            <div class="feature-cards">
              <div class="feature-card">
                <div class="feature-icon">🤖</div>
                <div class="feature-content">
                  <h4>智能体管理</h4>
                  <p>创建、编辑和管理智能体</p>
                </div>
              </div>
              <div class="feature-card">
                <div class="feature-icon">💬</div>
                <div class="feature-content">
                  <h4>会话管理</h4>
                  <p>与智能体进行对话交互</p>
                </div>
              </div>
              <div class="feature-card">
                <div class="feature-icon">📊</div>
                <div class="feature-content">
                  <h4>数据分析</h4>
                  <p>查看系统运行数据和统计信息</p>
                </div>
              </div>
              <div class="feature-card">
                <div class="feature-icon">⚙️</div>
                <div class="feature-content">
                  <h4>系统设置</h4>
                  <p>配置个人账户和系统偏好</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import api from '../utils/api.js'

export default {
  name: 'HomeView',
  data() {
    return {
      user: null,
      currentTime: new Date().toLocaleString()
    }
  },
  mounted() {
    // 获取用户信息
    this.getUserInfo()
    
    // 检查登录状态
    this.checkLoginStatus()
    
    // 每秒更新时间
    this.timeInterval = setInterval(() => {
      this.currentTime = new Date().toLocaleString()
    }, 1000)
  },
  beforeUnmount() {
    // 清理定时器
    if (this.timeInterval) {
      clearInterval(this.timeInterval)
    }
  },
  methods: {
    // 获取用户信息
    getUserInfo() {
      this.user = api.auth.getCurrentUser()
    },
    
    // 检查登录状态
    checkLoginStatus() {
      if (!api.auth.isLoggedIn()) {
        // 没有登录，跳转到登录页
        this.$router.push('/login')
      }
    },
    
    // 处理退出登录
    async handleLogout() {
      try {
        // 使用API工具调用退出登录接口
        await api.auth.logout()
      } catch (error) {
        console.error('退出登录失败:', error)
      } finally {
        // 无论如何都跳转到登录页
        this.$router.push('/login')
      }
    }
  }
}
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: 'Arial', sans-serif;
}

/* 导航栏样式 */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 24px;
  height: 64px;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.navbar-brand .brand-name {
  font-size: 20px;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.navbar-user {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-info .username {
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
}

.btn-logout {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-logout:hover {
  background-color: #5a67d8;
}

/* 主内容区样式 */
.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 侧边栏样式 */
.sidebar {
  width: 240px;
  background-color: #f7fafc;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px 16px;
  border-bottom: 1px solid #e2e8f0;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
}

.sidebar-nav {
  padding: 16px;
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-message {
  text-align: center;
  color: #a0aec0;
  font-size: 14px;
  padding: 20px;
}

/* 内容区样式 */
.content {
  flex: 1;
  padding: 24px;
  background-color: #f8fafc;
  overflow-y: auto;
}

.content-header {
  margin-bottom: 32px;
}

.content-header h2 {
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 600;
  color: #2d3748;
}

.content-subtitle {
  margin: 0;
  font-size: 16px;
  color: #718096;
}

/* 仪表盘概览 */
.dashboard-overview {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.welcome-card {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 20px;
}

.welcome-icon {
  font-size: 48px;
}

.welcome-text h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 600;
  color: #2d3748;
}

.welcome-text p {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: #718096;
}

.current-time {
  font-size: 12px;
  color: #a0aec0;
}

/* 功能卡片区域 */
.features-section h3 {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
}

.feature-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
}

.feature-card {
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: flex-start;
  gap: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.feature-card .feature-icon {
  font-size: 32px;
  flex-shrink: 0;
}

.feature-content h4 {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
}

.feature-content p {
  margin: 0;
  font-size: 14px;
  color: #718096;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    height: auto;
    border-right: none;
    border-bottom: 1px solid #e2e8f0;
  }
  
  .feature-cards {
    grid-template-columns: 1fr;
  }
  
  .navbar {
    padding: 0 16px;
  }
  
  .content {
    padding: 16px;
  }
}
</style>
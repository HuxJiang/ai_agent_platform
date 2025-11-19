<template>
  <div class="welcome-container">
    <div class="welcome-content">
      <h1 class="welcome-title">欢迎使用</h1>
      <p class="welcome-subtitle">Web 前端管理控制台</p>
      <div class="welcome-description">
        <p>此页面用于展示管理控制台、Agent 状态、日志与调试界面。</p>
        <p>无需后端参与，即可预览前端界面。</p>
      </div>
      <div class="welcome-features">
        <div class="feature-item">
          <div class="feature-icon">📊</div>
          <div class="feature-text">管理控制台</div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🤖</div>
          <div class="feature-text">Agent 状态</div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">📝</div>
          <div class="feature-text">日志查看</div>
        </div>
        <div class="feature-item">
          <div class="feature-icon">🔍</div>
          <div class="feature-text">调试界面</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TestView',
  data() {
    return {
      currentTime: new Date().toLocaleString()
    }
  },
  mounted() {
    // 每秒更新当前时间
    this.timer = setInterval(() => {
      this.currentTime = new Date().toLocaleString()
    }, 1000)
  },
  beforeUnmount() {
    // 清理定时器
    if (this.timer) {
      clearInterval(this.timer)
    }
  }
}
</script>

<style scoped>
.welcome-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  font-family: 'Arial', sans-serif;
}

.welcome-content {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 20px;
  padding: 40px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  text-align: center;
  max-width: 600px;
  backdrop-filter: blur(10px);
}

.welcome-title {
  font-size: 3rem;
  color: #2d3748;
  margin-bottom: 10px;
  font-weight: 700;
}

.welcome-subtitle {
  font-size: 1.5rem;
  color: #4a5568;
  margin-bottom: 30px;
  font-weight: 500;
}

.welcome-description {
  margin-bottom: 40px;
  line-height: 1.6;
  color: #718096;
}

.welcome-features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.feature-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: #f7fafc;
  border-radius: 12px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 10px;
}

.feature-text {
  color: #2d3748;
  font-weight: 500;
}

@media (max-width: 768px) {
  .welcome-title {
    font-size: 2.2rem;
  }
  
  .welcome-subtitle {
    font-size: 1.2rem;
  }
  
  .welcome-content {
    padding: 30px 20px;
  }
  
  .welcome-features {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
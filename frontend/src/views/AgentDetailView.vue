<template>



  <div class="agent-detail-container">
    <!-- 头部区域 -->
    <header class="agent-header">
      <div class="header-content">
        <div class="avatar-section">
          <img
            :src="agent.avatar || 'https://via.placeholder.com/120'"
            :alt="agent.name"
            class="agent-avatar"
          />
          <div class="avatar-badge" :class="{ 'online': agent.isTested, 'offline': !agent.isTested }">
            {{ agent.isTested ? '已测试' : '未测试' }}
          </div>
        </div>
        <div class="title-section">
          <h1 class="agent-name">{{ agent.name || '未命名智能体' }}</h1>
          <div class="agent-meta">
            <span class="category-badge">{{ agent.category || '未分类' }}</span>
            <span class="favorite-count">❤️ {{ agent.favoriteCount || 0 }} 收藏</span>
            <span class="connect-type" v-if="agent.connectType">🔗 {{ agent.connectType }}</span>
          </div>
          <p class="agent-description">{{ agent.description || '暂无描述信息。' }}</p>
        </div>
      </div>
    </header>

    <!-- 主要内容区域 -->
    <main class="agent-content">
      <div class="content-grid">
        <!-- 左侧：基本信息 -->
        <div class="info-card">
          <div class="card-header">
            <h2>📋 基本信息</h2>
          </div>
          <div class="card-body">
            <div class="info-item">
              <span class="info-label">ID</span>
              <span class="info-value">{{ agent.id || '未知' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">名称</span>
              <span class="info-value">{{ agent.name || '未命名' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">分类</span>
              <span class="info-value">{{ agent.category || '未分类' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">连接类型</span>
              <span class="info-value">{{ agent.connectType || '未知' }}</span>
            </div>
          </div>
        </div>

        <!-- 中间：配置信息 -->
        <div class="info-card">
          <div class="card-header">
            <h2>⚙️ 配置信息</h2>
          </div>
          <div class="card-body">
            <div class="info-item">
              <span class="info-label">系统提示</span>
              <span class="info-value">{{ agent.systemPrompt || '无' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">模型</span>
              <span class="info-value">{{ agent.model || '默认' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">温度</span>
              <span class="info-value">{{ agent.temperature !== undefined ? agent.temperature : 0.7 }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">最大令牌数</span>
              <span class="info-value">{{ agent.maxTokens !== undefined ? agent.maxTokens : 4096 }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">公开状态</span>
              <span class="info-value">
                <span class="status-badge" :class="{ 'public': agent.isPublic, 'private': !agent.isPublic }">
                  {{ agent.isPublic ? '公开' : '私有' }}
                </span>
              </span>
            </div>
          </div>
        </div>

        <!-- 右侧：状态信息 -->
        <div class="info-card">
          <div class="card-header">
            <h2>📊 状态信息</h2>
          </div>
          <div class="card-body">
            <div class="info-item">
              <span class="info-label">测试状态</span>
              <span class="info-value">
                <span class="status-badge" :class="{ 'tested': agent.isTested, 'untested': !agent.isTested }">
                  {{ agent.isTested ? '已测试' : '未测试' }}
                </span>
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">收藏状态</span>
              <span class="info-value">
                <span class="status-badge" :class="{ 'favorited': agent.isFavorite, 'not-favorited': !agent.isFavorite }">
                  {{ agent.isFavorite ? '已收藏' : '未收藏' }}
                </span>
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">收藏数量</span>
              <span class="info-value">{{ agent.favoriteCount || 0 }}</span>
            </div>
          </div>
        </div>

        <!-- 底部：时间信息 -->
        <div class="info-card full-width">
          <div class="card-header">
            <h2>⏰ 时间信息</h2>
          </div>
          <div class="card-body">
            <div class="time-grid">
              <div class="time-item">
                <span class="time-label">创建时间</span>
                <span class="time-value">{{ agent.createdAt ? formatDateTime(agent.createdAt) : '未知' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
export default {
  name: 'AgentDetailView',
  data() {
    return {
      agent: {},
      showRawData: false
    };
  },
  computed: {
    formattedAgentData() {
      return JSON.stringify(this.agent, null, 2);
    }
  },
  mounted() {
    this.loadAgentData();
  },
  methods: {
    loadAgentData() {
      const agentData = this.$route.query.agent;
      if (agentData) {
        try {
          this.agent = JSON.parse(agentData);
        } catch (error) {
          console.error('解析智能体数据失败:', error);
        }
      }
    },
    formatDateTime(dateString) {
      if (!dateString) return '未知';
      const date = new Date(dateString);
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      });
    }
  }
};
</script>

<style scoped>


.agent-detail-container {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f9fafb;
  min-height: 100vh;
  color: #111827;
}

/* 头部区域样式 */
.agent-header {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: white;
  padding: 40px 20px;
  border-bottom-left-radius: 24px;
  border-bottom-right-radius: 24px;
  box-shadow: 0 4px 20px rgba(79, 70, 229, 0.3);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 32px;
}

.avatar-section {
  position: relative;
  flex-shrink: 0;
}

.agent-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 4px solid rgba(255, 255, 255, 0.3);
  object-fit: cover;
  background-color: white;
}

.avatar-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  border: 2px solid white;
}

.avatar-badge.online {
  background-color: #10b981;
  color: white;
}

.avatar-badge.offline {
  background-color: #6b7280;
  color: white;
}

.title-section {
  flex: 1;
}

.agent-name {
  font-size: 32px;
  font-weight: 800;
  margin: 0 0 12px 0;
  color: white;
}

.agent-meta {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.category-badge {
  background: rgba(255, 255, 255, 0.2);
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 600;
  backdrop-filter: blur(10px);
}

.favorite-count {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.15);
  padding: 6px 12px;
  border-radius: 20px;
}

.connect-type {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.15);
  padding: 6px 12px;
  border-radius: 20px;
}

.agent-description {
  font-size: 16px;
  line-height: 1.6;
  margin: 0;
  opacity: 0.9;
  max-width: 800px;
}

/* 主要内容区域样式 */
.agent-content {
  max-width: 1200px;
  margin: 40px auto;
  padding: 0 20px;
}

.content-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
  margin-bottom: 24px;
}

.info-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
}

.info-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
}

.info-card.full-width {
  grid-column: 1 / -1;
}

.card-header {
  background: #f8fafc;
  padding: 20px 24px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
}

.card-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 700;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-icon {
  font-size: 14px;
  color: #6b7280;
  transition: transform 0.2s;
}

.card-body {
  padding: 24px;
}

/* 信息项样式 */
.info-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 12px 0;
  border-bottom: 1px solid #f3f4f6;
}

.info-item:last-child {
  border-bottom: none;
}

.info-label {
  font-size: 14px;
  font-weight: 600;
  color: #4b5563;
  flex: 0 0 120px;
}

.info-value {
  font-size: 14px;
  color: #111827;
  flex: 1;
  text-align: right;
  word-break: break-word;
}

.info-link {
  color: #4f46e5;
  text-decoration: none;
  font-weight: 500;
}

.info-link:hover {
  text-decoration: underline;
  color: #4338ca;
}

/* 状态徽章样式 */
.status-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-badge.public {
  background-color: #dcfce7;
  color: #166534;
}

.status-badge.private {
  background-color: #fee2e2;
  color: #991b1b;
}

.status-badge.tested {
  background-color: #dbeafe;
  color: #1e40af;
}

.status-badge.untested {
  background-color: #f3f4f6;
  color: #4b5563;
}

.status-badge.favorited {
  background-color: #fef3c7;
  color: #92400e;
}

.status-badge.not-favorited {
  background-color: #f3f4f6;
  color: #6b7280;
}

/* 时间信息样式 */
.time-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.time-item {
  background: #f8fafc;
  padding: 16px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.time-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #6b7280;
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.time-value {
  display: block;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

/* 原始数据样式 */
.raw-data {
  background: #1f2937;
  color: #e5e7eb;
  padding: 20px;
  border-radius: 8px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
  line-height: 1.5;
  overflow-x: auto;
  max-height: 400px;
  overflow-y: auto;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }

  .agent-meta {
    justify-content: center;
  }

  .content-grid {
    grid-template-columns: 1fr;
  }

  .info-item {
    flex-direction: column;
    gap: 8px;
  }

  .info-label {
    flex: none;
  }

  .info-value {
    text-align: left;
    width: 100%;
  }

  .agent-name {
    font-size: 24px;
  }

  .agent-avatar {
    width: 100px;
    height: 100px;
  }
}

@media (max-width: 480px) {
  .agent-header {
    padding: 30px 16px;
  }

  .agent-content {
    padding: 0 16px;
    margin: 24px auto;
  }

  .card-body {
    padding: 16px;
  }

  .time-grid {
    grid-template-columns: 1fr;
  }
}
</style>

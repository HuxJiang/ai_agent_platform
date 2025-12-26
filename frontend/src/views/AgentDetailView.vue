<template>
  <div class="agent-detail-container">
    <!-- 返回按钮 -->
    <el-button class="back-home-btn" type="primary" @click="goBackHome" :icon="House">
      返回首页
    </el-button>

    <!-- 头部区域 -->
    <el-card class="agent-header-card" shadow="never">
      <div class="header-content">
        <!-- 头像区域 -->
        <div class="avatar-section">
          <el-avatar
            :size="120"
            :src="agent.avatar || 'https://via.placeholder.com/120'"
            :alt="agent.name"
            class="agent-avatar"
          />
          <el-tag
            class="avatar-badge"
            :type="agent.isTested ? 'success' : 'info'"
            size="small"
            round
          >
            {{ agent.isTested ? '已测试' : '未测试' }}
          </el-tag>
        </div>

        <!-- 标题区域 -->
        <div class="title-section">
          <h1 class="agent-name">{{ agent.name || '未命名智能体' }}</h1>

          <el-space class="agent-meta" :size="16" wrap>
            <el-tag class="category-badge" type="warning" size="large" round>
              {{ agent.category || '未分类' }}
            </el-tag>

            <el-tag class="favorite-count" type="danger" size="large">
              <template #default>
                <el-icon><Star /></el-icon>
                {{ agent.favoriteCount || 0 }} 收藏
              </template>
            </el-tag>

            <el-tag v-if="agent.connectType" class="connect-type" type="primary" size="large">
              <template #default>
                <el-icon><Connection /></el-icon>
                {{ agent.connectType }}
              </template>
            </el-tag>
          </el-space>

          <p class="agent-description">{{ agent.description || '暂无描述信息。' }}</p>
        </div>
      </div>
    </el-card>

    <!-- 主要内容区域 -->
    <div class="agent-content">
      <el-row :gutter="24" class="content-grid">
        <!-- 左侧：基本信息 -->
        <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
          <el-card class="info-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><Document /></el-icon>
                <span>📋 基本信息</span>
              </div>
            </template>

            <el-descriptions :column="1" border size="default">
              <el-descriptions-item label="ID">
                {{ agent.id || '未知' }}
              </el-descriptions-item>
              <el-descriptions-item label="名称">
                {{ agent.name || '未命名' }}
              </el-descriptions-item>
              <el-descriptions-item label="分类">
                {{ agent.category || '未分类' }}
              </el-descriptions-item>
              <el-descriptions-item label="连接类型">
                {{ agent.connectType || '未知' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>

        <!-- 中间：配置信息 -->
        <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
          <el-card class="info-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><Setting /></el-icon>
                <span>⚙️ 配置信息</span>
              </div>
            </template>

            <el-descriptions :column="1" border size="default">
              <el-descriptions-item label="系统提示">
                {{ agent.systemPrompt || '无' }}
              </el-descriptions-item>
              <el-descriptions-item label="模型">
                {{ agent.model || '默认' }}
              </el-descriptions-item>
              <el-descriptions-item label="温度">
                {{ agent.temperature !== undefined ? agent.temperature : 0.7 }}
              </el-descriptions-item>
              <el-descriptions-item label="最大令牌数">
                {{ agent.maxTokens !== undefined ? agent.maxTokens : 4096 }}
              </el-descriptions-item>
              <el-descriptions-item label="公开状态">
                <el-tag :type="agent.isPublic ? 'success' : 'danger'" size="small">
                  {{ agent.isPublic ? '公开' : '私有' }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>

        <!-- 右侧：状态信息 -->
        <el-col :xs="24" :sm="24" :md="8" :lg="8" :xl="8">
          <el-card class="info-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><DataAnalysis /></el-icon>
                <span>📊 状态信息</span>
              </div>
            </template>

            <el-descriptions :column="1" border size="default">
              <el-descriptions-item label="测试状态">
                <el-tag :type="agent.isTested ? 'success' : 'info'" size="small">
                  {{ agent.isTested ? '已测试' : '未测试' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="收藏状态">
                <el-tag :type="agent.isFavorite ? 'warning' : 'info'" size="small">
                  {{ agent.isFavorite ? '已收藏' : '未收藏' }}
                </el-tag>
              </el-descriptions-item>
              <el-descriptions-item label="收藏数量">
                {{ agent.favoriteCount || 0 }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>

        <!-- 底部：时间信息 -->
        <el-col :span="24">
          <el-card class="info-card full-width" shadow="hover">
            <template #header>
              <div class="card-header">
                <el-icon><Clock /></el-icon>
                <span>⏰ 时间信息</span>
              </div>
            </template>

            <el-descriptions :column="1" border size="default">
              <el-descriptions-item label="创建时间">
                {{ agent.createdAt ? formatDateTime(agent.createdAt) : '未知' }}
              </el-descriptions-item>
            </el-descriptions>
          </el-card>
        </el-col>
      </el-row>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  House,
  Star,
  Connection,
  Document,
  Setting,
  DataAnalysis,
  Clock
} from '@element-plus/icons-vue'

export default {
  name: 'AgentDetailView',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const agent = ref({})
    const showRawData = ref(false)

    const goBackHome = () => {
      router.push('/home')
    }

    const loadAgentData = () => {
      const agentData = route.query.agent
      if (agentData) {
        try {
          agent.value = JSON.parse(agentData)
        } catch (error) {
          console.error('解析智能体数据失败:', error)
        }
      }
    }

    const formatDateTime = (dateString) => {
      if (!dateString) return '未知'
      const date = new Date(dateString)
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
      })
    }

    onMounted(() => {
      loadAgentData()
    })

    return {
      agent,
      showRawData,
      goBackHome,
      formatDateTime,
      House,
      Star,
      Connection,
      Document,
      Setting,
      DataAnalysis,
      Clock
    }
  }
}
</script>

<style scoped>
.agent-detail-container {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background-color: #f9fafb;
  min-height: 100vh;
  color: #111827;
  padding: 20px;
}

/* 返回按钮样式 */
.back-home-btn {
  margin-bottom: 24px;
}

/* 头部卡片样式 */
.agent-header-card {
  background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
  color: white;
  border: none;
  border-radius: 16px;
  margin-bottom: 32px;
}

.agent-header-card :deep(.el-card__body) {
  padding: 40px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 32px;
}

.avatar-section {
  position: relative;
  flex-shrink: 0;
}

.agent-avatar {
  border: 4px solid rgba(255, 255, 255, 0.3);
  background-color: white;
}

.avatar-badge {
  position: absolute;
  bottom: 0;
  right: 0;
  transform: translate(25%, 25%);
}

.title-section {
  flex: 1;
}

.agent-name {
  font-size: 32px;
  font-weight: 800;
  margin: 0 0 16px 0;
  color: white;
}

.agent-meta {
  margin-bottom: 16px;
}

.category-badge,
.favorite-count,
.connect-type {
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.2);
  border: none;
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
  margin: 0 auto;
}

.content-grid {
  margin-bottom: 24px;
}

.info-card {
  height: 100%;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
}

.info-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1);
}

.info-card.full-width {
  margin-top: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 16px;
}

.card-header .el-icon {
  font-size: 18px;
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

  .agent-name {
    font-size: 24px;
  }

  .agent-avatar {
    width: 100px;
    height: 100px;
  }

  .agent-header-card :deep(.el-card__body) {
    padding: 24px;
  }
}

@media (max-width: 480px) {
  .agent-detail-container {
    padding: 16px;
  }

  .agent-header-card :deep(.el-card__body) {
    padding: 20px;
  }
}
</style>

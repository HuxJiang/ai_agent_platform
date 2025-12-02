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
      <!-- 左侧会话列表 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <h3>会话列表</h3>
        </div>
        <div class="sidebar-content">
          <!-- 会话列表 -->
          <div class="conversations-list">
            <div 
              v-for="conversation in conversations" 
              :key="conversation.id" 
              class="conversation-item"
            >
              <div 
                class="conversation-name" 
                @click="selectConversation(conversation)"
                :class="{ 'active': selectedConversation?.id === conversation.id }"
              >
                {{ conversation.title }}
              </div>
              <button 
                class="btn-delete-conversation" 
                @click="deleteConversation(conversation.id)"
                title="删除会话"
              >
                ×
              </button>
            </div>
            
            <!-- 空会话提示 -->
            <div v-if="conversations.length === 0" class="empty-conversations">
              暂无会话，请创建新会话
            </div>
          </div>
        </div>
      </aside>
      
      <!-- 中间内容区：聊天历史 -->
      <main class="content">
        <!-- 会话标题 -->
        <div class="content-header">
          <h2>{{ selectedConversation?.title || '请选择一个会话' }}</h2>
          <p class="content-subtitle">
            {{ selectedConversation?.createdAt ? `创建于: ${selectedConversation.createdAt}` : '' }}
          </p>
        </div>
        
        <!-- 聊天历史 -->
        <div class="chat-history">
          <!-- 加载状态 -->
          <div v-if="isLoadingConversation" class="loading">
            加载会话中...
          </div>
          
          <!-- 聊天消息列表 -->
          <div v-if="messages.length > 0" class="messages-list">
            <div v-for="(messagePair, index) in messages" :key="index" class="message-pair">
              <!-- 用户消息 -->
              <div class="message user-message">
                <div class="message-sender">用户</div>
                <div class="message-content">{{ messagePair.userMessageVO?.content || '无内容' }}</div>
                <div class="message-time">{{ messagePair.userMessageVO?.createdAt || '' }}</div>
              </div>
              
              <!-- 智能体消息 -->
              <div class="message agent-message">
                <div class="message-sender">智能体</div>
                <div class="message-content">{{ messagePair.agentMessageVO?.content || '无内容' }}</div>
                <div class="message-time">{{ messagePair.agentMessageVO?.createdAt || '' }}</div>
              </div>
            </div>
          </div>
          
          <!-- 无消息提示 -->
          <div v-else-if="selectedConversation" class="empty-messages">
            暂无消息，开始对话吧
          </div>
          
          <!-- 未选择会话提示 -->
          <div v-else class="select-conversation-prompt">
            <p>请从左侧选择一个会话开始聊天</p>
          </div>
        </div>
        
        <!-- 错误信息 -->
        <div v-if="error" class="error-message">{{ error }}</div>
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
      currentTime: new Date().toLocaleString(),
      
      // 会话相关数据
      conversations: [],
      selectedConversation: null,
      messages: [],
      
      // 状态管理
      isLoadingConversations: false,
      isLoadingConversation: false,
      error: ''
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
    
    // 加载会话列表
    this.loadConversations()
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
    },
    
    // 加载会话列表
    async loadConversations() {
      this.isLoadingConversations = true
      this.error = ''
      
      try {
        const response = await api.conversation.getConversationList()
        if (response && response.conversations) {
          this.conversations = response.conversations
        }
      } catch (error) {
        console.error('加载会话列表失败:', error)
        this.error = '加载会话列表失败，请稍后重试'
      } finally {
        this.isLoadingConversations = false
      }
    },
    
    // 选择会话
    async selectConversation(conversation) {
      this.isLoadingConversation = true
      this.error = ''
      
      try {
        // 设置选中会话
        this.selectedConversation = conversation
        
        // 获取会话详情
        const conversationDetails = await api.conversation.getConversation(conversation.id)
        this.selectedConversation = conversationDetails
        
        // 获取消息历史
        const messagesResponse = await api.conversation.getMessageHistory(conversation.id)
        if (messagesResponse && messagesResponse.history) {
          this.messages = messagesResponse.history
        } else {
          this.messages = []
        }
      } catch (error) {
        console.error('获取会话详情失败:', error)
        this.error = '获取会话详情失败，请稍后重试'
      } finally {
        this.isLoadingConversation = false
      }
    },
    
    // 删除会话
    async deleteConversation(conversationId) {
      try {
        await api.conversation.deleteConversation(conversationId)
        
        // 更新会话列表
        this.conversations = this.conversations.filter(conv => conv.id !== conversationId)
        
        // 如果删除的是当前选中的会话，清空选中状态和消息
        if (this.selectedConversation?.id === conversationId) {
          this.selectedConversation = null
          this.messages = []
        }
      } catch (error) {
        console.error('删除会话失败:', error)
        this.error = '删除会话失败，请稍后重试'
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

.sidebar-content {
  padding: 16px;
  flex: 1;
  overflow-y: auto;
}

/* 会话列表样式 */
.conversations-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.conversation-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 6px;
  background-color: white;
  border: 1px solid #e2e8f0;
  transition: all 0.2s;
  cursor: pointer;
}

.conversation-item:hover {
  background-color: #edf2f7;
}

.conversation-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-name.active {
  background-color: #667eea;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
}

.btn-delete-conversation {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #e53e3e;
  color: white;
  border: none;
  border-radius: 50%;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  line-height: 1;
  transition: background-color 0.2s;
}

.btn-delete-conversation:hover {
  background-color: #c53030;
}

.empty-conversations {
  text-align: center;
  color: #a0aec0;
  font-size: 14px;
  padding: 20px;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
}

/* 内容区样式 */
.content {
  flex: 1;
  padding: 24px;
  background-color: #f8fafc;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
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

/* 聊天历史样式 */
.chat-history {
  flex: 1;
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #718096;
  font-size: 16px;
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.message-pair {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 16px;
  border-radius: 8px;
  max-width: 80%;
}

.user-message {
  align-self: flex-end;
  background-color: #667eea;
  color: white;
}

.agent-message {
  align-self: flex-start;
  background-color: #edf2f7;
  color: #2d3748;
}

.message-sender {
  font-size: 12px;
  font-weight: 600;
  opacity: 0.8;
}

.message-content {
  font-size: 14px;
  line-height: 1.5;
}

.message-time {
  font-size: 10px;
  opacity: 0.6;
  align-self: flex-end;
}

.select-conversation-prompt {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #a0aec0;
  font-size: 16px;
}

.empty-messages {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #a0aec0;
  font-size: 16px;
}

/* 错误信息样式 */
.error-message {
  margin-top: 16px;
  padding: 12px;
  background-color: #fed7d7;
  color: #e53e3e;
  border-radius: 6px;
  font-size: 14px;
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
  
  .navbar {
    padding: 0 16px;
  }
  
  .content {
    padding: 16px;
  }
  
  .message {
    max-width: 90%;
  }
}
</style>
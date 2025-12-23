<template>
  <div class="app-container">
    <!-- 1. 全局顶部导航栏 -->
        <AppNavbar :user="user" @logout="handleLogout" />

    <div class="main-layout">
      <!-- 2. 左侧导航侧边栏 -->
      <AppSidebar />

      <!-- 3. 左侧会话菜单栏 -->
      <aside class="conversation-sidebar">
        <!-- 会话列表区域 -->
        <div class="conversations-section">
          <div class="section-header">
            <h3>我的会话</h3>
            <button class="btn-new-conversation" @click="createNewConversation" title="创建新会话">
              + 新建会话
            </button>
          </div>

          <div class="conversations-list">
            <div v-if="conversationsLoading" class="loading-conversations">
              <div class="spinner small"></div>
              <span>加载会话中...</span>
            </div>

            <div v-else-if="conversations.length === 0" class="no-conversations">
              <p>暂无会话</p>
            </div>

            <div
              v-for="conversation in conversations"
              :key="conversation.id"
              :class="['conversation-item', { active: currentConversation?.id === conversation.id }]"
            >
              <div class="conversation-info" @click="selectConversation(conversation)">
                <div class="conversation-title">{{ conversation.title || '未命名会话' }}</div>
                <div class="conversation-preview">{{ getConversationPreview(conversation) }}</div>
              </div>
              <div class="conversation-actions">
                <span class="conversation-time">{{ formatTime(conversation.updatedAt || conversation.createdAt) }}</span>
                <button
                  class="btn-delete-conversation"
                  @click.stop="deleteConversation(conversation)"
                  title="删除会话"
                >
                  🗑️
                </button>
              </div>
            </div>
          </div>
        </div>

      </aside>

      <!-- 4. 核心聊天内容区 -->
      <main class="chat-content">
        <!-- 聊天头部 -->
        <header class="chat-header">
          <div class="header-info">
            <h2>{{ currentConversation?.title || '实时对话' }}</h2>
            <p class="subtitle">与您的 AI 助手进行互动</p>
          </div>
          <div class="header-actions" v-if="currentConversation">
            <button class="btn-edit-settings" @click="openSettingsDialog(currentConversation)" title="编辑会话设置">
              ⚙️ 设置
            </button>
          </div>
        </header>

        <!-- 消息列表区域 -->
        <div class="chat-viewport" ref="chatViewport">
          <div v-if="loading" class="state-container">
            <div class="spinner"></div>
            <p>正在连接智能体...</p>
          </div>

          <div v-else-if="messages.length === 0" class="state-container empty">
            <div class="empty-icon">👋</div>
            <h3>开始新对话</h3>
            <p>与您的智能助手开始交流吧</p>
          </div>

          <div v-else class="messages-list">
            <div
              v-for="(message, index) in messages"
              :key="index"
              :class="['message-row', message.role]"
            >
              <div class="avatar-col">
                <img
                  :src="message.role === 'user' ? userAvatar : getAgentAvatar(message.role)"
                  class="chat-avatar"
                  :alt="message.role"
                />
              </div>
              <div class="bubble-col">
                <div class="message-meta">
                  <span class="sender-name">{{ message.role === 'user' ? '我' : getAgentName() }}</span>
                  <span class="time">{{ formatTime(message.createdAt) }}</span>
                </div>
                <div class="message-bubble">
                  {{ message.content }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部输入框 (CSS 已优化) -->
        <footer class="chat-input-area">
          <div class="input-wrapper" :class="{ 'sending': sending }">
            <input
              type="text"
              v-model="inputMessage"
              placeholder="输入消息，Enter 发送..."
              class="message-input"
              @keyup.enter="handleSendMessage"
              :disabled="sending"
            />
            <button
              class="btn-send"
              @click="handleSendMessage"
              :disabled="!inputMessage.trim() || sending"
            >
              <span v-if="sending" class="loading-dots">...</span>
              <span v-else>➤</span>
            </button>
          </div>
        </footer>
      </main>
    </div>

    <!-- 参数设置对话框 -->
    <div v-if="showSettingsDialog" class="settings-dialog-overlay" @click.self="closeSettingsDialog">
      <div class="settings-dialog">
        <div class="dialog-header">
          <div class="dialog-title">
            <h3>{{ currentConversation ? '编辑会话设置' : '创建新会话' }}</h3>
            <p class="dialog-subtitle">配置会话参数以获得最佳体验</p>
          </div>
          <button class="btn-close" @click="closeSettingsDialog">×</button>
        </div>

        <div class="dialog-tabs">
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'basic' }"
            @click="activeTab = 'basic'"
          >
            <span class="tab-icon">⚙️</span> 基本设置
          </button>
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'advanced' }"
            @click="activeTab = 'advanced'"
          >
            <span class="tab-icon">🔧</span> 高级设置
          </button>
        </div>

        <div class="dialog-body">
          <!-- 基本设置选项卡 -->
          <div v-if="activeTab === 'basic'" class="tab-content">
            <div class="form-section">
              <h4 class="section-title">
                <span class="section-icon">💬</span> 会话信息
              </h4>
              <div class="form-group">
                <label for="conversation-title" class="form-label">
                  <span class="label-icon">📝</span> 会话标题
                </label>
                <input
                  id="conversation-title"
                  type="text"
                  v-model="conversationSettings.title"
                  placeholder="例如：项目讨论、学习助手..."
                  class="form-input"
                />
                <small class="form-hint">为会话起一个有意义的名字，方便后续查找</small>
              </div>
            </div>

            <div class="form-section">
              <h4 class="section-title">
                <span class="section-icon">🤖</span> AI 模型设置
              </h4>

              <div class="form-group">
                <label for="conversation-model" class="form-label">
                  <span class="label-icon">🧠</span> 模型选择
                </label>
                <select
                  id="conversation-model"
                  v-model="conversationSettings.model"
                  class="form-input"
                >
                  <option v-for="model in chat_model" :key="model.id" :value="model.name">
                    {{ model.name }}
                  </option>
                </select>
                <small class="form-hint">如果留空，将使用所选智能体的默认模型</small>
              </div>
            </div>

            <div class="form-section">
              <h4 class="section-title">
                <span class="section-icon">⚒️</span> 插件配置
              </h4>
              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">🔗</span> 关联插件
                </label>
                <div class="agent-selection-card">
                  <div class="agent-card-header">
                    <span class="agent-card-title">已选插件</span>
                    <span class="agent-card-count" v-if="conversationSettings.agentIds.length > 1">
                      {{ conversationSettings.agentIds.length }} 个
                    </span>
                  </div>
                  <div class="agent-card-body">
                    <div v-if="conversationSettings.agentIds.length === 1" class="no-agents-selected">
                      <span class="no-agents-icon">⚒️</span>
                      <p>尚未选择任何插件</p>
                      <small>点击下方按钮添加插件</small>
                    </div>
                    <div v-else class="selected-agents-list">
                      <div class="selected-agent-item" v-for="agentId in conversationSettings.agentIds" :key="agentId">
                        <span class="agent-avatar">⚒️</span>
                        <span class="agent-name">
                          {{ getAgentById(agentId)?.name || `插件 ${agentId}` }}
                        </span>
                        <button class="remove-agent-btn" @click="removeAgent(agentId)" title="移除">
                          ×
                        </button>
                      </div>
                    </div>
                  </div>
                  <div class="agent-card-footer">
                    <button type="button" class="btn-add-agents" @click="openAgentSelection">
                      <span class="btn-icon">+</span> 添加插件
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 高级设置选项卡 -->
          <div v-if="activeTab === 'advanced'" class="tab-content">
            <div class="form-section">
              <h4 class="section-title">
                <span class="section-icon">🎛️</span> 模型参数
              </h4>

              <div class="form-group">
                <label for="conversation-temperature" class="form-label">
                  <span class="label-icon">🌡️</span> 温度控制
                  <span class="value-display">{{ conversationSettings.temperature.toFixed(1) }}</span>
                </label>
                <div class="slider-container">
                  <input
                    id="conversation-temperature"
                    type="range"
                    v-model.number="conversationSettings.temperature"
                    min="0"
                    max="2"
                    step="0.1"
                    class="form-range"
                  />
                  <div class="slider-labels">
                    <span class="slider-label">精确</span>
                    <span class="slider-label">平衡</span>
                    <span class="slider-label">创意</span>
                  </div>
                  <div class="slider-hint">
                    控制回复的随机性：较低值更精确，较高值更有创意
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label for="conversation-maxTokens" class="form-label">
                  <span class="label-icon">📏</span> 最大令牌数
                </label>
                <div class="input-with-unit">
                  <input
                    id="conversation-maxTokens"
                    type="number"
                    v-model.number="conversationSettings.maxTokens"
                    min="1"
                    max="8192"
                    class="form-input"
                  />
                  <span class="input-unit">tokens</span>
                </div>
                <small class="form-hint">控制单次回复的最大长度，建议值：1024-4096</small>
              </div>
            </div>

            <div class="form-section">
              <h4 class="section-title">
                <span class="section-icon">📊</span> 元数据配置
              </h4>
              <div class="form-group">
                <label for="conversation-metadata" class="form-label">
                  <span class="label-icon">📋</span> 自定义元数据
                </label>
                <div class="metadata-editor">
                  <div class="editor-header">
                    <span class="editor-title">JSON 编辑器</span>
                    <button
                      type="button"
                      class="btn-format"
                      @click="formatMetadata"
                      title="格式化 JSON"
                    >
                      格式化
                    </button>
                  </div>
                  <textarea
                    id="conversation-metadata"
                    v-model="metadataJson"
                    placeholder='{\n  "key": "value",\n  "category": "general"\n}'
                    class="form-textarea metadata-textarea"
                    rows="6"
                  ></textarea>
                  <div class="editor-footer">
                    <small class="form-hint">可选的会话元数据，用于存储自定义信息</small>
                    <span class="json-status" :class="{ valid: isJsonValid }">
                      {{ isJsonValid ? '✓ JSON 有效' : '⚠ 检查 JSON 格式' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div class="form-section">
              <h4 class="section-title">
                <span class="section-icon">⚡</span> 性能选项
              </h4>
              <div class="form-group">
                <label class="form-label">
                  <span class="label-icon">🚀</span> 其他设置
                </label>
                <div class="checkbox-group">
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="conversationSettings.streaming" class="checkbox-input" />
                    <span class="checkbox-custom"></span>
                    <span class="checkbox-text">启用流式响应</span>
                  </label>
                  <label class="checkbox-label">
                    <input type="checkbox" v-model="conversationSettings.cache" class="checkbox-input" checked />
                    <span class="checkbox-custom"></span>
                    <span class="checkbox-text">启用响应缓存</span>
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="dialog-footer">
          <div class="footer-actions">
            <button class="btn-secondary" @click="closeSettingsDialog">
              <span class="btn-icon">←</span> 取消
            </button>
            <div class="primary-actions">
              <button class="btn-outline" @click="resetToDefaults" v-if="activeTab === 'advanced'">
                恢复默认
              </button>
              <button class="btn-primary" @click="saveConversationSettings">
                <span class="btn-icon">💾</span>
                {{ currentConversation ? '保存设置' : '创建会话' }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// Script 逻辑保持不变
import AppNavbar from '../components/AppNavbar.vue'
import AppSidebar from '../components/AppSidebar.vue'
import api from '../utils/api.js'

export default {
  name: 'ConversationView',
  components: { AppNavbar, AppSidebar },
  data() {
    return {
      user: null,
      agents: [],
      chat_model: [], // List for chat models
      tools: [], // List for tools
      selectedAgentId: null,
      urlAgentId: null,
      currentConversation: null,
      messages: [],
      inputMessage: '',
      loading: false,
      sending: false,
      userAvatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix',
      // 会话列表相关数据
      conversations: [],
      conversationsLoading: false,
      // 参数设置相关数据
      showSettingsDialog: false,
      activeTab: 'basic', // 当前激活的选项卡
      conversationSettings: {
        title: '',
        provider: 'deepseek',
        model: '',
        temperature: 0.7,
        maxTokens: 1024,
        agentIds: [],
        metadata: {},
        streaming: true,
        cache: true
      }
    }
  },
  computed: {
    metadataJson: {
      get() {
        try {
          return JSON.stringify(this.conversationSettings.metadata, null, 2)
        } catch (error) {
          return '{}'
        }
      },
      set(value) {
        try {
          this.conversationSettings.metadata = JSON.parse(value)
        } catch (error) {
          // 保持原值不变
        }
      }
    },
    isJsonValid() {
      try {
        JSON.parse(this.metadataJson)
        return true
      } catch (error) {
        return false
      }
    }
  },
  mounted() {
    this.checkLoginStatus()
    this.getUserInfo()
    // 从URL参数中获取agent_id（如果有）
    this.urlAgentId = this.$route.query.agent_id
    this.getAgentsList()
  },
  updated() {
    this.scrollToBottom()
  },
  methods: {
    checkLoginStatus() {
      if (!api.auth.isLoggedIn()) this.$router.push('/login')
    },
    getUserInfo() {
      this.user = api.auth.getCurrentUser()
    },
    async handleLogout() {
      try { await api.auth.logout() } finally { this.$router.push('/login') }
    },
    async getAgentsList() {
      if (!this.user) return;
      this.loading = true;
      try {
        const response = await api.agent.getUserAgentList(this.user.id);
        this.agents = response.agents || [];

        // Categorize agents into chat_model and tools
        this.chat_model = this.agents.filter(agent => agent.category === 'chat-model');
        this.tools = this.agents.filter(agent => agent.category === 'tool');

        if (this.chat_model.length > 0) {
          // 优先使用URL参数中的agent_id，否则使用第一个智能体
          if (this.urlAgentId) {
            const urlAgentIdStr = String(this.urlAgentId);
            const matchingAgent = this.chat_model.find(agent => String(agent.id) === urlAgentIdStr);
            if (matchingAgent) {
              this.selectedAgentId = matchingAgent.id;
            } else {
              this.selectedAgentId = this.chat_model[0].id;
            }
          } else {
            this.selectedAgentId = this.chat_model[0].id;
          }
          // 创建默认会话前，先获取会话列表
          await this.getConversationsList();
        }
      } catch (error) {
        console.error('Error:', error);
      } finally {
        this.loading = false;
      }
    },
    // 获取会话列表
    async getConversationsList() {
      if (!this.user) return
      this.conversationsLoading = true
      try {
        const response = await api.conversation.getConversationList({ userId: this.user.id })
        this.conversations = response || []
      } catch (error) {
        console.error('获取会话列表失败:', error)
        this.conversations = []
      } finally {
        this.conversationsLoading = false
      }
    },
    // 创建新会话
    async createNewConversation() {
      if (!this.user || !this.selectedAgentId) return
      this.loading = true
      try {
        await this.createDefaultConversation()
        // 创建成功后，重新获取会话列表
        await this.getConversationsList()
      } catch (error) {
        console.error('创建新会话失败:', error)
      } finally {
        this.loading = false
      }
    },
    // 选择会话
    async selectConversation(conversation) {
      this.currentConversation = conversation
      this.messages = []
      this.loading = true

      // 更新当前智能体选择
      if (conversation.mainAgent) {
        this.selectedAgentId = conversation.mainAgent
      }

      // 加载会话消息历史
      await this.loadConversationMessages(conversation.id)

      this.loading = false
    },

    // 加载会话消息历史
    async loadConversationMessages(conversationId) {
      try {
        const response = await api.conversation.getConversationDetail({
          conversationId,
          userId: this.user.id
        });

        if ( response.messages.length > 0) {
          // 提取消息历史并格式化
          this.messages = response.messages.map(msg => ({
            role: msg.role,
            content: msg.content,
            type: msg.type,
            createdAt: msg.createdAt
          }));
        } else {
          this.messages = [];
        }
      } catch (error) {
        console.error('加载会话消息失败:', error);
        this.messages = [];
      }
    },
    // 获取会话预览
    getConversationPreview(conversation) {
      if (conversation.messages && conversation.messages.length > 0) {
        const lastMessage = conversation.messages[conversation.messages.length - 1]
        return lastMessage.content?.substring(0, 30) + (lastMessage.content?.length > 30 ? '...' : '')
      }
      return '无消息'
    },
    // 删除会话
    async deleteConversation(conversation) {
      if (confirm(`确定要删除会话"${conversation.title || '未命名会话'}"吗？此操作不可恢复。`)) {
        try {
          // 直接传递queryParams参数，生成正确的URL
          await api.conversation.deleteConversation({
            conversationId: conversation.id,
            userId: this.user.id
          })
          // 后续逻辑不变
          await this.getConversationsList()
          if (this.currentConversation?.id === conversation.id) {
            this.currentConversation = null
            this.messages = []
          }
        } catch (error) {
          console.error('删除会话失败:', error)
          alert('删除会话失败，请稍后重试')
        }
      }
    },
    async createDefaultConversation() {
      if (!this.user || !this.selectedAgentId) return;
      this.loading = true;
      try {
        const mainAgentId = Number(this.selectedAgentId);
        const selectedAgent = this.agents.find(agent => agent.id === this.selectedAgentId);
        const model = selectedAgent ? selectedAgent.name : 'default-model';
        const agentIds = [2, 3];

        const response = await api.conversation.createConversation({
          userId: this.user.id,
          model: model, // Dynamically set model
          provider: 'deepseek',
          temperature: 0.7,
          maxTokens: 1024,
          mainAgent: mainAgentId,
          agentIds
        });
        this.currentConversation = response;
        this.messages = [];
      } catch (error) {
        console.error('Error:', error);
      } finally {
        this.loading = false;
      }
    },
    async handleAgentChange() {
      // 通过路由跳转带上agent_id参数，实现模型切换
      this.$router.push({
        path: '/conversation',
        query: {
          agent_id: this.selectedAgentId
        }
      })
    },
    async handleSendMessage() {
      if (!this.inputMessage.trim() || !this.user || !this.currentConversation || this.sending) return

      const messageContent = this.inputMessage.trim()
      this.inputMessage = ''
      this.sending = true

      try {
        const userMessage = { role: 'user', content: messageContent, createdAt: new Date().toISOString() }
        this.messages.push(userMessage)

        const sendParams = {
          conversationId: this.currentConversation.id,
          userId: this.user.id,
          messages: [{ role: 'user', content: messageContent }]
        }

        const response = await api.conversation.sendMessage(sendParams)
        const responseMessages = this.extractAssistantMessages(response)

        if (responseMessages.length > 0) {
          this.messages.push(...responseMessages)
        } else {
          this.messages.push({
            role: 'assistant',
            content: (response && (response.content || response.message?.content)) || '处理中...',
            createdAt: new Date().toISOString()
          })
        }
      } catch (error) {
        console.error('Error:', error)
        this.messages.pop()
      } finally {
        this.sending = false
      }
    },
    getAgentAvatar(role) {
      if (role === 'assistant' && this.selectedAgentId) {
        const agent = this.agents.find(a => a.id === this.selectedAgentId)
        return agent?.avatar || 'https://api.dicebear.com/7.x/bottts/svg?seed=Agent'
      }
      return 'https://api.dicebear.com/7.x/bottts/svg?seed=Bot'
    },
    getAgentName() {
       const agent = this.agents.find(a => a.id === this.selectedAgentId)
       return agent ? agent.name : '智能体'
    },
    formatTime(timeString) {
      if (!timeString) return ''
      return new Date(timeString).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
    },
    scrollToBottom() {
      const container = this.$refs.chatViewport
      if (container) container.scrollTop = container.scrollHeight
    },
    extractAssistantMessages(response) {
      const normalizeTimestamp = (value) => value ? new Date(value).toISOString() : new Date().toISOString()
      const collectMessages = () => {
        if (Array.isArray(response)) return response
        if (Array.isArray(response?.messages)) return response.messages
        if (response?.message) return [response.message]
        return []
      }
      return collectMessages()
        .filter(msg => msg && msg.role === 'assistant')
        .map(msg => ({
          role: 'assistant',
          content: msg.content || '',
          createdAt: normalizeTimestamp(msg.createdAt || msg.created_at || msg.timestamp)
        }))
    },
    // 打开参数设置对话框
    openSettingsDialog(conversation = null) {
      if (conversation) {
        // 编辑现有会话
        this.conversationSettings = {
          title: conversation.title || '',
          provider: conversation.provider || 'deepseek',
          model: conversation.model || '',
          temperature: conversation.temperature || 0.7,
          maxTokens: conversation.maxTokens || 1024,
          agentIds: conversation.agentIds || [],
          metadata: conversation.metadata || {}
        }
        this.currentConversation = conversation
      } else {
        // 创建新会话
        const selectedAgent = this.agents.find(agent => agent.id === this.selectedAgentId)
        this.conversationSettings = {
          title: '',
          provider: 'deepseek',
          model: selectedAgent ? selectedAgent.name : '',
          temperature: 0.7,
          maxTokens: 1024,
          agentIds: [this.selectedAgentId],
          metadata: {}
        }
        this.currentConversation = null
      }
      this.showSettingsDialog = true
    },
    // 关闭参数设置对话框
    closeSettingsDialog() {
      this.showSettingsDialog = false
      this.conversationSettings = {
        title: '',
        provider: 'deepseek',
        model: '',
        temperature: 0.7,
        maxTokens: 1024,
        agentIds: [],
        metadata: {}
      }
    },
    // 保存会话设置
    async saveConversationSettings() {
      if (!this.user) return

      this.loading = true
      try {
        const mainAgentId = Number(this.selectedAgentId)
        const selectedAgent = this.agents.find(agent => agent.id === this.selectedAgentId)
        const model = this.conversationSettings.model || (selectedAgent ? selectedAgent.name : 'default-model')

        const conversationData = {
          userId: this.user.id,
          title: this.conversationSettings.title || '未命名会话',
          provider: this.conversationSettings.provider,
          model: model,
          temperature: this.conversationSettings.temperature,
          maxTokens: this.conversationSettings.maxTokens,
          mainAgent: mainAgentId,
          agentIds: this.conversationSettings.agentIds.length > 0 ? this.conversationSettings.agentIds : [mainAgentId],
          metadata: this.conversationSettings.metadata
        }

        let response
        if (this.currentConversation) {
          // 更新现有会话
          response = await api.conversation.updateConversation({
            conversationId: this.currentConversation.id,
            ...conversationData
          })
        } else {
          // 创建新会话
          response = await api.conversation.createConversation(conversationData)
        }

        this.currentConversation = response
        this.messages = []
        this.closeSettingsDialog()

        // 重新获取会话列表
        await this.getConversationsList()
      } catch (error) {
        console.error('保存会话设置失败:', error)
        alert('保存会话设置失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    // 打开智能体选择
    openAgentSelection() {
      // 这里可以扩展为打开智能体选择对话框
      // 暂时简单地将当前选中的智能体添加到列表中
      if (this.selectedAgentId && !this.conversationSettings.agentIds.includes(this.selectedAgentId)) {
        this.conversationSettings.agentIds.push(this.selectedAgentId)
      }
    },
    // 修改createNewConversation方法，改为打开参数设置对话框
    async createNewConversation() {
      if (!this.user || !this.selectedAgentId) return
      this.openSettingsDialog()
    },
    // 根据ID获取智能体信息
    getAgentById(agentId) {
      return this.agents.find(agent => agent.id === agentId)
    },
    // 移除智能体
    removeAgent(agentId) {
      this.conversationSettings.agentIds = this.conversationSettings.agentIds.filter(id => id !== agentId)
    },
    // 格式化元数据JSON
    formatMetadata() {
      try {
        const parsed = JSON.parse(this.metadataJson)
        this.metadataJson = JSON.stringify(parsed, null, 2)
      } catch (error) {
        // 如果JSON无效，保持原样
      }
    },
    // 恢复默认设置
    resetToDefaults() {
      this.conversationSettings.temperature = 0.7
      this.conversationSettings.maxTokens = 1024
      this.conversationSettings.streaming = true
      this.conversationSettings.cache = true
    },
    // 更新openSettingsDialog方法以包含新字段
    openSettingsDialog(conversation = null) {
      if (conversation) {
        // 编辑现有会话
        this.conversationSettings = {
          title: conversation.title || '',
          provider: conversation.provider || 'deepseek',
          model: conversation.model || '',
          temperature: conversation.temperature || 0.7,
          maxTokens: conversation.maxTokens || 1024,
          agentIds: conversation.agentIds || [],
          metadata: conversation.metadata || {},
          streaming: conversation.streaming !== undefined ? conversation.streaming : true,
          cache: conversation.cache !== undefined ? conversation.cache : true
        }
        this.currentConversation = conversation
      } else {
        // 创建新会话
        const selectedAgent = this.agents.find(agent => agent.id === this.selectedAgentId)
        this.conversationSettings = {
          title: '',
          provider: 'deepseek',
          model: selectedAgent ? selectedAgent.name : '',
          temperature: 0.7,
          maxTokens: 1024,
          agentIds: [this.selectedAgentId],
          metadata: {},
          streaming: true,
          cache: true
        }
        this.currentConversation = null
      }
      this.activeTab = 'basic'
      this.showSettingsDialog = true
    },
    // 更新saveConversationSettings方法以包含新字段
    async saveConversationSettings() {
      if (!this.user) return

      this.loading = true
      try {
        const mainAgentId = Number(this.selectedAgentId)
        const selectedAgent = this.agents.find(agent => agent.id === this.selectedAgentId)
        const model = this.conversationSettings.model || (selectedAgent ? selectedAgent.name : 'default-model')

        const conversationData = {
          userId: this.user.id,
          title: this.conversationSettings.title || '未命名会话',
          provider: this.conversationSettings.provider,
          model: model,
          temperature: this.conversationSettings.temperature,
          maxTokens: this.conversationSettings.maxTokens,
          mainAgent: mainAgentId,
          agentIds: this.conversationSettings.agentIds.length > 0 ? this.conversationSettings.agentIds : [mainAgentId],
          metadata: this.conversationSettings.metadata,
          streaming: this.conversationSettings.streaming,
          cache: this.conversationSettings.cache
        }

        let response
        if (this.currentConversation) {
          // 更新现有会话
          response = await api.conversation.updateConversation({
            conversationId: this.currentConversation.id,
            ...conversationData
          })
        } else {
          // 创建新会话
          response = await api.conversation.createConversation(conversationData)
        }

        this.currentConversation = response
        this.messages = []
        this.closeSettingsDialog()

        // 重新获取会话列表
        await this.getConversationsList()
      } catch (error) {
        console.error('保存会话设置失败:', error)
        alert('保存会话设置失败，请稍后重试')
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
/* ================== CSS 变量 ================== */
:root {
  --primary-color: #6366f1;
  --primary-hover: #4f46e5;
  --primary-light: #e0e7ff;
  --secondary-color: #8b5cf6;
  --success-color: #10b981;
  --danger-color: #ef4444;
  --warning-color: #f59e0b;

  --bg-color: #5e6c79;
  --bg-elevated: #ffffff;
  --bg-hover: #f1f5f9;
  --bg-active: #e2e8f0;

  --white: #ffffff;
  --text-main: #1e293b;
  --text-secondary: #64748b;
  --text-tertiary: #94a3b8;
  --text-inverse: #ffffff;

  --border-color: #ba2727;
  --border-hover: #cbd5e1;
  --border-active: #94a3b8;

  --user-bubble: #6366f1;
  --bot-bubble: #ffffff;
  --assistant-bubble: #f1f5f9;

  --shadow-xs: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);

  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-full: 9999px;

  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  --font-mono: 'SF Mono', Monaco, 'Cascadia Mono', 'Segoe UI Mono', 'Roboto Mono', monospace;

  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
}

* { box-sizing: border-box; }

.app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: var(--font-sans);
  background-color: var(--bg-color);
  color: var(--text-main);
}

/* ================== Navbar ================== */
.navbar {
  display: flex; justify-content: space-between; align-items: center; padding: 0 32px;
  height: 70px; background-color: var(--white); box-shadow: var(--shadow-sm);
  z-index: 50; border-bottom: 1px solid var(--border-color); flex-shrink: 0;
}
.navbar-brand { display: flex; align-items: center; gap: 12px; }
.logo-icon {
  width: 40px; height: 40px; background: var(--primary-color); color: white;
  border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 24px;
}
.brand-name { font-size: 20px; font-weight: 700; color: var(--text-main); margin: 0; }
.navbar-user { display: flex; align-items: center; gap: 20px; }
.user-info { display: flex; align-items: center; gap: 10px; }
.avatar {
  width: 32px; height: 32px; background-color: #e0e7ff; color: var(--primary-color);
  border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600;
}
.username { font-size: 14px; font-weight: 500; }
.btn-logout {
  width: 36px; height: 36px; border-radius: 8px; border: 1px solid var(--border-color);
  background: white; color: var(--text-sub); cursor: pointer; display: flex; align-items: center; justify-content: center;
}
.btn-logout:hover { background-color: #fef2f2; color: #ef4444; border-color: #fecaca; }

/* ================== Sidebar ================== */
.main-layout { display: flex; flex: 1; overflow: hidden; }
.sidebar {
  width: 240px; background-color: var(--white); border-right: 1px solid var(--border-color);
  padding: 24px 16px; flex-shrink: 0;
}

/* ================== Conversation Sidebar ================== */
.conversation-sidebar {
  width: 300px;
  box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.08);
  background-color: var(--bg-elevated);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
  transition: width var(--transition-base);
}

/* Section Common Styles */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid var(--border-color);
  background-color: var(--bg-elevated);
}

.section-header h3 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-main);
  margin: 0;
  letter-spacing: 0.01em;
}

/* Conversations Section */
.conversations-section {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.conversations-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.conversations-list::-webkit-scrollbar {
  width: 8px;
}

.conversations-list::-webkit-scrollbar-track {
  background: transparent;
}

.conversations-list::-webkit-scrollbar-thumb {
  background-color: var(--border-color);
  border-radius: var(--radius-full);
  transition: background-color var(--transition-fast);
}

.conversations-list::-webkit-scrollbar-thumb:hover {
  background-color: var(--border-hover);
}

/* Loading Conversations */
.loading-conversations {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  gap: 16px;
  color: var(--text-tertiary);
}

.spinner.small {
  width: 24px;
  height: 24px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

/* No Conversations */
.no-conversations {
  text-align: center;
  padding: 60px 24px;
  color: var(--text-tertiary);
}

.no-conversations p {
  margin-bottom: 20px;
  font-size: 14px;
}

.no-conversations .btn-small {
  margin-top: 16px;
  padding: 10px 20px;
  background: var(--primary-color);
  color: var(--text-inverse);
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
  box-shadow: var(--shadow-sm);
}

.no-conversations .btn-small:hover {
  background: #dfdfdf;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* Conversation Item */
.conversation-item {
  display: flex;
  flex-direction: column;
  padding: 16px;
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-base);
  margin-bottom: 8px;
  background: var(--bg-color);
  border: 2px solid var(--border-color);
  position: relative;
  overflow: hidden;
}

.conversation-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 4px;
  height: 100%;
  background: transparent;
  transition: background-color var(--transition-base);
}

.conversation-item:hover {
  background: var(--bg-hover);
  border-color: var(--border-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.conversation-item:hover::before {
  background: var(--primary-light);
}

.conversation-item.active {
  background: var(--primary-light);
  border-color: var(--primary-color);
  box-shadow: var(--shadow-sm);
}

.conversation-item.active::before {
  background: var(--primary-color);
}

.conversation-info {
  flex: 1;
  margin-bottom: 12px;
  position: relative;
  z-index: 1;
}

.conversation-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 6px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.conversation-preview {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.4;
}

.conversation-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  position: relative;
  z-index: 1;
}

.conversation-time {
  font-size: 12px;
  color: var(--text-tertiary);
  font-feature-settings: "tnum";
}

/* Delete Conversation Button */
.btn-delete-conversation {
  width: 28px;
  height: 28px;
  border: none;
  background: transparent;
  color: var(--text-tertiary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.btn-delete-conversation:hover {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
  transform: scale(1.1);
}

/* New Conversation Button */
.btn-new-conversation {
  padding: 8px 16px;
  background: var(--primary-color);
  color: var(--text-inverse);
  background: #efefef;
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
  box-shadow: var(--shadow-sm);
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-new-conversation:hover {
  background: #dfdfdf;
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* 移除重复的 + 符号，因为按钮文本中已有 + */
.btn-new-conversation::before {
  content: '';
}

/* Model Selector Section */
.model-selector-section {
  border-top: 1px solid var(--border-color);
  padding: 20px 24px;
  background-color: var(--bg-elevated);
}

.model-selector-section .section-header {
  padding: 0 0 16px 0;
  border-bottom: none;
}

.model-selector {
  position: relative;
}

.model-selector .agent-select {
  width: 100%;
  padding: 12px 16px;
  padding-right: 40px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 14px;
  background: var(--bg-elevated);
  color: var(--text-main);
  cursor: pointer;
  outline: none;
  transition: all var(--transition-base);
  appearance: none;
  font-family: var(--font-sans);
}

.model-selector .agent-select:hover {
  border-color: var(--border-hover);
  background: var(--bg-hover);
}

.model-selector .agent-select:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  background: var(--bg-elevated);
}

.model-selector .select-arrow {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  font-size: 12px;
  color: var(--text-tertiary);
  transition: transform var(--transition-fast);
}

.model-selector .agent-select:focus + .select-arrow {
  transform: translateY(-50%) rotate(180deg);
}

/* Header Actions */
.header-actions {
  display: flex; gap: 12px;
}

.header-actions .btn-small {
  padding: 6px 12px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.header-actions .btn-small:hover {
  background: var(--primary-hover);
}
.menu-list { list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px; }
.menu-link {
  display: flex; align-items: center; gap: 12px; padding: 12px 16px;
  text-decoration: none; color: #4b5563; font-size: 15px; font-weight: 500;
  border-radius: 8px; transition: all 0.2s;
}
.menu-link:hover { background-color: #f3f4f6; color: var(--text-main); }
.menu-link.active { background-color: #e0e7ff; color: var(--primary-color); font-weight: 600; }

/* ================== Chat Content ================== */
.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, var(--bg-color) 0%, var(--bg-elevated) 100%);
  position: relative;
}

.chat-header {
  height: 80px;
  background-color: var(--bg-elevated);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 32px;
  flex-shrink: 0;
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 20;
}

.header-info h2 {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 6px 0;
  color: var(--text-main);
  line-height: 1.3;
}

.header-info .subtitle {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
  font-weight: 400;
}

/* Chat Viewport */
.chat-viewport {
  flex: 1;
  overflow-y: auto;
  padding: 32px;
  display: flex;
  flex-direction: column;
  scroll-behavior: smooth;
}

.chat-viewport::-webkit-scrollbar {
  width: 8px;
}

.chat-viewport::-webkit-scrollbar-track {
  background: transparent;
}

.chat-viewport::-webkit-scrollbar-thumb {
  background-color: var(--border-color);
  border-radius: var(--radius-full);
  transition: background-color var(--transition-fast);
}

.chat-viewport::-webkit-scrollbar-thumb:hover {
  background-color: var(--border-hover);
}

/* Messages States */
.state-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: var(--text-tertiary);
  text-align: center;
  padding: 60px 32px;
}

.state-container.empty {
  animation: fadeIn 0.5s ease-out;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 24px;
  opacity: 0.8;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 20px;
}

/* Messages List */
.messages-list {
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding-bottom: 40px;
}

.message-row {
  display: flex;
  gap: 16px;
  max-width: 85%;
  animation: messageAppear 0.3s ease-out;
}

@keyframes messageAppear {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-row.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-row.assistant {
  align-self: flex-start;
}

.chat-avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: var(--shadow-sm);
  background: var(--bg-elevated);
  border: 2px solid var(--bg-elevated);
  flex-shrink: 0;
  transition: transform var(--transition-fast);
}

.message-row:hover .chat-avatar {
  transform: scale(1.05);
}

.bubble-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 100%;
}

.message-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  font-size: 13px;
  color: var(--text-tertiary);
  padding: 0 4px;
}

.message-row.user .message-meta {
  justify-content: flex-end;
}

.sender-name {
  font-weight: 600;
  color: var(--text-secondary);
}

.time {
  font-size: 12px;
  font-feature-settings: "tnum";
  opacity: 0.8;
}

.message-bubble {
  padding: 16px 20px;
  font-size: 15px;
  line-height: 1.6;
  word-wrap: break-word;
  position: relative;
  transition: all var(--transition-base);
}

.message-row.user .message-bubble {
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: var(--text-inverse);
  border-radius: 24px 24px 8px 24px;
  box-shadow: var(--shadow-md);
}

.message-row.user .message-bubble::after {
  content: '';
  position: absolute;
  bottom: 0;
  right: -8px;
  width: 16px;
  height: 16px;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  clip-path: polygon(0 0, 100% 0, 100% 100%);
  border-radius: 0 0 0 8px;
}

.message-row.assistant .message-bubble {
  background-color: var(--assistant-bubble);
  color: var(--text-main);
  border: 1px solid var(--border-color);
  border-radius: 24px 24px 24px 8px;
  box-shadow: var(--shadow-sm);
}

.message-row.assistant .message-bubble::before {
  content: '';
  position: absolute;
  bottom: 0;
  left: -8px;
  width: 16px;
  height: 16px;
  background-color: var(--assistant-bubble);
  border-left: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
  clip-path: polygon(0 0, 100% 100%, 0 100%);
  border-radius: 0 0 8px 0;
}

.message-row.user:hover .message-bubble {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.message-row.assistant:hover .message-bubble {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--border-hover);
}

/* ================== Chat Input Area (优化重点) ================== */
.chat-input-area {
  padding: 32px;
  box-shadow: 0 -8px 32px rgba(0, 0, 0, 0.08);
  background-color: var(--bg-elevated);
  border-top: 1px solid var(--border-color);
  z-index: 30;
  position: sticky;
  bottom: 0;
}

.input-wrapper {
  display: flex;
  align-items: center;
  background-color: var(--bg-color);
  border: 2px solid var(--border-color);
  border-radius: var(--radius-xl);
  padding: 8px 8px 8px 24px;
  box-shadow: var(--shadow-md);
  transition: all var(--transition-base);
  position: relative;
  overflow: hidden;
}

.input-wrapper::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
  transform: scaleX(0);
  transform-origin: left;
  transition: transform var(--transition-base);
}

.input-wrapper:focus-within {
  border-color: var(--primary-color);
  background-color: var(--bg-elevated);
  box-shadow: var(--shadow-lg);
  transform: translateY(-2px);
}

.input-wrapper:focus-within::before {
  transform: scaleX(1);
}

.input-wrapper.sending {
  opacity: 0.8;
}

.input-wrapper.sending::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.1), transparent);
  animation: shimmer 2s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.message-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 16px;
  color: var(--text-main);
  padding: 12px 0;
  outline: none;
  font-family: var(--font-sans);
  line-height: 1.5;
  min-height: 24px;
  max-height: 120px;
  resize: none;
  overflow-y: auto;
}

.message-input::placeholder {
  color: var(--text-tertiary);
  font-weight: 400;
}

.message-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-send {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  color: var(--text-inverse);
  border: none;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-base);
  box-shadow: var(--shadow-md);
  position: relative;
  overflow: hidden;
  flex-shrink: 0;
  margin-left: 8px;
}

.btn-send::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, var(--primary-hover), var(--secondary-color));
  opacity: 0;
  transition: opacity var(--transition-base);
}

.btn-send:hover:not(:disabled)::before {
  opacity: 1;
}

.btn-send:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.05);
  box-shadow: var(--shadow-xl);
}

.btn-send:active:not(:disabled) {
  transform: translateY(0) scale(0.98);
}

.btn-send:disabled {
  background: var(--border-color);
  color: var(--text-tertiary);
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.btn-send span {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-dots {
  font-size: 24px;
  line-height: 10px;
  letter-spacing: 2px;
  animation: pulse 1.5s infinite;
  position: relative;
  top: -2px;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(0.9); }
  50% { opacity: 1; transform: scale(1.1); }
}

/* 输入框滚动条样式 */
.message-input::-webkit-scrollbar {
  width: 6px;
}

.message-input::-webkit-scrollbar-track {
  background: transparent;
}

.message-input::-webkit-scrollbar-thumb {
  background-color: var(--border-color);
  border-radius: var(--radius-full);
}

.message-input::-webkit-scrollbar-thumb:hover {
  background-color: var(--border-hover);
}

/* ================== 响应式设计 ================== */
@media (max-width: 1200px) {
  .conversation-sidebar {
    width: 280px;
  }

  .chat-header,
  .chat-viewport,
  .chat-input-area {
    padding-left: 24px;
    padding-right: 24px;
  }
}

@media (max-width: 1024px) {
  .conversation-sidebar {
    width: 260px;
  }

  .sidebar {
    width: 200px;
    padding: 20px 12px;
  }

  .chat-header {
    height: 70px;
    padding: 0 24px;
  }

  .header-info h2 {
    font-size: 18px;
  }

  .chat-viewport {
    padding: 24px;
  }

  .chat-input-area {
    padding: 24px;
  }

  .message-row {
    max-width: 90%;
  }
}

@media (max-width: 900px) {
  .conversation-sidebar {
    width: 240px;
  }

  .section-header {
    padding: 16px 20px;
  }

  .conversations-list {
    padding: 8px;
  }

  .conversation-item {
    padding: 12px;
  }

  .model-selector-section {
    padding: 16px 20px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }

  .conversation-sidebar {
    position: fixed;
    left: 0;
    top: 70px;
    bottom: 0;
    z-index: 40;
    transform: translateX(-100%);
    transition: transform var(--transition-base);
    box-shadow: var(--shadow-xl);
  }

  .conversation-sidebar.mobile-open {
    transform: translateX(0);
  }

  .chat-header,
  .chat-viewport,
  .chat-input-area {
    padding-left: 16px;
    padding-right: 16px;
  }

  .chat-header {
    height: 60px;
    padding: 0 16px;
  }

  .header-info h2 {
    font-size: 16px;
    margin-bottom: 4px;
  }

  .header-info .subtitle {
    font-size: 12px;
  }

  .chat-viewport {
    padding: 20px 16px;
  }

  .chat-input-area {
    padding: 20px 16px;
  }

  .input-wrapper {
    padding: 6px 6px 6px 16px;
  }

  .message-input {
    font-size: 15px;
    padding: 10px 0;
  }

  .btn-send {
    width: 44px;
    height: 44px;
    font-size: 18px;
  }

  .message-row {
    max-width: 95%;
    gap: 12px;
  }

  .chat-avatar {
    width: 36px;
    height: 36px;
  }

  .message-bubble {
    padding: 14px 16px;
    font-size: 14px;
  }

  .messages-list {
    gap: 24px;
  }

  .state-container {
    padding: 40px 16px;
  }

  .empty-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }

  .spinner {
    width: 32px;
    height: 32px;
  }

  /* 移动端菜单按钮 */
  .mobile-menu-toggle {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 40px;
    height: 40px;
    border: none;
    background: transparent;
    color: var(--text-main);
    cursor: pointer;
    border-radius: var(--radius-md);
    margin-right: 12px;
    transition: all var(--transition-fast);
  }

  .mobile-menu-toggle:hover {
    background: var(--bg-hover);
  }

  .mobile-menu-toggle span {
    font-size: 20px;
  }

  .header-actions {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .header-actions .btn-small {
    padding: 6px 12px;
    font-size: 12px;
  }
}

@media (max-width: 480px) {
  .chat-header {
    padding: 0 12px;
  }

  .chat-viewport {
    padding: 16px 12px;
  }

  .chat-input-area {
    padding: 16px 12px;
  }

  .input-wrapper {
    border-radius: var(--radius-lg);
  }

  .message-input {
    font-size: 14px;
  }

  .message-row {
    max-width: 100%;
  }

  .message-bubble {
    padding: 12px 14px;
    font-size: 13px;
  }

  .sender-name {
    font-size: 12px;
  }

  .time {
    font-size: 11px;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  :root {
    --bg-color: #0f172a;
    --bg-elevated: #1e293b;
    --bg-hover: #334155;
    --bg-active: #475569;

    --text-main: #f1f5f9;
    --text-secondary: #cbd5e1;
    --text-tertiary: #94a3b8;

    --border-color: #334155;
    --border-hover: #475569;
    --border-active: #64748b;

    --assistant-bubble: #1e293b;

    --shadow-sm: 0 1px 3px 0 rgba(0, 0, 0, 0.3), 0 1px 2px 0 rgba(0, 0, 0, 0.2);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.3), 0 2px 4px -1px rgba(0, 0, 0, 0.2);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.3), 0 4px 6px -2px rgba(0, 0, 0, 0.2);
  }

  .chat-content {
    background: linear-gradient(180deg, var(--bg-color) 0%, var(--bg-elevated) 100%);
  }

  .message-row.assistant .message-bubble {
    border-color: var(--border-color);
  }

  .input-wrapper {
    background-color: var(--bg-elevated);
  }
}

/* ================== 参数设置对话框样式 ================== */
.settings-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(135, 135, 135, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
  animation: fadeIn 0.2s ease-out;
}

.settings-dialog {
  background-color: var(--bg-elevated);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-xl);
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dialog-header {
  padding: 24px 32px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: var(--bg-elevated);
}

.dialog-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-main);
}

.btn-close {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  color: var(--text-tertiary);
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.btn-close:hover {
  background-color: var(--bg-hover);
  color: var(--text-secondary);
}

.dialog-body {
  padding: 32px;
  overflow-y: auto;
  flex: 1;
}

.dialog-footer {
  padding: 24px 32px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background-color: var(--bg-elevated);
}

.form-group {
  margin-bottom: 24px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-main);
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-family: var(--font-sans);
  background-color: var(--bg-color);
  color: var(--text-main);
  transition: all var(--transition-base);
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  background-color: var(--bg-elevated);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.form-hint {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .half {
  flex: 1;
}

.form-range {
  width: 100%;
  height: 6px;
  margin: 12px 0;
  background: var(--border-color);
  border-radius: var(--radius-full);
  outline: none;
  -webkit-appearance: none;
}

.form-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--primary-color);
  cursor: pointer;
  border: 2px solid var(--white);
  box-shadow: var(--shadow-sm);
}

.range-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 4px;
}

.agent-selection {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selected-agents {
  flex: 1;
  padding: 12px 16px;
  background-color: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 14px;
}

.no-agents {
  color: var(--text-tertiary);
}

.agent-count {
  color: var(--text-secondary);
}

.btn-select-agents {
  padding: 10px 16px;
  background-color: var(--primary-light);
  color: var(--primary-color);
  border: 1px solid var(--primary-light);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-select-agents:hover {
  background-color: var(--primary-color);
  color: var(--text-inverse);
}

.btn-secondary {
  padding: 10px 20px;
  background-color: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-secondary:hover {
  background-color: var(--bg-hover);
  border-color: var(--border-hover);
}

.btn-primary {
  padding: 10px 20px;
  background-color: var(--primary-color);
  color: var(--text-inverse);
  border: none;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
  box-shadow: var(--shadow-sm);
}

.btn-primary:hover {
  background-color: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-primary:active {
  transform: translateY(0);
}

.btn-edit-settings {
  padding: 8px 16px;
  background-color: var(--primary-light);
  color: var(--primary-color);
  border: 1px solid var(--primary-light);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
  display: flex;
  align-items: center;
  gap: 6px;
}

.btn-edit-settings:hover {
  background-color: var(--primary-color);
  color: var(--text-inverse);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .settings-dialog {
    width: 95%;
    max-height: 85vh;
  }

  .dialog-header,
  .dialog-body,
  .dialog-footer {
    padding: 20px;
  }

  .form-row {
    flex-direction: column;
    gap: 0;
  }

  .form-row .half {
    margin-bottom: 16px;
  }

  .agent-selection {
    flex-direction: column;
    align-items: stretch;
  }
}

/* ================== 优化后的设置界面样式 ================== */
.dialog-title {

  flex: 1;
}

.dialog-title h3 {
  margin: 0 0 4px 0;
  font-size: 20px;
  font-weight: 700;
  color: var(--text-main);
}

.dialog-subtitle {
  margin: 0;
  font-size: 13px;
  color: var(--text-tertiary);
  font-weight: 400;
}

.dialog-tabs {
  display: flex;
  border-bottom: 1px solid var(--border-color);
  background-color: var(--bg-elevated);
  padding: 0 32px;
}

.tab-btn {
  flex: 1;
  padding: 16px 0;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-tertiary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all var(--transition-base);
}

.tab-btn:hover {
  color: var(--text-secondary);
}

.tab-btn.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.tab-icon {
  font-size: 16px;
}

.tab-content {
  animation: fadeIn 0.3s ease-out;
}

.form-section {
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-main);
}

.section-icon {
  font-size: 18px;
}

.form-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-main);
}

.label-icon {
  margin-right: 8px;
  font-size: 16px;
}

.value-display {
  font-size: 14px;
  font-weight: 600;
  color: var(--primary-color);
  background: var(--primary-light);
  padding: 4px 10px;
  border-radius: var(--radius-sm);
}

.select-wrapper {
  position: relative;
}

.select-wrapper .form-select {
  padding-right: 40px;
}

.select-wrapper .select-arrow {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  font-size: 12px;
  color: var(--text-tertiary);
}

.agent-selection-card {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.agent-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-color);
}

.agent-card-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-main);
}

.agent-card-count {
  font-size: 12px;
  font-weight: 500;
  color: var(--primary-color);
  background: var(--primary-light);
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.agent-card-body {
  padding: 20px 16px;
  min-height: 120px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-agents-selected {
  text-align: center;
  color: var(--text-tertiary);
}

.no-agents-icon {
  display: block;
  font-size: 32px;
  margin-bottom: 12px;
  opacity: 0.6;
}

.no-agents-selected p {
  margin: 0 0 6px 0;
  font-size: 14px;
}

.no-agents-selected small {
  font-size: 12px;
}

.selected-agents-list {
  width: 100%;
}

.selected-agent-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--bg-elevated);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  margin-bottom: 8px;
  transition: all var(--transition-fast);
}

.selected-agent-item:hover {
  border-color: var(--border-hover);
  background: var(--bg-hover);
}

.agent-avatar {
  font-size: 20px;
  flex-shrink: 0;
}

.agent-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-main);
}

.remove-agent-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  color: var(--text-tertiary);
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.remove-agent-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
}

.agent-card-footer {
  padding: 16px;
  border-top: 1px solid var(--border-color);
  background: var(--bg-elevated);
}

.btn-add-agents {
  width: 100%;
  padding: 12px;
  background: var(--primary-light);
  color: var(--primary-color);
  border: 1px solid var(--primary-light);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all var(--transition-base);
}

.btn-add-agents:hover {
  background: var(--primary-color);
  color: var(--text-inverse);
}

.btn-icon {
  font-size: 16px;
  font-weight: 600;
}

.slider-container {
  margin-top: 8px;
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.slider-label {
  flex: 1;
  text-align: center;
}

.slider-hint {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-tertiary);
  line-height: 1.4;
}

.input-with-unit {
  position: relative;
}

.input-with-unit .form-input {
  padding-right: 70px;
}

.input-unit {
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  font-size: 14px;
  color: var(--text-tertiary);
}

.metadata-editor {
  background: var(--bg-color);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-elevated);
  border-bottom: 1px solid var(--border-color);
}

.editor-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-main);
}

.btn-format {
  padding: 4px 12px;
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-format:hover {
  background: var(--bg-hover);
  border-color: var(--border-hover);
}

.metadata-textarea {
  font-family: var(--font-mono);
  font-size: 13px;
  line-height: 1.5;
  border: none;
  border-radius: 0;
  min-height: 120px;
  background: var(--bg-color);
}

.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--bg-elevated);
  border-top: 1px solid var(--border-color);
}

.json-status {
  font-size: 11px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: var(--radius-sm);
  background: rgba(239, 68, 68, 0.1);
  color: var(--danger-color);
}

.json-status.valid {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
}

.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  user-select: none;
}

.checkbox-input {
  display: none;
}

.checkbox-custom {
  width: 18px;
  height: 18px;
  border: 2px solid var(--border-color);
  border-radius: var(--radius-sm);
  background: var(--bg-elevated);
  position: relative;
  transition: all var(--transition-fast);
}

.checkbox-input:checked + .checkbox-custom {
  background: var(--primary-color);
  border-color: var(--primary-color);
}

.checkbox-input:checked + .checkbox-custom::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: var(--text-inverse);
  font-size: 12px;
  font-weight: bold;
}

.checkbox-text {
  font-size: 14px;
  color: var(--text-main);
}

.footer-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.primary-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.btn-outline {
  padding: 10px 20px;
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
}

.btn-outline:hover {
  background: var(--bg-hover);
  border-color: var(--border-hover);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .dialog-tabs {
    padding: 0 20px;
  }

  .tab-btn {
    padding: 14px 0;
    font-size: 13px;
  }

  .form-section {
    margin-bottom: 24px;
    padding-bottom: 20px;
  }

  .agent-card-body {
    min-height: 100px;
    padding: 16px;
  }

  .footer-actions {
    flex-direction: column;
    gap: 16px;
  }

  .primary-actions {
    width: 100%;
    justify-content: space-between;
  }

  .btn-outline,
  .btn-primary {
    flex: 1;
  }
}
</style>

<template>
  <div class="home-container">
    <!-- 1. 全局顶部导航栏 -->
    <AppNavbar :user="user" @logout="handleLogout" />

    <el-container class="main-content">
      <!-- 2. 左侧导航侧边栏 -->
      <AppSidebar />

      <!-- 3. 左侧会话菜单栏 -->
      <el-aside class="conversation-sidebar" width="300px">
        <!-- 会话列表区域 -->
        <div class="conversations-section">
          <div class="section-header">
            <h3>我的会话</h3>
            <el-button
              type="primary"
              size="small"
              @click="createNewConversation"
              class="btn-new-conversation"
              title="创建新会话"
            >
              <el-icon><Plus /></el-icon>新建会话
            </el-button>
          </div>

          <div class="conversations-list">
            <div v-if="conversationsLoading" class="loading-conversations">
              <el-icon class="is-loading"><Loading /></el-icon>
              <span>加载会话中...</span>
            </div>

            <div v-else-if="conversations.length === 0" class="no-conversations">
              <p>暂无会话</p>
              <el-button type="primary" size="small" @click="createNewConversation">
                创建第一个会话
              </el-button>
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
                <el-button
                  type="danger"
                  size="small"
                  circle
                  @click.stop="deleteConversation(conversation)"
                  title="删除会话"
                  class="btn-delete-conversation"
                ><el-icon><Delete /></el-icon></el-button>
              </div>
            </div>
          </div>
        </div>
      </el-aside>

      <!-- 4. 核心聊天内容区 -->
      <el-main class="chat-content">
        <!-- 聊天头部 -->
        <el-header class="chat-header">
          <div class="header-info">
            <h2>{{ currentConversation?.title || '实时对话' }}</h2>
            <p class="subtitle">与您的 AI 助手进行互动</p>
          </div>
          <div class="header-actions" v-if="currentConversation">
            <el-button
              type="primary"
              plain
              :icon="Setting"
              @click="openSettingsDialog(currentConversation)"
              title="编辑会话设置"
              class="btn-edit-settings"
            >
              设置
            </el-button>
          </div>
        </el-header>

        <!-- 消息列表区域 -->
        <div class="chat-viewport" ref="chatViewport">
          <div v-if="loading" class="state-container">
            <el-icon class="is-loading"><Loading /></el-icon>
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
                <el-avatar
                  :size="44"
                  :src="message.role === 'user' ? userAvatar : getAgentAvatar(message.role)"
                  :alt="message.role"
                  class="chat-avatar"
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

        <!-- 底部输入框 -->
        <el-footer class="chat-input-area">
          <div class="input-wrapper" :class="{ 'sending': sending }">
            <el-input
              type="textarea"
              v-model="inputMessage"
              :placeholder="sending ? '正在发送...' : '输入消息，Enter 发送...'"
              class="message-input"
              @keyup.enter.native="handleSendMessage"
              :disabled="sending"
              :autosize="{ minRows: 1, maxRows: 4 }"
              resize="none"
            />
            <el-button
              type="primary"
              circle
              @click="handleSendMessage"
              :disabled="!inputMessage.trim() || sending"
              class="btn-send"
              :loading="sending"
            >
              <el-icon v-if="sending"><Loading /></el-icon>
              <el-icon v-else><Right /></el-icon>
            </el-button>
          </div>
        </el-footer>
      </el-main>
    </el-container>

    <!-- 参数设置对话框 -->
    <el-dialog
      v-model="showSettingsDialog"
      :title="currentConversation ? '编辑会话设置' : '创建新会话'"
      width="500px"
      :before-close="closeSettingsDialog"
      class="settings-dialog"
    >
      <div class="dialog-tabs">
        <el-tabs v-model="activeTab">
          <el-tab-pane label="基本设置" name="basic">
            <div class="form-section">
              <h4 class="section-title">
                <el-icon><ChatDotRound /></el-icon> 会话信息
              </h4>
              <el-form :model="conversationSettings" label-width="120px">
                <el-form-item label="会话标题">
                  <el-input
                    v-model="conversationSettings.title"
                    placeholder="例如：项目讨论、学习助手..."
                    clearable
                  />
                  <div class="form-hint">为会话起一个有意义的名字，方便后续查找</div>
                </el-form-item>

                <el-form-item label="AI 模型">
                  <el-select
                    v-model="conversationSettings.model"
                    placeholder="请选择模型"
                    clearable
                    style="width: 100%"
                  >
                    <el-option
                      v-for="model in chat_model"
                      :key="model.id"
                      :label="model.name"
                      :value="model.name"
                    />
                  </el-select>
                  <div class="form-hint">如果留空，将使用所选智能体的默认模型</div>
                </el-form-item>

                <el-form-item label="插件选择">
                  <div class="tools-list">
                    <el-checkbox-group v-model="conversationSettings.agentIds">
                      <el-checkbox
                        v-for="tool in tools_list"
                        :key="tool.id"
                        :label="tool.id"
                        :value="tool.id"
                      >
                        {{ tool.name }}
                      </el-checkbox>
                    </el-checkbox-group>
                    <div v-if="tools_list.length === 0" class="no-agents-available">
                      <el-icon><Tools /></el-icon>
                      <p>暂无可用插件</p>
                    </div>
                  </div>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>

          <el-tab-pane label="高级设置" name="advanced">
            <div class="form-section">
              <h4 class="section-title">
                <el-icon><Operation /></el-icon> 模型参数
              </h4>
              <el-form :model="conversationSettings" label-width="120px">
                <el-form-item label="温度控制">
                  <div class="slider-container">
                    <el-slider
                      v-model="conversationSettings.temperature"
                      :min="0"
                      :max="2"
                      :step="0.1"
                      :show-input="true"
                      :format-tooltip="(value) => value.toFixed(1)"
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
                </el-form-item>

                <el-form-item label="最大令牌数">
                  <el-input-number
                    v-model="conversationSettings.maxTokens"
                    :min="1"
                    :max="8192"
                    controls-position="right"
                    style="width: 100%"
                  />
                  <div class="form-hint">控制单次回复的最大长度，建议值：1024-4096</div>
                </el-form-item>

                <el-form-item label="自定义元数据">
                  <div class="metadata-editor">
                    <div class="editor-header">
                      <span class="editor-title">JSON 编辑器</span>
                      <el-button
                        type="primary"
                        size="small"
                        @click="formatMetadata"
                        title="格式化 JSON"
                      >
                        格式化
                      </el-button>
                    </div>
                    <el-input
                      type="textarea"
                      v-model="metadataJson"
                      placeholder='{
  "key": "value",
  "category": "general"
}'
                      :rows="6"
                      :class="{ 'is-error': !isJsonValid }"
                    />
                    <div class="editor-footer">
                      <div class="form-hint">可选的会话元数据，用于存储自定义信息</div>
                      <span class="json-status" :class="{ valid: isJsonValid }">
                        {{ isJsonValid ? '✓ JSON 有效' : '⚠ 检查 JSON 格式' }}
                      </span>
                    </div>
                  </div>
                </el-form-item>

                <el-form-item label="性能选项">
                  <el-checkbox-group v-model="performanceOptions">
                    <el-checkbox label="streaming">启用流式响应</el-checkbox>
                    <el-checkbox label="cache">启用响应缓存</el-checkbox>
                  </el-checkbox-group>
                </el-form-item>
              </el-form>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>

      <template #footer>
        <span class="dialog-footer">
          <el-button @click="closeSettingsDialog">取消</el-button>
          <el-button
            v-if="activeTab === 'advanced'"
            @click="resetToDefaults"
            class="btn-outline"
          >
            恢复默认
          </el-button>
          <el-button
            type="primary"
            @click="saveConversationSettings"
            :loading="loading"
          >
            {{ currentConversation ? '保存设置' : '创建会话' }}
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
// 保留核心逻辑，已清理无用代码
import AppNavbar from '../components/AppNavbar.vue'
import AppSidebar from '../components/AppSidebar.vue'
import api from '../utils/api.js'
import {
  Plus,
  Delete,
  Setting,
  Loading,
  Right,
  ChatDotRound,
  Tools,
  Operation
} from '@element-plus/icons-vue'

export default {
  name: 'ConversationView',
  components: {
    AppNavbar,
    AppSidebar,
    Plus,
    Delete,
    Setting,
    Loading,
    Right,
    ChatDotRound,
    Tools,
    Operation
  },
  data() {
    return {
      user: null,
      agents: [],
      chat_model: [], // List for chat models
      tools_list: [], // List for tools
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
    },
    performanceOptions: {
      get() {
        const options = []
        if (this.conversationSettings.streaming) options.push('streaming')
        if (this.conversationSettings.cache) options.push('cache')
        return options
      },
      set(value) {
        this.conversationSettings.streaming = value.includes('streaming')
        this.conversationSettings.cache = value.includes('cache')
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
        this.tools_list = this.agents.filter(agent => agent.category === 'tool');

        // Log tools_list to the console
        console.log('Tools List:', this.tools_list);

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
        metadata: {},
        streaming: true,
        cache: true
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
          agentIds: this.conversationSettings.agentIds,
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
    }
  }
}
</script>

<style scoped>
/* 全局样式优化 */
.home-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  color: #2c3e50;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
  background: #fff;
  border-radius: 12px;
  margin: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

/* 会话侧边栏优化 */
.conversation-sidebar {
  background: #ffffff;
  border-right: 1px solid #e8ebf0;
  display: flex;
  flex-direction: column;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 16px;
  background: linear-gradient(90deg, #f8fafc 0%, #ffffff 100%);
  border-bottom: 1px solid #e8ebf0;
  position: sticky;
  top: 0;
  z-index: 10;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  letter-spacing: 0.5px;
}

.btn-new-conversation {
  padding: 6px 12px;
  font-size: 12px;
  border-radius: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.2);
  transition: all 0.3s ease;
}

.btn-new-conversation:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.conversations-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  background: #fafbfd;
}

.conversations-list::-webkit-scrollbar {
  width: 4px;
}

.conversations-list::-webkit-scrollbar-track {
  background: #f1f3f9;
}

.conversations-list::-webkit-scrollbar-thumb {
  background: #c1c9d2;
  border-radius: 2px;
}

.loading-conversations,
.no-conversations {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 16px;
  text-align: center;
  color: #8a94a6;
}

.loading-conversations .el-icon {
  margin-bottom: 16px;
  font-size: 28px;
  color: #667eea;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.no-conversations p {
  margin-bottom: 20px;
  font-size: 14px;
  color: #8a94a6;
}

.conversation-item {
  display: flex;
  padding: 14px;
  margin-bottom: 10px;
  border-radius: 12px;
  background: #ffffff;
  border: 1px solid #e8ebf0;
  cursor: pointer;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
}

.conversation-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  height: 100%;
  width: 3px;
  background: transparent;
  transition: all 0.3s ease;
}

.conversation-item:hover {
  background: linear-gradient(90deg, #f8fafc 0%, #ffffff 100%);
  border-color: #d0d7e3;
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
}

.conversation-item:hover::before {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
}

.conversation-item.active {
  background: linear-gradient(90deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.08) 100%);
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.1);
}

.conversation-item.active::before {
  background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
}

.conversation-info {
  flex: 1;
  min-width: 0;
  margin-right: 12px;
}

.conversation-title {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a1a;
  margin-bottom: 6px;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-preview {
  font-size: 12px;
  color: #8a94a6;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.conversation-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-content: space-between;
  min-width: 60px;
}

.conversation-time {
  font-size: 11px;
  color: #b0b8c5;
  margin-bottom: 8px;
  white-space: nowrap;
}

.btn-delete-conversation {
  padding: 4px;
  width: 28px;
  height: 28px;
  border: 1px solid #ffe0e0;
  background: #fff5f5;
  transition: all 0.2s ease;
}

.btn-delete-conversation:hover {
  background: #f56565;
  border-color: #f56565;
  transform: scale(1.1);
}

.btn-delete-conversation:hover :deep(svg) {
  color: white;
}

/* 聊天内容区优化 */
.chat-content {
  display: flex;
  flex-direction: column;
  background: linear-gradient(180deg, #ffffff 0%, #fafbfd 100%);
  position: relative;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 28px;
  background: #ffffff;
  border-bottom: 1px solid #e8ebf0;
  height: 72px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.04);
  position: sticky;
  top: 0;
  z-index: 10;
}

.header-info h2 {
  margin: 0 0 6px 0;
  font-size: 20px;
  font-weight: 700;
  color: #1a1a1a;
  letter-spacing: -0.3px;
}

.header-info .subtitle {
  margin: 0;
  font-size: 13px;
  color: #8a94a6;
  letter-spacing: 0.3px;
}

.btn-edit-settings {
  padding: 8px 16px;
  border-radius: 8px;
  border: 1px solid #e8ebf0;
  background: #ffffff;
  color: #667eea;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-edit-settings:hover {
  background: #667eea;
  color: white;
  border-color: #667eea;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.chat-viewport {
  flex: 1;
  overflow-y: auto;
  padding: 28px;
  background: linear-gradient(180deg, #fafbfd 0%, #ffffff 100%);
}

.chat-viewport::-webkit-scrollbar {
  width: 6px;
}

.chat-viewport::-webkit-scrollbar-track {
  background: #f1f3f9;
}

.chat-viewport::-webkit-scrollbar-thumb {
  background: #c1c9d2;
  border-radius: 3px;
}

.state-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #8a94a6;
}

.state-container .el-icon {
  margin-bottom: 20px;
  font-size: 36px;
  color: #667eea;
  opacity: 0.8;
}

.state-container.empty {
  animation: fadeInUp 0.6s ease-out;
}

.empty-icon {
  font-size: 56px;
  margin-bottom: 20px;
  opacity: 0.9;
  filter: drop-shadow(0 4px 8px rgba(0, 0, 0, 0.1));
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.messages-list {
  display: flex;
  flex-direction: column;
  gap: 28px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
}

.message-row {
  display: flex;
  gap: 16px;
  animation: messageAppear 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes messageAppear {
  from {
    opacity: 0;
    transform: translateY(20px) scale(0.98);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.message-row.user {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.message-row.assistant {
  align-self: flex-start;
}

.avatar-col {
  flex-shrink: 0;
}

.chat-avatar {
  border: 2px solid white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.chat-avatar:hover {
  transform: scale(1.05);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.bubble-col {
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-width: calc(100% - 60px);
}

.message-meta {
  display: flex;
  gap: 10px;
  align-items: center;
  font-size: 12px;
  color: #8a94a6;
  padding: 0 6px;
  letter-spacing: 0.3px;
}

.message-row.user .message-meta {
  justify-content: flex-end;
}

.sender-name {
  font-weight: 600;
  color: #4a5568;
}

.time {
  font-size: 11px;
  opacity: 0.7;
  font-family: 'SF Mono', Monaco, 'Cascadia Mono', monospace;
}

.message-bubble {
  padding: 16px 20px;
  border-radius: 20px;
  font-size: 14.5px;
  line-height: 1.6;
  word-wrap: break-word;
  position: relative;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  animation: bubbleRise 0.3s ease-out;
}

@keyframes bubbleRise {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-row.user .message-bubble {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 20px 20px 6px 20px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.message-row.assistant .message-bubble {
  background: white;
  color: #2d3748;
  border: 1px solid #e8ebf0;
  border-radius: 20px 20px 20px 6px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.05);
}

.message-row.assistant .message-bubble::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 16px;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 8px 8px 8px 0;
  border-color: transparent #e8ebf0 transparent transparent;
}

.message-row.assistant .message-bubble::after {
  content: '';
  position: absolute;
  left: -7px;
  top: 16px;
  width: 0;
  height: 0;
  border-style: solid;
  border-width: 8px 8px 8px 0;
  border-color: transparent white transparent transparent;
}

/* 输入框区域优化 */
.chat-input-area {
  padding: 10px 10px;
  height: 200px;
  /* border-top: 1px solid #e8ebf0; */
  /* box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.04); */
  position: sticky;
  bottom: 0;
  z-index: 10;
}


.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: 16px;
  background: #ffffff;
  border: 2px solid #e8ebf0;
  border-radius: 16px;
  padding: 12px 16px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  width: 100%;
  max-width: 900px;
  margin: 0 auto;
}

.input-wrapper:hover {
  border-color: #c1c9d2;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.input-wrapper:focus-within {
  border-color: #667eea;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);
  transform: translateY(-1px);
}

.input-wrapper.sending {
  opacity: 0.8;
  background: #f8fafc;
}



.message-input {
  flex: 1 1 0%;
  font-size: 14.5px;
  color: #2d3748;
  outline: none;
  resize: none;
  min-height: 140px;
  max-height: 240px;
  line-height: 1.5;
  font-family: inherit;
  box-shadow: none !important;
}

/* 强制去除 el-input textarea 的边框和背景 */
.message-input :deep(.el-textarea__inner),
.message-input >>> .el-textarea__inner {
  border: none !important;
  background: transparent !important;
  box-shadow: none !important;
  resize: none !important;
  padding-left: 0 !important;
  padding-right: 0 !important;
}

.message-input::placeholder {
  color: #a0aec0;
  opacity: 0.7;
}

.btn-send {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
  flex-shrink: 0;
}

.btn-send:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.btn-send:disabled {
  background: #c1c9d2;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

/* 设置对话框样式优化 */
.settings-dialog :deep(.el-dialog) {
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.settings-dialog :deep(.el-dialog__header) {
  background: linear-gradient(90deg, #f8fafc 0%, #ffffff 100%);
  border-bottom: 1px solid #e8ebf0;
  padding: 20px 24px;
  margin: 0;
}

.settings-dialog :deep(.el-dialog__title) {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a1a;
}

.dialog-tabs {
  margin-bottom: 8px;
}

.dialog-tabs :deep(.el-tabs__header) {
  margin: 0 0 20px 0;
  padding: 0 24px;
}

.dialog-tabs :deep(.el-tabs__nav-wrap::after) {
  height: 1px;
  background: #e8ebf0;
}

.dialog-tabs :deep(.el-tabs__item) {
  padding: 0 16px;
  height: 48px;
  font-weight: 500;
  color: #8a94a6;
  transition: all 0.3s ease;
}

.dialog-tabs :deep(.el-tabs__item:hover) {
  color: #667eea;
}

.dialog-tabs :deep(.el-tabs__item.is-active) {
  color: #667eea;
  font-weight: 600;
}

.dialog-tabs :deep(.el-tabs__active-bar) {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  height: 3px;
  border-radius: 3px 3px 0 0;
}

.form-section {
  margin-bottom: 32px;
  padding: 0 24px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0 0 20px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a1a;
  padding-bottom: 12px;
  border-bottom: 1px solid #e8ebf0;
}

.section-title .el-icon {
  font-size: 18px;
  color: #667eea;
}

.form-hint {
  display: block;
  margin-top: 6px;
  font-size: 12px;
  color: #8a94a6;
  line-height: 1.4;
}

.slider-container {
  width: 100%;
  padding: 8px 0;
}

.slider-container :deep(.el-slider__runway) {
  height: 6px;
  background: #e8ebf0;
  border-radius: 3px;
}

.slider-container :deep(.el-slider__bar) {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  height: 6px;
  border-radius: 3px;
}

.slider-container :deep(.el-slider__button) {
  width: 20px;
  height: 20px;
  border: 3px solid #667eea;
  background: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
  transition: all 0.2s ease;
}

.slider-container :deep(.el-slider__button:hover) {
  transform: scale(1.2);
}

.slider-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  font-size: 12px;
  color: #8a94a6;
}

.slider-label {
  font-weight: 500;
}

.metadata-editor {
  border: 1px solid #e8ebf0;
  border-radius: 12px;
  overflow: hidden;
  background: #f8fafc;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #ffffff;
  border-bottom: 1px solid #e8ebf0;
}

.editor-title {
  font-size: 14px;
  font-weight: 600;
  color: #4a5568;
}

.editor-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #ffffff;
  border-top: 1px solid #e8ebf0;
}

.json-status {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 12px;
  background: #f0f9ff;
}

.json-status.valid {
  color: #10b981;
  background: #ecfdf5;
}

.json-status:not(.valid) {
  color: #f59e0b;
  background: #fffbeb;
}

.tools-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 240px;
  overflow-y: auto;
  padding: 16px;
  border: 1px solid #e8ebf0;
  border-radius: 12px;
  background: #f8fafc;
}

.tools-list :deep(.el-checkbox) {
  margin-right: 0;
  padding: 10px 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e8ebf0;
  transition: all 0.2s ease;
}

.tools-list :deep(.el-checkbox:hover) {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.04);
  transform: translateY(-1px);
}

.no-agents-available {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 24px;
  color: #a0aec0;
  text-align: center;
}

.no-agents-available .el-icon {
  font-size: 32px;
  margin-bottom: 16px;
  opacity: 0.6;
}

.no-agents-available p {
  margin: 0;
  font-size: 14px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  background: #f8fafc;
  border-top: 1px solid #e8ebf0;
}

.btn-outline {
  border: 1px solid #e8ebf0;
  color: #4a5568;
  background: white;
  padding: 10px 20px;
  border-radius: 10px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn-outline:hover {
  border-color: #667eea;
  color: #667eea;
  background: rgba(102, 126, 234, 0.04);
  transform: translateY(-1px);
}

.dialog-footer :deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 10px 24px;
  border-radius: 10px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.dialog-footer :deep(.el-button--primary:hover) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3);
}

/* 响应式设计优化 */
@media (max-width: 768px) {
  .main-content {
    margin: 4px;
    border-radius: 8px;
  }

  .conversation-sidebar {
    width: 100% !important;
    position: fixed;
    left: 0;
    top: 0;
    bottom: 0;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 0 40px rgba(0, 0, 0, 0.15);
  }

  .conversation-sidebar.mobile-open {
    transform: translateX(0);
  }

  .chat-header {
    padding: 0 16px;
    height: 60px;
  }

  .header-info h2 {
    font-size: 17px;
    margin-bottom: 4px;
  }

  .header-info .subtitle {
    font-size: 12px;
  }

  .chat-viewport {
    padding: 16px;
  }

  .chat-input-area {
    padding: 16px;
  }

  .input-wrapper {
    padding: 10px 14px;
    gap: 12px;
  }

  .btn-send {
    width: 40px;
    height: 40px;
  }

  .message-row {
    max-width: 95%;
    gap: 12px;
  }

  .message-bubble {
    padding: 14px 16px;
    font-size: 14px;
  }

  .settings-dialog :deep(.el-dialog) {
    width: 90% !important;
    margin: 20px auto !important;
    border-radius: 12px;
  }

  .form-section {
    padding: 0 16px;
  }

  .dialog-tabs :deep(.el-tabs__header) {
    padding: 0 16px;
  }
}

@media (max-width: 480px) {
  .home-container {
    background: #f8fafc;
  }

  .main-content {
    margin: 0;
    border-radius: 0;
    box-shadow: none;
  }

  .section-header {
    padding: 16px;
  }

  .btn-new-conversation span {
    display: none;
  }

  .btn-new-conversation .el-icon {
    margin: 0 !important;
  }

  .conversations-list {
    padding: 8px;
  }

  .conversation-item {
    padding: 12px;
    margin-bottom: 8px;
  }

  .conversation-preview {
    -webkit-line-clamp: 1;
  }

  .messages-list {
    gap: 20px;
  }

  .message-bubble {
    padding: 12px 14px;
    border-radius: 16px;
  }
}
</style>
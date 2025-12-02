<template>
  <div class="plugins-container">
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
        <nav class="menu">
          <ul class="menu-list">
            <li class="menu-item">
              <router-link to="/home" class="menu-link" active-class="active">
                <span class="menu-icon">🏠</span>
                <span class="menu-text">主页</span>
              </router-link>
            </li>
            <li class="menu-item">
              <router-link to="/plugins" class="menu-link" active-class="active">
                <span class="menu-icon">🔌</span>
                <span class="menu-text">插件</span>
              </router-link>
            </li>
            <li class="menu-item">
              <router-link to="/workflow" class="menu-link" active-class="active">
                <span class="menu-icon">🔄</span>
                <span class="menu-text">工作流</span>
              </router-link>
            </li>
            <li class="menu-item">
              <router-link to="/knowledge" class="menu-link" active-class="active">
                <span class="menu-icon">📚</span>
                <span class="menu-text">知识库</span>
              </router-link>
            </li>
          </ul>
        </nav>
      </aside>
      
      <!-- 插件页面内容 -->
      <main class="content">
        <div class="plugins-layout">
          <!-- 左侧插件列表区域 -->
          <div class="plugins-list-section">
            <div class="list-header">
              <div class="search-filter-bar">
                <input
                  type="text"
                  v-model="searchKeyword"
                  class="search-input"
                  placeholder="搜索插件名称..."
                  @input="handleSearch"
                />
                <div class="filter-buttons">
                  <button
                    class="filter-btn"
                    :class="{ active: filterType === 'all' }"
                    @click="filterType = 'all'; loadPlugins()"
                  >
                    全部
                  </button>
                  <button
                    class="filter-btn"
                    :class="{ active: filterType === 'my' }"
                    @click="filterType = 'my'; loadPlugins()"
                  >
                    我的插件
                  </button>
                  <button
                    class="filter-btn"
                    :class="{ active: filterType === 'system' }"
                    @click="filterType = 'system'; loadPlugins()"
                  >
                    系统插件
                  </button>
                </div>
              </div>
              <button class="btn-create-plugin" @click="showCreateModal = true">
                + 创建插件
              </button>
            </div>
            
            <div class="plugins-list" v-if="!loading && plugins.length > 0">
              <div
                v-for="plugin in plugins"
                :key="plugin.id"
                class="plugin-card"
                :class="{ active: selectedPlugin?.id === plugin.id }"
                @click="selectPlugin(plugin)"
              >
                <div class="plugin-card-header">
                  <h3 class="plugin-name">{{ plugin.name }}</h3>
                  <div class="plugin-badges">
                    <span v-if="plugin.is_system === 1" class="badge badge-system">系统</span>
                    <span v-if="plugin.is_active === 1" class="badge badge-active">激活</span>
                    <span v-else class="badge badge-inactive">未激活</span>
                  </div>
                </div>
                <p class="plugin-description">{{ plugin.description || '无描述' }}</p>
                <div class="plugin-card-actions">
                  <button
                    class="btn-action btn-edit"
                    @click.stop="handleEditPlugin(plugin)"
                    title="编辑插件"
                  >
                    编辑
                  </button>
                  <button
                    v-if="plugin.is_system !== 1"
                    class="btn-action btn-delete"
                    @click.stop="handleDeletePlugin(plugin)"
                    title="删除插件"
                  >
                    删除
                  </button>
                </div>
              </div>
            </div>
            
            <div v-if="loading" class="loading-state">
              <p>加载中...</p>
            </div>
            
            <div v-if="!loading && plugins.length === 0" class="empty-state">
              <p>暂无插件</p>
            </div>
          </div>

          <!-- 右侧插件详情/关联管理区域 -->
          <div class="plugin-detail-section">
            <div v-if="!selectedPlugin" class="empty-detail">
              <p>选择一个插件查看详情</p>
            </div>
            
            <div v-else class="plugin-detail-content">
              <div class="detail-header">
                <h2>{{ selectedPlugin.name }}</h2>
                <button class="btn-edit-detail" @click="handleEditPlugin(selectedPlugin)">
                  编辑插件
                </button>
              </div>
              
              <div class="detail-info">
                <div class="info-item">
                  <label>UUID:</label>
                  <span class="info-value">{{ selectedPlugin.uuid }}</span>
                </div>
                <div class="info-item">
                  <label>描述:</label>
                  <span class="info-value">{{ selectedPlugin.description || '无描述' }}</span>
                </div>
                <div class="info-item">
                  <label>状态:</label>
                  <span class="info-value">
                    <span v-if="selectedPlugin.is_active === 1" class="status-active">激活</span>
                    <span v-else class="status-inactive">未激活</span>
                    <span v-if="selectedPlugin.is_system === 1" class="status-system">（系统插件）</span>
                  </span>
                </div>
                <div class="info-item">
                  <label>创建时间:</label>
                  <span class="info-value">{{ formatTime(selectedPlugin.created_at) }}</span>
                </div>
              </div>
              
              <div class="agent-associations">
                <div class="associations-header">
                  <h3>关联的智能体</h3>
                  <button class="btn-add-association" @click="showAgentSelectModal = true">
                    + 添加关联
                  </button>
                </div>
                
                <div v-if="associations.length === 0" class="empty-associations">
                  <p>暂无关联的智能体</p>
                </div>
                
                <div v-else class="associations-list">
                  <div
                    v-for="assoc in associations"
                    :key="assoc.id"
                    class="association-item"
                  >
                    <div class="association-info">
                      <span class="agent-name">{{ assoc.agent_name }}</span>
                      <div class="association-controls">
                        <label class="toggle-label">
                          <input
                            type="checkbox"
                            :checked="assoc.is_enabled === 1"
                            @change="handleToggleAssociation(assoc)"
                          />
                          启用
                        </label>
                        <div class="priority-input">
                          <label>优先级:</label>
                          <input
                            type="number"
                            :value="assoc.priority"
                            @blur="handleUpdatePriority(assoc, $event)"
                            min="0"
                            class="priority-field"
                          />
                        </div>
                      </div>
                    </div>
                    <button
                      class="btn-remove-association"
                      @click="handleRemoveAssociation(assoc)"
                      title="移除关联"
                    >
                      ×
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>

    <!-- 创建/编辑插件弹窗 -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal-content">
        <div class="modal-header">
          <h3>{{ showEditModal ? '编辑插件' : '创建插件' }}</h3>
          <button class="modal-close" @click="closeModals">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label for="pluginName">插件名称 <span class="required">*</span></label>
            <input
              type="text"
              id="pluginName"
              v-model="pluginForm.name"
              class="form-input"
              placeholder="请输入插件名称"
              required
            />
          </div>
          <div class="form-group">
            <label for="pluginDescription">插件描述</label>
            <textarea
              id="pluginDescription"
              v-model="pluginForm.description"
              class="form-textarea"
              rows="3"
              placeholder="请输入插件描述（可选）"
            ></textarea>
          </div>
          <div class="form-group">
            <label for="openapiFile">OpenAPI规范文件 <span class="required">*</span></label>
            <div class="file-upload-area">
              <input
                type="file"
                id="openapiFile"
                ref="fileInput"
                accept=".json"
                @change="handleFileSelect"
                class="file-input"
              />
              <div v-if="selectedFile" class="file-info">
                <span class="file-name">{{ selectedFile.name }}</span>
                <span class="file-size">({{ formatFileSize(selectedFile.size) }})</span>
                <button class="btn-remove-file" @click="removeSelectedFile">×</button>
              </div>
              <div v-else class="file-placeholder">
                点击选择JSON文件或拖拽文件到此处
              </div>
            </div>
          </div>
          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeModals">取消</button>
          <button
            class="btn-confirm"
            @click="handleSubmitPlugin"
            :disabled="!isPluginFormValid || submitting"
          >
            {{ submitting ? '提交中...' : (showEditModal ? '更新' : '创建') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 智能体选择弹窗 -->
    <div v-if="showAgentSelectModal" class="modal-overlay" @click.self="showAgentSelectModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>选择智能体</h3>
          <button class="modal-close" @click="showAgentSelectModal = false">×</button>
        </div>
        <div class="modal-body">
          <div v-if="loadingAgents" class="loading-state">
            <p>加载中...</p>
          </div>
          <div v-else-if="availableAgents.length === 0" class="empty-state">
            <p>没有可用的智能体</p>
          </div>
          <div v-else class="agent-select-list">
            <div
              v-for="agent in availableAgents"
              :key="agent.id"
              class="agent-select-item"
              :class="{ disabled: isAgentAssociated(agent.id) }"
              @click="!isAgentAssociated(agent.id) && selectAgentForAssociation(agent)"
            >
              <div class="agent-select-info">
                <span class="agent-select-name">{{ agent.name }}</span>
                <span v-if="isAgentAssociated(agent.id)" class="already-associated">已关联</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 关联配置弹窗 -->
    <div v-if="showAssociationConfigModal" class="modal-overlay" @click.self="showAssociationConfigModal = false">
      <div class="modal-content">
        <div class="modal-header">
          <h3>配置关联</h3>
          <button class="modal-close" @click="showAssociationConfigModal = false">×</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label>智能体:</label>
            <span class="config-value">{{ selectedAgentForAssociation?.name }}</span>
          </div>
          <div class="form-group">
            <label>
              <input
                type="checkbox"
                v-model="associationConfig.isEnabled"
              />
              启用
            </label>
          </div>
          <div class="form-group">
            <label for="priority">优先级:</label>
            <input
              type="number"
              id="priority"
              v-model.number="associationConfig.priority"
              min="0"
              class="form-input"
            />
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="showAssociationConfigModal = false">取消</button>
          <button
            class="btn-confirm"
            @click="handleCreateAssociation"
            :disabled="creatingAssociation"
          >
            {{ creatingAssociation ? '创建中...' : '确认' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../utils/api.js'

export default {
  name: 'PluginsView',
  data() {
    return {
      user: null,
      plugins: [],
      selectedPlugin: null,
      associations: [],
      filterType: 'all',
      searchKeyword: '',
      loading: false,
      loadingAgents: false,
      availableAgents: [],
      showCreateModal: false,
      showEditModal: false,
      showAgentSelectModal: false,
      showAssociationConfigModal: false,
      submitting: false,
      creatingAssociation: false,
      errorMessage: '',
      pluginForm: {
        name: '',
        description: '',
        is_active: 1
      },
      selectedFile: null,
      editingPlugin: null,
      selectedAgentForAssociation: null,
      associationConfig: {
        isEnabled: true,
        priority: 0
      }
    }
  },
  computed: {
    isPluginFormValid() {
      return (
        this.pluginForm.name.trim() !== '' &&
        (this.selectedFile || this.showEditModal)
      )
    }
  },
  mounted() {
    this.getUserInfo()
    this.checkLoginStatus()
    this.loadPlugins()
  },
  methods: {
    getUserInfo() {
      this.user = api.auth.getCurrentUser()
    },
    
    checkLoginStatus() {
      if (!api.auth.isLoggedIn()) {
        this.$router.push('/login')
      }
    },
    
    async handleLogout() {
      try {
        await api.auth.logout()
      } catch (error) {
        console.error('退出登录失败:', error)
      } finally {
        this.$router.push('/login')
      }
    },
    
    async loadPlugins() {
      this.loading = true
      try {
        const params = {
          page: 1,
          limit: 100,
          type: this.filterType,
          ...(this.searchKeyword && { search: this.searchKeyword })
        }
        const response = await api.plugin.getPluginList(params)
        this.plugins = response.plugins || []
      } catch (error) {
        console.error('获取插件列表失败:', error)
        alert('获取插件列表失败，请稍后重试')
      } finally {
        this.loading = false
      }
    },
    
    handleSearch() {
      // 防抖处理
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.loadPlugins()
      }, 500)
    },
    
    async selectPlugin(plugin) {
      this.selectedPlugin = plugin
      await this.loadAssociations(plugin.id)
    },
    
    async loadAssociations(pluginId) {
      try {
        const response = await api.plugin.getPluginAgents(pluginId)
        this.associations = response.associations || []
      } catch (error) {
        console.error('获取关联列表失败:', error)
        this.associations = []
      }
    },
    
    handleEditPlugin(plugin) {
      this.editingPlugin = plugin
      this.pluginForm = {
        name: plugin.name,
        description: plugin.description || '',
        is_active: plugin.is_active
      }
      this.selectedFile = null
      this.errorMessage = ''
      this.showEditModal = true
    },
    
    async handleDeletePlugin(plugin) {
      if (plugin.is_system === 1) {
        alert('系统插件不能删除')
        return
      }
      
      if (confirm(`确定要删除插件"${plugin.name}"吗？此操作不可恢复。`)) {
        try {
          await api.plugin.deletePlugin(plugin.id)
          if (this.selectedPlugin?.id === plugin.id) {
            this.selectedPlugin = null
            this.associations = []
          }
          await this.loadPlugins()
        } catch (error) {
          console.error('删除插件失败:', error)
          alert('删除插件失败，请稍后重试')
        }
      }
    },
    
    handleFileSelect(event) {
      const file = event.target.files[0]
      if (file) {
        if (!file.name.endsWith('.json')) {
          this.errorMessage = '请选择JSON格式的文件'
          return
        }
        this.validateOpenAPIFile(file)
      }
    },
    
    async validateOpenAPIFile(file) {
      try {
        const text = await file.text()
        const json = JSON.parse(text)
        
        // 基本OpenAPI规范验证
        if (!json.openapi || !json.info || !json.paths) {
          this.errorMessage = 'OpenAPI规范格式不正确：缺少必需字段（openapi、info、paths）'
          this.selectedFile = null
          return
        }
        
        if (!json.openapi.startsWith('3.')) {
          this.errorMessage = 'OpenAPI规范版本必须是3.x'
          this.selectedFile = null
          return
        }
        
        this.selectedFile = file
        this.errorMessage = ''
      } catch (error) {
        this.errorMessage = 'JSON文件格式错误：' + error.message
        this.selectedFile = null
      }
    },
    
    removeSelectedFile() {
      this.selectedFile = null
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
    },
    
    formatFileSize(bytes) {
      if (bytes === 0) return '0 Bytes'
      const k = 1024
      const sizes = ['Bytes', 'KB', 'MB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
    },
    
    closeModals() {
      this.showCreateModal = false
      this.showEditModal = false
      this.pluginForm = {
        name: '',
        description: '',
        is_active: 1
      }
      this.selectedFile = null
      this.errorMessage = ''
      this.editingPlugin = null
    },
    
    async handleSubmitPlugin() {
      if (!this.isPluginFormValid) {
        this.errorMessage = '请填写所有必填字段'
        return
      }
      
      this.submitting = true
      this.errorMessage = ''
      
      try {
        if (this.showEditModal) {
          // 更新插件
          await api.plugin.updatePlugin(this.editingPlugin.id, {
            name: this.pluginForm.name,
            description: this.pluginForm.description,
            openapiFile: this.selectedFile,
            is_active: this.pluginForm.is_active
          })
        } else {
          // 创建插件
          await api.plugin.createPlugin(
            this.pluginForm.name,
            this.pluginForm.description,
            this.selectedFile
          )
        }
        
        this.closeModals()
        await this.loadPlugins()
      } catch (error) {
        console.error('操作失败:', error)
        this.errorMessage = error.message || '操作失败，请稍后重试'
      } finally {
        this.submitting = false
      }
    },
    
    async loadAvailableAgents() {
      this.loadingAgents = true
      try {
        const response = await api.agent.getAgentList({ page: 1, limit: 100 })
        this.availableAgents = response.agents || []
      } catch (error) {
        console.error('获取智能体列表失败:', error)
        this.availableAgents = []
      } finally {
        this.loadingAgents = false
      }
    },
    
    isAgentAssociated(agentId) {
      return this.associations.some(assoc => assoc.agent_id === agentId)
    },
    
    selectAgentForAssociation(agent) {
      this.selectedAgentForAssociation = agent
      this.associationConfig = {
        isEnabled: true,
        priority: 0
      }
      this.showAgentSelectModal = false
      this.showAssociationConfigModal = true
    },
    
    async handleCreateAssociation() {
      if (!this.selectedPlugin || !this.selectedAgentForAssociation) {
        return
      }
      
      this.creatingAssociation = true
      try {
        await api.plugin.createPluginAgent(
          this.selectedPlugin.id,
          this.selectedAgentForAssociation.id,
          this.associationConfig.isEnabled,
          this.associationConfig.priority
        )
        
        this.showAssociationConfigModal = false
        this.selectedAgentForAssociation = null
        await this.loadAssociations(this.selectedPlugin.id)
      } catch (error) {
        console.error('创建关联失败:', error)
        alert('创建关联失败，请稍后重试')
      } finally {
        this.creatingAssociation = false
      }
    },
    
    async handleToggleAssociation(assoc) {
      try {
        await api.plugin.updatePluginAgent(
          this.selectedPlugin.id,
          assoc.id,
          !assoc.is_enabled,
          assoc.priority
        )
        await this.loadAssociations(this.selectedPlugin.id)
      } catch (error) {
        console.error('更新关联失败:', error)
        alert('更新关联失败，请稍后重试')
      }
    },
    
    async handleUpdatePriority(assoc, event) {
      const newPriority = parseInt(event.target.value) || 0
      if (newPriority === assoc.priority) {
        return
      }
      
      try {
        await api.plugin.updatePluginAgent(
          this.selectedPlugin.id,
          assoc.id,
          assoc.is_enabled === 1,
          newPriority
        )
        await this.loadAssociations(this.selectedPlugin.id)
      } catch (error) {
        console.error('更新优先级失败:', error)
        alert('更新优先级失败，请稍后重试')
        event.target.value = assoc.priority
      }
    },
    
    async handleRemoveAssociation(assoc) {
      if (confirm(`确定要移除与"${assoc.agent_name}"的关联吗？`)) {
        try {
          await api.plugin.deletePluginAgent(this.selectedPlugin.id, assoc.id)
          await this.loadAssociations(this.selectedPlugin.id)
        } catch (error) {
          console.error('删除关联失败:', error)
          alert('删除关联失败，请稍后重试')
        }
      }
    },
    
    formatTime(timeString) {
      if (!timeString) return ''
      const date = new Date(timeString)
      return date.toLocaleString('zh-CN')
    }
  },
  watch: {
    showAgentSelectModal(newVal) {
      if (newVal) {
        this.loadAvailableAgents()
      }
    }
  }
}
</script>

<style scoped>
/* 基础样式和其他页面保持一致 */
.plugins-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: 'Arial', sans-serif;
}

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

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.sidebar {
  width: 200px;
  background-color: #f7fafc;
  border-right: 1px solid #e2e8f0;
  display: flex;
  flex-direction: column;
}

.menu {
  padding: 16px 0;
  flex: 1;
}

.menu-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.menu-item {
  margin-bottom: 4px;
}

.menu-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  text-decoration: none;
  color: #4a5568;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
  border-radius: 0 6px 6px 0;
}

.menu-link:hover {
  background-color: #edf2f7;
  color: #2d3748;
}

.menu-link.active {
  background-color: #667eea;
  color: white;
}

.menu-icon {
  font-size: 18px;
}

.menu-text {
  flex: 1;
}

.content {
  flex: 1;
  padding: 24px;
  background-color: #f8fafc;
  overflow-y: auto;
}

/* 插件布局样式 */
.plugins-layout {
  display: flex;
  gap: 24px;
  height: 100%;
}

.plugins-list-section {
  flex: 0 0 60%;
  display: flex;
  flex-direction: column;
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.list-header {
  margin-bottom: 24px;
}

.search-filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  align-items: center;
}

.search-input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
}

.filter-buttons {
  display: flex;
  gap: 8px;
}

.filter-btn {
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  background-color: white;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  background-color: #f7fafc;
}

.filter-btn.active {
  background-color: #667eea;
  color: white;
  border-color: #667eea;
}

.btn-create-plugin {
  width: 100%;
  padding: 12px;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-create-plugin:hover {
  background-color: #5a67d8;
}

.plugins-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.plugin-card {
  padding: 16px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.plugin-card:hover {
  border-color: #667eea;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.plugin-card.active {
  border-color: #667eea;
  background-color: #f0f4ff;
}

.plugin-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.plugin-name {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.plugin-badges {
  display: flex;
  gap: 8px;
}

.badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.badge-system {
  background-color: #fed7d7;
  color: #c53030;
}

.badge-active {
  background-color: #c6f6d5;
  color: #22543d;
}

.badge-inactive {
  background-color: #e2e8f0;
  color: #4a5568;
}

.plugin-description {
  font-size: 14px;
  color: #718096;
  margin: 8px 0;
  line-height: 1.5;
}

.plugin-card-actions {
  display: flex;
  gap: 8px;
  margin-top: 12px;
}

.btn-action {
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  background-color: white;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-edit {
  color: #667eea;
  border-color: #667eea;
}

.btn-edit:hover {
  background-color: #667eea;
  color: white;
}

.btn-delete {
  color: #e53e3e;
  border-color: #e53e3e;
}

.btn-delete:hover {
  background-color: #e53e3e;
  color: white;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 40px;
  color: #718096;
}

/* 插件详情区域样式 */
.plugin-detail-section {
  flex: 0 0 40%;
  display: flex;
  flex-direction: column;
  background-color: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
}

.empty-detail {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #718096;
}

.plugin-detail-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.detail-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.btn-edit-detail {
  padding: 8px 16px;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
}

.detail-info {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-item {
  display: flex;
  gap: 12px;
}

.info-item label {
  font-weight: 500;
  color: #4a5568;
  min-width: 80px;
}

.info-value {
  color: #2d3748;
}

.status-active {
  color: #22543d;
}

.status-inactive {
  color: #718096;
}

.status-system {
  color: #c53030;
  font-size: 12px;
}

.agent-associations {
  border-top: 1px solid #e2e8f0;
  padding-top: 24px;
}

.associations-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.associations-header h3 {
  font-size: 16px;
  font-weight: 600;
  color: #2d3748;
  margin: 0;
}

.btn-add-association {
  padding: 6px 12px;
  background-color: #667eea;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
}

.empty-associations {
  text-align: center;
  padding: 20px;
  color: #718096;
}

.associations-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.association-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
}

.association-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.agent-name {
  font-weight: 500;
  color: #2d3748;
}

.association-controls {
  display: flex;
  gap: 16px;
  align-items: center;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  cursor: pointer;
}

.priority-input {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
}

.priority-field {
  width: 60px;
  padding: 4px 8px;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 14px;
}

.btn-remove-association {
  width: 24px;
  height: 24px;
  border: none;
  background-color: transparent;
  color: #718096;
  font-size: 20px;
  cursor: pointer;
  border-radius: 4px;
}

.btn-remove-association:hover {
  background-color: #fed7d7;
  color: #c53030;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background-color: white;
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: #a0aec0;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.modal-close:hover {
  background-color: #f7fafc;
  color: #4a5568;
}

.modal-body {
  padding: 24px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #4a5568;
}

.form-group .required {
  color: #e53e3e;
}

.form-input,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  box-sizing: border-box;
}

.form-textarea {
  resize: vertical;
}

.file-upload-area {
  border: 2px dashed #cbd5e0;
  border-radius: 6px;
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
}

.file-upload-area:hover {
  border-color: #667eea;
  background-color: #f7fafc;
}

.file-input {
  display: none;
}

.file-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: #2d3748;
}

.file-name {
  font-weight: 500;
}

.file-size {
  color: #718096;
  font-size: 12px;
}

.btn-remove-file {
  padding: 4px 8px;
  border: none;
  background-color: #fed7d7;
  color: #c53030;
  border-radius: 4px;
  cursor: pointer;
}

.file-placeholder {
  color: #718096;
}

.error-message {
  padding: 12px;
  background-color: #fed7d7;
  color: #c53030;
  border-radius: 6px;
  font-size: 14px;
  margin-top: 12px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 20px 24px;
  border-top: 1px solid #e2e8f0;
}

.btn-cancel,
.btn-confirm {
  padding: 10px 20px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
}

.btn-cancel {
  background-color: #f7fafc;
  color: #4a5568;
  border: 1px solid #e2e8f0;
}

.btn-confirm {
  background-color: #667eea;
  color: white;
}

.btn-confirm:hover:not(:disabled) {
  background-color: #5a67d8;
}

.btn-confirm:disabled {
  background-color: #a0aec0;
  cursor: not-allowed;
  opacity: 0.6;
}

.agent-select-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.agent-select-item {
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.agent-select-item:hover:not(.disabled) {
  border-color: #667eea;
  background-color: #f7fafc;
}

.agent-select-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.agent-select-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.agent-select-name {
  font-weight: 500;
  color: #2d3748;
}

.already-associated {
  font-size: 12px;
  color: #718096;
}

.config-value {
  font-weight: 500;
  color: #2d3748;
}
</style>

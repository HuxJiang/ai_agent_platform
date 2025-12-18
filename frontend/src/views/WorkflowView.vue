<template>
  <div class="workflow-container">
    <!-- 顶部工具栏 -->
    <header class="toolbar">
      <div class="toolbar-left">
        <el-button type="primary" plain class="back-btn" @click="goBackHome">
          🏠 返回首页
        </el-button>
        <div class="logo-circle">WF</div>
        <h3>工作流设计器</h3>
      </div>
      
      <!-- 中间按钮区域：美化后的下拉菜单 -->
      <div class="toolbar-center">
        <el-dropdown class="custom-dropdown" @command="handleAddAgentNode" trigger="click">
          <!-- 自定义触发按钮 -->
          <div class="fancy-trigger-btn">
            <div class="icon-box">🤖</div>
            <span class="trigger-text">添加智能体节点</span>
            <el-icon class="trigger-arrow"><arrow-down /></el-icon>
          </div>
          
          <template #dropdown>
            <el-dropdown-menu class="custom-dropdown-menu">
              <!-- 增加一个简单的标题头，提升体验 -->
              <div class="dropdown-header">可选智能体列表</div>
              
              <el-dropdown-item 
                v-for="agent in agents" 
                :key="agent.id" 
                :command="agent"
                class="styled-dropdown-item"
              >
                <div class="dropdown-item-content">
                  <div class="agent-info-simple">
                    <span class="agent-name-small">{{ agent.name }}</span>
                  </div>
                  <span class="add-icon-hint">+</span>
                </div>
              </el-dropdown-item>
              
              <!-- 空状态处理 -->
              <div v-if="agents.length === 0" class="empty-dropdown">
                暂无可用智能体
              </div>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>

      <div class="toolbar-right">
        <el-button type="success" class="save-btn" @click="handleSave" :loading="saving">
          💾 保存画布
        </el-button>
      </div>
    </header>

    <!-- 画布区域 (保持不变) -->
    <div class="canvas-wrapper">
      <VueFlow
        v-model="elements"
        :default-viewport="{ zoom: 1 }"
        :min-zoom="0.2"
        :max-zoom="4"
        fit-view-on-init
        @pane-ready="onPaneReady"
        @connect="onConnect"
        @node-double-click="onNodeDoubleClick"
      >
        <Background pattern-color="#aaa" :gap="16" />
        <MiniMap />
        <Controls />

        <template #node-custom="{ id, data, selected }">
          <div class="custom-node-shell" :class="[data.type, { selected }]">
            <div 
              v-if="selected" 
              class="delete-handle" 
              @click.stop="removeNode(id)"
              title="删除节点"
            >×</div>
            <Handle type="target" position="left" class="port-handle" />
            <div class="node-content">
              <template v-if="data.type === 'agent'">
                <img 
                  :src="data.avatar || 'https://via.placeholder.com/100'" 
                  :alt="data.label" 
                  class="agent-avatar"
                />
              </template>
              <template v-else>
                <div class="node-icon">{{ getNodeIcon(data.type) }}</div>
              </template>
              <div class="node-label">{{ data.label }}</div>
            </div>
            <Handle type="source" position="right" class="port-handle" />
          </div>
        </template>
      </VueFlow>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// --- 1. 核心库引入 ---
import { 
  VueFlow, 
  useVueFlow, 
  Handle,
} from '@vue-flow/core'

// --- 2. 插件组件引入 ---
import { Background } from '@vue-flow/background'
import { MiniMap } from '@vue-flow/minimap'
import { Controls } from '@vue-flow/controls'

// --- 3. 样式文件引入 ---
import '@vue-flow/core/dist/style.css'
import '@vue-flow/core/dist/theme-default.css'
import '@vue-flow/controls/dist/style.css'
import '@vue-flow/minimap/dist/style.css'

import { ElMessage, ElMessageBox, ElDropdown, ElDropdownMenu, ElDropdownItem } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'

import { getWorkflowData, saveWorkflowData } from '@/utils/workflow'
import api from '../utils/api.js'

// --- 状态定义 ---
const router = useRouter()
const { 
  addEdges, 
  addNodes, 
  removeNodes, 
  findNode, 
  toObject, 
  project, 
  viewport 
} = useVueFlow()

const elements = ref([]) 
const saving = ref(false)
const flowInstance = ref(null)
const agents = ref([])
const user = ref(null)

// --- 生命周期 ---
onMounted(() => {
  getUserInfo()
  loadAgents()
  loadData()
})

// --- 业务逻辑 ---
const getUserInfo = () => {
  user.value = api.auth.getCurrentUser()
}

const loadAgents = async () => {
  try {
    if (!user.value) {
      user.value = await api.getUserInfo()
    }
    const response = await api.agent.getUserAgentList(user.value.id)
    agents.value = response.agents || []
  } catch (error) {
    console.error('获取智能体列表失败:', error)
    ElMessage.error('获取智能体列表失败')
    agents.value = []
  }
}

const loadData = async () => {
  try {
    const res = await getWorkflowData()
    if (res && (res.nodes || res.edges)) {
      elements.value = [...(res.nodes || []), ...(res.edges || [])]
    } else {
      elements.value = []
    }
  } catch (error) {
    ElMessage.error('加载工作流失败')
  }
}

const handleSave = async () => {
  saving.value = true
  try {
    const flowData = toObject()
    await saveWorkflowData(flowData)
    ElMessage.success('保存成功')
  } catch (error) {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const goBackHome = () => {
  router.push('/home')
}

const handleAddAgentNode = (agent) => {
  const id = `node_${Date.now()}_${agent.id}`
  const { x, y, zoom } = viewport.value || { x: 0, y: 0, zoom: 1 }
  const centerX = window.innerWidth / 2
  const centerY = window.innerHeight / 2
  const projected = project({ x: centerX, y: centerY })

  const newNode = {
    id,
    type: 'custom', 
    position: { 
      x: projected.x + Math.random() * 50 - 25, 
      y: projected.y + Math.random() * 50 - 25 
    },
    data: { 
      label: agent.name, 
      type: 'agent',
      agentId: agent.id,
      avatar: agent.avatar
    },
  }
  
  addNodes([newNode])
}

const removeNode = (id) => {
  removeNodes([id])
}

const onConnect = (params) => {
  addEdges([{
    ...params,
    id: `e_${params.source}-${params.target}`,
    type: 'smoothstep', 
    animated: true,     
    style: { stroke: '#555' }
  }])
}

const onNodeDoubleClick = async (event) => {
  const { node } = event
  try {
    const { value } = await ElMessageBox.prompt('请输入新的节点名称', '编辑节点', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      inputValue: node.data.label,
    })
    const targetNode = findNode(node.id)
    if (targetNode) {
      targetNode.data.label = value
    }
  } catch (e) { }    
}

const onPaneReady = (instance) => {
  flowInstance.value = instance
}

const getNodeIcon = (type) => {
  switch(type) {
    case 'start': return '🚀'
    case 'process': return '⚙️'
    case 'end': return '🏁'
    case 'agent': return '🤖'
    default: return '📄'
  }
}
</script>

<style scoped>
.workflow-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  width: 100%;
  background-color: #f5f7fa;
}

/* --- 工具栏样式优化 --- */
.toolbar {
  height: 64px;
  padding: 0 24px;
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05);
  z-index: 10;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  margin-right: 8px;
  padding: 6px 12px;
  font-weight: 500;
  transition: all 0.3s;
  border-radius: 6px;
}

.back-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.2);
}

.logo-circle {
  width: 32px;
  height: 32px;
  background: #409eff;
  color: white;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 14px;
}

.toolbar-left h3 {
  margin: 0;
  font-size: 18px;
  color: #303133;
  font-weight: 600;
}

/* --- 重点：下拉菜单美化区域 --- */
.toolbar-center {
  display: flex;
  justify-content: center;
}

/* 自定义触发器按钮样式 */
.fancy-trigger-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px 8px 8px;
  background-color: #ecf5ff; /* 浅蓝背景 */
  border: 1px solid #d9ecff;
  border-radius: 24px; /* 胶囊形状 */
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  color: #409eff;
  user-select: none;
}

.fancy-trigger-btn:hover {
  background-color: #409eff;
  border-color: #409eff;
  color: white;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.3);
}

.fancy-trigger-btn:active {
  transform: translateY(0);
}

.icon-box {
  width: 32px;
  height: 32px;
  background-color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  transition: transform 0.3s;
}

.fancy-trigger-btn:hover .icon-box {
  transform: scale(1.05);
}

.trigger-text {
  font-weight: 600;
  font-size: 14px;
  padding-right: 4px;
}

.trigger-arrow {
  font-size: 12px;
  transition: transform 0.3s;
}

/* 下拉菜单内部样式 (注意：element-plus dropdown menu 是插入到 body 的，
   所以这里的样式可能需要深度选择器或者在全局样式中定义，
   但为了不破坏你的结构，我们尽量用内联类名控制) */

.dropdown-header {
  padding: 8px 16px;
  font-size: 12px;
  color: #909399;
  border-bottom: 1px solid #ebeef5;
  margin-bottom: 4px;
  font-weight: 500;
}

.styled-dropdown-item {
  padding: 10px 16px !important; /* 增加点击区域 */
  border-radius: 8px;
  margin: 2px 4px;
}

.dropdown-item-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  min-width: 200px;
  padding: 0 4px;
}

.agent-info-simple {
  flex: 1;
  display: flex;
  align-items: center;
}

.agent-name-small {
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  letter-spacing: 0.5px;
  transition: all 0.3s;
}

.styled-dropdown-item:hover .agent-name-small {
  color: #409eff;
  font-weight: 700;
}

.add-icon-hint {
  font-size: 20px;
  color: #409eff;
  opacity: 0;
  transform: translateX(-8px);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: bold;
  background: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 6px rgba(64, 158, 255, 0.2);
}

/* 下拉项 Hover 效果 */
.styled-dropdown-item:hover .add-icon-hint {
  opacity: 1;
  transform: translateX(0);
}

.styled-dropdown-item:hover {
  background-color: #f0f9ff !important;
  transform: translateX(4px);
  border-radius: 12px;
}

.styled-dropdown-item {
  padding: 12px 20px !important;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.empty-dropdown {
  padding: 16px;
  text-align: center;
  color: #909399;
  font-size: 13px;
}

/* --- 保存按钮 --- */
.save-btn {
  padding: 8px 20px;
  font-weight: 600;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(103, 194, 58, 0.2);
}

.canvas-wrapper {
  flex: 1;
  position: relative;
  overflow: hidden;
  background-color: #f0f2f5;
}

/* --- 节点样式 (保持不变) --- */
.custom-node-shell {
  padding: 10px 20px;
  border-radius: 8px;
  background: #fff;
  border: 1px solid #dcdfe6;
  box-shadow: 0 4px 10px rgba(0,0,0,0.08); /* 阴影加深 */
  min-width: 140px;
  text-align: center;
  position: relative; 
  transition: all 0.3s ease;
  cursor: grab;
}

.custom-node-shell:active { cursor: grabbing; }

.custom-node-shell.selected {
  border-color: #409eff;
  box-shadow: 0 0 0 3px rgba(64, 158, 255, 0.2);
}

.custom-node-shell.start { border-left: 5px solid #67c23a; }
.custom-node-shell.process { border-left: 5px solid #409eff; }
.custom-node-shell.end { border-left: 5px solid #f56c6c; }

.node-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  justify-content: center;
  font-size: 14px;
  color: #333;
  font-weight: 500;
}

.agent-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid #e4e7ed;
}

.custom-node-shell.agent { 
  border-left: 5px solid #909399; 
}

.node-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
}

.delete-handle {
  position: absolute;
  top: -8px;
  right: -8px;
  width: 22px;
  height: 22px;
  background: #f56c6c;
  color: white;
  border-radius: 50%;
  font-size: 16px;
  line-height: 20px;
  text-align: center;
  cursor: pointer;
  z-index: 10;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
  border: 2px solid #fff;
}

.delete-handle:hover {
  background: #ff4949;
  transform: scale(1.1);
}

.port-handle {
  width: 10px;
  height: 10px;
  background: #409eff;
  border: 2px solid #fff; /* 增加白色描边让端口更清晰 */
}
</style>
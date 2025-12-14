<template>
  <div class="workflow-container">
    <!-- 顶部工具栏 -->
    <header class="toolbar">
      <div class="toolbar-left">
        <div class="logo-circle">WF</div>
        <h3>工作流设计器</h3>
      </div>
      
      <!-- 中间按钮区域：已美化，增加间距 -->
      <div class="toolbar-center">
        <el-button type="primary" plain class="tool-btn" @click="addNode('start')">
          <span class="btn-icon">🚀</span> 添加开始
        </el-button>
        <el-button type="primary" plain class="tool-btn" @click="addNode('process')">
          <span class="btn-icon">⚙️</span> 添加处理
        </el-button>
        <el-button type="primary" plain class="tool-btn" @click="addNode('end')">
          <span class="btn-icon">🏁</span> 添加结束
        </el-button>
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
              <div class="node-icon">{{ getNodeIcon(data.type) }}</div>
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

import { ElMessage, ElMessageBox } from 'element-plus'

// --- 修改点：路径修正为 utils ---
import { getWorkflowData, saveWorkflowData } from '@/utils/workflow'

// --- 状态定义 ---
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

// --- 生命周期 ---
onMounted(() => {
  loadData()
})

// --- 业务逻辑 ---
const loadData = async () => {
  try {
    const res = await getWorkflowData()
    if (res && (res.nodes || res.edges)) {
      elements.value = [...(res.nodes || []), ...(res.edges || [])]
    } else {
      elements.value = [
        { 
          id: '1', 
          type: 'custom', 
          label: '开始', 
          position: { x: 250, y: 5 }, 
          data: { label: '开始流程', type: 'start' } 
        }
      ]
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

const addNode = (type) => {
  const id = `node_${Date.now()}`
  const { x, y, zoom } = viewport.value || { x: 0, y: 0, zoom: 1 }
  const centerX = window.innerWidth / 2
  const centerY = window.innerHeight / 2
  const projected = project({ x: centerX, y: centerY })

  const labelMap = {
    start: '开始节点',
    process: '处理节点',
    end: '结束节点'
  }

  const newNode = {
    id,
    type: 'custom', 
    position: { 
      x: projected.x + Math.random() * 50 - 25, 
      y: projected.y + Math.random() * 50 - 25 
    },
    data: { 
      label: labelMap[type], 
      type: type 
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
  height: 64px; /* 稍微增高 */
  padding: 0 24px;
  background: #ffffff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  box-shadow: 0 4px 12px rgba(0,0,0,0.05); /* 增加投影 */
  z-index: 10;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
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

/* 重点：中间按钮区域美化 */
.toolbar-center {
  display: flex;
  gap: 12px; /* 按钮之间的间距 */
}

/* 按钮自定义样式，防止 Element 样式未加载时太丑 */
.tool-btn {
  padding: 8px 16px;
  font-weight: 500;
  transition: all 0.3s;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05); /* 轻微阴影 */
  border-radius: 6px;
}

.tool-btn:hover {
  transform: translateY(-2px); /* 悬浮上移效果 */
  box-shadow: 0 4px 8px rgba(64, 158, 255, 0.2);
}

.save-btn {
  padding: 8px 20px;
  font-weight: 600;
  border-radius: 6px;
  box-shadow: 0 2px 6px rgba(103, 194, 58, 0.2);
}

.btn-icon {
  margin-right: 6px;
}

.canvas-wrapper {
  flex: 1;
  position: relative;
  overflow: hidden;
  background-color: #f0f2f5;
}

/* --- 节点样式 (保持不变，微调阴影) --- */
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
  align-items: center;
  gap: 10px;
  justify-content: center;
  font-size: 14px;
  color: #333;
  font-weight: 500;
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
// src/api/workflow.js
import { get, post } from '@/utils/http'

// 模拟的工作流 ID，实际项目中可能从路由参数获取
const CURRENT_WORKFLOW_ID = 'wf_demo_001'

/**
 * 获取工作流详情（包含节点和连线数据）
 * @param {string} id 工作流ID
 */
export function getWorkflowData(id = CURRENT_WORKFLOW_ID) {
  return get(`/workflows/${id}`)
}

/**
 * 保存工作流数据
 * @param {object} data { nodes: [], edges: [], viewport: {} }
 * @param {string} id 工作流ID
 */
export function saveWorkflowData(data, id = CURRENT_WORKFLOW_ID) {
  return post(`/workflows/${id}/save`, data)
}
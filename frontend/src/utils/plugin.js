// 导入必要的工具函数和请求方法
import { get, post, put, del, getAccessToken } from './user.js'

const API_BASE_URL = '/api'

/**
 * 文件上传请求（multipart/form-data）
 */
async function postFormData(endpoint, formData) {
  const url = `${API_BASE_URL}${endpoint}`
  const headers = {}

  // 如果有访问令牌，则添加到请求头
  const token = getAccessToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  // 注意：不要设置Content-Type，让浏览器自动设置multipart/form-data边界
  const response = await fetch(url, {
    method: 'POST',
    headers,
    body: formData
  })

  if (!response.ok) {
    let errorData
    try {
      errorData = await response.json()
    } catch (e) {
      errorData = { message: '请求失败，请稍后重试' }
    }
    throw new Error(errorData.message || `HTTP error! status: ${response.status}`)
  }

  const data = await response.json()
  if (data.code !== 200) {
    throw new Error(data.message || 'API返回错误')
  }

  return data.data
}

/**
 * 文件更新请求（multipart/form-data）
 */
async function putFormData(endpoint, formData) {
  const url = `${API_BASE_URL}${endpoint}`
  const headers = {}

  const token = getAccessToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetch(url, {
    method: 'PUT',
    headers,
    body: formData
  })

  if (!response.ok) {
    let errorData
    try {
      errorData = await response.json()
    } catch (e) {
      errorData = { message: '请求失败，请稍后重试' }
    }
    throw new Error(errorData.message || `HTTP error! status: ${response.status}`)
  }

  const data = await response.json()
  if (data.code !== 200) {
    throw new Error(data.message || 'API返回错误')
  }

  return data.data
}

/**
 * 插件相关API
 */
export const pluginAPI = {
  /**
   * 获取插件列表
   */
  async getPluginList(params = {}) {
    try {
      const queryParams = {
        page: params.page || 1,
        limit: params.limit || 20,
        ...(params.type && { type: params.type }),
        ...(params.search && { search: params.search })
      }
      const response = await get('/plugin/list', queryParams)
      return response
    } catch (error) {
      console.error('获取插件列表失败:', error)
      throw error
    }
  },
  
  /**
   * 创建插件
   */
  async createPlugin(name, description, openapiFile) {
    try {
      const formData = new FormData()
      formData.append('name', name)
      if (description) {
        formData.append('description', description)
      }
      formData.append('openapi_file', openapiFile)
      
      const response = await postFormData('/plugin/create', formData)
      return response
    } catch (error) {
      console.error('创建插件失败:', error)
      throw error
    }
  },
  
  /**
   * 获取插件详情
   */
  async getPlugin(pluginId) {
    try {
      const response = await get(`/plugin/${pluginId}`)
      return response
    } catch (error) {
      console.error('获取插件详情失败:', error)
      throw error
    }
  },
  
  /**
   * 更新插件
   */
  async updatePlugin(pluginId, data) {
    try {
      const formData = new FormData()
      if (data.name !== undefined) {
        formData.append('name', data.name)
      }
      if (data.description !== undefined) {
        formData.append('description', data.description)
      }
      if (data.openapiFile) {
        formData.append('openapi_file', data.openapiFile)
      }
      if (data.is_active !== undefined) {
        formData.append('is_active', data.is_active)
      }
      
      const response = await putFormData(`/plugin/${pluginId}`, formData)
      return response
    } catch (error) {
      console.error('更新插件失败:', error)
      throw error
    }
  },
  
  /**
   * 删除插件
   */
  async deletePlugin(pluginId) {
    try {
      const response = await del(`/plugin/${pluginId}`)
      return response
    } catch (error) {
      console.error('删除插件失败:', error)
      throw error
    }
  },
  
  /**
   * 获取插件的智能体关联列表
   */
  async getPluginAgents(pluginId) {
    try {
      const response = await get(`/plugin/${pluginId}/agents`)
      return response
    } catch (error) {
      console.error('获取插件关联列表失败:', error)
      throw error
    }
  },
  
  /**
   * 创建插件与智能体关联
   */
  async createPluginAgent(pluginId, agentId, isEnabled, priority) {
    try {
      const response = await post(`/plugin/${pluginId}/agent`, {
        agent_id: agentId,
        is_enabled: isEnabled ? 1 : 0,
        priority: priority || 0
      })
      return response
    } catch (error) {
      console.error('创建关联失败:', error)
      throw error
    }
  },
  
  /**
   * 更新插件与智能体关联
   */
  async updatePluginAgent(pluginId, associationId, isEnabled, priority) {
    try {
      const response = await put(`/plugin/${pluginId}/agent/${associationId}`, {
        is_enabled: isEnabled ? 1 : 0,
        priority: priority || 0
      })
      return response
    } catch (error) {
      console.error('更新关联失败:', error)
      throw error
    }
  },
  
  /**
   * 删除插件与智能体关联
   */
  async deletePluginAgent(pluginId, associationId) {
    try {
      const response = await del(`/plugin/${pluginId}/agent/${associationId}`)
      return response
    } catch (error) {
      console.error('删除关联失败:', error)
      throw error
    }
  },
  
  /**
   * 获取智能体的插件关联列表
   */
  async getAgentPlugins(agentId) {
    try {
      const response = await get(`/agent/${agentId}/plugins`)
      return response
    } catch (error) {
      console.error('获取智能体插件列表失败:', error)
      throw error
    }
  },
  
  /**
   * 为智能体添加插件关联
   */
  async createAgentPlugin(agentId, pluginId, isEnabled, priority) {
    try {
      const response = await post(`/agent/${agentId}/plugin`, {
        plugin_id: pluginId,
        is_enabled: isEnabled ? 1 : 0,
        priority: priority || 0
      })
      return response
    } catch (error) {
      console.error('创建关联失败:', error)
      throw error
    }
  },
  
  /**
   * 更新智能体与插件关联
   */
  async updateAgentPlugin(agentId, associationId, isEnabled, priority) {
    try {
      const response = await put(`/agent/${agentId}/plugin/${associationId}`, {
        is_enabled: isEnabled ? 1 : 0,
        priority: priority || 0
      })
      return response
    } catch (error) {
      console.error('更新关联失败:', error)
      throw error
    }
  },
  
  /**
   * 删除智能体与插件关联
   */
  async deleteAgentPlugin(agentId, associationId) {
    try {
      const response = await del(`/agent/${agentId}/plugin/${associationId}`)
      return response
    } catch (error) {
      console.error('删除关联失败:', error)
      throw error
    }
  }
}


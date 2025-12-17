// API基础URL
const API_BASE_URL = '/api'

/**
 * 获取存储在localStorage中的访问令牌
 */
export function getAccessToken() {
  return localStorage.getItem('access_token')
}

/**
 * 通用fetch函数，处理API请求
 */
export async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  // 构建请求头：直接合并options.headers，不再做DELETE的特殊处理
  const headers = { ...options.headers }
  
  // 【删除原有的DELETE请求头处理逻辑】
  // 原逻辑：if (options.method !== 'DELETE' && options.body) { ... }
  // 原逻辑：if (options.method === 'DELETE' && headers['Content-Type']) { delete ... }

  // 补充：如果有请求体（非DELETE场景），默认设置Content-Type（保留原有非DELETE的逻辑）
  if (options.body && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json'
  }

  // 如果有访问令牌，则添加到请求头
  const token = getAccessToken()
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const config = {
    ...options,
    headers
  }

  // 增加调试日志
  console.log('[fetchAPI 调试] URL:', url)
  console.log('[fetchAPI 调试] Headers:', headers)
  console.log('[fetchAPI 调试] Body:', options.body)
  
  try {
    const response = await fetch(url, config)

    // 检查响应状态
    if (!response.ok) {
      // 新增：若401/403自动登出跳转登录（仅非登录相关页面）
      if ((response.status === 401 || response.status === 403) && typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        if (typeof localStorage.removeUserInfo === 'function') {
          localStorage.removeUserInfo();
        }
        // 确保不是在登录/注册页，避免死循环
        const path = window.location.pathname
        if (!/\/login|\/register/.test(path)) {
          window.location.href = '/login';
        }
      }
      // 尝试解析错误响应
      let errorData
      try {
        errorData = await response.json()
      } catch (e) {
        errorData = { message: '请求失败，请稍后重试' }
      }

      throw new Error(errorData.message || `HTTP error! status: ${response.status}`)
    }

    // 对于204 No Content响应，不尝试解析JSON
    if (response.status === 204) {
      return null
    }

    // 解析JSON响应
    const data = await response.json()

    // 根据后端实际返回的状态码调整
    // 本项目后端统一返回格式: { code: 0, message: '', data: ... }
    // 兼容历史或其它实现也可能返回 HTTP-style code 200
    if (data.code !== 0 && data.code !== 200) {
      throw new Error(data.message || 'API返回错误')
    }

    return data.data
  } catch (error) {
    console.error('API请求错误:', error)
    throw error
  }
}

/**
 * GET请求
 */
export async function get(endpoint, params = {}) {
  // 构建查询字符串
  const queryString = Object.keys(params)
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(params[key])}`)
    .join('&')

  const separator = endpoint.includes('?') ? '&' : '?'
  const url = queryString ? `${endpoint}${separator}${queryString}` : endpoint

  return fetchAPI(url, {
    method: 'GET'
  })
}

/**
 * POST请求
 */
export async function post(endpoint, data = {}) {
  return fetchAPI(endpoint, {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

/**
 * PUT请求
 */
export async function put(endpoint, data = {}) {
  return fetchAPI(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data)
  })
}

/**
 * DELETE请求
 * @param {string} endpoint - API端点
 * @param {object} params - 查询参数
 */
export async function del(endpoint, queryParams = {}) {
  // 构建查询字符串（agentId和userId仍在queryString中）
  const queryString = Object.keys(queryParams)
    .map(key => `${encodeURIComponent(key)}=${encodeURIComponent(queryParams[key])}`)
    .join('&')
  
  const separator = endpoint.includes('?') ? '&' : '?'
  const url = queryString ? `${endpoint}${separator}${queryString}` : endpoint

  return fetchAPI(url, {
    method: 'DELETE'
  })
}
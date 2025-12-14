import { getAccessToken, post } from './http'

/**
 * 设置访问令牌到localStorage
 */
export function setAccessToken(token) {
  localStorage.setItem('access_token', token)
}

/**
 * 从localStorage移除访问令牌
 */
export function removeAccessToken() {
  localStorage.removeItem('access_token')
}

/**
 * 保存用户信息到localStorage
 */
export function saveUserInfo(userInfo) {
  localStorage.setItem('user', JSON.stringify(userInfo))
}

/**
 * 从localStorage获取用户信息
 */
export function getUserInfo() {
  const userStr = localStorage.getItem('user')
  return userStr ? JSON.parse(userStr) : null
}

/**
 * 从localStorage移除用户信息
 */
export function removeUserInfo() {
  localStorage.removeItem('user')
}

/**
 * 用户认证相关API
 */
export const authAPI = {
  /**
   * 检查用户是否已登录
   */
  isLoggedIn() {
    return !!localStorage.getItem('access_token')
  },

  /**
   * 用户登录
   */
  async login(username, password) {
    try {
      const response = await post('/user/login', {
        username,
        password
      })

      // 保存token和用户信息
      if (response && response.access_token) {
        await Promise.resolve(setAccessToken(response.access_token));
        // 保存用户信息（用户信息直接包含在response对象中）
        await Promise.resolve(saveUserInfo({
          id: response.id,
          username: response.username,
          nickname: response.nickname,
          email: response.email,
          avatar: response.avatar,
          lastLoginTime: response.lastLoginTime
        }));
      }

      return response
    } catch (error) {
      console.error('登录失败:', error)
      throw error
    }
  },

  /**
   * 用户注册
   */
  async register(username, password, email) {
    try {
      const response = await post('/user/register', {
        username,
        password,
        email
      })
      return response
    } catch (error) {
      console.error('注册失败:', error)
      throw error
    }
  },

  /**
   * 刷新令牌
   */
  async refreshToken() {
    try {
      const response = await post('/user/refresh')
      if (response && response.access_token) {
        setAccessToken(response.access_token)
      }
      return response
    } catch (error) {
      console.error('刷新令牌失败:', error)
      // 刷新令牌失败，清除本地存储的token
      removeAccessToken()
      removeUserInfo()
      throw error
    }
  },

  /**
   * 退出登录
   */
  async logout() {
    try {
      // 调用退出登录API
      await post('/user/logout')
    } catch (error) {
      console.error('退出登录API调用失败:', error)
      // 即使API调用失败，也要清除本地存储
    } finally {
      // 清除本地存储的token和用户信息
      removeAccessToken()
      removeUserInfo()
    }
  },

  /**
   * 检查是否已登录
   */
  isLoggedIn() {
    return getAccessToken() !== null
  },

  /**
   * 获取当前用户信息
   */
  getCurrentUser() {
    return getUserInfo()
  }
}
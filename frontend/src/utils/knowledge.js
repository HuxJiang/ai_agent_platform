// 导入必要的工具函数和请求方法
import { post } from './user.js'

/**
 * 知识库相关API
 */
export const knowledgeAPI = {
  /**
   * 导入原始文本
   */
  async ingestRaw(data) {
    try {
      const response = await post('/rag/ingest', data)
      return response
    } catch (error) {
      console.error('导入原始文本失败:', error)
      throw error
    }
  },
  
  /**
   * 从数据库同步
   */
  async syncDb(data) {
    try {
      const response = await post('/rag/sync-db', data)
      return response
    } catch (error) {
      console.error('从数据库同步失败:', error)
      throw error
    }
  },
  
  /**
   * 向量检索
   */
  async search(data) {
    try {
      const response = await post('/rag/search', data)
      return response
    } catch (error) {
      console.error('向量检索失败:', error)
      throw error
    }
  },
  
  /**
   * 混合检索
   */
  async hybridSearch(data) {
    try {
      const response = await post('/rag/hybrid-search', data)
      return response
    } catch (error) {
      console.error('混合检索失败:', error)
      throw error
    }
  },
  
  /**
   * 根据标题删除
   */
  async deleteByTitle(title) {
    try {
      const response = await post('/rag/delete-by-title', { title })
      return response
    } catch (error) {
      console.error('根据标题删除失败:', error)
      throw error
    }
  },
  
  /**
   * 根据类别删除
   */
  async deleteByCategory(category) {
    try {
      const response = await post('/rag/delete-by-category', { category })
      return response
    } catch (error) {
      console.error('根据类别删除失败:', error)
      throw error
    }
  }
}
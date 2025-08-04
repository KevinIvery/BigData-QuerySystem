// API工具函数 - JavaScript版本
export const useApi = () => {
  const config = useRuntimeConfig()
  
  // 通用API请求函数
  const request = async (path, options = {}) => {
    const { method = 'GET', body, query, headers = {} } = options
    
    // 构建完整URL
    const url = `${config.public.apiBase}${path.startsWith('/') ? path : `/${path}`}`
    
    // 默认headers
    const defaultHeaders = {
      'Content-Type': 'application/json',
      ...headers
    }
    
    try {
      // 使用$fetch，自动支持服务端渲染
      return await $fetch(url, {
        method,
        body,
        query,
        headers: defaultHeaders,
        // 服务端渲染支持
        server: true
      })
    } catch (error) {
      // 直接抛出错误，让组件自己处理
      throw error
    }
  }
  
  // 返回简洁的API对象
  return {
    // 基础HTTP方法
    get: (path, query) => request(path, { method: 'GET', query }),
    post: (path, body) => request(path, { method: 'POST', body }),
    put: (path, body) => request(path, { method: 'PUT', body }),
    delete: (path) => request(path, { method: 'DELETE' }),
    patch: (path, body) => request(path, { method: 'PATCH', body }),
    
    // 通用请求方法（支持自定义所有参数）
    request
  }
} 
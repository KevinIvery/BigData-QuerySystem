export default defineNuxtRouteMiddleware(async (to, from) => {
  // 只在客户端执行认证检查
  if (process.server) {
    return
  }
  
  const api = useApi()
  const { $ui } = useNuxtApp()
  
  try {
    // 调用后端认证检查接口
    const response = await api.post('/admin/auth-check/')
    
    // 如果认证失败，跳转到登录页
    if (response.code !== 0) {
      console.warn('认证检查返回非零状态码:', response.code)
      $ui.error('请重新登录', '登录状态已失效')
      return navigateTo('/a8f2c9e7d4b6f1a5c3e8d9f2b7a4c6e1/login')
    }
    
    // 认证成功，记录用户信息到会话状态
    if (response.data) {
      console.log('用户认证成功:', response.data.username)
    }
    
  } catch (error) {
    console.error('认证检查失败:', error)
    
    // 根据错误状态码处理
    const statusCode = error?.response?.status
    const errorCode = error?.response?.data?.code
    
    if (statusCode === 401 || errorCode === 401) {
      // 未登录或登录过期
      console.log('用户未登录或登录已过期')
      $ui.warning('请先登录', '您还未登录或登录已过期')
    } else if (statusCode === 403 || errorCode === 403) {
      // 权限不足
      console.log('用户权限不足')
      $ui.error('权限不足', '您没有访问此页面的权限')
    } else {
      // 其他错误（网络错误、服务器错误等）
      console.log('认证检查网络或服务器错误:', error.message)
      $ui.error('认证失败', '网络错误，请稍后重试')
    }
    
    // 跳转到登录页
    return navigateTo('/a8f2c9e7d4b6f1a5c3e8d9f2b7a4c6e1/login')
  }
}) 
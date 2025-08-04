export default defineNuxtRouteMiddleware(async (to, from) => {
  const api = useApi()
  
  try {
    // 检查代理认证状态
    const response = await api.post('/agent/auth-check/')
    
    if (response.code !== 0) {
      // 认证失败，重定向到登录页
      return navigateTo('/agent/login')
    }
    
    // 认证成功，继续访问
  } catch (error) {
    console.error('代理认证检查失败:', error)
    // 网络错误或其他异常，重定向到登录页
    return navigateTo('/agent/login')
  }
}) 
export default defineNuxtRouteMiddleware(async (to, from) => {
  // 只在客户端执行认证检查
  if (process.server) {
    return
  }
  
  const api = useApi()
  
  try {
    // 调用后端认证检查接口
    const response = await api.post('/admin/auth-check/')
    
    // 如果认证成功，说明用户已登录，重定向到后台首页
    if (response.code === 0) {
      console.log('用户已登录，重定向到后台首页')
      return navigateTo('/a8f2c9e7d4b6f1a5c3e8d9f2b7a4c6e1/')
    }
    
  } catch (error) {
    // 认证失败或错误，允许访问登录页面
    console.log('用户未登录，允许访问登录页面')
    // 不做任何处理，允许继续访问登录页
  }
}) 
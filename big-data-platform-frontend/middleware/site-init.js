export default defineNuxtRouteMiddleware(async (to, from) => {
  // 在服务端渲染时跳过，所有逻辑在客户端执行
  if (process.server) return;

  const AGENT_TAG_KEY = 'agent_tag';
  // 代理标签识别逻辑：支持 ?agent=xxx 和 ?xxx 两种形式
  const urlAgentTag = to.query.agent || to.query[AGENT_TAG_KEY] || Object.keys(to.query).find(key => to.query[key] === '' && key !== AGENT_TAG_KEY);
  
  const cookie = useCookie(AGENT_TAG_KEY, { maxAge: 60 * 60 * 24 * 30 });

  // 1. 代理标识处理 - 始终以URL中的为准
  console.log(`[Site-Init] URL参数:`, to.query);
  console.log(`[Site-Init] 检测到的代理标识: ${urlAgentTag}`);
  console.log(`[Site-Init] 当前Cookie中的代理标识: ${cookie.value}`);
  
  if (urlAgentTag) {
    if (cookie.value !== urlAgentTag) {
      cookie.value = urlAgentTag;
      console.log(`[Site-Init] 代理标识已通过URL设置/更新为: ${urlAgentTag}`);
    } else {
      console.log(`[Site-Init] 代理标识无变化，保持为: ${urlAgentTag}`);
    }
  } else {
    console.log(`[Site-Init] URL中无代理标识，当前Cookie保持为: ${cookie.value}`);
  }
  // 注意：我们不再清除cookie，让它持久化，除非被新的URL参数覆盖

  // 2. 站点状态检查 (只在首次进入网站时执行)
  if (!from.name) {
    try {
      const api = useApi();
      const response = await api.get('/frontend/status/');
      const status = response.data;
      
      console.log('站点状态检查报告:', status);

      // 检查是否需要强制微信访问
      const isWeChat = /micromessenger/i.test(navigator.userAgent);
      if (status.wechat_access_required && !isWeChat) {
          console.warn('站点要求在微信内访问。');
          return navigateTo({ path: '/maintenance', query: { reason: 'wechat_only' }});
      }

      // 检查核心配置是否完整
      if (!status.ready) {
        console.warn('站点配置不完整，将重定向到维护页面。');
        const reason = status.reason || 'config_incomplete';
        const missing = status.missing ? status.missing.join(',') : '';
        return navigateTo({ path: '/maintenance', query: { reason, missing }});
      }

    } catch (error) {
      console.error('站点状态检查失败:', error);
      return navigateTo({ path: '/maintenance', query: { reason: 'server_error' }});
    }
  }
}); 
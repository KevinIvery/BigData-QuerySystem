import { reactive } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useApi } from './useApi';

// 1. 全局、可共享的认证状态
const loginState = reactive({
  isLoggedIn: false,
  isLoading: true,
  user: null,
  error: null,
});

/**
 * 统一的认证管理 Composable
 */
export const useAuth = () => {
  const router = useRouter();
  const route = useRoute();
  const api = useApi();

  // 2. 检查环境
  const isWechatBrowser = process.client 
    ? /micromessenger/i.test(navigator.userAgent)
    : false;
  
  /**
   * 使用code向后端请求登录
   * @param {string} code 微信返回的授权码
   */
  const loginWithWechatCode = async (code) => {
    console.log('【Auth】--- 5. 开始使用code向后端发起登录请求...');
    try {
      // 调用后端的微信登录接口
      const result = await api.post('/frontend/login/wechat/', { code });
      
      if (result && result.success) {
        loginState.isLoggedIn = true;
        loginState.user = result.userInfo;
        console.log('【Auth】--- ✅ 微信登录成功:', result.userInfo);
        
        // 清理URL中的code和state参数，防止刷新时重复使用
        const cleanUrl = new URL(window.location.href);
        cleanUrl.searchParams.delete('code');
        cleanUrl.searchParams.delete('state');
        window.history.replaceState({}, document.title, cleanUrl.href);
        
      } else {
        // 如果后端返回失败，记录错误但不再跳转
        throw new Error(result?.message || '后端微信登录验证失败');
      }
    } catch (error) {
      console.error('【Auth】--- ❌ loginWithWechatCode 失败:', error.message);
      // 静默失败，后续依赖LoginPrompt提示
      loginState.error = '微信自动登录失败，请稍后重试或手动登录。';
    }
  };

  /**
   * 重定向到微信授权页面 (snsapi_base)
   * @param {string} appId - 公众号的AppID
   */
  const redirectToWechatAuth = (appId) => {
    if (!process.client) return;
    
    // 获取当前URL（不含hash）作为回调地址
    const redirectUri = encodeURIComponent(window.location.href.split('#')[0]);
    const authUrl = `https://open.weixin.qq.com/connect/oauth2/authorize?appid=${appId}&redirect_uri=${redirectUri}&response_type=code&scope=snsapi_base&state=STATE#wechat_redirect`;
    
    console.log('【Auth】--- 5. 重定向到微信授权页面...');
    console.log(`【Auth】  -> URL: ${authUrl}`);
    window.location.href = authUrl; // 执行跳转
  };


  /**
   * 核心认证流程初始化
   * @param {object} siteConfig - 从后端获取的站点配置，包含 { appid: '...' }
   */
  const initAuth = async (siteConfig = {}) => {
    console.log('【Auth】--- 1. 初始化认证流程 ---');
    loginState.isLoading = true;

    try {
      // 2. 优先检查后端会话
      console.log('【Auth】--- 2. 检查后端Session...');
      const session = await api.get('/frontend/auth-check/');
      if (session.code === 0 && session.data.id) {
        loginState.isLoggedIn = true;
        loginState.user = session.data;
        loginState.isLoading = false;
        console.log('【Auth】--- ✅ Session有效，用户已登录:', loginState.user);
        return; // 用户已登录，流程结束
      }
      console.log('【Auth】--- ❌ Session无效或未登录。');

      // 3. 如果未登录，根据环境决定下一步
      if (!isWechatBrowser) {
        console.log('【Auth】--- 3. 当前在普通浏览器，跳过自动登录。');
        loginState.isLoading = false;
        return; // 在普通浏览器中，等待用户手动操作
      }

      // --- 仅在微信浏览器中执行 ---
      console.log('【Auth】--- 3. 当前在微信浏览器内。');

      const code = route.query.code;
      const appId = siteConfig?.appid;

      // 4. 处理微信回调或发起授权
      if (code) {
        console.log('【Auth】--- 4. 检测到URL中有code，准备用code登录:', code);
        await loginWithWechatCode(code);
      } else {
        console.log('【Auth】--- 4. 未检测到code，准备重定向到微信授权。');
        if (!appId) {
            console.error('【Auth】--- ❌ 错误：缺少AppID，无法重定向！');
            loginState.error = '微信登录未配置';
            return;
        }
        redirectToWechatAuth(appId);
      }

    } catch (error) {
      console.error('【Auth】--- 认证流程发生严重错误:', error);
      loginState.error = '认证时发生错误';
    } finally {
      loginState.isLoading = false;
      console.log('【Auth】--- 认证流程结束，isLoading:', loginState.isLoading);
    }
  };

  /**
   * 登出
   */
  const logout = async () => {
    console.log('【Auth】--- 用户请求登出 ---');
    try {
      await api.post('/frontend/logout/');
      loginState.isLoggedIn = false;
      loginState.user = null;
      console.log('【Auth】--- 登出成功，已清理前端状态。');
    } catch (error) {
      console.error('【Auth】--- 登出时发生错误:', error);
    }
  };

  return {
    loginState,
    isWechatBrowser,
    initAuth,
    logout
  };
}; 
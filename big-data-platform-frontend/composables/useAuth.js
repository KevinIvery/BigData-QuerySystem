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
  console.log('【Auth】--- 检查环境');
  console.log('【Auth】--- navigator.userAgent:', navigator.userAgent);
  // 2. 检查环境
  const isWechatBrowser = process.client 
    ? /micromessenger/i.test(navigator.userAgent)
    : false;
  
  const isAlipayBrowser = process.client 
    ? /alipay/i.test(navigator.userAgent) || 
      /aliapp/i.test(navigator.userAgent) ||
      /AlipayClient/i.test(navigator.userAgent) ||
      /AlipayApp/i.test(navigator.userAgent) ||
      /AliApp/i.test(navigator.userAgent)
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
   * 使用auth_code向后端请求支付宝登录
   * @param {string} auth_code 支付宝返回的授权码
   */
  const loginWithAlipayCode = async (auth_code) => {
    console.log('【Auth】--- 5. 开始使用auth_code向后端发起支付宝登录请求...');
    console.log('【Auth】--- auth_code:', auth_code);
    
    try {
      // 调用后端的支付宝登录接口
      const result = await api.post('/frontend/login/alipay/', { auth_code });
      console.log('【Auth】--- 后端返回结果:', result);
      
      if (result && result.success) {
        loginState.isLoggedIn = true;
        loginState.user = result.userInfo;
        loginState.error = null; // 清除之前的错误
        console.log('【Auth】--- ✅ 支付宝登录成功:', result.userInfo);
        
        // 清理URL中的auth_code参数，防止刷新时重复使用
        const cleanUrl = new URL(window.location.href);
        cleanUrl.searchParams.delete('auth_code');
        window.history.replaceState({}, document.title, cleanUrl.href);
        
      } else {
        // 如果后端返回失败，记录错误但不再跳转
        const errorMsg = result?.message || '后端支付宝登录验证失败';
        console.error('【Auth】--- ❌ 后端登录失败:', errorMsg);
        throw new Error(errorMsg);
      }
    } catch (error) {
      console.error('【Auth】--- ❌ loginWithAlipayCode 失败:', error.message);
      // 静默失败，后续依赖LoginPrompt提示
      loginState.error = '支付宝自动登录失败，请稍后重试或手动登录。';
      throw error; // 重新抛出错误，让调用者知道失败了
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
   * 在支付宝环境中调用JSAPI获取授权码（静默授权）
   * @param {string} appId - 支付宝应用的AppID
   */
  const getAlipayAuthCode = (appId) => {
    if (!process.client) return;
    
    // 检查是否在支付宝环境中
    if (typeof ap === 'undefined') {
      console.error('【Auth】--- ❌ 当前不在支付宝环境中，无法调用ap.getAuthCode');
      console.log('【Auth】--- 提示：请确保在支付宝生活号或H5环境中访问');
      return;
    }
    
    console.log('【Auth】--- 5. 调用支付宝JSAPI获取授权码（静默授权）...');
    console.log('【Auth】--- 当前页面地址:', window.location.href);
    
    // 设置加载状态
    loginState.isLoading = true;
    console.log('【Auth】--- 设置加载状态: isLoading = true');
    
    // 调用支付宝JSAPI - 静默授权，无需用户确认
    ap.getAuthCode({
      appId: appId,
      scopes: ['auth_base'],
    }, function(res) {
      console.log('【Auth】--- ✅ 支付宝JSAPI回调被调用:', res);
      
      try {
        if (res.authCode) {
          console.log('【Auth】--- ✅ 获取到支付宝授权码:', res.authCode);
          
          // 发送到后端进行验证
          loginWithAlipayCode(res.authCode).then(() => {
            console.log('【Auth】--- ✅ 支付宝登录流程完成');
          }).catch((error) => {
            console.error('【Auth】--- ❌ 支付宝登录失败:', error);
          }).finally(() => {
            // 结束加载状态
            loginState.isLoading = false;
            console.log('【Auth】--- 结束加载状态: isLoading = false');
          });
          
        } else {
          console.error('【Auth】--- ❌ 获取支付宝授权码失败:', res.errorMessage);
          loginState.error = '支付宝授权失败，请重试';
          loginState.isLoading = false;
          console.log('【Auth】--- 结束加载状态: isLoading = false');
        }
      } catch (error) {
        console.error('【Auth】--- ❌ 处理支付宝授权码时发生错误:', error);
        loginState.error = '支付宝登录失败，请重试';
        loginState.isLoading = false;
        console.log('【Auth】--- 结束加载状态: isLoading = false');
      }
    });
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
      if (isAlipayBrowser) {
        // --- 在支付宝环境中执行 ---
        console.log('【Auth】--- 3. 当前在支付宝环境内。');

        const auth_code = route.query.auth_code;
        const alipayAppId = siteConfig?.alipay_appid;

        // 4. 处理支付宝回调或发起授权
        if (auth_code) {
          console.log('【Auth】--- 4. 检测到URL中有auth_code，准备用auth_code登录:', auth_code);
          await loginWithAlipayCode(auth_code);
        } else {
          console.log('【Auth】--- 4. 未检测到auth_code，准备调用支付宝JSAPI。');
          if (!alipayAppId) {
              console.error('【Auth】--- ❌ 错误：缺少支付宝AppID，无法调用JSAPI！');
              loginState.error = '支付宝登录未配置';
              return;
          }
          getAlipayAuthCode(alipayAppId);
        }
      } else if (isWechatBrowser) {
        // --- 在微信浏览器中执行 ---
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
      } else {
        console.log('【Auth】--- 3. 当前在普通浏览器，跳过自动登录。');
        loginState.isLoading = false;
        return; // 在普通浏览器中，等待用户手动操作
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
    isAlipayBrowser,
    initAuth,
    logout
  };
}; 
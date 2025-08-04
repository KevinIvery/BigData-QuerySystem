<template>
  <div class="relative font-sans antialiased text-gray-800 bg-slate-50 min-h-screen">
    <!-- Animated SVG Background -->

    <!-- Main Content -->
    <main class="relative z-10 pb-20">
      <!-- 根据activeTab显示不同内容 -->
      <FrontendHome 
        v-if="activeTab === 'home'"
        :site-data="siteData"
        :is-loading="isLoading"
        :login-state="loginState"
        @show-login-prompt="showLoginPrompt = true"
      />
      <FrontendProfile 
        v-if="activeTab === 'profile'"
        :site-data="siteData"
        :is-loading="isLoading"
        :login-state="loginState"
        @navigate-to-query="activeTab = 'home'"
        @logout="logout"
      />
    </main>

    <!-- 登录提示模态框 -->
    <LoginPrompt 
      :show="showLoginPrompt" 
      @login="handleLogin" 
      @close="showLoginPrompt = false" 
    />

    <!-- 投诉/客服悬浮按钮 -->
    <div v-if="siteData.system_config?.customer_service_url" class="fixed bottom-24 right-4 z-40">
      <button 
        @click="openCustomerService"
        class="group relative bg-gradient-to-r from-blue-400 to-blue-500 hover:from-blue-500 hover:to-blue-600 text-white rounded-lg px-3 py-2 shadow-md hover:shadow-lg transition-all duration-300 transform hover:scale-105 flex items-center space-x-1.5"
        title="投诉建议"
      >
        <!-- 图标 -->
        <Icon name="ph:megaphone-bold" class="w-4 h-4" />
        
        <!-- 文字 -->
        <span class="text-xs font-medium">投诉</span>
        
        <!-- 背景光晕效果 -->
        <div class="absolute inset-0 rounded-lg bg-blue-300 opacity-15 animate-pulse"></div>
        
        <!-- 边框发光效果 -->
        <div class="absolute inset-0 rounded-lg ring-1 ring-blue-200 opacity-0 group-hover:opacity-50 transition-opacity duration-300"></div>
      </button>
    </div>

    <!-- 底部菜单栏 - 固定定位 -->
    <footer class="fixed bottom-0 left-0 right-0 z-50">
      <!-- 立体背景层 -->
      <div class="absolute inset-0 bg-gradient-to-t from-blue-50/90 via-white/95 to-white/95 backdrop-blur-md border-t border-blue-200/60 shadow-xl">
        <!-- 顶部装饰线条 -->
        <div class="absolute top-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-blue-400 to-transparent opacity-50"></div>
        
        <!-- 底部装饰线条 -->
        <div class="absolute bottom-0 left-0 w-full h-0.5 bg-gradient-to-r from-transparent via-blue-300 to-transparent opacity-30"></div>
      </div>
      
      <!-- 菜单导航 -->
      <nav class="relative z-10 flex justify-around items-center h-20 max-w-md mx-auto">
        <button 
          v-for="item in menuItems" 
          :key="item.key"
          @click="handleMenuClick(item.key)"
          :class="[
            'flex flex-col items-center justify-center w-full h-full transition-colors duration-200 focus:outline-none',
            activeTab === item.key ? 'text-blue-600' : 'text-gray-500 hover:text-blue-500'
          ]"
        >
          <Icon :name="item.icon" class="w-6 h-6 mb-1" />
          <span class="text-xs font-medium">{{ item.name }}</span>
        </button>
      </nav>
    </footer>
  </div>
</template>

<style>
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); } 
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}
.animation-delay-2000 { animation-delay: 2s; }
.animation-delay-4000 { animation-delay: 4s; }

.animate-blob {
  animation: blob 7s infinite;
}
</style> 
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '~/composables/useAuth' // <-- 1. 替换为新的useAuth
import LoginPrompt from '~/components/LoginPrompt.vue'
import FrontendHome from '~/components/frontend/Home.vue'
import FrontendProfile from '~/components/frontend/Profile.vue'

definePageMeta({
  middleware: 'site-init'
})

// 状态管理
const activeTab = ref('home')
const siteData = ref({
  system_config: {},
  query_configs: [],
  agent_info: null
})
const isLoading = ref(true) // 这个isLoading是站点数据的加载状态
const api = useApi()
const router = useRouter()

// 登录相关状态
const { loginState, initAuth, logout } = useAuth() // <-- 2. 从新的useAuth获取
const showLoginPrompt = ref(false)
let promptTimer = null

// 菜单项配置
const menuItems = [
  { key: 'home', name: '首页', icon: 'ph:house-bold' },
  { key: 'profile', name: '我的', icon: 'ph:user-bold' }
]

// 菜单点击处理
const handleMenuClick = (key) => {
  // 3. 在切换到“我的”页面前，检查登录状态
  if (key === 'profile' && !loginState.isLoggedIn) {
    console.log('【Index】用户未登录，点击了“我的”，弹出登录提示。');
    showLoginPrompt.value = true;
  } else {
    activeTab.value = key;
  }
}

// “立即登录”按钮的处理
const handleLogin = () => {
  console.log('【Index】用户点击了“立即登录”，准备跳转到/login页面。');
  showLoginPrompt.value = false;
  router.push('/login');
}

// 打开客服链接
const openCustomerService = () => {
  const customerServiceUrl = siteData.value.system_config?.customer_service_url;
  if (customerServiceUrl) {
    console.log('【Index】打开客服链接:', customerServiceUrl);
    window.open(customerServiceUrl, '_blank');
  }
}

// 启动数据获取和认证流程
onMounted(async () => {
  console.log('【Index】--- 页面挂载，开始初始化流程 ---');
  

  // 监听支付状态（支付宝环境）
  if (process.client && typeof ap !== 'undefined') {
    // 监听来自支付窗口的消息
    window.addEventListener('message', (event) => {
      if (event.data && event.data.type === 'payment_started') {
        console.log('【Index】收到支付开始消息:', event.data)
        // 开始轮询支付状态
        startPaymentStatusPolling(event.data.order_no)
      }
    })
  }
  
  isLoading.value = true;
  try {
    // 4. 先获取站点数据
    console.log('【Index】1. 获取站点数据...');
    const response = await api.get('/frontend/data/');
    if (response.code === 0) {
      siteData.value = response.data;
      console.log('【Index】✅ 站点数据加载成功:', siteData.value);

      // 5. 然后用获取到的配置启动认证流程
      console.log('【Index】2. 调用initAuth启动认证...');
      console.log('【Index】siteData.value.system_config:', siteData.value.system_config);
      console.log('【Index】alipay_appid:', siteData.value.system_config?.alipay_appid);
      await initAuth(siteData.value.system_config);
    } else {
      console.error('【Index】❌ 获取站点数据失败:', response.message);
    }
  } catch (error) {
    console.error('【Index】❌ 初始化流程发生严重错误:', error);
  } finally {
    isLoading.value = false;
    console.log('【Index】--- 初始化流程结束 ---');
  }

  // 6. 如果认证流程跑完后，用户仍未登录，则2秒后提示
  if (!loginState.isLoggedIn) {
    promptTimer = setTimeout(() => {
      // 仅在首页时自动弹出
      if (activeTab.value === 'home') {
        console.log('【Index】用户长时间未登录，自动弹出登录提示。');
        showLoginPrompt.value = true;
      }
    }, 2000);
  }
});

// 支付状态轮询
let paymentPollingTimer = null

// 全局支付状态检查函数
const checkPaymentStatus = async (orderNo) => {
  try {
    console.log('【Index】检查支付状态:', orderNo)
    const response = await api.get(`/frontend/query-result/${orderNo}/`)
    
    if (response.code === 0) {
      const orderData = response.data
      
      // 如果支付成功，跳转到结果页
      if (orderData.status === 'paid' || orderData.status === 'querying' || orderData.status === 'completed') {
        console.log('【Index】支付成功，跳转到结果页')
        stopPaymentStatusPolling()
        
        // 跳转到结果页
        router.push(`/query-result/${orderNo}`)
        return true
      }
    }
    return false
  } catch (error) {
    console.error('【Index】检查支付状态失败:', error)
    return false
  }
}

const startPaymentStatusPolling = (orderNo) => {
  console.log('【Index】开始轮询支付状态:', orderNo)
  
  // 清除之前的轮询
  if (paymentPollingTimer) {
    clearInterval(paymentPollingTimer)
  }
  
  // 开始轮询
  paymentPollingTimer = setInterval(async () => {
    await checkPaymentStatus(orderNo)
  }, 3000) // 每3秒检查一次
  
  // 10分钟后停止轮询
  setTimeout(() => {
    if (paymentPollingTimer) {
      console.log('【Index】支付状态轮询超时，停止轮询')
      stopPaymentStatusPolling()
    }
  }, 10 * 60 * 1000)
}

const stopPaymentStatusPolling = () => {
  if (paymentPollingTimer) {
    clearInterval(paymentPollingTimer)
    paymentPollingTimer = null
  }
}

// 暴露给子组件使用
provide('checkPaymentStatus', checkPaymentStatus)
provide('startPaymentStatusPolling', startPaymentStatusPolling)

// 监听登录状态变化
watch(loginState, (newState) => {
  // 如果用户在提示框弹出前登录成功，则取消定时器
  if (newState.isLoggedIn && promptTimer) {
    clearTimeout(promptTimer);
    promptTimer = null;
  }
  // 如果用户在“我的”页面登出，则切换回首页
  if (!newState.isLoggedIn && activeTab.value === 'profile') {
    activeTab.value = 'home';
  }
}, { deep: true });

// SEO和页面标题
useHead({
  title: computed(() => siteData.value.system_config?.site_title || '大数据查询平台'),
  meta: [
    { name: 'description', content: computed(() => siteData.value.system_config?.description || '一站式大数据查询服务平台') },
    { name: 'keywords', content: computed(() => siteData.value.system_config?.keywords || '大数据, 查询, 风险, 监控') }
  ],
  bodyAttrs: {
    class: 'bg-slate-50'
  }
})
</script> 
<template>
  <!-- 主容器 - 白蓝色科技感背景 -->
  <div class="relative min-h-screen bg-gradient-to-br from-blue-50 via-white to-blue-100 flex flex-col items-center justify-center p-4 overflow-hidden">
    
    <!-- 动态背景层1: 蓝色科技网格 -->
    <div class="absolute inset-0 opacity-30">
      <svg class="w-full h-full" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <pattern id="tech-grid" x="0" y="0" width="80" height="80" patternUnits="userSpaceOnUse">
            <path d="M 80 0 L 0 0 0 80" fill="none" stroke="#3b82f6" stroke-width="0.5" opacity="0.4"/>
            <circle cx="40" cy="40" r="1.5" fill="#2563eb" opacity="0.8">
              <animate attributeName="opacity" values="0.8;1;0.8" dur="4s" repeatCount="indefinite"/>
            </circle>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#tech-grid)"/>
      </svg>
    </div>

    <!-- 动态背景层2: 白色浮动元素 -->
    <div class="absolute inset-0 overflow-hidden">
      <div class="absolute top-1/4 left-1/4 w-40 h-40 bg-white/60 rounded-full blur-3xl animate-pulse"></div>
      <div class="absolute top-3/4 right-1/4 w-32 h-32 bg-blue-200/40 rounded-full blur-2xl animate-pulse animation-delay-1000"></div>
      <div class="absolute bottom-1/4 left-1/3 w-24 h-24 bg-white/80 rounded-full blur-2xl animate-pulse animation-delay-2000"></div>
    </div>

    <!-- 动态背景层3: 蓝色数据流线条 -->
    <div class="absolute inset-0 opacity-20">
      <svg class="w-full h-full" xmlns="http://www.w3.org/2000/svg">
        <defs>
          <linearGradient id="flow-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:0"/>
            <stop offset="50%" style="stop-color:#2563eb;stop-opacity:1"/>
            <stop offset="100%" style="stop-color:#3b82f6;stop-opacity:0"/>
          </linearGradient>
        </defs>
        <line x1="0" y1="25%" x2="100%" y2="25%" stroke="url(#flow-gradient)" stroke-width="1">
          <animate attributeName="opacity" values="0;1;0" dur="6s" repeatCount="indefinite"/>
        </line>
        <line x1="0" y1="75%" x2="100%" y2="75%" stroke="url(#flow-gradient)" stroke-width="1">
          <animate attributeName="opacity" values="0;1;0" dur="6s" begin="3s" repeatCount="indefinite"/>
        </line>
      </svg>
    </div>

    <!-- 返回按钮 -->
    <div class="absolute top-6 left-6 z-30">
      <button @click="$router.back()" class="flex items-center space-x-2 text-blue-600 hover:text-blue-800 transition-all duration-300 bg-white/80 backdrop-blur-md px-4 py-2 rounded-lg border border-blue-200 hover:border-blue-300 hover:bg-white/90 shadow-lg hover:shadow-xl">
        <Icon name="ph:arrow-left-bold" class="w-5 h-5" />
        <span>返回</span>
      </button>
    </div>

    <!-- 主登录卡片 -->
    <div class="w-full max-w-md bg-white/90 backdrop-blur-xl rounded-2xl shadow-2xl p-8 border border-blue-200/50 z-20 relative overflow-hidden">
      
      <!-- 卡片内部蓝色光效 -->
      <div class="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-transparent to-blue-100/30 rounded-2xl"></div>
      
      <!-- Logo和标题区域 -->
      <div class="text-center mb-8 relative z-10">
        <div class="w-20 h-20 mx-auto mb-4 relative">
          <img v-if="logoUrl" :src="logoUrl" :alt="siteData.system_config?.site_title || 'Logo'" class="w-full h-full object-contain rounded-xl shadow-lg bg-white p-2" />
          <div v-else class="w-full h-full bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg">
            <Icon name="ph:database-duotone" class="w-12 h-12 text-white" />
          </div>
          <!-- Logo周围的蓝色光环效果 -->
          <div class="absolute inset-0 bg-blue-500/20 rounded-xl blur-lg animate-pulse"></div>
        </div>
        <h1 class="text-2xl font-bold text-gray-800 mb-2">{{ siteData.system_config?.site_title || '大数据查询平台' }}</h1>
        <p class="text-blue-600 text-sm">{{ siteData.system_config?.description || '智能数据分析与查询服务' }}</p>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm relative z-10">
        <div class="flex items-center space-x-2">
          <Icon name="ph:warning-circle" class="w-4 h-4" />
          <span>{{ error }}</span>
        </div>
      </div>

      <!-- 成功提示 -->
      <div v-if="success" class="mb-4 p-3 bg-green-50 border border-green-200 rounded-lg text-green-600 text-sm relative z-10">
        <div class="flex items-center space-x-2">
          <Icon name="ph:check-circle" class="w-4 h-4" />
          <span>{{ success }}</span>
        </div>
      </div>

      <!-- 登录表单 -->
      <form @submit.prevent="handleLogin" class="space-y-6 relative z-10">
        <!-- 手机号输入框 -->
        <div class="relative">
          <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Icon name="ph:phone" class="w-5 h-5 text-blue-500" />
          </div>
          <input 
            type="tel" 
            v-model="phone" 
            id="phone" 
            placeholder="请输入手机号码" 
            class="w-full pl-10 pr-4 py-3 bg-white/80 border border-blue-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 text-gray-800 placeholder-gray-500 backdrop-blur-sm shadow-sm"
            :disabled="isLoading"
            required
          >
        </div>

        <!-- 验证码输入框 -->
        <div class="flex items-center space-x-3">
          <div class="relative flex-1">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Icon name="ph:shield-check" class="w-5 h-5 text-blue-500" />
            </div>
            <input 
              type="text" 
              v-model="code" 
              placeholder="请输入验证码" 
              class="w-full pl-10 pr-4 py-3 bg-white/80 border border-blue-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-300 text-gray-800 placeholder-gray-500 backdrop-blur-sm shadow-sm"
              :disabled="isLoading"
              maxlength="6"
              required 
            >
          </div>
          <button 
            type="button" 
            @click="sendCode" 
            :disabled="isCounting || isLoading || !phone" 
            class="px-6 py-3 whitespace-nowrap rounded-xl font-semibold transition-all duration-300 border backdrop-blur-sm shadow-sm relative"
            :class="(isCounting || isLoading || !phone)
              ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed' 
              : 'bg-blue-50 text-blue-600 border-blue-200 hover:bg-blue-100 hover:text-blue-700 hover:border-blue-300 hover:shadow-md'"
          >
            <span v-if="isSendingCode" class="flex items-center space-x-1">
              <Icon name="ph:spinner" class="w-4 h-4 animate-spin" />
              <span>发送中</span>
            </span>
            <span v-else>{{ countdownText }}</span>
          </button>
        </div>

        <!-- 协议勾选 -->
        <div class="flex items-start space-x-3 pt-2">
          <input 
            type="checkbox" 
            v-model="agreementsAccepted" 
            id="login-agreements" 
            class="h-4 w-4 mt-0.5 rounded border-blue-300 bg-white text-blue-600 focus:ring-blue-500 focus:ring-offset-0 flex-shrink-0"
            :disabled="isLoading"
          >
          <label for="login-agreements" class="text-xs text-gray-600 leading-relaxed">
            我已阅读并同意
            <a @click.prevent="viewAgreement(UserAgreement)" class="text-blue-600 hover:text-blue-800 hover:underline cursor-pointer transition-colors">《用户服务协议》</a>、
            <a @click.prevent="viewAgreement(PrivacyPolicy)" class="text-blue-600 hover:text-blue-800 hover:underline cursor-pointer transition-colors">《隐私政策》</a>
          </label>
        </div>

        <!-- 登录按钮 -->
        <button 
          type="submit" 
          :disabled="!agreementsAccepted || isLoading || !phone || !code" 
          class="w-full py-3 px-6 rounded-xl font-bold text-lg tracking-wider transition-all duration-300 shadow-lg hover:shadow-xl relative overflow-hidden group"
          :class="(agreementsAccepted && !isLoading && phone && code)
            ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white hover:from-blue-600 hover:to-blue-700 transform hover:scale-105 hover:shadow-blue-200/50' 
            : 'bg-gray-200 text-gray-400 cursor-not-allowed'"
        >
          <span v-if="isLoading" class="flex items-center justify-center space-x-2">
            <Icon name="ph:spinner" class="w-5 h-5 animate-spin" />
            <span>登录中...</span>
          </span>
          <span v-else class="relative z-10">登录 / 注册</span>
          <div v-if="agreementsAccepted && !isLoading" class="absolute inset-0 bg-gradient-to-r from-blue-400 to-blue-500 opacity-0 group-hover:opacity-30 transition-opacity duration-300"></div>
        </button>
      </form>

      <!-- 科技装饰线条 -->
      <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-500 to-transparent"></div>
      <div class="absolute bottom-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-blue-400 to-transparent"></div>
    </div>
    
    <!-- 页脚版权信息 -->
    <footer v-if="siteData.system_config?.footer_copyright" class="absolute bottom-6 left-0 right-0 z-10 px-4">
      <div v-html="siteData.system_config.footer_copyright" class="text-sm text-gray-600 text-center bg-white/60 backdrop-blur-sm rounded-lg px-4 py-2 shadow-sm border border-blue-100"></div>
    </footer>

    <!-- 科技感装饰元素 -->
    <div class="absolute top-10 right-10 w-32 h-32 opacity-30">
      <svg viewBox="0 0 100 100" class="w-full h-full">
        <circle cx="50" cy="50" r="45" fill="none" stroke="#3b82f6" stroke-width="1" opacity="0.4">
          <animate attributeName="r" values="45;48;45" dur="3s" repeatCount="indefinite"/>
        </circle>
        <circle cx="50" cy="50" r="35" fill="none" stroke="#2563eb" stroke-width="1" opacity="0.6">
          <animate attributeName="r" values="35;32;35" dur="3s" repeatCount="indefinite"/>
        </circle>
        <circle cx="50" cy="50" r="3" fill="#2563eb" opacity="0.8">
          <animate attributeName="opacity" values="0.8;1;0.8" dur="2s" repeatCount="indefinite"/>
        </circle>
      </svg>
    </div>

    <!-- 左下角装饰 -->
    <div class="absolute bottom-10 left-10 w-24 h-24 opacity-20">
      <svg viewBox="0 0 100 100" class="w-full h-full">
        <rect x="10" y="10" width="80" height="80" fill="none" stroke="#3b82f6" stroke-width="2" opacity="0.5">
          <animate attributeName="stroke-width" values="2;3;2" dur="4s" repeatCount="indefinite"/>
        </rect>
        <rect x="25" y="25" width="50" height="50" fill="none" stroke="#2563eb" stroke-width="1" opacity="0.7">
          <animate attributeName="opacity" values="0.7;1;0.7" dur="2s" repeatCount="indefinite"/>
        </rect>
      </svg>
    </div>
  </div>

  <!-- 协议查看弹窗 -->
  <div v-if="isAgreementViewerVisible" class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
    <div class="bg-white/95 backdrop-blur-xl shadow-2xl w-full max-w-4xl max-h-[80vh] flex flex-col relative rounded-2xl border border-blue-200">
      <button @click="closeAgreementViewer" class="absolute top-4 right-4 text-gray-500 hover:text-gray-700 z-10 p-2 rounded-full bg-blue-50 hover:bg-blue-100 transition-all duration-200">
        <Icon name="ph:x-bold" class="w-5 h-5" />
      </button>
      <main class="flex-1 overflow-y-auto px-8 pt-8 pb-8 text-sm text-gray-700 agreement-content">
        <component :is="activeAgreementComponent" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '~/composables/useApi'
import UserAgreement from '~/components/agreements/UserAgreement.vue'
import PrivacyPolicy from '~/components/agreements/PrivacyPolicy.vue'

definePageMeta({ layout: false })

const phone = ref('')
const code = ref('')
const error = ref('')
const success = ref('')
const isCounting = ref(false)
const countdown = ref(60)
const isLoading = ref(false)
const isSendingCode = ref(false)

const siteData = ref({ system_config: {} })
const agreementsAccepted = ref(false)
const isAgreementViewerVisible = ref(false)
const activeAgreementComponent = ref(null)

const api = useApi()
const router = useRouter()
const config = useRuntimeConfig()

// Logo URL
const logoUrl = computed(() => {
  const logo = siteData.value.system_config?.logo
  if (!logo) return ''
  return logo.startsWith('http') ? logo : (config.public.fileUrl || '') + logo
})

// Countdown text
const countdownText = computed(() => isCounting.value ? `${countdown.value}s` : '获取验证码')

// 清除提示信息
const clearMessages = () => {
  error.value = ''
  success.value = ''
}

// 显示错误信息
const showError = (message) => {
  error.value = message
  success.value = ''
  setTimeout(() => {
    error.value = ''
  }, 5000)
}

// 显示成功信息
const showSuccess = (message) => {
  success.value = message
  error.value = ''
  setTimeout(() => {
    success.value = ''
  }, 3000)
}

// 获取站点配置数据
onMounted(async () => {
  try {
    console.log('🚀 [Login Page] 开始获取站点配置...')
    const response = await api.get('/frontend/data/')
    console.log('📡 [Login Page] API响应:', response)
    
    if (response.code === 0) {
      siteData.value = response.data
      console.log('✅ [Login Page] 站点配置加载成功:', {
        system_config: siteData.value.system_config,
        has_footer_copyright: !!siteData.value.system_config?.footer_copyright,
        footer_copyright: siteData.value.system_config?.footer_copyright
      })
    } else {
      console.error('❌ [Login Page] API返回错误:', response)
    }
  } catch (e) {
    console.error('💥 [Login Page] 获取站点配置失败:', e)
  }
})

// 协议查看相关
const viewAgreement = (component) => {
  activeAgreementComponent.value = component
  isAgreementViewerVisible.value = true
}

const closeAgreementViewer = () => {
  isAgreementViewerVisible.value = false
  activeAgreementComponent.value = null
}

// 发送验证码
const sendCode = async () => {
  if (!phone.value) {
    showError('请先输入手机号码')
    return
  }

  if (!/^1[3-9]\d{9}$/.test(phone.value)) {
    showError('请输入正确的手机号码')
    return
  }

  if (isCounting.value || isSendingCode.value) {
    return
  }

  try {
    clearMessages()
    isSendingCode.value = true
    
    console.log('📱 [Login Page] 准备发送验证码到:', phone.value)
    
    const response = await api.post('/frontend/send-sms-code/', {
      phone: phone.value
    })
    
    console.log('📱 [Login Page] 发送验证码响应:', response)
    
    if (response.code === 0) {
      // 开始倒计时
      startCountdown()
      showSuccess(response.message || '验证码发送成功')
    } else {
      showError(response.message || '验证码发送失败')
    }
  } catch (e) {
    console.error('💥 [Login Page] 发送验证码失败:', e)
    showError('验证码发送失败，请稍后重试')
  } finally {
    isSendingCode.value = false
  }
}

// 开始倒计时
const startCountdown = () => {
  isCounting.value = true
  countdown.value = 60
  
  const timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
      isCounting.value = false
      countdown.value = 60
    }
  }, 1000)
}

// 处理登录
const handleLogin = async () => {
  if (!agreementsAccepted.value) {
    showError('请先阅读并同意用户协议和隐私政策')
    return
  }

  if (!phone.value) {
    showError('请输入手机号码')
    return
  }

  if (!/^1[3-9]\d{9}$/.test(phone.value)) {
    showError('请输入正确的手机号码')
    return
  }

  if (!code.value) {
    showError('请输入验证码')
    return
  }

  if (code.value.length !== 6) {
    showError('请输入6位验证码')
    return
  }

  try {
    clearMessages()
    isLoading.value = true
    
    console.log('🔐 [Login Page] 准备登录:', { phone: phone.value, code: code.value })
    
    const response = await api.post('/frontend/login/sms/', {
      phone: phone.value,
      code: code.value
    })
    
    console.log('🔐 [Login Page] 登录响应:', response)
    
    if (response.code === 0) {
      console.log('✅ [Login Page] 登录成功:', response.data)
      
      // 显示成功消息
      showSuccess(response.message || '登录成功')
      
      // 保存用户信息到localStorage (可选)
      if (response.data) {
        localStorage.setItem('userInfo', JSON.stringify(response.data))
      }
      
      // 延迟跳转，让用户看到成功提示
      setTimeout(async () => {
        // 跳转到首页或者用户来源页面
        const redirectTo = router.currentRoute.value.query.redirect || '/'
        await router.push(redirectTo)
      }, 100)
      
    } else {
      showError(response.message || '登录失败')
    }
  } catch (e) {
    console.error('💥 [Login Page] 登录失败:', e)
    showError('登录失败，请稍后重试')
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* 动画延迟类 */
.animation-delay-1000 { animation-delay: 1s; }
.animation-delay-2000 { animation-delay: 2s; }

/* 协议内容滚动条样式 */
.agreement-content::-webkit-scrollbar { width: 8px; }
.agreement-content::-webkit-scrollbar-thumb { 
  background: linear-gradient(to bottom, #3b82f6, #2563eb); 
  border-radius: 4px; 
}
.agreement-content::-webkit-scrollbar-track { 
  background: #f1f5f9; 
  border-radius: 4px; 
}

/* 输入框focus时的蓝色发光效果 */
input:focus {
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1), 0 0 20px rgba(59, 130, 246, 0.15);
}

/* 按钮悬停时的蓝色发光效果 */
button:not(:disabled):hover {
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.2);
}

/* 科技感脉冲动画 */
@keyframes tech-pulse {
  0%, 100% { opacity: 0.8; transform: scale(1); }
  50% { opacity: 1; transform: scale(1.02); }
}

.tech-pulse {
  animation: tech-pulse 3s ease-in-out infinite;
}

/* 页脚版权信息的特殊样式 */
footer {
  backdrop-filter: blur(10px);
}
</style> 
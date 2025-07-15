<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="max-w-md w-full space-y-8">
      <!-- Logo和标题 -->
      <div class="text-center">
        <div class="mx-auto h-16 w-16 bg-indigo-600 rounded-xl flex items-center justify-center">
          <svg class="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
          </svg>
        </div>
        <h2 class="mt-6 text-3xl font-bold text-gray-900">
          代理管理后台
        </h2>
        <p class="mt-2 text-sm text-gray-600">
          请登录您的代理账户
        </p>
      </div>

      <!-- 登录表单 -->
      <div class="bg-white rounded-2xl shadow-xl p-8">
        <form @submit.prevent="handleLogin" class="space-y-6">
          <div>
            <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
              用户名
            </label>
            <div class="relative">
              <input
                id="username"
                v-model="loginForm.username"
                type="text"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                placeholder="请输入用户名"
              >
              <div class="absolute inset-y-0 right-0 pr-3 flex items-center">
                <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
              </div>
            </div>
          </div>

          <div>
            <label for="password" class="block text-sm font-medium text-gray-700 mb-2">
              密码
            </label>
            <div class="relative">
              <input
                id="password"
                v-model="loginForm.password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                placeholder="请输入密码"
              >
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <svg v-if="!showPassword" class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                </svg>
                <svg v-else class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- 验证码 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              安全验证
            </label>
            <TextCaptcha 
              ref="captchaRef"
              @success="handleCaptchaSuccess"
              @fail="handleCaptchaFail"
              @update:token="captchaToken = $event"
              @update:fingerprint="fingerprint = $event"
            />
          </div>

          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <input
                id="remember"
                v-model="loginForm.remember"
                type="checkbox"
                class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              >
              <label for="remember" class="ml-2 block text-sm text-gray-700">
                记住我
              </label>
            </div>
            <div class="text-sm">
              <a href="#" class="font-medium text-indigo-600 hover:text-indigo-500">
                忘记密码？
              </a>
            </div>
          </div>

          <button
            type="submit"
            :disabled="loading"
            class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ loading ? '登录中...' : '登录' }}
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
// 页面元信息
definePageMeta({
  layout: false,
  auth: false,
  middleware: 'guest' // 如果已登录则重定向到代理后台首页
})

const { $ui } = useNuxtApp()
const api = useApi()

// 登录表单数据
const loginForm = ref({
  username: '',
  password: '',
  remember: false
})

const showPassword = ref(false)
const loading = ref(false)

// 验证码相关
const captchaRef = ref(null)
const captchaToken = ref('')
const fingerprint = ref('')

// 验证码成功回调
const handleCaptchaSuccess = (token) => {
  captchaToken.value = token
  console.log('验证码验证成功:', token)
}

// 验证码失败回调
const handleCaptchaFail = (error) => {
  console.error('验证码验证失败:', error)
}

// 处理登录
const handleLogin = async () => {
  try {
    loading.value = true
    
    // 检查验证码是否完成
    if (!captchaRef.value?.isVerified) {
      $ui.warning('请先完成安全验证')
      return
    }
    
    if (!captchaToken.value) {
      $ui.warning('验证码token无效，请重新验证')
      return
    }
    
    // 调用代理登录API
    const result = await api.post('/agent/login/', {
      username: loginForm.value.username,
      password: loginForm.value.password,
      captcha_token: captchaToken.value,
      fingerprint: fingerprint.value,
      remember: loginForm.value.remember
    })
    
    if (result.code === 0) {
      $ui.success('登录成功！', '欢迎回来')
      
      // 将用户信息存储到sessionStorage中，供其他页面使用
      if (result.data) {
        sessionStorage.setItem('agent_user_info', JSON.stringify(result.data))
        console.log('代理用户信息已存储:', result.data)
      }
      
      // 跳转到代理后台首页
      await navigateTo('/agent/')
    } else {
      $ui.error('登录失败', result.message)
    }

  } catch (error) {
    console.error('登录失败:', error)
    $ui.error('登录失败', error.message)
  } finally {
    loading.value = false
  }
}

// 页面标题
useHead({
  title: '代理登录 - 大数据查询平台'
})
</script> 
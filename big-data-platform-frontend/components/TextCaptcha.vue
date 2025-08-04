<template>
  <div class="text-captcha">
    <!-- 验证按钮 -->
    <button 
      v-if="!isVisible && !verified"
      type="button" 
      @click="getCaptcha"
      class="w-full flex items-center text-blue-600 justify-center p-3 bg-gray-50 border border-gray-200 rounded-lg hover:bg-gray-100 transition-all"
    >
      <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zM21 5a2 2 0 00-2-2h-4a2 2 0 00-2 2v12a4 4 0 004 4h4a4 4 0 004-4V5z"/>
      </svg>
      <span class="text-sm">点击进行身份验证</span>
    </button>
    
    <!-- 验证成功展示 -->
    <button 
      v-else-if="verified"
      type="button" 
      class="w-full flex items-center justify-center p-3 bg-green-50 border border-green-200 rounded-lg text-green-600"
    >
      <svg class="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
      </svg>
      <span>验证通过</span>
    </button>
    
    <!-- 验证码弹窗 -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition duration-300 ease-out"
        enter-from-class="opacity-0"
        enter-to-class="opacity-100"
        leave-active-class="transition duration-200 ease-in"
        leave-from-class="opacity-100"
        leave-to-class="opacity-0"
      >
        <div v-if="isVisible" class="fixed inset-0 flex items-center justify-center z-50">
          <div class="absolute inset-0 bg-black bg-opacity-50" @click="closeModal"></div>
          <div class="relative bg-white rounded-xl shadow-2xl w-full max-w-md p-6 mx-4">
            <div class="flex justify-between items-center mb-4">
              <h3 class="text-lg font-semibold text-gray-900">文字验证</h3>
              <button 
                @click="closeModal"
                class="text-gray-500 hover:text-gray-700"
              >
                <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
                </svg>
              </button>
            </div>
            
            <div class="mb-6">
              <p class="text-sm text-gray-600 mb-4" v-if="prompt">{{ prompt }}</p>
              
              <!-- 错误提示 -->
              <div 
                v-if="errorMsg" 
                class="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded-lg mb-4 text-sm flex items-start"
              >
                <svg class="h-5 w-5 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"/>
                </svg>
                <div>{{ errorMsg }}</div>
              </div>
              
              <!-- 验证码图片区域 -->
              <div 
                v-if="bgImage" 
                class="relative overflow-hidden rounded-lg mb-3"
                ref="captchaImage"
              >
                <img 
                  :src="bgImage" 
                  class="w-full h-auto" 
                  @load="onImageLoad"
                  ref="captchaImageElement"
                  alt="验证码图片"
                  @mousemove="handleMouseMove"
                  @click="handleImageClick"
                />
                
                <!-- 点击标记 -->
                <div 
                  v-for="(click, index) in clicks" 
                  :key="index"
                  class="absolute w-6 h-6 -ml-3 -mt-3 bg-blue-600 rounded-full flex items-center justify-center text-white text-xs"
                  :style="{ left: `${click.displayX}px`, top: `${click.displayY}px` }"
                >
                  {{ index + 1 }}
                </div>
                
                <!-- 加载中遮罩 -->
                <div 
                  v-if="loading"
                  class="absolute inset-0 bg-white bg-opacity-70 flex items-center justify-center"
                >
                  <div class="flex flex-col items-center">
                    <div class="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-2"></div>
                    <span class="text-sm text-gray-600">处理中...</span>
                  </div>
                </div>
              </div>
              
              <div class="flex justify-between items-center">
                <button 
                  type="button"
                  @click="resetClicks"
                  class="text-sm text-blue-600 hover:underline"
                  :disabled="loading || clicks.length === 0"
                >
                  <svg class="h-4 w-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                  </svg>
                  重新点击
                </button>
                
                <button
                  type="button"
                  @click="refreshCaptcha"
                  class="text-sm text-blue-600 hover:underline"
                  :disabled="loading"
                >
                  <svg class="h-4 w-4 inline-block mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
                  </svg>
                  换一张图片
                </button>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
const emit = defineEmits(['success', 'fail', 'update:token', 'update:fingerprint'])

const api = useApi()

// 状态变量
const isVisible = ref(false)
const verified = ref(false)
const loading = ref(false)
const token = ref('')
const bgImage = ref('')
const prompt = ref('')
const clicks = ref([])
const captchaImage = ref(null)
const captchaImageElement = ref(null)
const errorMsg = ref('') // 错误信息

// 图片信息
const imageLoaded = ref(false)
const originalWidth = ref(300)  // 默认后端生成图片宽度
const originalHeight = ref(150) // 默认后端生成图片高度

// 鼠标移动记录 - 用于创建更自然的点击模式
const mouseTrack = ref([])
const lastMouseMoveTime = ref(0)

// 获取指纹
const fingerprint = (() => {
  // 检查是否已有存储的指纹
  if (process.client) {
    try {
      const storedFingerprint = localStorage.getItem('captcha_fingerprint')
      if (storedFingerprint) {
        return storedFingerprint
      }
    } catch (e) {
      console.warn('无法访问localStorage:', e)
    }
    
    // 生成新指纹
    const screenInfo = `${window.screen.width}x${window.screen.height}x${window.screen.colorDepth}`
    const timeZone = new Date().getTimezoneOffset()
    const language = navigator.language || navigator.userLanguage || ''
    const platform = navigator.platform || ''
    
    // 生成稳定指纹，不使用时间戳
    const hashSource = `${screenInfo}|${timeZone}|${language}|${platform}`
    let hash = 0
    for (let i = 0; i < hashSource.length; i++) {
      hash = ((hash << 5) - hash) + hashSource.charCodeAt(i)
      hash |= 0 // 转为32位整数
    }
    
    const newFingerprint = hash.toString(16)
    try {
      localStorage.setItem('captcha_fingerprint', newFingerprint)
    } catch (e) {
      console.warn('无法保存到localStorage:', e)
    }
    return newFingerprint
  }
  return ''
})()

// 图片加载完成处理
const onImageLoad = () => {
  if (captchaImageElement.value) {
    // 获取图片原始尺寸
    originalWidth.value = captchaImageElement.value.naturalWidth || 300
    originalHeight.value = captchaImageElement.value.naturalHeight || 150
    imageLoaded.value = true
    console.log(`图片加载完成，原始尺寸: ${originalWidth.value}x${originalHeight.value}`)
  }
}

// 记录鼠标移动轨迹
const handleMouseMove = (event) => {
  // 限制记录频率，每50ms记录一次
  const now = Date.now()
  if (now - lastMouseMoveTime.value < 50) return
  lastMouseMoveTime.value = now
  
  if (!imageLoaded.value) return
  
  const rect = event.target.getBoundingClientRect()
  const x = Math.round(event.clientX - rect.left)
  const y = Math.round(event.clientY - rect.top)
  
  // 只记录最近20个点
  mouseTrack.value.push({ x, y, t: now })
  if (mouseTrack.value.length > 20) {
    mouseTrack.value.shift()
  }
}

// 组件挂载后通知父组件指纹值
onMounted(() => {
  if (fingerprint) {
    emit('update:fingerprint', fingerprint)
    console.log('组件挂载时已通知父组件指纹值')
  }
})

// 关闭验证码弹窗
const closeModal = () => {
  // 只有在未验证成功的情况下，关闭弹窗才重置状态
  if (!verified.value) {
    resetClicks()
  }
  isVisible.value = false
}

// 获取验证码
const getCaptcha = async () => {
  if (loading.value) return false
  
  try {
    loading.value = true
    resetClicks()
    imageLoaded.value = false
    mouseTrack.value = [] // 重置鼠标轨迹
    errorMsg.value = '' // 清除错误信息
    
    console.log('正在获取验证码，指纹:', fingerprint)
    
    const response = await api.post('/captcha/generate/', {
      fingerprint
    })
    
    // 检查响应状态码
    if (response && response.code === 0) {
      const result = response.data
      
      if (result && result.type === 'text') {
        token.value = result.token
        bgImage.value = result.bg_image
        prompt.value = result.prompt
        isVisible.value = true
        
        // 通知父组件
        emit('update:token', token.value)
        emit('update:fingerprint', fingerprint)
        
        console.log('验证码获取成功，token:', token.value.substring(0, 8) + '...')
        return true
      } else {
        console.error('验证码类型不正确:', result)
        errorMsg.value = '验证码类型不支持'
        emit('fail', { message: '验证码类型不支持' })
        return false
      }
    } else {
      // 服务器返回非零状态码
      console.error('获取验证码失败，服务器返回:', response)
      errorMsg.value = response?.message || '获取验证码失败'
      emit('fail', { message: errorMsg.value })
      return false
    }
  } catch (error) {
    console.error('获取验证码请求异常:', error)
    errorMsg.value = error?.message || '获取验证码失败，请刷新页面重试'
    emit('fail', error)
    return false
  } finally {
    loading.value = false
  }
}

// 刷新验证码
const refreshCaptcha = async () => {
  resetClicks()
  errorMsg.value = '' // 清除错误信息
  return await getCaptcha()
}

// 重置点击记录
const resetClicks = () => {
  clicks.value = []
  errorMsg.value = '' // 清除错误信息
}

// 添加自然性随机偏移
const addNaturalOffset = (x, y) => {
  // 人类点击通常不会精确命中中心，添加小范围随机偏移
  const offset = 5; // 最大偏移像素
  
  // 生成-offset到+offset之间的随机偏移
  const offsetX = Math.floor(Math.random() * (2 * offset + 1)) - offset;
  const offsetY = Math.floor(Math.random() * (2 * offset + 1)) - offset;
  
  return {
    x: x + offsetX,
    y: y + offsetY
  };
}

// 处理图片点击 - 修改为计算坐标映射
const handleImageClick = (event) => {
  if (loading.value || clicks.value.length >= 5 || !imageLoaded.value) return
  
  // 清除错误信息
  errorMsg.value = ''
  
  // 获取图片显示区域的位置和尺寸
  const rect = event.target.getBoundingClientRect()
  
  // 计算点击在显示元素上的坐标
  const displayX = Math.round(event.clientX - rect.left)
  const displayY = Math.round(event.clientY - rect.top)
  
  // 计算缩放比例
  const scaleX = originalWidth.value / rect.width
  const scaleY = originalHeight.value / rect.height
  
  // 应用缩放并添加自然随机偏移
  const { x: rawX, y: rawY } = addNaturalOffset(displayX, displayY)
  
  // 计算在原始图片上的坐标
  const x = Math.round(rawX * scaleX)
  const y = Math.round(rawY * scaleY)
  
  console.log(`点击坐标: 显示(${displayX},${displayY}), 实际(${x},${y}), 缩放比例(${scaleX.toFixed(2)},${scaleY.toFixed(2)})`)
  
  // 收集用户点击前的鼠标移动数据，这有助于验证真实用户
  const recentTracks = [...mouseTrack.value]
  
  // 记录点击位置和时间，同时为显示保存显示坐标
  clicks.value.push({
    x,  // 发送给服务器的实际坐标
    y,  // 发送给服务器的实际坐标
    displayX, // 用于前端显示的坐标
    displayY, // 用于前端显示的坐标
    t: Date.now(),
    // 额外可选：记录点击前的鼠标轨迹，后端如果需要可以分析
    // tracks: recentTracks
  })
  
  // 点击完成后验证
  if (clicks.value.length === 5) {
    setTimeout(() => {
      verifyCaptcha()
    }, 300)
  }
}

// 验证点击结果
const verifyCaptcha = async () => {
  if (loading.value || !token.value) return false
  
  try {
    loading.value = true
    errorMsg.value = '' // 清除错误信息
    
    // 只发送服务器需要的坐标数据
    const clicksData = clicks.value.map(click => ({
      x: click.x,
      y: click.y,
      t: click.t
    }))
    
    console.log('正在验证点击，token:', token.value.substring(0, 8) + '...', '点击数:', clicks.value.length)
    
    const response = await api.post('/captcha/verify/', {
      token: token.value,
      clicks: clicksData,
      fingerprint
    })
    
    // 检查响应状态码
    if (response && response.code === 0) {
      // 验证成功
      verified.value = true
      isVisible.value = false
      console.log('验证成功')
      
      // 通知父组件
      emit('success', token.value)
      return true
    } else {
      // 服务器返回非零状态码
      console.error('验证失败，服务器返回:', response)
      errorMsg.value = response?.message || '验证失败，请重试'
      
      // 延迟一段时间后自动刷新验证码
      setTimeout(() => {
        if (errorMsg.value) {
          console.log('自动刷新验证码')
          refreshCaptcha()
        }
      }, 1500)
      
      emit('fail', { message: errorMsg.value })
      return false
    }
  } catch (error) {
    console.error('验证请求异常:', error)
    
    // 处理错误信息
    const errorMessage = error?.response?.data?.message || error.message || '验证失败，请重试'
    errorMsg.value = errorMessage
    
    // 延迟一段时间后自动刷新验证码
    setTimeout(() => {
      if (errorMsg.value) {
        console.log('验证失败后自动刷新验证码')
        refreshCaptcha()
      }
    }, 1500)
    
    emit('fail', error)
    return false
  } finally {
    loading.value = false
  }
}

// 完全重置验证状态
const reset = () => {
  console.log('重置验证码状态')
  verified.value = false
  token.value = ''
  bgImage.value = ''
  prompt.value = ''
  errorMsg.value = ''
  isVisible.value = false
  resetClicks()
  imageLoaded.value = false
  mouseTrack.value = []
}

// 获取指纹值方法
const getFingerprint = () => {
  return fingerprint
}

// 获取验证状态
const isVerified = computed(() => verified.value)

// 获取验证码token
const captchaToken = computed(() => token.value)

// 对外暴露方法
defineExpose({
  getCaptcha,
  refreshCaptcha,
  reset,
  isVerified,
  captchaToken,
  getFingerprint
})
</script>

<style scoped>
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style> 
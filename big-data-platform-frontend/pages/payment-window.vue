<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 头部 -->
    <header class="bg-white shadow-sm border-b border-gray-200 px-4 py-3">
      <div class="flex items-center justify-between">
        <h1 class="text-lg font-semibold text-gray-800">支付确认</h1>
        <button @click="closeWindow" class="text-gray-400 hover:text-gray-600">
          <Icon name="ph:x-bold" class="w-5 h-5" />
        </button>
      </div>
    </header>

    <!-- 主要内容 -->
    <main class="flex-1 flex flex-col items-center justify-center px-4 py-8">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="text-center">
        <div class="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-gray-600">正在准备支付...</p>
      </div>

      <!-- 支付信息 -->
      <div v-else-if="orderData" class="w-full max-w-sm">
        <div class="bg-white rounded-lg shadow-lg p-6 mb-4">
          <div class="text-center mb-4">
            <div class="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-3">
              <Icon name="ph:credit-card-bold" class="w-6 h-6 text-white" />
            </div>
            <h2 class="text-lg font-semibold text-gray-800">风险查询报告</h2>
            <p class="text-sm text-gray-500">订单号: {{ orderData.order_no }}</p>
          </div>

          <div class="space-y-3">
            <div class="flex justify-between items-center">
              <span class="text-gray-600">查询类型</span>
              <span class="text-blue-600 font-medium">{{ getQueryTypeText() }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="text-gray-600">支付金额</span>
              <span class="text-lg font-bold text-red-500">¥{{ orderData.amount }}</span>
            </div>
          </div>
        </div>

        <!-- 支付方式选择 -->
        <div class="space-y-3 mb-4">
          <!-- 支付宝支付 -->
          <div 
            @click="selectedPaymentMethod = 'alipay'"
            :class="[
              'flex items-center p-3 border rounded-lg cursor-pointer transition-all duration-200',
              selectedPaymentMethod === 'alipay' 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-200 hover:border-gray-300'
            ]"
          >
            <div class="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center mr-3">
              <Icon name="ri:alipay-fill" class="w-4 h-4 text-white" />
            </div>
            <div class="flex-1">
              <h4 class="text-sm font-medium text-gray-800">支付宝支付</h4>
              <p class="text-xs text-gray-500">安全便捷</p>
            </div>
            <div class="flex items-center">
              <span class="text-lg font-bold text-gray-800 mr-2">¥{{ orderData.amount }}</span>
              <div v-if="selectedPaymentMethod === 'alipay'" class="text-blue-500">
                <Icon name="ri:check-fill" class="w-4 h-4" />
              </div>
            </div>
          </div>

          <!-- 微信支付 -->
          <div 
            v-if="isWeChat"
            @click="selectedPaymentMethod = 'wechat'"
            :class="[
              'flex items-center p-3 border rounded-lg cursor-pointer transition-all duration-200',
              selectedPaymentMethod === 'wechat' 
                ? 'border-green-500 bg-green-50' 
                : 'border-gray-200 hover:border-gray-300'
            ]"
          >
            <div class="w-8 h-8 bg-green-500 rounded-lg flex items-center justify-center mr-3">
              <Icon name="ri:wechat-pay-fill" class="w-4 h-4 text-white" />
            </div>
            <div class="flex-1">
              <h4 class="text-sm font-medium text-gray-800">微信支付</h4>
              <p class="text-xs text-gray-500">微信安全支付</p>
            </div>
            <div class="flex items-center">
              <span class="text-lg font-bold text-gray-800 mr-2">¥{{ orderData.amount }}</span>
              <div v-if="selectedPaymentMethod === 'wechat'" class="text-green-500">
                <Icon name="ri:check-fill" class="w-4 h-4" />
              </div>
            </div>
          </div>
        </div>

        <!-- 风险提示 -->
        <div class="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-700">
          <Icon name="ri:shield-check-line" class="w-3 h-3 inline mr-1" />
          支付后即可解锁完整风险报告
        </div>
      </div>

      <!-- 错误状态 -->
      <div v-else-if="error" class="text-center">
        <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Icon name="ph:warning-circle-bold" class="w-8 h-8 text-red-500" />
        </div>
        <h3 class="text-lg font-semibold text-gray-800 mb-2">加载失败</h3>
        <p class="text-gray-600 mb-4">{{ error }}</p>
        <button @click="retryLoad" class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
          重试
        </button>
      </div>
    </main>

    <!-- 底部按钮 -->
    <footer class="bg-white border-t border-gray-200 px-4 py-3">
      <button 
        @click="confirmPayment" 
        :disabled="!selectedPaymentMethod || isProcessing"
        class="w-full py-3 px-4 rounded-lg font-bold text-white transition-all duration-200 flex items-center justify-center bg-gradient-to-r from-red-500 to-pink-600 hover:from-red-600 hover:to-pink-700 shadow-lg hover:shadow-xl disabled:bg-gray-400 disabled:cursor-not-allowed disabled:shadow-none"
      >
        <div v-if="isProcessing" class="flex items-center justify-center">
          <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
          <span class="text-sm">处理中...</span>
        </div>
        <div v-else class="flex items-center justify-center">
          <Icon name="ri:lock-unlock-line" class="w-4 h-4 mr-2" />
          <span class="text-sm">解锁风险报告</span>
        </div>
      </button>
      
      <!-- 取消按钮 -->
      <button 
        @click="closeWindow" 
        class="w-full mt-2 py-2 text-xs text-gray-500 hover:text-gray-700 transition-colors"
      >
        取消
      </button>
    </footer>

    <!-- Toast 消息 -->
    <SimpleToast
      v-if="currentToast"
      :message="currentToast.message"
      :type="currentToast.type"
      :duration="currentToast.duration"
      @close="currentToast = null"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useApi } from '~/composables/useApi'
import SimpleToast from '~/components/frontend/SimpleToast.vue'

const route = useRoute()
const api = useApi()
const orderData = ref(null)
const isLoading = ref(true)
const isProcessing = ref(false)
const error = ref(null)
const selectedPaymentMethod = ref('')

// Toast 相关状态
const currentToast = ref(null)

// 检测微信环境
const isWeChat = computed(() => {
  if (process.client) {
    return /micromessenger/i.test(navigator.userAgent)
  }
  return false
})

// Toast 消息提示
const showToast = (message, type = 'info') => {
  console.log(`[PaymentWindow Toast] ${type}: ${message}`)
  
  currentToast.value = {
    message,
    type,
    duration: 3000
  }
}

// 获取查询类型文本
const getQueryTypeText = () => {
  if (!orderData.value?.query_type) return '未知'
  
  if (orderData.value.query_type.includes('个人')) {
    return '个人查询'
  } else if (orderData.value.query_type.includes('企业')) {
    return '企业查询'
  }
  
  return orderData.value.query_type
}

// 获取URL参数并构建订单数据
onMounted(async () => {

  
  try {
    const query = route.query
    const payUrl = query.pay_url
    const orderNo = query.order_no
    const amount = query.amount
    const queryType = query.query_type
    const queryData = query.query_data

    if (!orderNo) {
      throw new Error('缺少订单号')
    }

    // 构建订单数据
    orderData.value = {
      order_no: orderNo,
      amount: amount || '0.00',
      query_type: queryType,
      query_data: queryData ? JSON.parse(queryData) : {},
      pay_url: payUrl
    }

    console.log('【PaymentWindow】订单数据:', orderData.value)
    
    // 自动选择支付方式
    if (isWeChat.value) {
      selectedPaymentMethod.value = 'wechat'
    } else {
      selectedPaymentMethod.value = 'alipay'
    }
    
  } catch (err) {
    console.error('【PaymentWindow】加载订单数据失败:', err)
    error.value = err.message || '加载订单数据失败'
  } finally {
    isLoading.value = false
  }
})

// 重试加载
const retryLoad = () => {
  error.value = null
  isLoading.value = true
  onMounted()
}

// 确认支付
const confirmPayment = async () => {
  if (!selectedPaymentMethod.value || isProcessing.value) return
  
  isProcessing.value = true
  console.log('【PaymentWindow】用户选择支付方式:', selectedPaymentMethod.value)
  
  try {
    // 如果没有pay_url，需要先创建支付订单
    if (!orderData.value.pay_url) {
      console.log('【PaymentWindow】需要创建支付订单')
      
      const paymentData = {
        order_no: orderData.value.order_no,
        payment_method: selectedPaymentMethod.value
      }
      
      // 支付宝支付需要传递当前URL用于生成return_url
      if (selectedPaymentMethod.value === 'alipay') {
        paymentData.current_url = window.location.origin
        
        // 检测设备类型
        const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile/i.test(navigator.userAgent)
        paymentData.is_mobile = isMobile
        
        console.log('【PaymentWindow】支付宝支付，传递当前URL:', paymentData.current_url)
        console.log('【PaymentWindow】设备类型检测:', isMobile ? '移动设备' : 'PC设备')
      }
      
      const paymentResult = await api.post('/frontend/create-payment/', paymentData)
      
      // 参考Home.vue的处理方式，使用 response.code === 0 判断成功
      const paymentResponse = paymentResult.code === 0 
        ? { success: true, message: paymentResult.message, data: paymentResult.data }
        : { success: false, message: paymentResult.message || '创建支付订单失败' }
      
      if (!paymentResponse.success) {
        showToast(paymentResponse.message || '创建支付订单失败', 'error')
        return
      }
      
      orderData.value.pay_url = paymentResponse.data.pay_url
      console.log('【PaymentWindow】支付订单创建成功:', paymentResponse.data)
      showToast('支付订单创建成功', 'success')
    }
    
    // 跳转到支付页面
    if (selectedPaymentMethod.value === 'alipay' && orderData.value.pay_url) {
      console.log('【PaymentWindow】跳转到支付宝支付:', orderData.value.pay_url)
      showToast('正在跳转支付页面...', 'info')
      
      // 在跳转前，通知主窗口准备跳转到结果页
      if (process.client && typeof ap !== 'undefined') {
        // 在支付宝环境中，通知主窗口
        try {
          ap.postMessage({
            type: 'payment_started',
            order_no: orderData.value.order_no
          })
        } catch (e) {
          console.log('【PaymentWindow】无法发送消息到主窗口:', e)
        }
      }
      
      window.location.href = orderData.value.pay_url
    } else if (selectedPaymentMethod.value === 'wechat') {
      // 处理微信支付（如果需要）
      console.log('【PaymentWindow】微信支付暂未实现')
      showToast('微信支付功能暂未开放', 'warning')
    }
  } catch (error) {
    console.error('【PaymentWindow】支付流程异常:', error)
    showToast('支付流程异常，请重试', 'error')
  } finally {
    isProcessing.value = false
  }
}

// 关闭窗口
const closeWindow = () => {
  console.log('【PaymentWindow】用户取消支付，关闭窗口')
  
  if (process.client && typeof ap !== 'undefined') {
    // 在支付宝环境中，关闭当前窗口
    ap.closeWindow()
  } else {
    // 在外部浏览器中，返回上一页
    window.history.back()
  }
}

// 页面标题
useHead({
  title: '支付确认'
})
</script> 
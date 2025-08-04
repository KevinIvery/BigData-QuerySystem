<template>
  <div v-if="isVisible" class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
    <div class="bg-white shadow-2xl w-full max-w-xs flex flex-col relative rounded-xl overflow-hidden">
      <!-- 关闭按钮 -->
      <button @click="$emit('cancel')" class="absolute top-2 right-2 text-gray-400 hover:text-gray-600 z-10 p-1">
        <Icon name="ri:close-line" class="w-4 h-4" />
      </button>

      <!-- 头部 -->
      <div class="bg-gradient-to-r from-blue-500 to-indigo-600 p-4 text-white text-center">
        <div class="text-lg font-bold mb-1">
          风险查询报告
        </div>
        <p class="text-blue-100 text-xs">专业数据分析服务</p>
        
        <!-- 营销信息 -->
        <div class="mt-2 text-xs text-blue-100 opacity-90">
          <Icon name="ri:group-line" class="w-3 h-3 inline mr-1" />
          {{ queryCount }}人已查询
        </div>
      </div>

      <!-- 流程显示 -->
      <div class="px-4 py-3 bg-gray-50">
        <div class="flex items-center justify-between text-xs">
          <div class="flex items-center text-green-600">
            <Icon name="ri:check-fill" class="w-3 h-3 mr-1" />
            <span>输入信息</span>
          </div>
          <div class="flex-1 h-px bg-gray-300 mx-2"></div>
          <div class="flex items-center text-blue-600">
            <Icon name="ri:money-dollar-circle-fill" class="w-3 h-3 mr-1" />
            <span>支付</span>
          </div>
          <div class="flex-1 h-px bg-gray-300 mx-2"></div>
          <div class="flex items-center text-gray-400">
            <Icon name="ri:file-text-line" class="w-3 h-3 mr-1" />
            <span>查看报告</span>
          </div>
        </div>
      </div>

      <!-- 支付方式选择 -->
      <div class="p-4 flex-1">
        <!-- 支付宝支付 - 仅在非微信环境显示 -->
        <div 
          v-if="!isWeChat"
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
            <span class="text-lg font-bold text-gray-800 mr-2">¥{{ order?.amount || '0.00' }}</span>
            <div v-if="selectedPaymentMethod === 'alipay'" class="text-blue-500">
              <Icon name="ri:check-fill" class="w-4 h-4" />
            </div>
          </div>
        </div>

        <!-- 微信支付 - 仅在微信环境显示 -->
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
            <span class="text-lg font-bold text-gray-800 mr-2">¥{{ order?.amount || '0.00' }}</span>
            <div v-if="selectedPaymentMethod === 'wechat'" class="text-green-500">
              <Icon name="ri:check-fill" class="w-4 h-4" />
            </div>
          </div>
        </div>

        <!-- 风险提示 -->
        <div class="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-xs text-yellow-700">
          <Icon name="ri:shield-check-line" class="w-3 h-3 inline mr-1" />
          支付后即可解锁完整风险报告
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="p-4">
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
          @click="$emit('cancel')" 
          class="w-full mt-2 py-2 text-xs text-gray-500 hover:text-gray-700 transition-colors"
        >
          取消
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  isVisible: { type: Boolean, default: false },
  order: { type: Object, default: null }
})

const emit = defineEmits(['confirm', 'cancel'])

const selectedPaymentMethod = ref('')
const isProcessing = ref(false)

// 检测微信环境，自动选择支付方式
const isWeChat = computed(() => {
  if (process.client) {
    return /micromessenger/i.test(navigator.userAgent)
  }
  return false
})

// 营销数据：查询人数（模拟数据，实际应该从后端获取）
const queryCount = computed(() => {
  // 基于当前时间生成一个相对稳定的数字，让数字看起来更真实
  const baseCount = 12847
  const today = new Date()
  const dayOfYear = Math.floor((today - new Date(today.getFullYear(), 0, 0)) / (1000 * 60 * 60 * 24))
  const variation = Math.floor(Math.sin(dayOfYear * 0.1) * 500) + Math.floor(Math.random() * 100)
  return (baseCount + variation).toLocaleString()
})

// 监听模态框显示状态，自动选择支付方式
watch(() => props.isVisible, (visible) => {
  if (visible) {
    // 根据环境自动选择支付方式：微信环境使用微信支付，其他环境使用支付宝
    if (isWeChat.value) {
      selectedPaymentMethod.value = 'wechat'
    } else {
      selectedPaymentMethod.value = 'alipay'
    }
    isProcessing.value = false
  } else {
    selectedPaymentMethod.value = ''
    isProcessing.value = false
  }
})

const confirmPayment = () => {
  if (!selectedPaymentMethod.value || isProcessing.value) return
  
  isProcessing.value = true
  emit('confirm', selectedPaymentMethod.value)
  
  // 防止处理时间过长，5秒后重置状态
  setTimeout(() => {
    isProcessing.value = false
  }, 5000)
}
</script>

<style scoped>
/* 模态框动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}
</style> 
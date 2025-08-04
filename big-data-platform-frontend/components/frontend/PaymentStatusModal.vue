<template>
  <Transition name="modal">
    <div v-if="isVisible" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <!-- 背景遮罩 -->
      <div class="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-sm"></div>
      
      <!-- 弹窗内容 -->
      <div class="relative bg-white rounded-2xl shadow-2xl max-w-md w-full max-h-[90vh] overflow-y-auto">
        <!-- 头部 -->
        <div class="flex items-center justify-between p-6 border-b border-gray-100">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <Icon name="ph:question-bold" class="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900">支付状态确认</h3>
              <p class="text-sm text-gray-500">请确认您的支付状态</p>
            </div>
          </div>
          <button 
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <Icon name="ph:x-bold" class="w-5 h-5" />
          </button>
        </div>
        
        <!-- 订单信息 -->
        <div class="p-6">
          <div v-if="order" class="mb-6">
            <div class="bg-gray-50 rounded-lg p-4 mb-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-600">订单号</span>
                <span class="text-sm font-mono text-gray-900">{{ order.order_no }}</span>
              </div>
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium text-gray-600">查询类型</span>
                <span class="text-sm text-gray-900">{{ order.query_type }}</span>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-sm font-medium text-gray-600">订单金额</span>
                <span class="text-lg font-bold text-red-600">¥{{ order.amount }}</span>
              </div>
            </div>
            
            <div class="text-center mb-6">
              <p class="text-gray-700 mb-2">请确认您是否已完成支付？</p>
              <p class="text-sm text-gray-500">系统将自动检查您的支付状态</p>
            </div>
          </div>
          
          <!-- 按钮组 -->
          <div class="space-y-3">
            <!-- 已支付按钮 -->
            <button 
              @click="handlePaid"
              :disabled="isChecking"
              class="w-full py-3 px-4 rounded-lg font-bold text-white transition-all duration-200 flex items-center justify-center bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 shadow-lg hover:shadow-xl disabled:bg-gray-400 disabled:cursor-not-allowed disabled:shadow-none"
            >
              <div v-if="isChecking" class="flex items-center justify-center">
                <div class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
                <span class="text-sm">检查中...</span>
              </div>
              <div v-else class="flex items-center justify-center">
                <Icon name="ph:check-circle-bold" class="w-4 h-4 mr-2" />
                <span class="text-sm">我已支付</span>
              </div>
            </button>
            
            <!-- 未支付按钮 -->
            <button 
              @click="handleNotPaid"
              :disabled="props.isChecking"
              class="w-full py-3 px-4 rounded-lg font-bold text-gray-700 transition-all duration-200 flex items-center justify-center bg-gray-100 hover:bg-gray-200 shadow-lg hover:shadow-xl disabled:bg-gray-50 disabled:cursor-not-allowed disabled:shadow-none"
            >
              <Icon name="ph:x-circle-bold" class="w-4 h-4 mr-2" />
              <span class="text-sm">我未支付</span>
            </button>
          </div>
          
          <!-- 提示信息 -->
          <div class="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div class="flex items-start space-x-2">
              <Icon name="ph:info-bold" class="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" />
              <div class="text-sm text-blue-800">
                <p class="font-medium mb-1">温馨提示</p>
                <p>• 如果您已完成支付，请点击"我已支付"</p>
                <p>• 如果您还未支付，请点击"我未支付"</p>
                <p>• 系统会自动检查支付状态并跳转到结果页</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  isVisible: { type: Boolean, default: false },
  order: { type: Object, default: null },
  isChecking: { type: Boolean, default: false }
})

const emit = defineEmits(['close', 'check-status'])

// 处理已支付
const handlePaid = () => {
  if (props.isChecking) return
  
  // 触发父组件的检查支付状态方法
  emit('check-status')
}

// 处理未支付
const handleNotPaid = () => {
  emit('close')
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
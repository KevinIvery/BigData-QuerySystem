<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 p-4" @click.self="$emit('close')">
    <div class="w-full max-w-md bg-white rounded-2xl shadow-xl transform transition-all" 
      :class="isSubmitted ? 'scale-100' : 'scale-95 opacity-0 animate-scale-in'">
      
      <!-- Form View -->
      <div v-if="!isSubmitted" class="p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-bold text-gray-900">代理申请</h3>
          <button @click="$emit('close')" class="p-1 rounded-full text-gray-400 hover:bg-gray-100 hover:text-gray-600">
            <Icon name="ph:x-bold" class="w-5 h-5" />
          </button>
        </div>
        
        <!-- 错误提示 -->
        <div v-if="errorMessage" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-600">{{ errorMessage }}</p>
        </div>
        
        <form @submit.prevent="handleSubmit" class="space-y-4">
          <div>
            <label for="applicant-name" class="block text-sm font-medium text-gray-700 mb-1">您的姓名</label>
            <input v-model="form.name" type="text" id="applicant-name" placeholder="请输入真实姓名"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition" 
              required :disabled="isSubmitting">
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">联系方式</label>
            <div class="flex items-center space-x-4 mb-2">
              <div class="flex items-center">
                <input v-model="form.contactType" type="radio" id="contact-phone" value="phone" 
                  class="h-4 w-4 text-indigo-600 border-gray-300 focus:ring-indigo-500" :disabled="isSubmitting">
                <label for="contact-phone" class="ml-2 block text-sm text-gray-900">手机号</label>
              </div>
              <div class="flex items-center">
                <input v-model="form.contactType" type="radio" id="contact-wechat" value="wechat" 
                  class="h-4 w-4 text-indigo-600 border-gray-300 focus:ring-indigo-500" :disabled="isSubmitting">
                <label for="contact-wechat" class="ml-2 block text-sm text-gray-900">微信号</label>
              </div>
            </div>
            <input v-model="form.contact" 
              :type="form.contactType === 'phone' ? 'tel' : 'text'" 
              id="applicant-contact" 
              :placeholder="form.contactType === 'phone' ? '请输入手机号码' : '请输入微信号'"
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 transition" 
              required :disabled="isSubmitting">
          </div>
          <button type="submit" 
            :disabled="isSubmitting"
            class="w-full bg-indigo-600 text-white font-semibold py-3 rounded-lg hover:bg-indigo-700 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed">
            <span v-if="isSubmitting" class="flex items-center justify-center">
              <Icon name="ph:spinner-gap" class="w-5 h-5 animate-spin mr-2" />
              提交中...
            </span>
            <span v-else>提交申请</span>
          </button>
        </form>
      </div>

      <!-- Success View -->
      <div v-else class="p-8 text-center">
        <div class="w-16 h-16 mx-auto bg-green-100 rounded-full flex items-center justify-center">
          <Icon name="ph:check-circle-duotone" class="w-10 h-10 text-green-600" />
        </div>
        <h3 class="text-lg font-bold text-gray-900 mt-4">提交成功</h3>
        <p class="text-sm text-gray-600 mt-2">
          您的代理申请已成功提交！我们的工作人员将会尽快与您联系，请保持通讯畅通。
        </p>
        <button @click="$emit('close')"
          class="mt-6 w-full bg-gray-200 text-gray-800 font-semibold py-2.5 rounded-lg hover:bg-gray-300 transition-colors">
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const emit = defineEmits(['close'])
const api = useApi()

const isSubmitted = ref(false)
const isSubmitting = ref(false)
const errorMessage = ref('')

const form = ref({
  name: '',
  contact: '',
  contactType: 'phone' // 默认联系方式为手机号
})

const handleSubmit = async () => {
  try {
    isSubmitting.value = true
    errorMessage.value = ''
    
    console.log('【Agency Application】代理申请提交:', form.value)
    
    // 验证表单数据
    if (!form.value.name.trim()) {
      throw new Error('请输入姓名')
    }
    
    if (!form.value.contact.trim()) {
      throw new Error('请输入联系方式')
    }
    
    if (form.value.contactType === 'phone') {
      // 验证手机号格式
      const phoneRegex = /^1[3-9]\d{9}$/
      if (!phoneRegex.test(form.value.contact.trim())) {
        throw new Error('请输入正确的手机号码')
      }
    }
    
    // 准备提交数据
    const submitData = {
      applicant_name: form.value.name.trim(),
      contact_type: form.value.contactType,
      contact_info: form.value.contact.trim()
    }
    
    // 调用后端API
    const response = await api.post('/frontend/submit-agency-application/', submitData)
    
    console.log('【Agency Application】提交成功:', response)
    
    // 检查响应状态
    if (response.code === 0) {
      // 显示成功状态
      isSubmitted.value = true
    } else {
      throw new Error(response.message || '提交失败')
    }
    
  } catch (error) {
    console.error('【Agency Application】提交失败:', error)
    
    // 显示错误信息
    if (error.data && error.data.message) {
      errorMessage.value = error.data.message
    } else if (error.message) {
      errorMessage.value = error.message
    } else {
      errorMessage.value = '提交失败，请稍后重试'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
@keyframes scale-in {
  from {
    opacity: 0;
    transform: scale(0.95);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}
.animate-scale-in {
  animation: scale-in 0.3s ease-out forwards;
}
</style> 
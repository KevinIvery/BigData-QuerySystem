<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
    <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4 max-h-[90vh] overflow-y-auto">
      <!-- 弹窗头部 -->
      <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
        <h3 class="text-lg font-medium text-gray-900">收款配置</h3>
        <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600">
          <Icon name="clarity:close-line" class="w-6 h-6" />
        </button>
      </div>

      <!-- 弹窗内容 -->
      <form @submit.prevent="submitConfig" class="px-6 py-4 space-y-4">
        <!-- 支付方式选择 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">收款方式</label>
          <div class="grid grid-cols-2 gap-3">
            <label class="relative">
              <input
                type="radio"
                value="alipay"
                v-model="form.payment_method"
                class="sr-only"
              />
              <div
                :class="[
                  'border-2 rounded-lg p-3 cursor-pointer transition-all',
                  form.payment_method === 'alipay'
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                ]"
              >
                <div class="flex items-center justify-center">
                  <Icon name="simple-icons:alipay" class="w-8 h-8 text-blue-600" />
                </div>
                <div class="mt-2 text-center text-sm font-medium text-gray-900">
                  支付宝
                </div>
              </div>
            </label>
            
            <label class="relative">
              <input
                type="radio"
                value="wechat"
                v-model="form.payment_method"
                class="sr-only"
              />
              <div
                :class="[
                  'border-2 rounded-lg p-3 cursor-pointer transition-all',
                  form.payment_method === 'wechat'
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-gray-300'
                ]"
              >
                <div class="flex items-center justify-center">
                  <Icon name="simple-icons:wechat" class="w-8 h-8 text-green-600" />
                </div>
                <div class="mt-2 text-center text-sm font-medium text-gray-900">
                  微信支付
                </div>
              </div>
            </label>
          </div>
        </div>

        <!-- 收款账号 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">
            {{ form.payment_method === 'alipay' ? '支付宝账号' : '微信账号' }}
          </label>
          <input
            type="text"
            v-model="form.payment_account"
            :placeholder="getAccountPlaceholder()"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
          <p class="mt-1 text-xs text-gray-500">
            {{ getAccountHelperText() }}
          </p>
        </div>

        <!-- 收款人姓名 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">收款人姓名</label>
          <input
            type="text"
            v-model="form.payment_name"
            placeholder="请输入收款人真实姓名"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        <!-- 收款码图片（可选） -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">收款码图片（可选）</label>
          <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md hover:border-gray-400 transition-colors">
            <div class="space-y-1 text-center">
              <Icon name="clarity:cloud-upload-line" class="mx-auto h-12 w-12 text-gray-400" />
              <div class="flex text-sm text-gray-600">
                <label class="relative cursor-pointer bg-white rounded-md font-medium text-blue-600 hover:text-blue-500 focus-within:outline-none">
                  <span>上传收款码</span>
                  <input type="file" class="sr-only" accept="image/*" @change="handleFileUpload" />
                </label>
              </div>
              <p class="text-xs text-gray-500">PNG, JPG, GIF 最大 2MB</p>
            </div>
          </div>
          
          <!-- 图片预览 -->
          <div v-if="form.payment_qr_code" class="mt-3">
            <img :src="qrCodePreviewUrl" alt="收款码预览" class="h-32 w-32 object-cover rounded-md border mx-auto" />
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="flex justify-end space-x-3 pt-4">
          <button
            type="button"
            @click="$emit('close')"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            取消
          </button>
          <button
            type="submit"
            :disabled="loading || !isFormValid"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Icon v-if="loading" name="clarity:refresh-line" class="w-4 h-4 mr-2 animate-spin" />
            {{ loading ? '保存中...' : existingConfig ? '更新配置' : '保存配置' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
const emit = defineEmits(['close', 'saved'])
const { $ui } = useNuxtApp()
const api = useApi()
const config = useRuntimeConfig()

// 响应式数据
const loading = ref(false)
const existingConfig = ref(false)
const form = ref({
  payment_method: 'alipay',
  payment_account: '',
  payment_name: '',
  payment_qr_code: ''
})

// 计算属性
const isFormValid = computed(() => {
  return form.value.payment_method &&
         form.value.payment_account.trim() &&
         form.value.payment_name.trim()
})

const qrCodePreviewUrl = computed(() => {
  if (!form.value.payment_qr_code) return ''
  return (config.public.fileUrl || '') + form.value.payment_qr_code
})

// 获取账号输入框占位符
const getAccountPlaceholder = () => {
  if (form.value.payment_method === 'alipay') {
    return '请输入支付宝账号（手机号或邮箱）'
  } else {
    return '请输入微信号或手机号'
  }
}

// 获取账号帮助文本
const getAccountHelperText = () => {
  if (form.value.payment_method === 'alipay') {
    return '支持手机号或邮箱格式'
  } else {
    return '支持微信号或手机号格式'
  }
}

// 处理文件上传
const handleFileUpload = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 文件大小检查
  if (file.size > 2 * 1024 * 1024) {
    $ui.warning('图片大小不能超过2MB')
    return
  }

  // 文件类型检查
  if (!file.type.startsWith('image/')) {
    $ui.warning('只能上传图片文件')
    return
  }

  try {
    $ui.showLoading('正在上传图片...')

    const formData = new FormData()
    formData.append('file', file)

    // 直接使用fetch调用上传接口
    const response = await fetch('/api/upload/', {
      method: 'POST',
      credentials: 'include',
      body: formData
    })

    const result = await response.json()

    if (result.code === 0) {
      form.value.payment_qr_code = result.data.file_url
      $ui.success('图片上传成功')
    } else {
      $ui.error('上传失败', result.message)
    }
  } catch (error) {
    console.error('上传图片失败:', error)
    $ui.error('上传失败', '网络错误，请稍后重试')
  } finally {
    $ui.hideLoading()
  }
}

// 获取现有配置
const getExistingConfig = async () => {
  try {
    const response = await api.get('/agent/payment-config/')
    
    if (response.code === 0 && response.data.configured) {
      existingConfig.value = true
      form.value = {
        payment_method: response.data.payment_method,
        payment_account: response.data.payment_account,
        payment_name: response.data.payment_name,
        payment_qr_code: response.data.payment_qr_code || ''
      }
    }
  } catch (error) {
    console.error('获取收款配置失败:', error)
  }
}

// 提交配置
const submitConfig = async () => {
  if (!isFormValid.value) {
    $ui.warning('请填写完整的配置信息')
    return
  }

  // 表单验证
  const { payment_method, payment_account, payment_name } = form.value

  // 账号格式验证
  if (payment_method === 'alipay') {
    const phoneRegex = /^1[3-9]\d{9}$/
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
    if (!phoneRegex.test(payment_account) && !emailRegex.test(payment_account)) {
      $ui.warning('支付宝账号格式不正确，请输入手机号或邮箱')
      return
    }
  } else if (payment_method === 'wechat') {
    const phoneRegex = /^1[3-9]\d{9}$/
    const wechatRegex = /^[a-zA-Z0-9_-]{6,20}$/
    if (!phoneRegex.test(payment_account) && !wechatRegex.test(payment_account)) {
      $ui.warning('微信账号格式不正确，请输入微信号或手机号')
      return
    }
  }

  // 姓名验证
  const nameRegex = /^[\u4e00-\u9fa5a-zA-Z\s]+$/
  if (!nameRegex.test(payment_name)) {
    $ui.warning('收款人姓名只能包含中文、英文字母和空格')
    return
  }

  try {
    loading.value = true
    
    const response = await api.post('/agent/payment-config/save/', form.value)
    
    if (response.code === 0) {
      $ui.success(existingConfig.value ? '收款配置更新成功' : '收款配置保存成功')
      emit('saved', response.data)
    } else {
      $ui.error('保存失败', response.message)
    }
  } catch (error) {
    console.error('保存收款配置失败:', error)
    $ui.error('保存失败', '网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 组件挂载时获取现有配置
onMounted(() => {
  getExistingConfig()
})
</script>

<style scoped>
/* 自定义样式 */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}
</style> 
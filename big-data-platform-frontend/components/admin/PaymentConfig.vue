<template>
  <div class="max-w-4xl mx-auto">
    <!-- 页面标题 -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">支付配置</h1>
      <p class="mt-1 text-sm text-gray-600">管理支付宝和微信支付的接口凭证。</p>
    </div>

    <!-- 功能说明 -->
    <div class="mb-6 bg-blue-50 border-l-4 border-blue-400 p-4 text-xs leading-5 text-blue-800">
        <p><strong><Icon name="logos:alipay" class="inline-block mr-1"/>支付宝:</strong> 用于PC网站和外部浏览器支付。</p>
        <p><strong><Icon name="logos:wechat-pay" class="inline-block mr-1"/>微信支付:</strong> 用于微信生态内(如H5、公众号)支付。</p>
        <p>若系统设置中已开启“仅限微信内访问”，可不配置支付宝。</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-10">
      <Icon name="clarity:refresh-line" class="w-8 h-8 text-gray-400 animate-spin" />
      <p class="mt-2 text-sm text-gray-500">正在加载支付配置...</p>
    </div>

    <div v-else>
      <!-- Tab导航 -->
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex space-x-8" aria-label="Tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            @click="activeTab = tab.key"
            :class="[
              activeTab === tab.key
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm focus:outline-none'
            ]"
          >
            {{ tab.name }}
          </button>
        </nav>
      </div>

      <!-- Tab内容 -->
      <div class="mt-8">
        <form @submit.prevent="saveConfig">
          <div class="bg-white shadow rounded-lg p-6 space-y-6">
            <!-- 支付宝支付 -->
            <div v-if="activeTab === 'alipay_payment'">
               <h3 class="text-lg font-medium text-gray-900 mb-4">支付宝支付配置</h3>
               <div class="space-y-4">
                 <input v-model="forms.alipay_payment.config_name" type="text" placeholder="配置名称 (e.g., 支付宝当面付)" required class="w-full px-3 py-2 border rounded-md">
                 <input v-model="forms.alipay_payment.credentials.app_id" type="text" placeholder="App ID" required class="w-full px-3 py-2 border rounded-md">
                 <textarea v-model="forms.alipay_payment.credentials.app_private_key" :class="{ 'password-mask': !showSensitive }" rows="5" placeholder="应用私钥 (app_private_key)" required class="w-full px-3 py-2 border rounded-md font-mono text-sm"></textarea>
                 <textarea v-model="forms.alipay_payment.credentials.alipay_public_key" :class="{ 'password-mask': !showSensitive }" rows="5" placeholder="支付宝公钥 (alipay_public_key)" required class="w-full px-3 py-2 border rounded-md font-mono text-sm"></textarea>
                 <input v-model="forms.alipay_payment.credentials.notify_url" type="url" placeholder="支付回调域名 (例如: https://api.v2.tybigdata.com)" required class="w-full px-3 py-2 border rounded-md">
                 <p class="text-xs text-gray-500">回调路径将自动拼接为: <code class="bg-gray-100 p-1 rounded">/api/payment/alipay/notify/</code></p>
               </div>
            </div>

            <!-- 微信支付 -->
            <div v-if="activeTab === 'wechat_payment'">
               <h3 class="text-lg font-medium text-gray-900 mb-4">微信支付配置</h3>
               <div class="space-y-4">
                 <input v-model="forms.wechat_payment.config_name" type="text" placeholder="配置名称 (e.g., 微信JSAPI支付)" required class="w-full px-3 py-2 border rounded-md">
                 <input v-model="forms.wechat_payment.credentials.app_id" type="text" placeholder="AppID" required class="w-full px-3 py-2 border rounded-md">
                 <input v-model="forms.wechat_payment.credentials.mch_id" type="text" placeholder="商户号 (MchId)" required class="w-full px-3 py-2 border rounded-md">
                 <input v-model="forms.wechat_payment.credentials.api_v3_key" :type="showSensitive ? 'text' : 'password'" placeholder="API v3密钥" autocomplete="new-password" required class="w-full px-3 py-2 border rounded-md">
                 <textarea v-model="forms.wechat_payment.credentials.key_path" :class="{ 'password-mask': !showSensitive }" rows="5" placeholder="证书私钥内容 (apiclient_key.pem)" required class="w-full px-3 py-2 border rounded-md font-mono text-sm"></textarea>
                 <input v-model="forms.wechat_payment.credentials.serial_no" type="text" placeholder="商户证书序列号" required class="w-full px-3 py-2 border rounded-md">
                 <input v-model="forms.wechat_payment.credentials.notify_url" type="url" placeholder="支付回调域名 (例如: https://api.v2.tybigdata.com)" required class="w-full px-3 py-2 border rounded-md">
                 <p class="text-xs text-gray-500">回调路径将自动拼接为: <code class="bg-gray-100 p-1 rounded">/api/payment/wechat/notify/</code></p>
               </div>
            </div>

             <div class="pt-6 border-t border-gray-200">
                <label class="flex items-center">
                  <input v-model="activeConfig.is_active" type="checkbox" class="h-4 w-4 text-indigo-600 border-gray-300 rounded">
                  <span class="ml-2 text-sm text-gray-700">启用该配置</span>
                </label>
             </div>
          </div>
          
          <!-- 操作按钮 (移到表单外部) -->
          <div class="mt-6 flex justify-between items-center">
             <label class="flex items-center text-sm text-gray-600">
              <input type="checkbox" v-model="showSensitive" class="h-4 w-4 text-indigo-600 border-gray-300 rounded">
              <span class="ml-2">显示/隐藏密钥</span>
            </label>
            <div class="space-x-3">
              <button type="button" @click="fetchConfigs" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">重置</button>
              <button type="submit" :disabled="isSubmitting" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md disabled:opacity-50">
                <Icon v-if="isSubmitting" name="clarity:refresh-line" class="w-4 h-4 mr-1 animate-spin" />
                保存配置
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'

const api = useApi()
const { $ui } = useNuxtApp()

const loading = ref(true)
const isSubmitting = ref(false)
const activeTab = ref('alipay_payment')
const showSensitive = ref(false)

const tabs = [
  { key: 'alipay_payment', name: '支付宝支付' },
  { key: 'wechat_payment', name: '微信支付' }
]

// 使用一个对象来存储所有表单数据
const forms = reactive({
  alipay_payment: { config_name: '', credentials: { app_id: '', app_private_key: '', alipay_public_key: '', notify_url: '' }, is_active: true },
  wechat_payment: { config_name: '', credentials: { app_id: '', mch_id: '', api_v3_key: '', key_path: '', serial_no: '', notify_url: '' }, is_active: true }
})

// 计算属性，获取当前激活Tab的表单数据
const activeConfig = computed(() => forms[activeTab.value])

// 获取所有配置
const fetchConfigs = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/external-api-configs/')
    if (response.code === 0) {
      const configs = response.data
      for (const type in configs) {
        if (forms[type] && configs[type]) {
          forms[type].config_name = configs[type].config_name
          forms[type].credentials = typeof configs[type].credentials === 'string' 
            ? JSON.parse(configs[type].credentials) 
            : configs[type].credentials
          forms[type].is_active = configs[type].is_active
        }
      }
    } else {
      $ui.error('获取配置失败', response.message)
    }
  } catch (error) {
    $ui.error('获取配置失败', '网络错误')
  } finally {
    loading.value = false
  }
}

// 保存配置
const saveConfig = async () => {
  isSubmitting.value = true
  try {
    const payload = {
      config_type: activeTab.value,
      config_name: activeConfig.value.config_name,
      credentials: JSON.stringify(activeConfig.value.credentials),
      is_active: activeConfig.value.is_active
    }
    
    const response = await api.post('/admin/external-api-configs/update/', payload)
    if (response.code === 0) {
      $ui.success(response.message)
      await fetchConfigs() // 刷新数据
    } else {
      $ui.error('保存失败', response.message)
    }
  } catch (error) {
    $ui.error('保存失败', error?.response?.data?.message || '网络错误')
  } finally {
    isSubmitting.value = false
  }
}

onMounted(fetchConfigs)
</script> 

<style scoped>
.password-mask {
  -webkit-text-security: disc;
  text-security: disc;
}

/* 动画效果 */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style> 
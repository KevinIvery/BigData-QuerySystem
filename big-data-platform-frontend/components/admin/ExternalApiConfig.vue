<template>
  <div class="max-w-4xl mx-auto">
    <!-- 页面标题 -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">外部API配置</h1>
      <p class="mt-1 text-sm text-gray-600">管理系统所依赖的第三方服务接口凭证。</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-10">
      <Icon name="clarity:refresh-line" class="w-8 h-8 text-gray-400 animate-spin" />
      <p class="mt-2 text-sm text-gray-500">正在加载API配置...</p>
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
            <!-- 天远API -->
            <div v-if="activeTab === 'tianyuan_risk_api'">
              <h3 class="text-lg font-medium text-gray-900 mb-4">天远API配置</h3>
              <p class="text-sm text-gray-500 mb-4">
                用于所有核心风险查询。请前往 
                <a href="https://tianyuanapi.com" target="_blank" class="text-indigo-600 hover:underline">天远API官网</a> 
                获取您的凭证。
              </p>
              <div class="space-y-4">
                <input v-model="forms.tianyuan_risk_api.config_name" type="text" placeholder="配置名称 (e.g., 主账号)" required class="w-full px-3 py-2 border rounded-md">
                <input v-model="forms.tianyuan_risk_api.credentials.app_id" type="text" placeholder="Access-Id" required class="w-full px-3 py-2 border rounded-md">
                <input v-model="forms.tianyuan_risk_api.credentials.app_secret" :type="showSensitive ? 'text' : 'password'" placeholder="Encryption-Key" autocomplete="new-password" required class="w-full px-3 py-2 border rounded-md">
              </div>
            </div>

            <!-- 阿里云短信 -->
            <div v-if="activeTab === 'aliyun_sms'">
               <h3 class="text-lg font-medium text-gray-900 mb-4">阿里云短信配置</h3>
               <div class="space-y-4">
                 <input v-model="forms.aliyun_sms.config_name" type="text" placeholder="配置名称 (e.g., 官方短信通道)" required class="w-full px-3 py-2 border rounded-md">
                 <input v-model="forms.aliyun_sms.credentials.app_id" type="text" placeholder="AccessKey ID" required class="w-full px-3 py-2 border rounded-md">
                 <input v-model="forms.aliyun_sms.credentials.app_secret" :type="showSensitive ? 'text' : 'password'" placeholder="AccessKey Secret" autocomplete="new-password" required class="w-full px-3 py-2 border rounded-md">
                 <input v-model="forms.aliyun_sms.credentials.SignName" type="text" placeholder="短信签名" required class="w-full px-3 py-2 border rounded-md">
                 <input v-model="forms.aliyun_sms.credentials.TemplateCode" type="text" placeholder="短信模板CODE" required class="w-full px-3 py-2 border rounded-md">
               </div>
            </div>
            
            <!-- 微信公众号 -->
            <div v-if="activeTab === 'wechat_oauth'">
               <h3 class="text-lg font-medium text-gray-900 mb-4">微信公众号登录配置</h3>
               <div class="space-y-4">
                 <input v-model="forms.wechat_oauth.config_name" type="text" placeholder="配置名称 (e.g., 主公众号)" required class="w-full px-3 py-2 border rounded-md">
                 <input v-model="forms.wechat_oauth.credentials.app_id" type="text" placeholder="AppID" required class="w-full px-3 py-2 border rounded-md">
                 <input v-model="forms.wechat_oauth.credentials.app_secret" :type="showSensitive ? 'text' : 'password'" placeholder="AppSecret" autocomplete="new-password" required class="w-full px-3 py-2 border rounded-md">
               </div>
            </div>

             <div class="pt-6 border-t border-gray-200">
                <label class="flex items-center">
                  <input v-model="activeConfig.is_active" type="checkbox" class="h-4 w-4 text-indigo-600 border-gray-300 rounded">
                  <span class="ml-2 text-sm text-gray-700">启用该配置</span>
                </label>
             </div>
          </div>
          
          <!-- 操作按钮 -->
          <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center">
            <label class="flex items-center text-sm text-gray-600">
              <input type="checkbox" v-model="showSensitive" class="h-4 w-4 text-indigo-600 border-gray-300 rounded">
              <span class="ml-2">显示/隐藏密钥</span>
            </label>
            <button type="submit" :disabled="isSubmitting" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md disabled:opacity-50">
               <Icon v-if="isSubmitting" name="clarity:refresh-line" class="w-4 h-4 mr-1 animate-spin" />
               保存配置
            </button>
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
const activeTab = ref('tianyuan_risk_api')
const showSensitive = ref(false)

const tabs = [
  { key: 'tianyuan_risk_api', name: '天远风险查询' },
  { key: 'aliyun_sms', name: '阿里云短信' },
  { key: 'wechat_oauth', name: '微信公众号登录' }
]

// 使用一个对象来存储所有表单数据
const forms = reactive({
  tianyuan_risk_api: { config_name: '', credentials: { app_id: '', app_secret: '' }, is_active: true },
  aliyun_sms: { config_name: '', credentials: { app_id: '', app_secret: '', SignName: '', TemplateCode: '' }, is_active: true },
  wechat_oauth: { config_name: '', credentials: { app_id: '', app_secret: '' }, is_active: true }
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
          // 将JSON字符串解析为对象
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
      // 将凭证对象转换为JSON字符串
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
<template>
  <div class="max-w-4xl mx-auto">
    <!-- 页面标题 -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">查询配置</h1>
      <p class="mt-1 text-sm text-gray-600">管理个人和企业查询的可用性、价格及包含的接口。</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-10">
      <Icon name="clarity:refresh-line" class="w-8 h-8 text-gray-400 animate-spin" />
      <p class="mt-2 text-sm text-gray-500">正在加载配置...</p>
    </div>

    <div v-else>
      <!-- Tab导航 -->
      <div class="border-b border-gray-200">
        <nav class="-mb-px flex space-x-8" aria-label="Tabs">
          <button
            @click="currentTab = 'personal'"
            :class="[
              currentTab === 'personal'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm focus:outline-none'
            ]"
          >
            个人查询配置
          </button>
          <button
            @click="currentTab = 'enterprise'"
            :class="[
              currentTab === 'enterprise'
                ? 'border-indigo-500 text-indigo-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
              'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm focus:outline-none'
            ]"
          >
            企业查询配置
          </button>
        </nav>
      </div>

      <!-- Tab内容 -->
      <div class="mt-8">
        <!-- 个人配置 -->
        <div v-show="currentTab === 'personal'" v-if="personalConfig">
          <form @submit.prevent="saveConfig(personalConfig.id)" class="bg-white shadow rounded-lg">
            <!-- 卡片头部 -->
            <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h3 class="text-lg font-medium text-gray-900">{{ personalConfig.config_name }}</h3>
              <div class="flex items-center space-x-3">
                <span class="text-sm text-gray-500">启用查询</span>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" v-model="personalConfig.is_active" class="sr-only peer">
                  <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-focus:ring-4 peer-focus:ring-indigo-300 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                </label>
              </div>
            </div>

            <!-- 卡片内容 -->
            <div class="px-6 py-4 space-y-6">
              <!-- 查询类别 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">查询配置类别</label>
                <select v-model="personalConfig.category" class="w-full md:w-1/3 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 bg-white">
                  <option :value="null">-- 未选择 --</option>
                  <option v-for="cat in categoryOptions" :key="cat.value" :value="cat.value">{{ cat.text }}</option>
                </select>
                <p v-if="currentCategoryDescription" class="mt-2 text-xs text-gray-500">{{ currentCategoryDescription }}</p>
              </div>
              
              <!-- 客户查询单价 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">客户查询单价 (元)</label>
                <input type="number" step="0.01" min="0" v-model="personalConfig.customer_price" class="w-full md:w-1/3 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="例如: 19.90"/>
              </div>

              <!-- 子接口配置 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">包含的接口</label>
                <div class="space-y-3 mt-2">
                  <div v-for="api in personalConfig.apis" :key="api.id" class="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                    <div>
                      <p class="text-sm font-medium text-gray-800">{{ api.api_name }}</p>
                      <p class="text-xs text-gray-500">接口编号: {{ api.api_code }}</p>
                      <p class="text-xs text-red-600 font-medium">参考费用: ¥{{ api.cost_price }}</p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" v-model="api.is_active" class="sr-only peer" :disabled="isApiToggleDisabled(personalConfig, api)"/>
                      <div class="w-9 h-5 bg-gray-300 rounded-full peer-focus:ring-2 peer-focus:ring-indigo-300 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all" :class="{ 'peer-checked:bg-green-500': !isApiToggleDisabled(personalConfig, api), 'cursor-not-allowed': isApiToggleDisabled(personalConfig, api) }"></div>
                    </label>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 操作按钮 -->
            <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end">
              <button type="submit" :disabled="saving[personalConfig.id]" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
                <Icon v-if="saving[personalConfig.id]" name="clarity:refresh-line" class="w-4 h-4 mr-2 animate-spin" />
                {{ saving[personalConfig.id] ? '保存中...' : '保存配置' }}
              </button>
            </div>
          </form>
        </div>

        <!-- 企业配置 -->
        <div v-show="currentTab === 'enterprise'" v-if="enterpriseConfig">
          <form @submit.prevent="saveConfig(enterpriseConfig.id)" class="bg-white shadow rounded-lg">
             <!-- 卡片头部, 内容和操作都类似, 这里只做结构展示 -->
             <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h3 class="text-lg font-medium text-gray-900">{{ enterpriseConfig.config_name }}</h3>
              <div class="flex items-center space-x-3">
                <span class="text-sm text-gray-500">启用查询</span>
                <label class="relative inline-flex items-center cursor-pointer">
                  <input type="checkbox" v-model="enterpriseConfig.is_active" class="sr-only peer">
                  <div class="w-11 h-6 bg-gray-200 rounded-full peer peer-focus:ring-4 peer-focus:ring-indigo-300 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-indigo-600"></div>
                </label>
              </div>
            </div>
             <div class="px-6 py-4 space-y-6">
              <!-- 客户查询单价 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">客户查询单价 (元)</label>
                <input type="number" step="0.01" min="0" v-model="enterpriseConfig.customer_price" class="w-full md:w-1/3 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500" placeholder="例如: 19.90"/>
              </div>
              <!-- 子接口配置 -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">包含的接口</label>
                <div class="space-y-3 mt-2">
                  <div v-for="api in enterpriseConfig.apis" :key="api.id" class="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                    <div>
                      <p class="text-sm font-medium text-gray-800">{{ api.api_name }}</p>
                      <p class="text-xs text-gray-500">接口编号: {{ api.api_code }}</p>
                      <p class="text-xs text-red-600 font-medium">成本价: ¥{{ api.cost_price }}</p>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" v-model="api.is_active" class="sr-only peer" :disabled="isApiToggleDisabled(enterpriseConfig, api)"/>
                      <div class="w-9 h-5 bg-gray-300 rounded-full peer-focus:ring-2 peer-focus:ring-indigo-300 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-0.5 after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all" :class="{ 'peer-checked:bg-green-500': !isApiToggleDisabled(enterpriseConfig, api), 'cursor-not-allowed': isApiToggleDisabled(enterpriseConfig, api) }"></div>
                    </label>
                  </div>
                </div>
              </div>
            </div>
            <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end">
              <button type="submit" :disabled="saving[enterpriseConfig.id]" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50">
                <Icon v-if="saving[enterpriseConfig.id]" name="clarity:refresh-line" class="w-4 h-4 mr-2 animate-spin" />
                {{ saving[enterpriseConfig.id] ? '保存中...' : '保存配置' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 法律声明弹窗 -->
    <Teleport to="body">
      <div v-if="showLegalWarningModal" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
        <div class="bg-white rounded-lg shadow-xl max-w-lg w-full p-6">
          <h3 class="text-lg font-bold text-gray-900">重要授权提示</h3>
          <div class="mt-4 text-sm text-gray-600 space-y-3">
            <p>您正在启用需要特定授权的查询服务。</p>
            <p class="font-semibold">请确保您已通过合法、有效的途径获得了被查询人的明确授权，并已留存好相关的书面、电子或其他具有同等法律效力的授权证明文件。</p>
            <p>您需要对授权的真实性和有效性负全部法律责任。</p>
          </div>
          <div class="mt-6 flex justify-end space-x-3">
            <button @click="handleCancelLegalWarning" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
              取消
            </button>
            <button @click="handleConfirmLegalWarning" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 border border-transparent rounded-md hover:bg-indigo-700">
              我已了解并同意
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { watch, computed } from 'vue';

const api = useApi()
const { $ui } = useNuxtApp()

const loading = ref(true)
const saving = ref({})
const queryConfigs = ref([])
const currentTab = ref('personal')

// 授权提醒弹窗状态
const showLegalWarningModal = ref(false)
const categoryChange = ref({ from: null, to: null })
// 一个标志位，用于防止watch的无限循环
const isProgrammaticChange = ref(false)

const categoryOptions = [
  { value: 'two_factor', text: '二要素' },
  { value: 'three_factor', text: '三要素' },
//   { value: 'face', text: '人脸' }
]

const categoryDescriptions = {
  two_factor: '用户输入姓名和身份证号，验证一致性后即可查询。',
  three_factor: '用户输入姓名、身份证号和手机号，并完成短信验证码校验后方可查询。',
  face: '用户输入姓名、身份证号，并完成人脸识别活体检测后方可查询。'
}

const personalConfig = computed(() => queryConfigs.value.find(c => c.config_name === '个人查询配置'))
const enterpriseConfig = computed(() => queryConfigs.value.find(c => c.config_name === '企业查询配置'))

const currentCategoryDescription = computed(() => {
  if (personalConfig.value && personalConfig.value.category) {
    return categoryDescriptions[personalConfig.value.category]
  }
  return ''
})

// 监听个人配置的类别变化
watch(() => personalConfig.value?.category, (newValue, oldValue) => {
  // 如果是代码触发的变更，则重置标志位并跳过
  if (isProgrammaticChange.value) {
    isProgrammaticChange.value = false
    return
  }
  
  // 仅当用户手动将值从“非二要素”改为“二要素”时触发
  // oldValue !== undefined 防止页面初次加载时 watch 被触发
  if (newValue === 'two_factor' && oldValue !== 'two_factor' && oldValue !== undefined) {
    // 立即将值恢复，等待用户确认
    if (personalConfig.value) {
      // 标记下一次变更是代码触发的
      isProgrammaticChange.value = true
      personalConfig.value.category = oldValue
    }
    // 保存变更意图
    categoryChange.value = { from: oldValue, to: newValue }
    // 显示弹窗
    showLegalWarningModal.value = true
  }
})

// 用户同意授权声明
const handleConfirmLegalWarning = () => {
  if (personalConfig.value) {
    // 标记下一次变更是代码触发的
    isProgrammaticChange.value = true
    personalConfig.value.category = categoryChange.value.to
  }
  showLegalWarningModal.value = false
}

// 用户取消授权声明
const handleCancelLegalWarning = () => {
  // 值已经被恢复，所以只需关闭弹窗
  showLegalWarningModal.value = false
}


// 获取配置数据
const fetchQueryConfigs = async () => {
  try {
    loading.value = true
    const response = await api.get('/admin/query-configs/')
    if (response.code === 0) {
      queryConfigs.value = response.data
    } else {
      $ui.error('获取配置失败', response.message)
    }
  } catch (error) {
    console.error('获取查询配置失败:', error)
    $ui.error('获取配置失败', '网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 检查子接口开关是否应被禁用
const isApiToggleDisabled = (config, currentApi) => {
  if (!config) return true
  // 企业查询只有一个接口，永远不能禁用
  if (config.config_name === '企业查询配置' && config.apis.length === 1) {
    return true
  }
  // 如果这是当前配置中唯一一个启用的接口，则不能禁用它
  const activeApis = config.apis.filter(a => a.is_active)
  if (activeApis.length === 1 && currentApi.is_active) {
    return true
  }
  return false
}

// 保存配置
const saveConfig = async (configId) => {
  const configToSave = queryConfigs.value.find(c => c.id === configId)
  if (!configToSave) return

  // 验证：价格不能为空
  if (configToSave.customer_price === '' || configToSave.customer_price === null) {
      $ui.warning('客户查询单价不能为空')
      return
  }

  // 验证：主开关关闭前，检查是否是最后一个启用的主开关
  if (!configToSave.is_active) {
    const otherActiveConfigs = queryConfigs.value.filter(c => c.id !== configId && c.is_active)
    if (otherActiveConfigs.length === 0) {
      $ui.warning('必须至少保留一个查询配置处于启用状态')
      // 恢复开关状态
      configToSave.is_active = true
      return
    }
  }
  
  try {
    saving.value[configId] = true
    
    const payload = {
      is_active: configToSave.is_active,
      customer_price: parseFloat(configToSave.customer_price),
      apis: configToSave.apis.map(a => ({ id: a.id, is_active: a.is_active }))
    }
    // 只为个人配置添加category字段
    if (configToSave.config_name === '个人查询配置') {
      payload.category = configToSave.category
    }
    
    const response = await api.post(`/admin/query-configs/update/${configId}/`, payload)
    
    if (response.code === 0) {
      $ui.success(`${configToSave.config_name} 更新成功`)
      // 重新获取数据以确保同步
      await fetchQueryConfigs()
    } else {
      $ui.error('保存失败', response.message)
    }
  } catch (error) {
    console.error('保存查询配置失败:', error)
    $ui.error('保存失败', error?.response?.data?.message || '网络错误')
  } finally {
    saving.value[configId] = false
  }
}

onMounted(fetchQueryConfigs)
</script> 
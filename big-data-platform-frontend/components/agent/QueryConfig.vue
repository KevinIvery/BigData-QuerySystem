<template>
  <div class="max-w-4xl mx-auto">
    <!-- 页面标题 -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">查询配置</h1>
      <p class="mt-1 text-sm text-gray-600">管理个人和企业查询的客户价格设置。接口组合由管理员控制。</p>
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
                ? 'border-green-500 text-green-600'
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
                ? 'border-green-500 text-green-600'
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
                <span class="text-sm text-gray-500">配置状态</span>
                <span :class="[
                  personalConfig.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800',
                  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'
                ]">
                  {{ personalConfig.is_active ? '已启用' : '已禁用' }}
                </span>
              </div>
            </div>

            <!-- 卡片内容 -->
            <div class="px-6 py-4 space-y-6">
              <!-- 价格设置区域 -->
              <div class="bg-blue-50 p-4 rounded-lg">
                <h4 class="text-sm font-medium text-blue-900 mb-3">价格设置</h4>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <!-- 管理员底价 -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">管理员底价</label>
                    <div class="flex items-center">
                      <span class="text-lg font-semibold text-red-600">¥{{ personalConfig.bottom_price }}</span>
                      <span class="ml-2 text-xs text-gray-500">（不可修改）</span>
                    </div>
                  </div>
                  
                  <!-- 客户查询价格 -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">客户查询价格</label>
                    <div class="flex items-center">
                      <span class="text-sm text-gray-500 mr-1">¥</span>
                      <input 
                        type="number" 
                        step="0.01" 
                        :min="personalConfig.bottom_price" 
                        v-model="personalConfig.customer_price" 
                        class="w-24 px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                        :class="{ 'border-red-300': parseFloat(personalConfig.customer_price) < parseFloat(personalConfig.bottom_price) }"
                      />
                    </div>
                    <p v-if="parseFloat(personalConfig.customer_price) < parseFloat(personalConfig.bottom_price)" class="text-xs text-red-600 mt-1">
                      客户价格不能低于底价限制
                    </p>
                  </div>
                  
                  <!-- 代理收益 -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">代理收益</label>
                    <div class="flex items-center">
                      <span class="text-lg font-semibold text-green-600">
                        ¥{{ calculateProfit(personalConfig.customer_price, personalConfig.bottom_price) }}
                      </span>
                      <span class="ml-2 text-xs text-gray-500">（每笔）</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 接口配置（只读） -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">包含的接口（由管理员控制）</label>
                <div class="space-y-3 mt-2">
                  <div v-for="api in personalConfig.apis" :key="api.id" class="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                    <div>
                      <p class="text-sm font-medium text-gray-800">{{ api.api_name }}</p>
                    </div>
                    <div class="flex items-center">
                      <span :class="[
                        api.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800',
                        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'
                      ]">
                        {{ api.is_active ? '已启用' : '已禁用' }}
                      </span>
                    </div>
                  </div>
                </div>
                <p class="mt-2 text-xs text-gray-500">
                  <Icon name="clarity:info-line" class="w-4 h-4 inline mr-1" />
                  接口的启用/禁用状态由管理员控制，如需调整请联系管理员
                </p>
              </div>
            </div>
            
            <!-- 操作按钮 -->
            <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end">
              <button 
                type="submit" 
                :disabled="saving[personalConfig.id] || !isValidPrice(personalConfig.customer_price, personalConfig.bottom_price)" 
                class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Icon v-if="saving[personalConfig.id]" name="clarity:refresh-line" class="w-4 h-4 mr-2 animate-spin" />
                {{ saving[personalConfig.id] ? '保存中...' : '保存价格设置' }}
              </button>
            </div>
          </form>
        </div>

        <!-- 企业配置 -->
        <div v-show="currentTab === 'enterprise'" v-if="enterpriseConfig">
          <form @submit.prevent="saveConfig(enterpriseConfig.id)" class="bg-white shadow rounded-lg">
            <!-- 卡片头部 -->
            <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
              <h3 class="text-lg font-medium text-gray-900">{{ enterpriseConfig.config_name }}</h3>
              <div class="flex items-center space-x-3">
                <span class="text-sm text-gray-500">配置状态</span>
                <span :class="[
                  enterpriseConfig.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-gray-100 text-gray-800',
                  'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'
                ]">
                  {{ enterpriseConfig.is_active ? '已启用' : '已禁用' }}
                </span>
              </div>
            </div>

            <!-- 卡片内容 -->
            <div class="px-6 py-4 space-y-6">
              <!-- 价格设置区域 -->
              <div class="bg-purple-50 p-4 rounded-lg">
                <h4 class="text-sm font-medium text-purple-900 mb-3">价格设置</h4>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <!-- 管理员底价 -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">管理员底价</label>
                    <div class="flex items-center">
                      <span class="text-lg font-semibold text-red-600">¥{{ enterpriseConfig.bottom_price }}</span>
                      <span class="ml-2 text-xs text-gray-500">（不可修改）</span>
                    </div>
                  </div>
                  
                  <!-- 客户查询价格 -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">客户查询价格</label>
                    <div class="flex items-center">
                      <span class="text-sm text-gray-500 mr-1">¥</span>
                      <input 
                        type="number" 
                        step="0.01" 
                        :min="enterpriseConfig.bottom_price" 
                        v-model="enterpriseConfig.customer_price" 
                        class="w-24 px-2 py-1 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 text-sm"
                        :class="{ 'border-red-300': parseFloat(enterpriseConfig.customer_price) < parseFloat(enterpriseConfig.bottom_price) }"
                      />
                    </div>
                    <p v-if="parseFloat(enterpriseConfig.customer_price) < parseFloat(enterpriseConfig.bottom_price)" class="text-xs text-red-600 mt-1">
                      客户价格不能低于底价限制
                    </p>
                  </div>
                  
                  <!-- 代理收益 -->
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-1">代理收益</label>
                    <div class="flex items-center">
                      <span class="text-lg font-semibold text-green-600">
                        ¥{{ calculateProfit(enterpriseConfig.customer_price, enterpriseConfig.bottom_price) }}
                      </span>
                      <span class="ml-2 text-xs text-gray-500">（每笔）</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 接口配置（只读） -->
              <div>
                <label class="block text-sm font-medium text-gray-700 mb-2">包含的接口（由管理员控制）</label>
                <div class="space-y-3 mt-2">
                  <div v-for="api in enterpriseConfig.apis" :key="api.id" class="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                    <div>
                      <p class="text-sm font-medium text-gray-800">{{ api.api_name }}</p>
                    </div>
                    <div class="flex items-center">
                      <span :class="[
                        api.is_active 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800',
                        'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'
                      ]">
                        {{ api.is_active ? '已启用' : '已禁用' }}
                      </span>
                    </div>
                  </div>
                </div>
                <p class="mt-2 text-xs text-gray-500">
                  <Icon name="clarity:info-line" class="w-4 h-4 inline mr-1" />
                  接口的启用/禁用状态由管理员控制，如需调整请联系管理员
                </p>
              </div>
            </div>
            
            <!-- 操作按钮 -->
            <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end">
              <button 
                type="submit" 
                :disabled="saving[enterpriseConfig.id] || !isValidPrice(enterpriseConfig.customer_price, enterpriseConfig.bottom_price)" 
                class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Icon v-if="saving[enterpriseConfig.id]" name="clarity:refresh-line" class="w-4 h-4 mr-2 animate-spin" />
                {{ saving[enterpriseConfig.id] ? '保存中...' : '保存价格设置' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const api = useApi()
const { $ui } = useNuxtApp()

const loading = ref(true)
const saving = ref({})
const queryConfigs = ref([])
const currentTab = ref('personal')

const personalConfig = computed(() => queryConfigs.value.find(c => c.config_name === '个人查询配置'))
const enterpriseConfig = computed(() => queryConfigs.value.find(c => c.config_name === '企业查询配置'))

// 获取配置数据
const fetchQueryConfigs = async () => {
  try {
    loading.value = true
    const response = await api.post('/agent/query-configs/')
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

// 计算代理收益
const calculateProfit = (customerPrice, bottomPrice) => {
  const profit = parseFloat(customerPrice || 0) - parseFloat(bottomPrice || 0)
  return profit > 0 ? profit.toFixed(2) : '0.00'
}

// 验证价格是否有效
const isValidPrice = (customerPrice, bottomPrice) => {
  const customer = parseFloat(customerPrice || 0)
  const bottom = parseFloat(bottomPrice || 0)
  return customer >= bottom && customer > 0
}

// 保存配置
const saveConfig = async (configId) => {
  const configToSave = queryConfigs.value.find(c => c.id === configId)
  if (!configToSave) return

  // 验证：价格不能为空
  if (configToSave.customer_price === '' || configToSave.customer_price === null) {
    $ui.warning('客户查询价格不能为空')
    return
  }

  // 验证：价格不能低于底价
  if (!isValidPrice(configToSave.customer_price, configToSave.bottom_price)) {
    $ui.warning('客户价格不能低于底价限制')
    return
  }
  
  try {
    saving.value[configId] = true
    
    const payload = {
      customer_price: parseFloat(configToSave.customer_price)
    }
    
    const response = await api.post(`/agent/query-configs/update/${configId}/`, payload)
    
    if (response.code === 0) {
      $ui.success(`${configToSave.config_name} 价格更新成功`)
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

<style scoped>
/* 动画效果 */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style> 
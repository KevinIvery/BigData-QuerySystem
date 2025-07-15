<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
    <!-- 头部导航 -->
    <Header :order-no="orderNo" />
    <!-- 目录锚点菜单 -->
    <TableOfContents 
      v-if="menuItems.length > 0"
      :menu-items="menuItems"
      @section-change="handleSectionChange"
    />
    <!-- 支付完成等待报告时显示全屏蒙版 -->
    <div v-if="orderData && orderData.status === 'paid' && orderData.query_result?.status !== 'success' && orderData.query_result?.status !== 'failed'" class="fixed inset-0 z-50 flex flex-col items-center justify-center bg-white/80 backdrop-blur-sm">
      <div class="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mb-6"></div>
      <div class="text-lg font-semibold text-gray-800 mb-2">正在查询，请稍候</div>
      <div class="text-gray-500 text-sm">您的支付已完成，正在为您生成报告…</div>
    </div>
    <!-- 主内容 -->
    <main class="max-w-2xl mx-auto  py-6">
      <!-- 加载状态 -->
      <div v-if="isLoading" class="text-center py-12">
        <div class="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-gray-600">正在加载订单信息...</p>
      </div>
      <!-- 错误状态 -->
      <div v-else-if="error" class="text-center py-12">
        <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Icon name="ph:warning-circle-bold" class="w-8 h-8 text-red-500" />
        </div>
        <h3 class="text-lg font-semibold text-gray-800 mb-2">加载失败</h3>
        <p class="text-gray-600 mb-4">{{ error }}</p>
        <button @click="fetchOrderData" class="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
          重试
        </button>
      </div>
      <!-- 处理中/未完成时显示进度条 -->
      <div v-else-if="orderData && orderData.query_result?.status !== 'success' && orderData.query_result?.status !== 'failed'" class="mb-6">
        <div class="bg-white rounded-2xl shadow-lg p-6">
          <h2 class="text-lg font-semibold text-gray-800 mb-6">查询进度</h2>
          <div class="relative">
            <div class="absolute top-6 left-6 right-6 h-0.5 bg-gray-200">
              <div 
                class="h-full bg-blue-500 transition-all duration-500 ease-out"
                :style="{ width: progressWidth }"
              ></div>
            </div>
            <div class="relative flex justify-between">
              <div 
                v-for="(step, index) in statusSteps" 
                :key="step.key"
                class="flex flex-col items-center"
              >
                <div 
                  :class="[
                    'w-12 h-12 rounded-full flex items-center justify-center border-2 transition-all duration-300',
                    getStepClass(step.key)
                  ]"
                >
                  <Icon :name="step.icon" class="w-6 h-6" />
                </div>
                <div class="mt-3 text-center">
                  <p :class="['text-sm font-medium', isStepActive(step.key) ? 'text-blue-600' : 'text-gray-500']">
                    {{ step.label }}
                  </p>
                  <p v-if="getStepTime(step.key)" class="text-xs text-gray-400 mt-1">
                    {{ formatTime(getStepTime(step.key)) }}
                  </p>
                </div>
              </div>
            </div>
          </div>
          <div class="mt-6 p-4 bg-gray-50 rounded-lg">
            <div class="flex items-center">
              <div 
                :class="[
                  'w-3 h-3 rounded-full mr-3',
                  getStatusColor()
                ]"
              ></div>
              <span class="font-medium text-gray-800">{{ getStatusText() }}</span>
            </div>
            <p class="text-sm text-gray-600 mt-2">{{ getStatusDescription() }}</p>
            <div v-if="orderData.status === 'pending' && orderData.payment_method" class="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <div class="flex items-center">
                <div class="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mr-2"></div>
                <span class="text-sm text-blue-700 font-medium">正在检查支付状态...</span>
              </div>
              <p class="text-xs text-blue-600 mt-1">系统会自动检测您的支付状态，请稍候</p>
            </div>
          </div>
        </div>
      </div>
      <!-- 查询结果报告展示 -->
      <div v-else-if="orderData.query_result?.status === 'success'" class="space-y-6">

        <!-- 报告概况组件 - 根据查询类型动态选择 -->
        <component
          :is="getReportOverviewComponent()"
          :user-info="orderData.query_result.result_data.data.user_info || {}"
          :query-type="orderData.query_type"
          :query-time="orderData.query_result.result_data.data.query_time"
          :api-results="orderData.query_result.result_data.data.api_results || []"
        />
        <!-- 动态渲染查询结果组件 -->
        <template v-for="code in filteredApiCodes" :key="code">
          <component
            :is="apiComponentMap[code]?.component"
            :data="getApiResult(code)"
            :show-debug="showDebug"
          />
          <div v-if="!apiComponentMap[code]?.component" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            <strong>调试信息:</strong> API代码 {{ code }} 没有找到对应的组件映射
          </div>
        </template>
        <DisclaimerNote />
        <div v-if="showDebug" class="bg-white rounded-2xl shadow-lg p-6">
          <h3 class="text-lg font-semibold text-gray-800 mb-4">调试信息</h3>
          <div class="bg-gray-50 rounded-lg p-4">
            <h4 class="font-medium text-gray-800 mb-3">完整查询数据</h4>
            <pre class="text-sm text-gray-600 whitespace-pre-wrap">{{ JSON.stringify(orderData.query_result.result_data, null, 2) }}</pre>
          </div>
        </div>
      </div>
      <!-- 查询失败 -->
      <div v-else-if="orderData.query_result?.status === 'failed'" class="bg-white rounded-2xl shadow-lg p-6 text-center py-6">
        <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Icon name="ph:x-circle-bold" class="w-8 h-8 text-red-500" />
        </div>
        <h4 class="font-semibold text-gray-800 mb-2">查询失败</h4>
        <p class="text-gray-600">{{ orderData.query_result.error_message || '查询过程中发生错误' }}</p>
      </div>
      <!-- 查询中兜底 -->
      <div v-else-if="orderData.query_result" class="bg-white rounded-2xl shadow-lg p-6 text-center py-6">
        <div class="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <h4 class="font-semibold text-gray-800 mb-2">查询处理中</h4>
        <p class="text-gray-600">请稍候，我们正在为您查询数据...</p>
      </div>
    </main>
    <!-- 底部操作按钮 -->
    <!-- <Footer 
    v-if="orderData?.query_result?.status === 'success' && menuItems.length > 0"/> -->
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useApi } from '~/composables/useApi'
import { apiComponentMap, isEnterpriseApi } from '~/composables/useApiComponentMap'

// 导入查询结果组件
import Header from '~/components/query-results/Header.vue'
import TableOfContents from '~/components/query-results/TableOfContents.vue'
import Footer from '~/components/query-results/Footer.vue'
import DisclaimerNote from '~/components/query-results/DisclaimerNote.vue'
definePageMeta({
  middleware: 'site-init'
})

const route = useRoute()
const router = useRouter()
const api = useApi()

const orderNo = route.params.orderNo
const isLoading = ref(true)
const error = ref(null)
const orderData = ref(null)
const pollingTimer = ref(null)
const showDebug = ref(false)

// 状态步骤定义
const statusSteps = [
  { key: 'pending', label: '待支付', icon: 'ph:clock-bold' },
  { key: 'paid', label: '已支付', icon: 'ph:check-bold' },
  { key: 'querying', label: '查询中', icon: 'ph:magnifying-glass-bold' },
  { key: 'completed', label: '查询完成', icon: 'ph:check-circle-bold' }
]

// 计算进度宽度
const progressWidth = computed(() => {
  if (!orderData.value) return '0%'
  
  const currentStatus = orderData.value.status
  const stepIndex = statusSteps.findIndex(step => step.key === currentStatus)
  
  if (stepIndex === -1) return '0%'
  
  return `${(stepIndex / (statusSteps.length - 1)) * 100}%`
})

// 获取步骤样式
const getStepClass = (stepKey) => {
  if (!orderData.value) return 'bg-gray-100 border-gray-300 text-gray-400'
  
  const currentStatus = orderData.value.status
  const currentIndex = statusSteps.findIndex(step => step.key === currentStatus)
  const stepIndex = statusSteps.findIndex(step => step.key === stepKey)
  
  if (stepIndex <= currentIndex) {
    return 'bg-blue-500 border-blue-500 text-white'
  } else {
    return 'bg-gray-100 border-gray-300 text-gray-400'
  }
}

// 判断步骤是否激活
const isStepActive = (stepKey) => {
  if (!orderData.value) return false
  
  const currentStatus = orderData.value.status
  const currentIndex = statusSteps.findIndex(step => step.key === currentStatus)
  const stepIndex = statusSteps.findIndex(step => step.key === stepKey)
  
  return stepIndex <= currentIndex
}

// 获取步骤时间
const getStepTime = (stepKey) => {
  if (!orderData.value) return null
  
  switch (stepKey) {
    case 'pending':
      return orderData.value.created_at
    case 'paid':
      return orderData.value.payment_time
    case 'querying':
      return orderData.value.query_start_time
    case 'completed':
      return orderData.value.query_complete_time
    default:
      return null
  }
}

// 获取状态颜色
const getStatusColor = () => {
  if (!orderData.value) return 'bg-gray-400'
  
  switch (orderData.value.status) {
    case 'pending':
      return 'bg-yellow-400'
    case 'paid':
    case 'querying':
      return 'bg-blue-400 animate-pulse'
    case 'completed':
      return 'bg-green-400'
    case 'failed':
      return 'bg-red-400'
    default:
      return 'bg-gray-400'
  }
}

// 获取状态文本
const getStatusText = () => {
  if (!orderData.value) return '未知状态'
  
  switch (orderData.value.status) {
    case 'pending':
      return '等待支付'
    case 'paid':
      return '支付成功'
    case 'querying':
      return '查询中'
    case 'completed':
      return '查询完成'
    case 'failed':
      return '查询失败'
    default:
      return '未知状态'
  }
}

// 获取状态描述
const getStatusDescription = () => {
  if (!orderData.value) return ''
  
  switch (orderData.value.status) {
    case 'pending':
      return '请完成支付以开始查询'
    case 'paid':
      return '支付成功，正在准备查询'
    case 'querying':
      return '正在查询数据，请稍候...'
    case 'completed':
      return '查询已完成，您可以查看结果'
    case 'failed':
      return '查询过程中发生错误'
    default:
      return ''
  }
}



// 格式化时间
const formatTime = (timeString) => {
  if (!timeString) return ''
  
  const date = new Date(timeString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const enabledApiCodes = computed(() => {
  return orderData.value?.query_result?.result_data?.data?.api_results?.map(r => r.api_code) || []
})

// 根据查询类型过滤API组件
const filteredApiCodes = computed(() => {
  if (!orderData.value?.query_type) {
    return enabledApiCodes.value
  }
  
  const isEnterprise = orderData.value.query_type === '企业查询配置'
  
  return enabledApiCodes.value.filter(code => {
    const isEnterpriseCode = isEnterpriseApi(code)
    return isEnterprise ? isEnterpriseCode : !isEnterpriseCode
  })
})

const menuItems = computed(() => {
  return filteredApiCodes.value.map(code => ({
    id: apiComponentMap[code]?.menuId || code,
    title: apiComponentMap[code]?.title || code,
    icon: apiComponentMap[code]?.icon
  }))
})

// 根据查询类型选择报告概况组件
const getReportOverviewComponent = () => {
  const isEnterprise = orderData.value?.query_type === '企业查询配置'
  
  // 动态查找对应的报告概况组件
  const reportOverviewCodes = Object.keys(apiComponentMap).filter(code => 
    apiComponentMap[code]?.title?.includes('报告概况')
  )
  
  if (isEnterprise) {
    // 查找企业报告概况组件
    const enterpriseReportCode = reportOverviewCodes.find(code => isEnterpriseApi(code))
    if (enterpriseReportCode) {
      return apiComponentMap[enterpriseReportCode]?.component
    }
  }
  
  // 查找个人报告概况组件（默认）
  const personalReportCode = reportOverviewCodes.find(code => !isEnterpriseApi(code))
  return apiComponentMap[personalReportCode]?.component
}

const getApiResult = (apiCode) => {
  return orderData.value?.query_result?.result_data?.data?.api_results?.find(r => r.api_code === apiCode)
}

// 处理目录区域变化
const handleSectionChange = (sectionId) => {
  // 目录区域变化处理
}

// 获取订单数据
const fetchOrderData = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    const response = await api.get(`/frontend/query-result/${orderNo}/`)
    
    if (response.code === 0) {
      orderData.value = response.data
      
      // 如果订单还在处理中，启动轮询
      if (['pending', 'paid', 'querying'].includes(orderData.value.status)) {
        startPolling()
      }
    } else {
      error.value = response.message || '获取订单信息失败'
    }
  } catch (err) {
    error.value = '网络错误，请检查网络连接'
  } finally {
    isLoading.value = false
  }
}

// 开始轮询
const startPolling = () => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
  }
  
  pollingTimer.value = setInterval(async () => {
    try {
      const response = await api.get(`/frontend/query-result/${orderNo}/`)
      
      if (response.code === 0) {
        const previousStatus = orderData.value?.status
        orderData.value = response.data
        
        // 如果查询完成或失败，停止轮询
        if (['completed', 'failed'].includes(orderData.value.status)) {
          stopPolling()
        }
      }
    } catch (err) {
      // 轮询异常时静默处理
    }
  }, 3000)
}

// 停止轮询
const stopPolling = () => {
  if (pollingTimer.value) {
    clearInterval(pollingTimer.value)
    pollingTimer.value = null
  }
}

// 刷新数据
const refreshData = async () => {
  try {
    const response = await api.get(`/frontend/query-result/${orderNo}/`)
    
    if (response.code === 0) {
      orderData.value = response.data
    }
  } catch (error) {
    // 刷新失败时静默处理
  }
}

// 页面挂载时获取数据
onMounted(() => {
  fetchOrderData()
})

// 页面卸载时清理轮询
onUnmounted(() => {
  stopPolling()
})

// 页面标题
useHead({
  title: '查询结果 '
})
</script>

 
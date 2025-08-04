<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
    <Header order-no="EXAMPLE" />
    <TableOfContents v-if="menuItems.length > 0" :menu-items="menuItems" />
    <main class="max-w-2xl mx-auto  py-6">
      <div v-if="isLoading" class="text-center py-12">
        <div class="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
        <p class="text-gray-600">正在加载示例报告...</p>
      </div>
      <div v-else-if="error" class="text-center py-12">
        <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <Icon name="ph:warning-circle-bold" class="w-8 h-8 text-red-500" />
        </div>
        <h3 class="text-lg font-semibold text-gray-800 mb-2">加载失败</h3>
        <p class="text-gray-600 mb-4">{{ error }}</p>
      </div>
      <div v-else class="space-y-6">
        <!-- 报告概况组件 -->
        <component
          v-if="queryType === 'enterprise'"
          :is="apiComponentMap['ENTERPRISE_REPORT_OVERVIEW']?.component"
          :user-info="reportData.user_info || {}"
          :query-type="reportData.query_type"
          :query-time="reportData.query_time"
          :api-results="reportData.api_results || []"
        />
        <component
          v-else
          :is="apiComponentMap['REPORT_OVERVIEW']?.component"
          :user-info="reportData.user_info || {}"
          :query-type="reportData.query_type"
          :query-time="reportData.query_time"
          :api-results="reportData.api_results || []"
        />
        
        <!-- 动态渲染API组件 -->
        <component
          v-for="code in enabledApiCodes.filter(code => shouldRenderComponent(code) && !['REPORT_OVERVIEW', 'ENTERPRISE_REPORT_OVERVIEW'].includes(code))"
          :is="apiComponentMap[code]?.component"
          :key="code"
          :data="getApiResult(code)"
          :show-debug="false"
        />
        <DisclaimerNote />
      </div>
    </main>
    <Footer v-if="menuItems.length > 0" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import Header from '~/components/query-results/Header.vue'
import TableOfContents from '~/components/query-results/TableOfContents.vue'
import Footer from '~/components/query-results/Footer.vue'
import DisclaimerNote from '~/components/query-results/DisclaimerNote.vue'
import { useApi } from '~/composables/useApi'
import { apiComponentMap } from '~/composables/useApiComponentMap'

const isLoading = ref(true)
const error = ref(null)
const reportData = ref(null)
const siteConfig = ref(null)
const api = useApi()
const route = useRoute()

// 从URL参数获取查询类型，默认为个人
const queryType = computed(() => {
  return route.query.type === 'enterprise' ? 'enterprise' : 'personal'
})

console.log('[example-report] 查询类型:', queryType.value)

// 1. 先请求站点配置，再请求示例报告
const fetchAll = async () => {
  isLoading.value = true
  error.value = null
  try {
    const siteRes = await api.get('/frontend/data/')
    if (siteRes.code === 0 && siteRes.data) {
      siteConfig.value = siteRes.data
    } else {
      throw new Error(siteRes.message || '获取站点配置失败')
    }
    
    // 请求示例报告时传递查询类型参数
    const reportRes = await api.get('/frontend/example-report/', {
       type: queryType.value 
    })
    
    if (reportRes.code === 0 && reportRes.data) {
      if (reportRes.data.api_results) {
        reportData.value = reportRes.data
      } else if (reportRes.data.query_result?.result_data?.data?.api_results) {
        reportData.value = reportRes.data.query_result.result_data.data
      } else {
        throw new Error('示例报告数据结构异常')
      }
    } else {
      throw new Error(reportRes.message || '获取示例报告失败')
    }
  } catch (e) {
    error.value = e.message
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  fetchAll()
})

// 根据查询类型获取对应的查询配置
const getCurrentQueryConfig = () => {
  const configs = siteConfig.value?.query_configs || []
  if (queryType.value === 'enterprise') {
    return configs.find(c => c.config_name === '企业查询配置')
  } else {
    return configs.find(c => c.config_name === '个人查询配置')
  }
}

// 获取启用的API代码
const enabledApiCodes = computed(() => {
  const currentConfig = getCurrentQueryConfig()
  if (!currentConfig) return []
  
  console.log('[example-report] 当前配置:', currentConfig)
  
  let apiCodes = currentConfig.included_apis.filter(api => api.is_active).map(api => api.api_code)
  
  // 如果是企业查询，需要添加企业报告概况组件
  if (queryType.value === 'enterprise') {
    apiCodes = ['ENTERPRISE_REPORT_OVERVIEW', ...apiCodes]
  } else {
    // 个人查询添加个人报告概况组件
    apiCodes = ['REPORT_OVERVIEW', ...apiCodes]
  }
  
  return apiCodes
})

const menuItems = computed(() => enabledApiCodes.value.map(code => ({
  id: apiComponentMap[code]?.menuId || code,
  title: apiComponentMap[code]?.title || code,
  icon: apiComponentMap[code]?.icon
})))

const getApiResult = (apiCode) => {
  if (!reportData.value?.api_results) return null
  return reportData.value.api_results.find(r => r.api_code === apiCode)
}

// 根据查询类型渲染不同的组件
const shouldRenderComponent = (apiCode) => {
  // 企业查询的组件过滤
  if (queryType.value === 'enterprise') {
    // 企业专用组件
    const enterpriseComponents = ['ENTERPRISE_REPORT_OVERVIEW', 'QYGL8261']
    return enterpriseComponents.includes(apiCode)
  }
  
  // 个人查询保持现有逻辑
  return true
}
</script> 
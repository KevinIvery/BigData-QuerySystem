<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- Header -->
    <div class="sticky top-0 z-10 bg-white border-b border-gray-200 px-4 py-3">
      <div class="flex items-center">
        <button @click="$router.back()" class="mr-3 p-2 -ml-2 text-gray-600">
          <Icon name="ph:arrow-left-bold" class="w-6 h-6" />
        </button>
        <h1 class="text-lg font-semibold text-gray-900">查询历史</h1>
      </div>
    </div>

    <!-- Content -->
    <div class="px-4 py-4">
      <!-- Query History List -->
      <div v-if="queryHistory.length > 0" class="space-y-3">
        <div 
          v-for="query in queryHistory" 
          :key="query.id"
          class="bg-white rounded-lg shadow-sm border border-gray-200 p-4"
        >
          <!-- Query Header -->
          <div class="flex justify-between items-start mb-3">
            <div>
              <div class="text-sm text-gray-500">查询项目</div>
              <div class="text-base font-medium text-gray-900">{{ query.query_type }}</div>
            </div>
            <div>
              <span 
                :class="{
                  'bg-green-100 text-green-800': query.status === 'completed',
                  'bg-red-100 text-red-800': query.status === 'failed',
                  'bg-orange-100 text-orange-800': query.status === 'expired',
                  'bg-blue-100 text-blue-800': query.status === 'pending'
                }"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              >
                {{ query.status_text }}
              </span>
            </div>
          </div>

          <!-- Query Details -->
          <div class="mb-3">
            <div class="text-xs text-gray-500 mb-1">关联订单号</div>
            <div class="font-mono text-sm text-gray-700">{{ query.order_no }}</div>
          </div>

          <!-- Time Info -->
          <div class="flex justify-between items-center text-xs text-gray-500 mb-3">
            <div>查询时间: {{ formatDateTime(query.created_at) }}</div>
            <div v-if="query.expires_at">
              到期时间: {{ formatDateTime(query.expires_at) }}
            </div>
          </div>

          <!-- Error Message -->
          <div v-if="query.error_message" class="mb-3 p-3 bg-red-50 rounded-lg">
            <div class="text-xs text-red-600 font-medium mb-1">错误信息</div>
            <div class="text-sm text-red-700">{{ query.error_message }}</div>
          </div>

          <!-- Actions -->
          <div class="flex space-x-2">
            <button 
              v-if="query.status === 'completed'"
              @click="viewQueryResult(query.order_no)"
              class="flex-1 bg-blue-50 text-blue-600 py-2 px-4 rounded-lg text-sm font-medium hover:bg-blue-100 transition-colors"
            >
              查看报告
            </button>
            <button 
              v-if="query.status === 'expired'"
              @click="requery(query.order_no)"
              class="flex-1 bg-gray-50 text-gray-600 py-2 px-4 rounded-lg text-sm font-medium hover:bg-gray-100 transition-colors"
            >
              重新查询
            </button>
            <button 
              v-if="query.status === 'failed'"
              @click="contactSupport(query.order_no)"
              class="flex-1 bg-orange-50 text-orange-600 py-2 px-4 rounded-lg text-sm font-medium hover:bg-orange-100 transition-colors"
            >
              联系客服
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!isLoading" class="text-center py-16">
        <Icon name="ph:file-search-duotone" class="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">暂无查询记录</h3>
        <p class="text-gray-500 mb-6">您还没有任何查询记录</p>
        <button 
          @click="$router.push('/')"
          class="bg-blue-500 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-600 transition-colors"
        >
          立即查询
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="space-y-3">
        <div v-for="i in 3" :key="i" class="bg-white rounded-lg shadow-sm border border-gray-200 p-4 animate-pulse">
          <div class="flex justify-between items-start mb-3">
            <div>
              <div class="h-3 bg-gray-200 rounded w-16 mb-2"></div>
              <div class="h-5 bg-gray-200 rounded w-24"></div>
            </div>
            <div class="h-6 bg-gray-200 rounded w-16"></div>
          </div>
          <div class="mb-3">
            <div class="h-3 bg-gray-200 rounded w-20 mb-2"></div>
            <div class="h-4 bg-gray-200 rounded w-32"></div>
          </div>
          <div class="flex justify-between items-center mb-3">
            <div class="h-3 bg-gray-200 rounded w-28"></div>
            <div class="h-3 bg-gray-200 rounded w-28"></div>
          </div>
          <div class="h-8 bg-gray-200 rounded"></div>
        </div>
      </div>

      <!-- Load More Button -->
      <div v-if="hasMore && !isLoading" class="mt-6 text-center">
        <button 
          @click="loadMore"
          class="bg-gray-100 text-gray-700 px-6 py-2 rounded-lg font-medium hover:bg-gray-200 transition-colors"
        >
          加载更多
        </button>
      </div>

      <!-- Loading More Indicator -->
      <div v-if="isLoadingMore" class="mt-6 text-center">
        <div class="inline-flex items-center text-gray-500">
          <Icon name="ph:spinner" class="w-4 h-4 mr-2 animate-spin" />
          加载中...
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// 数据状态
const queryHistory = ref([])
const isLoading = ref(false)
const isLoadingMore = ref(false)
const hasMore = ref(true)
const currentPage = ref(1)
const pageSize = 10

// 页面标题
useHead({
  title: '查询历史'
})

// 加载查询历史
const loadQueryHistory = async (page = 1, append = false) => {
  try {
    if (page === 1) {
      isLoading.value = true
    } else {
      isLoadingMore.value = true
    }

    const api = useApi()
    const response = await api.get('/frontend/query-history/', {
      page,
      page_size: pageSize
    })

    const { query_history, pagination } = response.data
    
    if (append) {
      queryHistory.value.push(...query_history)
    } else {
      queryHistory.value = query_history
    }

    hasMore.value = pagination.has_next
    currentPage.value = pagination.current_page

  } catch (error) {
    console.error('加载查询历史异常:', error)
    // 错误已由API工具自动处理
  } finally {
    isLoading.value = false
    isLoadingMore.value = false
  }
}

// 加载更多
const loadMore = () => {
  if (hasMore.value && !isLoadingMore.value) {
    loadQueryHistory(currentPage.value + 1, true)
  }
}

// 查看查询结果
const viewQueryResult = (orderNo) => {
  router.push(`/query-result/${orderNo}`)
}

// 重新查询
const requery = (orderNo) => {
  // 这里可以跳转到首页重新开始查询流程
  router.push('/')
}

// 联系客服
const contactSupport = (orderNo) => {
  const { $ui } = useNuxtApp()
  $ui.info('联系客服', `请联系客服处理订单：${orderNo}`)
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 页面挂载时加载数据
onMounted(() => {
  loadQueryHistory()
})
</script>

<style scoped>
/* 确保内容不被底部菜单栏遮挡 */
.pb-20 {
  padding-bottom: 5rem; /* 80px */
}
</style> 
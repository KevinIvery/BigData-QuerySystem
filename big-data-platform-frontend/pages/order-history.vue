<template>
  <div class="min-h-screen bg-gray-50 pb-20">
    <!-- Header -->
    <div class="sticky top-0 z-10 bg-white border-b border-gray-200 px-4 py-3">
      <div class="flex items-center">
        <button @click="$router.back()" class="mr-3 p-2 -ml-2 text-gray-600">
          <Icon name="ph:arrow-left-bold" class="w-6 h-6" />
        </button>
        <h1 class="text-lg font-semibold text-gray-900">订单历史</h1>
      </div>
    </div>

    <!-- Content -->
    <div class="px-4 py-4">
      <!-- Order List -->
      <div v-if="orders.length > 0" class="space-y-3">
        <div 
          v-for="order in orders" 
          :key="order.id"
          class="bg-white rounded-lg shadow-sm border border-gray-200 p-4"
        >
          <!-- Order Header -->
          <div class="flex justify-between items-start mb-3">
            <div>
              <div class="text-sm text-gray-500">订单号</div>
              <div class="font-mono text-sm text-gray-900">{{ order.order_no }}</div>
            </div>
            <div class="text-right">
              <div class="text-sm text-gray-500">金额</div>
              <div class="font-semibold text-lg text-gray-900">¥{{ order.amount.toFixed(2) }}</div>
            </div>
          </div>

          <!-- Order Details -->
          <div class="grid grid-cols-2 gap-4 mb-3">
            <div>
              <div class="text-xs text-gray-500 mb-1">查询类型</div>
              <div class="text-sm text-gray-900">{{ order.query_type }}</div>
            </div>
            <div>
              <div class="text-xs text-gray-500 mb-1">支付方式</div>
              <div class="text-sm text-gray-900">
                <span v-if="order.payment_method === 'alipay'" class="inline-flex items-center">
                  <Icon name="simple-icons:alipay" class="w-4 h-4 mr-1 text-blue-500" />
                  支付宝
                </span>
                <span v-else-if="order.payment_method === 'wechat'" class="inline-flex items-center">
                  <Icon name="simple-icons:wechat" class="w-4 h-4 mr-1 text-green-500" />
                  微信支付
                </span>
                <span v-else class="text-gray-400">-</span>
              </div>
            </div>
          </div>

          <!-- Status and Time -->
          <div class="flex justify-between items-center">
            <div>
              <span 
                :class="{
                  'bg-yellow-100 text-yellow-800': order.status === 'pending',
                  'bg-blue-100 text-blue-800': order.status === 'paid',
                  'bg-purple-100 text-purple-800': order.status === 'querying',
                  'bg-green-100 text-green-800': order.status === 'completed',
                  'bg-red-100 text-red-800': order.status === 'failed',
                  'bg-gray-100 text-gray-800': order.status === 'cancelled',
                  'bg-orange-100 text-orange-800': order.status === 'refunded'
                }"
                class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              >
                {{ order.status_text }}
              </span>
            </div>
            <div class="text-xs text-gray-500">
              {{ formatDateTime(order.created_at) }}
            </div>
          </div>

          <!-- Actions -->
          <div v-if="order.status === 'completed'" class="mt-3 pt-3 border-t border-gray-100">
            <button 
              @click="viewQueryResult(order.order_no)"
              class="w-full bg-blue-50 text-blue-600 py-2 px-4 rounded-lg text-sm font-medium hover:bg-blue-100 transition-colors"
            >
              查看报告
            </button>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else-if="!isLoading" class="text-center py-16">
        <Icon name="ph:receipt-duotone" class="w-16 h-16 text-gray-300 mx-auto mb-4" />
        <h3 class="text-lg font-medium text-gray-900 mb-2">暂无订单记录</h3>
        <p class="text-gray-500 mb-6">您还没有任何订单记录</p>
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
              <div class="h-4 bg-gray-200 rounded w-32"></div>
            </div>
            <div class="text-right">
              <div class="h-3 bg-gray-200 rounded w-12 mb-2"></div>
              <div class="h-6 bg-gray-200 rounded w-20"></div>
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4 mb-3">
            <div class="h-12 bg-gray-200 rounded"></div>
            <div class="h-12 bg-gray-200 rounded"></div>
          </div>
          <div class="flex justify-between items-center">
            <div class="h-6 bg-gray-200 rounded w-16"></div>
            <div class="h-4 bg-gray-200 rounded w-24"></div>
          </div>
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
const orders = ref([])
const isLoading = ref(false)
const isLoadingMore = ref(false)
const hasMore = ref(true)
const currentPage = ref(1)
const pageSize = 10

// 页面标题
useHead({
  title: '订单历史'
})

// 加载订单历史
const loadOrderHistory = async (page = 1, append = false) => {
  try {
    if (page === 1) {
      isLoading.value = true
    } else {
      isLoadingMore.value = true
    }

    const api = useApi()
    const response = await api.get('/frontend/order-history/', {
      page,
      page_size: pageSize
    })

    const { order_history, pagination } = response.data
    
    if (append) {
      orders.value.push(...order_history)
    } else {
      orders.value = order_history
    }

    hasMore.value = pagination.has_next
    currentPage.value = pagination.current_page

  } catch (error) {
    console.error('加载订单历史异常:', error)
    // 错误已由API工具自动处理
  } finally {
    isLoading.value = false
    isLoadingMore.value = false
  }
}

// 加载更多
const loadMore = () => {
  if (hasMore.value && !isLoadingMore.value) {
    loadOrderHistory(currentPage.value + 1, true)
  }
}

// 查看查询结果
const viewQueryResult = (orderNo) => {
  router.push(`/query-result/${orderNo}`)
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
  loadOrderHistory()
})
</script>

<style scoped>
/* 确保内容不被底部菜单栏遮挡 */
.pb-20 {
  padding-bottom: 5rem; /* 80px */
}
</style> 
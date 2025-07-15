<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- 页面标题 -->
    <div class="bg-white shadow rounded-lg p-6 mb-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">订单记录</h1>
          <p class="mt-2 text-sm text-gray-600">查看您的订单记录和佣金收益情况</p>
        </div>
        <div class="flex items-center space-x-2">
          <span class="text-sm text-gray-500">共计 {{ pagination.total_items }} 个订单</span>
        </div>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="bg-white shadow rounded-lg p-6 mb-6">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- 订单号搜索 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">订单号搜索</label>
          <input
            v-model="searchForm.search"
            type="text"
            placeholder="请输入订单号"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
            @keyup.enter="handleSearch"
          />
        </div>
        
        <!-- 日期范围 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">时间范围</label>
          <select
            v-model="searchForm.date_range"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
            @change="handleSearch"
          >
            <option value="all">全部时间</option>
            <option value="today">今日</option>
            <option value="7d">近7天</option>
            <option value="15d">近15天</option>
            <option value="30d">近30天</option>
          </select>
        </div>

        <!-- 订单状态 -->
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">订单状态</label>
          <select
            v-model="searchForm.status"
            class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
            @change="handleSearch"
          >
            <option value="">全部状态</option>
            <option value="pending">待支付</option>
            <option value="paid">已支付</option>
            <option value="querying">查询中</option>
            <option value="completed">查询完成</option>
            <option value="failed">查询失败</option>
            <option value="cancelled">已取消</option>
            <option value="refunded">已退款</option>
          </select>
        </div>

        <!-- 搜索按钮 -->
        <div class="flex items-end">
          <button
            @click="handleSearch"
            class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            <Icon name="ri:search-line" class="w-4 h-4 mr-2" />
            搜索
          </button>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="bg-white shadow rounded-lg overflow-hidden">
      <!-- 加载状态 -->
      <div v-if="loading" class="p-12 text-center">
        <div class="inline-flex items-center">
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <span class="text-gray-600">正在加载数据...</span>
        </div>
      </div>

      <!-- 表格 -->
      <div v-else>
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                订单信息
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                用户/查询类型
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                付费价格
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                佣金收益
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                状态
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                创建时间
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <!-- 无数据状态 -->
            <tr v-if="!orders.length">
              <td colspan="6" class="px-6 py-12 text-center">
                <div class="text-gray-400">
                  <svg class="mx-auto h-12 w-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  <p class="text-sm">暂无订单记录</p>
                </div>
              </td>
            </tr>
            
            <!-- 数据行 -->
            <tr v-for="order in orders" :key="order.id" class="hover:bg-gray-50">
              <!-- 订单信息 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ order.order_no }}</div>
                <div class="text-sm text-gray-500">
                  <span v-if="order.payment_method_display">{{ order.payment_method_display }}</span>
                  <span v-else>未知支付方式</span>
                </div>
              </td>
              
              <!-- 用户/查询类型 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ order.username }}</div>
                <div class="text-sm text-gray-500">{{ order.query_type }}</div>
              </td>
              
              <!-- 付费价格 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">¥{{ order.amount.toFixed(2) }}</div>
              </td>
              
              <!-- 佣金收益 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-green-600">¥{{ order.agent_commission.toFixed(2) }}</div>
              </td>
              
              <!-- 状态 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                      :class="getStatusClass(order.status)">
                  {{ order.status_display }}
                </span>
              </td>
              
              <!-- 创建时间 -->
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDateTime(order.created_at) }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div v-if="!loading && orders.length" class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
        <div class="flex items-center justify-between">
          <div class="flex-1 flex justify-between sm:hidden">
            <button
              @click="changePage(pagination.current_page - 1)"
              :disabled="!pagination.has_previous"
              class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              上一页
            </button>
            <button
              @click="changePage(pagination.current_page + 1)"
              :disabled="!pagination.has_next"
              class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              下一页
            </button>
          </div>
          
          <!-- 桌面版分页 -->
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                显示第
                <span class="font-medium">{{ (pagination.current_page - 1) * pagination.page_size + 1 }}</span>
                -
                <span class="font-medium">{{ Math.min(pagination.current_page * pagination.page_size, pagination.total_items) }}</span>
                条，共
                <span class="font-medium">{{ pagination.total_items }}</span>
                条记录
              </p>
            </div>
            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                <!-- 上一页 -->
                <button
                  @click="changePage(pagination.current_page - 1)"
                  :disabled="!pagination.has_previous"
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span class="sr-only">上一页</span>
                  <Icon name="ri:arrow-left-s-line" class="h-5 w-5" />
                </button>

                <!-- 页码 -->
                <button
                  v-for="page in visiblePages"
                  :key="page"
                  @click="changePage(page)"
                  :class="[
                    'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                    page === pagination.current_page
                      ? 'z-10 bg-green-50 border-green-500 text-green-600'
                      : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                  ]"
                >
                  {{ page }}
                </button>

                <!-- 下一页 -->
                <button
                  @click="changePage(pagination.current_page + 1)"
                  :disabled="!pagination.has_next"
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span class="sr-only">下一页</span>
                  <Icon name="ri:arrow-right-s-line" class="h-5 w-5" />
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const { $ui } = useNuxtApp()
const api = useApi()

// 响应式数据
const loading = ref(true)
const orders = ref([])
const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total_items: 0,
  page_size: 20,
  has_next: false,
  has_previous: false
})

// 搜索表单
const searchForm = ref({
  search: '',
  date_range: 'all',
  status: ''
})

// 计算可见页码
const visiblePages = computed(() => {
  const current = pagination.value.current_page
  const total = pagination.value.total_pages
  const pages = []
  
  // 最多显示5个页码
  let start = Math.max(1, current - 2)
  let end = Math.min(total, start + 4)
  
  // 调整开始位置
  if (end - start < 4) {
    start = Math.max(1, end - 4)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// 获取订单状态样式
const getStatusClass = (status) => {
  const statusMap = {
    'pending': 'bg-yellow-100 text-yellow-800',
    'paid': 'bg-blue-100 text-blue-800',
    'querying': 'bg-purple-100 text-purple-800',
    'completed': 'bg-green-100 text-green-800',
    'failed': 'bg-red-100 text-red-800',
    'cancelled': 'bg-gray-100 text-gray-800',
    'refunded': 'bg-orange-100 text-orange-800'
  }
  return statusMap[status] || 'bg-gray-100 text-gray-800'
}

// 获取订单列表
const fetchOrders = async (page = 1) => {
  try {
    loading.value = true
    
    const response = await api.get('/agent/orders/', {
      params: {
        page,
        page_size: pagination.value.page_size,
        search: searchForm.value.search,
        date_range: searchForm.value.date_range,
        status: searchForm.value.status
      }
    })
    
    if (response.code === 0) {
      orders.value = response.data.items || []
      pagination.value = response.data.pagination || pagination.value
    } else {
      $ui.error('获取失败', response.message || '获取订单记录失败')
    }
  } catch (error) {
    console.error('获取订单记录失败:', error)
    $ui.error('获取失败', '网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 处理搜索
const handleSearch = () => {
  fetchOrders(1) // 重置到第一页
}

// 切换页码
const changePage = (page) => {
  if (page >= 1 && page <= pagination.value.total_pages) {
    fetchOrders(page)
  }
}

// 格式化日期时间
const formatDateTime = (dateTimeStr) => {
  try {
    const date = new Date(dateTimeStr)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return dateTimeStr
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
/* 表格自适应 */
@media (max-width: 640px) {
  table {
    font-size: 0.875rem;
  }
  
  th, td {
    padding: 0.75rem 0.5rem;
  }
}
</style> 
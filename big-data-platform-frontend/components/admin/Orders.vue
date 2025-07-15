<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="md:flex md:items-center md:justify-between">
      <div class="flex-1 min-w-0">
        <h1 class="text-3xl font-light text-gray-900">订单记录管理</h1>
        <p class="mt-2 text-base text-gray-600">查看和管理用户订单记录</p>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="bg-white border border-gray-200 rounded-lg">
      <div class="flex flex-wrap items-end gap-4 p-6">
        <!-- 搜索订单号/用户名 -->
        <div class="flex flex-col space-y-1 min-w-0 flex-1 max-w-xs">
          <label for="search" class="text-sm font-medium text-gray-700">
            搜索关键词
          </label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Icon name="clarity:search-line" class="h-5 w-5 text-gray-400" />
            </div>
            <input
              id="search"
              v-model="filters.search"
              type="text"
              placeholder="订单号或用户名"
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent sm:text-sm"
            />
          </div>
        </div>

        <!-- 代理搜索 -->
        <div class="flex flex-col space-y-1 min-w-0 max-w-xs">
          <label for="agent_search" class="text-sm font-medium text-gray-700">
            代理搜索
          </label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Icon name="clarity:user-line" class="h-5 w-5 text-gray-400" />
            </div>
            <input
              id="agent_search"
              v-model="filters.agent_search"
              type="text"
              placeholder="代理用户名/手机号"
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent sm:text-sm"
            />
          </div>
        </div>

        <!-- 日期范围 -->
        <div class="flex flex-col space-y-1 min-w-0">
          <label for="date_range" class="text-sm font-medium text-gray-700">
            日期范围
          </label>
          <select
            id="date_range"
            v-model="filters.date_range"
            class="block w-auto px-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent sm:text-sm"
          >
            <option value="all">全部</option>
            <option value="today">今日</option>
            <option value="7d">近七天</option>
            <option value="6m">半年</option>
          </select>
        </div>

        <!-- 支付方式 -->
        <div class="flex flex-col space-y-1 min-w-0">
          <label for="payment_method" class="text-sm font-medium text-gray-700">
            支付方式
          </label>
          <select
            id="payment_method"
            v-model="filters.payment_method"
            class="block w-auto px-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent sm:text-sm"
          >
            <option value="">全部</option>
            <option value="alipay">支付宝</option>
            <option value="wechat">微信支付</option>
          </select>
        </div>

        <!-- 订单状态 -->
        <div class="flex flex-col space-y-1 min-w-0">
          <label for="status" class="text-sm font-medium text-gray-700">
            订单状态
          </label>
          <select
            id="status"
            v-model="filters.status"
            class="block w-auto px-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent sm:text-sm"
          >
            <option value="">全部状态</option>
            <option value="pending">待支付</option>
            <option value="paid">已支付</option>
            <option value="querying">查询中</option>
            <option value="completed">查询完成</option>
            <option value="failed">查询失败</option>
            <option value="cancelled">已取消</option>
          </select>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <!-- 加载状态 -->
      <div v-if="loading" class="p-8 text-center">
        <Icon name="clarity:refresh-line" class="w-8 h-8 text-gray-400 animate-spin mx-auto" />
        <p class="mt-3 text-sm text-gray-500">正在加载订单列表...</p>
      </div>

      <!-- 空状态 -->
      <div v-else-if="orders.length === 0" class="p-8 text-center">
        <Icon name="clarity:receipt-line" class="w-16 h-16 text-gray-300 mx-auto" />
        <h3 class="mt-4 text-lg font-medium text-gray-900">暂无订单记录</h3>
        <p class="mt-2 text-sm text-gray-500">没有找到符合条件的订单记录</p>
      </div>

      <!-- 表格内容 -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                订单信息
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                用户信息
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                支付信息
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                订单状态
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                金额信息
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                创建时间
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody class="bg-white">
            <tr v-for="item in orders" :key="item.id" class="border-b border-gray-100 hover:bg-gray-50 transition-colors duration-150">
              <!-- 订单信息 -->
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900 font-mono" :title="item.order_no">
                  {{ truncateOrderNo(item.order_no) }}
                </div>
                <div class="text-sm text-gray-500 mt-1">{{ item.query_type }}</div>
              </td>

              <!-- 用户信息 -->
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">{{ item.username }}</div>
                <div v-if="item.agent_info" class="text-sm text-blue-600 mt-1">
                  代理: {{ item.agent_info.username }}
                </div>
              </td>

              <!-- 支付信息 -->
              <td class="px-6 py-4">
                <span class="px-3 py-1 inline-flex text-xs font-medium rounded-full border"
                      :class="[
                        item.payment_method === 'alipay' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                        item.payment_method === 'wechat' ? 'bg-green-50 text-green-700 border-green-200' :
                        'bg-gray-50 text-gray-700 border-gray-200'
                      ]">
                  {{ item.payment_method_display }}
                </span>
                <div v-if="item.payment_time" class="text-xs text-gray-500 mt-1">
                  {{ formatDate(item.payment_time) }}
                </div>
              </td>

              <!-- 订单状态 -->
              <td class="px-6 py-4">
                <span class="px-3 py-1 inline-flex text-xs font-medium rounded-full border"
                      :class="[
                        item.status === 'completed' ? 'bg-green-50 text-green-700 border-green-200' :
                        item.status === 'failed' ? 'bg-red-50 text-red-700 border-red-200' :
                        item.status === 'querying' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' :
                        item.status === 'paid' ? 'bg-blue-50 text-blue-700 border-blue-200' :
                        item.status === 'pending' ? 'bg-gray-50 text-gray-700 border-gray-200' :
                        'bg-red-50 text-red-700 border-red-200'
                      ]">
                  {{ item.status_display }}
                </span>
              </td>

              <!-- 金额信息 -->
              <td class="px-6 py-4 text-sm text-gray-900">
                <div class="font-medium">¥{{ item.amount }}</div>
                <div v-if="item.agent_info" class="text-blue-600 text-xs mt-1">
                  代理佣金+ {{ Number(item.agent_commission).toFixed(2) }}
                </div>
              </td>

              <!-- 创建时间 -->
              <td class="px-6 py-4 text-sm text-gray-600">
                {{ formatDate(item.created_at) }}
              </td>

              <!-- 操作 -->
              <td class="px-6 py-4 text-sm font-medium">
                <button
                  v-if="item.status === 'paid' || item.status === 'completed'"
                  @click="showRefundModal(item)"
                  :disabled="refunding === item.id"
                  class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-orange-600 hover:text-orange-700 hover:bg-orange-50 rounded-lg transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Icon v-if="refunding === item.id" name="clarity:refresh-line" class="w-4 h-4 mr-1 animate-spin" />
                  <Icon v-else name="clarity:refresh-line" class="w-4 h-4 mr-1" />
                  {{ refunding === item.id ? '退款中...' : '退款' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div v-if="total > 0" class="px-6 py-4 border-t border-gray-200 flex items-center justify-between bg-gray-50">
        <div class="flex items-center text-sm text-gray-700">
          <span>显示第 {{ (currentPage - 1) * pageSize + 1 }} 到 {{ Math.min(currentPage * pageSize, total) }} 条，共 {{ total }} 条</span>
        </div>
        <div v-if="totalPages > 1" class="flex items-center space-x-2">
          <button
            @click="changePage(currentPage - 1)"
            :disabled="currentPage <= 1"
            class="px-4 py-2 text-sm font-medium border border-gray-300 rounded-lg hover:bg-white transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            上一页
          </button>
          <span class="px-4 py-2 text-sm text-gray-700 font-medium">
            {{ currentPage }} / {{ totalPages }}
          </span>
          <button
            @click="changePage(currentPage + 1)"
            :disabled="currentPage >= totalPages"
            class="px-4 py-2 text-sm font-medium border border-gray-300 rounded-lg hover:bg-white transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一页
          </button>
        </div>
      </div>
    </div>

    <!-- 退款弹窗 -->
    <Teleport to="body">
      <div v-if="showRefundModalFlag" class="fixed inset-0 z-50 overflow-y-auto">
        <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="closeRefundModal"></div>
          
          <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-orange-100 sm:mx-0 sm:h-10 sm:w-10">
                  <Icon name="clarity:refresh-line" class="h-6 w-6 text-orange-600" />
                </div>
                <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                  <h3 class="text-lg leading-6 font-medium text-gray-900">订单退款</h3>
                  <div class="mt-2">
                    <p class="text-sm text-gray-500">确定要对订单 <strong>{{ truncateOrderNo(currentRefundOrder?.order_no) }}</strong> 进行退款吗？</p>
                    <div class="mt-4 space-y-3">
                      <div>
                        <label class="block text-sm font-medium text-gray-700">支付方式</label>
                        <input
                          type="text"
                          readonly
                          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
                          :value="currentRefundOrder?.payment_method_display"
                        >
                      </div>
                      <div>
                        <label class="block text-sm font-medium text-gray-700">退款交易号</label>
                        <input
                          type="text"
                          readonly
                          class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 font-mono text-xs"
                          :value="currentRefundOrder?.third_party_trade_no || currentRefundOrder?.third_party_order_id"
                        >
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                @click="confirmRefund"
                :disabled="refunding"
                class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-orange-600 text-base font-medium text-white hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
              >
                <Icon v-if="refunding" name="clarity:refresh-line" class="w-4 h-4 mr-2 animate-spin" />
                {{ refunding ? '退款中...' : '确认退款' }}
              </button>
              <button
                @click="closeRefundModal"
                :disabled="refunding"
                class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50"
              >
                取消
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
const api = useApi()
const { $ui } = useNuxtApp()

// 响应式数据
const orders = ref([])
const loading = ref(false)
const refunding = ref(false)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const totalPages = ref(0)

// 退款相关
const showRefundModalFlag = ref(false)
const currentRefundOrder = ref(null)

// 筛选条件
const filters = ref({
  search: '',
  agent_search: '',
  date_range: 'all',
  payment_method: '',
  status: ''
})

// 计算总页数
const calculateTotalPages = () => {
  totalPages.value = Math.ceil(total.value / pageSize.value)
}

// 截断订单号显示
const truncateOrderNo = (orderNo) => {
  if (!orderNo) return '-'
  if (orderNo.length <= 20) return orderNo
  return orderNo.substring(0, 12) + '...' + orderNo.substring(orderNo.length - 6)
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 获取订单列表
const getOrders = async () => {
  try {
    loading.value = true
    
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...filters.value
    }

    const response = await api.get('/admin/orders/', { params })
    
    if (response.code === 0) {
      orders.value = response.data.items || []
      total.value = response.data.pagination?.total_items || 0
      currentPage.value = response.data.pagination?.current_page || 1
      pageSize.value = response.data.pagination?.page_size || 20
      calculateTotalPages()
    } else {
      $ui.error('获取订单记录失败', response.message)
    }
  } catch (error) {
    console.error('获取订单记录失败:', error)
    $ui.error('获取订单记录失败', '网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 重置页面并搜索
const resetAndSearch = () => {
  currentPage.value = 1
  getOrders()
}

// 切换页面
const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  getOrders()
}

// 显示退款弹窗
const showRefundModal = (order) => {
  currentRefundOrder.value = order
  showRefundModalFlag.value = true
}

// 关闭退款弹窗
const closeRefundModal = () => {
  if (refunding.value) return
  showRefundModalFlag.value = false
  currentRefundOrder.value = null
}

// 确认退款
const confirmRefund = async () => {
  try {
    if (!currentRefundOrder.value) return

    refunding.value = true
    
    const response = await api.post('/admin/orders/refund/', {
      order_id: currentRefundOrder.value.id,
      payment_method: currentRefundOrder.value.payment_method,
      third_party_order_id: currentRefundOrder.value.third_party_order_id,
      third_party_trade_no: currentRefundOrder.value.third_party_trade_no
    })
    
    if (response.code === 0) {
      $ui.success('退款申请提交成功')
      getOrders() // 重新加载数据
    } else {
      $ui.error('退款失败', response.message || '请稍后重试')
    }
  } catch (error) {
    console.error('退款失败:', error)
    $ui.error('退款失败', '网络错误，请稍后重试')
  } finally {
    refunding.value = false
    closeRefundModal() // 无论成功还是失败都关闭弹窗
  }
}

// 页面初始化
onMounted(() => {
  getOrders()
})

// 搜索防抖定时器
let searchTimeout = null

// 监听筛选条件变化，自动搜索
watch(filters, () => {
  // 防抖处理
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    resetAndSearch()
  }, 500)
}, { deep: true })
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style> 
<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="md:flex md:items-center md:justify-between">
      <div class="flex-1 min-w-0">
        <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          代理仪表盘
        </h2>
        <p class="mt-1 text-sm text-gray-500">
          欢迎回来，{{ userInfo.username }}！以下是您的业务概览信息。
        </p>
      </div>
      <!-- 收款配置状态 -->
      <div class="mt-4 flex md:mt-0 md:ml-4">
        <div v-if="paymentConfigStatus !== null" class="flex items-center space-x-2">
          <div class="flex items-center">
            <div
              :class="[
                'h-2 w-2 rounded-full mr-2',
                paymentConfigStatus ? 'bg-green-500' : 'bg-red-500'
              ]"
            ></div>
            <span class="text-sm text-gray-600">
              收款配置{{ paymentConfigStatus ? '已完成' : '未配置' }}
            </span>
          </div>
          <button
            v-if="!paymentConfigStatus"
            @click="showPaymentConfigModal"
            class="inline-flex items-center px-3 py-1 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
          >
            立即配置
          </button>
          <button
            v-else
            @click="showPaymentConfigModal"
            class="inline-flex items-center px-3 py-1 border border-gray-300 text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
          >
            查看配置
          </button>
        </div>
      </div>
    </div>

    <!-- 佣金统计卡片 -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <!-- 累计收益 -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <Icon name="clarity:dollar-line" class="h-6 w-6 text-green-500" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">累计收益</dt>
                <dd class="text-lg font-medium text-green-600">¥{{ dashboardStats?.commission_stats?.total_profit || '0.00' }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- 累计佣金 -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <Icon name="clarity:coin-bag-line" class="h-6 w-6 text-blue-500" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">累计佣金</dt>
                <dd class="text-lg font-medium text-blue-600">¥{{ dashboardStats?.commission_stats?.total_commission || '0.00' }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- 未结算佣金 -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <Icon name="clarity:clock-line" class="h-6 w-6 text-yellow-500" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">未结算佣金</dt>
                <dd class="text-lg font-medium text-yellow-600">¥{{ dashboardStats?.commission_stats?.unsettled_commission || '0.00' }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- 已结算佣金 -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <Icon name="clarity:check-circle-line" class="h-6 w-6 text-green-500" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">已结算佣金</dt>
                <dd class="text-lg font-medium text-green-600">¥{{ dashboardStats?.commission_stats?.settled_commission || '0.00' }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 用户和订单统计卡片 -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <!-- 客户总数 -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <Icon name="clarity:users-line" class="h-6 w-6 text-gray-500" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">客户总数</dt>
                <dd class="text-lg font-medium text-gray-900">{{ dashboardStats?.user_stats?.total_users || 0 }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- 今日新增客户 -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <Icon name="clarity:user-add-line" class="h-6 w-6 text-blue-500" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">今日新增客户</dt>
                <dd class="text-lg font-medium text-blue-600">{{ dashboardStats?.user_stats?.today_new_users || 0 }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- 累计订单 -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <Icon name="clarity:shopping-cart-line" class="h-6 w-6 text-purple-500" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">累计订单</dt>
                <dd class="text-lg font-medium text-purple-600">{{ dashboardStats?.order_stats?.total_orders || 0 }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- 今日订单 -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <Icon name="clarity:calendar-line" class="h-6 w-6 text-green-500" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">今日订单</dt>
                <dd class="text-lg font-medium text-green-600">{{ dashboardStats?.order_stats?.today_orders || 0 }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表展示区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 近30天用户新增趋势 -->
      <div class="bg-white shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">近30天用户新增趋势</h3>
        <div class="h-64">
          <canvas ref="userChartCanvas"></canvas>
        </div>
      </div>

      <!-- 近30天订单趋势 -->
      <div class="bg-white shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">近30天订单趋势</h3>
        <div class="h-64">
          <canvas ref="orderChartCanvas"></canvas>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">快速操作</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            @click="$emit('menu-select', { key: 'commission-details' })"
            class="relative group bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-green-500 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div>
              <span class="rounded-lg inline-flex p-3 bg-green-50 text-green-600 group-hover:bg-green-100">
                <Icon name="clarity:coin-bag-line" class="h-6 w-6" />
              </span>
            </div>
            <div class="mt-4">
              <h3 class="text-sm font-medium text-gray-900">
                <span class="absolute inset-0" aria-hidden="true"></span>
                佣金明细
              </h3>
              <p class="mt-2 text-sm text-gray-500">
                查看佣金收益和申请提现
              </p>
            </div>
          </button>

          <button
            @click="$emit('menu-select', { key: 'orders' })"
            class="relative group bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-green-500 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div>
              <span class="rounded-lg inline-flex p-3 bg-blue-50 text-blue-600 group-hover:bg-blue-100">
                <Icon name="clarity:shopping-cart-line" class="h-6 w-6" />
              </span>
            </div>
            <div class="mt-4">
              <h3 class="text-sm font-medium text-gray-900">
                <span class="absolute inset-0" aria-hidden="true"></span>
                订单管理
              </h3>
              <p class="mt-2 text-sm text-gray-500">
                查看和管理所有订单信息
              </p>
            </div>
          </button>

          <button
            @click="showPaymentConfigModal"
            class="relative group bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-green-500 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div>
              <span class="rounded-lg inline-flex p-3 bg-purple-50 text-purple-600 group-hover:bg-purple-100">
                <Icon name="clarity:wallet-line" class="h-6 w-6" />
              </span>
            </div>
            <div class="mt-4">
              <h3 class="text-sm font-medium text-gray-900">
                <span class="absolute inset-0" aria-hidden="true"></span>
                收款配置
              </h3>
              <p class="mt-2 text-sm text-gray-500">
                配置提现收款方式
              </p>
            </div>
          </button>

          <button
            @click="$emit('menu-select', { key: 'system-config' })"
            class="relative group bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-green-500 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div>
              <span class="rounded-lg inline-flex p-3 bg-yellow-50 text-yellow-600 group-hover:bg-yellow-100">
                <Icon name="clarity:settings-line" class="h-6 w-6" />
              </span>
            </div>
            <div class="mt-4">
              <h3 class="text-sm font-medium text-gray-900">
                <span class="absolute inset-0" aria-hidden="true"></span>
                系统设置
              </h3>
              <p class="mt-2 text-sm text-gray-500">
                配置您的网站和系统参数
              </p>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- 收款配置组件 -->
    <AgentPaymentConfig
      v-if="showPaymentConfig"
      @close="showPaymentConfig = false"
      @saved="handlePaymentConfigSaved"
    />
  </div>
</template>

<script setup>
const props = defineProps({
  userInfo: {
    type: Object,
    default: () => ({
      username: '代理用户',
      domain_suffix: 'agent'
    })
  }
})

const emit = defineEmits(['menu-select'])
const { $ui } = useNuxtApp()
const api = useApi()

// 响应式数据
const dashboardStats = ref(null)
const paymentConfigStatus = ref(null)
const showPaymentConfig = ref(false)
const userChartCanvas = ref(null)
const orderChartCanvas = ref(null)
const userChart = ref(null)
const orderChart = ref(null)

// 获取仪表盘统计数据
const getDashboardStats = async () => {
  try {
    $ui.showLoading('正在加载统计数据...')
    
    const response = await api.get('/agent/dashboard/stats/')
    
    if (response.code === 0) {
      dashboardStats.value = response.data
      console.log('仪表盘统计数据:', dashboardStats.value)
      
      // 数据加载完成后初始化图表
      await nextTick()
      await initCharts()
    } else {
      $ui.error('获取统计数据失败', response.message)
    }
  } catch (error) {
    console.error('获取仪表盘统计数据失败:', error)
    $ui.error('获取统计数据失败', '网络错误，请稍后重试')
  } finally {
    $ui.hideLoading()
  }
}

// 获取收款配置状态
const getPaymentConfigStatus = async () => {
  try {
    const response = await api.get('/agent/payment-config/')
    
    if (response.code === 0) {
      paymentConfigStatus.value = response.data.configured
      console.log('收款配置状态:', paymentConfigStatus.value)
      
      // 如果未配置，显示提示弹窗
      if (!paymentConfigStatus.value) {
        await nextTick()
        showPaymentConfigPrompt()
      }
    }
  } catch (error) {
    console.error('获取收款配置状态失败:', error)
  }
}

// 显示收款配置提示
const showPaymentConfigPrompt = () => {
  $ui.showConfirm({
    title: '收款配置提醒',
    message: '您还未配置收款信息，为确保佣金能正常提现，建议立即配置收款方式。',
    confirmText: '立即配置',
    cancelText: '稍后配置',
    onConfirm: () => {
      showPaymentConfigModal()
    },
    onCancel: () => {
      console.log('用户选择稍后配置')
    }
  })
}

// 显示收款配置弹窗
const showPaymentConfigModal = () => {
  showPaymentConfig.value = true
}

// 处理收款配置保存完成
const handlePaymentConfigSaved = () => {
  showPaymentConfig.value = false
  paymentConfigStatus.value = true
  $ui.success('收款配置保存成功')
}

// 初始化图表
const initCharts = async () => {
  if (!dashboardStats.value) return
  
  try {
    const { Chart, registerables } = await import('chart.js')
    Chart.register(...registerables)
    
    // 初始化用户新增趋势图表
    initUserChart(Chart)
    
    // 初始化订单趋势图表
    initOrderChart(Chart)
    
  } catch (error) {
    console.error('初始化图表失败:', error)
  }
}

// 初始化用户新增趋势图表
const initUserChart = (Chart) => {
  if (!userChartCanvas.value) return
  
  const userData = dashboardStats.value.user_stats.daily_users_30d || []
  const labels = userData.map(item => {
    const date = new Date(item.date)
    return `${date.getMonth() + 1}/${date.getDate()}`
  })
  const data = userData.map(item => item.new_users)
  
  // 销毁现有图表
  if (userChart.value) {
    userChart.value.destroy()
  }
  
  const ctx = userChartCanvas.value.getContext('2d')
  userChart.value = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: '新增用户',
        data: data,
        borderColor: 'rgb(59, 130, 246)',
        backgroundColor: 'rgba(59, 130, 246, 0.1)',
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
        }
      }
    }
  })
}

// 初始化订单趋势图表
const initOrderChart = (Chart) => {
  if (!orderChartCanvas.value) return
  
  const orderData = dashboardStats.value.order_stats.daily_orders_30d || []
  const labels = orderData.map(item => {
    const date = new Date(item.date)
    return `${date.getMonth() + 1}/${date.getDate()}`
  })
  const orders = orderData.map(item => item.orders)
  const refunds = orderData.map(item => item.refunds)
  
  // 销毁现有图表
  if (orderChart.value) {
    orderChart.value.destroy()
  }
  
  const ctx = orderChartCanvas.value.getContext('2d')
  orderChart.value = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: '订单量',
          data: orders,
          backgroundColor: 'rgba(34, 197, 94, 0.8)',
          borderColor: 'rgb(34, 197, 94)',
          borderWidth: 1
        },
        {
          label: '退款量',
          data: refunds,
          backgroundColor: 'rgba(239, 68, 68, 0.8)',
          borderColor: 'rgb(239, 68, 68)',
          borderWidth: 1
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top'
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            stepSize: 1
          }
        }
      }
    }
  })
}

// 页面加载时获取数据
onMounted(async () => {
  await Promise.all([
    getDashboardStats(),
    getPaymentConfigStatus()
  ])
})

// 页面卸载时销毁图表
onUnmounted(() => {
  if (userChart.value) {
    userChart.value.destroy()
  }
  if (orderChart.value) {
    orderChart.value.destroy()
  }
})
</script> 
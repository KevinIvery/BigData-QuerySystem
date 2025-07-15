<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="md:flex md:items-center md:justify-between">
      <div class="flex-1 min-w-0">
        <h2 class="text-3xl font-light leading-7 text-gray-900 sm:truncate">
          仪表盘
        </h2>
        <p class="mt-1 text-base text-gray-600">
          欢迎回来，{{ userInfo.username }}！以下是系统概览信息。
        </p>
      </div>
      <div class="mt-4 flex md:mt-0 md:ml-4">
        <button
          @click="refreshStats"
          :disabled="loading"
          class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          <Icon name="clarity:refresh-line" :class="['w-4 h-4 mr-2', { 'animate-spin': loading }]" />
          刷新数据
        </button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
      <!-- 用户总数 -->
      <div class="bg-white overflow-hidden border border-gray-200 rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <Icon name="clarity:users-line" class="h-8 w-8 text-blue-500" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">用户总数</dt>
                <dd class="text-2xl font-bold text-gray-900">{{ stats.users?.total_users || 0 }}</dd>
                <dd class="text-sm text-green-600">今日新增: {{ stats.users?.today_new_users || 0 }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- 查询总数 -->
      <div class="bg-white overflow-hidden border border-gray-200 rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <Icon name="clarity:search-line" class="h-8 w-8 text-green-500" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">查询总数</dt>
                <dd class="text-2xl font-bold text-gray-900">{{ stats.queries?.total_queries || 0 }}</dd>
                <dd class="text-sm text-green-600">今日查询: {{ stats.queries?.today_queries || 0 }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- 订单总数 -->
      <div class="bg-white overflow-hidden border border-gray-200 rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <Icon name="clarity:shopping-cart-line" class="h-8 w-8 text-purple-500" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">订单总数</dt>
                <dd class="text-2xl font-bold text-gray-900">{{ stats.orders?.total_orders || 0 }}</dd>
                <dd class="text-sm text-green-600">今日订单: {{ stats.orders?.today_orders || 0 }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- 总收入 -->
      <div class="bg-white overflow-hidden border border-gray-200 rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <Icon name="clarity:coin-bag-line" class="h-8 w-8 text-yellow-500" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">总收入</dt>
                <dd class="text-2xl font-bold text-gray-900">¥{{ formatNumber(stats.revenue?.total_revenue || 0) }}</dd>
                <dd class="text-sm text-green-600">今日收入: ¥{{ formatNumber(stats.revenue?.today_revenue || 0) }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 用户来源分布 -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">用户来源分布</h3>
        <div class="h-64">
          <canvas ref="userSourceChart"></canvas>
        </div>
      </div>

      <!-- 查询类型分布 -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">查询类型分布</h3>
        <div class="h-64">
          <canvas ref="queryTypeChart"></canvas>
        </div>
      </div>

      <!-- 订单状态分析 -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">订单状态分析</h3>
        <div class="h-64">
          <canvas ref="orderStatusChart"></canvas>
        </div>
      </div>

      <!-- 支付方式统计 -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">支付方式统计</h3>
        <div class="h-64">
          <canvas ref="paymentMethodChart"></canvas>
        </div>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="bg-white border border-gray-200 rounded-lg">
      <div class="px-6 py-5">
        <h3 class="text-lg leading-6 font-semibold text-gray-900 mb-4">快速操作</h3>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <button
            @click="$emit('menu-select', { key: 'users' })"
            class="relative group bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div>
              <span class="rounded-lg inline-flex p-3 bg-indigo-50 text-indigo-600 group-hover:bg-indigo-100">
                <Icon name="clarity:users-line" class="h-6 w-6" />
              </span>
            </div>
            <div class="mt-4">
              <h3 class="text-sm font-medium text-gray-900">
                <span class="absolute inset-0" aria-hidden="true"></span>
                用户管理
              </h3>
              <p class="mt-2 text-sm text-gray-500">
                管理系统用户账户和权限
              </p>
            </div>
          </button>

          <button
            @click="$emit('menu-select', { key: 'system-config' })"
            class="relative group bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div>
              <span class="rounded-lg inline-flex p-3 bg-green-50 text-green-600 group-hover:bg-green-100">
                <Icon name="clarity:cog-line" class="h-6 w-6" />
              </span>
            </div>
            <div class="mt-4">
              <h3 class="text-sm font-medium text-gray-900">
                <span class="absolute inset-0" aria-hidden="true"></span>
                系统配置
              </h3>
              <p class="mt-2 text-sm text-gray-500">
                配置系统参数和功能设置
              </p>
            </div>
          </button>

          <button
            @click="$emit('menu-select', { key: 'orders' })"
            class="relative group bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div>
              <span class="rounded-lg inline-flex p-3 bg-yellow-50 text-yellow-600 group-hover:bg-yellow-100">
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
            @click="$emit('menu-select', { key: 'query-history' })"
            class="relative group bg-gray-50 p-6 focus-within:ring-2 focus-within:ring-inset focus-within:ring-indigo-500 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div>
              <span class="rounded-lg inline-flex p-3 bg-purple-50 text-purple-600 group-hover:bg-purple-100">
                <Icon name="clarity:history-line" class="h-6 w-6" />
              </span>
            </div>
            <div class="mt-4">
              <h3 class="text-sm font-medium text-gray-900">
                <span class="absolute inset-0" aria-hidden="true"></span>
                查询记录
              </h3>
              <p class="mt-2 text-sm text-gray-500">
                查看用户查询历史记录
              </p>
            </div>
          </button>
        </div>
      </div>
    </div>

    <!-- 详细统计信息 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 用户统计详情 -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">用户统计详情</h3>
        <div class="space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">外部来源用户（手机号）</span>
            <span class="text-sm font-medium text-gray-900">{{ stats.users?.external_users || 0 }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">微信来源用户</span>
            <span class="text-sm font-medium text-gray-900">{{ stats.users?.wechat_users || 0 }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-sm text-gray-600">今日新增用户</span>
            <span class="text-sm font-medium text-green-600">{{ stats.users?.today_new_users || 0 }}</span>
        </div>
      </div>
    </div>

    <!-- 系统状态 -->
      <div class="bg-white border border-gray-200 rounded-lg p-6">
        <h3 class="text-lg font-semibold text-gray-900 mb-4">系统状态</h3>
        <div class="space-y-4">
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-gray-900">API服务状态</span>
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200">
              <svg class="-ml-0.5 mr-1.5 h-2 w-2 text-green-400" fill="currentColor" viewBox="0 0 8 8">
                <circle cx="4" cy="4" r="3"/>
              </svg>
              正常
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-gray-900">数据库连接</span>
            <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-50 text-green-700 border border-green-200">
              <svg class="-ml-0.5 mr-1.5 h-2 w-2 text-green-400" fill="currentColor" viewBox="0 0 8 8">
                <circle cx="4" cy="4" r="3"/>
              </svg>
              正常
            </span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-gray-900">统计数据更新时间</span>
            <span class="text-xs text-gray-500">{{ formatTime(stats.generated_at) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue'

const props = defineProps({
  userInfo: {
    type: Object,
    default: () => ({
      username: '管理员',
      company_name: '系统管理'
    })
  }
})

const emit = defineEmits(['menu-select'])

const api = useApi()
const { $ui } = useNuxtApp()

// 统计数据
const stats = ref({})
const loading = ref(false)

// Chart.js 图表实例
const userSourceChart = ref(null)
const queryTypeChart = ref(null)
const orderStatusChart = ref(null)
const paymentMethodChart = ref(null)

// 图表实例存储
let chartInstances = {}

// 获取统计数据
const fetchStats = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/dashboard/stats/')
    if (response.code === 0) {
      stats.value = response.data
      // 数据更新后重新渲染图表
      await nextTick()
      initCharts()
    } else {
      $ui.error('获取统计数据失败', response.message)
    }
  } catch (error) {
    console.error('获取统计数据失败:', error)
    $ui.error('获取统计数据失败', '网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 刷新统计数据
const refreshStats = () => {
  fetchStats()
}

// 格式化数字
const formatNumber = (num) => {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万'
  }
  return num.toLocaleString()
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '--'
  return new Date(timeStr).toLocaleString()
}

// 初始化图表
const initCharts = async () => {
  try {
    // 动态导入 Chart.js
    const { Chart, registerables } = await import('chart.js')
    Chart.register(...registerables)

    // 销毁已存在的图表
    Object.values(chartInstances).forEach(chart => {
      if (chart) chart.destroy()
    })
    chartInstances = {}

    // 用户来源分布饼图
    if (userSourceChart.value) {
      const userStats = stats.value.users || {}
      chartInstances.userSource = new Chart(userSourceChart.value, {
        type: 'doughnut',
        data: {
          labels: ['微信用户', '外部用户'],
          datasets: [{
            data: [userStats.wechat_users || 0, userStats.external_users || 0],
            backgroundColor: ['#3B82F6', '#10B981'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      })
    }

    // 查询类型分布饼图
    if (queryTypeChart.value) {
      const queryStats = stats.value.queries || {}
      chartInstances.queryType = new Chart(queryTypeChart.value, {
        type: 'doughnut',
        data: {
          labels: ['个人查询', '企业查询'],
          datasets: [{
            data: [
              queryStats.personal_queries?.total || 0,
              queryStats.enterprise_queries?.total || 0
            ],
            backgroundColor: ['#8B5CF6', '#F59E0B'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      })
    }

    // 订单状态分析柱状图
    if (orderStatusChart.value) {
      const orderStats = stats.value.orders?.status_analysis || {}
      chartInstances.orderStatus = new Chart(orderStatusChart.value, {
        type: 'bar',
        data: {
          labels: ['已完成', '待支付', '查询中', '已支付', '失败', '已取消', '已退款'],
          datasets: [{
            label: '订单数量',
            data: [
              orderStats.completed || 0,
              orderStats.pending || 0,
              orderStats.querying || 0,
              orderStats.paid || 0,
              orderStats.failed || 0,
              orderStats.cancelled || 0,
              orderStats.refunded || 0
            ],
            backgroundColor: '#3B82F6',
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                stepSize: 1
              }
            }
          },
          plugins: {
            legend: {
              display: false
            }
          }
        }
      })
    }

    // 支付方式统计饼图
    if (paymentMethodChart.value) {
      const paymentStats = stats.value.orders?.payment_method || {}
      chartInstances.paymentMethod = new Chart(paymentMethodChart.value, {
        type: 'doughnut',
        data: {
          labels: ['支付宝', '微信支付'],
          datasets: [{
            data: [paymentStats.alipay || 0, paymentStats.wechat || 0],
            backgroundColor: ['#1677FF', '#07C160'],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      })
    }

  } catch (error) {
    console.error('初始化图表失败:', error)
  }
}

// 页面加载时获取统计数据
onMounted(() => {
  fetchStats()
})

// 组件销毁时清理图表
onBeforeUnmount(() => {
  Object.values(chartInstances).forEach(chart => {
    if (chart) chart.destroy()
  })
})
</script> 
<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="md:flex md:items-center md:justify-between">
      <div class="flex-1 min-w-0">
        <h2 class="text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate">
          佣金明细
        </h2>
        <p class="mt-1 text-sm text-gray-500">
          管理您的佣金收益、配置收款方式和申请提现
        </p>
      </div>
    </div>

    <!-- 佣金概览卡片 -->
    <div class="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
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
                <dd class="text-lg font-medium text-blue-600">¥{{ commissionStats?.total_commission || '0.00' }}</dd>
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
                <dd class="text-lg font-medium text-yellow-600">¥{{ commissionStats?.unsettled_commission || '0.00' }}</dd>
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
                <dd class="text-lg font-medium text-green-600">¥{{ commissionStats?.settled_commission || '0.00' }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>

      <!-- 提现中金额 -->
      <div class="bg-white overflow-hidden shadow rounded-lg">
        <div class="p-5">
          <div class="flex items-center">
            <div class="flex-shrink-0">
              <Icon name="clarity:hourglass-line" class="h-6 w-6 text-purple-500" />
            </div>
            <div class="ml-5 w-0 flex-1">
              <dl>
                <dt class="text-sm font-medium text-gray-500 truncate">提现中金额</dt>
                <dd class="text-lg font-medium text-purple-600">¥{{ commissionStats?.withdrawing_amount || '0.00' }}</dd>
              </dl>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作区域 -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 收款设置 -->
      <div class="bg-white shadow rounded-lg p-6">
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-lg font-medium text-gray-900">收款设置</h3>
          <div class="flex items-center space-x-2">
            <div
              :class="[
                'h-2 w-2 rounded-full',
                paymentConfigStatus ? 'bg-green-500' : 'bg-red-500'
              ]"
            ></div>
            <span class="text-sm text-gray-600">
              {{ paymentConfigStatus ? '已配置' : '未配置' }}
            </span>
          </div>
        </div>
        
        <div class="space-y-4">
          <p class="text-sm text-gray-500">
            配置您的收款信息以便接收佣金提现。支持支付宝和微信收款。
          </p>
          
          <div v-if="paymentConfigStatus && paymentConfig" class="bg-gray-50 rounded-lg p-4">
            <div class="flex items-center space-x-3">
              <Icon 
                :name="paymentConfig.payment_method === 'alipay' ? 'simple-icons:alipay' : 'simple-icons:wechat'" 
                :class="[
                  'w-6 h-6',
                  paymentConfig.payment_method === 'alipay' ? 'text-blue-600' : 'text-green-600'
                ]"
              />
              <div>
                <p class="text-sm font-medium text-gray-900">
                  {{ paymentConfig.payment_method === 'alipay' ? '支付宝' : '微信支付' }}
                </p>
                <p class="text-sm text-gray-500">{{ paymentConfig.payment_account }}</p>
                <p class="text-sm text-gray-500">{{ paymentConfig.payment_name }}</p>
              </div>
            </div>
          </div>
          
          <button
            @click="showPaymentConfigModal"
            :class="[
              'w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white focus:outline-none focus:ring-2 focus:ring-offset-2',
              paymentConfigStatus 
                ? 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500' 
                : 'bg-red-600 hover:bg-red-700 focus:ring-red-500'
            ]"
          >
            <Icon name="clarity:settings-line" class="w-4 h-4 mr-2" />
            {{ paymentConfigStatus ? '修改配置' : '立即配置' }}
          </button>
        </div>
      </div>

      <!-- 申请提现 -->
      <div class="bg-white shadow rounded-lg p-6">
        <h3 class="text-lg font-medium text-gray-900 mb-4">申请提现</h3>
        
        <div class="space-y-4">
          <div class="bg-blue-50 rounded-lg p-4">
            <p class="text-sm text-blue-800">
              可提现金额：<span class="font-medium">¥{{ commissionStats?.unsettled_commission || '0.00' }}</span>
            </p>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">提现金额</label>
            <div class="relative">
              <span class="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">¥</span>
              <input
                type="number"
                v-model="withdrawalForm.amount"
                :max="parseFloat(commissionStats?.unsettled_commission || '0')"
                min="0"
                step="0.01"
                placeholder="请输入提现金额"
                class="w-full pl-8 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <p class="mt-1 text-xs text-gray-500">
              最低提现金额：¥5.00，当前可提现：¥{{ commissionStats?.unsettled_commission || '0.00' }}
            </p>
          </div>
          
          <button
            @click="submitWithdrawal"
            :disabled="!canWithdraw || withdrawalLoading"
            class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Icon v-if="withdrawalLoading" name="clarity:refresh-line" class="w-4 h-4 mr-2 animate-spin" />
            <Icon v-else name="clarity:wallet-line" class="w-4 h-4 mr-2" />
            {{ withdrawalLoading ? '提交中...' : '申请提现' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 提现记录 -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-6 py-4 border-b border-gray-200">
        <h3 class="text-lg font-medium text-gray-900">提现记录</h3>
      </div>
      
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                申请时间
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                提现金额
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                收款方式
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                状态
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                处理时间
              </th>
              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                备注
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-if="withdrawalRecords.length === 0">
              <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                <Icon name="clarity:inbox-line" class="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p>暂无提现记录</p>
              </td>
            </tr>
            <tr v-for="record in withdrawalRecords" :key="record.id">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                {{ formatDateTime(record.created_at) }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                ¥{{ record.amount }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                <div class="flex items-center">
                  <Icon 
                    :name="record.payment_method === 'alipay' ? 'simple-icons:alipay' : 'simple-icons:wechat'" 
                    :class="[
                      'w-4 h-4 mr-1',
                      record.payment_method === 'alipay' ? 'text-blue-600' : 'text-green-600'
                    ]"
                  />
                  {{ record.payment_method === 'alipay' ? '支付宝' : '微信支付' }}
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span
                  :class="[
                    'inline-flex px-2 py-1 text-xs font-semibold rounded-full',
                    record.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                    record.status === 'completed' ? 'bg-green-100 text-green-800' :
                    'bg-red-100 text-red-800'
                  ]"
                >
                  {{ getStatusText(record.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ record.processed_at ? formatDateTime(record.processed_at) : '-' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ record.admin_remark || '-' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- 分页 -->
      <div v-if="pagination.total > pagination.per_page" class="px-6 py-4 border-t border-gray-200">
        <div class="flex items-center justify-between">
          <div class="text-sm text-gray-700">
            共 {{ pagination.total }} 条记录，第 {{ pagination.current_page }} / {{ Math.ceil(pagination.total / pagination.per_page) }} 页
          </div>
          <div class="flex space-x-2">
            <button
              @click="goToPage(pagination.current_page - 1)"
              :disabled="pagination.current_page <= 1"
              class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              上一页
            </button>
            <button
              @click="goToPage(pagination.current_page + 1)"
              :disabled="pagination.current_page >= Math.ceil(pagination.total / pagination.per_page)"
              class="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              下一页
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 收款配置弹窗 -->
    <AgentPaymentConfig
      v-if="showPaymentConfig"
      @close="showPaymentConfig = false"
      @saved="handlePaymentConfigSaved"
    />
  </div>
</template>

<script setup>
const { $ui } = useNuxtApp()
const api = useApi()

// 响应式数据
const commissionStats = ref(null)
const paymentConfigStatus = ref(false)
const paymentConfig = ref(null)
const showPaymentConfig = ref(false)
const withdrawalRecords = ref([])
const withdrawalLoading = ref(false)

// 提现表单
const withdrawalForm = ref({
  amount: ''
})

// 分页数据
const pagination = ref({
  current_page: 1,
  per_page: 10,
  total: 0
})

// 计算属性
const canWithdraw = computed(() => {
  const amount = parseFloat(withdrawalForm.value.amount)
  const maxAmount = parseFloat(commissionStats.value?.unsettled_commission || '0')
  return paymentConfigStatus.value && 
         amount >= 5 && 
         amount <= maxAmount && 
         !withdrawalLoading.value
})

// 获取佣金统计数据
const getCommissionStats = async () => {
  try {
    const response = await api.get('/agent/dashboard/stats/')
    
    if (response.code === 0) {
      commissionStats.value = response.data.commission_stats
      
      // 计算提现中金额
      const pendingWithdrawals = withdrawalRecords.value
        .filter(record => record.status === 'pending')
        .reduce((sum, record) => sum + parseFloat(record.amount), 0)
      
      if (commissionStats.value) {
        commissionStats.value.withdrawing_amount = pendingWithdrawals.toFixed(2)
      }
    }
  } catch (error) {
    console.error('获取佣金统计失败:', error)
  }
}

// 获取收款配置状态
const getPaymentConfigStatus = async () => {
  try {
    const response = await api.get('/agent/payment-config/')
    
    if (response.code === 0) {
      paymentConfigStatus.value = response.data.configured
      if (response.data.configured) {
        paymentConfig.value = response.data
      }
    }
  } catch (error) {
    console.error('获取收款配置状态失败:', error)
  }
}

// 获取提现记录
const getWithdrawalRecords = async (page = 1) => {
  try {
    const response = await api.get(`/agent/withdrawal/records/?page=${page}&per_page=${pagination.value.per_page}`)
    
    if (response.code === 0) {
      withdrawalRecords.value = response.data.records || []
      pagination.value = {
        current_page: response.data.current_page || 1,
        per_page: response.data.per_page || 10,
        total: response.data.total || 0
      }
      
      // 重新计算提现中金额
      if (commissionStats.value) {
        const pendingWithdrawals = withdrawalRecords.value
          .filter(record => record.status === 'pending')
          .reduce((sum, record) => sum + parseFloat(record.amount), 0)
        commissionStats.value.withdrawing_amount = pendingWithdrawals.toFixed(2)
      }
    }
  } catch (error) {
    console.error('获取提现记录失败:', error)
  }
}

// 显示收款配置弹窗
const showPaymentConfigModal = () => {
  showPaymentConfig.value = true
}

// 处理收款配置保存完成
const handlePaymentConfigSaved = (configData) => {
  showPaymentConfig.value = false
  paymentConfigStatus.value = true
  paymentConfig.value = configData
  $ui.success('收款配置保存成功')
}

// 申请提现
const submitWithdrawal = async () => {
  if (!canWithdraw.value) {
    if (!paymentConfigStatus.value) {
      $ui.warning('请先配置收款信息')
      return
    }
    
    const amount = parseFloat(withdrawalForm.value.amount)
    if (amount < 5) {
      $ui.warning('最低提现金额为¥5.00')
      return
    }
    
    const maxAmount = parseFloat(commissionStats.value?.unsettled_commission || '0')
    if (amount > maxAmount) {
      $ui.warning('提现金额不能超过可提现金额')
      return
    }
    
    return
  }

  try {
    withdrawalLoading.value = true
    
    const response = await api.post('/agent/withdrawal/submit/', {
      amount: parseFloat(withdrawalForm.value.amount)
    })
    
    if (response.code === 0) {
      $ui.success('提现申请提交成功，请等待审核')
      withdrawalForm.value.amount = ''
      
      // 刷新数据
      await Promise.all([
        getCommissionStats(),
        getWithdrawalRecords()
      ])
    } else {
      $ui.error('提现申请失败', response.message)
    }
  } catch (error) {
    console.error('提现申请失败:', error)
    $ui.error('提现申请失败', '网络错误，请稍后重试')
  } finally {
    withdrawalLoading.value = false
  }
}

// 状态文本转换
const getStatusText = (status) => {
  const statusMap = {
    'pending': '待处理',
    'completed': '已完成',
    'rejected': '已拒绝'
  }
  return statusMap[status] || '未知'
}

// 格式化日期时间
const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 分页跳转
const goToPage = (page) => {
  if (page >= 1 && page <= Math.ceil(pagination.value.total / pagination.value.per_page)) {
    getWithdrawalRecords(page)
  }
}

// 页面初始化
onMounted(async () => {
  await Promise.all([
    getCommissionStats(),
    getPaymentConfigStatus(),
    getWithdrawalRecords()
  ])
})
</script> 
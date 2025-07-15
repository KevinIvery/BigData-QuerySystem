<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="flex justify-between items-center">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">代理提现申请</h1>
        <p class="mt-1 text-sm text-gray-500">
          管理代理的佣金提现申请，查看收款信息并进行处理
        </p>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700">搜索代理</label>
            <input
              v-model="filters.search"
              type="text"
              placeholder="代理用户名或手机号"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">申请状态</label>
            <select
              v-model="filters.status"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            >
              <option value="">全部状态</option>
              <option value="pending">待处理</option>
              <option value="completed">已完成</option>
              <option value="rejected">已拒绝</option>
            </select>
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700">日期范围</label>
            <select
              v-model="filters.date_range"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            >
              <option value="all">全部时间</option>
              <option value="today">今天</option>
              <option value="7d">最近7天</option>
              <option value="1m">最近1个月</option>
              <option value="3m">最近3个月</option>
            </select>
          </div>
          
          <div class="flex items-end">
            <button
              @click="resetFilters"
              class="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              重置筛选
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 申请列表 -->
    <div class="bg-white shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <div v-if="loading" class="text-center py-8">
          <Icon name="clarity:refresh-line" class="animate-spin h-8 w-8 text-indigo-500 mx-auto mb-2" />
          <p class="text-gray-500">正在加载...</p>
        </div>
        
        <div v-else-if="withdrawals.length === 0" class="text-center py-8">
          <Icon name="clarity:inbox-line" class="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 class="text-lg font-medium text-gray-900 mb-2">暂无申请记录</h3>
          <p class="text-gray-500">当前筛选条件下没有找到佣金提现申请</p>
        </div>
        
        <div v-else class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">代理信息</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">提现金额</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">申请时佣金</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">申请时间</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr v-for="withdrawal in withdrawals" :key="withdrawal.id" class="hover:bg-gray-50">
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                      <div class="h-10 w-10 rounded-full bg-indigo-100 flex items-center justify-center">
                        <Icon name="clarity:user-line" class="h-5 w-5 text-indigo-600" />
                      </div>
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">
                        {{ withdrawal.agent_info?.username || '未知代理' }}
                      </div>
                      <div class="text-sm text-gray-500">
                        {{ withdrawal.agent_info?.phone || '-' }}
                      </div>
                      <div class="text-xs text-gray-400">
                        {{ withdrawal.agent_info?.domain_suffix || '-' }}
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm font-semibold text-red-600">
                    ¥{{ withdrawal.withdrawal_amount.toFixed(2) }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <div class="text-sm text-gray-900">
                    ¥{{ withdrawal.unsettled_amount_snapshot.toFixed(2) }}
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="{
                    'bg-yellow-100 text-yellow-800': withdrawal.status === 'pending',
                    'bg-green-100 text-green-800': withdrawal.status === 'completed',
                    'bg-red-100 text-red-800': withdrawal.status === 'rejected'
                  }">
                    {{ withdrawal.status_display }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {{ formatDate(withdrawal.created_at) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                  <button
                    @click="viewDetail(withdrawal)"
                    class="text-indigo-600 hover:text-indigo-900"
                  >
                    查看详情
                  </button>
                  <button
                    v-if="withdrawal.status === 'pending'"
                    @click="processWithdrawal(withdrawal, 'approve')"
                    class="text-green-600 hover:text-green-900"
                  >
                    批准
                  </button>
                  <button
                    v-if="withdrawal.status === 'pending'"
                    @click="processWithdrawal(withdrawal, 'reject')"
                    class="text-red-600 hover:text-red-900"
                  >
                    拒绝
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- 分页 -->
        <div v-if="pagination.total_pages > 1" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6 mt-4">
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
          <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
              <p class="text-sm text-gray-700">
                显示第 <span class="font-medium">{{ (pagination.current_page - 1) * pagination.page_size + 1 }}</span> 到 
                <span class="font-medium">{{ Math.min(pagination.current_page * pagination.page_size, pagination.total_items) }}</span> 条，
                共 <span class="font-medium">{{ pagination.total_items }}</span> 条记录
              </p>
            </div>
            <div>
              <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                  @click="changePage(pagination.current_page - 1)"
                  :disabled="!pagination.has_previous"
                  class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  上一页
                </button>
                <button
                  @click="changePage(pagination.current_page + 1)"
                  :disabled="!pagination.has_next"
                  class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  下一页
                </button>
              </nav>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <Teleport to="body">
      <div v-if="showDetailModal" class="fixed inset-0 z-50 overflow-y-auto">
        <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
          <div class="fixed inset-0 transition-opacity">
            <div class="absolute inset-0 bg-gray-500 opacity-75" @click="closeDetailModal"></div>
          </div>

          <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="w-full">
                  <h3 class="text-lg leading-6 font-medium text-gray-900 mb-4">
                    提现申请详情
                  </h3>
                  
                  <div v-if="selectedWithdrawal">
                    <!-- 标签页导航 -->
                    <div class="border-b border-gray-200 mb-4">
                      <nav class="-mb-px flex space-x-8">
                        <button
                          @click="activeTab = 'application'"
                          :class="activeTab === 'application' 
                            ? 'border-indigo-500 text-indigo-600' 
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
                          class="whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm"
                        >
                          申请信息
                        </button>
                        <button
                          @click="activeTab = 'agent'"
                          :class="activeTab === 'agent' 
                            ? 'border-indigo-500 text-indigo-600' 
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
                          class="whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm"
                        >
                          代理信息
                        </button>
                        <button
                          @click="activeTab = 'payment'"
                          :class="activeTab === 'payment' 
                            ? 'border-indigo-500 text-indigo-600' 
                            : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
                          class="whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm"
                        >
                          收款信息
                        </button>
                      </nav>
                    </div>

                    <!-- 标签页内容 -->
                    <div class="min-h-80">
                      <!-- 申请信息 -->
                      <div v-if="activeTab === 'application'" class="space-y-4">
                        <div class="bg-gray-50 rounded-lg p-4 space-y-3">
                          <div class="flex justify-between">
                            <span class="text-sm text-gray-600">申请金额:</span>
                            <span class="text-sm font-semibold text-red-600">¥{{ selectedWithdrawal.withdrawal_amount.toFixed(2) }}</span>
                          </div>
                          <div class="flex justify-between">
                            <span class="text-sm text-gray-600">申请时未结算金额:</span>
                            <span class="text-sm text-gray-900">¥{{ selectedWithdrawal.unsettled_amount_snapshot.toFixed(2) }}</span>
                          </div>
                          <div class="flex justify-between">
                            <span class="text-sm text-gray-600">申请状态:</span>
                            <span class="text-sm" :class="{
                              'text-yellow-600': selectedWithdrawal.status === 'pending',
                              'text-green-600': selectedWithdrawal.status === 'completed',
                              'text-red-600': selectedWithdrawal.status === 'rejected'
                            }">
                              {{ selectedWithdrawal.status_display }}
                            </span>
                          </div>
                          <div class="flex justify-between">
                            <span class="text-sm text-gray-600">申请时间:</span>
                            <span class="text-sm text-gray-900">{{ formatDate(selectedWithdrawal.created_at) }}</span>
                          </div>
                          <div v-if="selectedWithdrawal.completed_at" class="flex justify-between">
                            <span class="text-sm text-gray-600">处理时间:</span>
                            <span class="text-sm text-gray-900">{{ formatDate(selectedWithdrawal.completed_at) }}</span>
                          </div>
                          <div v-if="selectedWithdrawal.admin_note" class="space-y-1">
                            <span class="text-sm text-gray-600">管理员备注:</span>
                            <p class="text-sm text-gray-900 bg-white rounded p-2 border">{{ selectedWithdrawal.admin_note }}</p>
                          </div>
                        </div>
                      </div>

                      <!-- 代理信息 -->
                      <div v-if="activeTab === 'agent'" class="space-y-4">
                        <div v-if="detailData?.agent" class="bg-gray-50 rounded-lg p-4 space-y-3">
                          <div class="flex justify-between">
                            <span class="text-sm text-gray-600">用户名:</span>
                            <span class="text-sm text-gray-900">{{ detailData.agent.username }}</span>
                          </div>
                          <div class="flex justify-between">
                            <span class="text-sm text-gray-600">手机号:</span>
                            <span class="text-sm text-gray-900">{{ detailData.agent.phone || '-' }}</span>
                          </div>
                          <div class="flex justify-between">
                            <span class="text-sm text-gray-600">域名后缀:</span>
                            <span class="text-sm text-gray-900">{{ detailData.agent.domain_suffix }}</span>
                          </div>
                          <div class="flex justify-between">
                            <span class="text-sm text-gray-600">累计佣金:</span>
                            <span class="text-sm text-gray-900">¥{{ detailData.agent.total_commission.toFixed(2) }}</span>
                          </div>
                          <div class="flex justify-between">
                            <span class="text-sm text-gray-600">已结算佣金:</span>
                            <span class="text-sm text-green-600">¥{{ detailData.agent.settled_commission.toFixed(2) }}</span>
                          </div>
                          <div class="flex justify-between">
                            <span class="text-sm text-gray-600">未结算佣金:</span>
                            <span class="text-sm text-orange-600">¥{{ detailData.agent.unsettled_commission.toFixed(2) }}</span>
                          </div>
                        </div>
                        <div v-else class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                          <p class="text-sm text-yellow-800">代理信息加载中...</p>
                        </div>
                      </div>

                      <!-- 收款信息 -->
                      <div v-if="activeTab === 'payment'" class="space-y-4">
                        <div v-if="detailData?.payment_config" class="bg-gray-50 rounded-lg p-4 space-y-3">
                          <div class="flex justify-between">
                            <span class="text-sm text-gray-600">收款方式:</span>
                            <span class="text-sm text-gray-900">{{ detailData.payment_config.payment_method_display }}</span>
                          </div>
                          <div class="flex justify-between">
                            <span class="text-sm text-gray-600">收款账号:</span>
                            <span class="text-sm text-gray-900">{{ detailData.payment_config.payment_account }}</span>
                          </div>
                          <div class="flex justify-between">
                            <span class="text-sm text-gray-600">收款人姓名:</span>
                            <span class="text-sm text-gray-900">{{ detailData.payment_config.payment_name }}</span>
                          </div>
                          <div v-if="detailData.payment_config.payment_qr_code" class="space-y-2">
                            <span class="text-sm text-gray-600">收款码:</span>
                            <div class="bg-white rounded p-2 border flex justify-center">
                              <img 
                                :src="getImageUrl(detailData.payment_config.payment_qr_code)" 
                                alt="收款码"
                                class="max-w-48 max-h-48"
                                @error="handleImageError"
                              />
                            </div>
                          </div>
                        </div>
                        <div v-else class="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                          <p class="text-sm text-yellow-800">该代理尚未配置收款信息</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                @click="closeDetailModal"
                type="button"
                class="w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm"
              >
                关闭
              </button>
              
              <button
                v-if="selectedWithdrawal && selectedWithdrawal.status === 'pending'"
                @click="processWithdrawal(selectedWithdrawal, 'approve')"
                type="button"
                class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-green-600 text-base font-medium text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:ml-3 sm:w-auto sm:text-sm"
              >
                批准提现
              </button>
              
              <button
                v-if="selectedWithdrawal && selectedWithdrawal.status === 'pending'"
                @click="processWithdrawal(selectedWithdrawal, 'reject')"
                type="button"
                class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm"
              >
                拒绝申请
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 处理申请弹窗 -->
    <Teleport to="body">
      <div v-if="showProcessModal" class="fixed inset-0 z-50 overflow-y-auto">
        <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
          <div class="fixed inset-0 transition-opacity">
            <div class="absolute inset-0 bg-gray-500 opacity-75" @click="closeProcessModal"></div>
          </div>

          <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full sm:mx-0 sm:h-10 sm:w-10" :class="{
                  'bg-green-100': processAction === 'approve',
                  'bg-red-100': processAction === 'reject'
                }">
                  <Icon 
                    :name="processAction === 'approve' ? 'clarity:check-circle-line' : 'clarity:times-circle-line'"
                    class="h-6 w-6"
                    :class="{
                      'text-green-600': processAction === 'approve',
                      'text-red-600': processAction === 'reject'
                    }"
                  />
                </div>
                <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                  <h3 class="text-lg leading-6 font-medium text-gray-900">
                    {{ processAction === 'approve' ? '批准提现申请' : '拒绝提现申请' }}
                  </h3>
                  <div class="mt-2">
                    <p class="text-sm text-gray-500">
                      {{ processAction === 'approve' 
                        ? `确认批准代理 ${processingWithdrawal?.agent_info?.username} 的提现申请吗？金额：¥${processingWithdrawal?.withdrawal_amount.toFixed(2)}`
                        : `确认拒绝代理 ${processingWithdrawal?.agent_info?.username} 的提现申请吗？` 
                      }}
                    </p>
                    
                    <div class="mt-4">
                      <label for="admin-note" class="block text-sm font-medium text-gray-700">
                        {{ processAction === 'approve' ? '处理备注（可选）' : '拒绝原因' }}
                      </label>
                      <textarea
                        id="admin-note"
                        v-model="adminNote"
                        rows="3"
                        :placeholder="processAction === 'approve' ? '请输入处理备注...' : '请输入拒绝原因...'"
                        :required="processAction === 'reject'"
                        class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      ></textarea>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                @click="confirmProcess"
                :disabled="processAction === 'reject' && !adminNote.trim()"
                type="button"
                class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 text-base font-medium text-white focus:outline-none focus:ring-2 focus:ring-offset-2 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                :class="{
                  'bg-green-600 hover:bg-green-700 focus:ring-green-500': processAction === 'approve',
                  'bg-red-600 hover:bg-red-700 focus:ring-red-500': processAction === 'reject'
                }"
              >
                {{ processAction === 'approve' ? '确认批准' : '确认拒绝' }}
              </button>
              <button
                @click="closeProcessModal"
                type="button"
                class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
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
import { ref, reactive, watch, onMounted } from 'vue'

const { $ui } = useNuxtApp()
const api = useApi()

// 响应式数据
const loading = ref(false)
const withdrawals = ref([])
const pagination = ref({
  total_items: 0,
  total_pages: 0,
  current_page: 1,
  page_size: 20,
  has_next: false,
  has_previous: false
})

// 筛选条件 - 使用reactive，参考Agents.vue的模式
const filters = reactive({
  search: '',
  status: '',
  date_range: 'all',
  page: 1,
  page_size: 20
})

// 弹窗状态
const showDetailModal = ref(false)
const showProcessModal = ref(false)
const selectedWithdrawal = ref(null)
const detailData = ref(null)
const activeTab = ref('application') // 默认显示申请信息标签页

// 处理申请相关
const processingWithdrawal = ref(null)
const processAction = ref('')
const adminNote = ref('')

// 生命周期
onMounted(() => {
  loadWithdrawals()
})

// 方法
const loadWithdrawals = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      page,
      page_size: filters.page_size,
      search: filters.search.trim(),
      status: filters.status,
      date_range: filters.date_range
    }

    const response = await api.get('/admin/commission-withdrawals/', { params })
    
    if (response.code === 0) {
      withdrawals.value = response.data.items
      pagination.value = response.data.pagination
    } else {
      $ui.error('获取数据失败', response.message)
    }
  } catch (error) {
    console.error('获取佣金申请列表失败:', error)
    $ui.error('获取数据失败', '网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

const changePage = (page) => {
  if (page >= 1 && page <= pagination.value.total_pages) {
    filters.page = page
    loadWithdrawals(page)
  }
}

const resetFilters = () => {
  filters.search = ''
  filters.status = ''
  filters.date_range = 'all'
  filters.page = 1
  loadWithdrawals()
}

const viewDetail = async (withdrawal) => {
  selectedWithdrawal.value = withdrawal
  activeTab.value = 'application' // 重置到申请信息标签页
  
  try {
    const response = await api.get(`/admin/commission-withdrawals/detail/${withdrawal.id}/`)
    if (response.code === 0) {
      detailData.value = response.data
      showDetailModal.value = true
    } else {
      $ui.error('获取详情失败', response.message)
    }
  } catch (error) {
    console.error('获取提现申请详情失败:', error)
    $ui.error('获取详情失败', '网络错误，请稍后重试')
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  selectedWithdrawal.value = null
  detailData.value = null
  activeTab.value = 'application' // 重置标签页状态
}

const processWithdrawal = (withdrawal, action) => {
  processingWithdrawal.value = withdrawal
  processAction.value = action
  adminNote.value = ''
  showProcessModal.value = true
  closeDetailModal()
}

const closeProcessModal = () => {
  showProcessModal.value = false
  processingWithdrawal.value = null
  processAction.value = ''
  adminNote.value = ''
}

const confirmProcess = async () => {
  if (processAction.value === 'reject' && !adminNote.value.trim()) {
    $ui.error('请输入拒绝原因')
    return
  }

  try {
    $ui.showLoading('正在处理...')
    
    const response = await api.post('/admin/commission-withdrawals/process/', {
      withdrawal_id: processingWithdrawal.value.id,
      action: processAction.value,
      admin_note: adminNote.value.trim()
    })
    
    if (response.code === 0) {
      $ui.success(
        processAction.value === 'approve' ? '提现申请已批准' : '提现申请已拒绝'
      )
      
      // 刷新列表
      await loadWithdrawals(pagination.value.current_page)
      
      closeProcessModal()
    } else {
      $ui.error('处理失败', response.message)
    }
  } catch (error) {
    console.error('处理提现申请失败:', error)
    $ui.error('处理失败', '网络错误，请稍后重试')
  } finally {
    $ui.hideLoading()
  }
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getImageUrl = (path) => {
  if (!path) return ''
  // 如果已经是完整URL，直接返回
  if (path.startsWith('http://') || path.startsWith('https://')) {
    return path
  }
  // 拼接API基础URL
  const config = useRuntimeConfig()
  return `${config.public.fileUrl}${path}`
}

const handleImageError = (event) => {
  event.target.style.display = 'none'
  const parent = event.target.parentElement
  if (parent) {
    parent.innerHTML = '<div class="text-center text-gray-500 py-4">图片加载失败</div>'
  }
}

// 监听筛选条件变化 - 参考Agents.vue的模式
watch(() => filters.search, () => {
  filters.page = 1
  loadWithdrawals()
})

watch(() => filters.status, () => {
  filters.page = 1
  loadWithdrawals()
})

watch(() => filters.date_range, () => {
  filters.page = 1
  loadWithdrawals()
})
</script> 
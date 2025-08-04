<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="md:flex md:items-center md:justify-between">
      <div class="flex-1 min-w-0">
        <h1 class="text-3xl font-light text-gray-900">查询记录管理</h1>
        <p class="mt-2 text-base text-gray-600">查看和管理用户查询记录</p>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="bg-white border border-gray-200 rounded-lg">
      <div class="flex flex-wrap items-end gap-4 p-6">
        <!-- 搜索框 -->
        <div class="flex flex-col space-y-1 min-w-0 flex-1 max-w-xs">
          <label for="search" class="text-sm font-medium text-gray-700">搜索用户</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Icon name="clarity:search-line" class="h-5 w-5 text-gray-400" />
            </div>
            <input
              v-model="filters.search"
              id="search"
              name="search"
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent sm:text-sm"
              placeholder="搜索用户名"
              type="search"
            />
          </div>
        </div>

        <!-- 查询类型筛选 -->
        <div class="flex flex-col space-y-1 min-w-0">
          <label for="query_type" class="text-sm font-medium text-gray-700">查询类型</label>
          <select
            v-model="filters.query_type"
            id="query_type"
            class="block w-auto px-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent sm:text-sm"
          >
            <option v-for="type in queryTypes" :key="type.value" :value="type.value">
              {{ type.text }}
            </option>
          </select>
        </div>

        <!-- 状态筛选 -->
        <div class="flex flex-col space-y-1 min-w-0">
          <label for="status" class="text-sm font-medium text-gray-700">查询状态</label>
          <select
            v-model="filters.status"
            id="status"
            class="block w-auto px-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent sm:text-sm"
          >
            <option v-for="status in statusFilters" :key="status.value" :value="status.value">
              {{ status.text }}
            </option>
          </select>
        </div>

        <!-- 日期范围 -->
        <div class="flex flex-col space-y-1 min-w-0">
          <label class="text-sm font-medium text-gray-700">时间范围</label>
          <div class="flex flex-wrap gap-1 h-10 items-center">
            <button
              v-for="range in dateRanges"
              :key="range.value"
              @click="filters.date_range = range.value"
              :class="[
                filters.date_range === range.value
                  ? 'bg-indigo-500 text-white border-indigo-500'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50',
                'px-3 py-2 text-sm font-medium rounded-lg border transition-all duration-200 whitespace-nowrap h-10 flex items-center'
              ]"
            >
              {{ range.text }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 查询记录列表 -->
    <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <!-- 加载状态 -->
      <div v-if="loading" class="p-8 text-center">
        <Icon name="clarity:refresh-line" class="w-8 h-8 text-gray-400 animate-spin mx-auto" />
        <p class="mt-3 text-sm text-gray-500">正在加载查询记录...</p>
      </div>

      <!-- 空状态 -->
      <div v-else-if="queryRecords.length === 0" class="p-8 text-center">
        <Icon name="clarity:file-line" class="w-16 h-16 text-gray-300 mx-auto" />
        <h3 class="mt-4 text-lg font-medium text-gray-900">未找到查询记录</h3>
        <p class="mt-2 text-sm text-gray-500">尝试调整筛选条件。</p>
      </div>

      <!-- 表格 -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th scope="col" class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">用户信息</th>
              <th scope="col" class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">查询类型</th>
              <th scope="col" class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">订单信息</th>
              <th scope="col" class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">查询状态</th>
              <th scope="col" class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">创建时间</th>
              <th scope="col" class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white">
            <tr v-for="item in queryRecords" :key="item.id" class="border-b border-gray-100 hover:bg-gray-50 transition-colors duration-150">
              <!-- 用户信息 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ item.username }}</div>
                <div v-if="item.agent_info" class="text-xs text-indigo-600 mt-1">
                  代理: {{ item.agent_info.username }}
                </div>
              </td>

              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ item.order_info.query_type }}</div>
              </td>
              <!-- 订单信息 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div v-if="item.order_info" class="text-sm">
                  <div class="font-medium text-gray-900">
                    {{ item.order_info.order_no }}
                  </div>
  
                  <div class="text-gray-500 mt-1">
                    ¥{{ item.order_info.amount }}
                  </div>
                </div>
                <div v-else class="text-sm text-gray-500">
                  无关联订单
                </div>
              </td>

              <!-- 查询状态 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="[
                  item.status === 'success' ? 'bg-green-50 text-green-700 border-green-200' :
                  item.status === 'failed' ? 'bg-red-50 text-red-700 border-red-200' :
                  item.status === 'processing' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' :
                  'bg-gray-50 text-gray-700 border-gray-200',
                  'px-3 py-1 inline-flex text-xs font-medium rounded-full border'
                ]">
                  {{ item.status_display }}
                </span>
                <div v-if="item.error_message" class="mt-1 text-xs text-red-600 max-w-xs truncate" :title="item.error_message">
                  {{ item.error_message }}
                </div>
              </td>

              <!-- 创建时间 -->
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                {{ formatDate(item.created_at) }}
                <div v-if="item.completed_time" class="text-xs text-gray-400 mt-1">
                  完成: {{ formatDate(item.completed_time) }}
                </div>
              </td>

              <!-- 操作 -->
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  @click="deleteRecord(item)"
                  :disabled="deleting === item.id"
                  class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Icon v-if="deleting === item.id" name="clarity:refresh-line" class="w-4 h-4 mr-1 animate-spin" />
                  <Icon v-else name="clarity:trash-line" class="w-4 h-4 mr-1" />
                  {{ deleting === item.id ? '删除中...' : '删除' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div v-if="pagination.total_items > 0" class="px-6 py-4 border-t border-gray-200 flex items-center justify-between bg-gray-50">
        <div class="flex items-center text-sm text-gray-700">
          <span>显示第 {{ (pagination.current_page - 1) * pagination.page_size + 1 }} 到 {{ Math.min(pagination.current_page * pagination.page_size, pagination.total_items) }} 条，共 {{ pagination.total_items }} 条</span>
        </div>
        <div v-if="pagination.total_pages > 1" class="flex items-center space-x-2">
          <button
            @click="changePage(pagination.current_page - 1)"
            :disabled="!pagination.has_previous"
            class="px-4 py-2 text-sm font-medium border border-gray-300 rounded-lg hover:bg-white transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            上一页
          </button>
          <span class="px-4 py-2 text-sm text-gray-700 font-medium">{{ pagination.current_page }} / {{ pagination.total_pages }}</span>
          <button
            @click="changePage(pagination.current_page + 1)"
            :disabled="!pagination.has_next"
            class="px-4 py-2 text-sm font-medium border border-gray-300 rounded-lg hover:bg-white transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            下一页
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const api = useApi()
const { $ui } = useNuxtApp()

// 响应式数据
const queryRecords = ref([])
const loading = ref(false)
const deleting = ref(null)
const pagination = ref({
  current_page: 1,
  total_pages: 0,
  total_items: 0,
  page_size: 10,
  has_next: false,
  has_previous: false
})

// 筛选条件
const filters = ref({
  search: '',
  date_range: 'all',
  query_type: '',
  status: '',
  page: 1,
  page_size: 20
})

// 筛选选项
const dateRanges = [
  { text: '全部', value: 'all' },
  { text: '今日', value: 'today' },
  { text: '近7天', value: '7d' },
  { text: '一个月', value: '1m' },
  { text: '三个月', value: '3m' },
  { text: '半年', value: '6m' }
]

const queryTypes = [
  { text: '全部', value: '' },
  { text: '个人查询', value: '个人查询配置' },
  { text: '企业查询', value: '企业查询配置' }
]

const statusFilters = [
  { text: '全部', value: '' },
  { text: '成功', value: 'success' },
  { text: '失败', value: 'failed' },
  { text: '处理中', value: 'processing' },
  { text: '超时', value: 'timeout' }
]

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

// 获取查询记录列表
const getQueryRecords = async () => {
  try {
    loading.value = true
    
    const params = {
      page: pagination.value.current_page,
      page_size: 20,
      ...filters.value
    }

    const response = await api.get('/admin/query-records/',  params )
    
    if (response.code === 0) {
      queryRecords.value = response.data.items || []
      pagination.value = response.data.pagination || {
        current_page: 1,
        total_pages: 0,
        total_items: 0,
        page_size: 10,
        has_next: false,
        has_previous: false
      }
    } else {
      $ui.error('获取查询记录失败', response.message)
    }
  } catch (error) {
    console.error('获取查询记录失败:', error)
    $ui.error('获取查询记录失败', '网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.value.current_page = 1
  getQueryRecords()
}

// 切换页面
const changePage = (page) => {
  if (page < 1 || page > pagination.value.total_pages) return
  pagination.value.current_page = page
  getQueryRecords()
}

// 删除记录
const deleteRecord = async (item) => {
  try {
    if (!confirm(`确定要删除这条查询记录吗？`)) {
      return
    }

    deleting.value = item.id
    
    const response = await api.post(`/admin/query-records/delete/${item.id}/`)
    
    if (response.code === 0) {
      $ui.success('查询记录删除成功')
      getQueryRecords() // 重新加载数据
    } else {
      $ui.error('删除失败', response.message || '请稍后重试')
    }
  } catch (error) {
    console.error('删除查询记录失败:', error)
    $ui.error('删除失败', '网络错误，请稍后重试')
  } finally {
    deleting.value = null
  }
}

// 页面初始化
onMounted(() => {
  getQueryRecords()
})

// 监听筛选条件变化
watch(filters, () => {
  // 防抖处理
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  searchTimeout = setTimeout(() => {
    handleSearch()
  }, 500)
}, { deep: true })
</script>

<style scoped>
/* 动画效果 */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style> 
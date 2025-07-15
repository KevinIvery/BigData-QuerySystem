<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="md:flex md:items-center md:justify-between">
      <div class="flex-1 min-w-0">
        <h1 class="text-3xl font-light text-gray-900">普通用户管理</h1>
        <p class="mt-1 text-base text-gray-600">管理系统中的普通用户账户</p>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="bg-white border border-gray-200 rounded-lg p-6">
      <div class="flex flex-wrap items-end gap-4">
        <!-- 搜索框 -->
        <div class="max-w-xs">
          <label for="search" class="sr-only">搜索</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Icon name="clarity:search-line" class="h-5 w-5 text-gray-400" />
            </div>
            <input
              v-model="filters.search"
              id="search"
              name="search"
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="搜索用户名或手机号"
              type="search"
            />
          </div>
        </div>

        <!-- 登录类型筛选 -->
        <div class="flex items-center space-x-2">
          <span class="text-sm font-medium text-gray-700">登录类型:</span>
          <button
            v-for="type in loginTypes"
            :key="type.value"
            @click="filters.login_type = type.value"
            :class="[
              filters.login_type === type.value
                ? 'bg-indigo-500 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
              'px-3 py-2 text-sm font-medium rounded-lg transition-all duration-150'
            ]"
          >
            {{ type.text }}
          </button>
        </div>

        <!-- 代理筛选 -->
        <div class="flex items-center space-x-2">
          <span class="text-sm font-medium text-gray-700">来源:</span>
          <select
            v-model="filters.agent_id"
            class="border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">全部</option>
            <option value="main">主站</option>
            <option v-for="agent in agents" :key="agent.id" :value="agent.id">
              {{ agent.username }}
            </option>
          </select>
        </div>

        <!-- 状态筛选 -->
        <div class="flex items-center space-x-2">
          <span class="text-sm font-medium text-gray-700">状态:</span>
          <button
            v-for="status in statusTypes"
            :key="status.value"
            @click="filters.status = status.value"
            :class="[
              filters.status === status.value
                ? 'bg-indigo-500 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
              'px-3 py-2 text-sm font-medium rounded-lg transition-all duration-150'
            ]"
          >
            {{ status.text }}
          </button>
        </div>

        <!-- 日期范围 -->
        <div class="flex items-center space-x-2">
          <span class="text-sm font-medium text-gray-700">注册时间:</span>
          <button
            v-for="range in dateRanges"
            :key="range.value"
            @click="filters.date_range = range.value"
            :class="[
              filters.date_range === range.value
                ? 'bg-indigo-500 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
              'px-3 py-2 text-sm font-medium rounded-lg transition-all duration-150 h-10'
            ]"
          >
            {{ range.text }}
          </button>
        </div>
      </div>
    </div>

    <!-- 待处理注销申请提示 -->
    <div v-if="deactivatedUsersCount > 0" class="bg-amber-50 border border-amber-200 rounded-lg p-4">
      <div class="flex items-center">
        <Icon name="clarity:warning-standard-line" class="w-5 h-5 text-amber-600 mr-2" />
        <div class="flex-1">
          <h3 class="text-sm font-medium text-amber-800">
            有 {{ deactivatedUsersCount }} 个用户申请注销
          </h3>
          <p class="text-sm text-amber-700 mt-1">
            这些用户已标记为注销状态，请及时处理。已注销用户会优先显示在列表顶部。
          </p>
        </div>
        <button 
          @click="filters.status = 'deactivated'"
          class="bg-amber-600 text-white px-3 py-1 rounded-md text-sm hover:bg-amber-700 transition-colors"
        >
          查看注销用户
        </button>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <!-- 加载状态 -->
      <div v-if="loading" class="p-6 text-center">
        <Icon name="clarity:refresh-line" class="w-8 h-8 text-gray-400 animate-spin mx-auto" />
        <p class="mt-2 text-sm text-gray-500">正在加载用户列表...</p>
      </div>

      <!-- 空状态 -->
      <div v-else-if="users.length === 0" class="p-6 text-center">
        <Icon name="clarity:users-line" class="w-12 h-12 text-gray-400 mx-auto" />
        <h3 class="mt-2 text-sm font-medium text-gray-900">未找到用户</h3>
        <p class="mt-1 text-sm text-gray-500">尝试调整筛选条件。</p>
      </div>

      <!-- 表格 -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
          <thead class="bg-gray-50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">用户信息</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">登录方式</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">来源</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">注册时间</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">状态</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">操作</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-100">
            <tr v-for="user in users" :key="user.id" :class="[
              user.is_deactivated 
                ? 'bg-red-50 hover:bg-red-100 border-l-4 border-red-400' 
                : 'hover:bg-gray-50',
              'transition-colors duration-200'
            ]">
              <!-- 用户信息 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="flex-shrink-0 h-10 w-10">
                    <img class="h-10 w-10 rounded-full" :src="`https://ui-avatars.com/api/?name=${user.username}&background=6366f1&color=fff`" alt="">
                  </div>
                  <div class="ml-4">
                    <div class="text-sm font-medium text-gray-900">{{ user.username }}</div>
                    <div class="text-sm text-gray-500">{{ user.phone || '无手机号' }}</div>
                  </div>
                </div>
              </td>
              
              <!-- 登录方式 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ user.login_type_display }}</div>
                <div v-if="user.openid" class="text-xs text-gray-500">微信: {{ user.openid.slice(0, 8) }}...</div>
              </td>
              
              <!-- 来源 -->
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                <div v-if="user.agent_info" class="flex items-center">
                  <Icon name="clarity:building-line" class="w-4 h-4 text-indigo-500 mr-1" />
                  <span>{{ user.agent_info.username }}</span>
                </div>
                <div v-else class="flex items-center">
                  <Icon name="clarity:home-line" class="w-4 h-4 text-green-500 mr-1" />
                  <span>主站</span>
                </div>
              </td>
              
              <!-- 注册时间 -->
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ new Date(user.created_at).toLocaleString() }}
              </td>
              
              <!-- 状态 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <span :class="[
                    user.is_deactivated ? 'bg-red-100 text-red-800 border border-red-200' : 'bg-green-50 text-green-700 border border-green-200',
                    'px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-md'
                  ]">
                    {{ user.is_deactivated ? '申请注销' : '正常' }}
                  </span>
                  <Icon v-if="user.is_deactivated" name="clarity:exclamation-triangle-line" class="w-4 h-4 text-red-500 ml-2" />
                </div>
                <div v-if="user.is_deactivated && user.deactivated_at" class="text-xs text-red-600 mt-1">
                  注销时间: {{ new Date(user.deactivated_at).toLocaleString() }}
                </div>
              </td>
              
              <!-- 操作 -->
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <div v-if="user.is_deactivated" class="flex items-center space-x-2">
                  <button 
                    @click="confirmDeleteUser(user)"
                    class="text-red-600 hover:text-red-900 bg-red-50 hover:bg-red-100 px-3 py-1 rounded-md transition-colors duration-150 font-medium"
                  >
                    <Icon name="clarity:check-line" class="w-4 h-4 mr-1 inline" />
                    确认注销
                  </button>
                  <span class="text-xs text-red-600 bg-red-100 px-2 py-1 rounded">待处理</span>
                </div>
                <button 
                  v-else
                  @click="confirmDeleteUser(user)"
                  class="text-red-600 hover:text-red-900 bg-red-50 hover:bg-red-100 px-3 py-1 rounded-md transition-colors duration-150"
                >
                  <Icon name="clarity:trash-line" class="w-4 h-4 mr-1 inline" />
                  注销
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div v-if="pagination.total_items > 0" class="px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
        <div class="flex-1 flex justify-between sm:hidden">
          <button @click="changePage(pagination.current_page - 1)" :disabled="!pagination.has_previous" class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
            上一页
          </button>
          <button @click="changePage(pagination.current_page + 1)" :disabled="!pagination.has_next" class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
            下一页
          </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              第 <span class="font-medium">{{ pagination.current_page }}</span> 页，共 <span class="font-medium">{{ pagination.total_pages }}</span> 页 (总计 <span class="font-medium">{{ pagination.total_items }}</span> 条)
            </p>
          </div>
          <div>
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
              <button @click="changePage(pagination.current_page - 1)" :disabled="!pagination.has_previous" class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
                <span class="sr-only">上一页</span>
                <Icon name="clarity:angle-line" class="h-5 w-5 rotate-90" />
              </button>
              <button @click="changePage(pagination.current_page + 1)" :disabled="!pagination.has_next" class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
                <span class="sr-only">下一页</span>
                <Icon name="clarity:angle-line" class="h-5 w-5 -rotate-90"/>
              </button>
            </nav>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'

const api = useApi()
const { $ui } = useNuxtApp()

const users = ref([])
const agents = ref([])
const pagination = ref({})
const loading = ref(true)
const deactivatedUsersCount = ref(0)

const filters = reactive({
  search: '',
  date_range: 'all',
  login_type: 'all',
  agent_id: '',
  status: 'all',
  page: 1,
  page_size: 20
})

const dateRanges = [
  { text: '全部', value: 'all' },
  { text: '今日', value: 'today' },
  { text: '近7天', value: '7d' },
  { text: '一个月', value: '1m' },
  { text: '三个月', value: '3m' },
  { text: '六个月', value: '6m' }
]

const loginTypes = [
  { text: '全部', value: 'all' },
  { text: '微信', value: 'wechat' },
  { text: '手机号', value: 'mobile' }
]

const statusTypes = [
  { text: '全部', value: 'all' },
  { text: '正常', value: 'active' },
  { text: '申请注销', value: 'deactivated' }
]

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/regular-users/', filters)
    if (response.code === 0) {
      users.value = response.data.items
      pagination.value = response.data.pagination
      deactivatedUsersCount.value = response.data.deactivated_count
    } else {
      $ui.error('获取用户列表失败', response.message)
    }
  } catch (error) {
    $ui.error('获取用户列表失败', '网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

const fetchAgents = async () => {
  try {
    const response = await api.get('/admin/agents/')
    if (response.code === 0) {
      agents.value = response.data.items
    }
  } catch (error) {
    console.error('获取代理列表失败:', error)
  }
}

const confirmDeleteUser = (user) => {
  let confirmMessage
  if (user.is_deactivated) {
    confirmMessage = `用户 ${user.username} 已申请注销，您确定要完成注销处理吗？此操作将彻底删除用户数据且不可撤销。`
  } else {
    confirmMessage = `您确定要注销用户 ${user.username} 吗？此操作不可撤销。`
  }
  
  if (confirm(confirmMessage)) {
    handleDeleteUser(user.id)
  }
}

const handleDeleteUser = async (userId) => {
  try {
    const response = await api.post(`/admin/regular-users/delete/${userId}/`)
    if (response.code === 0) {
      $ui.success('用户注销成功')
      fetchUsers()
    } else {
      $ui.error('注销失败', response.message)
    }
  } catch (error) {
    $ui.error('注销失败', '网络错误，请稍后重试')
  }
}

const changePage = (page) => {
  if (page > 0 && page <= pagination.value.total_pages) {
    filters.page = page
    fetchUsers()
  }
}

// 监听筛选条件变化
watch(() => filters.login_type, () => {
  filters.page = 1
  fetchUsers()
})

watch(() => filters.search, () => {
  filters.page = 1
  fetchUsers()
})

watch(() => filters.date_range, () => {
  filters.page = 1
  fetchUsers()
})

watch(() => filters.agent_id, () => {
  filters.page = 1
  fetchUsers()
})

watch(() => filters.status, () => {
  filters.page = 1
  fetchUsers()
})

onMounted(() => {
  fetchUsers()
  fetchAgents()
})
</script> 
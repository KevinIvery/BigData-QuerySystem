<template>
  <div class="space-y-6">
    <!-- 页面标题 -->
    <div class="md:flex md:items-center md:justify-between">
      <div class="flex-1 min-w-0">
        <h1 class="text-3xl font-light text-gray-900">个人查询授权书管理</h1>
        <p class="mt-2 text-base text-gray-600">查看和管理个人查询生成的授权书</p>
      </div>
    </div>

    <!-- 搜索和筛选 -->
    <div class="bg-white border border-gray-200 rounded-lg">
      <div class="flex flex-wrap items-end gap-4 p-6">
        <!-- 搜索关键词 -->
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
              placeholder="用户名、姓名、身份证号"
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-2 focus:ring-indigo-500 focus:border-transparent sm:text-sm"
            />
          </div>
        </div>

        <!-- 查询类型 -->
        <div class="flex flex-col space-y-1 min-w-0">
          <label for="query_type" class="text-sm font-medium text-gray-700">
            查询类型
          </label>
          <select
            id="query_type"
            v-model="filters.query_type"
            class="block w-auto px-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent sm:text-sm"
          >
            <option value="">全部类型</option>
            <option value="personal">个人查询</option>
          </select>
        </div>

        <!-- 状态 -->
        <div class="flex flex-col space-y-1 min-w-0">
          <label for="status" class="text-sm font-medium text-gray-700">
            状态
          </label>
          <select
            id="status"
            v-model="filters.status"
            class="block w-auto px-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent sm:text-sm"
          >
            <option value="">全部状态</option>
            <option value="active">有效</option>
            <option value="expired">已过期</option>
          </select>
        </div>


      </div>
    </div>

    <!-- 数据表格 -->
    <div class="bg-white border border-gray-200 rounded-lg overflow-hidden">
      <!-- 加载状态 -->
      <div v-if="loading" class="p-8 text-center">
        <Icon name="clarity:refresh-line" class="w-8 h-8 text-gray-400 animate-spin mx-auto" />
        <p class="mt-3 text-sm text-gray-500">正在加载授权书列表...</p>
      </div>

      <!-- 空状态 -->
      <div v-else-if="authorizationLetters.length === 0" class="p-8 text-center">
        <Icon name="clarity:file-line" class="w-16 h-16 text-gray-300 mx-auto" />
        <h3 class="mt-4 text-lg font-medium text-gray-900">暂无个人查询授权书</h3>
        <p class="mt-2 text-sm text-gray-500">没有找到符合条件的个人查询授权书记录</p>
      </div>

      <!-- 表格内容 -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                用户名
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                查询人信息
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                查询类型
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                创建时间
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                状态
              </th>
              <th class="px-6 py-4 text-left text-xs font-semibold text-gray-600 uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody class="bg-white">
            <tr v-for="item in authorizationLetters" :key="item.id" class="border-b border-gray-100 hover:bg-gray-50 transition-colors duration-150">
              <!-- 用户信息 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  {{ item.username }}
                </div>
              </td>

              <!-- 查询人信息 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">
                  {{ item.masked_name }}
                </div>
                <div class="text-sm text-gray-500 mt-1">
                  {{ item.masked_id_card }}
                </div>
              </td>

              <!-- 查询类型 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-3 py-1 inline-flex text-xs font-medium rounded-full border bg-blue-50 text-blue-700 border-blue-200">
                  个人查询
                </span>
              </td>

              <!-- 创建时间 -->
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                {{ formatDate(item.created_at) }}
              </td>

              <!-- 状态 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-3 py-1 inline-flex text-xs font-medium rounded-full border"
                      :class="[
                        item.is_expired 
                          ? 'bg-red-50 text-red-700 border-red-200' 
                          : 'bg-green-50 text-green-700 border-green-200'
                      ]">
                  {{ item.is_expired ? '已过期' : '有效' }}
                </span>
              </td>

              <!-- 操作 -->
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                <button
                  @click="downloadAuthorizationLetter(item)"
                  :disabled="downloading === item.id"
                  class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50 rounded-lg transition-colors duration-150 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Icon v-if="downloading === item.id" name="clarity:refresh-line" class="w-4 h-4 mr-1 animate-spin" />
                  <Icon v-else name="clarity:download-line" class="w-4 h-4 mr-1" />
                  {{ downloading === item.id ? '下载中...' : '下载' }}
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
  </div>
</template>

<script setup>
const api = useApi()
const { $ui } = useNuxtApp()

// 响应式数据
const authorizationLetters = ref([])
const loading = ref(false)
const downloading = ref(null)
const currentPage = ref(1)
const pageSize = ref(20)
const total = ref(0)
const totalPages = ref(0)

// 筛选条件
const filters = ref({
  search: '',
  query_type: '',
  status: ''
})

// 计算总页数
const calculateTotalPages = () => {
  totalPages.value = Math.ceil(total.value / pageSize.value)
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

// 获取授权书列表
const getAuthorizationLetters = async () => {
  try {
    loading.value = true
    
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...filters.value
    }

    const response = await api.get('/admin/authorization-letters/', { params })
    
    if (response.code === 0) {
      authorizationLetters.value = response.data.items || []
      total.value = response.data.pagination?.total_items || 0
      currentPage.value = response.data.pagination?.current_page || 1
      pageSize.value = response.data.pagination?.page_size || 20
      calculateTotalPages()
    } else {
      $ui.error('获取授权书列表失败', response.message)
    }
  } catch (error) {
    console.error('获取授权书列表失败:', error)
    $ui.error('获取授权书列表失败', '网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  currentPage.value = 1
  getAuthorizationLetters()
}

// 切换页面
const changePage = (page) => {
  if (page < 1 || page > totalPages.value) return
  currentPage.value = page
  getAuthorizationLetters()
}

// 下载授权书
const downloadAuthorizationLetter = async (item) => {
  try {
    downloading.value = item.id
    
    // 使用token直接下载文件
    const downloadUrl = `/api/admin/authorization-letters/download/${item.download_token}/`
    
    // 创建一个隐藏的a标签来下载文件
    const link = document.createElement('a')
    link.href = downloadUrl
    link.download = `授权书_${item.download_token}.pdf`
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    
    $ui.success('授权书下载成功')
  } catch (error) {
    console.error('下载授权书失败:', error)
    $ui.error('下载失败', '网络错误，请稍后重试')
  } finally {
    downloading.value = null
  }
}

// 页面初始化
onMounted(() => {
  getAuthorizationLetters()
})

// 搜索防抖定时器
let searchTimeout = null

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
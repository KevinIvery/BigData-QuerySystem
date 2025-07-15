<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- 页面标题 -->
    <div class="bg-white shadow rounded-lg p-6 mb-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900">代理申请管理</h1>
          <p class="mt-2 text-sm text-gray-600">管理和处理用户的代理申请请求</p>
        </div>
        <div class="flex items-center space-x-2">
          <span class="text-sm text-gray-500">共计 {{ pagination.total_items }} 份申请</span>
        </div>
      </div>
    </div>

    <!-- 数据表格 -->
    <div class="bg-white shadow rounded-lg overflow-hidden">
      <!-- 加载状态 -->
      <div v-if="loading" class="p-12 text-center">
        <div class="inline-flex items-center">
          <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
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
                申请人信息
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                关联用户
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                联系方式
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                申请时间
              </th>
              <th scope="col" class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                操作
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <!-- 无数据状态 -->
            <tr v-if="!applications.length">
              <td colspan="5" class="px-6 py-12 text-center">
                <div class="text-gray-400">
                  <svg class="mx-auto h-12 w-12 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                  </svg>
                  <p class="text-sm">暂无代理申请数据</p>
                </div>
              </td>
            </tr>
            
            <!-- 数据行 -->
            <tr v-for="application in applications" :key="application.id" class="hover:bg-gray-50">
              <!-- 申请人信息 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-gray-900">{{ application.applicant_name }}</div>
                <div class="text-sm text-gray-500">ID: {{ application.id }}</div>
              </td>
              
              <!-- 关联用户 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-gray-900">{{ application.username }}</div>
                <div class="text-sm text-gray-500" v-if="application.user_id">用户ID: {{ application.user_id }}</div>
              </td>
              
              <!-- 联系方式 -->
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                        :class="application.contact_type === 'wechat' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'">
                    <Icon :name="application.contact_type === 'wechat' ? 'ri:wechat-line' : 'ri:phone-line'" class="w-3 h-3 mr-1" />
                    {{ application.contact_type_display }}
                  </span>
                </div>
                <div class="text-sm text-gray-900 mt-1">{{ application.contact_info }}</div>
              </td>
              
              <!-- 申请时间 -->
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                {{ formatDateTime(application.application_time) }}
              </td>
              
              <!-- 操作 -->
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <div class="flex justify-end space-x-2">
                  <button
                    @click="deleteApplication(application)"
                    class="inline-flex items-center px-3 py-1 border border-transparent text-sm leading-4 font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-colors"
                  >
                    <Icon name="ri:delete-bin-line" class="w-4 h-4 mr-1" />
                    删除
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div v-if="!loading && applications.length" class="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
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
                      ? 'z-10 bg-indigo-50 border-indigo-500 text-indigo-600'
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

    <!-- 删除确认对话框 -->
    <Teleport to="body">
      <div v-if="showDeleteModal" class="fixed inset-0 z-50 overflow-y-auto">
        <div class="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
          <!-- 背景遮罩 -->
          <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" @click="showDeleteModal = false"></div>

          <!-- 居中容器 -->
          <span class="hidden sm:inline-block sm:align-middle sm:h-screen">&#8203;</span>

          <!-- 模态框内容 -->
          <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
            <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div class="sm:flex sm:items-start">
                <div class="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10">
                  <Icon name="ri:alert-line" class="h-6 w-6 text-red-600" />
                </div>
                <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                  <h3 class="text-lg leading-6 font-medium text-gray-900">
                    删除代理申请
                  </h3>
                  <div class="mt-2">
                    <p class="text-sm text-gray-500">
                      确定要删除 <strong>{{ applicationToDelete?.applicant_name }}</strong> 的代理申请吗？
                      <br>
                      此操作不可撤销。
                    </p>
                  </div>
                </div>
              </div>
            </div>
            <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
              <button
                @click="confirmDelete"
                :disabled="deleteLoading"
                class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span v-if="deleteLoading" class="inline-flex items-center">
                  <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  删除中...
                </span>
                <span v-else>确认删除</span>
              </button>
              <button
                @click="showDeleteModal = false"
                :disabled="deleteLoading"
                class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
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
const { $ui } = useNuxtApp()
const api = useApi()

// 响应式数据
const loading = ref(true)
const applications = ref([])
const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total_items: 0,
  page_size: 20,
  has_next: false,
  has_previous: false
})

// 删除相关状态
const showDeleteModal = ref(false)
const deleteLoading = ref(false)
const applicationToDelete = ref(null)

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

// 获取代理申请列表
const fetchApplications = async (page = 1) => {
  try {
    loading.value = true
    
    const response = await api.get('/admin/agent-applications/', {
      params: {
        page,
        page_size: pagination.value.page_size
      }
    })
    
    if (response.code === 0) {
      applications.value = response.data.items || []
      pagination.value = response.data.pagination || pagination.value
    } else {
      $ui.error('获取失败', response.message || '获取代理申请列表失败')
    }
  } catch (error) {
    console.error('获取代理申请列表失败:', error)
    $ui.error('获取失败', '网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 切换页码
const changePage = (page) => {
  if (page >= 1 && page <= pagination.value.total_pages) {
    fetchApplications(page)
  }
}

// 删除代理申请
const deleteApplication = (application) => {
  applicationToDelete.value = application
  showDeleteModal.value = true
}

// 确认删除
const confirmDelete = async () => {
  if (!applicationToDelete.value) return
  
  try {
    deleteLoading.value = true
    
    const response = await api.post(`/admin/agent-applications/delete/${applicationToDelete.value.id}/`)
    
    if (response.code === 0) {
      $ui.success('删除成功')
      showDeleteModal.value = false
      applicationToDelete.value = null
      
      // 重新加载当前页数据
      await fetchApplications(pagination.value.current_page)
      
      // 如果当前页没有数据且不是第一页，则跳转到上一页
      if (applications.value.length === 0 && pagination.value.current_page > 1) {
        await fetchApplications(pagination.value.current_page - 1)
      }
    } else {
      $ui.error('删除失败', response.message || '删除代理申请失败')
    }
  } catch (error) {
    console.error('删除代理申请失败:', error)
    $ui.error('删除失败', '网络错误，请稍后重试')
  } finally {
    deleteLoading.value = false
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
      minute: '2-digit',
      second: '2-digit'
    })
  } catch (error) {
    return dateTimeStr
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchApplications()
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
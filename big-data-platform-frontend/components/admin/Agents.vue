<template>
  <div class="space-y-6">
    <!-- 页面标题和操作按钮 -->
    <div class="md:flex md:items-center md:justify-between">
      <div class="flex-1 min-w-0">
        <h1 class="text-2xl font-bold text-gray-900">代理管理</h1>
        <p class="mt-1 text-sm text-gray-600">管理、搜索和创建代理商账户</p>
      </div>
      <div class="mt-4 flex md:mt-0 md:ml-4">
        <button
          @click="openCreateModal"
          class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <Icon name="clarity:add-line" class="w-5 h-5 mr-2 -ml-1" />
          新增代理
        </button>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="bg-white p-4 shadow rounded-lg">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        <!-- 搜索框 -->
        <div class="lg:col-span-1">
          <label for="search" class="sr-only">搜索</label>
          <div class="relative">
            <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Icon name="clarity:search-line" class="h-5 w-5 text-gray-400" />
            </div>
            <input
              v-model="filters.search"
              id="search"
              name="search"
              class="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
              placeholder="搜索用户名或手机号"
              type="search"
            />
          </div>
        </div>

        <!-- 状态筛选 -->
        <div class="flex items-center space-x-2">
          <span class="text-sm font-medium text-gray-700">状态:</span>
          <button
            v-for="status in statusFilters"
            :key="status.value"
            @click="filters.status = status.value"
            :class="[
              filters.status === status.value
                ? 'bg-indigo-100 text-indigo-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
              'px-3 py-1 text-sm font-medium rounded-md transition-colors'
            ]"
          >
            {{ status.text }}
          </button>
        </div>

        <!-- 日期范围 -->
        <div class="flex items-center space-x-2 justify-start lg:justify-end">
          <span class="text-sm font-medium text-gray-700">注册时间:</span>
           <button
            v-for="range in dateRanges"
            :key="range.value"
            @click="filters.date_range = range.value"
            :class="[
              filters.date_range === range.value
                ? 'bg-indigo-100 text-indigo-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200',
              'px-3 py-1 text-sm font-medium rounded-md transition-colors'
            ]"
          >
            {{ range.text }}
          </button>
        </div>
      </div>
    </div>

    <!-- 代理列表 -->
    <Agents_List
      :agents="agents"
      :pagination="pagination"
      :loading="loading"
      @view-detail="openDetailModal"
      @edit="openEditModal"
      @delete="confirmDeleteAgent"
      @change-page="changePage"
    />
    
    <!-- 新增/编辑代理弹窗 -->
    <Agents_Form
      v-if="modalState.show && modalState.mode !== 'detail'"
      :mode="modalState.mode"
      :agent-data="modalState.agentData"
      :is-submitting="isSubmitting"
      @close="closeModal"
      @submit="handleFormSubmit"
      @error="handleFormError"
    />

    <!-- 代理详情弹窗 -->
    <Agents_Detail
      v-if="modalState.show && modalState.mode === 'detail'"
      :agent-detail="agentDetail"
      @close="closeModal"
    />
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'
import Agents_Form from './Agents_Form.vue'
import Agents_Detail from './Agents_Detail.vue'
import Agents_List from './Agents_List.vue'

const api = useApi()
const { $ui } = useNuxtApp()
const config = useRuntimeConfig()

const agents = ref([])
const pagination = ref({})
const loading = ref(true)
const isSubmitting = ref(false)
const agentDetail = ref({})

const modalState = reactive({
  show: false,
  mode: 'create', // 'create', 'edit', 'detail'
  agentData: {}
})

const filters = reactive({
  search: '',
  date_range: 'all',
  status: 'all',
  page: 1,
  page_size: 10
})

const dateRanges = [
  { text: '全部', value: 'all' },
  { text: '近7天', value: '7d' },
  { text: '一个月', value: '30d' },
  { text: '一年', value: '1y' }
]

const statusFilters = [
  { text: '全部', value: 'all' },
  { text: '正常', value: 'active' },
  { text: '锁定', value: 'locked' }
]

const fetchAgents = async () => {
  loading.value = true
  try {
    const response = await api.get('/admin/agents/',filters)
    if (response.code === 0) {
      // 预处理代理数据，添加完整的域名信息
      agents.value = response.data.items.map(agent => {
        const baseUrl = config.public.AgentsUSL 
        const fullUrl = new URL(baseUrl)
        fullUrl.searchParams.set('agent', agent.domain_suffix)
        
        return {
          ...agent,
          full_domain: fullUrl.href,
          full_domain_display: fullUrl.href.replace(/https?:\/\//, ''),
          // 添加兼容性字段
          can_customize_apis: false,
          follow_main_config: true,
          // 确保佣金字段存在，提供默认值
          total_commission: agent.total_commission || '0.00',
          settled_commission: agent.settled_commission || '0.00',
          unsettled_commission: agent.unsettled_commission || '0.00'
        }
      })
      pagination.value = response.data.pagination
    } else {
      $ui.error('获取代理列表失败', response.message)
    }
  } catch (error) {
    $ui.error('获取代理列表失败', '网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

const openCreateModal = () => {
  modalState.mode = 'create'
  modalState.agentData = {}
  modalState.show = true
}

const openEditModal = (agent) => {
  modalState.mode = 'edit'
  modalState.agentData = agent
  modalState.show = true
}

const openDetailModal = async (agent) => {
  modalState.mode = 'detail'
  modalState.show = true
  
  // 获取详细的代理信息
  try {
    const response = await api.get(`/admin/agents/detail/${agent.id}/`)
    if (response.code === 0) {
      // 确保佣金字段存在
      agentDetail.value = {
        ...response.data,
        total_commission: response.data.total_commission || '0.00',
        settled_commission: response.data.settled_commission || '0.00',
        unsettled_commission: response.data.unsettled_commission || '0.00'
      }
    } else {
      $ui.error('获取代理详情失败', response.message)
      agentDetail.value = agent // 降级使用列表数据
    }
  } catch (error) {
    $ui.error('获取代理详情失败', '网络错误')
    agentDetail.value = agent // 降级使用列表数据
  }
}

const closeModal = () => {
  modalState.show = false
  modalState.mode = 'create'
  modalState.agentData = {}
  agentDetail.value = {}
}

const handleFormSubmit = async (formData) => {
  isSubmitting.value = true
  try {
    if (modalState.mode === 'create') {
      const response = await api.post('/admin/agents/create/', formData)
    if (response.code === 0) {
      $ui.success('代理创建成功')
        closeModal()
        fetchAgents()
    } else {
      $ui.error('创建失败', response.message)
    }
    } else if (modalState.mode === 'edit') {
      const response = await api.post(`/admin/agents/update/${modalState.agentData.id}/`, formData)
    if (response.code === 0) {
      $ui.success('代理更新成功')
        closeModal()
      fetchAgents()
    } else {
      $ui.error('更新失败', response.message)
      }
    }
  } catch (error) {
    $ui.error('操作失败', error?.response?.data?.message || '网络错误')
  } finally {
    isSubmitting.value = false
  }
}

const handleFormError = (message) => {
  $ui.warning(message)
}

const confirmDeleteAgent = (agentId) => {
  if (window.confirm('您确定要删除这个代理账户吗？此操作不可撤销。')) {
    handleDeleteAgent(agentId)
  }
}

const handleDeleteAgent = async (agentId) => {
  try {
    const response = await api.post(`/admin/agents/delete/${agentId}/`)
    if (response.code === 0) {
      $ui.success('代理删除成功')
      fetchAgents()
    } else {
      $ui.error('删除失败', response.message)
    }
  } catch (error) {
    $ui.error('删除失败', '网络错误，请稍后重试')
  }
}

const changePage = (page) => {
  if (page > 0 && page <= pagination.value.total_pages) {
    filters.page = page
    fetchAgents()
  }
}

// 监听筛选条件变化
watch(() => filters.status, () => {
  filters.page = 1
  fetchAgents()
})

watch(() => filters.search, () => {
  filters.page = 1
  fetchAgents()
})

watch(() => filters.date_range, () => {
  filters.page = 1
  fetchAgents()
})

onMounted(fetchAgents)
</script> 
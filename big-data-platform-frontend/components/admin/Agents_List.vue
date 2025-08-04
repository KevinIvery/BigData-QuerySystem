<template>
  <div class="bg-white shadow rounded-lg overflow-hidden">
    <!-- 加载状态 -->
    <div v-if="loading" class="p-6 text-center">
      <Icon name="clarity:refresh-line" class="w-8 h-8 text-gray-400 animate-spin mx-auto" />
      <p class="mt-2 text-sm text-gray-500">正在加载代理列表...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="agents.length === 0" class="p-6 text-center">
      <Icon name="clarity:users-line" class="w-12 h-12 text-gray-400 mx-auto" />
      <h3 class="mt-2 text-sm font-medium text-gray-900">未找到代理</h3>
      <p class="mt-1 text-sm text-gray-500">尝试调整筛选条件或新建一个代理。</p>
    </div>

    <!-- 表格 -->
    <div v-else class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">代理用户</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">手机号</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">链接</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">个人底价</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">企业底价</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">累计佣金</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">已结算</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">未结算</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">用户数量</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">自定义设置</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">状态</th>
            <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">操作</th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="agent in agents" :key="agent.id" class="hover:bg-gray-50">
            <!-- 代理用户 -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="text-sm font-medium text-gray-900">{{ agent.username }}</div>
              <div class="text-xs text-gray-500">注册于: {{ new Date(agent.created_at).toLocaleDateString() }}</div>
            </td>
            
            <!-- 手机号 -->
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ agent.phone || '-' }}
            </td>
            
            <!-- 链接 -->
            <td class="px-6 py-4 whitespace-nowrap text-sm">
              <a :href="agent.full_domain" target="_blank" class="text-blue-600 hover:text-blue-900 hover:underline">
                查看
              </a>
            </td>
            
            <!-- 个人底价 -->
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              <span class="text-red-600 font-medium">¥{{ agent.personal_query?.bottom_price || agent.personal_query_price || '0.00' }}</span>
            </td>
            
            <!-- 企业底价 -->
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              <span class="text-red-600 font-medium">¥{{ agent.enterprise_query?.bottom_price || agent.enterprise_query_min_price || '0.00' }}</span>
            </td>
            
            <!-- 累计佣金 -->
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              <span class="text-blue-600 font-medium">¥{{ agent.total_commission || '0.00' }}</span>
            </td>
            
            <!-- 已结算佣金 -->
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              <span class="text-green-600 font-medium">¥{{ agent.settled_commission || '0.00' }}</span>
            </td>
            
            <!-- 未结算佣金 -->
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              <span class="text-orange-600 font-medium">¥{{ agent.unsettled_commission || '0.00' }}</span>
            </td>
            
            <!-- 用户数量 -->
            <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
              {{ agent.user_count || 0 }}
            </td>
            
            <!-- 自定义设置 -->
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="w-3 h-3 rounded-full" :class="agent.can_customize_settings ? 'bg-green-400' : 'bg-gray-300'"></div>
                <span class="ml-2 text-xs text-gray-600">
                  {{ agent.can_customize_settings ? '开启' : '关闭' }}
                </span>
              </div>
            </td>
            
            <!-- 状态 -->
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="[
                agent.is_locked ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800',
                'px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full'
              ]">
                {{ agent.is_locked ? '锁定' : '正常' }}
              </span>
            </td>
            
            <!-- 操作 -->
            <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
              <div class="flex space-x-3">
                <button @click="$emit('view-detail', agent)" class="text-blue-600 hover:text-blue-900">详情</button>
                <button @click="$emit('edit', agent)" class="text-indigo-600 hover:text-indigo-900">编辑</button>
                <button @click="$emit('delete', agent.id)" class="text-red-600 hover:text-red-900">删除</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 分页 -->
    <div v-if="pagination.total_items > 0" class="px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
      <div class="flex-1 flex justify-between sm:hidden">
        <button @click="$emit('change-page', pagination.current_page - 1)" :disabled="!pagination.has_previous" class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50">
          上一页
        </button>
        <button @click="$emit('change-page', pagination.current_page + 1)" :disabled="!pagination.has_next" class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50">
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
            <button @click="$emit('change-page', pagination.current_page - 1)" :disabled="!pagination.has_previous" class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50">
              <span class="sr-only">上一页</span>
              <Icon name="clarity:angle-line" class="h-5 w-5" :class="{'-rotate-90': true}"/>

            </button>
            <button @click="$emit('change-page', pagination.current_page + 1)" :disabled="!pagination.has_next" class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50">
              <span class="sr-only">下一页</span>
              <Icon name="clarity:angle-line" class="h-5 w-5" :class="{'rotate-90': true}" />

            </button>
          </nav>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  agents: {
    type: Array,
    default: () => []
  },
  pagination: {
    type: Object,
    default: () => ({})
  },
  loading: {
    type: Boolean,
    default: false
  }
})

defineEmits(['view-detail', 'edit', 'delete', 'change-page'])
</script> 
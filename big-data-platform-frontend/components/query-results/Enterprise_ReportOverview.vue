<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center">
        <div class="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center mr-3">
          <Icon name="ph:buildings-bold" class="w-5 h-5 text-blue-500" />
        </div>
        <h3 class="text-base font-medium text-gray-800">企业查询信息</h3>
      </div>
      <!-- 核验通过标志 -->
      <div class="flex items-center bg-green-50 text-green-600 px-3 py-1 rounded-full">
        <Icon name="ph:check-circle-bold" class="w-4 h-4 mr-1" />
        <span class="text-sm font-medium">核验通过</span>
      </div>
    </div>
    
    <div class="space-y-3">
      <!-- 企业名称 -->
      <div class="flex items-center">
        <div class="w-6 h-6 bg-gray-50 rounded flex items-center justify-center mr-3">
          <Icon name="ph:buildings-bold" class="w-3 h-3 text-gray-400" />
        </div>
        <span class="text-sm text-gray-500 w-28">企业名称：</span>
        <span class="text-sm font-medium text-gray-800">{{ userInfo?.name || userInfo?.enterprise_name || '未提供' }}</span>
      </div>
      
      <!-- 统一社会信用代码 -->
      <div class="flex items-center">
        <div class="w-6 h-6 bg-gray-50 rounded flex items-center justify-center mr-3">
          <Icon name="ph:identification-card-bold" class="w-3 h-3 text-gray-400" />
        </div>
        <span class="text-sm text-gray-500 w-28">信用代码：</span>
        <span class="text-sm font-medium text-gray-800">{{ userInfo?.id_card || userInfo?.credit_code || '未提供' }}</span>
      </div>
      
      <!-- 手机号（仅在有数据时显示） -->
      <div v-if="userInfo?.phone" class="flex items-center">
        <div class="w-6 h-6 bg-gray-50 rounded flex items-center justify-center mr-3">
          <Icon name="ph:phone-bold" class="w-3 h-3 text-gray-400" />
        </div>
        <span class="text-sm text-gray-500 w-28">联系电话：</span>
        <span class="text-sm font-medium text-gray-800">{{ userInfo.phone }}</span>
      </div>
      
      <!-- 查询类型 -->
      <div class="flex items-center">
        <div class="w-6 h-6 bg-gray-50 rounded flex items-center justify-center mr-3">
          <Icon name="ph:list-checks-bold" class="w-3 h-3 text-gray-400" />
        </div>
        <span class="text-sm text-gray-500 w-28">查询类型：</span>
        <span class="text-sm font-medium text-gray-800">{{ queryType || '企业综合查询' }}</span>
      </div>
      
      <!-- 查询时间 -->
      <div class="flex items-center">
        <div class="w-6 h-6 bg-gray-50 rounded flex items-center justify-center mr-3">
          <Icon name="ph:clock-bold" class="w-3 h-3 text-gray-400" />
        </div>
        <span class="text-sm text-gray-500 w-28">查询时间：</span>
        <span class="text-sm font-medium text-gray-800">{{ formatQueryTime(queryTime) }}</span>
      </div>
      
      <!-- 查询项目数量 -->
      <!-- <div v-if="apiResults && apiResults.length > 0" class="flex items-center">
        <div class="w-6 h-6 bg-gray-50 rounded flex items-center justify-center mr-3">
          <Icon name="ph:database-bold" class="w-3 h-3 text-gray-400" />
        </div>
        <span class="text-sm text-gray-500 w-28">查询项目：</span>
        <span class="text-sm font-medium text-gray-800">{{ apiResults.length }} 个接口</span>
      </div> -->
    </div>
  </div>
</template>

<script setup>
// 定义组件属性
const props = defineProps({
  // 用户信息
  userInfo: {
    type: Object,
    default: () => ({})
  },
  // 查询类型
  queryType: {
    type: String,
    default: ''
  },
  // 查询时间
  queryTime: {
    type: String,
    default: ''
  },
  // API结果数组
  apiResults: {
    type: Array,
    default: () => []
  }
})

// 格式化查询时间
const formatQueryTime = (timeString) => {
  if (!timeString) return '未知'
  
  try {
    const date = new Date(timeString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return '格式错误'
  }
}
</script> 

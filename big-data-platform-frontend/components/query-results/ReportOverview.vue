<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 p-5">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center">
        <div class="w-8 h-8 bg-blue-50 rounded-lg flex items-center justify-center mr-3">
          <Icon name="ph:user-circle-bold" class="w-5 h-5 text-blue-500" />
        </div>
        <h3 class="text-base font-medium text-gray-800">查询信息</h3>
      </div>
      <!-- 核验通过标志 -->
      <div class="flex items-center bg-green-50 text-green-600 px-3 py-1 rounded-full">
        <Icon name="ph:check-circle-bold" class="w-4 h-4 mr-1" />
        <span class="text-sm font-medium">核验通过</span>
      </div>
    </div>
    
    <div class="space-y-3">
      <!-- 姓名 -->
      <div class="flex items-center">
        <div class="w-6 h-6 bg-gray-50 rounded flex items-center justify-center mr-3">
          <Icon name="ph:user-bold" class="w-3 h-3 text-gray-400" />
        </div>
        <span class="text-sm text-gray-500 w-24">姓名：</span>
        <span class="text-sm font-medium text-gray-800">{{ userInfo?.name || '未提供' }}</span>
      </div>
      
      <!-- 身份证号 -->
      <div class="flex items-center">
        <div class="w-6 h-6 bg-gray-50 rounded flex items-center justify-center mr-3">
          <Icon name="ph:identification-card-bold" class="w-3 h-3 text-gray-400" />
        </div>
        <span class="text-sm text-gray-500 w-24">身份证：</span>
        <span class="text-sm font-medium text-gray-800">{{ userInfo?.id_card || '未提供' }}</span>
      </div>
      
      <!-- 手机号（仅在有数据时显示） -->
      <div v-if="userInfo?.phone" class="flex items-center">
        <div class="w-6 h-6 bg-gray-50 rounded flex items-center justify-center mr-3">
          <Icon name="ph:phone-bold" class="w-3 h-3 text-gray-400" />
        </div>
        <span class="text-sm text-gray-500 w-24">手机号：</span>
        <span class="text-sm font-medium text-gray-800">{{ userInfo.phone }}</span>
      </div>
      
      <!-- 查询时间 -->
      <div class="flex items-center">
        <div class="w-6 h-6 bg-gray-50 rounded flex items-center justify-center mr-3">
          <Icon name="ph:clock-bold" class="w-3 h-3 text-gray-400" />
        </div>
        <span class="text-sm text-gray-500 w-24">查询时间：</span>
        <span class="text-sm font-medium text-gray-800">{{ formatQueryTime(queryTime) }}</span>
      </div>
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
<template>
  <section id="marriage-result" class="bg-gradient-to-br from-pink-50 to-rose-50 rounded-xl shadow-sm border border-pink-100 p-5 mb-6">
    <!-- 头部标题 -->
    <div class="flex items-center justify-between mb-5">
      <div class="flex items-center">
        <div class="w-8 h-8 bg-pink-50 rounded-lg flex items-center justify-center mr-3">
          <Icon name="ph:heart-bold" class="w-5 h-5 text-pink-500" />
        </div>
        <div>
          <h3 class="text-base font-medium text-gray-800">婚姻状况</h3>
          <p class="text-xs text-gray-500">婚姻状况查询结果</p>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <span class="text-xs text-gray-400">API: IVYZ5733</span>
        <div v-if="data?.success" class="w-2 h-2 bg-green-500 rounded-full"></div>
        <div v-else class="w-2 h-2 bg-red-500 rounded-full"></div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-8">
      <div class="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
      <p class="text-sm text-gray-500">正在查询婚姻状况...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="text-center py-8">
      <div class="w-10 h-10 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-3">
        <Icon name="ph:warning-circle-bold" class="w-5 h-5 text-red-500" />
      </div>
      <h4 class="text-sm font-medium text-gray-800 mb-1">查询失败</h4>
      <p class="text-xs text-gray-600">{{ error }}</p>
    </div>

    <!-- 成功状态 -->
    <div v-else-if="data?.success" class="space-y-5">
      <!-- 婚姻状态主卡片 -->
      <div 
        :class="[
          'rounded-lg p-6 relative overflow-hidden',
          marriageStatusInfo.cardBg,
          marriageStatusInfo.cardBorder
        ]"
      >
        <!-- 背景装饰 -->
        <div class="absolute -top-4 -right-4 opacity-10">
          <div :class="['w-24 h-24 rounded-full', marriageStatusInfo.decorBg]"></div>
        </div>
        
        <div class="flex items-center justify-between relative ">
          <div class="flex-1">
            <div class="flex items-center space-x-3 mb-3">
              <div :class="['w-12 h-12 rounded-full flex items-center justify-center', marriageStatusInfo.iconBg]">
                <Icon name="ph:heart-bold" :class="['w-6 h-6', marriageStatusInfo.iconColor]" />
              </div>
              <div>
                <div class="flex items-center space-x-2 mb-1">
                  <h4 class="text-lg font-semibold text-gray-800">状态</h4>
                  <span :class="['text-lg font-mono px-2 py-1 bg-white bg-opacity-80 rounded border', marriageStatusInfo.statusCodeBorder, marriageStatusInfo.statusCodeColor]">{{ getStatusCode() }}</span>
                </div>
                                  <p :class="['text-sm', marriageStatusInfo.subtitleColor]">{{ marriageStatusInfo.subtitle }}</p>
              </div>
            </div>
            
            <div class="mt-4">
              <p class="text-xs text-gray-600 leading-relaxed">{{ marriageStatusInfo.description }}</p>
            </div>
          </div>
          
          <!-- 右侧SVG图标 -->
          <div class="ml-4">
            <div v-html="marriageStatusInfo.svg" class="w-16 h-16"></div>
          </div>
        </div>
      </div>

      <!-- 数据说明 -->
      <div class="bg-gradient-to-r from-amber-50 to-orange-50 rounded-lg p-4 border border-amber-200">
        <h5 class="text-sm font-medium text-amber-800 mb-3 flex items-center">
          <Icon name="ph:lightbulb-bold" class="w-4 h-4 mr-2 text-amber-600" />
          数据说明
        </h5>
        <div class="text-xs text-gray-700 space-y-2">
          <div class="flex items-start space-x-2">
            <span class="font-mono text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded flex-shrink-0">INR</span>
            <span><strong>未婚或未进行婚姻登记：</strong>可能已结婚但数据未更新，建议过段时间重试</span>
          </div>
          <div class="flex items-start space-x-2">
            <span class="font-mono text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded flex-shrink-0">IA</span>
            <span><strong>结婚：</strong>已查询到婚姻登记记录，但可能已离婚但数据未更新</span>
          </div>
          <div class="flex items-start space-x-2">
            <span class="font-mono text-xs bg-amber-100 text-amber-700 px-2 py-0.5 rounded flex-shrink-0">IB</span>
            <span><strong>离婚：</strong>已查询到离婚记录，但可能已再次结婚但数据未更新</span>
          </div>
          <div class="mt-3 pt-3 border-t border-amber-200 bg-white bg-opacity-50 rounded p-2">
            <div class="flex items-start space-x-2">
              <Icon name="ph:warning-bold" class="w-3 h-3 text-orange-600 mt-0.5 flex-shrink-0" />
              <span class="text-orange-700 font-medium">
                婚姻状况数据可能存在延迟，仅供参考，请以民政部门最新记录为准
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 无数据状态 -->
    <div v-else class="text-center py-8">
      <div class="w-10 h-10 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-3">
        <Icon name="ph:file-text-bold" class="w-5 h-5 text-gray-400" />
      </div>
      <h4 class="text-sm font-medium text-gray-800 mb-1">暂无婚姻状况数据</h4>
      <p class="text-xs text-gray-600">暂无相关婚姻状况信息，或未被公开</p>
    </div>

    <!-- 调试信息 -->
    <div v-if="showDebug" class="mt-4 p-3 bg-gray-100 rounded-lg">
      <h5 class="text-xs font-medium text-gray-800 mb-2">调试信息</h5>
      <pre class="text-xs text-gray-600 whitespace-pre-wrap">{{ JSON.stringify(data, null, 2) }}</pre>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    default: null
  },
  loading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: null
  },
  showDebug: {
    type: Boolean,
    default: false
  }
})

// 获取状态码
const getStatusCode = () => {
  try {
    const rawData = props.data?.data?.data?.data
    if (!rawData) return 'UNKNOWN'
    
    // 提取状态码 (INR, IA, IB等)
    const match = rawData.match(/^([A-Z]+)/)
    return match ? match[1] : 'UNKNOWN'
  } catch (error) {
    return 'UNKNOWN'
  }
}



// 婚姻状态信息配置
const marriageStatusInfo = computed(() => {
  const statusCode = getStatusCode()
  
  switch (statusCode) {
    case 'IA':
      return {
        subtitle: '查询到婚姻登记记录',
        description: 'IA状态表示查询到婚姻登记记录，但婚姻状况可能已发生变化，数据存在延迟，请以民政部门最新记录为准。',
        cardBg: 'bg-gradient-to-br from-rose-50 to-pink-50',
        cardBorder: 'border border-rose-200',
        decorBg: 'bg-rose-200',
        iconBg: 'bg-rose-100',
        iconColor: 'text-rose-600',
        statusCodeBorder: 'border-rose-200',
        statusCodeColor: 'text-rose-700',
        subtitleColor: 'text-rose-700',
        svg: `
          <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="32" cy="32" r="30" fill="#E11D48" opacity="0.15"/>
            <path d="M32 20C28 16 20 16 20 24C20 32 32 44 32 44C32 44 44 32 44 24C44 16 36 16 32 20Z" fill="#E11D48" opacity="0.8"/>
            <circle cx="32" cy="26" r="3" fill="white"/>
          </svg>
        `
      }
    case 'IB':
      return {
        subtitle: '查询到离婚记录',
        description: 'IB状态表示查询到离婚记录，但婚姻状况可能已发生变化，数据存在延迟，请以民政部门最新记录为准。',
        cardBg: 'bg-gradient-to-br from-emerald-50 to-green-50',
        cardBorder: 'border border-emerald-200',
        decorBg: 'bg-emerald-200',
        iconBg: 'bg-emerald-100',
        iconColor: 'text-emerald-600',
        statusCodeBorder: 'border-emerald-200',
        statusCodeColor: 'text-emerald-700',
        subtitleColor: 'text-emerald-700',
        svg: `
          <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="32" cy="32" r="30" fill="#059669" opacity="0.15"/>
            <path d="M32 20C28 16 20 16 20 24C20 32 32 44 32 44C32 44 44 32 44 24C44 16 36 16 32 20Z" fill="#059669" opacity="0.3"/>
            <path d="M28 24L36 32M36 24L28 32" stroke="#059669" stroke-width="2" stroke-linecap="round"/>
          </svg>
        `
      }
    case 'INR':
    default:
      return {
        subtitle: '未查询到婚姻登记记录',
        description: 'INR状态表示未查询到婚姻登记记录，但可能已结婚但数据未更新，建议过段时间重试或以民政部门最新记录为准。',
        cardBg: 'bg-gradient-to-br from-blue-50 to-indigo-50',
        cardBorder: 'border border-blue-200',
        decorBg: 'bg-blue-200',
        iconBg: 'bg-blue-100',
        iconColor: 'text-blue-600',
        statusCodeBorder: 'border-blue-200',
        statusCodeColor: 'text-blue-700',
        subtitleColor: 'text-blue-700',
        svg: `
          <svg viewBox="0 0 64 64" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="32" cy="32" r="30" fill="#3B82F6" opacity="0.15"/>
            <circle cx="32" cy="26" r="8" fill="#3B82F6" opacity="0.6"/>
            <path d="M20 48C20 40 25 36 32 36C39 36 44 40 44 48" stroke="#3B82F6" stroke-width="3" stroke-linecap="round"/>
          </svg>
        `
      }
  }
})
</script>

<style scoped>
.transition-colors {
  transition-property: color, background-color, border-color;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 200ms;
}

/* 渐变背景动画 */
.bg-gradient-to-br {
  background-size: 200% 200%;
  animation: gradientShift 6s ease infinite;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

/* 响应式调整 */
@media (max-width: 640px) {
  .overflow-x-auto {
    -webkit-overflow-scrolling: touch;
  }
}
</style> 
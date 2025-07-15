<template>
  <div class="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center p-4">
    <!-- Back Button -->
    <div class="absolute top-4 left-4 z-10">
      <button @click="$router.back()" class="flex items-center space-x-2 text-gray-400 hover:text-white transition-colors">
        <Icon name="ph:arrow-left-bold" class="w-5 h-5" />
        <span>返回</span>
      </button>
    </div>
    
    <!-- Agency Promotion Card -->
    <div class="w-full max-w-2xl p-8 rounded-3xl shadow-2xl bg-gradient-to-r from-gray-800 via-gray-900 to-black relative overflow-hidden border border-gray-700">
      <div class="absolute inset-0 bg-grid-pattern opacity-10"></div>
      <div class="absolute -top-20 -right-20 w-60 h-60 bg-indigo-600/30 rounded-full filter blur-3xl animate-pulse"></div>
      <div class="absolute -bottom-20 -left-20 w-60 h-60 bg-purple-600/20 rounded-full filter blur-3xl animate-pulse animation-delay-2000"></div>

      <div class="relative z-10 text-center">
        <h1 class="text-4xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-br from-white to-gray-400 mb-2">
          成为数据服务代理
        </h1>
        <p class="text-lg text-gray-400 max-w-lg mx-auto">
          加入我们的数据服务网络，开启您的数据服务事业，共享平台发展红利。
        </p>

        <div class="grid grid-cols-1 sm:grid-cols-2 gap-6 my-10 text-left">
          <div v-for="feature in agencyFeatures" :key="feature.text" class="flex items-center space-x-4 p-4 rounded-xl bg-white/5 backdrop-blur-sm border border-white/10">
            <div class="w-10 h-10 rounded-full bg-indigo-500/20 flex-shrink-0 flex items-center justify-center">
              <Icon :name="feature.icon" class="w-6 h-6 text-indigo-300" />
            </div>
            <div>
              <h4 class="font-semibold text-gray-100">{{ feature.text }}</h4>
              <p class="text-xs text-gray-400">{{ feature.desc }}</p>
            </div>
          </div>
        </div>

        <!-- 根据申请状态显示不同的按钮 -->
        <div v-if="checkingStatus" class="w-full sm:w-auto bg-gray-600 text-white font-bold px-10 py-4 rounded-lg shadow-lg opacity-50 cursor-not-allowed">
          <Icon name="ph:spinner-gap" class="w-5 h-5 animate-spin inline mr-2" />
          检查申请状态...
        </div>
        
        <button v-else-if="!hasApplied" 
          @click="isAgencyModalVisible = true" 
          class="w-full sm:w-auto bg-indigo-600 text-white font-bold px-10 py-4 rounded-lg shadow-lg hover:bg-indigo-700 transition-all duration-300 transform hover:scale-105">
          立即申请
        </button>
        
        <div v-else class="w-full sm:w-auto bg-green-600 text-white font-bold px-10 py-4 rounded-lg shadow-lg cursor-default">
          <Icon name="ph:check-circle" class="w-5 h-5 inline mr-2" />
          已提交申请，请等待管理员联系您
        </div>
        
        <!-- 申请成功后的提示信息 -->
        <div v-if="hasApplied && applicationTime" class="mt-4 text-sm text-gray-400">
          申请时间：{{ formatDateTime(applicationTime) }}
        </div>
      </div>
    </div>
  </div>

  <!-- Agency Application Modal -->
  <AgencyApplicationModal 
    v-if="isAgencyModalVisible" 
    @close="handleModalClose" />
</template>

<script setup>
import { ref, onMounted } from 'vue'
import AgencyApplicationModal from '~/components/frontend/AgencyApplicationModal.vue'

definePageMeta({
  layout: false // 使用独立布局，不带底部菜单
})

const api = useApi()
const isAgencyModalVisible = ref(false)
const checkingStatus = ref(true)
const hasApplied = ref(false)
const applicationTime = ref(null)

const agencyFeatures = [
  { text: '独立推广与分成', desc: '获取专属推广链接，享受高额佣金分成。', icon: 'ph:rocket-launch-duotone' },
  { text: '自定义价格体系', desc: '在成本价基础上，自由设定您的客户价。', icon: 'ph:currency-cny-duotone' },
  { text: '专属后台管理', desc: '独立的管理后台，轻松管理您的客户与订单。', icon: 'ph:squares-four-duotone' },
  { text: '自定义品牌形象', desc: '可配置独立的Logo和站点信息，打造个人品牌。', icon: 'ph:paint-brush-duotone' },
]

// 检查用户申请状态
const checkApplicationStatus = async () => {
  try {
    checkingStatus.value = true
    console.log('【Agency Page】检查申请状态')
    
    const response = await api.get('/frontend/check-agency-application-status/')
    
    console.log('【Agency Page】申请状态响应:', response)
    
    if (response.code === 0 && response.data) {
      hasApplied.value = response.data.has_applied
      applicationTime.value = response.data.application_time
    }
    
  } catch (error) {
    console.error('【Agency Page】检查申请状态失败:', error)
    
    // 如果是认证错误，跳转到登录页面
    if (error.status === 401 || error.data?.code === 401) {
      console.log('【Agency Page】用户未登录，跳转到登录页面')
      await navigateTo('/login')
      return
    }
    
    // 其他错误，默认允许申请
    hasApplied.value = false
  } finally {
    checkingStatus.value = false
  }
}

// 处理模态框关闭事件
const handleModalClose = () => {
  isAgencyModalVisible.value = false
  // 重新检查申请状态，以防用户刚刚提交了申请
  checkApplicationStatus()
}

// 格式化日期时间
const formatDateTime = (dateTimeString) => {
  if (!dateTimeString) return ''
  
  try {
    const date = new Date(dateTimeString)
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return dateTimeString
  }
}

// 页面加载时检查申请状态
onMounted(() => {
  checkApplicationStatus()
})
</script>

<style scoped>
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}

.animate-pulse {
  animation: blob 7s infinite;
}
.animation-delay-2000 { animation-delay: 2s; }

.bg-grid-pattern {
  background-image: linear-gradient(rgba(255, 255, 255, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.05) 1px, transparent 1px);
  background-size: 20px 20px;
}
</style> 
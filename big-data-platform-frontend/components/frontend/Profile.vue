<template>
  <div class="min-h-screen bg-transparent pb-8">
    <!-- Enhanced Header Card with Animated Background -->
    <div class="p-6 md:p-8 rounded-b-3xl shadow-xl relative overflow-hidden">
      <!-- Background elements -->
      <div class="absolute inset-0 z-0 bg-gradient-to-br from-blue-500 via-purple-600 to-indigo-700">
        <div class="absolute top-0 left-0 w-32 h-32 bg-white/10 rounded-full filter blur-xl animate-blob animation-delay-4000"></div>
        <div class="absolute bottom-0 right-0 w-40 h-40 bg-white/10 rounded-full filter blur-xl animate-blob animation-delay-2000"></div>
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-24 h-24 bg-white/5 rounded-full filter blur-lg animate-pulse"></div>
        <div class="absolute inset-0 opacity-10" style="background-image: radial-gradient(circle at 1px 1px, white 1px, transparent 0); background-size: 20px 20px;"></div>
      </div>
      
      <!-- Dynamic User Info -->
      <div class="relative z-10 flex items-center space-x-6">
        <div class="relative">
          <div class="absolute -inset-2 rounded-full opacity-75 animate-pulse" :class="loginState.isLoggedIn ? 'bg-gradient-to-r from-cyan-400 to-blue-400' : 'bg-gray-400'"></div>
          <div class="relative w-20 h-20 rounded-full flex items-center justify-center border-3 border-white/40 shadow-lg backdrop-blur-sm" :class="loginState.isLoggedIn ? 'bg-white/20' : 'bg-gray-500/20'">
            <Icon name="ph:user-bold" class="w-10 h-10 text-white drop-shadow-lg" />
          </div>
          <div v-if="loginState.isLoggedIn" class="absolute -bottom-1 -right-1 w-6 h-6 bg-green-400 rounded-full border-2 border-white shadow-lg flex items-center justify-center">
            <div class="w-2 h-2 bg-white rounded-full animate-pulse"></div>
          </div>
        </div> 
        
        <div v-if="loginState.isLoggedIn && loginState.user" class="flex-1">
          <div class="flex items-center space-x-3 mb-2">
            <h2 class="text-2xl font-bold tracking-wide text-white drop-shadow-lg">用户 {{ loginState.user.username }}</h2>
            <div class="px-3 py-1 bg-white/20 rounded-full border border-white/30">
              <span class="text-xs font-medium text-white">VIP</span>
            </div>
          </div>
          <p class="text-blue-100 text-sm opacity-90 mb-2">尊贵的用户</p>
        </div>
        <div v-else class="flex-1">
           <h2 class="text-2xl font-bold tracking-wide text-white drop-shadow-lg">请先登录</h2>
           <p class="text-blue-100 text-sm opacity-90 mb-2">登录后查看更多信息</p>
        </div>
      </div>
    </div>

    <!-- Dynamic Call to Action Card -->
    <div class="p-4 -mt-10 relative z-20">
      <div class="bg-white/70 backdrop-blur-md border border-gray-200/50 p-5 rounded-2xl shadow-xl flex items-center justify-between">
        <div v-if="loginState.isLoggedIn">
          <h3 class="font-bold text-lg text-gray-800">开启精准查询</h3>
          <p class="text-sm text-gray-600 mt-1">即时获取全面的数据报告</p>
        </div>
        <div v-else>
           <h3 class="font-bold text-lg text-gray-800">欢迎回来</h3>
           <p class="text-sm text-gray-600 mt-1">登录以使用全部功能</p>
        </div>
        <button @click="handleCtaClick" class="text-white font-semibold px-5 py-2 rounded-lg shadow-md transition-colors" :class="loginState.isLoggedIn ? 'bg-blue-500 hover:bg-blue-600' : 'bg-green-500 hover:bg-green-600'">
          {{ loginState.isLoggedIn ? '立即查询' : '立即登录' }}
        </button>
      </div>
    </div>
    
    <!-- Main Services Section -->
    <div class="grid grid-cols-2 gap-4 px-4">
      <div v-for="item in mainServices" :key="item.title" @click="handleServiceClick(item)" class="bg-white/70 backdrop-blur-md border border-gray-200/50 p-4 rounded-xl shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all flex flex-col items-center justify-center space-y-2 cursor-pointer">
        <div :class="[item.color, 'w-12 h-12 rounded-full flex items-center justify-center']">
          <Icon :name="item.icon" class="w-7 h-7 text-white" />
        </div>
        <span class="font-semibold text-gray-800 text-sm">{{ item.title }}</span>
      </div>
    </div>

    <!-- Dynamic Menu Items List -->
    <div class="px-4 pt-4 pb-4 space-y-3">
      <div v-for="item in menuItems" :key="item.title" @click="handleMenuItemClick(item)" class="bg-white/70 backdrop-blur-md border border-gray-200/50 p-4 rounded-xl shadow-sm hover:shadow-md transition-shadow flex items-center justify-between cursor-pointer">
        <div class="flex items-center space-x-4">
          <div :class="[item.color, 'w-10 h-10 rounded-lg flex items-center justify-center']">
            <Icon :name="item.icon" class="w-6 h-6 text-white" />
          </div>
          <span class="font-medium text-gray-700">{{ item.title }}</span>
        </div>
        <Icon name="ph:caret-right-bold" class="w-5 h-5 text-gray-400" />
      </div>
    </div>
  </div>

  <!-- All Modals -->
  <!-- 1. 提升 z-index 层级 -->
  <div v-if="isAgreementViewerVisible" class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
    <div class="bg-white shadow-2xl w-full max-w-3xl max-h-[70vh] flex flex-col relative">
      <button @click="closeAgreementViewer" class="absolute top-3 right-3 text-gray-500 hover:text-gray-700 z-10 p-2 rounded-full bg-gray-100/50 hover:bg-gray-200/80 transition-colors">
        <Icon name="ph:x-bold" class="w-5 h-5" />
      </button>

      <main class="flex-1 overflow-y-auto px-8 pt-8 pb-8 text-sm text-gray-700 agreement-content">
        <component :is="activeAgreementComponent" />
      </main>
    </div>
  </div>

  <Transition name="modal-fade">
    <div v-if="isAccountSettingsModalVisible" @click.self="isAccountSettingsModalVisible = false" class="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black bg-opacity-50 p-4 pt-0 sm:p-4">
      <div class="w-full max-w-md bg-white rounded-t-2xl sm:rounded-lg shadow-xl">
        <div class="p-2">
          <button @click="handleLogout" class="w-full text-center py-3 text-gray-800 font-medium rounded-lg hover:bg-gray-100">退出登录</button>
          <button @click="openDeactivationConfirm" class="w-full text-center py-3 text-red-500 font-medium rounded-lg hover:bg-red-50">注销账户</button>
        </div>
        <div class="border-t border-gray-200 p-2">
          <button @click="isAccountSettingsModalVisible = false" class="w-full text-center py-3 text-gray-800 font-medium rounded-lg hover:bg-gray-100">取消</button>
        </div>
      </div>
    </div>
  </Transition>

  <Transition name="modal-fade">
    <div v-if="isDeactivationConfirmModalVisible" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 p-4">
      <div class="w-full max-w-sm bg-white rounded-2xl shadow-xl p-6">
        <h3 class="text-lg font-bold text-gray-900">确认注销账户</h3>
        <p class="mt-2 text-sm text-gray-600">
          您的账户将被标记为注销状态。7天后若未登录，您的所有数据将被永久删除且无法恢复。
        </p>
        <div class="mt-6 flex justify-end space-x-3">
          <button @click="isDeactivationConfirmModalVisible = false" class="px-5 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 text-sm font-medium">取消</button>
          <button @click="handleDeactivationConfirm" class="px-5 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm font-medium">确定注销</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import UserAgreement from '../agreements/UserAgreement.vue'
import PrivacyPolicy from '../agreements/PrivacyPolicy.vue'

const emit = defineEmits(['navigateToQuery', 'logout', 'show-login-prompt'])
const router = useRouter()

const props = defineProps({
  siteData: { type: Object, required: true },
  isLoading: { type: Boolean, default: false },
  loginState: { type: Object, required: true }
})

const isAccountSettingsModalVisible = ref(false)
const isDeactivationConfirmModalVisible = ref(false)
const isAgreementViewerVisible = ref(false)
const activeAgreementComponent = ref(null)

const handleCtaClick = () => {
  if (props.loginState.isLoggedIn) {
    emit('navigateToQuery')
  } else {
    emit('show-login-prompt')
  }
}

const handleServiceClick = (item) => {
  if (!props.loginState.isLoggedIn) {
    emit('show-login-prompt')
    return
  }
  
  if (item.action === 'order_history') {
    router.push('/order-history')
  } else if (item.action === 'query_history') {
    router.push('/query-history')
  }
}

const handleLogout = () => {
  isAccountSettingsModalVisible.value = false
  emit('logout')
}

const openDeactivationConfirm = () => {
  isAccountSettingsModalVisible.value = false
  isDeactivationConfirmModalVisible.value = true
}

const handleDeactivationConfirm = async () => {
  isDeactivationConfirmModalVisible.value = false
  
  try {
    const { $ui } = useNuxtApp()
    const api = useApi()
    await api.post('/frontend/deactivate-account/')
    $ui.success('账户注销成功', '您将被退出登录')
    // 延迟一下再退出登录，让用户看到成功提示
    setTimeout(() => {
      emit('logout')
    }, 1000)
  } catch (error) {
    // 错误已由API工具自动处理和显示
    console.error('注销账户失败:', error)
  }
}

const handleMenuItemClick = (item) => {
  if (item.action === 'settings') {
    isAccountSettingsModalVisible.value = true
  } else if (item.action === 'contact_cs') {
    window.open(item.url, '_blank')
  } else if (item.action === 'view_agreement') {
    activeAgreementComponent.value = item.component
    isAgreementViewerVisible.value = true
  } else if (item.action === 'navigate') {
    router.push(item.path)
  }
}

const closeAgreementViewer = () => {
  isAgreementViewerVisible.value = false
  activeAgreementComponent.value = null
}

const mainServices = computed(() => [
  { title: '订单记录', icon: 'ph:scroll-duotone', color: 'bg-blue-500', action: 'order_history' },
  { title: '历史报告', icon: 'ph:file-text-duotone', color: 'bg-indigo-500', action: 'query_history' },
])

const menuItems = computed(() => {
  const items = [
    { title: '申请代理', icon: 'ph:star-duotone', color: 'bg-amber-500', action: 'navigate', path: '/agency' },
    { title: '服务协议', icon: 'ph:book-bookmark-duotone', color: 'bg-teal-500', action: 'view_agreement', component: UserAgreement },
    { title: '隐私政策', icon: 'ph:shield-check-duotone', color: 'bg-purple-500', action: 'view_agreement', component: PrivacyPolicy },
  ]
  
  if (props.siteData.system_config?.customer_service_url) {
    items.unshift({ 
      title: '联系客服', 
      icon: 'ph:chats-circle-duotone', 
      color: 'bg-green-500',
      action: 'contact_cs',
      url: props.siteData.system_config.customer_service_url
    })
  }

  if (props.loginState.isLoggedIn) {
    items.push({ title: '账户设置', icon: 'ph:gear-six-duotone', color: 'bg-gray-600', action: 'settings' })
  }

  return items
})
</script>

<style scoped>
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}
.animation-delay-2000 { animation-delay: 2s; }
.animation-delay-4000 { animation-delay: 4s; }
.animate-blob {
  animation: blob 7s infinite;
}
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.agreement-content::-webkit-scrollbar {
  width: 6px;
}
.agreement-content::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}
.agreement-content::-webkit-scrollbar-track {
  background: #f1f5f9;
}
</style> 
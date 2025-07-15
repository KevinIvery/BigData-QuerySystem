<template>
  <div class="w-full max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
    <!-- New Header -->
    <header class="py-8 relative">
      <!-- 背景装饰 -->
      <div class="absolute inset-0 -z-10 overflow-hidden">
        <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-60 h-60 bg-gradient-to-r from-blue-200/30 via-purple-200/30 to-cyan-200/30 rounded-full filter blur-3xl animate-pulse"></div>
      </div>
      
      <!-- Logo和描述区域 -->
      <div class="text-center space-y-4">
        <!-- Logo -->
        <div class="h-16 flex items-center justify-center">
            <!-- 如果有logo图片就显示图片，否则显示默认SVG -->
            <img 
              v-if="logoUrl" 
              :src="logoUrl" 
              :alt="systemConfig.site_title || '平台Logo'"
              class="h-16 w-auto object-contain"
            />
            <!-- 默认SVG Logo -->
            <div v-else class="w-8 h-8 relative">
              <!-- 外圈旋转动画 -->
              <div class="absolute inset-0 border-2 border-transparent border-t-blue-500 border-r-purple-500 rounded-full animate-spin"></div>
              <div class="absolute inset-1 border-2 border-transparent border-b-cyan-500 border-l-indigo-500 rounded-full animate-spin-reverse"></div>
              
              <!-- 中心图标 -->
              <div class="absolute inset-0 flex items-center justify-center">
                <div class="w-5 h-5 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center shadow-lg">
                  <svg class="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2L13.09 5.26L16 4L14.74 7.09L18 8L14.74 10.91L16 14L13.09 12.74L12 16L10.91 12.74L8 14L9.26 10.91L6 8L9.26 7.09L8 4L10.91 5.26L12 2Z"/>
                    <circle cx="12" cy="12" r="2"/>
                  </svg>
                </div>
              </div>
            </div>
        </div>
        
        <!-- 描述区域 - 支持后台HTML配置 -->
        <div>
          <!-- 直接显示后台配置的HTML，不添加额外样式 -->
          <div 
            v-if="systemConfig.query_entrance_desc" 
            v-html="systemConfig.query_entrance_desc"
          ></div>
          <!-- 默认样式 -->
          <div v-else class="space-y-3">
            <h2 class="text-xl font-semibold text-gray-800 tracking-wide">{{ systemConfig.description || '专业的大数据查询服务平台' }}</h2>
            <div class="flex items-center justify-center space-x-6 text-sm text-gray-600">
              <span class="flex items-center space-x-1.5 bg-green-50 px-3 py-1.5 rounded-full">
                <svg class="w-4 h-4 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                <span class="font-medium">安全可靠</span>
              </span>
              <span class="flex items-center space-x-1.5 bg-blue-50 px-3 py-1.5 rounded-full">
                <svg class="w-4 h-4 text-blue-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clip-rule="evenodd"/>
                </svg>
                <span class="font-medium">极速查询</span>
              </span>
              <span class="flex items-center space-x-1.5 bg-purple-50 px-3 py-1.5 rounded-full">
                <svg class="w-4 h-4 text-purple-500" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <span class="font-medium">精准数据</span>
              </span>
            </div>
          </div>
        </div>
      </div>
    </header>
    
    <!-- Query Card -->
    <div class="bg-white/70 backdrop-blur-md rounded-2xl shadow-xl overflow-hidden border border-gray-200/50">
      <!-- Tabs -->
      <div class="flex bg-gray-100/50" v-if="personalQueryConfig && enterpriseQueryConfig">
        <button @click="activeQueryTab = 'personal'" :class="getTabClass('personal')">
          <Icon name="ph:user-circle-bold" class="w-5 h-5 mr-2"/> 个人查询
        </button>
        <button @click="activeQueryTab = 'enterprise'" :class="getTabClass('enterprise')">
          <Icon name="ph:buildings-bold" class="w-5 h-5 mr-2"/> 企业查询
        </button>
      </div>

      <!-- Form Container -->
      <div class="p-6 md:p-8">
        <!-- Personal Query -->
        <div v-if="activeQueryTab === 'personal' && personalQueryConfig">
          <form @submit.prevent="handlePersonalQuery" class="space-y-5">
            <input v-model="personalForm.name" type="text" placeholder="请输入姓名" 
              class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow" required>
            <input v-model="personalForm.idCard" type="text"  placeholder="请输入身份证号码" 
              class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow" required>
            
            <!-- 手机号输入框：三要素验证 或 包含需要手机号的接口时显示 --> 
            <div v-if="personalQueryConfig.requires_mobile" class="space-y-3">
              <!-- 手机号输入框 -->
              <div v-if="personalQueryConfig.requires_sms_verification" class="flex space-x-3">
                <input v-model="personalForm.phone" type="tel" placeholder="请输入手机号码" 
                  class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow flex-1" required>
                <button @click.prevent="sendVerificationCodeForQuery" :disabled="isCodeSent || isSendingCode" class="px-4 py-2 rounded-xl font-semibold transition-colors whitespace-nowrap"
                  :class="isCodeSent ? 'bg-gray-200 text-gray-500' : 'bg-blue-100 text-blue-700 hover:bg-blue-200'">
                  {{ isSendingCode ? '发送中...' : (isCodeSent ? `${countdown}s` : '获取验证码') }}
                </button>
              </div>
              
              <!-- 仅需要手机号但不需要验证码的情况 -->
              <input v-else v-model="personalForm.phone" type="tel" placeholder="请输入手机号码" 
                class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow" required>
            </div>
            
            <!-- 验证码输入框：仅在三要素验证时显示 -->
            <input v-if="personalQueryConfig.requires_sms_verification" v-model="personalForm.code" type="text" maxlength="6" placeholder="请输入验证码" 
              class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow" required>
            
             <!-- Agreements Checkbox -->
            <div class="space-y-2 pt-2">
              <div class="flex items-start space-x-3">
                <input type="checkbox" v-model="personalAgreementsAccepted[0]" id="personal-agreements-1" class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 flex-shrink-0">
                <label for="personal-agreements-1" class="text-xs text-gray-600">
                  我已阅读并同意
                  <template v-for="(agreement, index) in agreementConfig.personal.slice(0, 2)" :key="agreement.key">
                    <a @click.prevent="viewAgreement(agreement)" class="text-blue-600 hover:underline cursor-pointer">《{{ agreement.title }}》</a>
                    <span v-if="index < 1">、</span>
                  </template>
                </label>
              </div>
              <div class="flex items-start space-x-3">
                <input type="checkbox" v-model="personalAgreementsAccepted[1]" id="personal-agreements-2" class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 flex-shrink-0">
                <label for="personal-agreements-2" class="text-xs text-gray-600">
                  并同意
                  <template v-for="(agreement, index) in agreementConfig.personal.slice(2, 4)" :key="agreement.key">
                    <a @click.prevent="viewAgreement(agreement)" class="text-blue-600 hover:underline cursor-pointer">《{{ agreement.title }}》</a>
                    <span v-if="index < 1">、</span>
                  </template>
                </label>
              </div>
            </div>

            <button type="submit" :disabled="!allPersonalAgreementsAccepted" 
              class="w-full text-white py-3 px-6 rounded-xl font-bold tracking-wider transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
              :class="allPersonalAgreementsAccepted ? 'bg-blue-500 hover:bg-blue-600' : 'bg-gray-400'">
              立即查询 <span v-if="showQueryPrice"> ({{ personalQueryConfig.customer_price }} 元)</span>
            </button>
          </form>
        </div>
        
        <!-- Enterprise Query -->
        <div v-if="activeQueryTab === 'enterprise' && enterpriseQueryConfig">
           <form @submit.prevent="handleEnterpriseQuery" class="space-y-5">
            <input v-model="enterpriseForm.companyName" type="text" placeholder="请输入企业全称" 
              class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow" required>
            <input v-model="enterpriseForm.creditCode" type="text" placeholder="请输入统一社会信用代码" 
              class="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-shadow" required>

            <!-- Agreements Checkbox -->
            <div class="space-y-2 pt-2">
               <div class="flex items-start space-x-3">
                <input type="checkbox" v-model="enterpriseAgreementsAccepted[0]" id="enterprise-agreements-1" class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 flex-shrink-0">
                <label for="enterprise-agreements-1" class="text-xs text-gray-600">
                  我已阅读并同意
                  <template v-for="(agreement, index) in agreementConfig.enterprise.slice(0, 2)" :key="agreement.key">
                    <a @click.prevent="viewAgreement(agreement)" class="text-blue-600 hover:underline cursor-pointer">《{{ agreement.title }}》</a>
                    <span v-if="index < 1">、</span>
                  </template>
                </label>
              </div>
              <div class="flex items-start space-x-3">
                <input type="checkbox" v-model="enterpriseAgreementsAccepted[1]" id="enterprise-agreements-2" class="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 flex-shrink-0">
                <label for="enterprise-agreements-2" class="text-xs text-gray-600">
                  并同意
                  <template v-for="(agreement, index) in agreementConfig.enterprise.slice(2, 4)" :key="agreement.key">
                    <a @click.prevent="viewAgreement(agreement)" class="text-blue-600 hover:underline cursor-pointer">《{{ agreement.title }}》</a>
                    <span v-if="index < 1">、</span>
                  </template>
                </label>
              </div>
            </div>
            
            <button type="submit" :disabled="!allEnterpriseAgreementsAccepted"
              class="w-full text-white py-3 px-6 rounded-xl font-bold tracking-wider transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
              :class="allEnterpriseAgreementsAccepted ? 'bg-indigo-500 hover:bg-indigo-600' : 'bg-gray-400'">
              立即查询 <span v-if="showQueryPrice"> ({{ enterpriseQueryConfig.customer_price }} 元)</span>
            </button>
          </form>
        </div>
      </div>
    </div>
    
    <!-- Included APIs Section -->
    <div class="mt-8" v-if="currentIncludedApis.length > 0">
      <QueryItemsGrid :api-list="currentIncludedApis" :query-type="getQueryType()" />
    </div>

    <!-- Footer -->
    <footer v-if="systemConfig.footer_copyright" class="mt-2 pt-8 border-t border-gray-200/80">
      <div v-html="systemConfig.footer_copyright" class="text-xs text-gray-500 text-center space-y-2"></div>
    </footer>
  </div>

  <!-- Agreement Viewer Modal -->
  <div v-if="isAgreementViewerVisible" class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50 p-4">
    <div class="bg-white shadow-2xl w-full max-w-3xl max-h-[70vh] flex flex-col relative ">
      <button @click="closeAgreementViewer" class="absolute top-3 right-3 text-gray-500 hover:text-gray-700 z-10 p-2 rounded-full bg-gray-100/50 hover:bg-gray-200/80 transition-colors">
        <Icon name="ph:x-bold" class="w-5 h-5" />
      </button>

      <main class="flex-1 overflow-y-auto px-8 pt-8 pb-8 text-sm text-gray-700 agreement-content">
        <component :is="activeAgreementComponent" 
                   :name="personalForm.name" 
                   :idCard="personalForm.idCard" />
      </main>
    </div>
  </div>

  <!-- 支付确认模态框 -->
  <PaymentConfirmModal
    :is-visible="showPaymentModal"
    :order="currentOrder"
    @confirm="handlePaymentConfirm"
    @cancel="cancelPayment"
  />

  <!-- Toast 消息 -->
  <SimpleToast
    v-if="currentToast"
    :message="currentToast.message"
    :type="currentToast.type"
    :duration="currentToast.duration"
    @close="currentToast = null"
  />
 
</template>

<script setup>
import { computed, ref, onMounted, watchEffect } from 'vue'
import QueryItemsGrid from './QueryItemsGrid.vue'
import UserAgreement from '../agreements/UserAgreement.vue'
import PrivacyPolicy from '../agreements/PrivacyPolicy.vue'
import Disclaimer from '../agreements/Disclaimer.vue'
import DataAuthorization from '../agreements/DataAuthorization.vue' 
import EnterpriseComplianceCommitment from '../agreements/EnterpriseComplianceCommitment.vue'
import PaymentConfirmModal from './PaymentConfirmModal.vue'
import SimpleToast from './SimpleToast.vue'

const props = defineProps({
  siteData: { type: Object, required: true, default: () => ({ system_config: {}, query_configs: [] }) },
  isLoading: { type: Boolean, default: false },
  loginState: { type: Object, required: true } // <-- 1. 接收登录状态
})

const emit = defineEmits(['show-login-prompt']) // <-- 2. 定义事件

const activeQueryTab = ref('')
const personalForm = ref({ name: '', idCard: '', phone: '', code: '' })
const enterpriseForm = ref({ companyName: '', creditCode: '' })

const isCodeSent = ref(false)
const isSendingCode = ref(false)
const countdown = ref(60)
const toastRef = ref(null)

// Agreement State
const personalAgreementsAccepted = ref([false, false])
const enterpriseAgreementsAccepted = ref([false, false])
const isAgreementViewerVisible = ref(false)
const activeAgreementComponent = ref(null)
const activeAgreementTitle = ref('')

const allPersonalAgreementsAccepted = computed(() => personalAgreementsAccepted.value.every(v => v))
const allEnterpriseAgreementsAccepted = computed(() => enterpriseAgreementsAccepted.value.every(v => v))


const systemConfig = computed(() => props.siteData.system_config || {})
const queryConfigs = computed(() => props.siteData.query_configs || [])
const showQueryPrice = computed(() => systemConfig.value.show_query_price)

// Logo URL拼接逻辑
const config = useRuntimeConfig()
const logoUrl = computed(() => {
  if (!systemConfig.value.logo) {
    return ''
  }
  // 如果已经是完整的URL，直接返回
  if (systemConfig.value.logo.startsWith('http')) {
    return systemConfig.value.logo
  }
  // 对于相对路径，使用运行时配置的URL前缀进行拼接
  console.log('fileUrl配置:', config.public.fileUrl)
  console.log('原始logo路径:', systemConfig.value.logo)
  const fullUrl = (config.public.fileUrl || '') + systemConfig.value.logo
  console.log('拼接后的logo URL:', fullUrl)
  return fullUrl
})

// 调试信息
console.log('Home组件 - 系统配置:', systemConfig.value)
console.log('Home组件 - 查询配置:', queryConfigs.value)
console.log('Home组件 - Logo路径:', systemConfig.value.logo)
console.log('Home组件 - 查询入口描述:', systemConfig.value.query_entrance_desc)

const personalQueryConfig = computed(() => queryConfigs.value.find(c => c.config_name === '个人查询配置'))
const enterpriseQueryConfig = computed(() => queryConfigs.value.find(c => c.config_name === '企业查询配置'))

// 3. 使用 watchEffect 替代 onMounted 来响应式地设置初始Tab
watchEffect(() => {
  // 仅在 activeQueryTab 未被设置时执行
  if (!activeQueryTab.value) {
    if (personalQueryConfig.value) {
      console.log('【Home】检测到个人查询配置，自动激活Tab。')
      activeQueryTab.value = 'personal'
    } else if (enterpriseQueryConfig.value) {
      console.log('【Home】检测到企业查询配置，自动激活Tab。')
      activeQueryTab.value = 'enterprise'
    }
  }
})

// 配置验证
const validateConfigs = () => {
  console.log('=== 配置验证开始 ===')
  
  // 验证个人查询配置
  if (personalQueryConfig.value) {
    console.log('✅ 个人查询配置存在')
    console.log('  - 验证方式:', personalQueryConfig.value.category)
    console.log('  - 价格:', personalQueryConfig.value.customer_price)
    console.log('  - 包含API:', personalQueryConfig.value.included_apis)
    console.log('  - 需要手机号:', personalQueryConfig.value.requires_mobile)
    console.log('  - 需要短信验证:', personalQueryConfig.value.requires_sms_verification)
    
    if (personalQueryConfig.value.requires_sms_verification) {
      console.log('  ✅ 三要素验证 - 需要手机号和验证码')
    } else if (personalQueryConfig.value.requires_mobile) {
      console.log('  ✅ 二要素验证（含手机号） - 需要姓名、身份证和手机号')
    } else {
      console.log('  ✅ 二要素验证 - 仅需姓名和身份证')
    }
  } else {
    console.warn('⚠️ 个人查询配置缺失')
  }
  
  // 验证企业查询配置
  if (enterpriseQueryConfig.value) {
    console.log('✅ 企业查询配置存在')
    console.log('  - 价格:', enterpriseQueryConfig.value.customer_price)
    console.log('  - 包含API:', enterpriseQueryConfig.value.included_apis)
  } else {
    console.warn('⚠️ 企业查询配置缺失')
  }
  
  // 验证系统配置
  console.log('📋 系统配置检查:')
  console.log('  - 站点标题:', systemConfig.value.site_title || '默认')
  console.log('  - Logo:', systemConfig.value.logo ? '✅ 已配置' : '❌ 使用默认')
  console.log('  - 描述:', systemConfig.value.description || '默认')
  console.log('  - 显示价格:', systemConfig.value.show_query_price ? '✅ 是' : '❌ 否')
  console.log('  - 自定义入口描述:', systemConfig.value.query_entrance_desc ? '✅ 已配置' : '❌ 使用默认')
  
  console.log('=== 配置验证结束 ===')
}

onMounted(() => {
  // 执行配置验证
  validateConfigs()
});

const currentIncludedApis = computed(() => {
  const config = activeQueryTab.value === 'personal' ? personalQueryConfig.value : enterpriseQueryConfig.value;
  // 直接返回对象数组，适配 QueryItemsGrid.vue 的新逻辑
  return config?.included_apis || [];
});

const getTabClass = (tabName) => [
  'flex-1 py-3 px-4 font-semibold transition-all duration-300 flex items-center justify-center',
  activeQueryTab.value === tabName ? 'bg-white text-blue-600 shadow-sm' : 'bg-transparent text-gray-500'
]

// 新的三要素验证发送验证码方法
const sendVerificationCodeForQuery = async () => {
  if (isSendingCode.value || isCodeSent.value) return
  
  // 验证必填字段
  if (!personalForm.value.name) {
    showToast('请先输入姓名！', 'warning')
    return
  }
  if (!personalForm.value.idCard) {
    showToast('请先输入身份证号码！', 'warning')
    return
  }
  if (!personalForm.value.phone) {
    showToast('请先输入手机号码！', 'warning')
    return
  }
  
  isSendingCode.value = true
  
  try {
    console.log('【Home】开始发送三要素验证码')
    
    const response = await api.post('/frontend/send-verification-code-for-query/', {
      query_type: '个人查询配置',
      name: personalForm.value.name,
      id_card: personalForm.value.idCard,
      mobile: personalForm.value.phone
    })
    
    console.log('【Home】验证码发送响应:', response)
    
    if (response.code === 0) {
      showToast('验证码发送成功', 'success')
      
      // 开始倒计时
      isCodeSent.value = true
      const timer = setInterval(() => {
        countdown.value--
        if (countdown.value === 0) {
          clearInterval(timer)
          isCodeSent.value = false
          countdown.value = 60
        }
      }, 1000)
    } else {
      showToast(response.message || '验证码发送失败', 'error')
    }
  } catch (error) {
    console.error('【Home】发送验证码异常:', error)
    showToast('发送验证码失败，请重试', 'error')
  } finally {
    isSendingCode.value = false
  }
}

const agreementConfig = {
  personal: [
    { key: 'UserAgreement', title: '用户服务协议', component: UserAgreement },
    { key: 'PrivacyPolicy', title: '隐私政策', component: PrivacyPolicy },
    { key: 'Disclaimer', title: '免责声明', component: Disclaimer },
    { key: 'DataAuthorization', title: '数据查询授权书', component: DataAuthorization },
  ],
  enterprise: [
    { key: 'UserAgreement', title: '用户服务协议', component: UserAgreement },
    { key: 'PrivacyPolicy', title: '隐私政策', component: PrivacyPolicy },
    { key: 'Disclaimer', title: '免责声明', component: Disclaimer },
    { key: 'EnterpriseComplianceCommitment', title: '企业合规承诺书', component: EnterpriseComplianceCommitment },
  ],
}

const handlePersonalQuery = () => {
  // 4. 在查询前检查登录状态
  if (!props.loginState.isLoggedIn) {
    console.log('【Home】用户未登录，尝试进行个人查询，已发出登录提示事件。')
    emit('show-login-prompt')
    return
  }

  // 验证表单
  if (!personalForm.value.name) {
    showToast('请输入姓名！', 'warning')
    return
  }
  if (!personalForm.value.idCard) {
    showToast('请输入身份证号码！', 'warning')
    return
  }
  
  // 如果需要手机号，验证手机号
  if (personalQueryConfig.value.requires_mobile && !personalForm.value.phone) {
    showToast('请输入手机号码！', 'warning')
    return
  }
  
  // 如果需要短信验证码，验证验证码
  if (personalQueryConfig.value.requires_sms_verification && !personalForm.value.code) {
    showToast('请输入验证码！', 'warning')
    return
  }

  // 开始查询流程
  startQueryProcess('个人查询配置', personalForm.value)
}

const handleEnterpriseQuery = () => {
  // 5. 在查询前检查登录状态
  if (!props.loginState.isLoggedIn) {
    console.log('【Home】用户未登录，尝试进行企业查询，已发出登录提示事件。')
    emit('show-login-prompt')
    return
  }

  if (!enterpriseForm.value.companyName) {
    showToast('请输入企业全称！', 'warning')
    return
  }
  if (!enterpriseForm.value.creditCode) {
    showToast('请输入统一社会信用代码！', 'warning')
    return
  }

  // 开始查询流程
  startQueryProcess('企业查询配置', {
    name: enterpriseForm.value.companyName,
    idCard: enterpriseForm.value.creditCode
  })
}

// ==================== 查询支付功能 ====================
const api = useApi()
const router = useRouter()
const isQuerying = ref(false)
const currentOrder = ref(null)
const showPaymentModal = ref(false)

// Toast 相关状态 - 简化为单个Toast
const currentToast = ref(null)

// 检测是否在微信环境中
const isWeChat = computed(() => {
  if (process.client) {
    return /micromessenger/i.test(navigator.userAgent)
  }
  return false
})

// Toast 消息提示 - 简化版本
const showToast = (message, type = 'info') => {
  console.log(`[Toast] ${type}: ${message}`)
  
  // 显示新的toast，替换之前的
  currentToast.value = {
    message,
    type,
    duration: 1000
  }
}

// 开始查询流程
const startQueryProcess = async (queryType, queryData) => {
  if (isQuerying.value) return
  
  isQuerying.value = true
  console.log('【Home】开始查询流程:', { queryType, queryData })
  
  try {
    // 1. 创建查询订单
    const orderResult = await createQueryOrder(queryType, queryData)
    if (!orderResult.success) {
      showToast(orderResult.message || '创建订单失败', 'error')
      return
    }
    
    currentOrder.value = orderResult.data
    console.log('【Home】订单创建成功:', currentOrder.value)
    
    // 2. 显示支付确认模态框
    showPaymentModal.value = true
    
  } catch (error) {
    console.error('【Home】查询流程异常:', error)
    showToast('查询流程异常，请重试', 'error')
  } finally {
    isQuerying.value = false
  }
}

// 创建查询订单
const createQueryOrder = async (queryType, queryData) => {
  try {
    console.log('【Home】创建查询订单:', { queryType, queryData })
    
    const response = await api.post('/frontend/create-order/', {
      query_type: queryType,
      query_data: queryData
    })
    
    console.log('【Home】订单创建响应:', response)
    
    // 参考登录页面的处理方式，使用 response.code === 0 判断成功
    if (response.code === 0) {
      return { success: true, message: response.message, data: response.data }
    } else {
      return { success: false, message: response.message || '创建订单失败' }
    }
  } catch (error) {
    console.error('【Home】创建订单失败:', error)
    return { success: false, message: '创建订单失败' }
  }
}

// 处理支付确认
const handlePaymentConfirm = async (paymentMethod) => {
  if (!currentOrder.value) return
  
  try {
    console.log('【Home】开始支付流程:', paymentMethod)
    
    // 创建支付订单
    const paymentData = {
      order_no: currentOrder.value.order_no,
      payment_method: paymentMethod
    }
    
    // 支付宝支付需要传递当前URL用于生成return_url
    if (paymentMethod === 'alipay') {
      paymentData.current_url = window.location.origin
      
      // 检测设备类型
      const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini|Mobile/i.test(navigator.userAgent)
      paymentData.is_mobile = isMobile
      
      console.log('【Home】支付宝支付，传递当前URL:', paymentData.current_url)
      console.log('【Home】设备类型检测:', isMobile ? '移动设备' : 'PC设备')
    }
    
    // 如果是微信支付，需要获取openid
    if (paymentMethod === 'wechat') {
      const openid = await getWechatOpenid()
      if (!openid) {
        showToast('获取微信用户信息失败', 'error')
        return
      }
      paymentData.openid = openid
    }
    
    const paymentResult = await api.post('/frontend/create-payment/', paymentData)
    
    // 参考登录页面的处理方式，使用 response.code === 0 判断成功
    const paymentResponse = paymentResult.code === 0 
      ? { success: true, message: paymentResult.message, data: paymentResult.data }
      : { success: false, message: paymentResult.message || '创建支付订单失败' }
    
    if (!paymentResponse.success) {
      showToast(paymentResponse.message || '创建支付订单失败', 'error')
      return
    }
    
    console.log('【Home】支付订单创建成功:', paymentResponse.data)
    
    // 关闭支付模态框
    showPaymentModal.value = false
    
    // 根据支付方式处理
    if (paymentMethod === 'alipay') {
      await handleAlipayPayment(paymentResponse.data)
    } else if (paymentMethod === 'wechat') {
      await handleWechatPayment(paymentResponse.data)
    }
    
  } catch (error) {
    console.error('【Home】支付流程异常:', error)
    showToast('支付流程异常，请重试', 'error')
  }
}

// 处理支付宝支付
const handleAlipayPayment = async (paymentData) => {
  try {
    console.log('【Home】处理支付宝支付:', paymentData)
    
    if (paymentData.pay_url) {
      // 跳转到支付宝支付页面
      window.location.href = paymentData.pay_url
    } else {
      showToast('支付链接生成失败', 'error')
    }
  } catch (error) {
    console.error('【Home】支付宝支付失败:', error)
    showToast('支付宝支付失败', 'error')
  }
}

// 处理微信支付
const handleWechatPayment = async (paymentData) => {
  try {
    console.log('【Home】处理微信支付:', paymentData)
    
    // 检查是否有必要的JSAPI参数
    if (paymentData.appId && paymentData.timeStamp && paymentData.nonceStr && 
        paymentData.package && paymentData.signType && paymentData.paySign) {
      
      // 调用微信支付API
      if (typeof WeixinJSBridge !== 'undefined') {
        WeixinJSBridge.invoke('getBrandWCPayRequest', {
          appId: paymentData.appId,
          timeStamp: paymentData.timeStamp,
          nonceStr: paymentData.nonceStr,
          package: paymentData.package,
          signType: paymentData.signType,
          paySign: paymentData.paySign
        }, (res) => {
          console.log('【Home】微信支付结果:', res)
          if (res.err_msg === 'get_brand_wcpay_request:ok') {
            // 支付成功，跳转到查询结果页
            showToast('支付成功', 'success')
            router.push(`/query-result/${currentOrder.value.order_no}`)
          } else if (res.err_msg === 'get_brand_wcpay_request:cancel') {
            showToast('支付已取消', 'warning')
          } else {
            showToast('微信支付失败', 'error')
            console.error('【Home】微信支付失败:', res.err_msg)
          }
        })
      } else {
        showToast('请在微信中打开', 'error')
      }
    } else {
      console.error('【Home】微信支付参数不完整:', paymentData)
      showToast('微信支付参数异常', 'error')
    }
  } catch (error) {
    console.error('【Home】微信支付失败:', error)
    showToast('微信支付失败', 'error')
  }
}

// 获取微信openid
const getWechatOpenid = async () => {
  try {
    // 从登录状态中获取openid
    if (props.loginState.user && props.loginState.user.openid) {
      return props.loginState.user.openid
    }
    
    // 如果没有openid，可能需要重新授权
    console.warn('【Home】未找到微信openid，需要重新授权')
    return null
  } catch (error) {
    console.error('【Home】获取微信openid失败:', error)
    return null
  }
}

// 取消支付
const cancelPayment = () => {
  showPaymentModal.value = false
  currentOrder.value = null
}

// 获取当前查询类型
const getQueryType = () => {
  if (activeQueryTab.value === 'enterprise') {
    return 'enterprise'
  }
  return 'personal'
}

const viewAgreement = (agreement) => {
  activeAgreementComponent.value = agreement.component
  activeAgreementTitle.value = agreement.title
  isAgreementViewerVisible.value = true
}

const closeAgreementViewer = () => {
  isAgreementViewerVisible.value = false
  activeAgreementComponent.value = null
  activeAgreementTitle.value = ''
}

watchEffect(() => {
  console.log('[Home.vue] 当前tab:', activeQueryTab.value)
  console.log('[Home.vue] personalQueryConfig:', personalQueryConfig.value)
  console.log('[Home.vue] enterpriseQueryConfig:', enterpriseQueryConfig.value)
  console.log('[Home.vue] currentIncludedApis:', currentIncludedApis.value)
})
</script>

<style scoped>
@keyframes blob {
  0% { transform: translate(0px, 0px) scale(1); }
  33% { transform: translate(30px, -50px) scale(1.1); }
  66% { transform: translate(-20px, 20px) scale(0.9); }
  100% { transform: translate(0px, 0px) scale(1); }
}

@keyframes spin-reverse {
  from { transform: rotate(360deg); }
  to { transform: rotate(0deg); }
}

.animate-spin-reverse {
  animation: spin-reverse 3s linear infinite;
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

.animation-delay-1000 { animation-delay: 1s; }
.animation-delay-3000 { animation-delay: 3s; }
</style> 
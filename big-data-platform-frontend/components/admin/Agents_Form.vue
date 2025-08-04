<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-75 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
    <div class="relative mx-auto p-5 border w-full max-w-xl shadow-lg rounded-md bg-white" @click.stop>
      <form @submit.prevent="handleSubmit">
        <!-- 防止浏览器自动填充的隐藏输入框 -->
        <input type="text" style="display: none;" />
        <input type="password" style="display: none;" />
        
        <!-- 头部 -->
        <div class="flex items-center justify-between pb-3 border-b">
          <h3 class="text-lg font-medium text-gray-900">{{ mode === 'create' ? '新增代理' : '编辑代理' }}</h3>
          <button @click="$emit('close')" type="button" class="text-gray-400 hover:text-gray-600">
            <Icon name="clarity:close-line" class="w-5 h-5" />
          </button>
        </div>

        <!-- 表单内容 -->
        <div class="mt-4 space-y-6">
          <!-- 创建模式: 分步流程 -->
          <template v-if="mode === 'create'">
            <!-- 步骤一：账户信息 -->
            <div v-show="currentStep === 1">
              <h4 class="text-sm font-medium text-gray-500 mb-3">第一步：填写代理账户信息</h4>
              <div class="space-y-3">
                <div class="flex items-center mb-2">
                  <label class="w-20 text-gray-700 text-sm shrink-0">用户名</label>
                  <input v-model="form.username" type="text" placeholder="必填" class="flex-1 px-3 py-2 border border-gray-300 rounded-md" />
                </div>
                <div class="flex items-center mb-2">
                  <label class="w-20 text-gray-700 text-sm shrink-0">手机号</label>
                  <input v-model="form.phone" type="text" placeholder="可选" class="flex-1 px-3 py-2 border border-gray-300 rounded-md" />
                </div>
                <div class="flex items-center mb-2">
                  <label class="w-20 text-gray-700 text-sm shrink-0">密码</label>
                  <input 
                    v-model="form.password" 
                    type="password" 
                    placeholder="必填，至少6位" 
                    autocomplete="new-password"
                    data-lpignore="true"
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-md" 
                  />
                </div>
                <div class="flex items-center mb-2">
                  <label class="w-20 text-gray-700 text-sm shrink-0">域名后缀</label>
                  <input v-model="form.domain_suffix" type="text" placeholder="必填" class="flex-1 px-3 py-2 border border-gray-300 rounded-md" />
                </div>
              </div>
              <p class="text-xs text-gray-400 mt-2">* 密码至少6位，域名后缀建议为英文或拼音，用户名不可重复</p>
            </div>
            
            <!-- 步骤二：接口配置和定价 -->
            <div v-show="currentStep === 2">
              <h4 class="text-sm font-medium text-gray-500 mb-3">第二步：配置接口和定价</h4>
              <div class="space-y-4">
                <!-- 加载状态 -->
                <div v-if="loading" class="text-center py-4">
                  <Icon name="clarity:refresh-line" class="w-6 h-6 text-gray-400 animate-spin mx-auto" />
                  <p class="text-sm text-gray-500 mt-2">正在获取接口配置...</p>
                </div>
                
                <!-- 接口配置 -->
                <div v-else class="space-y-4">
                  <!-- 个人查询配置 -->
                  <div class="border rounded-lg p-4">
                    <div class="flex items-center justify-between mb-3">
                      <h5 class="font-medium text-gray-900">个人查询配置</h5>
                      <label class="flex items-center">
                        <input v-model="form.personal_enabled" type="checkbox" class="h-4 w-4 text-indigo-600 border-gray-300 rounded">
                        <span class="ml-2 text-sm text-gray-700">启用个人查询</span>
                      </label>
                    </div>
                    
                    <div v-if="form.personal_enabled" class="space-y-3">
                      <!-- 接口选择 -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">选择接口</label>
                        <div class="flex flex-wrap gap-2">
                          <label v-for="api in queryConfigs.find(c => c.config_name === '个人查询配置')?.apis || []" :key="api.id" class="flex items-center bg-gray-50 rounded px-2 py-1 mb-1">
                            <input v-model="form.personal_apis" :value="api.id" type="checkbox" class="h-4 w-4 text-indigo-600 border-gray-300 rounded">
                            <span class="ml-2 text-xs text-gray-700">{{ api.api_name }}</span>
                            <span class="ml-2 text-xs text-gray-400">(¥{{ api.cost_price }})</span>
                          </label>
                        </div>
                      </div>
                      
                      <!-- 底价设置 -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700">
                          底价限制 (元)
                        </label>
                        <input 
                          v-model="form.personal_query_price" 
                          type="number" 
                          step="0.01" 
                          min="0"
                          placeholder="例如: 9.00"
                          class="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                        <div class="text-xs text-gray-500 mt-1">
                          <p>代理收益 = 客户查询价 - 底价限制</p>
                          <p>我的收益 = 代理客户查询价 - 代理底价限制</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 企业查询配置 -->
                  <div class="border rounded-lg p-4">
                    <div class="flex items-center justify-between mb-3">
                      <h5 class="font-medium text-gray-900">企业查询配置</h5>
                      <label class="flex items-center">
                        <input v-model="form.enterprise_enabled" type="checkbox" class="h-4 w-4 text-indigo-600 border-gray-300 rounded">
                        <span class="ml-2 text-sm text-gray-700">启用企业查询</span>
                      </label>
                    </div>
                    
                    <div v-if="form.enterprise_enabled" class="space-y-3">
                      <!-- 接口选择 -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">选择接口</label>
                        <div class="space-y-2">
                          <label v-for="api in queryConfigs.find(c => c.config_name === '企业查询配置')?.apis || []" :key="api.id" class="flex items-center">
                            <input v-model="form.enterprise_apis" :value="api.id" type="checkbox" class="h-4 w-4 text-indigo-600 border-gray-300 rounded">
                            <span class="ml-2 text-sm text-gray-700">{{ api.api_name }}</span>
                            <span class="ml-2 text-xs text-gray-500">(¥{{ api.cost_price }})</span>
                          </label>
                        </div>
                      </div>
                      
                      <!-- 底价设置 -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700">
                          底价限制 (元)
                        </label>
                        <input 
                          v-model="form.enterprise_query_min_price" 
                          type="number" 
                          step="0.01" 
                          min="0"
                          placeholder="例如: 5.00"
                          class="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                        <div class="text-xs text-gray-500 mt-1">
                          <p>代理收益 = 客户查询价 - 底价限制</p>
                          <p>我的收益 = 代理客户查询价 - 代理底价限制</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 步骤三：权限设置 -->
            <div v-show="currentStep === 3">
              <h4 class="text-sm font-medium text-gray-500 mb-3">第三步：权限设置</h4>
              <div class="space-y-4">

                <!-- 权限设置 -->
                <div class="space-y-4">
                  <div>
                    <label class="flex items-center">
                      <input v-model="form.can_customize_settings" type="checkbox" class="h-4 w-4 text-indigo-600 border-gray-300 rounded">
                      <span class="ml-2 text-sm text-gray-700">允许自定义系统设置</span>
                    </label>
                    <p class="mt-1 ml-6 text-xs text-gray-500">允许代理商修改自己网站的Logo、标题、SEO信息等。</p>
                  </div>
                  <div>
                    <label class="flex items-center">
                      <input v-model="form.is_locked" type="checkbox" class="h-4 w-4 text-red-600 border-gray-300 rounded">
                      <span class="ml-2 text-sm text-gray-700">锁定该代理账户</span>
                    </label>
                    <p class="mt-1 ml-6 text-xs text-gray-500">锁定后，该代理将无法登录其管理后台。</p>
                  </div>
                </div>
              </div>
            </div>
          </template>

          <!-- 编辑模式: 使用相同的分步流程 -->
          <template v-if="mode === 'edit'">
            <!-- 步骤一：账户信息 -->
            <div v-show="currentStep === 1">
              <h4 class="text-sm font-medium text-gray-500 mb-3">第一步：修改代理账户信息</h4>
              <div class="space-y-3">
                <div class="flex items-center mb-2">
                  <label class="w-20 text-gray-700 text-sm shrink-0">用户名</label>
                  <input v-model="form.username" type="text" placeholder="用户名" disabled class="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-100 cursor-not-allowed" />
                </div>
                <div class="flex items-center mb-2">
                  <label class="w-20 text-gray-700 text-sm shrink-0">手机号</label>
                  <input v-model="form.phone" type="text" placeholder="可选" class="flex-1 px-3 py-2 border border-gray-300 rounded-md" />
                </div>
                <div class="flex items-center mb-2">
                  <label class="w-20 text-gray-700 text-sm shrink-0">密码</label>
                  <input 
                    v-model="form.password" 
                    type="password" 
                    placeholder="留空则不修改" 
                    autocomplete="new-password"
                    data-lpignore="true"
                    class="flex-1 px-3 py-2 border border-gray-300 rounded-md" 
                  />
                </div>
                <div class="flex items-center mb-2">
                  <label class="w-20 text-gray-700 text-sm shrink-0">域名后缀</label>
                  <input v-model="form.domain_suffix" type="text" placeholder="域名后缀" disabled class="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-100 cursor-not-allowed" />
                </div>
              </div>
              <p class="text-xs text-gray-400 mt-2">* 密码留空则不修改，用户名和域名后缀不可修改</p>
            </div>

            <!-- 步骤二：接口配置和定价 -->
            <div v-show="currentStep === 2">
              <h4 class="text-sm font-medium text-gray-500 mb-3">第二步：修改接口配置和定价</h4>
              <div class="space-y-4">
                <!-- 加载状态 -->
                <div v-if="loading" class="text-center py-4">
                  <Icon name="clarity:refresh-line" class="w-6 h-6 text-gray-400 animate-spin mx-auto" />
                  <p class="text-sm text-gray-500 mt-2">正在获取接口配置...</p>
                </div>
                
                <!-- 接口配置 -->
                <div v-else class="space-y-4">
                  <!-- 个人查询配置 -->
                  <div class="border rounded-lg p-4">
                    <div class="flex items-center justify-between mb-3">
                      <h5 class="font-medium text-gray-900">个人查询配置</h5>
                      <label class="flex items-center">
                        <input v-model="form.personal_enabled" type="checkbox" class="h-4 w-4 text-indigo-600 border-gray-300 rounded">
                        <span class="ml-2 text-sm text-gray-700">启用个人查询</span>
                      </label>
                    </div>
                    
                    <div v-if="form.personal_enabled" class="space-y-3">
                      <!-- 接口选择 -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">选择接口</label>
                        <div class="flex flex-wrap gap-2">
                          <label v-for="api in queryConfigs.find(c => c.config_name === '个人查询配置')?.apis || []" :key="api.id" class="flex items-center bg-gray-50 rounded px-2 py-1 mb-1">
                            <input v-model="form.personal_apis" :value="api.id" type="checkbox" class="h-4 w-4 text-indigo-600 border-gray-300 rounded">
                            <span class="ml-2 text-xs text-gray-700">{{ api.api_name }}</span>
                            <span class="ml-2 text-xs text-gray-400">(¥{{ api.cost_price }})</span>
                          </label>
                        </div>
                      </div>
                      
                      <!-- 底价设置 -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700">
                          底价限制 (元)
                        </label>
                        <input 
                          v-model="form.personal_query_price" 
                          type="number" 
                          step="0.01" 
                          min="0"
                          placeholder="例如: 9.00"
                          class="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                        <div class="text-xs text-gray-500 mt-1">
                          <p>代理收益 = 客户查询价 - 底价限制</p>
                          <p>我的收益 = 代理客户查询价 - 代理底价限制</p>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <!-- 企业查询配置 -->
                  <div class="border rounded-lg p-4">
                    <div class="flex items-center justify-between mb-3">
                      <h5 class="font-medium text-gray-900">企业查询配置</h5>
                      <label class="flex items-center">
                        <input v-model="form.enterprise_enabled" type="checkbox" class="h-4 w-4 text-indigo-600 border-gray-300 rounded">
                        <span class="ml-2 text-sm text-gray-700">启用企业查询</span>
                      </label>
                    </div>
                    
                    <div v-if="form.enterprise_enabled" class="space-y-3">
                      <!-- 接口选择 -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">选择接口</label>
                        <div class="space-y-2">
                          <label v-for="api in queryConfigs.find(c => c.config_name === '企业查询配置')?.apis || []" :key="api.id" class="flex items-center">
                            <input v-model="form.enterprise_apis" :value="api.id" type="checkbox" class="h-4 w-4 text-indigo-600 border-gray-300 rounded">
                            <span class="ml-2 text-sm text-gray-700">{{ api.api_name }}</span>
                            <span class="ml-2 text-xs text-gray-500">(¥{{ api.cost_price }})</span>
                          </label>
                        </div>
                      </div>
                      
                      <!-- 底价设置 -->
                      <div>
                        <label class="block text-sm font-medium text-gray-700">
                          底价限制 (元)
                        </label>
                        <input 
                          v-model="form.enterprise_query_min_price" 
                          type="number" 
                          step="0.01" 
                          min="0"
                          placeholder="例如: 5.00"
                          class="w-full px-3 py-2 border border-gray-300 rounded-md"
                        >
                        <div class="text-xs text-gray-500 mt-1">
                          <p>代理收益 = 客户查询价 - 底价限制</p>
                          <p>我的收益 = 代理客户查询价 - 代理底价限制</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 步骤三：权限设置 -->
            <div v-show="currentStep === 3">
              <h4 class="text-sm font-medium text-gray-500 mb-3">第三步：修改权限设置</h4>
              <div class="space-y-4">
                <!-- 权限设置 -->
                <div class="space-y-4">
                  <div>
                    <label class="flex items-center">
                      <input v-model="form.can_customize_settings" type="checkbox" class="h-4 w-4 text-indigo-600 border-gray-300 rounded">
                      <span class="ml-2 text-sm text-gray-700">允许自定义系统设置</span>
                    </label>
                    <p class="mt-1 ml-6 text-xs text-gray-500">允许代理商修改自己网站的Logo、标题、SEO信息等。</p>
                  </div>
                  <div>
                    <label class="flex items-center">
                      <input v-model="form.is_locked" type="checkbox" class="h-4 w-4 text-red-600 border-gray-300 rounded">
                      <span class="ml-2 text-sm text-gray-700">锁定该代理账户</span>
                    </label>
                    <p class="mt-1 ml-6 text-xs text-gray-500">锁定后，该代理将无法登录其管理后台。</p>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>
        
        <!-- 底部按钮 -->
        <div class="flex justify-end space-x-3 mt-6 pt-4 border-t">
          <template v-if="mode === 'create'">
            <button v-if="currentStep === 2" @click="currentStep = 1" type="button" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">上一步</button>
            <button v-if="currentStep === 3" @click="currentStep = 2" type="button" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">上一步</button>
            <button @click="$emit('close')" type="button" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">取消</button>
            <button v-if="currentStep === 1" @click="goToStep2" type="button" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md">下一步</button>
            <button v-if="currentStep === 2" @click="goToStep3" type="button" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md">下一步</button>
            <button v-if="currentStep === 3" @click.prevent="handleSubmit" :disabled="isSubmitting" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md disabled:opacity-50">
              <Icon v-if="isSubmitting" name="clarity:refresh-line" class="w-4 h-4 mr-1 animate-spin" />
              确认创建
            </button>
          </template>
          <template v-if="mode === 'edit'">
            <button v-if="currentStep === 2" @click="currentStep = 1" type="button" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">上一步</button>
            <button v-if="currentStep === 3" @click="currentStep = 2" type="button" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">上一步</button>
            <button @click="$emit('close')" type="button" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">取消</button>
            <button v-if="currentStep === 1" @click="goToStep2" type="button" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md">下一步</button>
            <button v-if="currentStep === 2" @click="goToStep3" type="button" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md">下一步</button>
            <button v-if="currentStep === 3" @click.prevent="handleSubmit" :disabled="isSubmitting" class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md disabled:opacity-50">
              <Icon v-if="isSubmitting" name="clarity:refresh-line" class="w-4 h-4 mr-1 animate-spin" />
              保存更新
            </button>
          </template>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted } from 'vue'

const props = defineProps({
  mode: {
    type: String,
    default: 'create' // 'create' or 'edit'
  },
  agentData: {
    type: Object,
    default: () => ({})
  },
  isSubmitting: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['close', 'submit'])

const currentStep = ref(1)
const queryConfigs = ref([])
const loading = ref(false)

const form = reactive({
  username: '',
  phone: '',
  password: '',
  domain_suffix: '',
  // 个人查询配置
  personal_enabled: true,
  personal_apis: [],
  personal_query_price: '',
  // 企业查询配置
  enterprise_enabled: true,
  enterprise_apis: [],
  enterprise_query_min_price: '',
  // 其他设置
  can_customize_settings: false,
  is_locked: false
})

// 获取查询配置（只在新建时需要）
const fetchQueryConfigs = async () => {
  loading.value = true
  try {
    const api = useApi()
    const response = await api.get('/admin/query-configs/')
    if (response.code === 0) {
      queryConfigs.value = response.data
      
      // 只在新建模式下自动设置接口和价格
      if (props.mode === 'create') {
        const personalConfig = response.data.find(c => c.config_name === '个人查询配置')
        const enterpriseConfig = response.data.find(c => c.config_name === '企业查询配置')
        
        if (personalConfig) {
          form.personal_apis = personalConfig.apis.map(api => api.id)
          if (!form.personal_query_price) {
            const totalCost = personalConfig.apis.reduce((sum, api) => sum + parseFloat(api.cost_price), 0)
            form.personal_query_price = (totalCost + 2).toFixed(2)
          }
        }
        
        if (enterpriseConfig) {
          form.enterprise_apis = enterpriseConfig.apis.map(api => api.id)
          if (!form.enterprise_query_min_price) {
            const totalCost = enterpriseConfig.apis.reduce((sum, api) => sum + parseFloat(api.cost_price), 0)
            form.enterprise_query_min_price = (totalCost + 3).toFixed(2)
          }
        }
      }
    }
    return response
  } catch (error) {
    console.error('获取查询配置失败:', error)
    throw error
  } finally {
    loading.value = false
  }
}

// 设置编辑模式的查询配置数据
const setEditModeData = (agentData) => {
  if (!agentData) return
  
  console.log('设置编辑模式数据:', agentData)
  
  // 设置基本信息
  Object.assign(form, {
    username: agentData.username || '',
    phone: agentData.phone || '',
    password: '', // 密码留空不修改
    domain_suffix: agentData.domain_suffix || '',
    can_customize_settings: agentData.can_customize_settings || false,
    is_locked: agentData.is_locked || false
  })
  
  // 设置个人查询配置
  if (agentData.personal_query) {
    form.personal_enabled = agentData.personal_query.enabled !== false
    form.personal_query_price = agentData.personal_query.bottom_price || ''
    form.personal_apis = agentData.personal_query.apis?.map(api => api.id) || []
  }
  
  // 设置企业查询配置
  if (agentData.enterprise_query) {
    form.enterprise_enabled = agentData.enterprise_query.enabled !== false
    form.enterprise_query_min_price = agentData.enterprise_query.bottom_price || ''
    form.enterprise_apis = agentData.enterprise_query.apis?.map(api => api.id) || []
  }
  
  console.log('设置完成，表单数据:', {
    personal_enabled: form.personal_enabled,
    personal_apis: form.personal_apis,
    personal_query_price: form.personal_query_price,
    enterprise_enabled: form.enterprise_enabled,
    enterprise_apis: form.enterprise_apis,
    enterprise_query_min_price: form.enterprise_query_min_price
  })
}

// 监听编辑模式的数据变化
watch(() => props.agentData, (newData) => {
  if (props.mode === 'edit' && newData.id) {
    setEditModeData(newData)
  }
})

// 组件挂载后的初始化
onMounted(() => {
  if (props.mode === 'edit' && props.agentData.id) {
    setEditModeData(props.agentData)
  }
})

const resetForm = () => {
  Object.assign(form, {
    username: '',
    phone: '',
    password: '',
    domain_suffix: '',
    // 个人查询配置
    personal_enabled: true,
    personal_apis: [],
    personal_query_price: '',
    // 企业查询配置
    enterprise_enabled: true,
    enterprise_apis: [],
    enterprise_query_min_price: '',
    // 其他设置
    can_customize_settings: false,
    is_locked: false
  })
}

const goToStep2 = () => {
  if (!form.username || !form.domain_suffix) {
    emit('error', '请填写完整的代理账户信息。')
    return
  }
  // 只有新建模式才要求密码必填
  if (props.mode === 'create' && !form.password) {
    emit('error', '请填写密码。')
    return
  }
  if (props.mode === 'create' && form.password.length < 6) {
    emit('error', '密码长度不能少于6位。')
    return
  }
  // 编辑模式下，如果填写了密码，也要检查长度
  if (props.mode === 'edit' && form.password && form.password.length < 6) {
    emit('error', '密码长度不能少于6位。')
    return
  }
  currentStep.value = 2
}

const goToStep3 = () => {
  // 检查是否至少启用了一个查询类型
  if (!form.personal_enabled && !form.enterprise_enabled) {
    emit('error', '请至少启用一种查询类型。')
    return
  }
  
  // 验证个人查询配置
  if (form.personal_enabled) {
    if (form.personal_apis.length === 0) {
      emit('error', '请为个人查询选择至少一个接口。')
      return
    }
    if (!form.personal_query_price) {
      emit('error', '请设置个人查询底价限制。')
      return
    }
    const personalPrice = parseFloat(form.personal_query_price)
    if (isNaN(personalPrice) || personalPrice < 0) {
      emit('error', '请输入有效的个人查询底价。')
      return
    }
  }
  
  // 验证企业查询配置
  if (form.enterprise_enabled) {
    if (form.enterprise_apis.length === 0) {
      emit('error', '请为企业查询选择至少一个接口。')
      return
    }
    if (!form.enterprise_query_min_price) {
      emit('error', '请设置企业查询底价限制。')
      return
    }
    const enterprisePrice = parseFloat(form.enterprise_query_min_price)
    if (isNaN(enterprisePrice) || enterprisePrice < 0) {
      emit('error', '请输入有效的企业查询底价。')
      return
    }
  }
  
  currentStep.value = 3
}

const handleSubmit = () => {
  if (props.mode === 'create') {
    // 验证必填字段
    if (!form.username || !form.password || !form.domain_suffix) {
      emit('error', '请填写完整的代理信息。')
      return
    }
    
    // 验证配置
    if (!form.personal_enabled && !form.enterprise_enabled) {
      emit('error', '请至少启用一种查询类型。')
      return
    }
    
    if (form.personal_enabled && (!form.personal_apis.length || !form.personal_query_price)) {
      emit('error', '请完善个人查询配置。')
      return
    }
    
    if (form.enterprise_enabled && (!form.enterprise_apis.length || !form.enterprise_query_min_price)) {
      emit('error', '请完善企业查询配置。')
      return
    }
  }
  
  emit('submit', { ...form })
}

// 重置表单
watch(() => props.mode, () => {
  if (props.mode === 'create') {
    resetForm()
    currentStep.value = 1
    // 获取查询配置
    fetchQueryConfigs()
  } else if (props.mode === 'edit') {
    currentStep.value = 1
    // 编辑模式也需要获取完整的查询配置，然后设置数据
    fetchQueryConfigs().then(() => {
      if (props.agentData.id) {
        setEditModeData(props.agentData)
      }
    })
  }
}, { immediate: true })
</script> 
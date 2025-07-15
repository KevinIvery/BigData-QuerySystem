<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 侧边栏 -->
    <div class="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0" 
         :class="{ '-translate-x-full': !sidebarOpen && isSmallScreen, 'translate-x-0': sidebarOpen || !isSmallScreen }"
         >
      <div class="p-4 border-b border-gray-100 bg-green-600">
        <h2 class="font-bold text-white text-center">代理管理后台</h2>
      </div>
      
      <!-- 菜单导航 -->
      <nav class="p-2 flex-grow">
        <div v-for="module in menuItems" :key="module.key" class="mb-1">
          <!-- 主菜单项 -->
          <button
            @click="handleMenuItemClick(module)"
            class="w-full flex items-center justify-between px-3 py-3 text-sm font-medium rounded-md transition-all duration-200"
            :class="[
              currentMenu === module.key && (!module.children || module.children.length === 0)
                ? 'bg-green-50 text-green-700' 
                : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
            ]"
          >
            <div class="flex items-center">
              <Icon :name="module.icon" class="w-5 h-5 mr-3" />
              <span>{{ module.name }}</span>
            </div>
            
            <!-- 只有拥有子菜单的项目才显示展开/折叠箭头 -->
            <Icon 
              v-if="module.children && module.children.length" 
              :name="expandedMenus.includes(module.key) ? 'ri:arrow-up-s-line' : 'ri:arrow-down-s-line'" 
              class="w-4 h-4"
            />
          </button>
          
          <!-- 子菜单容器 -->
          <div 
            v-if="module.children && module.children.length"
            class="ml-4 pl-2 border-l border-gray-100 mt-1 overflow-hidden transition-all duration-300"
            :class="[expandedMenus.includes(module.key) ? 'max-h-60' : 'max-h-0']"
          >
            <button
              v-for="subModule in module.children"
              :key="subModule.key"
              @click="handleSubMenuItemClick(module.key, subModule.key)"
              class="w-full flex items-center px-3 py-2 text-sm rounded-md transition-all duration-200 mb-1"
              :class="[
                currentMenu === subModule.key
                  ? 'bg-green-50 text-green-600 font-medium' 
                  : 'text-gray-500 hover:bg-gray-50 hover:text-gray-800'
              ]"
            >
              <span class="w-2 h-2 rounded-full mr-2" :class="[
                currentMenu === subModule.key
                  ? 'bg-green-500' : 'bg-gray-300'
              ]"></span>
              <span>{{ subModule.name }}</span>
            </button>
          </div>
        </div>
      </nav>
    </div>

    <!-- 顶部导航 -->
    <div class="lg:pl-64 relative z-10 flex-shrink-0 flex h-16 bg-white shadow">
      <button
        @click="sidebarOpen = !sidebarOpen"
        class="px-4 border-r border-gray-200 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-green-500 lg:hidden"
      >
        <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      
      <div class="flex-1 px-4 flex justify-between">
        <div class="flex-1 flex">
          <!-- 面包屑导航 -->
          <div class="flex items-center">
            <nav class="flex" aria-label="Breadcrumb">
              <ol class="flex items-center space-x-4">
                <li>
                  <div class="flex items-center">
                    <svg class="flex-shrink-0 h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                    </svg>
                    <span class="ml-2 text-sm font-medium text-gray-500">代理后台</span>
                  </div>
                </li>
                <li v-if="currentMenuName">
                  <div class="flex items-center">
                    <svg class="flex-shrink-0 h-5 w-5 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                    </svg>
                    <span class="ml-4 text-sm font-medium text-gray-700">{{ currentMenuName }}</span>
                  </div>
                </li>
              </ol>
            </nav>
          </div>
        </div>
        
        <!-- 用户菜单 -->
        <div class="ml-4 flex items-center md:ml-6">
          <div class="relative ml-3" data-user-menu>
            <div>
              <button
                @click="userMenuOpen = !userMenuOpen"
                class="max-w-xs bg-white flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                <img class="h-8 w-8 rounded-full" :src="`https://ui-avatars.com/api/?name=${userInfo.username}&background=16a34a&color=fff`" alt="用户头像">
                <span class="ml-2 text-gray-700 text-sm font-medium">{{ userInfo.username }}</span>
                <svg class="ml-2 h-4 w-4 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
            
            <!-- 用户下拉菜单 -->
            <div v-show="userMenuOpen" class="origin-top-right absolute right-0 mt-2 w-64 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5">
              <div class="px-4 py-3 border-b border-gray-100">
                <p class="text-sm font-medium text-gray-900">{{ userInfo.username }}</p>
                <p class="text-sm text-gray-500">{{ userInfo.domain_suffix }}.代理商</p>
              </div>
              <div class="py-1">
                <button @click="showChangePasswordModal" class="w-full text-left block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center">
                  <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m0 0a2 2 0 012 2v6a2 2 0 01-2 2H9a2 2 0 01-2-2V9a2 2 0 012-2m0 0V5a2 2 0 012-2h4a2 2 0 012 2v2M9 7h6"/>
                  </svg>
                  修改密码
                </button>
                <button @click="handleLogout" class="w-full text-left block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center">
                  <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                  </svg>
                  退出登录
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="lg:pl-64 flex flex-col flex-1">
      <!-- 主内容 -->
      <main class="flex-1 relative overflow-y-auto focus:outline-none">
        <div class="py-6">
          <div class="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
            <!-- 动态组件显示区域 -->
            <AgentDashboard 
              v-if="currentMenu === 'dashboard'" 
              :userInfo="userInfo"
              @menu-select="selectMenu"
            />
            
            <!-- 系统设置组件 -->
            <AgentSystemSettings 
              v-else-if="currentMenu === 'system-config'"
            />
            
            <!-- 查询配置组件 -->
            <AgentQueryConfig 
              v-else-if="currentMenu === 'query-config'"
            />
            
            <!-- 佣金明细组件 -->
            <AgentCommissionDetails 
              v-else-if="currentMenu === 'commission-details'"
            />
            
            <!-- 订单记录组件 -->
            <AgentOrders 
              v-else-if="currentMenu === 'orders'"
            />
            
            <!-- 其他功能组件暂时显示开发中状态 -->
            <AgentEmptyPage 
              v-else
              :title="`${currentMenuName} - 功能开发中`"
              :description="`${currentMenuName} 功能正在开发中，敬请期待...`"
              @back-to-dashboard="selectMenu({ key: 'dashboard' })"
            />
          </div>
        </div>
      </main>
    </div>

    <!-- 移动端遮罩 -->
    <div v-show="sidebarOpen" @click="sidebarOpen = false" class="fixed inset-0 z-40 bg-gray-600 bg-opacity-75 lg:hidden"></div>

    <!-- 修改密码弹窗 -->
    <div v-if="changePasswordModalOpen" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <!-- 弹窗头部 -->
        <div class="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <h3 class="text-lg font-medium text-gray-900">修改密码</h3>
          <button @click="closeChangePasswordModal" class="text-gray-400 hover:text-gray-600">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- 弹窗内容 -->
        <form @submit.prevent="submitChangePassword" class="px-6 py-4 space-y-4">
          <!-- 用户名（只读） -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
            <input 
              type="text" 
              :value="userInfo.username" 
              readonly 
              class="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-50 text-gray-500 cursor-not-allowed"
            >
          </div>

          <!-- 当前密码 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">当前密码</label>
            <input 
              type="password" 
              v-model="passwordForm.old_password"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
              placeholder="请输入当前密码"
              autocomplete="current-password"
            >
          </div>

          <!-- 新密码 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">新密码</label>
            <input 
              type="password" 
              v-model="passwordForm.new_password"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
              placeholder="请输入新密码（至少6位）"
              autocomplete="new-password"
            >
          </div>

          <!-- 确认新密码 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">确认新密码</label>
            <input 
              type="password" 
              v-model="passwordForm.confirm_password"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
              placeholder="请再次输入新密码"
              autocomplete="new-password"
            >
          </div>

          <!-- 操作按钮 -->
          <div class="flex justify-end space-x-3 pt-4">
            <button 
              type="button" 
              @click="closeChangePasswordModal"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              取消
            </button>
            <button 
              type="submit"
              :disabled="passwordLoading"
              class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Icon v-if="passwordLoading" name="clarity:refresh-line" class="w-4 h-4 mr-2 animate-spin" />
              {{ passwordLoading ? '修改中...' : '确认修改' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
// 页面元信息
definePageMeta({
  layout: false,
  middleware: 'auth-agent' // 需要代理认证
})

const { $ui } = useNuxtApp()
const api = useApi()

// 用户信息
const userInfo = ref({
  username: '代理用户',
  domain_suffix: 'agent'
})

// 响应式状态
const sidebarOpen = ref(false)
const userMenuOpen = ref(false)
const currentMenu = ref('dashboard')
const expandedMenus = ref(['business', 'settings'])

// 修改密码相关状态
const changePasswordModalOpen = ref(false)
const passwordForm = ref({
  old_password: '',
  new_password: '',
  confirm_password: ''
})
const passwordLoading = ref(false)

// 菜单配置
const menuItems = ref([
  {
    key: 'dashboard',
    name: '仪表盘',
    icon: 'clarity:dashboard-line'
  },
  {
    key: 'business',
    name: '业务管理',
    icon: 'clarity:briefcase-line',
    children: [
      {
          key: 'commission-details',
          name: '佣金明细'
      },
      {
        key: 'orders',
          name: '订单记录'
      }
    ]
  },
  {
    key: 'settings',
    name: '系统设置',
    icon: 'clarity:cog-line',
    children: [
      {
        key: 'system-config',
        name: '网站配置'
      },
      {
        key: 'query-config',
        name: '查询配置'
      }
    ]
  }
])

// 检测屏幕尺寸
const isSmallScreen = ref(false)

// 计算当前菜单名称
const currentMenuName = computed(() => {
  const findMenu = (items) => {
    for (const item of items) {
      if (item.key === currentMenu.value) {
        return item.name
      }
      if (item.children) {
        const found = findMenu(item.children)
        if (found) return found
      }
    }
    return null
  }
  return findMenu(menuItems.value)
})

// 检查屏幕尺寸
const checkScreenSize = () => {
  if (process.client) {
    isSmallScreen.value = window.innerWidth < 1024
  }
}

// 处理主菜单点击
const handleMenuItemClick = (module) => {
  // 如果模块没有子菜单，直接选择该模块
  if (!module.children || module.children.length === 0) {
    currentMenu.value = module.key
    if (isSmallScreen.value) {
      sidebarOpen.value = false
    }
  } else {
    // 有子菜单的模块处理展开/折叠状态
    if (expandedMenus.value.includes(module.key)) {
      expandedMenus.value = expandedMenus.value.filter(id => id !== module.key)
    } else {
      expandedMenus.value.push(module.key)
    }
  }
}

// 处理子菜单点击
const handleSubMenuItemClick = (moduleKey, subModuleKey) => {
  console.log('点击子菜单:', moduleKey, subModuleKey)
  currentMenu.value = subModuleKey
  console.log('当前菜单设置为:', currentMenu.value)
  if (isSmallScreen.value) {
    sidebarOpen.value = false
  }
}

// 选择菜单（保留原有方法以兼容仪表盘组件）
const selectMenu = (menu) => {
  currentMenu.value = menu.key
  if (isSmallScreen.value) {
    sidebarOpen.value = false
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    $ui.showLoading('正在退出登录...')
    
    // 调用登出API
    const response = await api.post('/agent/logout/')
    
    if (response.code === 0) {
      // 清除sessionStorage中的用户信息
      if (process.client) {
        sessionStorage.removeItem('agent_user_info')
      }
      
      $ui.success('已退出登录')
      await navigateTo('/agent/login')
    } else {
      $ui.error('退出失败', response.message || '请稍后重试')
    }
  } catch (error) {
    console.error('退出登录失败:', error)
    $ui.error('退出失败', '网络错误，请稍后重试')
  } finally {
    $ui.hideLoading()
  }
}

// 获取用户信息
const getUserInfo = async () => {
  try {
    // 优先从sessionStorage获取用户信息
    if (process.client) {
      const storedUserInfo = sessionStorage.getItem('agent_user_info')
      if (storedUserInfo) {
        try {
          const userData = JSON.parse(storedUserInfo)
          userInfo.value.username = userData.username || '代理用户'
          userInfo.value.domain_suffix = userData.domain_suffix || 'agent'
          userInfo.value.phone = userData.phone || ''
          userInfo.value.can_customize_settings = userData.can_customize_settings || false
          console.log('从sessionStorage加载用户信息:', userInfo.value)
          return // 如果成功从sessionStorage获取到信息，就不需要再调用API
        } catch (error) {
          console.error('解析sessionStorage中的用户信息失败:', error)
        }
      }
    }
    
    // 如果sessionStorage中没有信息，则调用API获取
    const response = await api.post('/agent/auth-check/')
    if (response.code === 0 && response.data) {
      userInfo.value.username = response.data.username || '代理用户'
      userInfo.value.domain_suffix = response.data.domain_suffix || 'agent'
      userInfo.value.phone = response.data.phone || ''
      userInfo.value.can_customize_settings = response.data.can_customize_settings || false
      
      // 将API获取的信息也存储到sessionStorage
      if (process.client) {
        sessionStorage.setItem('agent_user_info', JSON.stringify(response.data))
      }
      
      console.log('从API获取用户信息:', userInfo.value)
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 显示修改密码弹窗
const showChangePasswordModal = () => {
  userMenuOpen.value = false
  changePasswordModalOpen.value = true
  // 重置表单
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: ''
  }
}

// 关闭修改密码弹窗
const closeChangePasswordModal = () => {
  changePasswordModalOpen.value = false
  passwordForm.value = {
    old_password: '',
    new_password: '',
    confirm_password: ''
  }
}

// 提交修改密码
const submitChangePassword = async () => {
  // 基本验证
  if (!passwordForm.value.old_password || !passwordForm.value.new_password || !passwordForm.value.confirm_password) {
    $ui.warning('请填写所有密码字段')
    return
  }

  if (passwordForm.value.new_password.length < 6) {
    $ui.warning('新密码长度不能少于6位')
    return
  }

  if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
    $ui.warning('两次输入的新密码不一致')
    return
  }

  try {
    passwordLoading.value = true
    
    const response = await api.post('/agent/change-password/', {
      old_password: passwordForm.value.old_password,
      new_password: passwordForm.value.new_password,
      confirm_password: passwordForm.value.confirm_password
    })

    if (response.code === 0) {
      $ui.success('密码修改成功')
      closeChangePasswordModal()
    } else {
      $ui.error('修改失败', response.message || '请稍后重试')
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    $ui.error('修改失败', '网络错误，请稍后重试')
  } finally {
    passwordLoading.value = false
  }
}

// 点击外部关闭用户菜单
const closeUserMenu = (event) => {
  // 检查点击是否在用户菜单区域外
  const userMenuElement = event.target.closest('[data-user-menu]')
  if (!userMenuElement && userMenuOpen.value) {
    userMenuOpen.value = false
  }
}

// 页面初始化
onMounted(() => {
  document.addEventListener('click', closeUserMenu)
  checkScreenSize() // 检查屏幕尺寸
  window.addEventListener('resize', checkScreenSize)
  
  // 立即获取用户信息
  nextTick(() => {
    getUserInfo() // 获取用户信息
  })
})

onUnmounted(() => {
  document.removeEventListener('click', closeUserMenu)
  window.removeEventListener('resize', checkScreenSize)
})

// 页面标题
useHead({
  title: '代理后台 - 大数据查询平台'
})
</script>

<style scoped>
/* 确保子菜单展开/折叠的平滑过渡 */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 300ms;
}

/* 菜单项悬停效果 */
.group:hover .group-hover\:translate-x-2 {
  transform: translateX(0.5rem);
}
</style> 
<template>
    <div class="min-h-screen bg-gray-50">
      <!-- 侧边栏 -->
      <div class="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out lg:translate-x-0" 
           :class="{ '-translate-x-full': !sidebarOpen && isSmallScreen, 'translate-x-0': sidebarOpen || !isSmallScreen }"
           >
        <div class="p-4 border-b border-gray-100 bg-indigo-600">
          <h2 class="font-bold text-white text-center">后台管理系统</h2>
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
                  ? 'bg-indigo-50 text-indigo-700' 
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
                    ? 'bg-indigo-50 text-indigo-600 font-medium' 
                    : 'text-gray-500 hover:bg-gray-50 hover:text-gray-800'
                ]"
              >
                <span class="w-2 h-2 rounded-full mr-2" :class="[
                  currentMenu === subModule.key
                    ? 'bg-indigo-500' : 'bg-gray-300'
                ]"></span>
                <span>{{ subModule.name }}</span>
              </button>
            </div>
          </div>
        </nav>
      </div>
  
      <!-- 主内容区域 -->
      <div class="lg:pl-64 flex flex-col flex-1">
        <!-- 顶部导航 -->
        <div class="relative z-10 flex-shrink-0 flex h-16 bg-white shadow">
          <button
            @click="sidebarOpen = !sidebarOpen"
            class="px-4 border-r border-gray-200 text-gray-500 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-indigo-500 lg:hidden"
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
                        <span class="ml-2 text-sm font-medium text-gray-500">后台管理</span>
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
                    class="max-w-xs bg-white flex items-center text-sm rounded-full focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    <img class="h-8 w-8 rounded-full" :src="`https://ui-avatars.com/api/?name=${userInfo.username}&background=6366f1&color=fff`" alt="用户头像">
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
                    <p class="text-sm text-gray-500">{{ userInfo.company_name }}</p>
                  </div>
                  <div class="py-1">
                    <button @click="showProfileSettings" class="w-full text-left block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center">
                      <svg class="mr-2 h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                      </svg>
                      个人设置
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
  
        <!-- 主内容 -->
        <main class="flex-1 relative overflow-y-auto focus:outline-none">
          <div class="py-6">
            <div class="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
              <!-- 动态组件显示区域 -->
              <AdminDashboard 
                v-if="currentMenu === 'dashboard'" 
                :userInfo="userInfo"
                @menu-select="selectMenu"
              />
              
              <!-- 系统设置 -->
              <div v-else-if="currentMenu === 'system-config'">
                <AdminSystemSettings />
              </div>

              <!-- 查询配置 -->
              <div v-else-if="currentMenu === 'query-config'">
                <AdminQueryConfig />
              </div>

              <!-- 外部API配置 -->
              <div v-else-if="currentMenu === 'external-api-config'">
                <AdminExternalApiConfig />
              </div>

              <!-- 支付配置 -->
              <div v-else-if="currentMenu === 'payment-config'">
                <AdminPaymentConfig />
              </div>

              <!-- 普通用户管理 -->
              <div v-else-if="currentMenu === 'users'">
                <AdminUsers />
              </div>

              <!-- 代理管理 -->
              <div v-else-if="currentMenu === 'agents'">
                <AdminAgents />
              </div>

              <!-- 代理申请管理 -->
              <div v-else-if="currentMenu === 'agent-applications'">
                <AdminAgentApplications />
              </div>

              <!-- 授权书管理 -->
              <div v-else-if="currentMenu === 'authorization-letters'">
                <AdminAuthorizationLetters />
              </div>

              <!-- 查询记录管理 -->
              <div v-else-if="currentMenu === 'query-history'">
                <AdminQueryRecords />
              </div>

              <!-- 订单管理 -->
              <div v-else-if="currentMenu === 'orders'">
                <AdminOrders />
              </div>

              <!-- 佣金申请管理 -->
              <div v-else-if="currentMenu === 'commission-withdrawals'">
                <AdminCommissionWithdrawals />
              </div>
              
              <!-- 其他功能组件暂时显示开发中状态 -->
              <AdminEmptyPage 
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

      <!-- 个人设置弹窗 -->
      <Teleport to="body">
        <AdminProfileSettings
          v-if="showProfileModal"
          :user-info="userInfo"
          @close="showProfileModal = false"
          @updated="handleProfileUpdated"
        />
      </Teleport>
    </div>
  </template>
  
  <script setup>
  // 导入组件（如果自动导入失败）
  import AdminProfileSettings from '~/components/admin/ProfileSettings.vue'
  import AdminSystemSettings from '~/components/admin/SystemSettings.vue'
  import AdminQueryConfig from '~/components/admin/QueryConfig.vue'
  import AdminUsers from '~/components/admin/Users.vue'
  import AdminAgents from '~/components/admin/Agents.vue'
  import AdminAgentApplications from '~/components/admin/AgentApplications.vue'
  import AdminExternalApiConfig from '~/components/admin/ExternalApiConfig.vue'
  import AdminPaymentConfig from '~/components/admin/PaymentConfig.vue'
  import AdminAuthorizationLetters from '~/components/admin/AuthorizationLetters.vue'
  import AdminQueryRecords from '~/components/admin/QueryRecords.vue'
  import AdminOrders from '~/components/admin/Orders.vue'
  import AdminCommissionWithdrawals from '~/components/admin/CommissionWithdrawals.vue'
  
  // 页面元信息
  definePageMeta({
    layout: false,
    middleware: 'auth-admin' // 需要管理员认证
  })
  
  const { $ui } = useNuxtApp()
const api = useApi()

// 用户信息
const userInfo = ref({
  username: '管理员',
  company_name: '系统管理'
})
  
  // 响应式状态
  const sidebarOpen = ref(false)
  const userMenuOpen = ref(false)
  const currentMenu = ref('dashboard')
  const expandedMenus = ref(['users', 'config', 'business'])
  const showProfileModal = ref(false)
  
  // 菜单配置 - 基于数据模型设计，使用Nuxt Icon
  const menuItems = ref([
    {
      key: 'dashboard',
      name: '仪表盘',
      icon: 'clarity:dashboard-line'
    },
    {
      key: 'users',
      name: '用户管理',
      icon: 'clarity:users-line',
      children: [
        {
          key: 'users',
          name: '普通用户'
        },
        {
          key: 'agents',
          name: '代理用户'
        },
        {
          key: 'agent-applications',
          name: '代理申请'
        },
        {
          key: 'commission-withdrawals',
          name: '代理提现申请'
        }
      ]
    },
    {
      key: 'config',
      name: '系统配置',
      icon: 'clarity:cog-line',
      children: [
        {
          key: 'system-config',
          name: '系统设置'
        },
        {
          key: 'query-config',
          name: '查询配置'
        },
        {
          key: 'external-api-config',
          name: '外部API配置'
        },
        {
          key: 'payment-config',
          name: '支付配置'
        }
      ]
    },
    {
      key: 'business',
      name: '业务管理',
      icon: 'clarity:briefcase-line',
      children: [
        {
          key: 'orders',
          name: '订单管理'
        },
        {
          key: 'authorization-letters',
          name: '授权书管理'
        },
        {
          key: 'query-history',
          name: '查询记录'
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
    // 兼容快速操作的点击
    if (menu.key === 'users') {
        // 如果是点击了'用户管理'的快速操作，默认跳转到第一个子菜单
        const userModule = menuItems.value.find(m => m.key === 'users')
        if (userModule && userModule.children && userModule.children.length > 0) {
            currentMenu.value = userModule.children[0].key
        } else {
            currentMenu.value = 'users'
        }
    } else {
        currentMenu.value = menu.key
    }
    
    if (isSmallScreen.value) {
      sidebarOpen.value = false
    }
  }
  
  // 退出登录
  const handleLogout = async () => {
    try {
      $ui.showLoading('正在退出登录...')
      
      // 调用登出API
      const response = await api.post('/admin/logout/')
      
      if (response.code === 0) {
        $ui.success('已退出登录')
        await navigateTo('/a8f2c9e7d4b6f1a5c3e8d9f2b7a4c6e1/login')
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
      const response = await api.post('/admin/auth-check/')
      if (response.code === 0 && response.data) {
        userInfo.value.username = response.data.username || '管理员'
        userInfo.value.company_name = response.data.company_name || '系统管理'
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
    }
  }

  // 显示个人设置弹窗
  const showProfileSettings = () => {
    console.log('点击个人设置按钮')
    userMenuOpen.value = false // 关闭用户菜单
    showProfileModal.value = true
    console.log('showProfileModal设置为:', showProfileModal.value)
  }

  // 处理个人信息更新
  const handleProfileUpdated = (updatedUserInfo) => {
    // 更新本地用户信息
    if (updatedUserInfo.username) {
      userInfo.value.username = updatedUserInfo.username
    }
    if (updatedUserInfo.company_name) {
      userInfo.value.company_name = updatedUserInfo.company_name
    }
    
    // 可以选择重新获取完整的用户信息
    getUserInfo()
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
    getUserInfo() // 获取用户信息
  })
  
  onUnmounted(() => {
    document.removeEventListener('click', closeUserMenu)
    window.removeEventListener('resize', checkScreenSize)
  })
  
  // 页面标题
  useHead({
    title: '后台管理 - 大数据查询平台'
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
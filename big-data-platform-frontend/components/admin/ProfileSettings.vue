<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50" @click="closeModal">
    <div class="relative top-20 mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white" @click.stop>
      <!-- 头部 -->
      <div class="flex items-center justify-between pb-3 border-b">
        <h3 class="text-lg font-medium text-gray-900">个人设置</h3>
        <button @click="closeModal" class="text-gray-400 hover:text-gray-600">
          <Icon name="clarity:close-line" class="w-5 h-5" />
        </button>
      </div>

      <!-- 表单内容 -->
      <div class="mt-4">
        <form @submit.prevent="handleSubmit">
          <!-- 当前用户信息 -->
          <div class="mb-6 p-3 bg-gray-50 rounded-lg">
            <h4 class="text-sm font-medium text-gray-700 mb-2">当前账户信息</h4>
            <div class="space-y-1">
              <p class="text-xs text-gray-600">用户名: {{ userInfo.username }}</p>
              <p class="text-xs text-gray-600">公司名称: {{ userInfo.company_name }}</p>
            </div>
          </div>

          <!-- 修改用户名 -->
          <div class="mb-4">
            <label for="username" class="block text-sm font-medium text-gray-700 mb-2">
              新用户名
            </label>
            <input
              id="username"
              v-model="form.username"
              type="text"
              :placeholder="userInfo.username"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            />
            <p class="mt-1 text-xs text-gray-500">留空则不修改用户名</p>
          </div>

          <!-- 修改密码 -->
          <div class="mb-4">
            <label for="currentPassword" class="block text-sm font-medium text-gray-700 mb-2">
              当前密码
            </label>
            <div class="relative">
              <input
                id="currentPassword"
                v-model="form.currentPassword"
                :type="showCurrentPassword ? 'text' : 'password'"
                placeholder="请输入当前密码"
                class="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <button
                type="button"
                @click="showCurrentPassword = !showCurrentPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <Icon :name="showCurrentPassword ? 'clarity:eye-hide-line' : 'clarity:eye-line'" class="w-4 h-4 text-gray-400" />
              </button>
            </div>
            <p class="mt-1 text-xs text-gray-500">修改任何信息都需要验证当前密码</p>
          </div>

          <div class="mb-4">
            <label for="newPassword" class="block text-sm font-medium text-gray-700 mb-2">
              新密码
            </label>
            <div class="relative">
              <input
                id="newPassword"
                v-model="form.newPassword"
                :type="showNewPassword ? 'text' : 'password'"
                placeholder="请输入新密码"
                class="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <button
                type="button"
                @click="showNewPassword = !showNewPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <Icon :name="showNewPassword ? 'clarity:eye-hide-line' : 'clarity:eye-line'" class="w-4 h-4 text-gray-400" />
              </button>
            </div>
            <p class="mt-1 text-xs text-gray-500">留空则不修改密码</p>
          </div>

          <div class="mb-6">
            <label for="confirmPassword" class="block text-sm font-medium text-gray-700 mb-2">
              确认新密码
            </label>
            <div class="relative">
              <input
                id="confirmPassword"
                v-model="form.confirmPassword"
                :type="showConfirmPassword ? 'text' : 'password'"
                placeholder="请再次输入新密码"
                class="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
              <button
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center"
              >
                <Icon :name="showConfirmPassword ? 'clarity:eye-hide-line' : 'clarity:eye-line'" class="w-4 h-4 text-gray-400" />
              </button>
            </div>
          </div>

          <!-- 按钮组 -->
          <div class="flex justify-end space-x-3">
            <button
              type="button"
              @click="closeModal"
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              取消
            </button>
            <button
              type="submit"
              :disabled="loading || !canSubmit"
              class="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <Icon v-if="loading" name="clarity:refresh-line" class="w-4 h-4 mr-1 animate-spin" />
              {{ loading ? '保存中...' : '保存' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  userInfo: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['close', 'updated'])

const api = useApi()
const { $ui } = useNuxtApp()

// 表单数据
const form = ref({
  username: '',
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 显示密码状态
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

// 加载状态
const loading = ref(false)

// 计算是否可以提交
const canSubmit = computed(() => {
  // 必须输入当前密码
  if (!form.value.currentPassword.trim()) {
    return false
  }
  
  // 如果要修改用户名或密码，至少有一个不为空
  const hasUsername = form.value.username.trim()
  const hasNewPassword = form.value.newPassword.trim()
  
  if (!hasUsername && !hasNewPassword) {
    return false
  }
  
  // 如果要修改密码，确认密码必须匹配
  if (hasNewPassword) {
    return form.value.newPassword === form.value.confirmPassword
  }
  
  return true
})

// 关闭模态框
const closeModal = () => {
  emit('close')
}

// 表单验证
const validateForm = () => {
  const { username, currentPassword, newPassword, confirmPassword } = form.value
  
  if (!currentPassword.trim()) {
    $ui.warning('请输入当前密码')
    return false
  }
  
  if (!username.trim() && !newPassword.trim()) {
    $ui.warning('请至少修改用户名或密码其中一项')
    return false
  }
  
  if (newPassword.trim()) {
    if (newPassword.length < 6) {
      $ui.warning('新密码长度不能少于6位')
      return false
    }
    
    if (newPassword !== confirmPassword) {
      $ui.warning('两次输入的新密码不一致')
      return false
    }
  }
  
  return true
}

// 提交表单
const handleSubmit = async () => {
  if (!validateForm()) {
    return
  }
  
  try {
    loading.value = true
    
    // 准备提交数据
    const submitData = {
      current_password: form.value.currentPassword
    }
    
    // 只有当字段不为空时才添加到提交数据中
    if (form.value.username.trim()) {
      submitData.username = form.value.username.trim()
    }
    
    if (form.value.newPassword.trim()) {
      submitData.new_password = form.value.newPassword
    }
    
    // 调用API更新个人信息
    const response = await api.post('/admin/profile/update/', submitData)
    
    if (response.code === 0) {
      $ui.success('个人信息更新成功')
      
      // 通知父组件更新用户信息
      emit('updated', response.data)
      
      // 重置表单
      form.value = {
        username: '',
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
      
      // 关闭模态框
      closeModal()
    } else {
      $ui.error('更新失败', response.message || '请稍后重试')
    }
    
  } catch (error) {
    console.error('更新个人信息失败:', error)
    
    // 处理不同的错误类型
    const errorCode = error?.response?.data?.code
    const errorMessage = error?.response?.data?.message || '更新失败'
    
    if (errorCode === 401) {
      $ui.error('当前密码错误', '请检查您的当前密码')
    } else if (errorCode === 400) {
      $ui.error('参数错误', errorMessage)
    } else {
      $ui.error('更新失败', errorMessage)
    }
  } finally {
    loading.value = false
  }
}

// 组件挂载时的初始化
onMounted(() => {
  // 可以在这里预填充一些信息
  console.log('个人设置组件已加载')
})
</script>

<style scoped>
/* 动画效果 */
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style> 
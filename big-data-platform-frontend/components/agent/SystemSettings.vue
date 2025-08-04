<template>
  <div class="max-w-4xl mx-auto">
    <!-- 页面标题 -->
    <div class="mb-6">
      <h1 class="text-2xl font-bold text-gray-900">系统设置</h1>
      <p class="mt-1 text-sm text-gray-600">配置网站基本信息、SEO设置和显示选项</p>
    </div>

    <!-- 权限提示 -->
    <div v-if="!canCustomize" class="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
      <div class="flex items-center">
        <Icon name="clarity:warning-line" class="w-5 h-5 text-yellow-600 mr-2" />
        <p class="text-sm text-yellow-800">
          <strong>权限提示：</strong>您没有权限修改系统配置，请联系管理员开放权限。以下配置项为只读状态。
        </p>
      </div>
    </div>

    <!-- 配置表单 -->
    <div class="bg-white shadow rounded-lg">
      <form @submit.prevent="handleSubmit">
        <div class="px-6 py-4 border-b border-gray-200">
          <h3 class="text-lg font-medium text-gray-900">网站配置</h3>
        </div>

        <div class="px-6 py-4 space-y-6">
          <!-- Logo上传 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              网站Logo
            </label>
            <div class="flex items-center space-x-4">
              <!-- Logo预览 -->
              <div class="flex-shrink-0">
                <div v-if="form.logo" class="w-20 h-20 border border-gray-300 rounded-lg overflow-hidden bg-gray-50">
                  <img :src="logoPreviewUrl" alt="Logo预览" class="w-full h-full object-contain">
                </div>
                <div v-else class="w-20 h-20 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center bg-gray-50">
                  <Icon name="clarity:image-line" class="w-8 h-8 text-gray-400" />
                </div>
              </div>

              <!-- 上传按钮 -->
              <div>
                <input
                  ref="logoInput"
                  type="file"
                  accept="image/*"
                  @change="handleLogoUpload"
                  class="hidden"
                  :disabled="!canCustomize"
                >
                <button
                  type="button"
                  @click="canCustomize && $refs.logoInput.click()"
                  :disabled="uploading || !canCustomize"
                  class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Icon v-if="uploading" name="clarity:refresh-line" class="w-4 h-4 mr-2 animate-spin" />
                  <Icon v-else name="clarity:upload-line" class="w-4 h-4 mr-2" />
                  {{ uploading ? '上传中...' : '上传Logo' }}
                </button>
                <p class="mt-1 text-xs text-gray-500">
                  支持 JPG、PNG、GIF 格式，建议尺寸 200x200 像素
                </p>
              </div>
            </div>
          </div>

          <!-- 网站标题 -->
          <div>
            <label for="site_title" class="block text-sm font-medium text-gray-700 mb-2">
              网站标题
            </label>
            <input
              id="site_title"
              v-model="form.site_title"
              type="text"
              :disabled="!canCustomize"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-50 disabled:text-gray-500"
              placeholder="请输入网站标题"
            >
          </div>

          <!-- SEO关键词 -->
          <div>
            <label for="keywords" class="block text-sm font-medium text-gray-700 mb-2">
              SEO关键词
            </label>
            <input
              id="keywords"
              v-model="form.keywords"
              type="text"
              :disabled="!canCustomize"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-50 disabled:text-gray-500"
              placeholder="请输入关键词，用逗号分隔"
            >
            <p class="mt-1 text-xs text-gray-500">多个关键词请用逗号分隔，如：大数据,查询,平台</p>
          </div>

          <!-- 网站描述 -->
          <div>
            <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
              网站描述
            </label>
            <textarea
              id="description"
              v-model="form.description"
              rows="3"
              :disabled="!canCustomize"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-50 disabled:text-gray-500"
              placeholder="请输入网站描述"
            ></textarea>
          </div>

          <!-- 客服链接 -->
          <div>
            <label for="customer_service_url" class="block text-sm font-medium text-gray-700 mb-2">
              客服链接
            </label>
            <input
              id="customer_service_url"
              v-model="form.customer_service_url"
              type="url"
              :disabled="!canCustomize"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-50 disabled:text-gray-500"
              placeholder="例如: https://work.weixin.qq.com/kfid/..."
            >
            <p class="mt-1 text-xs text-gray-500">用于前端页面联系客服，请填写完整的URL</p>
          </div>

          <!-- 显示选项 -->
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">
              显示与访问
            </label>
            <div class="space-y-2">
              <label class="flex items-center">
                <input
                  v-model="form.show_query_price"
                  type="checkbox"
                  :disabled="!canCustomize"
                  class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded disabled:opacity-50"
                >
                <span class="ml-2 text-sm text-gray-700">显示查询价格</span>
              </label>
              <label class="flex items-center">
                <input
                  v-model="form.force_wechat_access"
                  type="checkbox"
                  :disabled="!canCustomize"
                  class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded disabled:opacity-50"
                >
                <span class="ml-2 text-sm text-gray-700">仅限微信内访问</span>
                <Icon name="logos:wechat" class="w-4 h-4 ml-1" />
              </label>
            </div>
          </div>

          <!-- 查询入口描述 -->
          <div>
            <label for="query_entrance_desc" class="block text-sm font-medium text-gray-700 mb-2">
              查询入口描述
            </label>
            <textarea
              id="query_entrance_desc"
              v-model="form.query_entrance_desc"
              rows="4"
              :disabled="!canCustomize"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-50 disabled:text-gray-500"
              placeholder="请输入查询入口的描述文字，支持HTML"
            ></textarea>
            <p class="mt-1 text-xs text-gray-500">支持HTML标签，用于自定义查询页面的描述内容</p>
          </div>

          <!-- 底部版权 -->
          <div>
            <label for="footer_copyright" class="block text-sm font-medium text-gray-700 mb-2">
              底部版权信息
            </label>
            <textarea
              id="footer_copyright"
              v-model="form.footer_copyright"
              rows="2"
              :disabled="!canCustomize"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-50 disabled:text-gray-500"
              placeholder="请输入底部版权信息，支持HTML"
            ></textarea>
            <p class="mt-1 text-xs text-gray-500">支持HTML标签，用于显示版权、备案号等信息</p>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-end space-x-3">
          <button
            type="button"
            @click="resetForm"
            :disabled="!canCustomize"
            class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            重置
          </button>
          <button
            type="submit"
            :disabled="loading || !canCustomize"
            class="px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Icon v-if="loading" name="clarity:refresh-line" class="w-4 h-4 mr-2 animate-spin" />
            {{ loading ? '保存中...' : '保存配置' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
const api = useApi()
const { $ui } = useNuxtApp()
const config = useRuntimeConfig()

// 表单数据
const form = ref({
  logo: '',
  site_title: '',
  keywords: '',
  description: '',
  show_query_price: true,
  query_entrance_desc: '',
  customer_service_url: '',
  force_wechat_access: false,
  footer_copyright: ''
})

const logoPreviewUrl = computed(() => {
  if (!form.value.logo) return ''
  return (config.public.fileUrl || '') + form.value.logo
})

// 原始数据（用于重置）
const originalData = ref({})

// 状态
const loading = ref(false)
const uploading = ref(false)
const canCustomize = ref(false)

// 获取系统配置
const getSystemConfig = async () => {
  try {
    loading.value = true
    const response = await api.post('/agent/system-config/')
    
    if (response.code === 0) {
      const data = response.data
      form.value = {
        logo: data.logo || '',
        site_title: data.site_title || '',
        keywords: data.keywords || '',
        description: data.description || '',
        show_query_price: data.show_query_price !== false,
        query_entrance_desc: data.query_entrance_desc || '',
        customer_service_url: data.customer_service_url || '',
        force_wechat_access: data.force_wechat_access || false,
        footer_copyright: data.footer_copyright || ''
      }
      
      // 获取权限信息
      canCustomize.value = data.can_customize || false
      
      // 保存原始数据
      originalData.value = { ...form.value }
    } else {
      $ui.error('获取配置失败', response.message)
    }
  } catch (error) {
    console.error('获取系统配置失败:', error)
    $ui.error('获取配置失败', '网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// Logo上传处理
const handleLogoUpload = async (event) => {
  if (!canCustomize.value) {
    $ui.warning('没有权限上传图片')
    return
  }

  const file = event.target.files[0]
  if (!file) return

  // 验证文件类型
  const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp']
  if (!allowedTypes.includes(file.type)) {
    $ui.error('文件格式错误', '只支持 JPG、PNG、GIF、WebP 格式的图片')
    return
  }

  // 验证文件大小 (5MB)
  if (file.size > 5 * 1024 * 1024) {
    $ui.error('文件太大', '图片大小不能超过 5MB')
    return
  }

  try {
    uploading.value = true
    
    // 创建FormData
    const formData = new FormData()
    formData.append('logo', file)

    // 上传Logo
    const response = await fetch('/api/upload/', {
      method: 'POST',
      credentials: 'include',
      body: formData
    })

    const result = await response.json()
    
    if (result.code === 0) {
      form.value.logo = result.data.file_url
      $ui.success('Logo上传成功')
    } else {
      $ui.error('上传失败', result.message || '请稍后重试')
    }
  } catch (error) {
    console.error('Logo上传失败:', error)
    $ui.error('上传失败', '网络错误，请稍后重试')
  } finally {
    uploading.value = false
    // 清空文件输入框
    event.target.value = ''
  }
}

// 提交表单
const handleSubmit = async () => {
  if (!canCustomize.value) {
    $ui.warning('没有权限修改配置')
    return
  }

  // 基本验证
  if (!form.value.site_title.trim()) {
    $ui.warning('请输入网站标题')
    return
  }

  try {
    loading.value = true
    
    const response = await api.post('/agent/system-config/update/', {
      logo: form.value.logo,
      site_title: form.value.site_title,
      keywords: form.value.keywords,
      description: form.value.description,
      show_query_price: form.value.show_query_price,
      query_entrance_desc: form.value.query_entrance_desc,
      customer_service_url: form.value.customer_service_url,
      force_wechat_access: form.value.force_wechat_access,
      footer_copyright: form.value.footer_copyright
    })

    if (response.code === 0) {
      $ui.success('系统配置保存成功')
      // 更新原始数据
      originalData.value = { ...form.value }
    } else {
      $ui.error('保存失败', response.message || '请稍后重试')
    }
  } catch (error) {
    console.error('保存系统配置失败:', error)
    $ui.error('保存失败', '网络错误，请稍后重试')
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  if (!canCustomize.value) {
    $ui.warning('没有权限重置配置')
    return
  }
  form.value = { ...originalData.value }
  $ui.info('表单已重置')
}

// 页面初始化
onMounted(() => {
  getSystemConfig()
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
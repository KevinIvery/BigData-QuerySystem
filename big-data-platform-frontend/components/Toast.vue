<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="transform scale-90 opacity-0 translate-y-4"
      enter-to-class="transform scale-100 opacity-100 translate-y-0"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="transform scale-100 opacity-100 translate-y-0"
      leave-to-class="transform scale-95 opacity-0 translate-y-2"
    >
      <div
        v-if="visible"
        class="fixed inset-0 z-50 flex items-center justify-center pointer-events-none"
      >
        <div 
          class="relative bg-white/90 dark:bg-gray-800/90 backdrop-blur-md rounded-xl shadow-xl border border-gray-100 dark:border-gray-700/30 overflow-hidden transform transition-all max-w-md w-full mx-4 pointer-events-auto"
        >
          <!-- 彩色顶部条 -->
          <div class="h-1 w-full bg-gradient-to-r" :class="[typeClass.bar]"></div>
          
          <div class="p-5">
            <div class="flex items-start">
              <!-- 图标 -->
              <div :class="['flex-shrink-0 rounded-full p-2', typeClass.bg]">
                <div class="w-6 h-6" :class="typeClass.iconColor">
                  <svg v-if="type === 'success'" fill="currentColor" viewBox="0 0 20 20" class="w-full h-full">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                  </svg>
                  <svg v-else-if="type === 'error'" fill="currentColor" viewBox="0 0 20 20" class="w-full h-full">
                    <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"/>
                  </svg>
                  <svg v-else-if="type === 'warning'" fill="currentColor" viewBox="0 0 20 20" class="w-full h-full">
                    <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                  </svg>
                  <svg v-else fill="currentColor" viewBox="0 0 20 20" class="w-full h-full">
                    <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clip-rule="evenodd"/>
                  </svg>
                </div>
              </div>
              
              <!-- 内容 -->
              <div class="ml-4 flex-1">
                <div class="flex justify-between items-start">
                  <h3 class="text-lg font-medium text-gray-900 dark:text-white">{{ typeClass.title }}</h3>
                  <button 
                    class="text-gray-400 hover:text-gray-500 focus:outline-none transition-colors"
                    @click="close"
                  >
                    <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"/>
                    </svg>
                  </button>
                </div>
                <div class="mt-1 text-sm text-gray-600 dark:text-gray-300">{{ message }}</div>
                <div v-if="description" class="mt-1 text-xs text-gray-500 dark:text-gray-400">{{ description }}</div>
              </div>
            </div>
          </div>
          
          <!-- 进度条 -->
          <div 
            v-if="showProgress && duration > 0" 
            class="h-1 transition-all duration-100 ease-linear"
            :class="typeClass.progressBar"
            :style="{ width: `${progress}%` }"
          ></div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
const props = defineProps({
  visible: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    default: 'info',
    validator: (val) => ['success', 'error', 'warning', 'info'].includes(val)
  },
  message: {
    type: String,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  duration: {
    type: Number,
    default: 3000
  },
  showProgress: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['close'])

// 状态
const progress = ref(100)
let progressInterval = null
let closeTimeout = null

// 不同类型提示的样式映射
const typeClasses = {
  success: {
    title: '成功',
    bar: 'from-green-400 to-teal-500',
    bg: 'bg-green-100 dark:bg-green-900/30',
    iconColor: 'text-green-600 dark:text-green-400',
    progressBar: 'bg-green-600 dark:bg-green-500'
  },
  error: {
    title: '错误',
    bar: 'from-red-400 to-pink-500',
    bg: 'bg-red-100 dark:bg-red-900/30',
    iconColor: 'text-red-600 dark:text-red-400',
    progressBar: 'bg-red-600 dark:bg-red-500'
  },
  warning: {
    title: '警告',
    bar: 'from-yellow-400 to-orange-500',
    bg: 'bg-yellow-100 dark:bg-yellow-900/30',
    iconColor: 'text-yellow-600 dark:text-yellow-400',
    progressBar: 'bg-yellow-600 dark:bg-yellow-500'
  },
  info: {
    title: '提示',
    bar: 'from-blue-400 to-indigo-500',
    bg: 'bg-blue-100 dark:bg-blue-900/30',
    iconColor: 'text-blue-600 dark:text-blue-400',
    progressBar: 'bg-blue-600 dark:bg-blue-500'
  }
}

// 计算属性：获取当前类型的样式
const typeClass = computed(() => typeClasses[props.type] || typeClasses.info)

// 关闭弹窗
const close = () => {
  emit('close')
  clearTimers()
}

// 清除定时器
const clearTimers = () => {
  if (progressInterval) {
    clearInterval(progressInterval)
    progressInterval = null
  }
  if (closeTimeout) {
    clearTimeout(closeTimeout)
    closeTimeout = null
  }
}

// 启动进度条和自动关闭逻辑
onMounted(() => {
  if (props.duration > 0) {
    const updateFrequency = 30 // 每30ms更新一次进度条
    const decrementPerStep = (100 * updateFrequency) / props.duration
    
    progressInterval = setInterval(() => {
      progress.value = Math.max(0, progress.value - decrementPerStep)
    }, updateFrequency)
    
    closeTimeout = setTimeout(() => {
      close()
    }, props.duration)
  }
})

// 组件卸载时清理
onBeforeUnmount(() => {
  clearTimers()
})
</script> 
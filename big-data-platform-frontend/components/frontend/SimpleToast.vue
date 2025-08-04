<template>
  <Teleport to="body">
    <Transition name="toast" appear>
      <div
        v-if="isVisible"
        class="fixed top-20 left-1/2 transform -translate-x-1/2 z-50 max-w-sm w-full mx-4"
      >
        <div
          :class="[
            'px-4 py-3 rounded-xl shadow-lg backdrop-blur-md border flex items-center space-x-3',
            getToastClass()
          ]"
        >
          <!-- 图标 -->
          <div class="flex-shrink-0">
            <Icon :name="getIcon()" class="w-5 h-5" />
          </div>
          
          <!-- 消息内容 -->
          <div class="flex-1 text-sm font-medium">
            {{ message }}
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  message: { type: String, required: true },
  type: { type: String, default: 'info' }, // success, error, warning, info
  duration: { type: Number, default: 1000 }
})

const emit = defineEmits(['close'])

const isVisible = ref(false)
let timer = null

// 获取Toast样式类
const getToastClass = () => {
  switch (props.type) {
    case 'success':
      return 'text-white bg-green-500/95 border-green-400/50'
    case 'error':
      return 'text-white bg-red-500/95 border-red-400/50'
    case 'warning':
      return 'text-white bg-amber-500/95 border-amber-400/50'
    case 'info':
    default:
      return 'text-white bg-blue-500/95 border-blue-400/50'
  }
}

// 获取图标
const getIcon = () => {
  switch (props.type) {
    case 'success':
      return 'ph:check-circle-bold'
    case 'error':
      return 'ph:x-circle-bold'
    case 'warning':
      return 'ph:warning-circle-bold'
    case 'info':
    default:
      return 'ph:info-bold'
  }
}

// 显示Toast
const show = () => {
  isVisible.value = true
  
  timer = setTimeout(() => {
    close()
  }, props.duration)
}

// 关闭Toast
const close = () => {
  isVisible.value = false
  if (timer) {
    clearTimeout(timer)
    timer = null
  }
  
  setTimeout(() => {
    emit('close')
  }, 300)
}

onMounted(() => {
  show()
})

onUnmounted(() => {
  if (timer) {
    clearTimeout(timer)
  }
})
</script>

<style scoped>
.toast-enter-active {
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.toast-leave-active {
  transition: all 0.25s ease-out;
}

.toast-enter-from {
  opacity: 0;
  transform: translate(-50%, -20px) scale(0.9);
}

.toast-leave-to {
  opacity: 0;
  transform: translate(-50%, -10px) scale(0.95);
}

.toast-enter-to,
.toast-leave-from {
  opacity: 1;
  transform: translate(-50%, 0) scale(1);
}
</style> 
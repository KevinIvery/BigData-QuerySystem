<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="visible"
        class="fixed inset-0 flex flex-col items-center justify-center z-50"
        :class="{ 'bg-black/50 backdrop-blur-sm': overlay }"
      >
        <div class="relative">
          <!-- 主要加载动画 -->
          <div class="loading-container">
            <div class="loading-ring" :style="{ '--size': size + 'px', '--border': Math.max(2, size / 20) + 'px' }">
              <div></div>
              <div></div>
              <div></div>
              <div></div>
            </div>
            
            <!-- 内部的圆环 -->
            <div class="loading-circle" :style="{ '--size': size * 0.8 + 'px' }">
              <svg viewBox="0 0 100 100" width="100%" height="100%">
                <circle
                  class="loading-circle-path"
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="4"
                  stroke-dasharray="60, 175"
                />
              </svg>
            </div>
            
            <!-- 中心图标 -->
            <div class="loading-icon" :style="{ '--size': size * 0.35 + 'px' }">
              <div class="text-blue-500 w-full h-full flex items-center justify-center">
                <svg viewBox="0 0 24 24" fill="none" class="w-full h-full">
                  <circle cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                  <path d="M12 1v6m0 8v6m11-7h-6m-8 0H1" stroke="currentColor" stroke-width="2"/>
                </svg>
              </div>
            </div>
          </div>
          
          <!-- 加载文字 -->
          <div 
            v-if="text" 
            class="mt-4 text-center text-sm font-medium"
            :class="overlay ? 'text-white' : 'text-blue-600'"
          >
            <div class="flex items-center justify-center">
              {{ text }}<span class="dots">...</span>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  visible: {
    type: Boolean,
    default: true
  },
  size: {
    type: Number,
    default: 80 // 默认大小
  },
  text: {
    type: String,
    default: '加载中'
  },
  overlay: {
    type: Boolean,
    default: true
  }
})
</script>

<style scoped>
.loading-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
}

.loading-ring {
  position: relative;
  width: var(--size);
  height: var(--size);
}

.loading-ring div {
  box-sizing: border-box;
  display: block;
  position: absolute;
  width: 100%;
  height: 100%;
  border: var(--border) solid transparent;
  border-radius: 50%;
  animation: loading-ring 1.5s cubic-bezier(0.5, 0, 0.5, 1) infinite;
}

.loading-ring div:nth-child(1) {
  border-top-color: #3b82f6;
  animation-delay: -0.45s;
}
.loading-ring div:nth-child(2) {
  border-top-color: #60a5fa;
  animation-delay: -0.3s;
}
.loading-ring div:nth-child(3) {
  border-right-color: #93c5fd;
  animation-delay: -0.15s;
}
.loading-ring div:nth-child(4) {
  border-bottom-color: #bfdbfe;
}

@keyframes loading-ring {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loading-circle {
  position: absolute;
  width: var(--size);
  height: var(--size);
  animation: rotate 2s linear infinite;
  color: #3b82f6;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

@keyframes rotate {
  100% {
    transform: translate(-50%, -50%) rotate(-360deg);
  }
}

.loading-circle-path {
  animation: circle-dash 1.5s ease-in-out infinite;
}

@keyframes circle-dash {
  0% {
    stroke-dasharray: 60, 175;
    stroke-dashoffset: 0;
  }
  50% {
    stroke-dasharray: 120, 175;
    stroke-dashoffset: -20;
  }
  100% {
    stroke-dasharray: 60, 175;
    stroke-dashoffset: -175;
  }
}

.loading-icon {
  position: absolute;
  width: var(--size);
  height: var(--size);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: pulse 2s infinite;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

@keyframes pulse {
  0% {
    transform: translate(-50%, -50%) scale(0.95);
    opacity: 0.8;
  }
  50% {
    transform: translate(-50%, -50%) scale(1.05);
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) scale(0.95);
    opacity: 0.8;
  }
}

.dots {
  display: inline-block;
  animation: dots 1.5s infinite;
  letter-spacing: 2px;
  padding-left: 2px;
}

@keyframes dots {
  0%, 20% {
    content: ".";
  }
  40% {
    content: "..";
  }
  60%, 100% {
    content: "...";
  }
}
</style> 
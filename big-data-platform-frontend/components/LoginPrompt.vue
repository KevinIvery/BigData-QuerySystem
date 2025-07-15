<template>
  <Transition name="modal-fade">
    <div v-if="show" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-60 p-4">
      <!-- 1. 增加动画和阴影 -->
      <div class="w-full max-w-sm bg-white rounded-2xl shadow-xl transform transition-all"
        :class="show ? 'scale-100 opacity-100' : 'scale-95 opacity-0'">
        
        <!-- 2. 增加图标和顶部装饰 -->
        <div class="p-6 text-center bg-gray-50 rounded-t-2xl">
          <div class="w-16 h-16 mx-auto bg-gradient-to-br from-blue-500 to-indigo-600 rounded-full flex items-center justify-center shadow-lg">
            <Icon name="ph:user-circle-plus-duotone" class="w-10 h-10 text-white" />
          </div>
        </div>

        <!-- 3. 调整文字和布局 -->
        <div class="p-6 text-center">
          <h3 class="text-xl font-bold text-gray-800">请先登录</h3>
          <p class="mt-2 text-base text-gray-600">
            登录后即可使用全部功能
          </p>
          <div class="mt-8 grid grid-cols-2 gap-4">
            <!-- 4. 美化按钮 -->
            <button 
              @click="$emit('close')"
              class="w-full py-3 px-4 bg-gray-200 text-gray-700 font-semibold rounded-xl hover:bg-gray-300 transition-colors duration-200"
            >
              稍后
            </button>
            <button 
              @click="$emit('login')"
              class="w-full py-3 px-4 bg-indigo-600 text-white font-semibold rounded-xl hover:bg-indigo-700 transition-colors duration-200 shadow-md hover:shadow-lg"
            >
              立即登录
            </button>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  show: {
    type: Boolean,
    required: true,
  },
});

defineEmits(['login', 'close']);
</script>

<style scoped>
/* 5. 更新过渡动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-active .transform,
.modal-fade-leave-active .transform {
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
</style> 
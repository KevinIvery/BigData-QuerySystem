<template>
  <footer class="bg-white border-t mt-6 sticky bottom-0 z-20 shadow-lg">
    <div class="max-w-2xl mx-auto px-2 mb-6  py-3 flex space-x-3 justify-center items-center">
      <button
        @click="refreshPage"
        class="px-8 py-2 bg-blue-500 text-white rounded-lg text-base font-semibold shadow hover:bg-blue-600 transition-colors"
      >
        刷新结果
      </button>
      <button
        @click="scrollToTop"
        class="px-8 py-2 bg-gray-500 text-white rounded-lg text-base font-semibold shadow hover:bg-gray-600 transition-colors"
      >
        回到顶部
      </button>
    </div>
  </footer> 
</template>

<script setup>
const refreshPage = () => {
  window.location.reload()
}
const scrollToTop = () => {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}
</script>  
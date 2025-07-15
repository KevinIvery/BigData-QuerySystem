<template>
  <header class="bg-white shadow-sm border-b sticky top-0 z-10">
    <div class="max-w-2xl mx-auto px-4 py-4 flex items-center">
      <button @click="goBack" class="mr-4 p-2 hover:bg-gray-100 rounded-lg transition-colors">
        <Icon name="ph:arrow-left-bold" class="w-6 h-6 text-gray-600" />
      </button>
      <h1 class="text-lg font-semibold text-gray-800">查询结果</h1>
      <span class="ml-auto text-sm text-gray-500 font-mono">{{ orderNo }}</span>
    </div>
  </header>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const props = defineProps({
  orderNo: {
    type: String,
    required: true
  }
})

const goBack = () => {
  router.push('/')
}
</script> 
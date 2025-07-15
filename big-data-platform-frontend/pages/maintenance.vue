<template>
  <div class="min-h-screen bg-gray-100 flex items-center justify-center text-center px-4">
    <div>
      <Icon :name="displayInfo.icon" class="text-6xl mx-auto mb-4" :class="displayInfo.iconColor" />
      <h1 class="text-3xl font-bold text-gray-800">{{ displayInfo.title }}</h1>
      <p class="mt-2 text-md text-gray-600">{{ displayInfo.message }}</p>
      <div v-if="displayInfo.details" class="mt-2 text-sm text-red-500 bg-red-50 p-2 rounded-md">
        <p>缺失的配置项: {{ displayInfo.details }}</p>
      </div>
      <div class="mt-6">
        <button 
          @click="refreshPage"
          class="px-5 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 transition-colors"
        >
          <Icon name="clarity:refresh-line" class="inline-block mr-1" />
          刷新重试
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';

definePageMeta({
  layout: false
})

const route = useRoute()

const reasonMessages = {
  wechat_only: {
    icon: 'logos:wechat',
    iconColor: '',
    title: '请在微信内访问',
    message: '为了给您提供更好的服务和安全保障，本页面需要通过微信客户端打开。'
  },
  config_incomplete: {
    icon: 'clarity:warning-standard-solid',
    iconColor: 'text-yellow-500',
    title: '系统配置不完整',
    message: '部分核心服务配置缺失，网站暂时无法访问。请联系管理员进行配置。'
  },
  server_error: {
    icon: 'clarity:error-standard-solid',
    iconColor: 'text-red-500',
    title: '服务器开小差啦',
    message: '站点状态检查时发生服务器内部错误，请稍后再试。'
  },
  default: {
    icon: 'clarity:tools-solid',
    iconColor: 'text-indigo-400',
    title: '系统维护中',
    message: '我们的网站正在进行一些必要的配置或升级。很快就会回来！'
  }
}

const displayInfo = computed(() => {
  const reason = route.query.reason || 'default';
  const info = reasonMessages[reason] || reasonMessages.default;
  if (reason === 'config_incomplete' && route.query.missing) {
    info.details = route.query.missing;
  }
  return info;
})

useHead({
  title: computed(() => displayInfo.value.title)
})

const refreshPage = () => {
  window.location.href = '/'; // 刷新到首页，重新触发中间件检查
}
</script> 
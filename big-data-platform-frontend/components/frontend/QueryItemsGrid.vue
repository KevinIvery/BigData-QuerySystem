<template>
  <div>
    <div class="flex justify-between items-center mb-3">
      <h3 class="text-base font-semibold text-gray-700">查询包含项目</h3>
      <button class="text-xs font-medium text-blue-600 hover:text-blue-800 transition-colors" @click="goToExampleReport">
        查看示例报告 &rarr;
      </button>
    </div>
    <div v-if="allItems.length > 0" class="grid grid-cols-3 md:grid-cols-4 gap-2">
      <template v-for="item in allItems" :key="item.name">
    <div class="bg-white p-2 rounded-lg shadow flex flex-col items-center space-y-1 border border-gray-100 hover:shadow-md transition-all min-h-[70px]">
      <div :class="[item.icon.bgColor, 'w-8 h-8 rounded flex items-center justify-center mb-1']">
        <Icon :name="item.icon.name" class="w-5 h-5" :class="item.icon.color" />
      </div>
      <p class="font-medium text-xs text-gray-800">{{ item.name }}</p>
    </div>
  </template>
    </div>
    <div v-else class="text-center text-gray-400 text-xs py-6">暂无可用查询项目，请检查后端数据或接口配置</div>
  </div>
</template>

<script setup> 
import { computed, watch } from 'vue';
import { apiComponentMap, apiSubItemsMap } from '~/composables/useApiComponentMap'

const props = defineProps({
  apiList: {
    type: Array,
    default: () => []
  },
  queryType: {
    type: String,
    default: 'personal' // 'personal' 或 'enterprise'
  }
});

const router = useRouter()

// 跳转到示例报告，带上查询类型参数
const goToExampleReport = () => {
  const queryParam = props.queryType === 'enterprise' ? 'enterprise' : 'personal'
  router.push(`/example-report?type=${queryParam}`)
}

const allItems = computed(() => {
  const apis = props.apiList.filter(api => api.is_active);
  let items = [];
  apis.forEach(api => {
    // 如果主接口有子标签，展示所有子标签
    if (apiSubItemsMap[api.api_code]) {
      items.push(...apiSubItemsMap[api.api_code].map(sub => sub.code));
    } else {
      items.push(api.api_code);
    }
  });
  // 去重
  items = [...new Set(items)];
  return items.map(code => {
    const map = apiComponentMap[code] || apiComponentMap.DEFAULT;
    return {
      name: map.title || code,
      icon: {
        name: map.icon,
        color: map.iconColor,
        bgColor: map.iconBg
      }
    }
  });
});

// 日志
watch(() => props.apiList, (val) => {
  console.log('[QueryItemsGrid] apiList changed:', val);
});
watch(() => props.queryType, (val) => {
  console.log('[QueryItemsGrid] queryType changed:', val);
});
watch(allItems, (val) => {
  console.log('[QueryItemsGrid] allItems:', val);
});
</script> 

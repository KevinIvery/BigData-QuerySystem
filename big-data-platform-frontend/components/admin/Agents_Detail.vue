<template>
  <div class="fixed inset-0 bg-gray-600 bg-opacity-75 overflow-y-auto h-full w-full z-50 flex items-center justify-center">
    <div class="relative mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white" @click.stop>
      <!-- 头部 -->
      <div class="flex items-center justify-between pb-3 border-b">
        <h3 class="text-lg font-medium text-gray-900">代理详情 - {{ agentDetail.username }}</h3>
        <button @click="$emit('close')" type="button" class="text-gray-400 hover:text-gray-600">
          <Icon name="clarity:close-line" class="w-5 h-5" />
        </button>
      </div>

      <!-- 内容 -->
      <div class="mt-4 max-h-[70vh] overflow-y-auto">
        <!-- 基本信息 -->
        <div class="mb-6">
          <h4 class="text-sm font-medium text-gray-500 mb-3">基本信息</h4>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span class="font-medium text-gray-500">用户名:</span>
              <p class="text-gray-900">{{ agentDetail.username }}</p>
            </div>
            <div>
              <span class="font-medium text-gray-500">手机号:</span>
              <p class="text-gray-900">{{ agentDetail.phone || '未设置' }}</p>
            </div>
            <div>
              <span class="font-medium text-gray-500">域名后缀:</span>
              <p class="text-gray-900">{{ agentDetail.domain_suffix }}</p>
            </div>
            <div>
              <span class="font-medium text-gray-500">注册时间:</span>
              <p class="text-gray-900">{{ new Date(agentDetail.created_at).toLocaleString() }}</p>
            </div>
            <div>
              <span class="font-medium text-gray-500">状态:</span>
              <span :class="[agentDetail.is_locked ? 'bg-red-100 text-red-800' : 'bg-green-100 text-green-800', 'px-2 py-0.5 inline-flex text-xs leading-5 font-semibold rounded-full']">
                {{ agentDetail.is_locked ? '锁定' : '正常' }}
              </span>
            </div>
            <div>
              <span class="font-medium text-gray-500">自定义设置:</span>
              <span :class="[agentDetail.can_customize_settings ? 'text-green-600' : 'text-gray-500', 'font-medium']">
                {{ agentDetail.can_customize_settings ? '允许' : '禁止' }}
              </span>
            </div>
            <div>
              <span class="font-medium text-gray-500">访问链接:</span>
              <a :href="getAgentUrl()" target="_blank" class="text-blue-600 hover:text-blue-900 hover:underline text-sm">
                查看站点
              </a>
            </div>
          </div>
        </div>

        <!-- 佣金统计 -->
        <div class="mb-6">
          <h4 class="text-sm font-medium text-gray-500 mb-3">佣金统计</h4>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div class="bg-blue-50 p-4 rounded-lg">
              <div class="flex items-center">
                <Icon name="clarity:coin-bag-line" class="w-8 h-8 text-blue-500 mr-3" />
                <div>
                  <p class="text-sm font-medium text-gray-600">累计佣金</p>
                  <p class="text-2xl font-bold text-blue-600">¥{{ agentDetail.total_commission || '0.00' }}</p>
                </div>
              </div>
            </div>
            <div class="bg-green-50 p-4 rounded-lg">
              <div class="flex items-center">
                <Icon name="clarity:check-circle-line" class="w-8 h-8 text-green-500 mr-3" />
                <div>
                  <p class="text-sm font-medium text-gray-600">已结算佣金</p>
                  <p class="text-2xl font-bold text-green-600">¥{{ agentDetail.settled_commission || '0.00' }}</p>
                </div>
              </div>
            </div>
            <div class="bg-orange-50 p-4 rounded-lg">
              <div class="flex items-center">
                <Icon name="clarity:clock-line" class="w-8 h-8 text-orange-500 mr-3" />
                <div>
                  <p class="text-sm font-medium text-gray-600">未结算佣金</p>
                  <p class="text-2xl font-bold text-orange-600">¥{{ agentDetail.unsettled_commission || '0.00' }}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 配置信息 -->
        <div class="space-y-4">
          <!-- 个人查询配置 -->
          <div class="bg-blue-50 p-4 rounded-lg">
            <div class="flex items-center justify-between mb-3">
              <h5 class="font-semibold text-blue-900 flex items-center">
                <Icon name="clarity:user-line" class="w-4 h-4 mr-2" />
                个人查询配置
              </h5>
              <span :class="[
                agentDetail.personal_query?.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
                'px-2 py-1 text-xs font-semibold rounded-full'
              ]">
                {{ agentDetail.personal_query?.enabled ? '启用' : '禁用' }}
              </span>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span class="font-medium text-gray-600">超管底价:</span>
                <p class="text-red-600 font-bold text-lg">¥{{ agentDetail.personal_query?.bottom_price || '0.00' }}</p>
                <p class="text-xs text-gray-500">代理不能低于此价格</p>
              </div>
              <div>
                <span class="font-medium text-gray-600">客户查询价:</span>
                <p class="text-green-600 font-bold text-lg">¥{{ agentDetail.personal_query?.customer_price || '0.00' }}</p>
                <p class="text-xs text-gray-500">代理设置的前端价格</p>
              </div>
              <div>
                <span class="font-medium text-gray-600">包含接口:</span>
                <p class="text-blue-700 font-medium">{{ agentDetail.personal_query?.apis?.length || 0 }}个</p>
                <div class="mt-1 text-xs text-gray-600">
                  <span v-for="(api, index) in agentDetail.personal_query?.apis || []" :key="api.id">
                    {{ api.name }}<span v-if="index < (agentDetail.personal_query?.apis?.length || 0) - 1">、</span>
                  </span>
                </div>
              </div>
              <div>
                <span class="font-medium text-gray-600">代理收益:</span>
                <p class="text-purple-600 font-bold text-lg">¥{{ ((agentDetail.personal_query?.customer_price || 0) - (agentDetail.personal_query?.bottom_price || 0)).toFixed(2) }}</p>
                <p class="text-xs text-gray-500">每次查询收益</p>
              </div>
            </div>
          </div>

          <!-- 企业查询配置 -->
          <div class="bg-purple-50 p-4 rounded-lg">
            <div class="flex items-center justify-between mb-3">
              <h5 class="font-semibold text-purple-900 flex items-center">
                <Icon name="clarity:building-line" class="w-4 h-4 mr-2" />
                企业查询配置
              </h5>
              <span :class="[
                agentDetail.enterprise_query?.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800',
                'px-2 py-1 text-xs font-semibold rounded-full'
              ]">
                {{ agentDetail.enterprise_query?.enabled ? '启用' : '禁用' }}
              </span>
            </div>
            
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
              <div>
                <span class="font-medium text-gray-600">超管底价:</span>
                <p class="text-red-600 font-bold text-lg">¥{{ agentDetail.enterprise_query?.bottom_price || '0.00' }}</p>
                <p class="text-xs text-gray-500">代理不能低于此价格</p>
              </div>
              <div>
                <span class="font-medium text-gray-600">客户查询价:</span>
                <p class="text-green-600 font-bold text-lg">¥{{ agentDetail.enterprise_query?.customer_price || '0.00' }}</p>
                <p class="text-xs text-gray-500">代理设置的前端价格</p>
              </div>
              <div>
                <span class="font-medium text-gray-600">包含接口:</span>
                <p class="text-purple-700 font-medium">{{ agentDetail.enterprise_query?.apis?.length || 0 }}个</p>
                <div class="mt-1 text-xs text-gray-600">
                  <span v-for="(api, index) in agentDetail.enterprise_query?.apis || []" :key="api.id">
                    {{ api.name }}<span v-if="index < (agentDetail.enterprise_query?.apis?.length || 0) - 1">、</span>
                  </span>
                </div>
              </div>
              <div>
                <span class="font-medium text-gray-600">代理收益:</span>
                <p class="text-purple-600 font-bold text-lg">¥{{ ((agentDetail.enterprise_query?.customer_price || 0) - (agentDetail.enterprise_query?.bottom_price || 0)).toFixed(2) }}</p>
                <p class="text-xs text-gray-500">每次查询收益</p>
              </div>
            </div>
          </div>

          <!-- 权限信息 -->
          <div class="bg-gray-50 p-4 rounded-lg">
            <h5 class="font-semibold text-gray-800 mb-3 flex items-center">
              <Icon name="clarity:settings-line" class="w-4 h-4 mr-2" />
              权限配置
            </h5>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div class="space-y-2">
                <div class="flex items-center">
                  <Icon :name="agentDetail.can_customize_settings ? 'clarity:check-circle-line' : 'clarity:times-circle-line'" 
                        :class="agentDetail.can_customize_settings ? 'text-green-500' : 'text-red-500'" 
                        class="w-4 h-4 mr-2" />
                  <span>自定义系统设置</span>
                </div>
              </div>
              <div class="space-y-2">

                <div class="flex items-center">
                  <Icon :name="!agentDetail.is_locked ? 'clarity:check-circle-line' : 'clarity:times-circle-line'" 
                        :class="!agentDetail.is_locked ? 'text-green-500' : 'text-red-500'" 
                        class="w-4 h-4 mr-2" />
                  <span>{{ agentDetail.is_locked ? '账户已锁定' : '账户正常' }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 底部按钮 -->
      <div class="flex justify-end space-x-3 mt-6 pt-4 border-t">
        <button @click="$emit('close')" type="button" class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50">
          关闭
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  agentDetail: {
    type: Object,
    default: () => ({})
  }
})

defineEmits(['close'])

const config = useRuntimeConfig()

const getAgentUrl = () => {
  if (!props.agentDetail.domain_suffix) return '#'
  
  const baseUrl = config.public.AgentsUSL || 'https://web.tybigdata.com/'
  const fullUrl = new URL(baseUrl)
  fullUrl.searchParams.set('agent', props.agentDetail.domain_suffix)
  return fullUrl.href
}
</script>
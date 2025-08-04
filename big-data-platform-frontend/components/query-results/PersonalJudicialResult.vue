<template>
  <section id="personal-judicial-result" class="bg-white rounded-xl shadow-sm border border-gray-100 p-5 mb-6">
    <!-- 头部标题 -->
    <div class="flex items-center justify-between mb-5">
      <div class="flex items-center">
        <div class="w-8 h-8 bg-red-50 rounded-lg flex items-center justify-center mr-3">
          <Icon name="ph:police-car-bold" class="w-5 h-5 text-red-500" />
        </div>
        <div>
          <h3 class="text-base font-medium text-gray-800">个人综合涉诉</h3>
          <p class="text-xs text-gray-500">个人综合涉诉查询结果</p>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <span class="text-xs text-gray-400">总数: {{ getTotalCases() }}</span>
        <div v-if="data?.success" class="w-2 h-2 bg-green-500 rounded-full"></div>
        <div v-else class="w-2 h-2 bg-red-500 rounded-full"></div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="text-center py-8">
      <div class="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
      <p class="text-sm text-gray-500">正在加载个人综合涉诉数据...</p>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="text-center py-8">
      <div class="w-10 h-10 bg-red-50 rounded-full flex items-center justify-center mx-auto mb-3">
        <Icon name="ph:warning-circle-bold" class="w-5 h-5 text-red-500" />
      </div>
      <h4 class="text-sm font-medium text-gray-800 mb-1">数据加载失败</h4>
      <p class="text-xs text-gray-600">{{ error }}</p>
    </div>

    <!-- 成功状态 -->
    <div v-else-if="data?.success" class="space-y-5">
      <!-- 饼图分布 -->
      <div class="bg-gray-50 rounded-lg p-4">
        <h4 class="text-sm font-medium text-gray-800 mb-3 flex items-center">
          <Icon name="ph:chart-pie-bold" class="w-4 h-4 mr-2 text-gray-500" />
          案件类型分布
        </h4>
        <div class="flex justify-center">
          <canvas ref="pieChartRef" width="240" height="240" class="max-w-[240px] max-h-[240px]"></canvas>
        </div>
      </div>

      <!-- 案件类型Tab切换 -->
      <div class="border-b border-gray-200">
        <div class="flex items-center">
          <button 
            @click="scrollTabs('left')"
            class="flex-shrink-0 p-2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <Icon name="ph:caret-left-bold" class="w-4 h-4" />
          </button>
          
          <div 
            ref="tabsContainer"
            class="flex space-x-1 overflow-x-auto scrollbar-hide scroll-smooth flex-1"
            style="scrollbar-width: none; -ms-overflow-style: none;"
          >
            <button
              v-for="tab in caseTabs"
              :key="tab.key"
              @click="activeTab = tab.key"
              :class="[
                'flex-shrink-0 px-3 py-2 text-sm font-medium rounded-t-lg border-b-2 transition-colors whitespace-nowrap',
                activeTab === tab.key
                  ? 'text-blue-600 border-blue-600 bg-blue-50'
                  : 'text-gray-500 border-transparent hover:text-gray-700 hover:border-gray-300'
              ]"
            >
              {{ tab.label }} ({{ tab.count }})
            </button>
          </div>
          
          <button 
            @click="scrollTabs('right')"
            class="flex-shrink-0 p-2 text-gray-400 hover:text-gray-600 transition-colors"
          >
            <Icon name="ph:caret-right-bold" class="w-4 h-4" />
          </button>
        </div>
      </div>

      <!-- 案件详情 -->
      <div class="space-y-4">
        <!-- 刑事案件 -->
        <div v-if="activeTab === 'criminal'">
          <div v-if="getCriminalCases() === 0" class="text-center py-6 text-gray-500">
            <Icon name="ph:file-text-bold" class="w-8 h-8 mx-auto mb-2 text-gray-300" />
            <p class="text-sm">暂无刑事案件，或未被公开</p>
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="(caseItem, index) in getCriminalData()"
              :key="index"
              class="bg-gray-50 rounded-lg p-4 space-y-3"
            >
              <div class="flex items-center justify-between">
                <h5 class="text-sm font-medium text-gray-800">{{ caseItem.c_ah || '--' }}</h5>
                <div class="flex items-center space-x-2">
                  <span class="text-xs text-gray-500">{{ index + 1 }}/{{ getCriminalCases() }}</span>
                  <span v-if="caseItem.n_slcx" class="text-xs px-2 py-1 bg-gray-100 text-gray-600 rounded-full">{{ caseItem.n_slcx }}</span>
                </div>
              </div>
              
              <!-- 基本信息 -->
              <div class="space-y-2">
                <div class="grid grid-cols-2 gap-3 text-xs">
                  <div class="flex justify-between">
                    <span class="text-gray-500">立案时间：</span>
                    <span class="text-gray-800">{{ formatDate(caseItem.d_larq) }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-500">结案时间：</span>
                    <span class="text-gray-800">{{ formatDate(caseItem.d_jarq) }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-500">结案方式：</span>
                    <span class="text-gray-800">{{ caseItem.n_jafs || '--' }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-500">诉讼地位：</span>
                    <span class="text-gray-800">{{ caseItem.n_ssdw || '--' }}</span>
                  </div>
                </div>
                
                <div class="text-xs">
                  <div class="flex items-start">
                    <span class="text-gray-500 flex-shrink-0 mr-2">经办法院：</span>
                    <span class="text-gray-800 break-all">{{ caseItem.n_jbfy || '--' }}</span>
                  </div>
                </div>
                
                <div class="text-xs">
                  <div class="flex items-start">
                    <span class="text-gray-500 flex-shrink-0 mr-2">立案案由：</span>
                    <span class="text-gray-800 break-all">{{ caseItem.n_laay_tree || '--' }}</span>
                  </div>
                </div>
                
                <!-- 案件类型和阶段标识 -->
                <div v-if="caseItem.n_ajlx || caseItem.n_ajjzjd" class="flex flex-wrap gap-2">
                  <span v-if="caseItem.n_ajlx" class="text-xs px-2 py-1 bg-blue-100 text-blue-600 rounded-full">{{ caseItem.n_ajlx }}</span>
                  <span v-if="caseItem.n_ajjzjd" class="text-xs px-2 py-1 bg-green-100 text-green-600 rounded-full">{{ caseItem.n_ajjzjd }}</span>
                </div>
              </div>
              
              <!-- 当事人信息 -->
              <div v-if="caseItem.c_dsrxx && caseItem.c_dsrxx.length > 0" class="text-xs">
                <div class="text-gray-500 mb-2">当事人信息</div>
                <div class="flex flex-wrap gap-2">
                  <span 
                    v-for="(person, pIndex) in caseItem.c_dsrxx" 
                    :key="pIndex"
                    :class="[
                      'px-2 py-1 rounded-full text-xs',
                      person.n_ssdw === '被告人' ? 'bg-red-100 text-red-700' : 
                      person.n_ssdw === '上诉人' ? 'bg-orange-100 text-orange-700' :
                      'bg-gray-100 text-gray-700'
                    ]"
                  >
                    {{ person.n_ssdw }}: {{ person.c_mc }}
                  </span>
                </div>
              </div>
              
              <!-- 判决结果 -->
              <div v-if="caseItem.n_pcjg" class="text-xs">
                <div class="flex items-start">
                  <span class="text-gray-500 flex-shrink-0 mr-2">判决结果：</span>
                  <span class="text-gray-800 break-all">{{ caseItem.n_pcjg }}</span>
                </div>
              </div>
              
              <!-- 详细信息 -->
              <div v-if="caseItem.c_gkws_dsr" class="text-xs">
                <div class="flex items-start">
                  <span class="text-gray-500 flex-shrink-0 mr-2">详细信息：</span>
                  <span class="text-gray-800 break-all leading-relaxed">{{ caseItem.c_gkws_dsr }}</span>
                </div>
              </div>
              
              <!-- 关联案件 -->
              <div v-if="caseItem.c_ah_hx || caseItem.c_ah_ys" class="text-xs">
                <div class="text-gray-500 mb-1">关联案件</div>
                <div class="space-y-1">
                  <div v-if="caseItem.c_ah_hx" class="text-gray-600">
                    <span class="text-gray-500">后续案件：</span>{{ caseItem.c_ah_hx.split(':')[0] }}
                  </div>
                  <div v-if="caseItem.c_ah_ys" class="text-gray-600">
                    <span class="text-gray-500">原审案件：</span>{{ caseItem.c_ah_ys.split(':')[0] }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 执行案件 -->
        <div v-if="activeTab === 'implement'">
          <div v-if="getExecutionCases() === 0" class="text-center py-6 text-gray-500">
            <Icon name="ph:file-text-bold" class="w-8 h-8 mx-auto mb-2 text-gray-300" />
            <p class="text-sm">暂无执行案件，或未被公开</p>
          </div>
          <div v-else class="space-y-3">
            <div
              v-for="(caseItem, index) in getExecutionData()"
              :key="index"
              class="bg-gray-50 rounded-lg p-4 space-y-3"
            >
              <div class="flex items-center justify-between">
                <h5 class="text-sm font-medium text-gray-800">{{ caseItem.c_ah || '--' }}</h5>
                <div class="flex items-center space-x-2">
                  <span class="text-xs text-gray-500">{{ index + 1 }}/{{ getExecutionCases() }}</span>
                </div>
              </div>
              
              <!-- 基本信息 -->
              <div class="space-y-2">
                <div class="grid grid-cols-2 gap-3 text-xs">
                  <div class="flex justify-between">
                    <span class="text-gray-500">立案时间：</span>
                    <span class="text-gray-800">{{ formatDate(caseItem.d_larq) }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-500">结案时间：</span>
                    <span class="text-gray-800">{{ formatDate(caseItem.d_jarq) }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-500">结案方式：</span>
                    <span class="text-gray-800">{{ caseItem.n_jafs || '--' }}</span>
                  </div>
                  <div class="flex justify-between">
                    <span class="text-gray-500">诉讼地位：</span>
                    <span class="text-gray-800">{{ caseItem.n_ssdw || '--' }}</span>
                  </div>
                </div>
                
                <!-- 执行金额信息 -->
                <div v-if="caseItem.n_sqzxbdje || caseItem.n_sjdwje || caseItem.n_wzxje" class="grid grid-cols-3 gap-3 text-xs bg-white p-2 rounded border">
                  <div v-if="caseItem.n_sqzxbdje" class="text-center">
                    <div class="text-gray-500">申请执行标的额</div>
                    <div class="text-blue-600 font-medium">{{ formatMoney(caseItem.n_sqzxbdje) }}</div>
                  </div>
                  <div v-if="caseItem.n_sjdwje" class="text-center">
                    <div class="text-gray-500">实际到位金额</div>
                    <div class="text-green-600 font-medium">{{ formatMoney(caseItem.n_sjdwje) }}</div>
                  </div>
                  <div v-if="caseItem.n_wzxje" class="text-center">
                    <div class="text-gray-500">未执行金额</div>
                    <div class="text-red-600 font-medium">{{ formatMoney(caseItem.n_wzxje) }}</div>
                  </div>
                </div>
                
                <div class="text-xs">
                  <div class="flex items-start">
                    <span class="text-gray-500 flex-shrink-0 mr-2">经办法院：</span>
                    <span class="text-gray-800 break-all">{{ caseItem.n_jbfy || '--' }}</span>
                  </div>
                </div>
                
                <div class="text-xs">
                  <div class="flex items-start">
                    <span class="text-gray-500 flex-shrink-0 mr-2">立案案由：</span>
                    <span class="text-gray-800 break-all">{{ caseItem.n_laay_tree || '--' }}</span>
                  </div>
                </div>
                
                <!-- 案件类型和阶段标识 -->
                <div v-if="caseItem.n_ajlx || caseItem.n_ajjzjd" class="flex flex-wrap gap-2">
                  <span v-if="caseItem.n_ajlx" class="text-xs px-2 py-1 bg-blue-100 text-blue-600 rounded-full">{{ caseItem.n_ajlx }}</span>
                  <span v-if="caseItem.n_ajjzjd" class="text-xs px-2 py-1 bg-green-100 text-green-600 rounded-full">{{ caseItem.n_ajjzjd }}</span>
                </div>
              </div>
              
              <!-- 当事人信息 -->
              <div v-if="caseItem.c_dsrxx && caseItem.c_dsrxx.length > 0" class="text-xs">
                <div class="text-gray-500 mb-2">当事人信息</div>
                <div class="flex flex-wrap gap-2">
                  <span 
                    v-for="(person, pIndex) in caseItem.c_dsrxx" 
                    :key="pIndex"
                    :class="[
                      'px-2 py-1 rounded-full text-xs',
                      person.n_ssdw === '申请执行人' ? 'bg-green-100 text-green-700' : 
                      person.n_ssdw === '被执行人' ? 'bg-red-100 text-red-700' :
                      'bg-gray-100 text-gray-700'
                    ]"
                  >
                    {{ person.n_ssdw }}: {{ person.c_mc }}
                  </span>
                </div>
              </div>
              
              <!-- 详细信息 -->
              <div v-if="caseItem.c_gkws_dsr" class="text-xs">
                <div class="flex items-start">
                  <span class="text-gray-500 flex-shrink-0 mr-2">详细信息：</span>
                  <span class="text-gray-800 break-all leading-relaxed">{{ caseItem.c_gkws_dsr }}</span>
                </div>
              </div>
              
              <!-- 关联案件 -->
              <div v-if="caseItem.c_ah_hx || caseItem.c_ah_ys" class="text-xs">
                <div class="text-gray-500 mb-1">关联案件</div>
                <div class="space-y-1">
                  <div v-if="caseItem.c_ah_hx" class="text-gray-600">
                    <span class="text-gray-500">后续案件：</span>{{ caseItem.c_ah_hx.split(':')[0] }}
                  </div>
                  <div v-if="caseItem.c_ah_ys" class="text-gray-600">
                    <span class="text-gray-500">原审案件：</span>{{ caseItem.c_ah_ys.split(':')[0] }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 其他分布信息 - 标签式展示 -->
        <div class="space-y-3">
          <h5 class="text-sm font-medium text-gray-800 flex items-center">
            <Icon name="ph:chart-bar-bold" class="w-4 h-4 mr-2 text-gray-500" />
            统计分析
          </h5>
          
          <!-- 地区分布 -->
          <div v-if="getAreaDistribution().length > 0" class="bg-gray-50 rounded-lg p-3">
            <div class="text-xs text-gray-600 mb-2">地区分布</div>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="area in getAreaDistribution()" 
                :key="area.name"
                class="px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full"
              >
                {{ area.name }} ({{ area.count }})
              </span>
            </div>
          </div>

          <!-- 时间分布 -->
          <div v-if="getTimeDistribution().length > 0" class="bg-gray-50 rounded-lg p-3">
            <div class="text-xs text-gray-600 mb-2">年份分布</div>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="time in getTimeDistribution()" 
                :key="time.year"
                class="px-2 py-1 text-xs bg-green-100 text-green-700 rounded-full"
              >
                {{ time.year }}年 ({{ time.count }})
              </span>
            </div>
          </div>

          <!-- 结案方式分布 -->
          <div v-if="getJafsDistribution().length > 0" class="bg-gray-50 rounded-lg p-3">
            <div class="text-xs text-gray-600 mb-2">结案方式分布</div>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="jafs in getJafsDistribution()" 
                :key="jafs.name"
                class="px-2 py-1 text-xs bg-purple-100 text-purple-700 rounded-full"
              >
                {{ jafs.name }} ({{ jafs.count }})
              </span>
            </div>
          </div>

          <!-- 案由分布 -->
          <div v-if="getCauseDistribution().length > 0" class="bg-gray-50 rounded-lg p-3">
            <div class="text-xs text-gray-600 mb-2">主要案由分布</div>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="cause in getCauseDistribution()" 
                :key="cause.name"
                class="px-2 py-1 text-xs bg-orange-100 text-orange-700 rounded-full"
              >
                {{ cause.name }} ({{ cause.count }})
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 无数据状态 -->
    <div v-else class="text-center py-8">
      <div class="w-10 h-10 bg-gray-50 rounded-full flex items-center justify-center mx-auto mb-3">
        <Icon name="ph:file-text-bold" class="w-5 h-5 text-gray-400" />
      </div>
      <h4 class="text-sm font-medium text-gray-800 mb-1">暂无个人综合涉诉记录</h4>
      <p class="text-xs text-gray-600">暂无相关个人综合涉诉信息，或未被公开</p>
    </div>

    <!-- 调试信息 -->
    <div v-if="showDebug" class="mt-4 p-3 bg-gray-100 rounded-lg">
      <h5 class="text-xs font-medium text-gray-800 mb-2">调试信息</h5>
      <pre class="text-xs text-gray-600 whitespace-pre-wrap">{{ JSON.stringify(data, null, 2) }}</pre>
    </div>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, nextTick, watch } from 'vue'

// Props
const props = defineProps({
  data: {
    type: Object,
    default: () => ({})
  },
  showDebug: {
    type: Boolean,
    default: false
  }
})

// 响应式数据
const loading = ref(false)
const error = ref(null)
const activeTab = ref('criminal')
const pieChartRef = ref(null)
const tabsContainer = ref(null)
let chartInstance = null

// 获取基础数据
const getBaseData = () => {
  try {
    // 新的数据结构路径
    return props.data?.data?.data?.data?.lawsuit_person_info?.data[0]?.detail || {}
  } catch (error) {
    console.error('获取基础数据失败:', error)
    return {}
  }
}

// 案件类型tabs
const caseTabs = computed(() => [
  { key: 'criminal', label: '刑事案件', count: getCriminalCases() },
  { key: 'implement', label: '执行案件', count: getExecutionCases() },
  { key: 'civil', label: '民事案件', count: getCivilCases() },
  { key: 'administrative', label: '行政案件', count: getAdministrativeCases() },
  { key: 'preservation', label: '保全案件', count: getPreservationCases() },
  { key: 'bankrupt', label: '破产案件', count: getBankruptCases() },
  { key: 'xgbzxr', label: '限制高消费', count: getXgbzxrCases() }
])

// Tab滚动控制
const scrollTabs = (direction) => {
  if (!tabsContainer.value) return
  
  const scrollAmount = 200
  const currentScroll = tabsContainer.value.scrollLeft
  
  if (direction === 'left') {
    tabsContainer.value.scrollTo({
      left: currentScroll - scrollAmount,
      behavior: 'smooth'
    })
  } else {
    tabsContainer.value.scrollTo({
      left: currentScroll + scrollAmount,
      behavior: 'smooth'
    })
  }
}

// 获取案件数量
const getTotalCases = () => {
  try {
    const criminal = getCriminalCases()
    const execution = getExecutionCases()
    const civil = getCivilCases()
    const administrative = getAdministrativeCases()
    const preservation = getPreservationCases()
    const bankrupt = getBankruptCases()
    const xgbzxr = getXgbzxrCases()
    return criminal + execution + civil + administrative + preservation + bankrupt + xgbzxr
  } catch (error) {
    return 0
  }
}

// 获取各类案件数量
const getCriminalCases = () => {
  try {
    const baseData = getBaseData()
    return baseData?.criminal?.cases?.length || 0
  } catch (error) {
    console.error('获取刑事案件数量失败:', error)
    return 0
  }
}

const getExecutionCases = () => {
  try {
    const baseData = getBaseData()
    return baseData?.implement?.cases?.length || 0
  } catch (error) {
    console.error('获取执行案件数量失败:', error)
    return 0
  }
}

const getCivilCases = () => {
  try {
    const baseData = getBaseData()
    return baseData?.civil?.cases?.length || 0
  } catch (error) {
    console.error('获取民事案件数量失败:', error)
    return 0
  }
}

const getAdministrativeCases = () => {
  try {
    const baseData = getBaseData()
    return baseData?.administrative?.cases?.length || 0
  } catch (error) {
    console.error('获取行政案件数量失败:', error)
    return 0
  }
}

const getPreservationCases = () => {
  try {
    const baseData = getBaseData()
    return baseData?.preservation?.cases?.length || 0
  } catch (error) {
    console.error('获取保全案件数量失败:', error)
    return 0
  }
}

const getBankruptCases = () => {
  try {
    const baseData = getBaseData()
    return baseData?.bankrupt?.cases?.length || 0
  } catch (error) {
    console.error('获取破产案件数量失败:', error)
    return 0
  }
}

const getXgbzxrCases = () => {
  try {
    const xgData = props.data?.data?.data?.data?.lawsuit_person_info?.data[0]?.xg
    return xgData?.xgbzxr_current?.length || 0
  } catch (error) {
    console.error('获取限高案件数量失败:', error)
    return 0
  }
}

// 获取各类案件数据
const getCriminalData = () => {
  try {
    const baseData = getBaseData()
    return baseData?.criminal?.cases || []
  } catch (error) {
    console.error('获取刑事案件数据失败:', error)
    return []
  }
}

const getExecutionData = () => {
  try {
    const baseData = getBaseData()
    return baseData?.implement?.cases || []
  } catch (error) {
    console.error('获取执行案件数据失败:', error)
    return []
  }
}

const getCivilData = () => {
  try {
    const baseData = getBaseData()
    return baseData?.civil?.cases || []
  } catch (error) {
    console.error('获取民事案件数据失败:', error)
    return []
  }
}

const getAdministrativeData = () => {
  try {
    const baseData = getBaseData()
    return baseData?.administrative?.cases || []
  } catch (error) {
    console.error('获取行政案件数据失败:', error)
    return []
  }
}

const getPreservationData = () => {
  try {
    const baseData = getBaseData()
    return baseData?.preservation?.cases || []
  } catch (error) {
    console.error('获取保全案件数据失败:', error)
    return []
  }
}

const getBankruptData = () => {
  try {
    const baseData = getBaseData()
    return baseData?.bankrupt?.cases || []
  } catch (error) {
    console.error('获取破产案件数据失败:', error)
    return []
  }
}

const getXgbzxrData = () => {
  try {
    const xgData = props.data?.data?.data?.data?.lawsuit_person_info?.data[0]?.xg
    return xgData?.xgbzxr_current || []
  } catch (error) {
    console.error('获取限高案件数据失败:', error)
    return []
  }
}

// 获取所有案件数据用于统计
const getAllCases = () => {
  const allCases = []
  allCases.push(...getCriminalData())
  allCases.push(...getExecutionData())
  allCases.push(...getCivilData())
  allCases.push(...getAdministrativeData())
  allCases.push(...getPreservationData())
  allCases.push(...getBankruptData())
  return allCases
}

// 地区分布统计
const getAreaDistribution = () => {
  const allCases = getAllCases()
  const areaMap = {}
  
  allCases.forEach(caseItem => {
    if (caseItem.n_jbfy) {
      const area = extractAreaFromCourt(caseItem.n_jbfy)
      if (area) {
        areaMap[area] = (areaMap[area] || 0) + 1
      }
    }
  })
  
  return Object.entries(areaMap)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)
}

// 从法院名称中提取地区
const extractAreaFromCourt = (courtName) => {
  if (!courtName) return null
  
  const patterns = [
    /^(.+?)省/,
    /^(.+?)市/,
    /^(.+?)县/,
    /^(.+?)区/,
    /^(.+?)(人民法院|中级|高级|最高)/
  ]
  
  for (const pattern of patterns) {
    const match = courtName.match(pattern)
    if (match && match[1]) {
      return match[1]
    }
  }
  
  return null
}

// 时间分布统计
const getTimeDistribution = () => {
  const allCases = getAllCases()
  const yearMap = {}
  
  allCases.forEach(caseItem => {
    if (caseItem.d_larq) {
      const year = new Date(caseItem.d_larq).getFullYear()
      if (!isNaN(year)) {
        yearMap[year] = (yearMap[year] || 0) + 1
      }
    }
  })
  
  return Object.entries(yearMap)
    .map(([year, count]) => ({ year: parseInt(year), count }))
    .sort((a, b) => b.year - a.year)
}

// 结案方式分布统计
const getJafsDistribution = () => {
  const allCases = getAllCases()
  const jafsMap = {}
  
  allCases.forEach(caseItem => {
    if (caseItem.n_jafs && caseItem.n_jafs !== '--') {
      jafsMap[caseItem.n_jafs] = (jafsMap[caseItem.n_jafs] || 0) + 1
    }
  })
  
  return Object.entries(jafsMap)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 8)
}

// 案由分布统计
const getCauseDistribution = () => {
  const allCases = getAllCases()
  const causeMap = {}
  
  allCases.forEach(caseItem => {
    if (caseItem.n_laay_tree && caseItem.n_laay_tree !== '--') {
      const causes = caseItem.n_laay_tree.split(',').map(cause => cause.trim())
      causes.forEach(cause => {
        if (cause) {
          causeMap[cause] = (causeMap[cause] || 0) + 1
        }
      })
    }
  })
  
  return Object.entries(causeMap)
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 10)
}

// 日期格式化
const formatDate = (dateStr) => {
  if (!dateStr) return '--'
  try {
    const date = new Date(dateStr)
    if (isNaN(date.getTime())) return '--'
    return date.toLocaleDateString('zh-CN')
  } catch (error) {
    return '--'
  }
}

// 金额格式化
const formatMoney = (amount) => {
  if (!amount || amount === 0) return '--'
  
  const num = Number(amount)
  if (isNaN(num)) return '--'
  
  if (num >= 100000000) {
    return (num / 100000000).toFixed(2) + '亿'
  } else if (num >= 10000) {
    return (num / 10000).toFixed(2) + '万'
  } else {
    return num.toLocaleString('zh-CN')
  }
}

// 组件挂载时打印调试信息
onMounted(async () => {
  console.log('[PersonalJudicialResult] 组件已挂载')
  console.log('[PersonalJudicialResult] 接收到的数据:', props.data)
  
  if (props.data) {
    const baseData = getBaseData()
    console.log('[PersonalJudicialResult] 基础数据:', baseData)
    console.log('[PersonalJudicialResult] 案件数量统计:')
    console.log('- 刑事案件:', getCriminalCases())
    console.log('- 执行案件:', getExecutionCases())
    console.log('- 民事案件:', getCivilCases())
    console.log('- 行政案件:', getAdministrativeCases())
    console.log('- 保全案件:', getPreservationCases())
    console.log('- 破产案件:', getBankruptCases())
    console.log('- 限高案件:', getXgbzxrCases())

    // 等待DOM更新后创建饼图
    await nextTick()
    createPieChart()
  }
})

// 监听数据变化，更新饼图
watch(() => props.data, async (newVal) => {
  if (newVal) {
    await nextTick()
    createPieChart()
  }
}, { deep: true })

// 组件销毁前清理图表
onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.destroy()
    chartInstance = null
  }
})

// 创建饼图
const createPieChart = async () => {
  if (!pieChartRef.value) return

  try {
    const { Chart, registerables } = await import('chart.js')
    Chart.register(...registerables)

    const ctx = pieChartRef.value.getContext('2d')
    
    if (chartInstance) {
      chartInstance.destroy()
    }

    // 获取最新的案件数量
    const chartData = [
      { label: '刑事', value: getCriminalCases(), color: '#FCA5A5' },
      { label: '执行', value: getExecutionCases(), color: '#86EFAC' },
      { label: '民事', value: getCivilCases(), color: '#93C5FD' },
      { label: '行政', value: getAdministrativeCases(), color: '#FDE68A' },
      { label: '保全', value: getPreservationCases(), color: '#DDD6FE' },
      { label: '破产', value: getBankruptCases(), color: '#D1D5DB' },
      { label: '限高', value: getXgbzxrCases(), color: '#FEF3C7' }
    ]

    console.log('[PersonalJudicialResult] 饼图数据:', chartData)

    const hasData = chartData.some(item => item.value > 0)
    
    if (!hasData) {
      chartData[0] = { label: '暂无数据', value: 1, color: '#F3F4F6' }
    }

    chartInstance = new Chart(ctx, {
      type: 'pie',
      data: {
        labels: chartData.map(item => item.label),
        datasets: [{
          data: chartData.map(item => item.value),
          backgroundColor: chartData.map(item => item.color),
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              usePointStyle: true,
              padding: 15,
              font: {
                size: 12
              },
              filter: function(legendItem, chartData) {
                return hasData
              }
            }
          },
          tooltip: {
            enabled: hasData,
            callbacks: {
              label: function(context) {
                if (!hasData) return ''
                const total = context.dataset.data.reduce((a, b) => a + b, 0)
                const percentage = ((context.parsed / total) * 100).toFixed(1)
                return `${context.label}: ${context.parsed} (${percentage}%)`
              }
            }
          }
        }
      }
    })

    console.log('[PersonalJudicialResult] 饼图创建成功')
  } catch (error) {
    console.error('[PersonalJudicialResult] 创建饼图失败:', error)
  }
}
</script>

<style scoped>
/* ... existing code ... */
</style> 
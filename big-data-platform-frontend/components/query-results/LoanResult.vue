<template>
  <section id="loan-result" class="bg-white rounded-xl shadow-sm p-4 mb-4">
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center space-x-2">
        <div class="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
          <Icon name="ph:strategy-bold" class="w-5 h-5 text-orange-600" />
        </div>
        <div>
          <h3 class="text-base font-semibold text-gray-800">多头借贷分析</h3>
          <p class="text-xs text-gray-500">近12个月多头借贷分析查询结果</p>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <span class="text-xs text-gray-400">API: JRZQ0A03</span>
        <div v-if="data?.success" class="w-2 h-2 bg-green-500 rounded-full"></div>
        <div v-else class="w-2 h-2 bg-red-500 rounded-full"></div>
      </div>
    </div>

    <!-- 成功状态 -->
    <div v-if="data?.success" class="space-y-4">
      <!-- 总体概览 -->
      <div class="bg-gradient-to-r from-orange-50 to-yellow-50 rounded-lg p-4">
        <h4 class="text-sm font-semibold text-gray-800 mb-3">借贷概览</h4>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
          <div class="text-center">
            <div class="text-xl font-bold text-orange-600">{{ getRiskLevel() }}</div>
            <div class="text-xs text-gray-600">风险等级</div>
          </div>
          <div class="text-center">
            <div class="text-xl font-bold text-blue-600">{{ getTotalApplications() }}</div>
            <div class="text-xs text-gray-600">总申请次数</div>
          </div>
          <div class="text-center">
            <div class="text-xl font-bold text-green-600">{{ getTotalOrganizations() }}</div>
            <div class="text-xs text-gray-600">涉及机构数</div>
          </div>
          <div class="text-center">
            <div class="text-xl font-bold text-purple-600">{{ getActiveMonths() }}/12</div>
            <div class="text-xs text-gray-600">活跃月份数</div>
          </div>
        </div>
      </div>

      <!-- 申请趋势分析（合并原来的时间趋势和时间段对比） -->
      <div class="bg-white border rounded-lg p-4">
        <h4 class="text-sm font-semibold text-gray-800 mb-3">申请趋势分析</h4>
        <div class="h-64">
          <canvas ref="trendChart"></canvas>
        </div>
      </div>

      <!-- 机构类型分布和产品类型分布 -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- 银行vs非银机构分布 -->
        <div class="bg-white border rounded-lg p-4">
          <h4 class="text-sm font-semibold text-gray-800 mb-3">机构类型分布<span class="text-xs text-gray-500">(近12个月)</span></h4>
          <div class="h-48">
            <canvas ref="institutionChart"></canvas>
          </div>
        </div>

        <!-- 申请类型分布 -->
        <div class="bg-white border rounded-lg p-4">
          <h4 class="text-sm font-semibold text-gray-800 mb-3">申请类型分布<span class="text-xs text-gray-500">(近12个月)</span></h4>
          <div class="h-48">
            <canvas ref="applicationTypeChart"></canvas>
          </div>
        </div>
      </div>

      <!-- 产品类型详细分布 -->
      <div class="bg-white border rounded-lg p-4">
        <h4 class="text-sm font-semibold text-gray-800 mb-3">产品类型详细分布 <span class="text-xs text-gray-500">(近12个月)</span></h4>
        <div class="overflow-x-auto">
          <table class="w-full text-xs">
            <thead>
              <tr class="border-b">
                <th class="text-left py-2 px-3 font-medium text-gray-700">产品类型</th>
                <th class="text-left py-2 px-3 font-medium text-gray-700">申请次数</th>
                <th class="text-left py-2 px-3 font-medium text-gray-700">机构数</th>
                <th class="text-left py-2 px-3 font-medium text-gray-700">占比</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="product in getProductDistribution()" :key="product.name" class="border-b hover:bg-gray-50">
                <td class="py-2 px-3 font-medium">{{ product.name }}</td>
                <td class="py-2 px-3">{{ product.applications }}</td>
                <td class="py-2 px-3">{{ product.organizations }}</td>
                <td class="py-2 px-3">
                  <div class="flex items-center space-x-2">
                    <div class="w-12 bg-gray-200 rounded-full h-1.5">
                      <div 
                        class="h-1.5 rounded-full" 
                        :style="{ width: product.percentage + '%', backgroundColor: product.color }"
                      ></div>
                    </div>
                    <span class="text-xs">{{ product.percentage }}%</span>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 时间段详细分析 -->
      <div class="bg-white border rounded-lg p-4">
        <h4 class="text-sm font-semibold text-gray-800 mb-3">时间段详细分析</h4>
        <div class="space-y-3">
          <div 
            v-for="period in getTimePeriodsData()" 
            :key="period.name" 
            class="border border-gray-200 rounded-lg overflow-hidden"
          >
            <div 
              class="p-3 flex justify-between items-center" 
              :class="getPeriodHeaderClass(period)"
            >
              <div class="font-medium">{{ period.name }}</div>
              <div class="flex items-center space-x-2">
                <span class="text-sm">总申请: {{ period.applications }}次</span>
                <span 
                  v-if="period.isHighRisk" 
                  class="px-2 py-0.5 text-xs bg-red-100 text-red-800 rounded-full"
                >
                  高频
                </span>
              </div>
            </div>
            <div class="p-3 bg-white">
              <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
                <div>
                  <div class="text-xs text-gray-500">银行机构申请</div>
                  <div class="text-sm font-medium text-green-600">{{ period.bankApplications }}次</div>
                </div>
                <div>
                  <div class="text-xs text-gray-500">非银机构申请</div>
                  <div class="text-sm font-medium text-purple-600">{{ period.nonBankApplications }}次</div>
                </div>
                <div>
                  <div class="text-xs text-gray-500">银行机构数</div>
                  <div class="text-sm font-medium text-green-600">{{ period.bankOrganizations }}个</div>
                </div>
                <div>
                  <div class="text-xs text-gray-500">非银机构数</div>
                  <div class="text-sm font-medium text-purple-600">{{ period.nonBankOrganizations }}个</div>
                </div>
              </div>
                           <!-- 申请强度分析（如果有相关数据） -->
              <div v-if="period.hasIntensityData" class="mb-3">
                <div class="text-xs text-gray-500 mb-2">申请强度分析</div>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                  <div v-if="period.avgMonthlyApplications !== null" class="text-center p-2 bg-green-50 rounded">
                    <div class="font-bold text-green-600">{{ period.avgMonthlyApplications }}</div>
                    <div class="text-xs text-gray-600">平均月申请次数</div>
                  </div>
                  <div v-if="period.maxMonthlyApplications !== null" class="text-center p-2 bg-red-50 rounded">
                    <div class="font-bold text-red-600">{{ period.maxMonthlyApplications }}</div>
                    <div class="text-xs text-gray-600">最大月申请次数</div>
                  </div>
                  <div v-if="period.minMonthlyApplications !== null" class="text-center p-2 bg-yellow-50 rounded">
                    <div class="font-bold text-yellow-600">{{ period.minMonthlyApplications }}</div>
                    <div class="text-xs text-gray-600">最小月申请次数</div>
                  </div>
                  <div v-if="period.activeMonths !== null" class="text-center p-2 bg-purple-50 rounded">
                    <div class="font-bold text-purple-600">{{ period.activeMonths }}</div>
                    <div class="text-xs text-gray-600">活跃月份数</div>
                  </div>
                </div>
              </div>
              <!-- 申请时间模式（如果有周末/夜间数据） -->
              <div v-if="period.hasTimePattern" class="mb-3">
                <div class="text-xs text-gray-500 mb-2">申请时间模式</div>
                <div class="grid grid-cols-2 gap-3">
                  <div class="flex items-center justify-between p-2 bg-blue-50 rounded">
                    <span class="text-xs font-medium text-gray-700">周末申请占比</span>
                    <div class="flex items-center space-x-2">
                      <div class="w-12 bg-gray-200 rounded-full h-1.5">
                        <div 
                          class="bg-blue-500 h-1.5 rounded-full" 
                          :style="{ width: period.weekendRatio + '%' }"
                        ></div>
                      </div>
                      <span class="text-xs font-semibold text-blue-600">{{ period.weekendRatio }}%</span>
                    </div>
                  </div>
                  <div class="flex items-center justify-between p-2 bg-purple-50 rounded">
                    <span class="text-xs font-medium text-gray-700">夜间申请占比</span>
                    <div class="flex items-center space-x-2">
                      <div class="w-12 bg-gray-200 rounded-full h-1.5">
                        <div 
                          class="bg-purple-500 h-1.5 rounded-full" 
                          :style="{ width: period.nightRatio + '%' }"
                        ></div>
                      </div>
                      <span class="text-xs font-semibold text-purple-600">{{ period.nightRatio }}%</span>
                    </div>
                  </div>
                </div>
                <div class="grid grid-cols-2 gap-2 text-xs mt-2">
                  <div class="text-center p-2 bg-gray-50 rounded">
                    <div class="font-bold text-gray-800">{{ period.weekendApplications }}</div>
                    <div class="text-gray-600">周末申请次数</div>
                  </div>
                  <div class="text-center p-2 bg-gray-50 rounded">
                    <div class="font-bold text-gray-800">{{ period.nightApplications }}</div>
                    <div class="text-gray-600">夜间申请次数</div>
                  </div>
                </div>
              </div>

 

              <!-- 申请间隔分析 -->
              <div v-if="period.hasIntervalData">
                <div class="text-xs text-gray-500 mb-2">申请间隔分析</div>
                <div class="grid grid-cols-2 gap-2 text-xs">
                  <div class="text-center p-2 bg-gray-50 rounded">
                    <div class="font-bold text-gray-800">{{ period.maxInterval }}</div>
                    <div class="text-gray-600">最大间隔天数</div>
                  </div>
                  <div class="text-center p-2 bg-gray-50 rounded">
                    <div class="font-bold text-gray-800">{{ period.minInterval }}</div>
                    <div class="text-gray-600">最小间隔天数</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 数据策略信息 -->
      <div v-if="getDataStrategy()" class="bg-blue-50 rounded-lg p-3">
        <h4 class="text-xs font-semibold text-gray-800 mb-2">数据策略信息</h4>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
          <div class="flex justify-between">
            <span class="text-gray-600">策略版本：</span>
            <span class="font-mono text-gray-800">{{ getDataStrategy().strategy_version }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">策略ID：</span>
            <span class="font-mono text-gray-800">{{ getDataStrategy().strategy_id }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-600">场景：</span>
            <span class="text-gray-800">{{ getDataStrategy().scene }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 无数据状态 -->
    <div v-else class="text-center py-6">
      <div class="w-10 h-10 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-2">
        <Icon name="ph:file-text-bold" class="w-5 h-5 text-gray-400" />
      </div>
      <h4 class="text-sm font-semibold text-gray-800 mb-1">暂无借贷意向数据</h4>
      <p class="text-xs text-gray-600">未查询到相关的借贷意向信息，或未被公开</p>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    default: null
  }
})

const selectedView = ref('summary')
const trendChart = ref(null)
const institutionChart = ref(null)
const applicationTypeChart = ref(null)

let chartInstances = []

// 获取风险等级
const getRiskLevel = () => {
  const totalApps = getTotalApplications()
  const totalOrgs = getTotalOrganizations()
  
  if (totalApps === 0) return '无记录'
  if (totalApps <= 5 && totalOrgs <= 2) return '低风险'
  if (totalApps <= 20 && totalOrgs <= 5) return '中风险'
  return '高风险'
}

// 获取总申请次数（身份证）
const getTotalApplications = () => {
  if (!props.data?.data?.data) return 0
  const data = props.data.data.data
  
  return (parseInt(data.als_m12_id_nbank_allnum) || 0) + (parseInt(data.als_m12_id_bank_allnum) || 0)
}

// 获取总机构数（身份证）
const getTotalOrganizations = () => {
  if (!props.data?.data?.data) return 0
  const data = props.data.data.data
  
  return (parseInt(data.als_m12_id_nbank_orgnum) || 0) + (parseInt(data.als_m12_id_bank_orgnum) || 0)
}

// 获取活跃月份数（显示为 X/12 的形式）
const getActiveMonths = () => {
  if (!props.data?.data?.data) return 0
  const data = props.data.data.data
  
  return parseInt(data.als_m12_id_tot_mons) || 0
}

// 获取产品分布数据
const getProductDistribution = () => {
  if (!props.data?.data?.data) return []
  const data = props.data.data.data
  
  const products = [
    { name: '线上小额现金贷', applications: parseInt(data.als_m12_id_pdl_allnum) || 0, organizations: parseInt(data.als_m12_id_pdl_orgnum) || 0, color: '#3B82F6' },
    { name: '线上现金分期', applications: parseInt(data.als_m12_id_caon_allnum) || 0, organizations: parseInt(data.als_m12_id_caon_orgnum) || 0, color: '#06B6D4' },
    { name: '信用卡申请', applications: parseInt(data.als_m12_id_rel_allnum) || 0, organizations: parseInt(data.als_m12_id_rel_orgnum) || 0, color: '#8B5CF6' },
    { name: '汽车金融', applications: parseInt(data.als_m12_id_af_allnum) || 0, organizations: parseInt(data.als_m12_id_af_orgnum) || 0, color: '#10B981' },
    { name: '线上消费分期', applications: parseInt(data.als_m12_id_coon_allnum) || 0, organizations: parseInt(data.als_m12_id_coon_orgnum) || 0, color: '#F59E0B' },
    { name: '线下现金分期', applications: parseInt(data.als_m12_id_caoff_allnum) || 0, organizations: parseInt(data.als_m12_id_caoff_orgnum) || 0, color: '#EF4444' },
    { name: '线下消费分期', applications: parseInt(data.als_m12_id_cooff_allnum) || 0, organizations: parseInt(data.als_m12_id_cooff_orgnum) || 0, color: '#EC4899' },
    { name: '其他', applications: parseInt(data.als_m12_id_oth_allnum) || 0, organizations: parseInt(data.als_m12_id_oth_orgnum) || 0, color: '#6B7280' }
  ]
  
  const totalApps = products.reduce((sum, p) => sum + p.applications, 0)
  
  return products
    .filter(p => p.applications > 0)
    .map(p => ({
      ...p,
      percentage: totalApps > 0 ? Math.round((p.applications / totalApps) * 100) : 0
    }))
    .sort((a, b) => b.applications - a.applications)
}

// 获取时间段数据
const getTimePeriodsData = () => {
  if (!props.data?.data?.data) return []
  const data = props.data.data.data
  
  const periods = [
    { 
      name: '近7天', 
      bankField: 'als_d7_id_bank_allnum', 
      nonBankField: 'als_d7_id_nbank_allnum',
      bankOrgField: 'als_d7_id_bank_orgnum',
      nonBankOrgField: 'als_d7_id_nbank_orgnum',
      hasIntervalData: false,
      hasTimePattern: false,
      hasIntensityData: false
    },
    { 
      name: '近15天', 
      bankField: 'als_d15_id_bank_allnum', 
      nonBankField: 'als_d15_id_nbank_allnum',
      bankOrgField: 'als_d15_id_bank_orgnum',
      nonBankOrgField: 'als_d15_id_nbank_orgnum',
      hasIntervalData: false,
      hasTimePattern: false,
      hasIntensityData: false
    },
    { 
      name: '近1个月', 
      bankField: 'als_m1_id_bank_allnum', 
      nonBankField: 'als_m1_id_nbank_allnum',
      bankOrgField: 'als_m1_id_bank_orgnum',
      nonBankOrgField: 'als_m1_id_nbank_orgnum',
      hasIntervalData: false,
      hasTimePattern: false,
      hasIntensityData: false
    },
    { 
      name: '近3个月', 
      bankField: 'als_m3_id_bank_allnum', 
      nonBankField: 'als_m3_id_nbank_allnum',
      bankOrgField: 'als_m3_id_bank_orgnum',
      nonBankOrgField: 'als_m3_id_nbank_orgnum',
      maxIntervalField: 'als_m3_id_max_inteday',
      minIntervalField: 'als_m3_id_min_inteday',
      bankWeekField: 'als_m3_id_bank_week_allnum',
      nonBankWeekField: 'als_m3_id_nbank_week_allnum',
      bankNightField: 'als_m3_id_bank_night_allnum',
      nonBankNightField: 'als_m3_id_nbank_night_allnum',
      avgMonthlyField: 'als_m3_id_avg_monnum',
      maxMonthlyField: 'als_m3_id_max_monnum',
      minMonthlyField: 'als_m3_id_min_monnum',
      activeMonthsField: 'als_m3_id_tot_mons',
      hasIntervalData: true,
      hasTimePattern: true,
      hasIntensityData: true
    },
    { 
      name: '近6个月', 
      bankField: 'als_m6_id_bank_allnum', 
      nonBankField: 'als_m6_id_nbank_allnum',
      bankOrgField: 'als_m6_id_bank_orgnum',
      nonBankOrgField: 'als_m6_id_nbank_orgnum',
      maxIntervalField: 'als_m6_id_max_inteday',
      minIntervalField: 'als_m6_id_min_inteday',
      bankWeekField: 'als_m6_id_bank_week_allnum',
      nonBankWeekField: 'als_m6_id_nbank_week_allnum',
      bankNightField: 'als_m6_id_bank_night_allnum',
      nonBankNightField: 'als_m6_id_nbank_night_allnum',
      avgMonthlyField: 'als_m6_id_avg_monnum',
      maxMonthlyField: 'als_m6_id_max_monnum',
      minMonthlyField: 'als_m6_id_min_monnum',
      activeMonthsField: 'als_m6_id_tot_mons',
      hasIntervalData: true,
      hasTimePattern: true,
      hasIntensityData: true
    },
    { 
      name: '近12个月', 
      bankField: 'als_m12_id_bank_allnum', 
      nonBankField: 'als_m12_id_nbank_allnum',
      bankOrgField: 'als_m12_id_bank_orgnum',
      nonBankOrgField: 'als_m12_id_nbank_orgnum',
      maxIntervalField: 'als_m12_id_max_inteday',
      minIntervalField: 'als_m12_id_min_inteday',
      bankWeekField: 'als_m12_id_bank_week_allnum',
      nonBankWeekField: 'als_m12_id_nbank_week_allnum',
      bankNightField: 'als_m12_id_bank_night_allnum',
      nonBankNightField: 'als_m12_id_nbank_night_allnum',
      avgMonthlyField: 'als_m12_id_avg_monnum',
      maxMonthlyField: 'als_m12_id_max_monnum',
      minMonthlyField: 'als_m12_id_min_monnum',
      activeMonthsField: 'als_m12_id_tot_mons',
      hasIntervalData: true,
      hasTimePattern: true,
      hasIntensityData: true
    }
  ]
  
  return periods.map(period => {
    const bankApps = parseInt(data[period.bankField]) || 0
    const nonBankApps = parseInt(data[period.nonBankField]) || 0
    const bankOrgs = parseInt(data[period.bankOrgField]) || 0
    const nonBankOrgs = parseInt(data[period.nonBankOrgField]) || 0
    const totalApps = bankApps + nonBankApps
    
    let maxInterval = '--'
    let minInterval = '--'
    let weekendApplications = 0
    let nightApplications = 0
    let weekendRatio = 0
    let nightRatio = 0
    let avgMonthlyApplications = null
    let maxMonthlyApplications = null
    let minMonthlyApplications = null
    let activeMonths = null
    
    if (period.hasIntervalData) {
      const maxVal = parseInt(data[period.maxIntervalField]) || 0
      const minVal = parseInt(data[period.minIntervalField]) || 0
      maxInterval = maxVal === 0 ? '--' : maxVal
      minInterval = minVal === 0 ? '--' : minVal
    }
    
    if (period.hasTimePattern) {
      const bankWeekApps = parseInt(data[period.bankWeekField]) || 0
      const nonBankWeekApps = parseInt(data[period.nonBankWeekField]) || 0
      const bankNightApps = parseInt(data[period.bankNightField]) || 0
      const nonBankNightApps = parseInt(data[period.nonBankNightField]) || 0
      
      weekendApplications = bankWeekApps + nonBankWeekApps
      nightApplications = bankNightApps + nonBankNightApps
      weekendRatio = totalApps > 0 ? Math.round((weekendApplications / totalApps) * 100) : 0
      nightRatio = totalApps > 0 ? Math.round((nightApplications / totalApps) * 100) : 0
    }
    
    if (period.hasIntensityData) {
      avgMonthlyApplications = parseFloat(data[period.avgMonthlyField]) || 0
      maxMonthlyApplications = parseInt(data[period.maxMonthlyField]) || 0
      minMonthlyApplications = parseInt(data[period.minMonthlyField]) || 0
      activeMonths = parseInt(data[period.activeMonthsField]) || 0
    }
    
    return {
      name: period.name,
      applications: totalApps,
      bankApplications: bankApps,
      nonBankApplications: nonBankApps,
      bankOrganizations: bankOrgs,
      nonBankOrganizations: nonBankOrgs,
      isHighRisk: totalApps > 10, // 简单的高频判断
      hasIntervalData: period.hasIntervalData,
      hasTimePattern: period.hasTimePattern,
      hasIntensityData: period.hasIntensityData,
      maxInterval,
      minInterval,
      weekendApplications,
      nightApplications,
      weekendRatio,
      nightRatio,
      avgMonthlyApplications,
      maxMonthlyApplications,
      minMonthlyApplications,
      activeMonths
    }
  })
}

// 获取时间段头部样式
const getPeriodHeaderClass = (period) => {
  if (period.isHighRisk) {
    return 'bg-red-50'
  }
  if (period.applications > 0) {
    return 'bg-blue-50'
  }
  return 'bg-gray-50'
}

// 获取数据策略信息
const getDataStrategy = () => {
  return props.data?.data?.data?.DataStrategy || null
}

// 初始化图表
const initCharts = async () => {
  if (!props.data?.success) return
  
  try {
    const { Chart, registerables } = await import('chart.js')
    Chart.register(...registerables)
    
    // 申请趋势图（合并原来的时间趋势和时间段对比）
    if (trendChart.value) {
      const periodsData = getTimePeriodsData()
      const trendChartInstance = new Chart(trendChart.value, {
        type: 'bar',
        data: {
          labels: periodsData.map(item => item.name),
          datasets: [
            {
              label: '银行申请',
              data: periodsData.map(item => item.bankApplications),
              backgroundColor: 'rgba(34, 197, 94, 0.8)'
            },
            {
              label: '非银申请',
              data: periodsData.map(item => item.nonBankApplications),
              backgroundColor: 'rgba(168, 85, 247, 0.8)'
            }
          ]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'top',
              labels: {
                font: {
                  size: 11
                }
              }
            }
          },
          scales: {
            x: {
              stacked: true,
              ticks: {
                font: {
                  size: 10
                }
              }
            },
            y: {
              stacked: true,
              beginAtZero: true,
              ticks: {
                font: {
                  size: 10
                }
              }
            }
          }
        }
      })
      chartInstances.push(trendChartInstance)
    }
    
    // 机构类型分布图
    if (institutionChart.value) {
      const data = props.data.data.data
      const bankApps = parseInt(data.als_m12_id_bank_allnum) || 0
      const nonBankApps = parseInt(data.als_m12_id_nbank_allnum) || 0
      
      const institutionChartInstance = new Chart(institutionChart.value, {
        type: 'doughnut',
        data: {
          labels: ['银行机构', '非银机构'],
          datasets: [{
            data: [bankApps, nonBankApps],
            backgroundColor: [
              'rgba(34, 197, 94, 0.8)',
              'rgba(168, 85, 247, 0.8)'
            ],
            borderWidth: 2,
            borderColor: '#fff'
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom',
              labels: {
                font: {
                  size: 11
                }
              }
            }
          }
        }
      })
      chartInstances.push(institutionChartInstance)
    }
    
    // 申请类型分布图
    if (applicationTypeChart.value) {
      const products = getProductDistribution()
      const applicationTypeChartInstance = new Chart(applicationTypeChart.value, {
        type: 'bar',
        data: {
          labels: products.map(p => p.name),
          datasets: [{
            label: '申请次数',
            data: products.map(p => p.applications),
            backgroundColor: products.map(p => p.color)
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                font: {
                  size: 10
                }
              }
            },
            x: {
              ticks: {
                font: {
                  size: 10
                }
              }
            }
          }
        }
      })
      chartInstances.push(applicationTypeChartInstance)
    }
    
  } catch (error) {
    console.error('Chart initialization failed:', error)
  }
}

// 清理图表
const destroyCharts = () => {
  chartInstances.forEach(chart => {
    if (chart) {
      chart.destroy()
    }
  })
  chartInstances = []
}

// 监听数据变化
watch(() => props.data, () => {
  destroyCharts()
  if (props.data?.success) {
    nextTick(() => {
      initCharts()
    })
  }
}, { deep: true })

onMounted(() => {
  if (props.data?.success) {
    nextTick(() => {
      initCharts()
    })
  }
})

onUnmounted(() => {
  destroyCharts()
})
</script> 
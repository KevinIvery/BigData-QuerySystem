// big-data-platform-frontend/composables/useApiComponentMap.js
import JudicialResult from '~/components/query-results/JudicialResult.vue'
import MarriageResult from '~/components/query-results/MarriageResult.vue'
import LoanResult from '~/components/query-results/LoanResult.vue'
import ReportOverview from '~/components/query-results/ReportOverview.vue'
// 企业相关组件
import Enterprise_JudicialResult from '~/components/query-results/Enterprise_JudicialResult.vue'
import Enterprise_ReportOverview from '~/components/query-results/Enterprise_ReportOverview.vue'

// ================================
// 个人查询配置
// ================================
const PERSONAL_API_CONFIG = {
  // 报告概况
  REPORT_OVERVIEW: {
    component: ReportOverview,
    title: '报告概况',
    icon: 'ph:user-circle-bold',
    menuId: 'report-overview',
    iconColor: 'text-blue-600',
    iconBg: 'bg-blue-100'
  },
  // 司法涉诉
  FLXG0V4B: {
    component: JudicialResult,
    title: '司法涉诉',
    icon: 'ph:police-car-bold',
    menuId: 'judicial-result',
    iconColor: 'text-red-600',
    iconBg: 'bg-red-100'
  },
  // 婚姻状况
  IVYZ5733: {
    component: MarriageResult,
    title: '婚姻状况',
    icon: 'ph:heartbeat-bold',
    menuId: 'marriage-result',
    iconColor: 'text-red-500',
    iconBg: 'bg-red-100'
  },
  // 借贷行为
  JRZQ0A03: {
    component: LoanResult,
    title: '多头借贷',
    icon: 'ph:strategy-bold',
    menuId: 'loan-result',
    iconColor: 'text-orange-500',
    iconBg: 'bg-orange-100'
  }
}

// ================================
// 企业查询配置
// ================================
const ENTERPRISE_API_CONFIG = {
  // 企业报告概况
  ENTERPRISE_REPORT_OVERVIEW: {
    component: Enterprise_ReportOverview,
    title: '企业报告概况',
    icon: 'ph:buildings-bold',
    menuId: 'enterprise-report-overview',
    iconColor: 'text-blue-600',
    iconBg: 'bg-blue-100'
  },
  // 企业综合涉诉
  QYGL8261: {
    component: Enterprise_JudicialResult,
    title: '企业综合涉诉',
    icon: 'ph:police-car-bold',
    menuId: 'enterprise-judicial-result',
    iconColor: 'text-red-600',
    iconBg: 'bg-red-100'
  }
  // 后续新增企业API在此添加
  // 例如：
  // QYXX1234: {
  //   component: Enterprise_CreditResult,
  //   title: '企业信用',
  //   icon: 'ph:certificate-bold',
  //   menuId: 'enterprise-credit-result',
  //   iconColor: 'text-green-600',
  //   iconBg: 'bg-green-100'
  // }
}

// ================================
// 通用配置（司法细项等）
// ================================
const COMMON_CONFIG = {
  // 司法细项（仅用于卡片/目录，不渲染组件）
  BANKRUPT: {
    title: '破产案件', icon: 'ph:archive-box-bold', iconColor: 'text-purple-600', iconBg: 'bg-purple-100'
  },
  CIVIL: {
    title: '民事案件', icon: 'ph:handshake-bold', iconColor: 'text-blue-600', iconBg: 'bg-blue-100'
  },
  CRIMINAL: {
    title: '刑事案件', icon: 'ph:police-car-bold', iconColor: 'text-red-600', iconBg: 'bg-red-100'
  },
  ADMIN: {
    title: '行政案件', icon: 'ph:bank-bold', iconColor: 'text-green-600', iconBg: 'bg-green-100'
  },
  PRESERVATION: {
    title: '非诉保全', icon: 'ph:shield-check-bold', iconColor: 'text-yellow-600', iconBg: 'bg-yellow-100'
  },
  COMPENSATION: {
    title: '赔偿案件', icon: 'ph:currency-circle-dollar-bold', iconColor: 'text-amber-600', iconBg: 'bg-amber-100'
  },
  JURISDICTION: {
    title: '管辖案件', icon: 'ph:globe-bold', iconColor: 'text-cyan-600', iconBg: 'bg-cyan-100'
  },
  LIMIT_HIGH: {
    title: '限高',
    icon: 'ph:arrow-fat-lines-up-bold',
    iconColor: 'text-yellow-700',
    iconBg: 'bg-yellow-100'
  },
  LIMIT_LOW: {
    title: '失信被执行',
    icon: 'ph:warning-octagon-bold',
    iconColor: 'text-orange-700',
    iconBg: 'bg-orange-100'
  },
  MARRIAGE: { title: '婚姻状况', icon: 'ph:heartbeat-bold', iconColor: 'text-red-500', iconBg: 'bg-red-100' },
  // 兜底
  DEFAULT: {
    title: '其他', icon: 'ph:files-bold', iconColor: 'text-gray-500', iconBg: 'bg-gray-100'
  }
}

// ================================
// 导出的主要配置和方法
// ================================

// 合并所有配置
export const apiComponentMap = {
  ...PERSONAL_API_CONFIG,
  ...ENTERPRISE_API_CONFIG,
  ...COMMON_CONFIG
}

// 企业API代码列表（从配置中自动生成）
export const ENTERPRISE_API_CODES = Object.keys(ENTERPRISE_API_CONFIG)

// 判断API代码是否为企业类型
export const isEnterpriseApi = (apiCode) => {
  return ENTERPRISE_API_CODES.includes(apiCode)
}

// 子标签映射
export const apiSubItemsMap = {
  // 司法涉诉细项
  FLXG0V4B: [
    { code: 'BANKRUPT', title: '破产案件' },
    { code: 'CIVIL', title: '民事案件' },
    { code: 'CRIMINAL', title: '刑事案件' },
    { code: 'ADMIN', title: '行政案件' },
    { code: 'PRESERVATION', title: '非诉保全' },
    { code: 'COMPENSATION', title: '赔偿案件' },
    { code: 'JURISDICTION', title: '管辖案件' },
    { code: 'LIMIT_HIGH', title: '限高' },
    { code: 'LIMIT_LOW', title: '失信被执行' },
  ],
  // 婚姻状况细项
  IVYZ5733: [
    { code: 'MARRIAGE', title: '婚姻状况' }
  ],
  // 借贷行为细项
  JRZQ0A03: [
    { code: 'JRZQ0A03', title: '多头借贷' }
  ],
  // 企业综合涉诉细项
  QYGL8261: [
    { code: 'BANKRUPT', title: '破产案件' },
    { code: 'CIVIL', title: '民事案件' },
    { code: 'CRIMINAL', title: '刑事案件' },
    { code: 'ADMIN', title: '行政案件' },
    { code: 'PRESERVATION', title: '非诉保全' },
    { code: 'COMPENSATION', title: '赔偿案件' },
    { code: 'JURISDICTION', title: '管辖案件' },
    { code: 'LIMIT_HIGH', title: '限高' },
    { code: 'LIMIT_LOW', title: '失信被执行' },
  ]
}

// 司法细项常量（用于卡片展示）
export const JUDICIAL_DETAIL_ITEMS = [
  'BANKRUPT',
  'CIVIL',
  'CRIMINAL',
  'ADMIN',
  'PRESERVATION',
  'COMPENSATION',
  'JURISDICTION'
] 
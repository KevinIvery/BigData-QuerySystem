<template>
  <div class="space-y-6 text-gray-800 leading-relaxed overflow-y-auto h-full font-songti">
    <!-- 标题 -->
    <h1 class="text-center font-bold text-xl">数据查询授权书</h1>
    
    <!-- 致送单位 -->
    <p class="pt-4">致：{{ companyName }}</p>

    <!-- 正文 -->
    <p class="text-indent-2">
      本人，<strong class="underline px-2">{{ name || '（待传入）' }}</strong>（身份证号码：<strong class="underline px-2">{{ idCard || '（待传入）' }}</strong>），在此确认并同意，为使用贵平台提供的大数据查询服务，本人自愿、明确且不可撤销地授权贵公司及贵公司合作的第三方数据服务机构，依据本授权书查询、核验、处理与本人相关的，为完成风险评估所必需的个人信息（包括但不限于个人基本信息、司法涉诉信息、信贷风险信息等）。
    </p>

    <p class="text-indent-2">
      本人同意贵公司将前述查询到的信息及数据分析结果，通过平台向本人展示，用于本人了解自身信用状况、进行风险评估等合法合规用途。
    </p>
    <p class="text-indent-2">
      本人知晓并同意，本授权是提供服务所必需。本授权自本人签署之日（即点击“同意”按钮之日）起生效，至本人注销平台账户之日止。本人已仔细阅读并完全理解本授权书的全部内容。
    </p>

    <!-- 电子存档声明 -->
    <p class="text-indent-2 font-semibold text-gray-700">
      本人确认，同意本授权书即视为本人以电子文档方式签署，本授权书将以电子档案形式留存，与纸质授权书具有同等法律效力，可作为处理相关争议的有效依据。
    </p>

    <!-- 签名区域 -->
    <div class="pt-10 space-y-2">
      <p>授权人：<span class="font-serif underline px-4">{{ name || '（待传入）' }}</span></p>
      <p>日期：<span class="font-serif underline px-4">{{ currentDate }}</span></p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, default: '' },
  idCard: { type: String, default: '' }
})

const companyName = computed(() => useRuntimeConfig().public.NUXT_Company_Name || '贵公司')

const currentDate = computed(() => {
  const date = new Date();
  const year = date.getFullYear();
  const month = date.getMonth() + 1;
  const day = date.getDate();
  return `${year}年${month}月${day}日`;
})
</script>

<style scoped>
.text-indent-2 {
  text-indent: 2em;
}
.font-songti {
  font-family: 'Songti SC', 'SimSun', serif; /* 衬线字体，更像正式文件 */
}
</style> 
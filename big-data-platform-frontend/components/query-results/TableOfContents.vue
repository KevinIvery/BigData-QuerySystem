<template>
  <nav class="bg-white shadow-sm border-b sticky top-16 z-10">
    <div class="max-w-2xl mx-auto px-4 py-3">
      <div class="flex space-x-1 overflow-x-auto scrollbar-hide">
        <button
          v-for="item in menuItems"
          :key="item.id"
          @click="scrollToSection(item.id)"
          :class="[
            'flex items-center flex-shrink-0 px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 whitespace-nowrap',
            activeSection === item.id
              ? 'bg-blue-500 text-white shadow-md'
              : 'text-gray-600 hover:text-gray-800 hover:bg-gray-100'
          ]"
        >
          <Icon :name="item.icon" class="w-4 h-4 mr-2" />
          {{ item.title }}
        </button>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  menuItems: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['section-change'])

const activeSection = ref('')

// 滚动到指定区域
const scrollToSection = (sectionId) => {
  const element = document.getElementById(sectionId)
  if (element) {
    element.scrollIntoView({ 
      behavior: 'smooth', 
      block: 'start' 
    })
    activeSection.value = sectionId
    emit('section-change', sectionId)
  }
}

// 监听滚动，自动更新活动区域
const handleScroll = () => {
  const sections = props.menuItems.map(item => ({
    id: item.id,
    element: document.getElementById(item.id)
  })).filter(section => section.element)

  if (sections.length === 0) return

  const scrollTop = window.pageYOffset || document.documentElement.scrollTop
  const windowHeight = window.innerHeight

  // 找到当前可见的区域
  let currentSection = sections[0].id
  for (const section of sections) {
    const rect = section.element.getBoundingClientRect()
    if (rect.top <= windowHeight * 0.3) {
      currentSection = section.id
    }
  }

  if (activeSection.value !== currentSection) {
    activeSection.value = currentSection
    emit('section-change', currentSection)
  }
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll, { passive: true })
  // 初始化活动区域
  if (props.menuItems.length > 0) {
    activeSection.value = props.menuItems[0].id
  }
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
.scrollbar-hide {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
.scrollbar-hide::-webkit-scrollbar {
  display: none;
}
</style> 
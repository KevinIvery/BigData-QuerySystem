// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  ssr: false,
  modules: ['@nuxtjs/tailwindcss', '@nuxt/image', '@nuxt/icon'],
  debug: true,
  app: {
    head: {
      meta: [
        { name: 'viewport', content: 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/logo.ico' },
        { rel: 'apple-touch-icon', href: '/logo.ico' }
      ],
      script: [
        { src: 'https://gw.alipayobjects.com/as/g/h5-lib/alipayjsapi/3.1.1/alipayjsapi.inc.min.js' },
      ]
    }
  },
  runtimeConfig: {
    public: {
      apiBase: '/api',  // 后端API前缀
      fileUrl: process.env.NUXT_FILE_URL,
      AgentsUSL: process.env.NUXT_Agents_USL,
      NUXT_Company_Name: process.env.NUXT_Company_Name
    }
  },
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  vite: {
    esbuild: {
      drop: ['console', 'debugger'] // 移除所有 console.log 和 debugger
    }
  },
  // 使用nitro的devProxy配置开发环境代理
  nitro: {
    devProxy: {
      // 开发环境：将客户端发起的 /api/* 请求转发到本地Django服务
      '/api/': {
        target: process.env.NUXT_PUBLIC_API_BASE_URL, // 本地Django开发服务器
        changeOrigin: true,
      },
    },
    routeRules: {
      // 生产环境：将 /api/** 请求代理到生产API服务器
      '/api/**': {
        proxy: {
          to: process.env.NUXT_PUBLIC_API_BASE_URL + '/**'
        }
      }
    }
  }
})

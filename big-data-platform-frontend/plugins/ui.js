import { defineNuxtPlugin } from '#app'
import { createApp } from 'vue'

export default defineNuxtPlugin((nuxtApp) => {
  // 全局UI工具
  const ui = {
    // Toast实例管理
    _toastInstances: [],

    /**
     * 显示全局提示消息
     * @param {Object} options - 提示选项
     * @param {string} options.message - 提示内容
     * @param {string} [options.type='info'] - 提示类型: info, success, warning, error
     * @param {string} [options.description] - 提示描述
     * @param {number} [options.duration=3000] - 自动关闭时间(毫秒)
     * @param {Function} [options.onClose] - 关闭回调
     */
    toast(options) {
      // 客户端执行
      if (process.client) {
        if (typeof options === 'string') {
          options = { message: options }
        }
        
        // 动态导入Toast组件
        import('~/components/Toast.vue').then((module) => {
          const Toast = module.default
          
          // 创建容器并挂载组件
          const container = document.createElement('div')
          document.body.appendChild(container)
          
          const app = createApp(Toast, {
            visible: true,
            type: options.type || 'info',
            message: options.message,
            description: options.description || '',
            duration: options.duration || 3000,
            onClose: () => {
              // 执行用户回调
              if (options.onClose) {
                options.onClose()
              }
              
              // 清理DOM - 等待过渡动画完成(200ms)
              setTimeout(() => {
                if (container && container.parentNode) {
                  app.unmount()
                  container.parentNode.removeChild(container)
                }
                // 从实例列表中移除
                const index = this._toastInstances.findIndex(inst => inst.container === container)
                if (index > -1) {
                  this._toastInstances.splice(index, 1)
                }
              }, 0)
            }
          })
          
          app.mount(container)
          
          // 添加到实例列表
          this._toastInstances.push({ app, container })
          
          // 自动关闭 - 不需要手动触发，组件内部会处理
        }).catch(err => {
          console.error('加载Toast组件出错:', err)
        })
      }
    },

    /**
     * 成功提示
     * @param {string|Object} message - 提示消息或选项对象
     */
    success(message, description = '') {
      const options = typeof message === 'string' 
        ? { message, description, type: 'success' } 
        : { ...message, type: 'success' }
      
      return this.toast(options)
    },

    /**
     * 错误提示
     * @param {string|Object} message - 提示消息或选项对象
     */
    error(message, description = '') {
      const options = typeof message === 'string' 
        ? { message, description, type: 'error' } 
        : { ...message, type: 'error' }
      
      return this.toast(options)
    },

    /**
     * 警告提示
     * @param {string|Object} message - 提示消息或选项对象
     */
    warning(message, description = '') {
      const options = typeof message === 'string' 
        ? { message, description, type: 'warning' } 
        : { ...message, type: 'warning' }
      
      return this.toast(options)
    },
    
    /**
     * 信息提示
     * @param {string|Object} message - 提示消息或选项对象
     */
    info(message, description = '') {
      const options = typeof message === 'string' 
        ? { message, description, type: 'info' } 
        : { ...message, type: 'info' }
      
      return this.toast(options)
    },

    // 加载提示管理
    _loadingInstance: null,

    /**
     * 显示加载提示
     * @param {Object|string} options - 加载选项或加载文本
     */
    showLoading(options = {}) {
      if (process.client) {
        // 关闭现有实例
        this.hideLoading()

        // 如果是字符串，转换为对象
        if (typeof options === 'string') {
          options = { text: options }
        }

        // 导入组件并创建
        import('~/components/Loading.vue').then((module) => {
          const Loading = module.default
          
          // 创建容器并挂载组件
          const container = document.createElement('div')
          document.body.appendChild(container)
          
          const app = createApp(Loading, {
            visible: true,
            text: options.text || '加载中...',
            closeable: options.closeable || false
          })
          
          app.mount(container)
          this._loadingInstance = { app, container }
        }).catch(err => {
          console.error('加载Loading组件出错:', err)
        })
      }
    },

    /**
     * 隐藏加载提示
     */
    hideLoading() {
      if (process.client && this._loadingInstance) {
        const { app, container } = this._loadingInstance
        
        if (container && container.parentNode) {
          app.unmount()
          container.parentNode.removeChild(container)
        }
        this._loadingInstance = null
      }
    }
  }

  // 提供给全局使用
  nuxtApp.provide('ui', ui)
}) 
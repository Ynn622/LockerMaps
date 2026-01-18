import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'node:url'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite';

// https://vite.dev/config/
export default defineConfig({
  base: '/',
  plugins: [vue(), tailwindcss()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  build: {
    // 優化構建性能
    target: 'es2015',
    minify: 'esbuild', // 使用 esbuild 加速壓縮
    cssMinify: 'esbuild',
    reportCompressedSize: false, // 禁用壓縮大小報告以加速構建
    rollupOptions: {
      output: {
        // 手動分塊以改善加載性能
        manualChunks: {
          'mapbox': ['mapbox-gl'],
          'vue-vendor': ['vue', 'vue-router'],
          'utils': ['@vueuse/core', 'gsap']
        }
      }
    },
    // 增加塊大小限制警告閾值
    chunkSizeWarningLimit: 1000
  },
  // 優化依賴預構建
  optimizeDeps: {
    include: ['vue', 'vue-router', 'mapbox-gl', '@vueuse/core', 'gsap']
  }
})

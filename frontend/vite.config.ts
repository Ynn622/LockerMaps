import { defineConfig } from 'vite'
import { fileURLToPath, URL } from 'node:url'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite';

const now = new Date();
const pad2 = (n: number) => String(n).padStart(2, '0');
const APP_VERSION = `${now.getUTCFullYear()}.${pad2(now.getUTCMonth() + 1)}.${pad2(now.getUTCDate())}-${Math.floor(now.getTime() / 1000)}`;
const BUILD_TIME = now.toISOString();

// https://vite.dev/config/
export default defineConfig({
  base: '/',
  define: {
    'import.meta.env.VITE_APP_VERSION': JSON.stringify(APP_VERSION)
  },
  plugins: [
    vue(),
    tailwindcss(),
    {
      name: 'emit-version-json',
      generateBundle() {
        this.emitFile({
          type: 'asset',
          fileName: 'version.json',
          source: JSON.stringify(
            {
              version: APP_VERSION,
              buildTime: BUILD_TIME
            },
            null,
            2
          )
        });
      }
    }
  ],
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
  },
})

import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'

// 医生工作台前端原型
// - 默认走内置 mock 数据层（VITE_API_MODE=mock，开箱即用）
// - VITE_API_MODE=real 时，/api 代理到 Runtime API Service（08_API_Service）
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const apiTarget = env.VITE_API_TARGET || 'http://127.0.0.1:8000'
  return {
    plugins: [vue()],
    server: {
      port: 5173,
      proxy: {
        '/api': {
          target: apiTarget,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        },
      },
    },
  }
})

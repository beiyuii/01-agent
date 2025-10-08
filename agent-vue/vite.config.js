import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

// https://vite.dev/config/
export default defineConfig({
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  plugins: [vue()],
  server: {
    proxy: {
      '/resume': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/match': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})

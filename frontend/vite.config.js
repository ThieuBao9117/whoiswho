import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    },
    // Thêm dòng này để cho phép host ngrok
    allowedHosts: [
      '8bd1-171-248-204-168.ngrok-free.app',  // host cụ thể của bạn
      '.ngrok-free.app'                       // hoặc cho phép mọi subdomain ngrok
    ]
  }
})
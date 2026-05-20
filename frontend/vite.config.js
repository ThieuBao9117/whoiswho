import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/game/',
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:7000',
        changeOrigin: true,
      }
    },
    allowedHosts: [
      '8bd1-171-248-204-168.ngrok-free.app',
      '.ngrok-free.app'
    ]
  }
})
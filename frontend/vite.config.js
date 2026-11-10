import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// /api 轉到後端 Flask :5001
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { '/api': 'http://localhost:5001' },
  },
  test: { environment: 'jsdom' },
})

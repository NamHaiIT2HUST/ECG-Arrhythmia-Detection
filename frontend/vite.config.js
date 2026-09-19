import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Frontend giờ gọi API/WS bằng đường dẫn tương đối (xem src/utils/serverUrl.js) thay vì
    // hardcode "localhost:8000" - khi chạy qua Nginx (production) nginx.conf lo việc proxy
    // /api, /ws sang backend; lúc `npm run dev` (Vite tự phục vụ, không qua Nginx) cần proxy
    // tương đương ở đây để dev local vẫn hoạt động đúng như production.
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/ws': { target: 'ws://localhost:8000', ws: true },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
  },
})

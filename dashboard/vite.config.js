import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Load environment variables
const API_HOST = process.env.VITE_API_HOST || 'localhost';
const API_PORT = process.env.VITE_API_PORT || '8000';
const API_URL = `http://${API_HOST}:${API_PORT}`;
const WS_URL = `ws://${API_HOST}:${API_PORT}`;

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: API_URL,
        changeOrigin: true,
      },
      '/ws': {
        target: WS_URL,
        ws: true,
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true
  }
})
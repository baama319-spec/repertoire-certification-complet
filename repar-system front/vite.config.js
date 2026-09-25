import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    watch: {
      // Le polling évite les erreurs ENOSPC lorsque la limite inotify est basse.
      usePolling: true,
      interval: 300,
    },
    proxy: {
      // L'API ReparSystem locale écoute sur le port 8001.
      // Garder ce proxy évite les erreurs CORS pendant le développement.
      '/api': 'http://127.0.0.1:8001',
      '/media': 'http://127.0.0.1:8001'
    }
  }
})

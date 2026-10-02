import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'
import './styles/admin-clients-table.css'
import './styles/admin-page-headers.css'
import './styles/branding.css'

createApp(App).use(router).mount('#app')

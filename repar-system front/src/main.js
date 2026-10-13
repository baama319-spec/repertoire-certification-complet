import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import AppIcon from './components/commun/AppIcon.vue'
import './style.css'
import './styles/admin-clients-table.css'
import './styles/admin-page-headers.css'
import './styles/branding.css'
import './styles/design-system.css'

createApp(App).component('AppIcon', AppIcon).use(router).mount('#app')

import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// Import Font Awesome
import '@fortawesome/fontawesome-free/css/all.css'

// Disable Vue DevTools in production
if (import.meta.env.PROD) {
  window.__VUE_DEVTOOLS_GLOBAL_HOOK__ = undefined
}

const app = createApp(App)

// Disable Vue DevTools completely
app.config.devtools = false

app.use(router).mount('#app')

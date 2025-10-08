import { createApp } from 'vue'
import { createPinia } from 'pinia'
import naive from 'naive-ui'

import App from '@/App.vue'
import router from '@/router'
import i18n from '@/i18n'

import '@/styles/base.css'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(i18n)
app.use(naive)

app.mount('#app')

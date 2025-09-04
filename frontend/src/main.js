import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // Importamos nuestro enrutador

const app = createApp(App)

app.use(router) // Le decimos a la app que use el enrutador

app.mount('#app')
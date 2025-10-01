// frontend/src/main.js

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import { supabase } from './supabase';
import { useAppStore } from './stores/appStore';

// Estilos de Vuetify
import 'vuetify/styles';
// --- LÍNEA CORREGIDA ---
// Importa la fuente de íconos Material Design Icons
import '@mdi/font/css/materialdesignicons.css'; 
// --- FIN DE LA CORRECCIÓN ---
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';

const vuetify = createVuetify({ components, directives });
const app = createApp(App);
app.use(createPinia());

async function initializeApp() {
  const appStore = useAppStore();
  
  supabase.auth.onAuthStateChange((event, session) => {
    appStore.setSession(session);
  });
  
  const { data: { session } } = await supabase.auth.getSession();
  await appStore.initialize(session);

  app.use(router);
  app.use(vuetify);
  app.mount('#app');
}

initializeApp();
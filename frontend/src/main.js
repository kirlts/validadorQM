// frontend/src/main.js

import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './App.vue';
import router from './router';
import { supabase } from './supabase';
import { useAuthStore } from './stores/authStore';

// Vuetify
import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import '@mdi/font/css/materialdesignicons.css';

const vuetify = createVuetify({ components, directives });

const app = createApp(App);
app.use(createPinia());

// Función de inicialización asíncrona
async function initializeApp() {
  const authStore = useAuthStore();

  // Espera a que Supabase verifique la sesión inicial
  const { data: { session } } = await supabase.auth.getSession();
  await authStore.initialize(session);

  // El listener de onAuthStateChange maneja los cambios POSTERIORES (login/logout)
  supabase.auth.onAuthStateChange((event, session) => {
    authStore.setSession(session);
  });
  
  // Ahora que la autenticación está lista, usamos el router y montamos la app
  app.use(router);
  app.use(vuetify);
  app.mount('#app');
}

initializeApp();
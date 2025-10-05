// frontend/src/main.js

import { createApp } from 'vue';
import { createPinia } from 'pinia';

import App from './App.vue';
import router from './router';

// Import Vuetify
import 'vuetify/styles';
import { createVuetify } from 'vuetify';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import '@mdi/font/css/materialdesignicons.css';

// Create the app instance
const app = createApp(App);

// Create and use Pinia for state management
const pinia = createPinia();
app.use(pinia);

// Create and use Vuetify for UI components
const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
  },
});
app.use(vuetify);

// Use the router for navigation
app.use(router);

// Mount the app to the DOM
app.mount('#app');
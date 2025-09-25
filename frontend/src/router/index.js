// frontend/src/router/index.js

import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '@/stores/authStore';
import WelcomeView from '../views/WelcomeView.vue';
import DashboardView from '../views/DashboardView.vue';
import DetailView from '../views/DetailView.vue';
import DefaultLayout from '../layouts/DefaultLayout.vue';

const routes = [
  { path: '/', name: 'welcome', component: WelcomeView, meta: { requiresAuth: false } },
  {
    path: '/app', component: DefaultLayout, meta: { requiresAuth: true }, children: [
      { path: '', redirect: { name: 'dashboard' } },
      { path: 'dashboard', name: 'dashboard', component: DashboardView },
      { path: 'di/:id', name: 'detail', component: DetailView, props: true }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/' }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

// Guardia de navegación
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore();
  
  // Espera a que la inicialización en main.js termine
  if (!authStore.isAuthReady) {
    await new Promise(resolve => {
      const unsubscribe = authStore.$subscribe((mutation, state) => {
        if (state.isAuthReady) {
          unsubscribe();
          resolve();
        }
      });
    });
  }

  const isLoggedIn = authStore.isLoggedIn;
  if (to.meta.requiresAuth && !isLoggedIn) {
    next({ name: 'welcome' });
  } else if (to.name === 'welcome' && isLoggedIn) {
    next({ name: 'dashboard' });
  } else {
    next();
  }
});

export default router;
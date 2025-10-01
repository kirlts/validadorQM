// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import { useAppStore } from '@/stores/appStore';

const routes = [
  { path: '/', name: 'welcome', component: () => import('@/views/WelcomeView.vue'), meta: { requiresAuth: false } },
  {
    path: '/app', component: () => import('@/layouts/DefaultLayout.vue'), meta: { requiresAuth: true }, children: [
      { path: '', redirect: { name: 'dashboard' } },
      { path: 'dashboard', name: 'dashboard', component: () => import('@/views/DashboardView.vue') },
      { path: 'di/:id', name: 'detail', component: () => import('@/views/DetailView.vue'), props: true }
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/' }
];
const router = createRouter({ history: createWebHistory(import.meta.env.BASE_URL), routes });

router.beforeEach(async (to, from, next) => {
  const appStore = useAppStore();
  if (!appStore.isAuthReady) {
    await new Promise(resolve => {
      const unsubscribe = appStore.$subscribe((mutation, state) => {
        if (state.isAuthReady) {
          unsubscribe();
          resolve();
        }
      });
    });
  }
  const isLoggedIn = appStore.isLoggedIn;
  if (to.meta.requiresAuth && !isLoggedIn) {
    next({ name: 'welcome' });
  } else if (to.name === 'welcome' && isLoggedIn) {
    next({ name: 'dashboard' });
  } else {
    next();
  }
});
export default router;
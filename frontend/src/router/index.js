import { createRouter, createWebHistory } from 'vue-router'
import WelcomeView from '../views/WelcomeView.vue'
import DashboardView from '../views/DashboardView.vue'
import DetailView from '../views/DetailView.vue'
// 1. Importamos el nuevo layout
import DefaultLayout from '../layouts/DefaultLayout.vue'
import { supabase } from '@/supabase'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'welcome',
      component: WelcomeView
    },
    // 2. Creamos una nueva ruta "padre" para las vistas protegidas
    {
      path: '/app',
      component: DefaultLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          name: 'dashboard',
          component: DashboardView,
        },
        {
          path: 'di/:id',
          name: 'detail',
          component: DetailView,
          props: true,
        }
      ]
    }
  ]
})

router.beforeEach(async (to, from, next) => {
  const { data: { session } } = await supabase.auth.getSession();
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);

  if (requiresAuth && !session) {
    next('/');
  } 
  // 3. Actualizamos la redirección para que apunte a la nueva ruta del dashboard
  else if (to.name === 'welcome' && session) {
    next('/app/dashboard');
  } 
  else {
    next();
  }
});

export default router
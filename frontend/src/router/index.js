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
    // Si la ruta es protegida y NO hay sesión, se va a la bienvenida.
    next({ name: 'welcome' });
  } else if (!requiresAuth && session && to.name === 'welcome') {
    // Si la ruta NO es protegida (bienvenida) y SÍ hay sesión, se va al dashboard.
    next({ name: 'dashboard' });
  } else {
    // En todos los demás casos, permite la navegación.
    next();
  }
});

export default router;
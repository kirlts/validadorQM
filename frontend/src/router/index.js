// frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import { useAppStore } from '@/stores/appStore';
import DefaultLayout from '@/layouts/DefaultLayout.vue'; // Importa el layout si lo usarás explícitamente

const routes = [
  { 
    path: '/', 
    name: 'welcome', 
    component: () => import('@/views/WelcomeView.vue'), 
    meta: { requiresAuth: false } 
  },
  {
    path: '/app', 
    component: DefaultLayout, // Usamos el layout como componente contenedor
    meta: { requiresAuth: true }, 
    children: [
      { 
        path: '', 
        redirect: { name: 'dashboard' } 
      },
      { 
        path: 'dashboard', 
        name: 'dashboard', 
        component: () => import('@/views/DashboardView.vue') 
      },
      { 
        path: 'di/:id', 
        name: 'detail', 
        component: () => import('@/views/DetailView.vue'), 
        props: true 
      },
      // --- NUEVA RUTA DE ADMINISTRACIÓN ---
      {
        path: '/admin',
        name: 'admin',
        component: () => import('@/views/AdminView.vue'),
        meta: { layout: DefaultLayout, requiresAuth: true },
        beforeEnter: (to, from, next) => {
          const appStore = useAppStore();
          
          if (appStore.isAuthReady) {
            if (appStore.isAdmin) {
              next(); // Permitir acceso
            } else {
              next({ name: 'dashboard' }); // Redirigir
            }
          } else if (!appStore.user) {
            // Manejar el caso donde la autenticación aún no se ha verificado
            next({ name: 'welcome' });
          }
        }
      }
    ]
  },
  { 
    path: '/:pathMatch(.*)*', 
    redirect: '/' 
  }
];

const router = createRouter({ 
  history: createWebHistory(import.meta.env.BASE_URL), 
  routes 
});

// La guarda de navegación global se mantiene para manejar la autenticación general.
router.beforeEach(async (to, from, next) => {
  const appStore = useAppStore();
  
  // Esperar a que el estado de autenticación se resuelva si aún no lo ha hecho.
  // Esto es crucial para que `isLoggedIn` y los datos del usuario estén disponibles.
  if (!appStore.isAuthReady) {
    await new Promise(resolve => {
      // Nos suscribimos a cambios en el store. Cuando isAuthReady cambie a true, continuamos.
      const unsubscribe = appStore.$subscribe((mutation, state) => {
        if (state.isAuthReady) {
          unsubscribe();
          resolve();
        }
      });
      // Si el store ya se inicializó mientras se creaba la promesa, resolvemos de inmediato.
      if (appStore.isAuthReady) {
          unsubscribe();
          resolve();
      }
    });
  }

  const isLoggedIn = appStore.isLoggedIn;

  if (to.meta.requiresAuth && !isLoggedIn) {
    // Si la ruta requiere autenticación y el usuario no ha iniciado sesión, redirigir a welcome.
    next({ name: 'welcome' });
  } else if (to.name === 'welcome' && isLoggedIn) {
    // Si el usuario ya inició sesión e intenta ir a la página de bienvenida, redirigir al dashboard.
    next({ name: 'dashboard' });
  } else {
    // En todos los demás casos, permitir la navegación.
    next();
  }
});

export default router;
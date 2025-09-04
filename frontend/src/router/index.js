import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import DashboardView from '../views/DashboardView.vue'
import DetailView from '../views/DetailView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login' // Redirigir la raíz a la página de login
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: DashboardView
    },
    {
      // Ruta dinámica para mostrar el detalle de un DI específico
      path: '/di/:id',
      name: 'detail',
      component: DetailView,
      props: true // Permite pasar el 'id' de la URL como prop al componente
    }
  ]
})

export default router
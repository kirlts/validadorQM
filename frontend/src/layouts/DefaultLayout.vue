// frontend/src/layouts/DefaultLayout.vue

<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-toolbar-title class="font-weight-bold">
        Validador QM
      </v-toolbar-title>
      
      <v-spacer></v-spacer>
      
      <v-btn v-if="appStore.user" icon @click="handleLogout" title="Cerrar Sesión">
        <v-icon>mdi-logout</v-icon>
      </v-btn>
    </v-app-bar>

    <v-main class="bg-grey-lighten-3">
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import { useAppStore } from '@/stores/appStore';

const appStore = useAppStore();

const handleLogout = () => {
  appStore.signOut();
};
</script>

<style scoped>
/* Puedes añadir estilos específicos para el layout si lo necesitas */
</style>
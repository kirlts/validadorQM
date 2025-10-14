<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-toolbar-title class="cursor-pointer" @click="goHome">
        Validador QM
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn v-if="isLoggedIn" :to="{ name: 'dashboard' }" prepend-icon="mdi-view-dashboard" variant="tonal">
        Dashboard
      </v-btn>
      <v-btn v-if="isAdmin" :to="{ name: 'admin' }" prepend-icon="mdi-shield-crown" variant="tonal" class="ml-2">
        Admin Panel
      </v-btn>

      <v-btn v-if="isLoggedIn" @click="handleSignOut" :loading="isLoading" class="ml-4">
        Cerrar Sesión
      </v-btn>
    </v-app-bar>

    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useAppStore } from '@/stores/appStore';
import { storeToRefs } from 'pinia';

const router = useRouter();
const appStore = useAppStore();

const { isLoggedIn, isLoading, isAdmin } = storeToRefs(appStore);

const handleSignOut = async () => {
  await appStore.signOut();
  router.push({ name: 'welcome' });
};

// La lógica de goHome ahora es más simple y robusta.
const goHome = () => {
  if (isLoggedIn.value) {
    router.push({ name: 'dashboard' });
  } else {
    router.push({ name: 'welcome' });
  }
};
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}
/* Este estilo se aplicará correctamente ahora */
.v-btn--active {
  background-color: rgba(255, 255, 255, 0.2) !important;
}
</style>
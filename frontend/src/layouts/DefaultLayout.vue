<template>
  <v-app>
    <v-app-bar app color="primary" dark>
      <v-toolbar-title>Validador QM</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn @click="handleLogout" text>
        <v-icon left>mdi-logout</v-icon>
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
import { supabase } from '@/supabase';

const router = useRouter();

async function handleLogout() {
  try {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    // Redirige al usuario a la página de bienvenida/login después de cerrar sesión
    router.push('/');
  } catch (error) {
    console.error('Error al cerrar sesión:', error.message);
  }
}
</script>

<style scoped>
/* Puedes añadir estilos específicos para el layout si es necesario */
</style>
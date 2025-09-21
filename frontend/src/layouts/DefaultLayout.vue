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
import { useDiStore } from '@/stores/diStore';

const router = useRouter();
const diStore = useDiStore();

async function handleLogout() {
  try {
    const { error } = await supabase.auth.signOut();
    if (error) throw error;
    
    // ANTES de redirigir, limpiamos los datos del store
    diStore.clearDesigns(); 

    router.push('/');
  } catch (error) {
    console.error('Error al cerrar sesión:', error.message);
  }
}
</script>

<style scoped>
/* Puedes añadir estilos específicos para el layout si es necesario */
</style>
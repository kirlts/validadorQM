// frontend/src/components/LoginCard.vue
<template>
  <v-card class="mx-auto pa-4" max-width="400" elevation="8">
    <v-card-title class="text-center text-h5">Bienvenido</v-card-title>
    <v-card-text>
      <v-form @submit.prevent="handleLogin">
        <v-text-field v-model="email" label="Email" type="email" required variant="outlined"></v-text-field>
        <v-text-field v-model="password" label="Contraseña" type="password" required variant="outlined" class="mt-2"></v-text-field>
        <v-alert v-if="errorMessage" type="error" dense class="mt-4">{{ errorMessage }}</v-alert>
        <v-btn :loading="loading" type="submit" block color="primary" class="mt-4">Iniciar Sesión</v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from 'vue';
// ¡Importamos supabase directamente!
import { supabase } from '@/supabase'; 
// Seguimos usando el store, pero no para la acción de login.
import { useAppStore } from '@/stores/appStore';

const email = ref('');
const password = ref('');
const loading = ref(false);
const errorMessage = ref('');
const appStore = useAppStore(); // El store sigue siendo útil para acceder al estado si fuera necesario.

const handleLogin = async () => {
  loading.value = true;
  errorMessage.value = '';
  try {
    // --- CAMBIO CLAVE ---
    // Llamamos directamente a la función de Supabase para iniciar sesión.
    const { error } = await supabase.auth.signInWithPassword({
      email: email.value,
      password: password.value,
    });
    
    // Si Supabase devuelve un error, lo mostramos.
    if (error) throw error;

    // Si el login es exitoso, el listener `onAuthStateChange` en appStore.js
    // se activará automáticamente y se encargará de redirigir al dashboard.
    // No necesitamos hacer nada más aquí.

  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    loading.value = false;
  }
};
</script>
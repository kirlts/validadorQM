// frontend/src/components/LoginCard.vue
<template>
  <v-card class="mx-auto pa-4" max-width="400" elevation="8">
    <v-card-title class="text-center text-h5">Bienvenido</v-card-title>
    <v-card-text>
      <v-form @submit.prevent="handleLogin">
        <v-text-field v-model="email" label="Email" type="email" required></v-text-field>
        <v-text-field v-model="password" label="Contraseña" type="password" required></v-text-field>
        <v-alert v-if="errorMessage" type="error" dense>{{ errorMessage }}</v-alert>
        <v-btn :loading="loading" type="submit" block color="primary" class="mt-4">Iniciar Sesión</v-btn>
      </v-form>
    </v-card-text>
  </v-card>
</template>

<script setup>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/authStore';

const email = ref('');
const password = ref('');
const loading = ref(false);
const errorMessage = ref('');
const authStore = useAuthStore();

const handleLogin = async () => {
  loading.value = true;
  errorMessage.value = '';
  try {
    await authStore.signIn({ email: email.value, password: password.value });
    // La redirección es manejada por el listener en setSession del authStore
  } catch (error) {
    errorMessage.value = error.message;
  } finally {
    loading.value = false;
  }
};
</script>
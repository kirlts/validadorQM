<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Inicio de Sesión</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <v-form @submit.prevent="handleLogin">
              <v-text-field
                label="Email"
                name="login"
                prepend-icon="mdi-account"
                type="text"
                v-model="email"
                required
              ></v-text-field>
              <v-text-field
                id="password"
                label="Contraseña"
                name="password"
                prepend-icon="mdi-lock"
                type="password"
                v-model="password"
                required
              ></v-text-field>
              <v-alert
                v-if="errorMessage"
                type="error"
                density="compact"
                class="mb-4"
              >
                {{ errorMessage }}
              </v-alert>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn 
              color="primary" 
              @click="handleLogin"
              :loading="loading"
              :disabled="loading"
            >
              Ingresar
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
// 3. Importamos nuestro cliente de Supabase
import { supabase } from '@/supabase';

const email = ref('');
const password = ref('');
// 4. Actualizamos las variables de estado para manejar carga y errores
const loading = ref(false);
const errorMessage = ref(null);
const router = useRouter();

// 5. La función de login ahora es asíncrona y se comunica con Supabase
async function handleLogin() {
  if (!email.value || !password.value) {
    errorMessage.value = 'Email y contraseña no pueden estar vacíos.';
    return;
  }

  try {
    loading.value = true;
    errorMessage.value = null;

    // Realizamos la llamada a Supabase para iniciar sesión
    const { data, error } = await supabase.auth.signInWithPassword({
      email: email.value,
      password: password.value,
    });

    if (error) throw error;

    // Si el login es exitoso, la librería de Supabase guarda la sesión automáticamente.
    // Solo necesitamos redirigir al usuario.
    router.push('/dashboard');

  } catch (error) {
    errorMessage.value = 'Credenciales inválidas. Por favor, intente de nuevo.';
    console.error('Error de autenticación:', error.message);
  } finally {
    loading.value = false;
  }
}
</script>
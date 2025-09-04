<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="4">
        <v-card class="elevation-12">
          <v-toolbar color="primary" dark flat>
            <v-toolbar-title>Inicio de Sesión</v-toolbar-title>
          </v-toolbar>
          <v-card-text>
            <v-form>
              <v-text-field
                label="Email"
                name="login"
                prepend-icon="mdi-account"
                type="text"
                v-model="email"
              ></v-text-field>
              <v-text-field
                id="password"
                label="Contraseña"
                name="password"
                prepend-icon="mdi-lock"
                type="password"
                v-model="password"
              ></v-text-field>
              <v-alert
                v-if="error"
                type="error"
                density="compact"
                class="mb-4"
              >
                Email y contraseña no pueden estar vacíos.
              </v-alert>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" @click="handleLogin">Ingresar</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const email = ref('');
const password = ref('');
const error = ref(false);
const router = useRouter();

function handleLogin() {
  if (email.value && password.value) {
    error.value = false;
    // En una aplicación real, aquí se guardaría el token JWT
    router.push('/dashboard');
  } else {
    error.value = true;
  }
}
</script>
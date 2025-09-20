<template>
  <v-container class="fill-height" fluid>
    <v-row align="center" justify="center">
      <v-col cols="12" sm="8" md="6" lg="4">
        <div class="text-center mb-6">
          <h1 class="text-h4 font-weight-bold">Validador QM con IA</h1>
          <p class="text-subtitle-1 grey--text text--darken-1">
            Una herramienta para asegurar la calidad de tus Diseños Instruccionales.
          </p>
        </div>
        <LoginCard />
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import LoginCard from '@/components/LoginCard.vue';
</script>
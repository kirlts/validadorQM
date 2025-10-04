// frontend/src/App.vue
<template>
  <router-view v-if="appStore.isAuthReady" />
  <v-container v-else fluid class="fill-height d-flex justify-center align-center">
    <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
  </v-container>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAppStore } from '@/stores/appStore';
const appStore = useAppStore();

// Llama a la inicialización cuando el componente se monta por primera vez.
onMounted(() => {
  appStore.initialize();
});
</script>
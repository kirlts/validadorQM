<template>
  <router-view />
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { supabase } from './supabase';

const router = useRouter();

onMounted(() => {
  supabase.auth.onAuthStateChange((event, session) => {
    const currentRoute = router.currentRoute.value;

    if (event === 'SIGNED_IN' && currentRoute.name !== 'dashboard') {
      console.log('SIGNED_IN detectado, navegando a dashboard...');
      router.push({ name: 'dashboard' });
    } else if (event === 'SIGNED_OUT' && currentRoute.name !== 'welcome') {
      console.log('SIGNED_OUT detectado, navegando a welcome...');
      router.push({ name: 'welcome' });
    }
  });
});
</script>
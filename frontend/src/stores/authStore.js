// frontend/src/stores/authStore.js

import { defineStore } from 'pinia';
import { supabase } from '@/supabase';
import { useDiStore } from './diStore';
import router from '@/router';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    isAuthReady: false, // Para que el router espere
  }),
  getters: {
    isLoggedIn: (state) => !!state.user,
  },
  actions: {
    // Se llama una sola vez al arrancar la app
    async initialize(session) {
      this.user = session?.user ?? null;
      this.isAuthReady = true;
      if (this.user) {
        const diStore = useDiStore();
        await diStore.fetchDesigns();
        diStore.subscribeToChanges();
      }
    },
    // Se llama cuando onAuthStateChange detecta un cambio
    async setSession(session) {
      this.user = session?.user ?? null;
      const diStore = useDiStore();

      if (this.user) {
        if (!diStore.realtimeChannel) {
          await diStore.fetchDesigns();
          diStore.subscribeToChanges();
        }
        if (router.currentRoute.value.name === 'welcome') {
          router.push({ name: 'dashboard' });
        }
      } else {
        diStore.unsubscribeAndClear();
        router.push({ name: 'welcome' });
      }
    },

    async signIn(credentials) {
      const { error } = await supabase.auth.signInWithPassword(credentials);
      if (error) throw error;
      // onAuthStateChange se encargará del resto
    },

    async signOut() {
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
      // onAuthStateChange se encargará del resto
    },
  },
});
// frontend/src/stores/appStore.js

import { defineStore } from 'pinia';
import { supabase } from '@/supabase';
import { getDis } from '@/services/apiService';
import router from '@/router';

export const useAppStore = defineStore('app', {
  state: () => ({
    user: null,
    isAuthReady: false,
    designs: [],
    isLoading: false,
    realtimeChannel: null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.user,
  },

  actions: {
    async initialize() {
      this.isLoading = true;
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session) {
          this.user = session.user;
          await this.fetchDesigns();
          this.subscribeToDiChanges();
        }
      } catch (error) {
        console.error("Error en la inicialización:", error);
      } finally {
        this.isAuthReady = true;
        this.isLoading = false;
      }

      supabase.auth.onAuthStateChange((event, session) => {
        const previousUser = this.user;
        this.user = session?.user || null;
        this.isAuthReady = true;
        
        if (!previousUser && this.user) {
          router.push({ name: 'dashboard' });
          this.fetchDesigns();
          this.subscribeToDiChanges();
        } else if (previousUser && !this.user) {
          router.push({ name: 'welcome' });
          this.unsubscribeFromDiChanges();
          this.designs = [];
        }
      });
    },

    async fetchDesigns() {
      this.isLoading = true;
      try {
        this.designs = await getDis();
      } catch (error) {
        console.error("Error al obtener DIs:", error);
      } finally {
        this.isLoading = false;
      }
    },

    // --- ESCUCHANDO BROADCASTS ---
    subscribeToDiChanges() {
      if (this.realtimeChannel) {
        this.unsubscribeFromDiChanges();
      }

      console.log('[Realtime-Broadcast] Sintonizando el canal "di_changes"...');
      
      this.realtimeChannel = supabase.channel('di_changes');
      
      this.realtimeChannel
        .on(
          'broadcast',
          { event: 'di_update' }, // Escuchamos nuestro evento personalizado 'di_update'
          (message) => {
            // El payload real está dentro de message.payload
            const payload = message.payload;
            console.log('[Realtime-Broadcast] Mensaje recibido:', payload);
            
            switch (payload.eventType) {
              case 'INSERT':
                // Añadimos el nuevo DI si no existe ya (para evitar duplicados)
                if (!this.designs.some(d => d.id_di === payload.new.id_di)) {
                    this.designs.unshift(payload.new);
                }
                break;
              case 'UPDATE':
                const index = this.designs.findIndex(d => d.id_di === payload.new.id_di);
                if (index !== -1) {
                  this.designs[index] = { ...this.designs[index], ...payload.new };
                }
                break;
              case 'DELETE':
                this.designs = this.designs.filter(d => d.id_di !== payload.old.id_di);
                break;
            }
          }
        )
        .subscribe((status, err) => {
          if (status === 'SUBSCRIBED') {
            console.log('[Realtime-Broadcast] ¡Conectado y escuchando broadcasts en "di_changes"!');
          }
          if (status === 'CHANNEL_ERROR') {
            console.error('[Realtime-Broadcast] Error en el canal:', err);
          }
        });
    },

    unsubscribeFromDiChanges() {
      if (this.realtimeChannel) {
        console.log('[Realtime-Broadcast] Dando de baja la suscripción.');
        supabase.removeChannel(this.realtimeChannel);
        this.realtimeChannel = null;
      }
    },

    async signOut() {
      this.isLoading = true;
      await supabase.auth.signOut();
      this.isLoading = false;
    },
  },
});
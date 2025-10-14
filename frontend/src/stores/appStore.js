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
      
      console.log('[Realtime-Broadcast] Intentando conectar al canal "di_changes"...');
      this.realtimeChannel = supabase.channel('di_changes');
      
      this.realtimeChannel
        .on(
          'broadcast',
          { event: 'di_update' },
          (message) => {
            const payload = message.payload;
            console.log('[Realtime-Broadcast] Mensaje recibido:', payload);
            
            switch (payload.eventType) {
              case 'INSERT':
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
          // Escuchar todos los cambios de estado del canal ---
          switch (status) {
            case 'SUBSCRIBED':
              console.log('[Realtime-Broadcast] ¡Conectado y escuchando broadcasts en "di_changes"!');
              // Si había un timer de reconexión, lo limpiamos porque ya lo logramos.
              if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
              break;
            
            case 'CHANNEL_ERROR':
              console.error('[Realtime-Broadcast] Error en el canal:', err);
              this.attemptReconnect();
              break;

            case 'TIMED_OUT':
              console.warn('[Realtime-Broadcast] Conexión agotada (TIMED_OUT). Intentando reconectar...');
              this.attemptReconnect();
              break;
            
            case 'CLOSED':
              console.warn('[Realtime-Broadcast] El canal fue cerrado (CLOSED). Podría ser por inactividad. Intentando reconectar...');
              // No reconectamos inmediatamente si el usuario cerró sesión.
              if (this.isLoggedIn) {
                this.attemptReconnect();
              }
              break;
          }
        });
    },
    
    attemptReconnect() {
      // Limpiamos cualquier timer anterior para evitar múltiples intentos.
      if (this.reconnectTimer) clearTimeout(this.reconnectTimer);

      // Programamos un reintento en 5 segundos.
      // Esto evita un bucle infinito de intentos si la red está caída.
      this.reconnectTimer = setTimeout(() => {
        console.log('[Realtime-Broadcast] Ejecutando intento de reconexión...');
        this.subscribeToDiChanges();
      }, 5000);
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
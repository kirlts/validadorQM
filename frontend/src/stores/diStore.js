// frontend/src/stores/diStore.js

import { defineStore } from 'pinia';
import { supabase } from '@/supabase';
import { getDis } from '@/services/apiService';

export const useDiStore = defineStore('di', {
  state: () => ({
    designs: [],
    isLoading: false,
    realtimeChannel: null,
  }),
  actions: {
    async fetchDesigns() {
      this.isLoading = true;
      try {
        this.designs = await getDis();
        console.log('Pinia Store (DI): Lista de DIs actualizada desde la API.');
      } catch (error) {
        console.error('Pinia Store (DI): Error al cargar los DIs:', error);
      } finally {
        this.isLoading = false;
      }
    },
    subscribeToChanges() {
      if (this.realtimeChannel) return;
      console.log('Pinia Store (DI): Suscribiéndose a cambios en la lista de DIs...');
      this.realtimeChannel = supabase
        .channel('disenos_instruccionales_list_changes') // Canal para la lista
        .on(
          'postgres_changes',
          { event: '*', schema: 'public', table: 'disenos_instruccionales' },
          (payload) => {
            console.log('Pinia Store (DI): Cambio detectado en la lista, recargando.', payload);
            this.fetchDesigns(); // Estrategia robusta: recargar la lista completa
          }
        )
        .subscribe();
    },
    unsubscribeAndClear() {
      if (this.realtimeChannel) {
        supabase.removeChannel(this.realtimeChannel);
        this.realtimeChannel = null;
        console.log('Pinia Store (DI): Suscripción a la lista cancelada.');
      }
      this.designs = [];
    }
  }
});
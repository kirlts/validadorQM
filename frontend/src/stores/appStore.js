// frontend/src/stores/appStore.js

import { defineStore } from 'pinia';
import { supabase } from '@/supabase';
import { getDis } from '@/services/apiService';
import router from '@/router';

// Función auxiliar para obtener un solo DI. La necesitamos aquí.
async function fetchSingleDi(diId) {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) throw new Error('No hay sesión de usuario activa.');

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';
    const response = await fetch(`${API_URL}/dis/${diId}`, {
        headers: { 'Authorization': `Bearer ${session.access_token}` },
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || `Error fetching DI ${diId}`);
    }
    return response.json();
}

export const useAppStore = defineStore('app', {
  state: () => ({
    user: null,
    isAuthReady: false,
    designs: [],
    isLoading: false,
    realtimeChannel: null,
    // Guardamos los intervalos de polling para poder detenerlos
    activePollers: new Map(), 
  }),
  getters: {
    isLoggedIn: (state) => !!state.user,
  },
  actions: {
    async initialize(session) {
      this.user = session?.user ?? null;
      if (this.user) {
        await this.fetchDesigns();
        this.subscribeToChanges();
      }
      this.isAuthReady = true;
    },
    setSession(session) {
        this.user = session?.user ?? null;
        if (this.user) {
            if (!this.realtimeChannel) {
                this.fetchDesigns();
                this.subscribeToChanges();
            }
            // Si el usuario está logueado y en la página de bienvenida, redirigir al dashboard.
            if(router.currentRoute.value.name === 'welcome'){
                router.push({ name: 'dashboard' });
            }
        } else {
            this.unsubscribeAndClear();
            // Si el usuario no está logueado, redirigir a la bienvenida.
            router.push({ name: 'welcome' });
        }
    },
    
    // --- FUNCIONES DE AUTENTICACIÓN RESTAURADAS ---
    async signIn(credentials) {
      const { error } = await supabase.auth.signInWithPassword(credentials);
      if (error) throw error;
    },
    async signOut() {
      await this.unsubscribeAndClear();
      const { error } = await supabase.auth.signOut();
      if (error) throw error;
      router.push({ name: 'welcome' }); // Asegurarse de redirigir al salir
    },

    async fetchDesigns() {
      this.isLoading = true;
      try {
        const fetchedDesigns = await getDis();
        this.designs = fetchedDesigns.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      } finally {
        this.isLoading = false;
      }
    },

    // --- LA LÓGICA DE POLLING ---
    startPollingDiStatus(diId, statusKey = 'estado_transformacion') {
        if (this.activePollers.has(diId)) return;

        console.log(`[Polling] Iniciando polling para DI ${diId} en el campo ${statusKey}`);
        
        const intervalId = setInterval(async () => {
            try {
                const updatedDi = await fetchSingleDi(diId);
                const currentState = updatedDi[statusKey];

                if (currentState !== 'processing') {
                    console.log(`[Polling] DI ${diId} ha terminado con estado: ${currentState}. Deteniendo polling.`);
                    const index = this.designs.findIndex(d => d.id_di === diId);
                    if (index !== -1) {
                        this.designs[index] = updatedDi;
                    }
                    clearInterval(this.activePollers.get(diId));
                    this.activePollers.delete(diId);
                }
            } catch (error) {
                console.error(`[Polling] Error al verificar estado para DI ${diId}:`, error);
                clearInterval(this.activePollers.get(diId));
                this.activePollers.delete(diId);
            }
        }, 3000);

        this.activePollers.set(diId, intervalId);
    },
    
    handleRealtimeStandardPayload(payload) {
      const { eventType, new: newRecord, old: oldRecord } = payload;
      
      switch (eventType) {
        case 'INSERT':
          if (!this.designs.some(d => d.id_di === newRecord.id_di)) {
            this.designs.unshift(newRecord);
          }
          break;
        case 'DELETE':
          const indexToDelete = this.designs.findIndex(d => d.id_di === oldRecord.id_di);
          if (indexToDelete !== -1) {
            this.designs.splice(indexToDelete, 1);
          }
          if (this.activePollers.has(oldRecord.id_di)) {
              clearInterval(this.activePollers.get(oldRecord.id_di));
              this.activePollers.delete(oldRecord.id_di);
          }
          break;
      }
    },

    subscribeToChanges() {
      if (this.realtimeChannel) return;
      this.realtimeChannel = supabase
        .channel(`di-changes-${this.user.id}`)
        .on(
          'postgres_changes',
          { event: '*', schema: 'public', table: 'disenos_instruccionales', filter: `id_usuario=eq.${this.user.id}`},
          this.handleRealtimeStandardPayload
        )
        .subscribe();
    },

    async unsubscribeAndClear() {
      this.activePollers.forEach(intervalId => clearInterval(intervalId));
      this.activePollers.clear();

      if (this.realtimeChannel) {
        await supabase.removeChannel(this.realtimeChannel);
        this.realtimeChannel = null;
      }
      this.designs = [];
      this.user = null;
    }
  }
});
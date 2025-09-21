import { defineStore } from 'pinia'
import { getDis } from '@/services/apiService'

export const useDiStore = defineStore('di', {
  state: () => ({
    designs: [],
    isLoading: false,
    hasLoaded: false,
  }),

  actions: {
    // 1. Añadimos un parámetro 'force' a la acción
    async fetchDesigns(force = false) {
      // 2. La lógica de caché ahora respeta el parámetro 'force'
      if (this.hasLoaded && !force) return;

      this.isLoading = true;
      try {
        console.log(`Pinia Store: Cargando DIs desde la API... (Forzado: ${force})`);
        // Si es una recarga forzada, es buena idea limpiar la lista actual
        if (force) {
          this.designs = [];
        }
        this.designs = await getDis();
        this.hasLoaded = true;
        console.log('Pinia Store: DIs cargados exitosamente.');
      } catch (error) {
        console.error('Pinia Store: Error al cargar los DIs:', error);
      } finally {
        this.isLoading = false;
      }
    },

    clearDesigns() {
      this.designs = [];
      this.hasLoaded = false;
      console.log('Pinia Store: Datos de DIs limpiados.');
    }
  },

  persist: {
    storage: sessionStorage,
  },
})
import { defineStore } from 'pinia';
import { getDis } from '@/services/apiService';

// Función para comparar profundamente dos arrays de objetos
function areEqual(array1, array2) {
  if (array1.length !== array2.length) {
    return false;
  }
  for (let i = 0; i < array1.length; i++) {
    const obj1 = array1[i];
    const obj2 = array2[i];

    // Compara el id_di, contenido_jsonld, estado_transformacion y error_transformacion
    if (
      obj1.id_di !== obj2.id_di ||
      obj1.contenido_jsonld !== obj2.contenido_jsonld ||
      obj1.estado_transformacion !== obj2.estado_transformacion ||
      obj1.error_transformacion !== obj2.error_transformacion
    ) {
      return false;
    }
  }
  return true;
}

export const useDiStore = defineStore('di', {
  state: () => ({
    designs: [],
    isLoading: false,
    hasLoaded: false,
  }),

  actions: {
    async fetchDesigns() {
      this.isLoading = true;
      try {
        const fetchedDesigns = await getDis();
        
        // Ordena ambas listas para asegurar una comparación consistente
        const sortedCurrentDesigns = [...this.designs].sort((a, b) => a.id_di.localeCompare(b.id_di));
        const sortedFetchedDesigns = [...fetchedDesigns].sort((a, b) => a.id_di.localeCompare(b.id_di));

        // Usa la función de comparación profunda
        if (!areEqual(sortedCurrentDesigns, sortedFetchedDesigns)) {
          console.log('Pinia Store: Datos de DIs actualizados.');
          this.designs = fetchedDesigns;
        } else {
          console.log('Pinia Store: No hay cambios en los DIs.');
        }

        this.hasLoaded = true;
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
  }
});
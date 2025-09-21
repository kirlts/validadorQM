<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="d-flex align-center">
            <span class="headline">Mis Diseños Instruccionales</span>
            <v-spacer></v-spacer>
            <v-btn
              icon
              variant="text"
              @click="handleRefresh"
              :loading="isLoading"
              :disabled="isLoading"
            >
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-subtitle>
            Selecciona un DI para ver su informe de calidad o proponer modificaciones.
          </v-card-subtitle>
          <v-progress-linear v-if="isLoading" indeterminate color="primary"></v-progress-linear>
          <v-list v-if="!isLoading && designs.length > 0" lines="two">
            <v-list-item
              v-for="design in designs"
              :key="design.id_di"
              @click="viewDetails(design.id_di)"
              :title="design.nombre_archivo"
              :subtitle="'Creado: ' + new Date(design.created_at).toLocaleDateString()"
            >
              <template v-slot:prepend>
                <v-avatar color="primary">
                  <v-icon icon="mdi-file-document-outline"></v-icon>
                </v-avatar>
              </template>
            </v-list-item>
          </v-list>
          <v-card-text v-if="!isLoading && designs.length === 0">
            No has subido ningún Diseño Instruccional todavía.
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" variant="flat">
              <v-icon left>mdi-upload</v-icon>
              Subir Nuevo DI
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useDiStore } from '@/stores/diStore';
import { storeToRefs } from 'pinia';

const router = useRouter();
const diStore = useDiStore();
const { designs, isLoading } = storeToRefs(diStore);

onMounted(() => {
  diStore.fetchDesigns();
});

// 3. Nueva función para manejar el clic del botón
function handleRefresh() {
  // Llamamos a la acción con el parámetro 'true' para forzar la recarga
  diStore.fetchDesigns(true);
}

function viewDetails(id) {
  router.push({ name: 'detail', params: { id: id } });
}
</script>
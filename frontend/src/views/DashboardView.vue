<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="headline">
            Mis Diseños Instruccionales
          </v-card-title>
          <v-card-subtitle>
            Selecciona un DI para ver su informe de calidad o proponer modificaciones.
          </v-card-subtitle>
          <v-list lines="two">
            <v-list-item
              v-for="design in designs"
              :key="design.id"
              @click="viewDetails(design.id)"
              :title="design.name"
              :subtitle="'Última modificación: ' + design.date"
            >
              <template v-slot:prepend>
                <v-avatar color="primary">
                  <v-icon icon="mdi-file-document-outline"></v-icon>
                </v-avatar>
              </template>
            </v-list-item>
          </v-list>
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
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getInstructionalDesigns } from '@/services/mockApiService';

const designs = ref([]);
const router = useRouter();

onMounted(async () => {
  designs.value = await getInstructionalDesigns();
});

function viewDetails(id) {
  // En lugar de construir la URL manualmente, navegamos por el nombre de la ruta.
  // Vue Router construirá la URL correcta (/app/di/1) automáticamente.
  router.push({ name: 'detail', params: { id: id } });
}
</script>
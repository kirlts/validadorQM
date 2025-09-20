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
import { getInstructionalDesigns } from '@/services/mockApiService';

const designs = ref([]);

onMounted(async () => {
  // La validación ahora la hace el guardia del enrutador.
  // El onMounted solo se preocupa de cargar los datos de la vista.
  console.log('Dashboard montado, cargando datos...');
  designs.value = await getInstructionalDesigns();
});
</script>
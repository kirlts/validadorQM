<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="10">
        <v-btn variant="text" @click="$router.back()" class="mb-4">
          <v-icon start>mdi-arrow-left</v-icon>
          Volver al Dashboard
        </v-btn>

        <v-card v-if="diData" class="mb-4">
          <v-card-title class="headline">
            Informe para: {{ diData.nombre_archivo }}
          </v-card-title>
          <v-card-subtitle>
            Análisis de alineación con la rúbrica Quality Matters.
          </v-card-subtitle>
          <v-divider></v-divider>
          
          <v-card-text v-if="procesoEs('validacion', 'success') && diData.evaluacion_di">
            <v-expansion-panels variant="inset">
              <v-expansion-panel v-for="item in reportSections" :key="item.key">
                <v-expansion-panel-title>{{ item.title }}</v-expansion-panel-title>
                <v-expansion-panel-text class="report-text" v-if="diData.evaluacion_di[item.key]">
                  {{ diData.evaluacion_di[item.key] }}
                </v-expansion-panel-text>
                <v-expansion-panel-text class="text-grey" v-else>
                  No se encontraron datos para esta sección.
                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
          </v-card-text>

          <v-card-text v-else-if="procesoEs(null, 'processing')" class="text-center pa-4">
            <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
            <p class="mt-4 text-grey-darken-1 text-h6">Procesando: {{ diData.proceso_actual.nombre }}...</p>
            <p class="text-grey-darken-2">El estado se actualizará automáticamente.</p>
          </v-card-text>

          <v-card-text v-else-if="procesoEs('validacion', 'error')" class="pa-4">
            <v-alert type="error" variant="tonal" border="start" prominent>
              <h3 class="mb-2">Error al Generar el Informe</h3>
              <p>Ocurrió un error: <code class="d-block mt-2 pa-2 error-code">{{ diData.proceso_actual.error_detalle || 'No hay detalles.' }}</code></p>
              <v-btn color="error" variant="outlined" class="mt-4" @click="startValidation" :loading="isStartingValidation" :disabled="isActionDisabled">
                Reintentar
              </v-btn>
            </v-alert>
          </v-card-text>

          <v-card-text v-else class="text-center pa-4">
            <v-alert type="info" variant="tonal" class="mb-4">
              Aún no se ha generado un informe para este DI.
            </v-alert>
            <v-btn color="primary" @click="startValidation" :loading="isStartingValidation" :disabled="isActionDisabled">
              <v-icon left>mdi-play-circle-outline</v-icon>
              Generar Informe
            </v-btn>
          </v-card-text>
        </v-card>

        <v-card v-else class="text-center pa-10">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
            <p class="mt-4">Cargando datos del Diseño Instruccional...</p>
        </v-card>

        <v-card class="mt-6" v-if="diData && procesoEs('validacion', 'success')">
          <v-card-title>Modificación Interactiva con IA</v-card-title>
          <v-card-subtitle>Propón cambios en lenguaje natural para mejorar el DI.</v-card-subtitle>
          <v-divider class="mt-2"></v-divider>
          </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
/* Estilos sin cambios */
</style>

<script setup>
import { ref, computed } from 'vue';
import { useAppStore } from '@/stores/appStore';
import { generateDiValidation } from '@/services/apiService';
import { getModificationSuggestion } from '@/services/mockApiService';

const props = defineProps({ id: { type: String, required: true } });
const appStore = useAppStore();
const isStartingValidation = ref(false);

const diData = computed(() => appStore.designs.find(d => d.id_di === props.id));

const procesoEs = (nombre, estado) => {
  const proceso = diData.value?.proceso_actual;
  if (!proceso) return false;
  if (nombre === null) return proceso.estado === estado;
  return proceso.nombre === nombre && proceso.estado === estado;
};

const isActionDisabled = computed(() => {
  return isStartingValidation.value || procesoEs(null, 'processing');
});

const reportSections = [
  { key: 'evaluacionPorEje', title: '1. Evaluación por Eje QM' },
  { key: 'analisisDebilidades', title: '2. Análisis de Debilidades' },
  { key: 'analisisFortalezas', title: '3. Análisis de Fortalezas' },
  { key: 'sugerenciasMejora', title: '4. Sugerencias de Mejora' },
  { key: 'comentariosProceso', title: '5. Comentarios del Proceso' }
];

async function startValidation() {
  isStartingValidation.value = true;
  try {
    await generateDiValidation(props.id);
  } catch (error) {
    console.error("Error al iniciar la validación:", error);
  } finally {
    isStartingValidation.value = false;
  }
}

// Lógica para la simulación de chat (sin cambios)
const userInput = ref('');
const isSuggestionLoading = ref(false);
const suggestionResponse = ref('');

async function handleSuggestionRequest() {
  if (!userInput.value.trim()) return;
  isSuggestionLoading.value = true;
  suggestionResponse.value = '';
  try {
    const response = await getModificationSuggestion(userInput.value);
    suggestionResponse.value = response;
  } catch (error) {
    suggestionResponse.value = '<p style="color: red;">Error al simular la respuesta de la IA.</p>';
  } finally {
    userInput.value = '';
    isSuggestionLoading.value = false;
  }
}
</script>
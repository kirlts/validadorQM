<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="10">
        <v-btn variant="text" @click="$router.back()" class="mb-4">
          <v-icon start>mdi-arrow-left</v-icon>
          Volver al Dashboard
        </v-btn>

        <!-- Card del Informe de Validación (existente) -->
        <v-card v-if="diData" class="mb-4">
          <v-card-title class="headline">
            Informe para: {{ diData.nombre_archivo }}
          </v-card-title>
          <v-card-subtitle>
            Análisis de alineación con la rúbrica Quality Matters.
          </v-card-subtitle>
          <v-divider></v-divider>
          
          <v-card-text v-if="diData.estado_evaluacion === 'success' && diData.evaluacion_di">
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

          <v-card-text v-else-if="diData.estado_evaluacion === 'processing'" class="text-center pa-4">
            <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
            <p class="mt-4 text-grey-darken-1 text-h6">Generando informe de validación...</p>
            <p class="text-grey-darken-2">Este proceso puede tardar unos minutos.</p>
          </v-card-text>

          <v-card-text v-else-if="diData.estado_evaluacion === 'error'" class="pa-4">
            <v-alert type="error" variant="tonal" border="start" prominent>
              <h3 class="mb-2">Error al Generar el Informe</h3>
              <p>Ocurrió un error: <code class="d-block mt-2 pa-2 error-code">{{ diData.error_evaluacion || 'No hay detalles.' }}</code></p>
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

        <!-- ================================================================== -->
        <!-- NUEVA CARD PARA LA MODIFICACIÓN INTERACTIVA (SIMULADA) -->
        <!-- ================================================================== -->
        <v-card class="mt-6" v-if="diData && diData.estado_evaluacion === 'success'">
          <v-card-title>Modificación Interactiva (Demo)</v-card-title>
          <v-card-subtitle>Propón cambios en lenguaje natural para mejorar el DI.</v-card-subtitle>
          <v-divider class="mt-2"></v-divider>

          <v-card-text>
            <!-- Área para mostrar la respuesta de la IA -->
            <v-expand-transition>
              <div v-if="suggestionResponse">
                <v-alert
                  icon="mdi-auto-fix"
                  variant="tonal"
                  color="info"
                  class="mb-4"
                  border="start"
                >
                  <h4 class="mb-2">Sugerencia de Implementación:</h4>
                  <!-- Usamos v-html porque la respuesta mock tiene formato HTML -->
                  <div v-html="suggestionResponse"></div>
                </v-alert>
              </div>
            </v-expand-transition>

            <!-- Área de texto para la entrada del usuario -->
            <v-textarea
              v-model="userInput"
              label="Describe la modificación que deseas realizar"
              placeholder="Ej: Añadir una actividad práctica en la semana 3 sobre bucles for."
              rows="3"
              variant="outlined"
              auto-grow
              clearable
              :disabled="isSuggestionLoading"
            ></v-textarea>
          </v-card-text>

          <!-- Barra de progreso lineal mientras se "genera" la respuesta -->
          <v-progress-linear
            :active="isSuggestionLoading"
            indeterminate
            color="primary"
          ></v-progress-linear>

          <v-card-actions class="pa-4">
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              variant="flat"
              @click="handleSuggestionRequest"
              :loading="isSuggestionLoading"
              :disabled="!userInput.trim()"
              prepend-icon="mdi-send"
            >
              Enviar Propuesta
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.report-text { white-space: pre-wrap; text-align: justify; }
.error-code { background-color: rgba(0,0,0,0.05); border-radius: 4px; }
</style>

<script setup>
import { ref, computed } from 'vue';
import { useAppStore } from '@/stores/appStore';
import { generateDiValidation } from '@/services/apiService';
// Importamos la función de simulación desde mockApiService
import { getModificationSuggestion } from '@/services/mockApiService';

const props = defineProps({ id: { type: String, required: true } });
const appStore = useAppStore();
const isStartingValidation = ref(false);

const diData = computed(() => appStore.designs.find(d => d.id_di === props.id));

const isActionDisabled = computed(() => {
  return isStartingValidation.value || (diData.value && diData.value.estado_evaluacion === 'processing');
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
  
  const diIndex = appStore.designs.findIndex(d => d.id_di === props.id);
  if (diIndex !== -1) {
    appStore.designs[diIndex].estado_evaluacion = 'processing';
    appStore.designs[diIndex].error_evaluacion = null;
  }

  try {
    await generateDiValidation(props.id);
    appStore.startPollingDiStatus(props.id, 'estado_evaluacion');
  } catch (error) {
    if (diIndex !== -1) {
      appStore.designs[diIndex].estado_evaluacion = 'error';
      appStore.designs[diIndex].error_evaluacion = error.message;
    }
  } finally {
    isStartingValidation.value = false;
  }
}

// ==================================================================
// NUEVA LÓGICA PARA LA SIMULACIÓN DE CHAT
// ==================================================================
const userInput = ref('');
const isSuggestionLoading = ref(false);
const suggestionResponse = ref('');

async function handleSuggestionRequest() {
  // No enviar si el input está vacío
  if (!userInput.value.trim()) return;

  isSuggestionLoading.value = true;
  suggestionResponse.value = ''; // Limpiar respuesta anterior

  try {
    // Llamamos a la función simulada y esperamos su respuesta
    const response = await getModificationSuggestion(userInput.value);
    suggestionResponse.value = response;
  } catch (error) {
    // Manejo de error por si la simulación falla
    suggestionResponse.value = '<p style="color: red;">Error al simular la respuesta de la IA.</p>';
  } finally {
    // Limpiamos el input y reactivamos el botón
    userInput.value = '';
    isSuggestionLoading.value = false;
  }
}
</script>
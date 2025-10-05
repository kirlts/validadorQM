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
          <v-card-text v-if="diData.evaluacion_di">
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
          </v-card-text>
          <v-card-text v-else-if="procesoEs('evaluacion', 'error')" class="pa-4">
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

        <v-card class="mt-6" v-if="diData && diData.evaluacion_di">
          <v-card-title>Asistencia Interactiva con IA</v-card-title>
          <v-card-subtitle>Realiza una consulta sobre el Diseño Instruccional y/o su informe de validación.</v-card-subtitle>
          <v-divider class="mt-2"></v-divider>

          <v-card-text>
            <v-expand-transition>
              <div v-if="showResponseArea">
                <v-card variant="tonal" color="light-blue-lighten-5" class="mb-4">
                  <div v-if="!isSuggestionLoading && suggestionPrompt">
                    <v-card-subtitle class="d-flex align-center pt-3 response-header">
                      <v-icon class="mr-2">mdi-account-voice-outline</v-icon>
                      Tu Pregunta:
                    </v-card-subtitle>
                    <v-card-text class="pb-0">
                      <p class="user-prompt">"{{ suggestionPrompt }}"</p>
                    </v-card-text>
                    <v-divider class="my-2 mx-4"></v-divider>
                  </div>
                  
                  <v-card-subtitle class="d-flex align-center pt-3 response-header">
                    <v-icon class="mr-2">mdi-auto-fix</v-icon>
                    Asistente IA:
                  </v-card-subtitle>
                  <v-card-text>
                    <v-skeleton-loader v-if="isSuggestionLoading" type="text@4" boilerplate></v-skeleton-loader>
                    <div v-else v-html="renderedMarkdown" class="markdown-content"></div>
                  </v-card-text>
                </v-card>
              </div>
            </v-expand-transition>
            
            <v-alert 
              v-if="procesoEs('consulta', 'error') && !isErrorDismissed"
              type="warning" 
              variant="tonal" 
              class="mb-4"
              closable
              @click:close="dismissError"
            >
                Error en la última consulta: {{ diData.proceso_actual.error_detalle }}
            </v-alert>
            
            <v-textarea v-model="userInput" label="Escribe tu pregunta aquí..." placeholder="Ej: ¿Puedes darme un ejemplo de una actividad para el indicador IL1.2?" rows="3" variant="outlined" auto-grow clearable :disabled="isActionDisabled" hide-details></v-textarea>
          </v-card-text>

          <v-card-actions class="pa-4 pt-2">
            <div v-if="hasPreviousResponse">
              <v-btn v-if="!showResponseArea" variant="tonal" @click="showResponseArea = true">
                <v-icon start>mdi-history</v-icon>
                Ver Última Respuesta
              </v-btn>
              <v-btn v-else variant="text" @click="showResponseArea = false">
                <v-icon start>mdi-eye-off-outline</v-icon>
                Ocultar Respuesta
              </v-btn>
            </div>
            
            <v-spacer></v-spacer>
            <v-btn color="primary" variant="flat" @click="handleSuggestionRequest" :loading="isSuggestionLoading" :disabled="!userInput.trim() || isActionDisabled" prepend-icon="mdi-send">
              Enviar Consulta
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
.response-header { font-weight: 500; color: #455A64; font-size: 1rem; }
.user-prompt { font-style: italic; color: #546E7A; font-size: 1rem; opacity: 0.9; }
.markdown-content { color: #333; }
.markdown-content :deep(h1), .markdown-content :deep(h2), .markdown-content :deep(h3) { margin-top: 16px; margin-bottom: 8px; line-height: 1.4; color: #111; }
.markdown-content :deep(p) { line-height: 1.7; margin-bottom: 12px; }
.markdown-content :deep(ul), .markdown-content :deep(ol) { padding-left: 24px; margin-bottom: 16px; }
.markdown-content :deep(li) { margin-bottom: 8px; }
.markdown-content :deep(code) { background-color: rgba(0,0,0,0.07); color: #c7254e; padding: 3px 6px; border-radius: 4px; font-family: 'Courier New', Courier, monospace; font-size: 0.9em; }
.markdown-content :deep(pre) { background-color: #2d2d2d; color: #f8f8f2; padding: 16px; border-radius: 8px; overflow-x: auto; margin-bottom: 16px; }
.markdown-content :deep(pre code) { background-color: transparent; color: inherit; padding: 0; }
.markdown-content :deep(blockquote) { border-left: 4px solid #b3e5fc; padding-left: 16px; margin-left: 0; color: #546e7a; font-style: italic; }
</style>

<script setup>
import { ref, computed, watch } from 'vue';
import { useAppStore } from '@/stores/appStore';
import { generateDiValidation, interactWithDi } from '@/services/apiService';
import MarkdownIt from 'markdown-it';

const md = new MarkdownIt();

const props = defineProps({ id: { type: String, required: true } });
const appStore = useAppStore();
const isStartingValidation = ref(false);

const diData = computed(() => appStore.designs.find(d => d.id_di === props.id));

const showResponseArea = ref(false);
const hasPreviousResponse = computed(() => !!diData.value?.ultima_respuesta_ia?.respuesta);
const suggestionPrompt = computed(() => diData.value?.ultima_respuesta_ia?.prompt);
const suggestionResponse = computed(() => diData.value?.ultima_respuesta_ia?.respuesta || '');

const renderedMarkdown = computed(() => {
    if (suggestionResponse.value) { return md.render(suggestionResponse.value); }
    return '';
});

const procesoEs = (nombre, estado) => {
  const proceso = diData.value?.proceso_actual;
  if (!proceso) return false;
  if (nombre === null) return proceso.estado === estado;
  return proceso.nombre === nombre && proceso.estado === estado;
};

const isActionDisabled = computed(() => {
  return isStartingValidation.value || procesoEs(null, 'processing');
});

const isSuggestionLoading = computed(() => procesoEs('consulta', 'processing'));

const dismissedErrorTimestamp = ref(localStorage.getItem(`dismissedError_${props.id}`));

const isErrorDismissed = computed(() => {
  if (!procesoEs('consulta', 'error')) return false;
  return dismissedErrorTimestamp.value === diData.value.proceso_actual.timestamp;
});

function dismissError() {
  if (procesoEs('consulta', 'error')) {
    const timestamp = diData.value.proceso_actual.timestamp;
    localStorage.setItem(`dismissedError_${props.id}`, timestamp);
    dismissedErrorTimestamp.value = timestamp;
  }
}

// --- LÓGICA DE VISIBILIDAD FINAL Y CORREGIDA ---
const requestInitiatedByUser = ref(false);

watch(() => diData.value?.proceso_actual, (newProceso, oldProceso) => {
    // Si un proceso de consulta acaba de terminar...
    if (oldProceso?.nombre === 'consulta' && oldProceso?.estado === 'processing' && newProceso?.estado !== 'processing') {
        // ...y la acción fue iniciada por el usuario en esta vista...
        if (requestInitiatedByUser.value) {
            // Si el resultado es un ERROR, ocultamos el área de respuesta para priorizar la alerta.
            if (newProceso.estado === 'error') {
                showResponseArea.value = false;
            }
            // Si el resultado es ÉXITO, el área de respuesta ya está abierta y se queda abierta.
            // No es necesario hacer nada.
        }
        // Reseteamos la bandera para la próxima interacción.
        requestInitiatedByUser.value = false;
    }

    // Limpiar errores descartados si llega un nuevo proceso de consulta.
    if (newProceso?.nombre === 'consulta' && newProceso?.estado !== 'error') {
        localStorage.removeItem(`dismissedError_${props.id}`);
        dismissedErrorTimestamp.value = null;
    }
});

const reportSections = [
  { key: 'evaluacionPorEje', title: '1. Evaluación por Eje QM' },
  { key: 'analisisDebilidades', title: '2. Análisis de Debilidades' },
  { key: 'analisisFortalezas', title: '3. Análisis de Fortalezas' },
  { key: 'sugerenciasMejora', title: '4. Sugerencias de Mejora' },
  { key: 'comentariosProceso', title: '5. Comentarios del Proceso' }
];

async function startValidation() {
  if (!diData.value) return;
  isStartingValidation.value = true;
  try { await generateDiValidation(diData.value.id_di); } 
  catch (error) { console.error("Error al iniciar la validación:", error); } 
  finally { isStartingValidation.value = false; }
}

async function handleSuggestionRequest() {
  if (!userInput.value.trim() || isSuggestionLoading.value || !diData.value) return;
  
  // Marcamos que la acción fue iniciada por el usuario ANTES de hacer nada.
  requestInitiatedByUser.value = true;
  
  // Abrimos el área de respuesta para mostrar el esqueleto de carga.
  showResponseArea.value = true;

  try { await interactWithDi(diData.value.id_di, userInput.value); } 
  catch (error) { console.error("Error al enviar la consulta:", error); } 
  finally { userInput.value = ''; }
}

const userInput = ref('');
</script>
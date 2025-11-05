<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="10">
        <!-- Estado de Carga Inicial -->
        <div v-if="isLoading" class="text-center pa-10">
          <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
          <p class="mt-4">Cargando datos del Diseño Instruccional...</p>
        </div>

        <!-- Contenido Principal de la Vista -->
        <v-card v-else-if="design">
          <!-- 1. Encabezado -->
          <v-toolbar color="primary" density="compact">
            <v-btn icon @click="$router.push({ name: 'dashboard' })" title="Volver al Dashboard">
              <v-icon>mdi-arrow-left</v-icon>
            </v-btn>
            <v-toolbar-title class="text-truncate">{{ design.nombre_archivo }}</v-toolbar-title>
          </v-toolbar>

          <!-- 2. Sección de Herramientas de Análisis -->
          <v-card-text>
            <v-card variant="outlined">
              <v-card-title>Herramientas de Análisis</v-card-title>
              <v-card-text>
                <p class="mb-4">
                  Selecciona una herramienta para obtener un análisis de alineamiento del archivo.
                </p>
                <v-btn
                  v-if="design.estructura_mei === 'MEI-Antiguo'"
                  color="primary"
                  @click="handleAlignmentAnalysis"
                  :loading="isAnalyzing"
                  :disabled="isProcessing"
                >
                  Analizar Alineamiento RA-AE-IL
                </v-btn>
                <v-btn
                  v-if="design.estructura_mei === 'MEI-Actualizado'"
                  color="primary"
                  @click="handleAlignmentAnalysis"
                  :loading="isAnalyzing"
                  :disabled="isProcessing"
                >
                  Analizar Alineamiento RF-RA-ID
                </v-btn>
              </v-card-text>
            </v-card>
          </v-card-text>

          <!-- 3. Sección de Resultados del Análisis de Alineamiento (AHORA DESPLEGABLE) -->
          <v-divider></v-divider>
          <div class="pa-4">
            <!-- Estado de Procesando (se muestra fuera del panel) -->
            <v-alert v-if="isProcessing && design.proceso_actual?.nombre === 'analisis_alineamiento'"
              type="info" variant="tonal" border="start" prominent class="mb-4">
              Procesando análisis... La vista se actualizará automáticamente al finalizar.
            </v-alert>
            
            <!-- Panel de Resultados (solo se muestra si hay datos) -->
            <v-expansion-panels v-if="analysisResult" v-model="analysisPanel" variant="inset">
              <v-expansion-panel>
                <v-expansion-panel-title class="text-h6">
                  Resultados del Análisis de Alineamiento
                </v-expansion-panel-title>
                <v-expansion-panel-text>
                  <!-- Veredicto General -->
                  <div v-if="analysisResult.resumenGeneral" class="pa-4 rounded-lg my-4" :class="getVerdictBgColor(analysisResult.resumenGeneral.veredictoGeneral)">
                    <h4 class="mb-1">Veredicto General: {{ analysisResult.resumenGeneral.veredictoGeneral }}</h4>
                    <p class="text-body-2 mb-0">Estructura MEI analizada: {{ analysisResult.resumenGeneral.paradigma }}</p>
                  </div>

                  <!-- Descripción del Curso -->
                  <div v-if="analysisResult.descripcionCurso" class="my-6">
                    <h4 class="mb-2">Descripción General de la Asignatura</h4>
                    <p class="text-body-1 text-medium-emphasis">{{ analysisResult.descripcionCurso }}</p>
                  </div>
                  <v-divider class="my-6"></v-divider>

                  <!-- Resultados de Aprendizaje (RA) -->
                  <div v-if="analysisResult.analisisResultadosAprendizaje && analysisResult.analisisResultadosAprendizaje.length">
                    <h4 class="mb-3">Resultados de Aprendizaje (RA) Formales</h4>
                    <div v-for="(ra, index) in analysisResult.analisisResultadosAprendizaje" :key="`ra-${index}`" class="mb-4">
                      <p class="text-body-1 font-weight-medium text-wrap">{{ ra.resultadoAprendizaje }}</p>
                      <v-chip size="small" label>{{ ra.verboPrincipal }} ({{ ra.nivelTaxonomico }})</v-chip>
                      <v-divider v-if="index < analysisResult.analisisResultadosAprendizaje.length - 1" class="mt-4"></v-divider>
                    </div>
                  </div>
                  <v-divider class="my-6"></v-divider>

                  <h4 class="mb-4">Análisis por Aprendizaje Esperado (AE)</h4>

                  <!-- Paneles Desplegables Internos por AE -->
                  <v-expansion-panels v-if="analysisResult.analisisPorObjetivo?.length" variant="accordion">
                    <v-expansion-panel v-for="(analisisAE, index) in analysisResult.analisisPorObjetivo" :key="index">
                        <v-expansion-panel-title>
                            <v-chip :color="getVerdictColor(analisisAE.veredicto)" class="verdict-chip mr-4" label>{{ analisisAE.veredicto }}</v-chip>
                            <div class="text-wrap">{{ analisisAE.objetivo }}</div>
                        </v-expansion-panel-title>
                        <v-expansion-panel-text class="pa-4">
                            <p><strong>Verbo Principal:</strong> {{ analisisAE.verboPrincipal }} ({{ analisisAE.nivelTaxonomico }})</p>
                            <p class="text-wrap"><strong>Coherencia con RA:</strong> <span class="text-medium-emphasis">{{ analisisAE.coherenciaConRA }}</span></p>
                            <p class="font-italic text-medium-emphasis mb-4"><strong>Justificación:</strong> {{ analisisAE.justificacion }}</p>
                            <v-divider class="my-4"></v-divider>
                            <h5 class="mb-3">Desglose de Indicadores</h5>
                            <div v-for="(indicador, i) in analisisAE.desgloseIndicadores" :key="i" class="py-3" :class="{ 'border-t': i > 0 }">
                                <p class="font-weight-bold text-wrap">{{ indicador.indicador }}</p>
                                <p class="text-body-2 mt-2 mb-0"><strong>Verbo:</strong> {{ indicador.verbo }} ({{ indicador.nivelTaxonomico }})</p>
                                <p class="text-body-2 mb-0"><strong>Coherencia Semántica:</strong> {{ indicador.analisisSemantico }}</p>
                                <p class="text-body-2 mb-0"><strong>Coherencia Taxonómica:</strong> <span :class="getTaxonomicColorClass(indicador.analisisTaxonomico)">{{ indicador.analisisTaxonomico }}</span></p>
                                <p v-if="indicador.analisisSintactico" class="text-body-2 mb-0"><strong>Coherencia Sintáctica:</strong> <span :class="getSyntacticColorClass(indicador.analisisSintactico)">{{ indicador.analisisSintactico }}</span></p>
                            </div>
                        </v-expansion-panel-text>
                    </v-expansion-panel>
                  </v-expansion-panels>

                </v-expansion-panel-text>
              </v-expansion-panel>
            </v-expansion-panels>
            
            <!-- Mensaje si no hay análisis aún -->
            <p v-else-if="!isProcessing">Aún no se ha realizado un análisis de alineamiento.</p>
          </div>
          
          <!-- Asistente de IA -->
          <v-divider class="my-6"></v-divider>
          <v-card-title>Asistencia Interactiva con IA</v-card-title>
           <v-card-text>
             <p class="mb-4">Realiza una consulta sobre el Diseño Instruccional y/o su análisis.</p>
             <v-textarea
                v-model="userPrompt"
                label="Tu Pregunta"
                rows="3"
                variant="outlined"
                prepend-inner-icon="mdi-account-voice-outline"
                clearable
                :disabled="isIaProcessing"
             ></v-textarea>
             
             <div v-if="isIaProcessing || (isIaError && !isErrorDismissed) || (showLastResponse && hasLastResponse)" class="ia-response-container pa-4 rounded-lg mb-4">
                <div v-if="isIaProcessing" class="text-center">
                    <v-progress-circular indeterminate color="primary"></v-progress-circular>
                    <p class="mt-2 text-medium-emphasis">El asistente está pensando...</p>
                </div>
                <div v-else-if="isIaError && !isErrorDismissed">
                    <div class="d-flex justify-space-between align-center">
                      <p class="text-error font-weight-bold">Error en la consulta</p>
                      <v-btn icon="mdi-close" variant="text" size="small" @click="dismissError" title="Descartar error"></v-btn>
                    </div>
                    <p>{{ design.proceso_actual.error_detalle || "Ocurrió un error desconocido." }}</p>
                </div>
                <div v-else-if="showLastResponse && hasLastResponse">
                    <pre class="ia-response-text">{{ design.ultima_respuesta_ia.respuesta }}</pre>
                </div>
             </div>
             
             <div class="d-flex justify-end align-center">
                <v-btn
                  variant="text"
                  @click="toggleLastResponse"
                  :disabled="!hasLastResponse || isIaProcessing"
                >
                  {{ showLastResponse ? 'Ocultar Respuesta' : 'Ver Última Respuesta IA' }}
                </v-btn>
                <v-spacer></v-spacer>
                <v-btn 
                    color="secondary" 
                    @click="handleInteract" 
                    :loading="isIaProcessing"
                    :disabled="isProcessing || !userPrompt"
                >
                    Enviar Consulta
                </v-btn>
             </div>
          </v-card-text>

        </v-card>
        
        <v-alert v-else type="error">
          No se encontró el Diseño Instruccional solicitado.
        </v-alert>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useAppStore } from '@/stores/appStore';
import { storeToRefs } from 'pinia';
import { analyzeAlignment, interactWithDi } from '@/services/apiService';

const route = useRoute();
const appStore = useAppStore();
const { designs } = storeToRefs(appStore);

const isAnalyzing = ref(false);
const userPrompt = ref('');
const diId = route.params.id;

// --- ESTADOS PARA GESTIONAR LA UI ---
const showLastResponse = ref(false);
const isErrorDismissed = ref(true); 
// NUEVO: Estado para controlar el panel de análisis principal
const analysisPanel = ref([]);

const design = computed(() => designs.value.find(d => d.id_di === diId));
const analysisResult = computed(() => design.value?.analisis_alineamiento?.resultado);
const isLoading = computed(() => appStore.isLoading && !design.value);
const isProcessing = computed(() => design.value?.proceso_actual?.estado === 'processing');

const isIaProcessing = computed(() => isProcessing.value && design.value?.proceso_actual?.nombre === 'consulta');
const hasLastResponse = computed(() => !!design.value?.ultima_respuesta_ia?.respuesta);
const isIaError = computed(() => design.value?.proceso_actual?.nombre === 'consulta' && design.value?.proceso_actual?.estado === 'error');

watch(design, (newDesign, oldDesign) => {
  if (!newDesign || !oldDesign) return;
  const oldProcess = oldDesign.proceso_actual;
  const newProcess = newDesign.proceso_actual;

  // Lógica para el chat de IA
  if (oldProcess?.nombre === 'consulta' && oldProcess?.estado === 'processing') {
    if (newProcess?.estado === 'success') {
      showLastResponse.value = true;
      isErrorDismissed.value = true;
    }
    if (newProcess?.estado === 'error') {
      showLastResponse.value = false;
      isErrorDismissed.value = false;
    }
  }

  // NUEVO: Lógica para auto-expandir el panel de análisis
  if (oldProcess?.nombre === 'analisis_alineamiento' && oldProcess?.estado === 'processing' &&
      newProcess?.nombre === 'analisis_alineamiento' && newProcess?.estado === 'success') {
    // El análisis acaba de terminar, abrimos el panel. El v-model es un array, [0] abre el primer panel.
    analysisPanel.value = [0];
  }
});

const handleInteract = async () => {
  if (!design.value || !userPrompt.value) return;
  showLastResponse.value = false;
  isErrorDismissed.value = true;
  try {
    await interactWithDi(design.value.id_di, userPrompt.value);
    userPrompt.value = '';
  } catch (error) {
    console.error("Error al enviar la consulta:", error);
    isErrorDismissed.value = false; 
  }
};

const toggleLastResponse = () => {
  showLastResponse.value = !showLastResponse.value;
  if (showLastResponse.value) {
    isErrorDismissed.value = true;
  }
};

const dismissError = () => {
  isErrorDismissed.value = true;
};

const getVerdictColor = (verdict) => {
  if (!verdict) return 'grey';
  if (verdict.includes('NO ALINEADO')) return 'error';
  if (verdict.includes('CON OBSERVACIONES')) return 'warning';
  if (verdict.includes('ALINEADO')) return 'success';
  return 'grey';
};
const getVerdictBgColor = (verdict) => {
  const color = getVerdictColor(verdict);
  if (color === 'error') return 'bg-red-lighten-5';
  if (color === 'warning') return 'bg-orange-lighten-5';
  if (color === 'success') return 'bg-green-lighten-5';
  return 'bg-grey-lighten-4';
};
const getTaxonomicColorClass = (text) => {
  if (!text) return '';
  if (text.toLowerCase().includes('incoherente')) return 'text-error font-weight-bold';
  if (text.toLowerCase().includes('coherente')) return 'text-success';
  return '';
};
const getSyntacticColorClass = (text) => {
  if (!text) return '';
  if (text.toLowerCase().includes('problema')) return 'text-error font-weight-bold';
  if (text.toLowerCase().includes('correcto')) return 'text-success';
  return '';
};
const handleAlignmentAnalysis = async () => {
  if (!design.value) return;
  isAnalyzing.value = true;
  try {
    await analyzeAlignment(design.value.id_di);
  } catch (error) {
    console.error("Error al iniciar el análisis:", error);
  } finally {
    isAnalyzing.value = false;
  }
};

onMounted(() => {
  if (designs.value.length === 0) {
    appStore.fetchDesigns();
  }
});
</script>

<style scoped>
  .ia-response-container {
    background-color: rgba(0,0,0,0.02);
    border: 1px solid rgba(0,0,0,0.08);
  }
  .ia-response-text {
    white-space: pre-wrap;
    word-wrap: break-word;
    font-family: 'Roboto', sans-serif;
    font-size: 0.9em;
    line-height: 1.6;
  }
  .text-wrap {
    white-space: normal !important;
  }
  .v-expansion-panel-title > div {
    white-space: normal;
    overflow: visible;
    text-overflow: clip;
  }
  .verdict-chip {
    height: auto !important;
    white-space: normal;
    padding-top: 4px;
    padding-bottom: 4px;
  }
  .v-expansion-panel-text {
    background-color: rgba(0,0,0,0.02);
  }
</style>
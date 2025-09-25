// frontend/src/views/DetailView.vue

<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="10">
        <v-btn variant="text" @click="$router.back()" class="mb-4">
          <v-icon start>mdi-arrow-left</v-icon>
          Volver al Dashboard
        </v-btn>
        <v-card class="mb-4">
          <v-card-title class="headline">
            Informe de Calidad para: {{ diData?.nombre_archivo || 'Cargando...' }}
          </v-card-title>
          <v-card-subtitle>
            Análisis de alineación con la rúbrica Quality Matters.
          </v-card-subtitle>
          <v-divider></v-divider>
          
          <v-card-text v-if="isLoadingReport" class="text-center pa-4">
            <v-progress-circular indeterminate color="primary"></v-progress-circular>
            <p class="mt-2 text-grey-darken-1">Cargando datos del informe...</p>
          </v-card-text>

          <v-card-text v-else-if="diData && diData.estado_evaluacion === 'success' && diData.evaluacion_di">
            <v-expansion-panels variant="inset">
              <v-expansion-panel
                v-for="item in reportSections"
                :key="item.key"
              >
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

          <v-card-text v-else-if="diData && diData.estado_evaluacion === 'processing'" class="text-center pa-4">
            <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
            <p class="mt-4 text-grey-darken-1 text-h6">Generando informe de validación...</p>
            <p class="text-grey-darken-2">Este proceso puede tardar unos minutos. El estado se actualizará automáticamente.</p>
          </v-card-text>

          <v-card-text v-else-if="diData && diData.estado_evaluacion === 'error'" class="pa-4">
            <v-alert type="error" variant="tonal" border="start" prominent>
              <h3 class="mb-2">Error al Generar el Informe</h3>
              <p>Ocurrió un error durante la validación del DI. Detalles del error:</p>
              <code class="d-block mt-2 pa-2 error-code">{{ diData.error_evaluacion || 'No se proporcionaron detalles.' }}</code>
              <v-btn color="error" variant="outlined" class="mt-4" @click="startValidation" :loading="isStartingValidation">
                Reintentar Generación
              </v-btn>
            </v-alert>
          </v-card-text>

          <v-card-text v-else class="text-center pa-4">
            <v-alert type="info" variant="tonal" class="mb-4">
              Aún no se ha generado un informe de validación para este Diseño Instruccional.
            </v-alert>
            <v-btn color="primary" @click="startValidation" :loading="isStartingValidation">
              <v-icon left>mdi-play-circle-outline</v-icon>
              Generar Informe de Validación
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<style scoped>
.report-text { white-space: pre-wrap; text-align: justify; }
.error-code { background-color: rgba(0,0,0,0.05); border-radius: 4px; padding: 4px 8px; display: block; white-space: pre-wrap; word-break: break-all; }
</style>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { supabase } from '@/supabase';
import { getDiValidation, generateDiValidation } from '@/services/apiService';

const props = defineProps({
  id: { type: String, required: true }
});

const diData = ref(null);
const isLoadingReport = ref(true);
const isStartingValidation = ref(false);
const realtimeChannel = ref(null);

const reportSections = [
  { key: 'evaluacionPorEje', title: '1. Evaluación por Eje QM' },
  { key: 'analisisDebilidades', title: '2. Análisis de Debilidades' },
  { key: 'analisisFortalezas', title: '3. Análisis de Fortalezas' },
  { key: 'sugerenciasMejora', title: '4. Sugerencias de Mejora' },
  { key: 'comentariosProceso', title: '5. Comentarios del Proceso' }
];

async function fetchData() {
  isLoadingReport.value = true;
  try {
    diData.value = await getDiValidation(props.id);
  } catch (error) {
    console.error("Error al cargar los datos del DI:", error);
  } finally {
    isLoadingReport.value = false;
  }
}

function subscribeToDiChanges() {
  if (realtimeChannel.value) return;

  realtimeChannel.value = supabase
    .channel(`di-detail-${props.id}`)
    .on(
      'postgres_changes',
      {
        event: 'UPDATE',
        schema: 'public',
        table: 'disenos_instruccionales',
        filter: `id_di=eq.${props.id}`
      },
      (payload) => {
        console.log('DetailView: Cambio detectado en el DI actual.', payload.new);
        // Actualización robusta: reemplaza el objeto completo para asegurar la reactividad
        if (payload.new) {
          diData.value = payload.new;
        }
      }
    )
    .subscribe();
}

async function startValidation() {
  isStartingValidation.value = true;
  
  // Actualización Optimista: cambia el estado local inmediatamente
  if (diData.value) {
    diData.value.estado_evaluacion = 'processing';
  }

  try {
    await generateDiValidation(props.id);
    // La suscripción de Realtime se encargará de actualizar con el resultado final ('success' o 'error')
  } catch (error) {
    console.error("Error al iniciar la validación:", error);
    // Si la llamada a la API falla, revierte el estado
    if (diData.value) {
      diData.value.estado_evaluacion = 'error';
      diData.value.error_evaluacion = error.message || 'Fallo al contactar el servidor.';
    }
  } finally {
    isStartingValidation.value = false;
  }
}

onMounted(() => {
  fetchData();
  subscribeToDiChanges();
});

onUnmounted(() => {
  if (realtimeChannel.value) {
    supabase.removeChannel(realtimeChannel.value);
  }
});
</script>q  
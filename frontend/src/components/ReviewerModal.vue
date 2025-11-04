<template>
  <v-dialog :model-value="modelValue" @update:model-value="closeModal" max-width="900px" persistent>
    <v-card>
      <v-toolbar color="white" density="compact">
        <v-toolbar-title>
          <v-icon left class="mr-2">mdi-check-decagram-outline</v-icon>
          Revisar Indicadores
        </v-toolbar-title>
        <v-spacer></v-spacer>
        <v-btn icon @click="closeModal" :disabled="isLoading"><v-icon>mdi-close</v-icon></v-btn>
      </v-toolbar>

      <v-form @submit.prevent="handleSubmit">
        <v-card-text style="max-height: 80vh; overflow-y: auto;">
          <v-alert
            v-if="errorMessage"
            type="error"
            variant="tonal"
            class="mb-4"
            closable
            @click:close="errorMessage = ''"
          >
            {{ errorMessage }}
          </v-alert>
          
          <p class="text-body-2 mb-6">
            Ingresa el contexto pedagógico (RF, RA, AE) y los indicadores que deseas que la IA revise.
            La IA analizará la coherencia, estructura y alineamiento de cada indicador.
          </p>

          <v-row>
            <v-col cols="12" md="6">
              <v-text-field
                v-model="form.nombre_curso"
                label="Nombre del Curso (Opcional)"
                variant="outlined"
                density="compact"
                :disabled="isLoading"
              ></v-text-field>
            </v-col>
            <v-col cols="12" md="6">
              <v-select
                v-model="form.estructuraMEI"
                :items="estructuraMEIOptions"
                label="Estructura MEI"
                variant="outlined"
                density="compact"
                :rules="[v => !!v || 'La estructura MEI es requerida']"
                required
                :disabled="isLoading"
              ></v-select>
            </v-col>
          </v-row>
          
          <v-divider class="my-4"></v-divider>

          <div v-if="form.estructuraMEI === 'MEI-Actualizado'">
            <div class="d-flex justify-space-between align-center mb-2">
              <h3 class="text-h6">Resultados Formativos (RF)</h3>
              <v-btn color="primary" @click="addRF" :disabled="isLoading" size="small">Agregar RF</v-btn>
            </div>
            <v-sheet v-if="form.resultadosFormativos.length === 0" class="pa-4 text-center text-grey" border rounded>
              Agrega al menos un Resultado Formativo.
            </v-sheet>
            <div v-for="(rf, index) in form.resultadosFormativos" :key="`rf-${index}`" class="mb-4">
              <v-textarea
                v-model="rf.texto"
                :label="`Resultado Formativo ${index + 1}`"
                variant="outlined"
                rows="3"
                auto-grow
                clearable
                :rules="[v => !!v || 'El texto es requerido']"
                :disabled="isLoading"
              >
                <template v-slot:append-inner>
                  <v-btn 
                    v-if="form.resultadosFormativos.length > 1" 
                    icon="mdi-delete-outline" 
                    color="error"
                    variant="text" 
                    @click="removeRF(index)" 
                    :disabled="isLoading"
                    title="Eliminar RF"
                  ></v-btn>
                </template>
              </v-textarea>
            </div>

            <v-divider class="my-4"></v-divider>

            <div class="d-flex justify-space-between align-center mb-2">
              <h3 class="text-h6">Resultados de Aprendizaje (RA)</h3>
              <v-btn color="primary" @click="addRA_MEI_A" :disabled="isLoading" size="small">Agregar RA</v-btn>
            </div>
            <v-sheet v-if="form.resultadosAprendizaje.length === 0" class="pa-4 text-center text-grey" border rounded>
              Agrega al menos un Resultado de Aprendizaje.
            </v-sheet>
            <div v-for="(ra, index) in form.resultadosAprendizaje" :key="`ra-${index}`" class="mb-4">
              <v-card variant="outlined">
                <v-card-text>
                  <v-textarea
                    v-model="ra.texto"
                    :label="`Resultado de Aprendizaje ${index + 1}`"
                    variant="outlined"
                    rows="3"
                    auto-grow
                    clearable
                    :rules="[v => !!v || 'El texto es requerido']"
                    :disabled="isLoading"
                  >
                    <template v-slot:append-inner>
                      <v-btn 
                        v-if="form.resultadosAprendizaje.length > 1" 
                        icon="mdi-delete-outline" 
                        color="error"
                        variant="text" 
                        @click="removeRA_MEI_A(index)" 
                        :disabled="isLoading"
                        title="Eliminar RA"
                      ></v-btn>
                    </template>
                  </v-textarea>

                  <v-divider class="my-3"></v-divider>
                  <div class="d-flex justify-space-between align-center mb-3">
                    <span class="text-subtitle-1 font-weight-medium">Indicadores a Revisar</span>
                    <v-btn color="primary" @click="addIndicator(ra)" :disabled="isLoading" size="small" variant="tonal">
                      <v-icon left>mdi-plus</v-icon>
                      Agregar Indicador
                    </v-btn>
                  </div>
                  
                  <div v-for="(indicador, indIndex) in ra.indicadores" :key="indicador.id" class="d-flex align-center ga-2 mb-2">
                    <v-text-field
                      v-model="indicador.texto"
                      :label="`Indicador ${indIndex + 1}`"
                      variant="outlined"
                      density="compact"
                      :rules="[v => !!v || 'El indicador no puede estar vacío']"
                      :disabled="isLoading"
                      hide-details="auto"
                    ></v-text-field>
                    <v-btn
                      v-if="ra.indicadores.length > 1"
                      icon="mdi-delete-outline"
                      color="error"
                      variant="text"
                      @click="removeIndicator(ra, indIndex)"
                      :disabled="isLoading"
                      title="Eliminar Indicador"
                    ></v-btn>
                  </div>
                  </v-card-text>
              </v-card>
            </div>
          </div>

          <div v-if="form.estructuraMEI === 'MEI-Antiguo'">
            <div class="d-flex justify-space-between align-center mb-2">
              <h3 class="text-h6">Resultados de Aprendizaje (RA)</h3>
              <v-btn color="primary" @click="addRA_MEI_B" :disabled="isLoading" size="small">Agregar RA</v-btn>
            </div>
            <v-sheet v-if="form.resultadosAprendizaje.length === 0" class="pa-4 text-center text-grey" border rounded>
              Agrega al menos un Resultado de Aprendizaje.
            </v-sheet>
            <div v-for="(ra, index) in form.resultadosAprendizaje" :key="`ra-b-${index}`" class="mb-4">
              <v-textarea
                v-model="ra.texto"
                :label="`Resultado de Aprendizaje ${index + 1}`"
                variant="outlined"
                rows="3"
                auto-grow
                clearable
                :rules="[v => !!v || 'El texto es requerido']"
                :disabled="isLoading"
              >
                <template v-slot:append-inner>
                  <v-btn 
                    v-if="form.resultadosAprendizaje.length > 1" 
                    icon="mdi-delete-outline" 
                    color="error"
                    variant="text" 
                    @click="removeRA_MEI_B(index)" 
                    :disabled="isLoading"
                    title="Eliminar RA"
                  ></v-btn>
                </template>
              </v-textarea>
            </div>
            
            <v-divider class="my-4"></v-divider>
            
            <div class="d-flex justify-space-between align-center mb-2">
              <h3 class="text-h6">Aprendizajes Esperados (AE)</h3>
              <v-btn color="primary" @click="addAE" :disabled="isLoading" size="small">Agregar AE</v-btn>
            </div>
            <v-sheet v-if="form.aprendizajesEsperados.length === 0" class="pa-4 text-center text-grey" border rounded>
              Agrega al menos un Aprendizaje Esperado.
            </v-sheet>
            <div v-for="(ae, index) in form.aprendizajesEsperados" :key="`ae-${index}`" class="mb-4">
              <v-card variant="outlined">
                <v-card-text>
                  <v-textarea
                    v-model="ae.texto"
                    :label="`Aprendizaje Esperado ${index + 1}`"
                    variant="outlined"
                    rows="3"
                    auto-grow
                    clearable
                    :rules="[v => !!v || 'El texto es requerido']"
                    :disabled="isLoading"
                  >
                    <template v-slot:append-inner>
                      <v-btn 
                        v-if="form.aprendizajesEsperados.length > 1" 
                        icon="mdi-delete-outline" 
                        color="error"
                        variant="text" 
                        @click="removeAE(index)" 
                        :disabled="isLoading"
                        title="Eliminar AE"
                      ></v-btn>
                    </template>
                  </v-textarea>
                  
                  <v-divider class="my-3"></v-divider>
                  <div class="d-flex justify-space-between align-center mb-3">
                    <span class="text-subtitle-1 font-weight-medium">Indicadores a Revisar</span>
                    <v-btn color="primary" @click="addIndicator(ae)" :disabled="isLoading" size="small" variant="tonal">
                      <v-icon left>mdi-plus</v-icon>
                      Agregar Indicador
                    </v-btn>
                  </div>
                  
                  <div v-for="(indicador, indIndex) in ae.indicadores" :key="indicador.id" class="d-flex align-center ga-2 mb-2">
                    <v-text-field
                      v-model="indicador.texto"
                      :label="`Indicador ${indIndex + 1}`"
                      variant="outlined"
                      density="compact"
                      :rules="[v => !!v || 'El indicador no puede estar vacío']"
                      :disabled="isLoading"
                      hide-details="auto"
                    ></v-text-field>
                    <v-btn
                      v-if="ae.indicadores.length > 1"
                      icon="mdi-delete-outline"
                      color="error"
                      variant="text"
                      @click="removeIndicator(ae, indIndex)"
                      :disabled="isLoading"
                      title="Eliminar Indicador"
                    ></v-btn>
                  </div>
                  </v-card-text>
              </v-card>
            </div>
          </div>
        </v-card-text>

        <v-divider></v-divider>
        <v-card-actions class="pa-4">
          <v-spacer></v-spacer>
          <v-btn 
            color="primary" 
            variant="flat" 
            type="submit"
            :loading="isLoading"
            :disabled="!isFormValid || isLoading"
          >
            Revisar Indicadores
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue';
import { revisarIndicadores } from '@/services/apiService';

const props = defineProps({
  modelValue: Boolean
});
const emit = defineEmits(['update:modelValue', 'review-complete']);

const isLoading = ref(false);
const errorMessage = ref('');

// --- INICIO CAMBIO ESTRUCTURAL ---
const defaultForm = () => ({
  nombre_curso: '',
  estructuraMEI: 'MEI-Actualizado',
  resultadosFormativos: [{ id: 'RF-1', texto: '' }],
  resultadosAprendizaje: [{ 
    id: 'RA-1', 
    texto: '', 
    indicadores: [{ id: `IND-${Date.now()}`, texto: '' }] // Inicia con un campo de indicador
  }],
  aprendizajesEsperados: [{ 
    id: 'AE-1', 
    texto: '', 
    indicadores: [{ id: `IND-${Date.now()}`, texto: '' }] // Inicia con un campo de indicador
  }]
});
// --- FIN CAMBIO ESTRUCTURAL ---

const form = reactive(defaultForm());

const estructuraMEIOptions = [
  { title: 'Antiguo (RA-AE-IL)', value: 'MEI-Antiguo' },
  { title: 'Actualizado (RF-RA-ID)', value: 'MEI-Actualizado' },
];

// --- INICIO CAMBIO DE LÓGICA DE VALIDACIÓN ---
const isFormValid = computed(() => {
  if (isLoading.value) return false;
  if (!form.estructuraMEI) return false;
  
  if (form.estructuraMEI === 'MEI-Actualizado') {
    return form.resultadosFormativos.length > 0 && 
           form.resultadosFormativos.every(rf => rf.texto.trim() !== '') &&
           form.resultadosAprendizaje.length > 0 &&
           form.resultadosAprendizaje.every(ra => 
             ra.texto.trim() !== '' &&
             ra.indicadores.length > 0 && // Debe tener al menos un indicador
             ra.indicadores.every(ind => ind.texto.trim() !== '') // Ningún indicador debe estar vacío
           );
  }
  if (form.estructuraMEI === 'MEI-Antiguo') {
    return form.resultadosAprendizaje.length > 0 &&
           form.resultadosAprendizaje.every(ra => ra.texto.trim() !== '') &&
           form.aprendizajesEsperados.length > 0 &&
           form.aprendizajesEsperados.every(ae => 
             ae.texto.trim() !== '' &&
             ae.indicadores.length > 0 && // Debe tener al menos un indicador
             ae.indicadores.every(ind => ind.texto.trim() !== '') // Ningún indicador debe estar vacío
           );
  }
  return false;
});
// --- FIN CAMBIO DE LÓGICA DE VALIDACIÓN ---

function closeModal() {
  if (isLoading.value) return;
  emit('update:modelValue', false);
}

// Lógica de watch corregida (sin cambios respecto a la anterior)
watch(() => form.estructuraMEI, (newValue) => {
  const tempMEI = newValue; 
  Object.assign(form, defaultForm()); 
  form.estructuraMEI = tempMEI; 
});

// --- Lógica de formulario (RA/AE) ---
function addRF() { form.resultadosFormativos.push({ id: `RF-${Date.now()}`, texto: '' }); }
function removeRF(index) { form.resultadosFormativos.splice(index, 1); }

function addRA_MEI_A() { 
  form.resultadosAprendizaje.push({ 
    id: `RA-${Date.now()}`, 
    texto: '', 
    indicadores: [{ id: `IND-${Date.now()}`, texto: '' }] 
  }); 
}
function removeRA_MEI_A(index) { form.resultadosAprendizaje.splice(index, 1); }

function addRA_MEI_B() { form.resultadosAprendizaje.push({ id: `RA-${Date.now()}`, texto: '' }); }
function removeRA_MEI_B(index) { form.resultadosAprendizaje.splice(index, 1); }

function addAE() { 
  form.aprendizajesEsperados.push({ 
    id: `AE-${Date.now()}`, 
    texto: '', 
    indicadores: [{ id: `IND-${Date.now()}`, texto: '' }] 
  }); 
}
function removeAE(index) { form.aprendizajesEsperados.splice(index, 1); }

// --- INICIO NUEVAS FUNCIONES (INDICADORES) ---
/**
 * Añade un nuevo campo de indicador vacío al RA o AE especificado.
 * @param {object} ra_or_ae - El objeto RA o AE (que contiene el array 'indicadores')
 */
function addIndicator(ra_or_ae) {
  ra_or_ae.indicadores.push({ id: `IND-${Date.now()}`, texto: '' });
}

/**
 * Elimina un campo de indicador de un RA o AE.
 * @param {object} ra_or_ae - El objeto RA o AE
 * @param {number} indicatorIndex - El índice del indicador a eliminar
 */
function removeIndicator(ra_or_ae, indicatorIndex) {
  // Asegura que siempre quede al menos un campo
  if (ra_or_ae.indicadores.length > 1) {
    ra_or_ae.indicadores.splice(indicatorIndex, 1);
  }
}
// --- FIN NUEVAS FUNCIONES (INDICADORES) ---

// --- Lógica de Envío ---
async function handleSubmit() {
  if (!isFormValid.value || isLoading.value) return;

  isLoading.value = true;
  errorMessage.value = '';

  const payload = {
    nombre_curso: form.nombre_curso || 'Curso No Especificado',
    estructuraMEI: form.estructuraMEI,
    resultadosFormativos: [],
    resultadosAprendizaje: [],
    aprendizajesEsperados: []
  };

  // --- INICIO CAMBIO LÓGICA DE PAYLOAD ---
  if (form.estructuraMEI === 'MEI-Actualizado') {
    payload.resultadosFormativos = form.resultadosFormativos
      .filter(rf => rf.texto.trim() !== '')
      .map(rf => ({ id: rf.id, texto: rf.texto.trim() }));
    
    payload.resultadosAprendizaje = form.resultadosAprendizaje
      .filter(ra => ra.texto.trim() !== '')
      .map(ra => ({
        id: ra.id,
        texto: ra.texto.trim(),
        // Construye el array de strings que espera el workflow
        indicadores_a_revisar: ra.indicadores
          .map(ind => ind.texto.trim())
          .filter(t => t !== '')
      }));

  } else if (form.estructuraMEI === 'MEI-Antiguo') {
    payload.resultadosAprendizaje = form.resultadosAprendizaje
      .filter(ra => ra.texto.trim() !== '')
      .map(ra => ({ id: ra.id, texto: ra.texto.trim() }));
    
    payload.aprendizajesEsperados = form.aprendizajesEsperados
      .filter(ae => ae.texto.trim() !== '')
      .map(ae => ({
        id: ae.id,
        texto: ae.texto.trim(),
        // Construye el array de strings que espera el workflow
        indicadores_a_revisar: ae.indicadores
          .map(ind => ind.texto.trim())
          .filter(t => t !== '')
      }));
  }
  // --- FIN CAMBIO LÓGICA DE PAYLOAD ---

  try {
    const reviewResult = await revisarIndicadores(payload); 

    const resultForDisplay = {
      input_data: payload,
      output_data: reviewResult, 
      created_at: new Date().toISOString(),
      nombre_generacion: `Revisión del ${new Date().toLocaleString()}`
    };

    emit('review-complete', resultForDisplay);
    closeModal();
    Object.assign(form, defaultForm());

  } catch (error) {
    console.error('Error al revisar indicadores:', error);
    errorMessage.value = `Error al contactar al servicio de revisión: ${error.message || 'Error desconocido'}`;
  } finally {
    isLoading.value = false;
  }
}
</script>
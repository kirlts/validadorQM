<template>
  <v-dialog v-model="dialog" max-width="900px">
    <v-card>
      <v-card-title>
        <span class="text-h5">Generar Indicadores Pedagógicos</span>
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-form ref="form" v-model="valid">
            <v-select
              v-model="formData.estructuraMEI"
              :items="estructuras"
              label="Estructura MEI"
              item-title="text"
              item-value="value"
              required
              :rules="[v => !!v || 'La estructura es requerida']"
              class="mb-4"
              variant="outlined"
            ></v-select>

            <v-text-field
              v-model="formData.nombre_curso"
              label="Nombre del Curso"
              required
              :rules="[v => !!v && v.trim() !== '' || 'El nombre del curso es requerido']"
              class="mb-4"
              variant="outlined"
              autofocus
            ></v-text-field>
            
            <v-text-field
              v-model.number="formData.trimestre"
              label="Trimestre (Opcional)"
              type="number"
              :rules="[
                v => v === null || v === '' || (Number.isInteger(Number(v)) && Number(v) > 0) || 'Debe ser un número positivo'
              ]"
              clearable
              class="mb-4"
              variant="outlined"
            ></v-text-field>
            <div v-if="formData.estructuraMEI === 'MEI-Actualizado'">
              <div class="d-flex justify-end mb-4">
                <v-btn 
                  color="secondary" 
                  variant="outlined" 
                  size="small"
                  @click="fillWithExample"
                  :disabled="loading"
                >
                  <v-icon left>mdi-file-document-edit-outline</v-icon>
                  Rellenar con ejemplo
                </v-btn>
              </div>
              <div v-for="(rf, index) in formData.resultadosFormativos" :key="rf.id" class="d-flex align-start mb-2">
                <v-textarea
                  v-model="rf.texto"
                  :label="`Resultado Formativo (RF) ${index + 1}`"
                  required
                  :rules="[v => !!v || 'El RF es requerido']"
                  rows="2"
                  auto-grow
                  class="flex-grow-1"
                  variant="outlined"
                ></v-textarea>
                <v-btn v-if="formData.resultadosFormativos.length > 1" icon="mdi-close" variant="text" @click="removeRF(index)" class="ml-2 mt-2"></v-btn>
              </div>
              <v-btn size="small" variant="tonal" @click="addRF" class="mb-6"><v-icon left>mdi-plus</v-icon> Agregar RF</v-btn>

              <div v-for="(ra, index) in formData.resultadosAprendizaje" :key="ra.id" class="mb-4 pa-4 border rounded">
                <div class="d-flex align-start">
                  <v-textarea
                    v-model="ra.texto"
                    :label="`Resultado de Aprendizaje (RA) ${index + 1}`"
                    required
                    :rules="[v => !!v || 'El RA es requerido']"
                    rows="2"
                    auto-grow
                    class="flex-grow-1"
                    variant="outlined"
                  ></v-textarea>
                  <v-btn v-if="formData.resultadosAprendizaje.length > 1" icon="mdi-close" variant="text" @click="removeRA(index)" class="ml-2 mt-2"></v-btn>
                </div>
                <v-textarea v-model="ra.contenido" label="Contenido Principal (Opcional)" rows="1" auto-grow variant="outlined"></v-textarea>
                <v-textarea v-model="ra.metodologia" label="Metodología Propuesta (Opcional)" rows="1" auto-grow variant="outlined"></v-textarea>
              </div>
              <v-btn size="small" variant="tonal" @click="addRA_Updated" class="mb-4"><v-icon left>mdi-plus</v-icon> Agregar RA</v-btn>
            </div>

            <div v-if="formData.estructuraMEI === 'MEI-Antiguo'">
              <div v-for="(ra, index) in formData.resultadosAprendizaje" :key="ra.id" class="d-flex align-start mb-2">
                <v-textarea
                  v-model="ra.texto"
                  :label="`Resultado de Aprendizaje (RA) ${index + 1}`"
                  required
                  :rules="[v => !!v || 'El RA es requerido']"
                  rows="2"
                  auto-grow
                  class="flex-grow-1"
                  variant="outlined"
                ></v-textarea>
                <v-btn v-if="formData.resultadosAprendizaje.length > 1" icon="mdi-close" variant="text" @click="removeRA(index)" class="ml-2 mt-2"></v-btn>
              </div>
              <v-btn size="small" variant="tonal" @click="addRA_Old" class="mb-6"><v-icon left>mdi-plus</v-icon> Agregar RA</v-btn>

              <div v-for="(ae, index) in formData.aprendizajesEsperados" :key="ae.id" class="d-flex align-start mb-2">
                <v-textarea
                  v-model="ae.texto"
                  :label="`Aprendizaje Esperado (AE) ${index + 1}`"
                  required
                  :rules="[v => !!v || 'El AE es requerido']"
                  rows="2"
                  auto-grow
                  class="flex-grow-1"
                  variant="outlined"
                ></v-textarea>
                <v-btn v-if="formData.aprendizajesEsperados.length > 1" icon="mdi-close" variant="text" @click="removeAE(index)" class="ml-2 mt-2"></v-btn>
              </div>
              <v-btn size="small" variant="tonal" @click="addAE"><v-icon left>mdi-plus</v-icon> Agregar AE</v-btn>
            </div>
            
            <v-alert v-if="error" type="error" dense class="mt-4">{{ error }}</v-alert>

          </v-form>
        </v-container>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="blue-darken-1" text @click="closeDialog" :disabled="loading">
          Cancelar
        </v-btn>
        <v-btn color="blue-darken-1" :loading="loading" :disabled="!valid" @click="submit">
          Generar Indicadores
        </v-btn>
      </v-card-actions>
      <v-progress-linear v-if="loading" indeterminate></v-progress-linear>
    </v-card>
  </v-dialog>
</template>

<script setup>
import { ref, watch } from 'vue';
import { generateIndicators } from '@/services/apiService';

const props = defineProps({
  modelValue: Boolean,
});
const emit = defineEmits(['update:modelValue', 'generation-complete']);

const dialog = ref(props.modelValue);
const form = ref(null);
const valid = ref(false);
const loading = ref(false);
const error = ref(null);

const estructuras = [
  { text: 'MEI Actualizado (RF - RA - ID)', value: 'MEI-Actualizado' },
  { text: 'MEI Antiguo (RA - AE - IL)', value: 'MEI-Antiguo' },
];

const getInitialFormData = () => ({
  estructuraMEI: 'MEI-Actualizado',
  nombre_curso: '', // <--- CAMPO AÑADIDO
  trimestre: null, // <--- CAMPO AÑADIDO
  resultadosFormativos: [{ id: Date.now(), texto: '' }],
  resultadosAprendizaje: [{ id: Date.now() + 1, texto: '', contenido: '', metodologia: '' }],
  aprendizajesEsperados: [{ id: Date.now() + 2, texto: '' }],
});

const formData = ref(getInitialFormData());

watch(() => props.modelValue, (newValue) => {
  dialog.value = newValue;
});

watch(dialog, (newValue) => {
  if (!newValue) {
    emit('update:modelValue', false);
    resetForm();
  }
});

watch(() => formData.value.estructuraMEI, () => {
  // Mantenemos los campos de curso y trimestre, pero reseteamos los arrays
  const nombreCurso = formData.value.nombre_curso;
  const trimestre = formData.value.trimestre;
  
  formData.value.resultadosFormativos = [{ id: Date.now(), texto: '' }];
  formData.value.resultadosAprendizaje = [{ id: Date.now() + 1, texto: '', contenido: '', metodologia: '' }];
  formData.value.aprendizajesEsperados = [{ id: Date.now() + 2, texto: '' }];

  // Restauramos los valores
  formData.value.nombre_curso = nombreCurso;
  formData.value.trimestre = trimestre;
});

// --- Funciones para agregar elementos ---
const addRF = () => formData.value.resultadosFormativos.push({ id: Date.now(), texto: '' });
const addRA_Updated = () => formData.value.resultadosAprendizaje.push({ id: Date.now(), texto: '', contenido: '', metodologia: '' });
const addRA_Old = () => formData.value.resultadosAprendizaje.push({ id: Date.now(), texto: '' });
const addAE = () => formData.value.aprendizajesEsperados.push({ id: Date.now(), texto: '' });

// --- Función para rellenar con ejemplo (solo MEI-Actualizado) ---
const fillWithExample = () => {
  if (formData.value.estructuraMEI !== 'MEI-Actualizado') return;
  
  // Datos de ejemplo de la sección GENERACION
  formData.value.nombre_curso = 'COMERCIO INTERNACIONAL';
  formData.value.resultadosFormativos = [
    { 
      id: Date.now(), 
      texto: 'Evaluar el entorno y las tendencias del mercado global, identificando riesgos, oportunidades y amenazas, para la toma de decisiones estratégicas, considerando el comportamiento e influencia de los actores clave que participan en él y el marco del sistema internacional que los regula.' 
    },
    { 
      id: Date.now() + 1, 
      texto: 'Formular estrategias de negocios internacionales, integrando herramientas analíticas, fundamentos y normativas del comercio exterior, para enfrentar desafíos propios de la profesión en entornos globales dinámicos.' 
    }
  ];
  formData.value.resultadosAprendizaje = [
    { 
      id: Date.now() + 2, 
      texto: 'Analizar las bases teóricas y normativas que sustentan el comercio internacional y la inserción de Chile en los mercados globales, considerando las principales teorías del intercambio comercial y el funcionamiento del sistema multilateral de comercio.',
      contenido: '',
      metodologia: ''
    }
  ];
};

// --- Funciones para remover elementos ---
const removeRF = (index) => formData.value.resultadosFormativos.splice(index, 1);
const removeRA = (index) => formData.value.resultadosAprendizaje.splice(index, 1);
const removeAE = (index) => formData.value.aprendizajesEsperados.splice(index, 1);

function closeDialog() {
  dialog.value = false;
}

function resetForm() {
  if (form.value) form.value.resetValidation();
  formData.value = getInitialFormData();
  error.value = null;
}

async function submit() {
  const { valid } = await form.value.validate();
  if (!valid) return;

  loading.value = true;
  error.value = null;

  try {
    const payload = buildPayload();
    const result = await generateIndicators(payload);
    emit('generation-complete', result);
    closeDialog();
  } catch (err) {
    error.value = err.message || 'Ocurrió un error inesperado al generar los indicadores.';
  } finally {
    loading.value = false;
  }
}

function buildPayload() {
  const data = formData.value;
  
  // --- PAYLOAD ACTUALIZADO ---
  // Se incluyen los nuevos campos en la raíz del payload
  const payload = { 
    estructuraMEI: data.estructuraMEI,
    nombre_curso: data.nombre_curso.trim(),
    trimestre: (data.trimestre && Number(data.trimestre)) ? Number(data.trimestre) : undefined
  };

  if (data.estructuraMEI === 'MEI-Actualizado') {
    // Filtra los RFs vacíos y mapea a la estructura esperada por el workflow
    payload.resultadosFormativos = data.resultadosFormativos
      .filter(rf => rf.texto.trim() !== '')
      .map((rf, index) => ({ id: `RF-${index + 1}`, texto: rf.texto.trim() }));
      
    // Filtra los RAs vacíos y mapea, asegurando que los opcionales no se envíen si están vacíos
    payload.resultadosAprendizaje = data.resultadosAprendizaje
      .filter(ra => ra.texto.trim() !== '')
      .map((ra, index) => ({
        id: `RA-${index + 1}`,
        tributaA: payload.resultadosFormativos.map(rf => rf.id), // Asume que tributa a todos los RFs ingresados
        texto: ra.texto.trim(),
        contenido: ra.contenido.trim() || undefined,
        metodologia: ra.metodologia.trim() || undefined,
      }));
  } else { // MEI-Antiguo
    payload.resultadosAprendizaje = data.resultadosAprendizaje
      .filter(ra => ra.texto.trim() !== '')
      .map((ra, index) => ({ id: `RA-${index + 1}`, texto: ra.texto.trim() }));
      
    payload.aprendizajesEsperados = data.aprendizajesEsperados
      .filter(ae => ae.texto.trim() !== '')
      .map((ae, index) => ({
        id: `AE-${index + 1}`,
        tributaA: payload.resultadosAprendizaje.map(ra => ra.id), // Asume que tributa a todos los RAs
        texto: ae.texto.trim()
      }));
  }
  return payload;
}
</script>
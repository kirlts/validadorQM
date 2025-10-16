<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">

        <!-- SECCIÓN DE HERRAMIENTAS DE GENERACIÓN -->
        <v-card class="mb-6">
          <v-card-title>Herramientas de Generación</v-card-title>
          <v-card-text>
            Utiliza el asistente de IA para generar componentes pedagógicos de alta calidad basados en las directrices de UNAB.
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" @click="openGeneratorModal">
              <v-icon left>mdi-auto-fix</v-icon>
              Generar Indicadores Pedagógicos
            </v-btn>
          </v-card-actions>
        </v-card>

        <!-- SECCIÓN: MIS GENERACIONES GUARDADAS -->
        <v-card class="mb-6">
          <v-card-title class="d-flex align-center">
            <span class="headline">Mis Generaciones Guardadas</span>
            <v-spacer></v-spacer>
            <v-btn icon variant="text" @click="fetchGenerations" :loading="isGenerationsLoading">
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-subtitle>
            Revisa las generaciones de indicadores que has creado anteriormente.
          </v-card-subtitle>
          
          <v-progress-linear v-if="isGenerationsLoading && generations.length === 0" indeterminate color="primary"></v-progress-linear>

          <v-list v-else lines="one">
            <template v-if="generations.length > 0">
              <v-list-item v-for="gen in generations" :key="gen.id">
                <template v-slot:prepend>
                  <v-avatar color="primary">
                    <v-icon>mdi-text-box-check-outline</v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>{{ gen.nombre_generacion || `Generación del ${new Date(gen.created_at).toLocaleString()}` }}</v-list-item-title>
                <v-list-item-subtitle>{{ gen.input_data.estructuraMEI }}</v-list-item-subtitle>
                
                <template v-slot:append>
                  <v-btn icon="mdi-eye" variant="text" @click="viewGeneration(gen.output_data)" title="Visualizar Resultado"></v-btn>
                  <v-btn icon="mdi-pencil" variant="text" @click="promptRename(gen)" title="Renombrar Generación"></v-btn>
                  <v-btn icon="mdi-delete" variant="text" @click="promptDeleteGeneration(gen)" title="Eliminar Generación"></v-btn>
                </template>
              </v-list-item>
            </template>
            <v-card-text v-else class="text-center py-4">
              No has guardado ninguna generación todavía.
            </v-card-text>
          </v-list>
        </v-card>

        <!-- SECCIÓN DE DISEÑOS INSTRUCCIONALES -->
        <v-card>
          <v-card-title class="d-flex align-center">
            <span class="headline">Mis Diseños Instruccionales</span>
            <v-spacer></v-spacer>
            <v-btn icon variant="text" @click="handleRefresh" :loading="isLoading" :disabled="isActionInProgress">
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-subtitle>
            Gestiona tus DIs y su estado de procesamiento.
          </v-card-subtitle>
          
          <v-progress-linear v-if="isLoading && designs.length === 0" indeterminate color="primary"></v-progress-linear>
          
          <v-list v-else lines="two">
            <template v-if="designs.length > 0">
              <v-list-item v-for="design in designs" :key="design.id_di" @click="viewDetails(design)" link>
                <template v-slot:prepend>
                  <v-avatar :color="getStatusColor(design)">
                      <v-progress-circular v-if="isProcessing(design)" indeterminate size="24" color="white"></v-progress-circular>
                      <v-icon v-else>{{ getStatusIcon(design) }}</v-icon>
                  </v-avatar>
                </template>

                <v-list-item-title>{{ design.nombre_archivo }}</v-list-item-title>
                
                <v-list-item-subtitle>{{ getStatusText(design) }}</v-list-item-subtitle>

                <template v-slot:append>
                  <div class="d-flex align-center">
                    <v-btn icon="mdi-eye" variant="text" @click.stop="handleView(design)" title="Visualizar Archivo"></v-btn>
                    <v-btn icon="mdi-download" variant="text" @click.stop="handleDownload(design)" title="Descargar Archivo Original" :disabled="isProcessing(design)"></v-btn>
                    <v-btn icon="mdi-delete" variant="text" @click.stop="promptDelete(design)" title="Eliminar DI" :loading="isDeleting === design.id_di" :disabled="isActionInProgress"></v-btn>
                  </div>
                </template>
              </v-list-item>
            </template>
            <v-card-text v-else class="text-center py-4">
              No has subido ningún Diseño Instruccional todavía.
            </v-card-text>
          </v-list>

          <v-divider></v-divider>

          <v-card-actions class="pa-4">
            <v-select
              v-model="selectedEstructuraMEI"
              :items="estructuraMEIOptions"
              label="Estructura MEI"
              variant="outlined"
              density="compact"
              class="mr-4"
              hide-details
              :disabled="isActionInProgress"
              style="max-width: 300px;"
            ></v-select>
            <v-spacer></v-spacer>
            <input type="file" id="fileInput" @change="handleFileUpload" hidden accept=".doc,.docx">
            <v-btn color="primary" variant="flat" @click="triggerFileInput" :loading="isUploading" :disabled="isActionInProgress || !selectedEstructuraMEI">
              <v-icon left>mdi-upload</v-icon>
              Subir Nuevo DI
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
    
    <!-- DIÁLOGO DE ELIMINACIÓN (GENERALIZADO) -->
    <v-dialog v-model="deleteDialog.show" max-width="500px" persistent>
      <v-card>
        <v-card-title class="headline">Confirmar Eliminación</v-card-title>
        <v-card-text>¿Estás seguro de que quieres eliminar <strong>{{ deleteDialog.itemName }}</strong>?</v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="deleteDialog.show = false">Cancelar</v-btn>
          <v-btn color="red-darken-1" variant="tonal" @click="confirmDelete">Eliminar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    
    <!-- DIÁLOGO DE VISUALIZACIÓN DE DI (EXISTENTE) -->
    <v-dialog v-model="viewerDialog.show" fullscreen scrollable>
       <v-card>
        <v-toolbar color="primary" dark>
          <v-toolbar-title>{{ viewerDialog.itemName }}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn icon @click="viewerDialog.show = false"><v-icon>mdi-close</v-icon></v-btn>
        </v-toolbar>
        <v-card-text class="pa-0" style="height: calc(100vh - 64px);">
          <div v-if="!viewerDialog.url" class="d-flex justify-center align-center h-100">
            <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
          </div>
          <iframe v-else :src="viewerDialog.url" width="100%" height="100%" frameborder="0"></iframe>
        </v-card-text>
      </v-card>
    </v-dialog>

    <!-- MODAL DE GENERACIÓN (NUEVO) -->
    <GeneratorModal
      v-model="isGeneratorModalOpen"
      @generation-complete="handleGenerationComplete"
    />

    <!-- MODAL PARA MOSTRAR RESULTADOS DE GENERACIÓN -->
    <v-dialog v-model="isResultModalOpen" max-width="900px">
        <v-card>
            <v-toolbar color="white" density="compact">
              <v-toolbar-title class="text-h6">Indicadores Generados</v-toolbar-title>
              <v-spacer></v-spacer>
              <v-btn icon @click="isResultModalOpen = false"><v-icon>mdi-close</v-icon></v-btn>
            </v-toolbar>
            <v-divider></v-divider>
            <v-card-text style="max-height: 70vh; overflow-y: auto;">
                <div v-if="generationResult">
                   <div v-if="generationResult.estructuraMEI === 'MEI-Actualizado' && generationResult.resultadosFormativos && generationResult.resultadosFormativos.length > 0">
                       <h3 class="text-subtitle-1 font-weight-bold mb-2">Resultados Formativos de Contexto:</h3>
                       <div v-for="(rf, rfIndex) in generationResult.resultadosFormativos" :key="rf.id" class="mb-3">
                           <p class="bg-blue-grey-lighten-5 pa-3 rounded"><strong>RF {{ rfIndex + 1 }}:</strong> {{ rf.texto }}</p>
                       </div>
                       <v-divider class="mb-4"></v-divider>
                   </div>
                   <div v-for="(item, index) in (generationResult.analisisResultadosAprendizaje || generationResult.analisisAprendizajesEsperados)" :key="index" class="mb-6">
                        <h3 class="text-h6 mb-2">
                            {{ generationResult.estructuraMEI === 'MEI-Actualizado' ? `Para el Resultado de Aprendizaje ${index + 1}:` : `Para el Aprendizaje Esperado ${index + 1}:`}}
                        </h3>
                        <p class="font-italic mb-3 bg-grey-lighten-4 pa-3 rounded">{{ item.texto }}</p>
                        <v-expansion-panels>
                            <v-expansion-panel v-for="(indicador, i) in item.indicadoresGenerados" :key="i">
                                <v-expansion-panel-title>
                                    <v-icon left class="mr-2" color="primary">mdi-lightbulb-on-outline</v-icon>
                                    <span class="font-weight-bold mr-2">{{ generationResult.estructuraMEI === 'MEI-Actualizado' ? 'ID' : 'IL' }}{{ index + 1 }}.{{ i + 1 }}:</span>
                                    <span>{{ indicador.indicador }}</span>
                                </v-expansion-panel-title>
                                <v-expansion-panel-text>
                                    <v-list-item class="pa-2">
                                        <v-list-item-title class="font-weight-bold">Verbo:</v-list-item-title>
                                        <v-list-item-subtitle>{{ indicador.verbo }}</v-list-item-subtitle>
                                    </v-list-item>
                                    <v-divider></v-divider>
                                     <v-list-item class="pa-2">
                                        <v-list-item-title class="font-weight-bold">Justificación Semántica:</v-list-item-title>
                                        <v-list-item-subtitle class="text-wrap">{{ indicador.justificacionSemantica }}</v-list-item-subtitle>
                                    </v-list-item>
                                    <v-divider></v-divider>
                                     <v-list-item class="pa-2">
                                        <v-list-item-title class="font-weight-bold">Justificación Taxonómica:</v-list-item-title>
                                        <v-list-item-subtitle class="text-wrap">{{ indicador.justificacionTaxonomica }}</v-list-item-subtitle>
                                    </v-list-item>
                                    <v-divider></v-divider>
                                     <v-list-item class="pa-2">
                                        <v-list-item-title class="font-weight-bold">Justificación Sintáctica:</v-list-item-title>
                                        <v-list-item-subtitle class="text-wrap">{{ indicador.justificacionSintactica }}</v-list-item-subtitle>
                                    </v-list-item>
                                </v-expansion-panel-text>
                            </v-expansion-panel>
                        </v-expansion-panels>
                   </div>
                </div>
            </v-card-text>
        </v-card>
    </v-dialog>

    <!-- DIÁLOGO PARA RENOMBRAR GENERACIÓN -->
    <v-dialog v-model="renameDialog.show" max-width="500px" persistent>
      <v-card>
        <v-card-title class="headline">Renombrar Generación</v-card-title>
        <v-card-text>
          <p class="mb-4">Ingresa un nuevo nombre para: <strong>{{ renameDialog.currentName }}</strong></p>
          <v-text-field
            v-model="renameDialog.newName"
            label="Nuevo nombre"
            variant="outlined"
            autofocus
            :rules="[v => !!v && v.trim() !== '' || 'El nombre no puede estar vacío']"
            @keyup.enter="confirmRename"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="renameDialog.show = false" :disabled="isRenaming">Cancelar</v-btn>
          <v-btn color="primary" variant="flat" @click="confirmRename" :loading="isRenaming">Guardar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAppStore } from '@/stores/appStore';
import { storeToRefs } from 'pinia';
import { uploadDi, getDownloadUrl, deleteDi, getGenerations, deleteGeneration, renameGeneration } from '@/services/apiService';
import GeneratorModal from '@/components/GeneratorModal.vue';

const router = useRouter();
const appStore = useAppStore();
const { designs, isLoading } = storeToRefs(appStore);

// --- Estado para DIs ---
const isUploading = ref(false);
const isDeleting = ref(null);
const selectedEstructuraMEI = ref('MEI-Antiguo'); 
const deleteDialog = reactive({ show: false, itemId: null, itemName: '', type: null });
const viewerDialog = reactive({ show: false, url: '', itemName: '' });
const estructuraMEIOptions = [
  { title: 'Antiguo (RA-AE-IL)', value: 'MEI-Antiguo' },
  { title: 'Actualizado (RF-RA-ID)', value: 'MEI-Actualizado' },
];

// --- Estado para Generaciones ---
const isGeneratorModalOpen = ref(false);
const isResultModalOpen = ref(false);
const generationResult = ref(null);
const generations = ref([]);
const isGenerationsLoading = ref(false);
const isRenaming = ref(false);
const renameDialog = reactive({ show: false, itemId: null, currentName: '', newName: '' });

const isActionInProgress = computed(() => isUploading.value || !!isDeleting.value || isGenerationsLoading.value || isRenaming.value);

onMounted(async () => {
  await fetchGenerations();
});

// --- Lógica de DIs (Completa) ---
const isProcessing = (design) => design.proceso_actual?.estado === 'processing';

const getStatusIcon = (design) => {
    const proceso = design.proceso_actual;
    if (proceso?.nombre === 'consulta') {
        return design.analisis_alineamiento ? 'mdi-check-circle' : 'mdi-file-question';
    }
    const estado = proceso?.estado;
    if (estado === 'success') return 'mdi-check-circle';
    if (estado === 'error') return 'mdi-alert-circle';
    return 'mdi-file-question';
};

const getStatusColor = (design) => {
    const proceso = design.proceso_actual;
    if (proceso?.nombre === 'consulta') {
        return design.analisis_alineamiento ? 'success' : 'grey';
    }
    const estado = proceso?.estado;
    if (estado === 'success') return 'success';
    if (estado === 'error') return 'error';
    if (estado === 'processing') return 'blue-grey';
    return 'grey';
};

const getStatusText = (design) => {
    const proceso = design.proceso_actual;
    const createdAt = design.created_at;
    const createdText = `Subido: ${new Date(createdAt).toLocaleDateString()}`;

    const estructuraMEIMap = {
        'MEI-Antiguo': 'MEI Antiguo (RA-AE-IL)',
        'MEI-Actualizado': 'MEI Actualizado (RF-RA-ID)'
    };
    const estructuraMEILabel = design.estructura_mei ? estructuraMEIMap[design.estructura_mei] : 'No definida';

    if (proceso?.nombre === 'consulta') {
        if (design.analisis_alineamiento) {
            return `Análisis de 'analisis_alineamiento' completado. ${createdText}`;
        }
        return `Estructura: ${estructuraMEILabel}. ${createdText}`;
    }

    if (!proceso || !proceso.estado || proceso.estado === 'pendiente') {
        return `Estructura: ${estructuraMEILabel}. ${createdText}`;
    }

    switch (proceso.estado) {
        case 'processing':
            return `Procesando: ${proceso.nombre}...`;
        case 'success':
            if (proceso.nombre === 'analisis_alineamiento') {
              return `Análisis de '${proceso.nombre}' completado. ${createdText}`;
            }
            return `Estructura: ${estructuraMEILabel}. ${createdText}`;
        case 'error':
            const errorMsg = proceso.error_detalle || 'Error desconocido.';
            return `Error en '${proceso.nombre}': ${errorMsg}`;
        default:
            return `Estado desconocido. ${createdText}`;
    }
};

function handleRefresh() {
  appStore.fetchDesigns();
}

function viewDetails(design) {
    if (isProcessing(design)) {
      return; 
    }
    router.push({ name: 'detail', params: { id: design.id_di } });
}

function triggerFileInput() { document.getElementById('fileInput').click(); }

async function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file || !selectedEstructuraMEI.value) return;

  isUploading.value = true;
  try {
    await uploadDi(file, selectedEstructuraMEI.value);
  } catch (error) {
    console.error("Error al subir:", error);
  } finally {
    isUploading.value = false;
    event.target.value = '';
    selectedEstructuraMEI.value = 'MEI-Antiguo';
  }
}

async function handleView(design) {
  viewerDialog.itemName = design.nombre_archivo;
  viewerDialog.url = '';
  viewerDialog.show = true;
  try {
    const response = await getDownloadUrl(design.id_di);
    viewerDialog.url = `https://docs.google.com/gview?url=${encodeURIComponent(response.signedURL)}&embedded=true`;
  } catch (error) {
    console.error("Error al obtener la URL de visualización:", error);
    viewerDialog.show = false;
  }
}

async function handleDownload(design) {
    try {
        const { signedURL } = await getDownloadUrl(design.id_di);
        window.open(signedURL, '_blank');
    } catch (error) {
        console.error("Error al obtener enlace de descarga:", error);
    }
}

// --- Lógica para Generaciones (Completa) ---
async function fetchGenerations() {
  isGenerationsLoading.value = true;
  try {
    generations.value = await getGenerations();
  } catch (error) {
    console.error("Error al obtener generaciones:", error);
  } finally {
    isGenerationsLoading.value = false;
  }
}

function viewGeneration(outputData) {
  generationResult.value = outputData;
  isResultModalOpen.value = true;
}

function openGeneratorModal() {
  isGeneratorModalOpen.value = true;
}

async function handleGenerationComplete(result) {
  generationResult.value = result;
  isResultModalOpen.value = true;
  await fetchGenerations();
}

function promptRename(gen) {
  renameDialog.itemId = gen.id;
  renameDialog.currentName = gen.nombre_generacion || `Generación del ${new Date(gen.created_at).toLocaleString()}`;
  renameDialog.newName = gen.nombre_generacion || '';
  renameDialog.show = true;
}

async function confirmRename() {
  if (!renameDialog.newName || renameDialog.newName.trim() === '') return;
  isRenaming.value = true;
  try {
    await renameGeneration(renameDialog.itemId, renameDialog.newName.trim());
    await fetchGenerations();
  } catch (error) {
    console.error("Error al renombrar:", error);
  } finally {
    isRenaming.value = false;
    renameDialog.show = false;
  }
}

// --- Lógica de Eliminación (Generalizada y Completa) ---
function promptDelete(design) {
  deleteDialog.itemId = design.id_di;
  deleteDialog.itemName = design.nombre_archivo;
  deleteDialog.type = 'di';
  deleteDialog.show = true;
}

function promptDeleteGeneration(gen) {
  deleteDialog.itemId = gen.id;
  deleteDialog.itemName = gen.nombre_generacion || `Generación del ${new Date(gen.created_at).toLocaleString()}`;
  deleteDialog.type = 'generation';
  deleteDialog.show = true;
}

async function confirmDelete() {
  const id = deleteDialog.itemId;
  const type = deleteDialog.type;
  if (!id) return;

  isDeleting.value = id;
  try {
    if (type === 'di') {
      await deleteDi(id);
    } else if (type === 'generation') {
      await deleteGeneration(id);
      await fetchGenerations();
    }
  } catch (error) {
    console.error("Error al eliminar:", error);
  } finally {
    isDeleting.value = null;
    deleteDialog.show = false;
  }
}
</script>
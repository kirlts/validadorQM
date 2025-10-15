<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">
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
    
    <!-- CORRECCIÓN: Contenido del diálogo de eliminación reinsertado -->
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
    
    <!-- CORRECCIÓN: Contenido del diálogo de visualización reinsertado -->
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
  </v-container>
</template>

<script setup>
// El script está correcto y no necesita cambios.
import { ref, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAppStore } from '@/stores/appStore';
import { storeToRefs } from 'pinia';
import { uploadDi, getDownloadUrl, deleteDi } from '@/services/apiService';

const router = useRouter();
const appStore = useAppStore();
const { designs, isLoading } = storeToRefs(appStore);

const isUploading = ref(false);
const isDeleting = ref(null);
const selectedEstructuraMEI = ref('MEI-Antiguo'); 
const deleteDialog = reactive({ show: false, itemId: null, itemName: '' });
const viewerDialog = reactive({ show: false, url: '', itemName: '' });

const estructuraMEIOptions = [
  { title: 'Antiguo (RA-AE-IL)', value: 'MEI-Antiguo' },
  { title: 'Actualizado (RF-RA-ID)', value: 'MEI-Actualizado' },
];

const isActionInProgress = computed(() => isUploading.value || !!isDeleting.value);

const isProcessing = (design) => design.proceso_actual?.estado === 'processing';

const getStatusIcon = (design) => {
    const proceso = design.proceso_actual;
    // Si el proceso es una consulta, mostramos el ícono del estado anterior (éxito o pendiente)
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
    // Si el proceso es una consulta, mostramos el color del estado anterior
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

    // ** LÓGICA CLAVE: Si el proceso actual es una 'consulta', lo ignoramos y mostramos el último estado principal. **
    if (proceso?.nombre === 'consulta') {
        if (design.analisis_alineamiento) {
            return `Análisis de 'analisis_alineamiento' completado. ${createdText}`;
        }
        return `Estructura: ${estructuraMEILabel}. ${createdText}`;
    }

    // Si NO es una consulta, se aplica la lógica original para mostrar el estado de procesos importantes.
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
            return `Estructura: ${estructuraMEILabel}. ${createdText}`; // Estado por defecto post-ingesta
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

function promptDelete(design) {
  deleteDialog.itemId = design.id_di;
  deleteDialog.itemName = design.nombre_archivo;
  deleteDialog.show = true;
}

async function confirmDelete() {
  const diId = deleteDialog.itemId;
  if (!diId) return;
  isDeleting.value = diId;
  try {
    await deleteDi(diId);
  } catch (error) {
    console.error("Error al eliminar:", error);
  } finally {
    isDeleting.value = null;
    deleteDialog.show = false;
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
</script>
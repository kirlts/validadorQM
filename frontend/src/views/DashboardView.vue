// frontend/src/views/DashboardView.vue

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

          <v-card-text>
            <v-alert
              v-if="notification.message"
              :type="notification.type"
              variant="tonal"
              closable
              @click:close="clearNotification"
              class="mb-4"
            >
              <span v-html="notification.message"></span>
            </v-alert>
          </v-card-text>

          <v-progress-linear v-if="isLoading" indeterminate color="primary"></v-progress-linear>

          <v-list v-if="!isLoading" lines="two">
            <template v-if="designs.length > 0">
              <v-list-item
                v-for="design in designs"
                :key="design.id_di"
                @click="viewDetails(design)"
                link
              >
                <template v-slot:prepend>
                  <v-avatar :color="getStatusColor(design)">
                     <v-progress-circular 
                      v-if="isProcessing(design)" 
                      indeterminate 
                      size="24"
                    ></v-progress-circular>
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
          
          <v-card-actions>
            <v-spacer></v-spacer>
            <input type="file" id="fileInput" @change="handleFileUpload" hidden accept=".pdf,.doc,.docx">
            <v-btn color="primary" variant="flat" @click="triggerFileInput" :loading="isUploading" :disabled="isActionInProgress">
              <v-icon left>mdi-upload</v-icon>
              Subir Nuevo DI
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
    
    <v-dialog v-model="deleteDialog.show" max-width="500px" persistent>
      <v-card>
        <v-card-title class="headline">Confirmar Eliminación</v-card-title>
        <v-card-text>
          ¿Estás seguro de que quieres eliminar el archivo <strong>{{ deleteDialog.itemName }}</strong>? Esta acción no se puede deshacer.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="deleteDialog.show = false">Cancelar</v-btn>
          <v-btn color="red-darken-1" variant="tonal" @click="confirmDelete">Eliminar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="transformDialog.show" max-width="500px" persistent>
        <v-card>
            <v-card-title class="headline">Procesamiento Pendiente</v-card-title>
            <v-card-text>
                <p>Para analizar este DI, primero debe ser transformado. Este proceso puede tardar unos segundos y el estado se actualizará automáticamente.</p>
            </v-card-text>
            <v-card-actions class="px-4 pb-4">
                <v-btn text @click="transformDialog.show = false">Cancelar</v-btn>
                <v-spacer></v-spacer>
                <v-btn color="primary" variant="flat" @click="handleTransform" :loading="isTransforming">
                    Transformar Ahora
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
    
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
import { ref, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useDiStore } from '@/stores/diStore';
import { storeToRefs } from 'pinia';
import { uploadDi, getDownloadUrl, deleteDi, transformDiToLd } from '@/services/apiService';

const router = useRouter();
const diStore = useDiStore();
const { designs, isLoading } = storeToRefs(diStore);

const isUploading = ref(false);
const isDeleting = ref(null);
const isTransforming = ref(false);
const notification = reactive({ message: '', type: 'success' });

const deleteDialog = reactive({ show: false, itemId: null, itemName: '' });
const transformDialog = reactive({ show: false, item: null });
const viewerDialog = reactive({ show: false, url: '', itemName: '' });

const isActionInProgress = computed(() => isUploading.value || isTransforming.value || !!isDeleting.value);

function handleRefresh() {
  notification.message = '';
  diStore.fetchDesigns();
}

function viewDetails(design) {
    clearNotification();
    if (design.estado_transformacion === 'error' || !design.contenido_jsonld) {
        promptTransform(design);
    } else {
        router.push({ name: 'detail', params: { id: design.id_di } });
    }
}

const isProcessing = (design) => design.estado_transformacion === 'processing';
const getStatusIcon = (design) => {
  switch (design.estado_transformacion) {
    case 'success': return 'mdi-check-circle';
    case 'error': return 'mdi-alert-circle';
    default: return 'mdi-file-question';
  }
};
const getStatusColor = (design) => {
  switch (design.estado_transformacion) {
    case 'processing': return 'blue-grey';
    case 'success': return 'success';
    case 'error': return 'error';
    default: return 'grey';
  }
};
const getStatusText = (design) => {
    switch (design.estado_transformacion) {
        case 'processing': return 'Transformando...';
        case 'success': return `Listo para validar. Creado: ${new Date(design.created_at).toLocaleDateString()}`;
        case 'error': return 'Error en la transformación. Haz clic para reintentar.';
        case 'pending': return `Pendiente. Creado: ${new Date(design.created_at).toLocaleDateString()}`;
        default: return `Creado: ${new Date(design.created_at).toLocaleDateString()}`;
    }
};

function clearNotification() { notification.message = ''; }
function triggerFileInput() { clearNotification(); document.getElementById('fileInput').click(); }

async function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  isUploading.value = true;
  clearNotification();
  try {
    const result = await uploadDi(file);
    notification.message = result.message || `"${file.name}" subido con éxito.`;
    notification.type = 'success';
  } catch (error) {
    notification.message = `<b>Error al subir "${file.name}":</b><br>${error.message}`;
    notification.type = 'error';
  } finally {
    isUploading.value = false;
    event.target.value = '';
  }
}

function promptDelete(design) {
  deleteDialog.itemId = design.id_di;
  deleteDialog.itemName = design.nombre_archivo;
  deleteDialog.show = true;
}

async function confirmDelete() {
  if (!deleteDialog.itemId) return;
  isDeleting.value = deleteDialog.itemId;
  try {
    await deleteDi(deleteDialog.itemId);
    notification.message = 'DI eliminado.';
    notification.type = 'success';
  } catch (error) {
    notification.message = `Error al eliminar: ${error.message}`;
    notification.type = 'error';
  } finally {
    isDeleting.value = null;
    deleteDialog.show = false;
  }
}

function promptTransform(design) {
    transformDialog.item = design;
    transformDialog.show = true;
}

async function handleTransform() {
  const design = transformDialog.item;
  if (!design) return;
  isTransforming.value = true;
  clearNotification();
  try {
    await transformDiToLd(design.id_di);
    notification.message = `Transformación iniciada para "<b>${design.nombre_archivo}</b>". La lista se actualizará automáticamente.`;
    notification.type = 'info';
  } catch (error) {
    notification.message = `Falló la transformación: ${error.message}`;
    notification.type = 'error';
  } finally {
    isTransforming.value = false;
    transformDialog.show = false;
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
    notification.message = `Error al obtener la URL: ${error.message}`;
    notification.type = 'error';
    viewerDialog.show = false;
  }
}
</script>
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
          
          <v-list v-if="!isLoading && designs.length > 0" lines="two">
            <v-list-item
              v-for="design in designs"
              :key="design.id_di"
              @click="viewDetails(design)"
              link
              :class="{ 'item-processing': isProcessing(design.id_di) }"
              :disabled="isProcessing(design.id_di)"
            >
              <template v-slot:prepend>
                <v-avatar :color="getStatusColor(design.contenido_jsonld)">
                  <v-progress-circular 
                    v-if="isProcessing(design.id_di)"
                    indeterminate 
                    size="24"
                  ></v-progress-circular>
                  <v-icon v-else>{{ getStatusIcon(design.contenido_jsonld) }}</v-icon>
                </v-avatar>
              </template>

              <v-list-item-title>{{ design.nombre_archivo }}</v-list-item-title>
              <v-list-item-subtitle>{{ 'Creado: ' + new Date(design.created_at).toLocaleDateString() }}</v-list-item-subtitle>

              <template v-slot:append>
                <div class="d-flex align-center">
                  <v-btn icon="mdi-eye" variant="text" @click.stop="handleView(design)" title="Visualizar Archivo"></v-btn>
                  <v-btn icon="mdi-download" variant="text" @click.stop="handleDownload(design)" title="Descargar Archivo Original"></v-btn>
                  <v-btn icon="mdi-delete" variant="text" @click.stop="promptDelete(design)" title="Eliminar DI"></v-btn>
                </div>
              </template>
            </v-list-item>
          </v-list>
          
          <v-card-text v-if="!isLoading && designs.length === 0" class="text-center py-4">
            No has subido ningún Diseño Instruccional todavía.
          </v-card-text>
          
          <v-card-actions>
            <v-spacer></v-spacer>
            <input 
              type="file" 
              id="fileInput" 
              @change="handleFileUpload" 
              hidden 
              accept=".pdf,.doc,.docx"
            >
            <v-btn color="primary" variant="flat" @click="triggerFileInput" :loading="isUploading">
              <v-icon left>mdi-upload</v-icon>
              Subir Nuevo DI
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>

    <v-dialog v-model="deleteDialog.show" max-width="500px">
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

    <v-dialog v-model="transformDialog.show" max-width="500px">
        <v-card>
            <v-card-title class="headline">Procesamiento Pendiente</v-card-title>
            <v-card-text>
                <v-alert type="info" variant="tonal" class="mb-4">
                    Este Diseño Instruccional aún no ha sido procesado para su análisis.
                </v-alert>
                <p class="text-justify">
                    Para poder validarlo e interactuar con el asistente de IA, primero debe ser transformado a un formato estructurado.
                </p>
            </v-card-text>
            <v-card-actions class="px-4 pb-4">
                <v-btn text @click="transformDialog.show = false">Cancelar</v-btn>
                <v-spacer></v-spacer>
                <v-btn color="primary" variant="flat" @click="handleTransform(transformDialog.item)" :loading="isTransforming === transformDialog.item?.id_di">
                    Transformar
                </v-btn>
            </v-card-actions>
        </v-card>
    </v-dialog>
    
    <v-dialog v-model="viewerDialog.show" fullscreen>
      <v-card>
        <v-toolbar color="primary" dark>
          <v-toolbar-title>{{ viewerDialog.itemName }}</v-toolbar-title>
          <v-spacer></v-spacer>
          <v-btn icon @click="viewerDialog.show = false">
            <v-icon>mdi-close</v-icon>
          </v-btn>
        </v-toolbar>
        <v-card-text class="pa-0" style="height: calc(100vh - 64px);">
          <v-progress-linear v-if="!viewerDialog.url" indeterminate></v-progress-linear>
          <iframe v-if="viewerDialog.url" :src="viewerDialog.url" width="100%" height="100%" frameborder="0"></iframe>
        </v-card-text>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<style scoped>
.item-processing {
  opacity: 0.5;
  pointer-events: none;
}
</style>

<script setup>
import { ref, onMounted, reactive, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useDiStore } from '@/stores/diStore';
import { storeToRefs } from 'pinia';
import { uploadDi, getDownloadUrl, deleteDi, transformDiToLd } from '@/services/apiService';

const router = useRouter();
const diStore = useDiStore();
const { designs, isLoading } = storeToRefs(diStore);

const isUploading = ref(false);
const isTransforming = ref(null);
const isDeleting = ref(null);
const notification = reactive({ message: '', type: 'success' });

// Diálogos
const deleteDialog = reactive({ show: false, itemId: null, itemName: '' });
const transformDialog = reactive({ show: false, item: null, itemName: '' });
const viewerDialog = reactive({ show: false, url: '', itemName: '' });

const isActionInProgress = computed(() => isUploading.value || !!isTransforming.value || !!isDeleting.value);

onMounted(() => {
  diStore.fetchDesigns();
});

function handleRefresh(force = true) {
  return diStore.fetchDesigns(force);
}

// Lógica de navegación principal
function viewDetails(design) {
    clearNotification();
    if (design.contenido_jsonld) {
        router.push({ name: 'detail', params: { id: design.id_di } });
    } else {
        promptTransform(design);
    }
}

// --- Lógica de UI ---
function isProcessing(designId) {
  return isTransforming.value === designId || isDeleting.value === designId;
}

function getStatusIcon(jsonldContent) {
    return jsonldContent ? 'mdi-check-circle' : 'mdi-alert-circle';
}

function getStatusColor(jsonldContent) {
    return jsonldContent ? 'success' : 'error';
}

function clearNotification() {
  notification.message = '';
}

// --- Lógica de Acciones ---

function triggerFileInput() {
  clearNotification();
  document.getElementById('fileInput').click();
}

async function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  isUploading.value = true;
  clearNotification();

  try {
    await uploadDi(file);
    notification.message = `Archivo "${file.name}" subido correctamente.`;
    notification.type = 'success';
  } catch (error) {
    if (error.status === 409) {
      notification.message = `Error: El archivo "${file.name}" ya existe.`;
    } else {
      notification.message = error.message || 'Ocurrió un error inesperado al subir.';
    }
    notification.type = 'error';
  } finally {
    isUploading.value = false;
    await handleRefresh();
  }
}

function promptDelete(design) {
  deleteDialog.itemId = design.id_di;
  deleteDialog.itemName = design.nombre_archivo;
  deleteDialog.show = true;
}

async function confirmDelete() {
  if (!deleteDialog.itemId) return;
  const itemIdToDelete = deleteDialog.itemId;
  const itemNameToDelete = deleteDialog.itemName;

  deleteDialog.show = false;
  isDeleting.value = itemIdToDelete;
  notification.message = `Eliminando "${itemNameToDelete}"...`;
  notification.type = 'info';

  try {
    await deleteDi(itemIdToDelete);
    notification.message = 'Archivo eliminado correctamente.';
    notification.type = 'success';
  } catch (error) {
    notification.message = `Error al eliminar: ${error.message}`;
    notification.type = 'error';
  } finally {
    isDeleting.value = null;
    handleRefresh();
  }
}

async function handleTransform(design) {
  if (!design) return;
  
  transformDialog.show = false;
  isTransforming.value = design.id_di;
  notification.message = `Transformando "${design.nombre_archivo}"...`;
  notification.type = 'info';
  
  try {
    const response = await transformDiToLd(design.id_di);
    
    // CORRECCIÓN: Formatea el mensaje de notificación según tu especificación
    const status = response.status || 'éxito';
    const message = response.message || 'Proceso completado.';
    
    notification.message = `Transformación: ${status}<br> ${message}`;
    notification.type = 'success';

  } catch (error) {
    notification.message = `Falló la transformación: ${error.message}`;
    notification.type = 'error';
  } finally {
    await handleRefresh();
    isTransforming.value = null;
  }
}

function promptTransform(design) {
    transformDialog.item = design;
    transformDialog.itemName = design.nombre_archivo;
    transformDialog.show = true;
}

async function handleView(design) {
  viewerDialog.itemName = design.nombre_archivo;
  viewerDialog.url = '';
  viewerDialog.show = true;
  
  try {
    const response = await getDownloadUrl(design.id_di);
    viewerDialog.url = `https://docs.google.com/gview?url=${encodeURIComponent(response.signedURL)}&embedded=true`;
  } catch (error) {
    notification.message = `Error al obtener la URL de visualización: ${error.message}`;
    notification.type = 'error';
    viewerDialog.show = false;
  }
}
</script>
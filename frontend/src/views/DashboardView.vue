<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="d-flex align-center">
            <span class="headline">Mis Diseños Instruccionales</span>
            <v-spacer></v-spacer>
            <v-btn icon variant="text" @click="handleRefresh" :loading="isLoading" :disabled="isLoading || isUploading || !!isTransforming">
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
              @click:close="notification.message = ''"
              class="mb-4"
            >
              {{ notification.message }}
            </v-alert>
          </v-card-text>

          <v-progress-linear v-if="isLoading" indeterminate color="primary"></v-progress-linear>
          
          <v-list v-if="!isLoading && designs.length > 0" lines="two">
            <v-list-item
              v-for="design in designs"
              :key="design.id_di"
              @click="viewDetails(design)"
              link
            >
              <template v-slot:prepend>
                <v-avatar :color="getStatusColor(design.estado_transformacion)">
                  <v-progress-circular 
                    v-if="design.estado_transformacion === 'pendiente' || isTransforming === design.id_di" 
                    indeterminate 
                    size="24"
                  ></v-progress-circular>
                  <v-icon v-else>{{ getStatusIcon(design.estado_transformacion) }}</v-icon>
                </v-avatar>
              </template>

              <v-list-item-title>{{ design.nombre_archivo }}</v-list-item-title>
              <v-list-item-subtitle>{{ 'Creado: ' + new Date(design.created_at).toLocaleDateString() }}</v-list-item-subtitle>

              <template v-slot:append>
                <div class="d-flex align-center">
                  <v-btn 
                    v-if="design.estado_transformacion === 'fallido'"
                    icon="mdi-cogs" 
                    variant="text" 
                    @click.stop="showError(design)"
                    :disabled="!!isTransforming"
                    title="Ver Error y Reintentar"
                  ></v-btn>
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

    <v-dialog v-model="errorDialog.show" max-width="600px">
        <v-card>
            <v-card-title class="headline">Error en la Transformación</v-card-title>
            <v-card-text>
                <p class="text-body-1">No se pudo procesar el archivo <strong>{{ errorDialog.itemName }}</strong>. El sistema reportó el siguiente error:</p>
                <v-alert type="error" variant="tonal" class="mt-4">
                    <code>{{ errorDialog.message }}</code>
                </v-alert>
                <p class="mt-4">Por favor, revisa que el archivo sea un Diseño Instruccional válido. Puedes reintentar el proceso ahora.</p>
            </v-card-text>
            <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn color="grey-darken-1" text @click="errorDialog.show = false">Cerrar</v-btn>
                <v-btn color="primary" variant="flat" @click="handleTransform(errorDialog.item)" :loading="isTransforming === errorDialog.item?.id_di">Reintentar</v-btn>
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
        <v-card-text class="pa-0">
          <v-progress-linear v-if="!viewerDialog.url" indeterminate></v-progress-linear>
          <iframe v-if="viewerDialog.url" :src="viewerDialog.url" width="100%" height="100%" frameborder="0"></iframe>
        </v-card-text>
      </v-card>
    </v-dialog>

  </v-container>
</template>

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
const notification = reactive({ message: '', type: 'success' });

// Estados de los diálogos
const deleteDialog = reactive({ show: false, itemId: null, itemName: '' });
const errorDialog = reactive({ show: false, item: null, itemName: '', message: '' });
const transformDialog = reactive({ show: false, item: null, itemName: '' });
const viewerDialog = reactive({ show: false, url: '', itemName: '' });

onMounted(() => {
  diStore.fetchDesigns();
});

function handleRefresh() {
  diStore.fetchDesigns(true);
}

function viewDetails(design) {
    notification.message = ''; // Limpia notificaciones al interactuar
    switch(design.estado_transformacion) {
        case 'exitoso':
            router.push({ name: 'detail', params: { id: design.id_di } });
            break;
        case 'fallido':
            showError(design);
            break;
        case 'pendiente':
        default:
            promptTransform(design);
            break;
    }
}

// Funciones de ayuda para la UI
function getStatusIcon(status) {
    const icons = {
        exitoso: 'mdi-check-circle',
        fallido: 'mdi-alert-circle',
        pendiente: 'mdi-help-circle-outline' 
    };
    return icons[status] || 'mdi-help-circle-outline';
}

function getStatusColor(status) {
    const colors = {
        exitoso: 'success',
        fallido: 'error',
        pendiente: 'grey-lighten-1'
    };
    return colors[status] || 'grey-lighten-1';
}

function triggerFileInput() {
  notification.message = '';
  document.getElementById('fileInput').click();
}

async function handleFileUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  isUploading.value = true;
  notification.message = '';
  try {
    await uploadDi(file);
    notification.message = 'Archivo subido. La transformación automática ha comenzado.';
    notification.type = 'success';
    setTimeout(() => handleRefresh(), 1500); 
  } catch (error) {
    notification.message = error.message || 'Ocurrió un error inesperado al subir.';
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
  try {
    await deleteDi(deleteDialog.itemId);
    notification.message = 'Archivo eliminado correctamente.';
    notification.type = 'success';
    handleRefresh();
  } catch (error) {
    notification.message = `Error al eliminar: ${error.message}`;
    notification.type = 'error';
  } finally {
    deleteDialog.show = false;
  }
}

async function handleDownload(design) {
  try {
    notification.message = `Preparando descarga para ${design.nombre_archivo}...`;
    notification.type = 'info';
    const response = await getDownloadUrl(design.id_di);
    window.open(response.signedURL, '_blank');
    notification.message = '';
  } catch (error) {
    notification.message = `Error al descargar: ${error.message}`;
    notification.type = 'error';
  }
}

async function handleTransform(design) {
  if (!design) return;
  errorDialog.show = false;
  transformDialog.show = false;
  
  isTransforming.value = design.id_di;
  notification.message = `Iniciando transformación para "${design.nombre_archivo}"...`;
  notification.type = 'info';
  
  try {
    const response = await transformDiToLd(design.id_di);
    notification.message = response.message || 'Proceso de transformación iniciado. El estado se actualizará en unos momentos.';
    notification.type = 'success';
    setTimeout(() => handleRefresh(), 5000);
  } catch (error) {
    notification.message = `Error al iniciar la transformación: ${error.message}`;
    notification.type = 'error';
    handleRefresh();
  } finally {
    isTransforming.value = null;
  }
}

function showError(design) {
    errorDialog.item = design;
    errorDialog.itemName = design.nombre_archivo;
    errorDialog.message = design.error_transformacion || 'No se proporcionaron detalles del error.';
    errorDialog.show = true;
}

function promptTransform(design) {
    transformDialog.item = design;
    transformDialog.itemName = design.nombre_archivo;
    transformDialog.show = true;
}

async function handleView(design) {
  viewerDialog.itemName = design.nombre_archivo;
  viewerDialog.url = ''; // Limpia la URL anterior
  viewerDialog.show = true;
  
  try {
    const response = await getDownloadUrl(design.id_di);
    // Usamos el visor de Google Docs, que es compatible con DOCX y PDF
    viewerDialog.url = `https://docs.google.com/gview?url=${encodeURIComponent(response.signedURL)}&embedded=true`;
  } catch (error) {
    notification.message = `Error al obtener la URL de visualización: ${error.message}`;
    notification.type = 'error';
    viewerDialog.show = false; // Cierra el diálogo si falla
  }
}
</script>
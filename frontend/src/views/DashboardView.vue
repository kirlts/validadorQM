<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="d-flex align-center">
            <span class="headline">Mis Diseños Instruccionales</span>
            <v-spacer></v-spacer>
            <v-btn icon variant="text" @click="handleRefresh" :loading="isLoading" :disabled="isLoading">
              <v-icon>mdi-refresh</v-icon>
            </v-btn>
          </v-card-title>
          <v-card-subtitle>
            Selecciona un DI para ver su informe de calidad o proponer modificaciones.
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
              @click="viewDetails(design.id_di)"
            >
              <template v-slot:prepend>
                <v-avatar color="primary">
                  <v-icon icon="mdi-file-document-outline"></v-icon>
                </v-avatar>
              </template>

              <v-list-item-title>{{ design.nombre_archivo }}</v-list-item-title>
              <v-list-item-subtitle>{{ 'Creado: ' + new Date(design.created_at).toLocaleDateString() }}</v-list-item-subtitle>

              <template v-slot:append>
                <v-btn icon="mdi-download" variant="text" @click.stop="handleDownload(design)"></v-btn>
                <v-btn icon="mdi-delete" variant="text" @click.stop="promptDelete(design)"></v-btn>
              </template>
            </v-list-item>
          </v-list>
          <v-card-text v-if="!isLoading && designs.length === 0">
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
  </v-container>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useDiStore } from '@/stores/diStore';
import { storeToRefs } from 'pinia';
import { uploadDi, getDownloadUrl, deleteDi } from '@/services/apiService';

const router = useRouter();
const diStore = useDiStore();
const { designs, isLoading } = storeToRefs(diStore);
const isUploading = ref(false);
const notification = reactive({ message: '', type: 'success' });
const deleteDialog = reactive({ show: false, itemId: null, itemName: '' });

onMounted(() => {
  diStore.fetchDesigns();
});

function handleRefresh() {
  diStore.fetchDesigns(true);
}

function viewDetails(id) {
  router.push({ name: 'detail', params: { id: id } });
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
    const result = await uploadDi(file);
    notification.message = 'Archivo subido correctamente.';
    notification.type = 'success';
    handleRefresh();
  } catch (error) {
    if (error && error.status === 409) {
      notification.message = 'El archivo ya existe en el sistema.';
    } else {
      notification.message = error.message || 'Ocurrió un error inesperado.';
    }
    notification.type = 'error';
  } finally {
    isUploading.value = false;
    event.target.value = '';
  }
}

// --- NUEVAS FUNCIONES ---
function promptDelete(design) {
  deleteDialog.itemId = design.id_di;
  deleteDialog.itemName = design.nombre_archivo;
  deleteDialog.show = true;
}

async function confirmDelete() {
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
    notification.message = ''; // Limpia el mensaje informativo
  } catch (error) {
    notification.message = `Error al descargar: ${error.message}`;
    notification.type = 'error';
  }
}
</script>
<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="8">
        <v-card>
          <v-card-title class="headline">
            Panel de Administración
          </v-card-title>
          <v-card-subtitle>
            Herramientas para el mantenimiento del sistema.
          </v-card-subtitle>

          <v-list>
            <v-list-item>
              <v-list-item-title>Glosario de Dominio</v-list-item-title>
              <v-list-item-subtitle>
                Actualiza la base de conocimiento pedagógico (entidades, taxonomía, reglas).
              </v-list-item-subtitle>
              <template v-slot:append>
                <v-btn
                  color="primary"
                  @click="handleSyncDomain"
                  :loading="isSyncingDomain"
                  :disabled="isSyncingVocabulary"
                >
                  Sincronizar Dominio
                </v-btn>
              </template>
            </v-list-item>

            <v-divider class="my-2"></v-divider>

            <v-list-item>
              <v-list-item-title>Vocabulario Técnico (JSON-LD)</v-list-item-title>
              <v-list-item-subtitle>
                Actualiza el diccionario de claves técnicas para la estructuración de datos.
              </v-list-item-subtitle>
              <template v-slot:append>
                <v-btn
                  color="secondary"
                  @click="handleSyncVocabulary"
                  :loading="isSyncingVocabulary"
                  :disabled="isSyncingDomain"
                >
                  Sincronizar Vocabulario
                </v-btn>
              </template>
            </v-list-item>
          </v-list>
        </v-card>
      </v-col>
    </v-row>
    <!-- Snackbar para feedback al usuario -->
    <v-snackbar v-model="snackbar.show" :color="snackbar.color" timeout="3000">
      {{ snackbar.text }}
    </v-snackbar>
  </v-container>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { syncDomainGlossary, syncVocabularyGlossary } from '@/services/apiService';

const isSyncingDomain = ref(false);
const isSyncingVocabulary = ref(false);
const snackbar = reactive({
  show: false,
  text: '',
  color: 'success',
});

const showSnackbar = (text, color = 'success') => {
  snackbar.text = text;
  snackbar.color = color;
  snackbar.show = true;
};

const handleSyncDomain = async () => {
  isSyncingDomain.value = true;
  try {
    const response = await syncDomainGlossary();
    showSnackbar(response.message || 'Sincronización iniciada con éxito.');
  } catch (error) {
    showSnackbar(error.message || 'Error al iniciar la sincronización.', 'error');
  } finally {
    isSyncingDomain.value = false;
  }
};

const handleSyncVocabulary = async () => {
  isSyncingVocabulary.value = true;
  try {
    const response = await syncVocabularyGlossary();
    showSnackbar(response.message || 'Sincronización iniciada con éxito.');
  } catch (error) {
    showSnackbar(error.message || 'Error al iniciar la sincronización.', 'error');
  } finally {
    isSyncingVocabulary.value = false;
  }
};
</script>
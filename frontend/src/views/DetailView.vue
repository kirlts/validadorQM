<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" md="10">
        <v-card class="mb-4">
          <v-card-title class="headline">
            Informe de Calidad para: {{ design ? design.name : 'Cargando...' }}
          </v-card-title>
          <v-card-subtitle>
            Análisis de alineación con la rúbrica Quality Matters.
          </v-card-subtitle>
          <v-divider></v-divider>
          <v-card-text>
            <h3>Fortalezas</h3>
            <p>
              Excelente alineación entre los objetivos de aprendizaje (QM 2.1, 2.2) y las evaluaciones sumativas (QM 3.1). Los materiales instruccionales son variados y actuales (QM 4.5).
            </p>
            <h3 class="mt-3">Áreas de Mejora</h3>
            <p>
              Se recomienda añadir más evaluaciones formativas de bajo impacto para cumplir con QM 3.5. La política de trabajos tardíos (QM 3.2) no está explícitamente detallada.
            </p>
          </v-card-text>
        </v-card>

        <v-card>
          <v-card-title class="headline">
            Asistente de Modificación IA
          </v-card-title>
          <v-card-text>
            <v-textarea
              label="Escribe tu solicitud de modificación aquí (ej. 'Agregar una actividad formativa sobre bucles for en la semana 3')"
              rows="3"
              variant="outlined"
            ></v-textarea>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="secondary" variant="flat">
              <v-icon left>mdi-lightbulb-on-outline</v-icon>
              Proponer Modificación
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getInstructionalDesignById } from '@/services/mockApiService';

// props definirá las propiedades que el componente puede recibir, como el 'id' de la ruta
const props = defineProps({
  id: {
    type: String,
    required: true
  }
});

const design = ref(null);

onMounted(async () => {
  design.value = await getInstructionalDesignById(props.id);
});
</script>
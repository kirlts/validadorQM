// Este archivo simulará las llamadas a nuestra API de backend.

const mockDesigns = [
  { id: 1, name: 'DI - Introducción a la Programación', date: '2025-08-15' },
  { id: 2, name: 'DI - Cálculo Avanzado', date: '2025-07-22' },
  { id: 3, name: 'DI - Biología Celular', date: '2025-06-30' }
];

// Simula la obtención de todos los DIs
export function getInstructionalDesigns() {
  console.log('Mock API: Fetching all designs...');
  return new Promise(resolve => {
    setTimeout(() => {
      resolve(mockDesigns);
    }, 500); // Simula un retraso de red de 500ms
  });
}

// Simula la obtención de un DI por su ID
export function getInstructionalDesignById(id) {
  console.log(`Mock API: Fetching design with id ${id}...`);
  return new Promise(resolve => {
    setTimeout(() => {
      const design = mockDesigns.find(d => d.id === parseInt(id));
      resolve(design);
    }, 300);
  });
}

// Simula la respuesta del LLM a una propuesta de modificación
export function getModificationSuggestion(requestText) {
  console.log(`Mock API: Generating suggestion for request: "${requestText}"`);
  
  // Usamos <br> para saltos de línea en HTML
  const mockResponse = `
    <p><strong>Análisis de Viabilidad:</strong> La petición es viable y se alinea con el estándar QM 5.1, ya que promueve el logro de los objetivos de aprendizaje.</p>
    <p><strong>Plan de Implementación:</strong></p>
    <ol>
      <li>Crear una nueva entidad <strong>ActividadAprendizaje</strong> con <code>@id: "act:Act_S3_2"</code>.</li>
      <li>Asociarla a la semana 3 a través de la propiedad <code>ocurreEn: { "@id": "sem:S3" }</code>.</li>
      <li>Alinearla con el indicador de logro correspondiente usando <code>apoyaIndicador: [{ "@id": "il:IL2.1" }]</code>.</li>
    </ol>
    <p>Este cambio fortalecerá la secuencia pedagógica de la unidad.</p>
  `;

  return new Promise(resolve => {
    setTimeout(() => {
      resolve(mockResponse);
    }, 1500); // Simula un tiempo de procesamiento del LLM
  });
}
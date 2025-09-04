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
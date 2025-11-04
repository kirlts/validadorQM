import { supabase } from '@/supabase';

// --- INICIO DE LA NUEVA LÓGICA ---

/**
 * Determina la URL base para la API del backend.
 * En modo de desarrollo, apunta a localhost:5000.
 * En modo de producción, asume que el backend se sirve desde el mismo host
 * que el frontend, pero en el puerto 5000.
 * @returns {string} La URL base de la API.
 */
function getApiBaseUrl() {
  // `import.meta.env.PROD` es una variable especial de Vite.
  // Es `true` cuando ejecutas `vite build` (para producción).
  // Es `false` cuando ejecutas `vite` (el servidor de desarrollo).
  if (import.meta.env.PROD) {
    // Para producción: Construye la URL usando el host de la ventana actual,
    // pero forzando el puerto a 5000.
    // ej. Si estás en http://54.145.207.36/, esto se convertirá en http://54.145.207.36:5000
    return '/api';
  } else {
    // Para desarrollo: Siempre usa localhost:5000.
    return 'http://localhost:5000/api';
  }
}

// Define la URL base de la API una vez, usando la función anterior.
const API_URL = getApiBaseUrl();

console.log(`[apiService] Configurado para usar la API en: ${API_URL}`);

async function fetchWithAuth(endpoint, options = {}) {
  const { data: { session } } = await supabase.auth.getSession();
  
  if (!session) {
    console.error('[apiService] fetchWithAuth falló: No hay sesión de usuario activa.');
    throw new Error('No hay sesión de usuario activa.');
  }

  const fetchOptions = { ...options, cache: 'no-store' };
  const headers = { 'Authorization': `Bearer ${session.access_token}`, ...fetchOptions.headers };

  if (!(fetchOptions.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  fetchOptions.headers = headers;

  console.log(`[apiService] Realizando fetch a: ${API_URL}/${endpoint}`);
  const response = await fetch(`${API_URL}/${endpoint}`, fetchOptions);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: `Error en la API: ${response.statusText}` }));
    console.error(`[apiService] Fetch fallido a ${endpoint}:`, errorData);
    const error = new Error(errorData.message || errorData.error || `Error: ${response.statusText}`);
    error.status = response.status;
    throw error;
  }
  
  console.log(`[apiService] Fetch exitoso a ${endpoint}`);
  const contentType = response.headers.get("content-type");
  if (contentType && contentType.indexOf("application/json") !== -1) {
    return response.json();
  } else {
    return { success: true };
  }
}


export function getDis() {
  return fetchWithAuth('dis');
}

export function uploadDi(file, estructuraMEI) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('estructuraMEI', estructuraMEI); 

  // REFACTOR: Usar fetchWithAuth para consistencia y manejo de errores
  return fetchWithAuth('dis', {
    method: 'POST',
    body: formData,
    // No es necesario 'Content-Type', fetchWithAuth lo omite
    // automáticamente para FormData, permitiendo al navegador
    // establecer el 'boundary' correcto.
  });
}

export function deleteDi(diId) {
  return fetchWithAuth(`dis/${diId}`, { method: 'DELETE' });
}

export function getDownloadUrl(diId) {
  return fetchWithAuth(`dis/${diId}/download-url`);
}

export function getDiValidation(diId) {
  return fetchWithAuth(`dis/${diId}/validation`);
}

export function generateDiValidation(diId) {
  return fetchWithAuth(`dis/${diId}/validate`, { method: 'POST' });
}

export function interactWithDi(diId, prompt) {
  return fetchWithAuth(`dis/${diId}/interact`, {
    method: 'POST',
    body: JSON.stringify({ prompt: prompt }),
  });
}

export function syncDomainGlossary() {
  return fetchWithAuth('sync/domain-glossary', { method: 'POST' });
}

export function syncVocabularyGlossary() {
  return fetchWithAuth('sync/vocabulary-glossary', { method: 'POST' });
}

export function analyzeAlignment(diId) {
  return fetchWithAuth(`dis/${diId}/analyze-alignment`, { method: 'POST' });
}

export function generateIndicators(payload) {
  return fetchWithAuth('generate/indicators', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function revisarIndicadores(payload) {
  // El endpoint 'revisar-indicadores' debe coincidir con la ruta definida en app.py
  return fetchWithAuth('revisar-indicadores', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export function getGenerations() {
    return fetchWithAuth('generations');
}

export function deleteGeneration(generationId) {
    return fetchWithAuth(`generations/${generationId}`, { method: 'DELETE' });
}

export function renameGeneration(generationId, newName) {
  return fetchWithAuth(`generations/${generationId}`, {
    method: 'PATCH',
    body: JSON.stringify({ nombre_generacion: newName }),
  });
}
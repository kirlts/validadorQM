import { supabase } from '@/supabase';

const API_URL = 'http://localhost:5000/api';

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

export async function uploadDi(file, estructuraMEI) { // <-- CAMBIO 1: Renombrar el segundo argumento para mayor claridad
  const formData = new FormData();
  formData.append('file', file);
  
  // --- CAMBIO 2: Usar la clave correcta 'estructuraMEI' que el backend espera ---
  formData.append('estructuraMEI', estructuraMEI); 

  const { data: { session } } = await supabase.auth.getSession();
  if (!session) throw new Error('No hay sesión de usuario activa.');

  const response = await fetch(`${API_URL}/dis`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${session.access_token}` },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const error = new Error(errorData.message || errorData.error || `Error: ${response.statusText}`);
    error.status = response.status;
    throw error;
  }
  return response.json();
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
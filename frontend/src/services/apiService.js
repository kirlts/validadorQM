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

export async function uploadDi(file, paradigma) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('paradigma', paradigma); 

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

// --- Nuevas funciones para el panel de administración ---
export function syncDomainGlossary() {
  return fetchWithAuth('sync/domain-glossary', { method: 'POST' });
}

export function syncVocabularyGlossary() {
  return fetchWithAuth('sync/vocabulary-glossary', { method: 'POST' });
}
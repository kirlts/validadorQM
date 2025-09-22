import { supabase } from '@/supabase';

const API_URL = 'http://localhost:5000/api';

async function fetchWithAuth(endpoint, options = {}) {
  const { data: { session } } = await supabase.auth.getSession();
  
  if (!session) {
    throw new Error('No hay sesión de usuario activa.');
  }

  // Clave: No establecer Content-Type si el body es FormData
  const headers = {
    'Authorization': `Bearer ${session.access_token}`,
    ...options.headers,
  };

  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${API_URL}/${endpoint}`, { ...options, headers });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ error: `Error en la API: ${response.statusText}` }));
    const error = new Error(errorData.message || errorData.error);
    error.status = response.status;
    throw error;
  }

  return response.json();
}

export function validateToken() {
  return fetchWithAuth('validate-token', { method: 'POST' });
}

export function getDis() {
  return fetchWithAuth('dis');
}

export async function uploadDi(file) {
  const formData = new FormData();
  formData.append('file', file);

  const { data: { session } } = await supabase.auth.getSession();
  if (!session) throw new Error('No hay sesión de usuario activa.');

  const response = await fetch(`${API_URL}/dis`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${session.access_token}` },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw { 
      status: response.status, 
      message: errorData.message || errorData.error || `Error: ${response.statusText}`
    };
  }
  return response.json();
}

export function deleteDi(diId) {
  return fetchWithAuth(`dis/${diId}`, { method: 'DELETE' });
}

export function getDownloadUrl(diId) {
  return fetchWithAuth(`dis/${diId}/download-url`);
}

export function transformDiToLd(diId) {
  return fetchWithAuth(`dis/${diId}/transform`, { method: 'POST' });
}
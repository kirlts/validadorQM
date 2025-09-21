import { supabase } from '@/supabase';

const API_URL = 'http://localhost:5000/api';

async function fetchWithAuth(endpoint, options = {}) {
  const { data: { session } } = await supabase.auth.getSession();
  
  if (!session) {
    throw new Error('No hay sesión de usuario activa.');
  }

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${session.access_token}`,
    ...options.headers,
  };

  const response = await fetch(`${API_URL}/${endpoint}`, { ...options, headers });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.error || `Error en la API: ${response.statusText}`);
  }

  return response.json();
}

export function validateToken() {
  return fetchWithAuth('validate-token', { method: 'POST' });
}

// Obtiene la lista de Diseños Instruccionales del usuario autenticado, espera un array limpio directamente del backend.
export async function getDis() {
  // La respuesta del backend ya es el array de DIs que necesitamos.
  // Flask se encarga de devolver la salida del nodo "Set" de N8N.
  const response = await fetchWithAuth('dis', { method: 'GET' });
  return response;
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
    const errorData = await response.json().catch(() => ({})); // Intenta parsear JSON, si falla, devuelve objeto vacío
    // --- CAMBIO CLAVE AQUÍ ---
    // Creamos y lanzamos un objeto de error personalizado que contiene el código de estado.
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
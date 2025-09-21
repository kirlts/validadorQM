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
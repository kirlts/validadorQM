// El cliente de supabase gestiona el token automáticamente.
// No necesitamos obtener la sesión manualmente aquí.
import { supabase } from '@/supabase';

const API_URL = 'http://localhost:5000/api';

async function fetchWithAuth(endpoint, options = {}) {
  // supabase.auth.getSession() es aún necesario aquí para obtener el token,
  // pero el oyente en App.vue asegura que cuando esta función se llame,
  // la sesión ya estará establecida.
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
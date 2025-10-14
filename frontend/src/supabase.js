// frontend/src/supabase.js

import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY

// --- Objeto de opciones para robustecer la conexión ---
const supabaseOptions = {
  realtime: {
    params: {
      // Aumenta el "heartbeat" para mantener la conexión activa.
      // El cliente enviará un ping al servidor cada 15 segundos.
      heartbeat_ms: 15000, 
    }
  }
};

export const supabase = createClient(supabaseUrl, supabaseAnonKey, supabaseOptions)
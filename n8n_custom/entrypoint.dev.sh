#!/bin/sh
# n8n_custom/entrypoint.dev.sh
# Este script es SOLO para el entorno de desarrollo.

set -e

# La ruta a la base de datos de SQLite que usa n8n en desarrollo.
DB_FILE="/home/node/.n8n/database.sqlite"

# Verificamos si la base de datos NO existe.
if [ ! -f "$DB_FILE" ]; then
    echo "--- [DEV SETUP] ---"
    echo "First time setup detected (database not found). Importing workflows..."
    
    # Si no existe, importamos y activamos los workflows base.
    # El proceso n8n se encargará de crear la BBDD al ejecutar estos comandos.
    n8n import:workflow --separate --input=/home/node/.n8n/workflows/
    n8n update:workflow --all --active=true
    
    echo "Workflows imported and activated."
    echo "--- [DEV SETUP COMPLETE] ---"
else
    echo "Existing n8n data found, skipping automatic workflow import."
fi

# Finalmente, pasamos el control al comando de inicio normal de n8n.
echo "Starting n8n..."
exec n8n
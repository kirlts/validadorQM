#!/bin/sh
set -e

echo "--- [Smart Entrypoint] Starting n8n in background..."
n8n start &
N8N_PID=$!

echo "--- [Smart Entrypoint] Waiting for n8n API to be ready..."
while ! curl -s --fail "http://localhost:5678/healthz" > /dev/null; do
   sleep 3
done
echo "n8n API is up. Giving 10s for DB/user setup to settle..."
sleep 10

echo "--- [Smart Entrypoint] Checking for existing owner user..."
# Intentamos obtener el ID del usuario.
# Usamos '|| true' para que el script no falle si grep no encuentra nada.
OWNER_ID=$(n8n user-management:list | grep -oP '"id": "\K[^"]+' | head -n 1 || true)

# Si NO se encontró un usuario, asumimos que es el primer arranque.
if [ -z "$OWNER_ID" ]; then
    echo "--- [Smart Entrypoint] No owner user found. Assuming first-time bootstrap."
    echo "Please go to the n8n UI to complete the 'Set up owner account' step."
    echo "This script will now wait for the main n8n process to finish."
else
    # Si se encontró un usuario, procedemos con el aprovisionamiento.
    echo "Owner User ID found: $OWNER_ID"
    
    echo "--- [Smart Entrypoint] Importing credentials for User ID: $OWNER_ID..."
    n8n import:credentials --input=/run/secrets/n8n_credentials --userId="$OWNER_ID"

    echo "--- [Smart Entrypoint] Importing and activating workflows for User ID: $OWNER_ID..."
    n8n import:workflow --separate --input=/home/node/workflows/ --userId="$OWNER_ID"
    n8n update:workflow --all --active=true
fi

echo "--- [Smart Entrypoint] Provisioning logic complete. Handing over to main n8n process."
wait $N8N_PID
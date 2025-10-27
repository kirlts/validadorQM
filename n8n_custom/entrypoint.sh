#!/bin/sh
set -e

echo "--- [Entrypoint] Starting n8n in background..."
n8n start &
N8N_PID=$!

echo "--- [Entrypoint] Waiting for n8n API to be ready..."
while ! curl -s --fail "http://localhost:5678/healthz" > /dev/null; do
   sleep 3
done
echo "n8n API is up. Giving 10s for owner user to be created..."
sleep 10

echo "--- [Entrypoint] Fetching Owner User ID..."
OWNER_ID=$(n8n user-management:list | grep -oP '"id": "\K[^"]+' | head -n 1)

if [ -z "$OWNER_ID" ]; then
    echo "FATAL: Could not find Owner User ID. Provisioning failed."
    # Detenemos el proceso de n8n en background para que el contenedor falle limpiamente
    kill $N8N_PID
    exit 1
fi
echo "Owner User ID found: $OWNER_ID"

echo "--- [Entrypoint] Importing credentials for User ID: $OWNER_ID..."
n8n import:credentials --input=/run/secrets/n8n_credentials --userId="$OWNER_ID"

echo "--- [Entrypoint] Importing and activating workflows for User ID: $OWNER_ID..."
n8n import:workflow --separate --input=/home/node/workflows/ --userId="$OWNER_ID"
n8n update:workflow --all --active=true

echo "--- [Entrypoint] Provisioning complete. Handing over to main n8n process."
wait $N8N_PID
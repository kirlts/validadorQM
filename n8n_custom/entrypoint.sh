#!/bin/sh
set -e

echo "--- [Entrypoint] Starting n8n in background for provisioning..."
n8n start &
N8N_PID=$!

echo "--- [Entrypoint] Waiting for n8n API to be ready..."
while ! curl -s --fail "http://localhost:5678/healthz" > /dev/null; do
   sleep 3
done
echo "n8n API is up. Giving 5s for DB to settle."
sleep 5

# PASO 1: IMPORTAR CREDENCIALES
echo "--- [Entrypoint] Importing credentials..."
n8n import:credentials --input=/run/secrets/n8n_credentials

# PASO 2: IMPORTAR Y ACTIVAR WORKFLOWS
echo "--- [Entrypoint] Importing and activating workflows..."
n8n import:workflow --separate --input=/home/node/workflows/
n8n update:workflow --all --active=true

echo "--- [Entrypoint] Provisioning complete. Handing over to n8n process."
wait $N8N_PID
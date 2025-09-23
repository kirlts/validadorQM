# Usa la imagen oficial de n8n como base
FROM n8nio/n8n:latest

# Cambia al usuario root para poder instalar paquetes
USER root

# Instala pandoc y poppler-utils usando el gestor de paquetes de Alpine (apk)
RUN apk add --no-cache pandoc poppler-utils

# Vuelve al usuario por defecto de n8n para mantener la seguridad
USER node
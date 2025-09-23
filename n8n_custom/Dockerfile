# Usa la imagen oficial de n8n como base
FROM n8nio/n8n:latest

# Cambia al usuario root para poder instalar paquetes
USER root

# Instala pandoc usando el gestor de paquetes de Alpine (apk)
# --no-cache asegura que no se guarde la caché de paquetes, manteniendo la imagen ligera
RUN apk add --no-cache pandoc

# Vuelve al usuario por defecto de n8n para mantener la seguridad
USER node
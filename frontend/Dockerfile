# frontend/Dockerfile (VERSIÓN DE PRODUCCIÓN)

# --- Etapa 1: Build ---
# Usamos una imagen de Node para construir el proyecto Vue.
FROM node:20-alpine AS build-stage

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# ¡CRÍTICO! Este comando construye los archivos estáticos para producción.
RUN npm run build

# --- Etapa 2: Serve ---
# Usamos una imagen ligera de Nginx para servir los archivos.
FROM nginx:stable-alpine AS production-stage

# Copiamos los archivos estáticos construidos desde la etapa anterior.
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copiamos nuestra configuración personalizada de Nginx.
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf

# Exponemos el puerto que Nginx está escuchando (definido en default.conf).
EXPOSE 8080

# El comando para iniciar Nginx.
CMD ["nginx", "-g", "daemon off;"]
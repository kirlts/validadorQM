# frontend/Dockerfile (VERSIÓN FINAL)

# --- Etapa 1: Build ---
FROM node:20-alpine AS build-stage

WORKDIR /app

# ¡CAMBIO CLAVE 1! Declaramos los argumentos que vamos a recibir desde docker-compose.
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY

COPY package*.json ./
RUN npm install
COPY . .

# ¡CAMBIO CLAVE 2! El comando 'RUN' tiene acceso a los ARGs. Vite los leerá
# como si fueran variables de entorno del sistema durante el build.
RUN npm run build

# --- Etapa 2: Serve ---
FROM nginx:stable-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html
COPY ./nginx/default.conf /etc/nginx/conf.d/default.conf
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
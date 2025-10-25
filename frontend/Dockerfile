# frontend/Dockerfile

# --- Etapa 1: Build ---
FROM node:20-alpine AS build-stage
WORKDIR /app
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY

# ¡CAMBIO! La ruta ahora es relativa a la raíz del proyecto.
COPY ./frontend/package*.json ./
RUN npm install

# ¡CAMBIO! Copiamos solo el contenido de la carpeta frontend.
COPY ./frontend/ .

RUN npm run build

# --- Etapa 2: Serve ---
FROM nginx:stable-alpine AS production-stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Esta ruta ya era correcta, la mantenemos.
COPY ./frontend/nginx/default.conf /etc/nginx/conf.d/default.conf

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
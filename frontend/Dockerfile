# frontend/Dockerfile

# --- Etapa 1: Build ---
# Esta etapa usa una imagen de Node para compilar tu aplicación de Vue.
FROM node:20-alpine AS build-stage

# Establece el directorio de trabajo dentro del contenedor de build.
WORKDIR /app

# Declara los argumentos de build que recibirá desde docker-compose.
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY

# Copia los archivos de definición de dependencias.
COPY ./frontend/package*.json ./

# Instala las dependencias de npm.
RUN npm install

# Copia el resto del código fuente del frontend.
COPY ./frontend/ .

# Ejecuta el script de build de Vite.
# En este paso, Vite leerá los ARGs (VITE_SUPABASE_URL, etc.)
# y los incrustará en los archivos JavaScript estáticos generados.
RUN npm run build


# --- Etapa 2: Serve ---
# Esta etapa usa una imagen ligera de Nginx para servir los archivos estáticos.
FROM nginx:stable-alpine AS production-stage

# Copia los archivos estáticos (la carpeta 'dist') desde la etapa de build.
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copia tu archivo de configuración de Nginx personalizado.
# Este es el archivo que simplificamos en la respuesta anterior.
COPY ./frontend/nginx/default.conf /etc/nginx/conf.d/default.conf

# Expone el puerto que Nginx escuchará dentro del contenedor.
EXPOSE 8080

# El comando por defecto para iniciar el servidor Nginx.
CMD ["nginx", "-g", "daemon off;"]
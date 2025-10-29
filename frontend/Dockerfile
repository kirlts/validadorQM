# frontend/Dockerfile (VERSIÓN SIMPLE Y FUNCIONAL PARA PRODUCCIÓN)

FROM node:20-alpine

WORKDIR /app

# Pasamos las claves de Supabase como argumentos de build
ARG VITE_SUPABASE_URL
ARG VITE_SUPABASE_ANON_KEY
ENV VITE_SUPABASE_URL=$VITE_SUPABASE_URL
ENV VITE_SUPABASE_ANON_KEY=$VITE_SUPABASE_ANON_KEY

COPY package*.json ./
RUN npm install
COPY . .

# 1. Construimos los archivos de producción
RUN npm run build

# 2. Exponemos el puerto que usará el servidor de preview de Vite
EXPOSE 8080

# 3. ¡CAMBIO CLAVE! Usamos 'npm run preview' con --host
# Este comando sirve los archivos de la carpeta 'dist/'
# de una manera que respeta el enrutamiento de Vue.
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "8080"]
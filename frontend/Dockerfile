# Fase 1: Usar una imagen oficial de Node.js como base
# Se recomienda usar una versión LTS (Long-Term Support) específica
FROM node:20-alpine

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de manifiesto de dependencias PRIMERO
# Esto aprovecha el caché de Docker. Si no cambian, no se re-instala.
COPY package*.json ./

# Instalar las dependencias del proyecto
RUN npm install

# Copiar el resto de los archivos de la aplicación
COPY . .

# Exponer el puerto que Vite usará dentro del contenedor
# Debe coincidir con el script "dev" en package.json (8080 en tu caso)
EXPOSE 8080

# El comando que se ejecutará cuando el contenedor se inicie
CMD ["npm", "run", "dev"]
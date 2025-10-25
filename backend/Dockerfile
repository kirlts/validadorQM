# Usa una imagen base de Python ligera
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de dependencias
COPY ./backend/requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY ./backend/ .

# Expone el puerto que Flask usará
EXPOSE 5000

# Comando para correr la aplicación
CMD ["flask", "run", "--host=0.0.0.0"]
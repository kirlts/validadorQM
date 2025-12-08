# Dockerfile para Streamlit
FROM python:3.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de dependencias
COPY ./streamlit/requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código de la aplicación
COPY ./streamlit/ .

# Expone el puerto que Streamlit usará (8501 es el puerto por defecto)
EXPOSE 8501

# Comando para correr Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]


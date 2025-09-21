# Validador QM con IA

Este proyecto es una aplicación web diseñada para validar Diseños Instruccionales (DIs) contra la rúbrica de Quality Matters (QM) utilizando un asistente de Inteligencia Artificial. El sistema permite a los docentes subir sus DIs, recibir un análisis de calidad y obtener sugerencias de mejora.

## 🚀 Tech Stack

- **Frontend:** Vue.js 3 con Vuetify
- **API Gateway:** Flask (Python)
- **Orquestador de Lógica:** N8N
- **Base de Datos y Almacenamiento:** Supabase
- **Entorno:** Docker y Docker Compose

## 📋 Prerrequisitos

- Docker y Docker Compose instalados.

## ⚙️ Configuración

1.  **Clonar el Repositorio:**
    ```bash
    git clone [https://github.com/kirlts/validadorQM.git](https://github.com/kirlts/validadorQM.git)
    cd validadorQM
    ```

2.  **Configurar Variables de Entorno:**
    Crea un archivo `.env` en la raíz del proyecto. Puedes usar el archivo `.env.example` como plantilla:
    ```bash
    cp .env.example .env
    ```
    Luego, edita el archivo `.env` y rellena todas las credenciales y URLs de tus servicios (Supabase, N8N, etc.).

3.  **Crear el Directorio de N8N:**
    El volumen de Docker para N8N requiere que el directorio exista antes de iniciar.
    ```bash
    mkdir n8n_data
    ```

## ▶️ Ejecutar el Proyecto

Una vez configurado el archivo `.env`, puedes levantar todo el entorno con un solo comando:

```bash
docker compose up -d --build
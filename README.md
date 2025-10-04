# Validador QM con IA

Este proyecto es una aplicación web diseñada para validar Diseños Instruccionales (DIs) contra la rúbrica de Quality Matters (QM) utilizando un asistente de Inteligencia Artificial. El sistema permite a los docentes subir sus DIs, recibir un análisis de calidad y obtener sugerencias de mejora.

---

## 🚀 Stack Tecnológico

- **Frontend:** Vue.js 3 con Vuety y Pinia
- **Backend (API Gateway):** Flask (Python)
- **Orquestador de Lógica Asíncrona:** n8n
- **Base de Datos y Servicios:** Supabase (PostgreSQL, Auth, Storage, Realtime)
- **Entorno:** Docker

---

## 🏛️ Arquitectura

La aplicación sigue una arquitectura de microservicios desacoplados, orquestada por Docker Compose. Cada componente tiene una responsabilidad única:

- **Frontend (Vue.js):** Es la única interfaz con la que el usuario interactúa. Su rol es mostrar datos y capturar eventos de usuario, delegando toda la lógica de negocio al backend.
- **Backend (Flask):** Actúa como un **API Gateway seguro**. Valida la autenticación del usuario, gestiona las operaciones con Supabase Storage y es el único punto de entrada para iniciar procesos asíncronos en n8n.
- **n8n:** Es el motor para **tareas de larga duración** (ej. conversión de documentos, llamadas a LLMs). Opera en segundo plano y nunca es contactado directamente por el frontend.
- **Supabase:** Provee la infraestructura de backend completa, actuando como la **fuente única de verdad** para los datos, la autenticación, el almacenamiento de archivos y el sistema de notificaciones.

---

## ⚡ Flujo de Datos en Tiempo Real

Para una experiencia de usuario fluida y reactiva, el sistema utiliza un **patrón de `Broadcast` híbrido**, garantizando que la UI siempre refleje el estado real de los datos.

1.  **Notificación Inmediata:** Cuando un usuario inicia una acción (ej. transformar un archivo), la API de Flask actualiza el estado en la base de datos y envía inmediatamente un mensaje `Broadcast` a través de Supabase. Esto actualiza la UI en menos de un segundo.
2.  **Notificación de Respaldo:** Cuando un proceso asíncrono en n8n finaliza y actualiza la base de datos, un `Trigger` en PostgreSQL se activa y envía otro mensaje `Broadcast`.
3.  **Suscripción del Frontend:** El frontend (a través de Pinia) está suscrito a un único canal de `Broadcast`. Al recibir un mensaje, actualiza el estado global y la interfaz reacciona automáticamente.

---

## 📋 Prerrequisitos

- Docker y Docker Compose instalados.

---

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
    Luego, edita el archivo `.env` y rellena todas las credenciales y URLs de tus servicios (Supabase, n8n, etc.). Asegúrate de configurar también las variables `VITE_*` en el archivo `.env` dentro de la carpeta `frontend/`.

---

## ▶️ Ejecutar el Proyecto

Una vez configurados los archivos `.env`, puedes levantar todo el entorno con un solo comando:

```bash
docker compose up -d --build
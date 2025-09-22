# Validador QM con IA

Este proyecto es una aplicación web diseñada para validar Diseños Instruccionales (DIs) contra la rúbrica de Quality Matters (QM) utilizando un asistente de Inteligencia Artificial. El sistema permite a los docentes subir sus DIs, recibir un análisis de calidad y obtener sugerencias de mejora.

---

## 🚀 Tech Stack

- **Frontend:** Vue.js 3 con Vuetify
- **API Gateway:** Flask (Python)
- **Orquestador de Lógica:** N8N
- **Base de Datos y Almacenamiento:** Supabase
- **Entorno:** Docker

---

## 📋 Prerrequisitos

- Docker instalado.

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
    Luego, edita el archivo `.env` y rellena todas las credenciales y URLs de tus servicios (Supabase, N8N, etc.).

---

## ▶️ Ejecutar el Proyecto

Una vez configurado el archivo `.env`, puedes levantar todo el entorno con un solo comando:

```bash
docker compose up -d --build
```

Una vez iniciados los contenedores, los servicios estarán disponibles en:

Frontend: **http://localhost:8080**

API de Flask: **http://localhost:5000**

Interfaz de N8N: **http://localhost:5678**

---

## Endpoints de la API

Todos los endpoints requieren un token JWT de Supabase en la cabecera Authorization: Bearer <token>

**GET /api/dis:** Lista los DIs del usuario autenticado.

**POST /api/dis:** Sube un nuevo archivo DI.

**DELETE /api/dis/<uuid:di_id>:** Elimina un DI específico.

**GET /api/dis/<uuid:di_id>/download-url:** Genera una URL de descarga firmada.
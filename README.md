# Validador QM con IA

Este repositorio contiene el código fuente del "Validador QM", una aplicación web diseñada para asistir a diseñadores instruccionales y equipos de calidad en el análisis y mejora de Diseños Instruccionales (DIs).

El sistema transforma DIs estáticos (formatos `.docx` y PDF) en modelos de datos estructurados (JSON-LD) y utiliza un motor de Inteligencia Artificial (IA) con RAG para:

* Validar el alineamiento constructivo contra estándares (como Quality Matters).
* Generar indicadores de aprendizaje y evaluación.
* Revisar la coherencia de indicadores existentes.
* Permitir la interacción en lenguaje natural sobre el contenido del DI.

---

## Stack

* **Frontend:** Vue.js 3 (servido con Nginx)
* **Gestión de Estado (Frontend):** Pinia
* **Backend (API Gateway):** Flask (Python) con Gunicorn
* **Motor IA y Lógica de Negocio:** N8N (Workflow Engine)
* **Base de Datos (Vectorial y Relacional):** Supabase (PostgreSQL con pgvector)
* **Servicios Adicionales:** Supabase Auth, Storage y Realtime
* **Entorno de Desarrollo y Producción:** Docker

---

## Arquitectura

La filosofía central es una **arquitectura de tres componentes desacoplados**, orquestada por Docker.

1.  **Frontend (Nginx + Vue.js):**
    * Es el único componente expuesto públicamente (Puerto 80).
    * Maneja toda la interacción del usuario y la gestión de estado con Pinia.
    * Nginx actúa como *proxy inverso* (`proxy_pass`) para dirigir el tráfico API al Backend y el tráfico de admin a N8N.

2.  **Backend (Flask + Gunicorn):**
    * Actúa como un **Gatekeeper**.
    * Su *única* responsabilidad es la autenticación (validar JWT de Supabase) y la autorización (chequear propiedad de recursos).
    * **No contiene lógica de negocio.** Recibe peticiones del frontend, las valida, y delega *inmediatamente* la tarea a N8N disparando un webhook.

3.  **Motor IA (N8N):**
    * Es el **"Cerebro" del sistema**.
    * Aquí reside el **100% de la lógica de negocio** y los flujos de IA (RAG, cadenas de agentes, etc.).
    * Se comunica directamente con Supabase para leer y escribir datos.

4.  **Base de Datos (Supabase):**
    * Es la **Fuente Única de Verdad**.
    * Provee la base de datos relacional, la base de datos vectorial (para RAG), almacenamiento de archivos, autenticación y el bus de eventos en tiempo real.

---

## Funcionalidades Principales

* Gestión de archivos de Diseño Instruccional (CRUD).
* Ingesta de archivos `.docx` y conversión a HTML/JSON-LD.
* Generación de Indicadores (RF-RA-ID y RA-AE-IL) mediante RAG.
* Revisión de coherencia de Indicadores existentes.
* Análisis de Alineamiento completo del DI.
* Asistente de Chat (RAG) sobre el contenido del DI y su análisis.
* Panel de Administración (protegido por rol) para sincronizar las bases de conocimiento (Glosarios) del RAG.

---

## Despliegue (CI/CD)

El sistema está configurado para despliegue continuo en **AWS**.

* **Proveedor:** AWS EC2 (Instancia t3.medium)
* **Pipeline:** GitHub Actions (`.github/workflows/deploy.yml`)
* **Registro:** Amazon ECR (Elastic Container Registry)

El *trigger* (un `push` a la rama `main`) inicia el pipeline, que automáticamente:
1.  Construye las imágenes de Docker del `frontend` y `backend`.
2.  Inyecta las variables de entorno (keys de Supabase) como *build-args*.
3.  Sube las imágenes a ECR.
4.  Se conecta vía SSH a la instancia EC2.
5.  Escribe el archivo `.env.prod` desde los Secrets de GitHub.
6.  Descarga las nuevas imágenes (`docker pull`) y reinicia los contenedores (`docker compose up -d`).

**Nota:** El contenedor de `n8n` se gestiona manualmente en el servidor para preservar los workflows y credenciales.

---

## Desarrollo Local

### Prerrequisitos

* Docker
* Docker Compose

### 1. Configuración de Entorno

1.  Clona el repositorio:
    ```bash
    git clone [https://github.com/kirlts/validadorQM.git](https://github.com/kirlts/validadorQM.git)
    cd validadorQM
    ```

2.  Crea el archivo de entorno principal (para Docker Compose y el Backend):
    ```bash
    cp .env.example .env
    ```

3.  Crea el archivo de entorno del Frontend:
    ```bash
    cp frontend/.env.example frontend/.env
    ```

4.  Edita **ambos** archivos `.env` y rellena todas las variables (URLs y Keys de Supabase, credenciales de N8N, etc.).

### 2. Ejecución

Levanta todo el stack de servicios usando el archivo de composición de desarrollo:

```bash
docker compose -f docker-compose.dev.yml up --build
Una vez que los contenedores estén en ejecución, los servicios estarán disponibles en:

Frontend (Aplicación): http://localhost:8080

Backend (API Gateway): http://localhost:5000

Motor IA (N8N): http://localhost:5678
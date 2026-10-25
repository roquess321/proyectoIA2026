# 🎓 Sistema Inteligente de Acompañamiento Académico - FIUNA

Plataforma académica interactiva desarrollada para la Facultad de Ingeniería de la Universidad Nacional de Asunción (**FIUNA**). Integra un **Dashboard de Malla Curricular**, un **Simulador Predictivo de Calificaciones** y un **Agente Académico Inteligente con memoria y persistencia**.

---

## 🏛️ Arquitectura del Sistema

El proyecto cumple estrictamente con una arquitectura cliente-servidor desacoplada y segura:

1. **Frontend (Svelte 5 & TypeScript):**
   - Construido con la última versión de Svelte 5 (sintaxis de Runes: `$state`, `$derived`, `$props`).
   - Interfaz moderna, reactiva y tipado estricto.
   - Consume la API propia del backend; **no expone claves privadas en el navegador**.

2. **Backend Orquestador (FastAPI & Python):**
   - Servidor intermedio que actúa como orquestador del agente de IA.
   - Gestiona la memoria contextual de las conversaciones.
   - Resguarda la API Key institucional de forma 100% segura.
   - Documentación OpenAPI/Swagger autogenerada en `/docs`.

3. **Capa de Persistencia (SQLite & SQLAlchemy):**
   - Almacena sesiones e historiales de conversación en una base de datos local SQLite (`backend/copilot.db`).
   - No requiere servicios ni contenedores externos para facilitar la evaluación.

4. **Proveedor LLM:**
   - Integrado con **Google Gemini** (`gemini-3.8-flash`) mediante llamadas REST asíncronas optimizadas.

---

## 🚀 Guía de Inicio Rápido

### 1. Clonar el repositorio y configurar variables de entorno
Crea tu archivo de variables de entorno a partir de la plantilla:

```bash
# Copiar plantilla en el backend
copy backend\.env.example backend\.env
```

Edita `backend/.env` y añade tu clave de API gratuita de Google Gemini:
```env
GEMINI_API_KEY=tu_clave_gemini_aqui
DATABASE_URL=sqlite:///./copilot.db
```

---

### 2. Iniciar el Backend (FastAPI)
Desde la raíz del proyecto (`prouebaSvelte/`), ejecuta:

```bash
# Con uv (recomendado, ultra rápido)
uv run uvicorn backend.main:app --reload --port 8000

# O activando el entorno virtual
.\.venv\Scripts\activate
uvicorn backend.main:app --reload --port 8000
```

* **API Backend:** `http://localhost:8000`
* **Documentación Interactiva Swagger:** `http://localhost:8000/docs`

---

### 3. Iniciar el Frontend (Svelte 5)
En una segunda terminal:

```bash
cd mi-app-svelte
npm install
npm run dev
```

* **Aplicación Web:** `http://localhost:5173`

---

## 📡 Endpoints Principales de la API

* `GET /` — Estado de salud del servicio backend.
* `POST /api/chat` — Envía una consulta al Agente, recupera el historial previo en SQLite, consulta al LLM y persiste la respuesta.
* `GET /api/chat/history/{session_id}` — Devuelve el historial completo de mensajes de una conversación.
* `GET /api/chat/sessions` — Lista todas las sesiones de chat registradas con su conteo de mensajes.
* `DELETE /api/chat/sessions/{session_id}` — Elimina una conversación de la base de datos.
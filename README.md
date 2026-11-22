# 🎓 Copiloto Académico FIUNA — Plataforma Inteligente de Acompañamiento y Predicción

Plataforma web interactiva desarrollada para estudiantes de la Facultad de Ingeniería de la Universidad Nacional de Asunción (**FIUNA**). Combina un portal de gestión académica, visualización de historial curricular, un simulador de notas, un **Agente Conversacional con Google Gemini** y **5 modelos de Machine Learning y Deep Learning** (clásicos y de series temporales) para estimar probabilidades de aprobación.

> 🌐 **Frontend publicado en Vercel:** `https://fiunai-helper.vercel.app/` (conectado vía **Cloudflare Tunnel HTTPS** al backend FastAPI local).  
> 📘 **Documentación académica por asignatura:** ver [DOCUMENTACION_IA_Y_LPV.md](./DOCUMENTACION_IA_Y_LPV.md).

---

## 🧠 Análisis de Arquitectura y Estado Actual del Proyecto

El sistema sigue una arquitectura **cliente-servidor desacoplada** para garantizar seguridad, persistencia local y facilidad de despliegue sin servicios externos pesados:

### 1. Frontend (`mi-app-svelte/`)
- **Tecnologías:** Svelte 5 (Runes `$state`, `$derived`, `$props`), SvelteKit, TypeScript estricto y Tailwind CSS.
- **Vistas implementadas (`src/routes/`):**
  - `/` — **Portal de Acceso & Vinculación InsWeb:** Registro e inicio de sesión local (PBKDF2-HMAC-SHA256), acceso en modo invitado, vinculación con INSWEB y monitor de scraping.
  - `/dashboard` — **Dashboard Académico:** Resumen de promedio general (PPG), materias en curso, evaluaciones recientes y métricas de rendimiento.
  - `/agente-ia-pronosticos` — **Simulador Predictivo & Copiloto IA:** Simulador paramétrico de parciales, escenarios de examen final y chat conectado al agente LLM.
  - `/historial-malla-curricular` — **Historial Académico y Malla Curricular:** Visualización de asignaturas aprobadas, notas finales y actas sincronizadas.
- **Seguridad:** No expone claves de API de IA en el navegador; todas las consultas pasan por el backend FastAPI.

### 2. Backend Orquestador (`backend/`)
- **Tecnologías:** FastAPI, Uvicorn, SQLAlchemy, Pydantic v2 y Python 3.14.
- **Persistencia (`copilot.db`):** Base de datos SQLite local administrada con SQLAlchemy (`ChatSession`, `ChatMessage`, `Estudiante`, `Inscripcion`, `Parcial`, `NotaFinal`, `UsuarioLocal`).
- **Seguridad (`backend/services/security.py`):** Contraseñas hasheadas localmente con `PBKDF2-HMAC-SHA256` y *salt* aleatorio.
- **Scraper Institucional (`backend/services/scraper/`):** Automatización con Playwright en modo *headless* para extraer inscripciones, parciales y notas finales desde INSWEB, sanitizarlas (`cleaner.py`) y guardarlas en SQLite (`pipeline.py`).
- **Agente LLM con Function Calling (`backend/services/llm.py`):** Integrado con Google Gemini (`gemini-3.5-flash-lite`) usando memoria conversacional persistente e invocación automática de herramientas locales de predicción.

### 3. Motor de Inteligencia Artificial (`backend/services/ml/`)
Los modelos ya se encuentran **entrenados y serializados** en `backend/services/ml/saved_models/` (listos para usarse sin necesidad de re-entrenar al iniciar):

| Paradigma | Modelo | Uso Principal | Ubicación |
| :--- | :--- | :--- | :--- |
| **ML Clásico (Tabulares)** | 1. Regresión Logística (+ StandardScaler)<br>2. Árbol de Decisión<br>3. Random Forest (200 árboles) | Predicción cuando se cuenta con las notas de proceso (`Primer.Par`, `Segundo.Par`, `TPLab.`). | `predictor.py` |
| **Serie Temporal Clásica** | 4. Ensamble Temporal Multi-Hito (*Gradient Boosting*) | Predicción progresiva en cualquier etapa del semestre (solo 1er Parcial, 1er Parcial + TP, o proceso completo). | `sequential_tracker.py` |
| **Deep Learning Secuencial** | 5. Red Neuronal Recurrente **LSTM** (PyTorch, 2 capas) | Modela secuencias de longitud variable, inercia académica y tendencias continuas con ponderación de desbalance (`pos_weight`). | `lstm_tracker.py` |

---

## 📋 Requisitos Previos (Instalación por única vez)

Antes de empezar, asegúrate de tener instalados estos **3 programas gratuitos** en tu computadora:

1. **Python 3.14 o superior:**  
   Descarga desde [python.org/downloads](https://www.python.org/downloads/).  
   *(En Windows, marca la casilla **"Add python.exe to PATH"** durante la instalación).*
2. **Node.js (versión LTS recomendada, 20 o superior):**  
   Descarga desde [nodejs.org](https://nodejs.org/) (incluye `npm` automáticamente).
3. **uv (Gestor rápido de paquetes Python):**  
   Abre una terminal y ejecuta el comando según tu sistema:
   - **Windows (PowerShell):**
     ```powershell
     powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
     ```
   - **macOS / Linux:**
     ```bash
     curl -LsSf https://astral.sh/uv/install.sh | sh
     ```
   *(Luego cierra y vuelve a abrir tu terminal para que reconozca el comando `uv`).*

---

## 🚀 Guía Paso a Paso para Levantar el Proyecto Localmente

### Paso 1: Descargar el proyecto
Si aún no lo tienes en tu PC, clona el repositorio y entra en la carpeta:

```bash
git clone https://github.com/roquess321/proyectoIA2026.git
cd proyectoIA2026
```
*(Si ya descargaste el archivo ZIP, descomprímelo y abre tu terminal dentro de la carpeta principal del proyecto).*

---

### Paso 2: Configurar la clave gratuita de Google Gemini
El asistente de chat necesita una clave gratuita de Google AI Studio.

1. Ingresa a [aistudio.google.com](https://aistudio.google.com/), inicia sesión con tu cuenta de Google y haz clic en **"Get API key" → "Create API key"**.
2. Copia la clave generada.
3. Crea el archivo de configuración del backend copiando la plantilla:
   - **En Windows (PowerShell o CMD):**
     ```powershell
     copy backend\.env.example backend\.env
     ```
   - **En macOS / Linux:**
     ```bash
     cp backend/.env.example backend/.env
     ```
4. Abre el archivo `backend/.env` con el Bloc de notas o VS Code y reemplaza `TU_CLAVE_GEMINI_AQUI` por tu clave real:
   ```env
   GEMINI_API_KEY=AIzaSyTuClaveRealDeGeminiAqui
   DATABASE_URL=sqlite:///./copilot.db
   ```
   > **Nota:** Guarda el archivo. Nunca subas tu `.env` a GitHub (ya está protegido en `.gitignore`).

---

### Paso 3: Instalar dependencias y encender el Backend (Terminal 1)

Desde la carpeta raíz del proyecto, instala todas las librerías de Python (FastAPI, scikit-learn, PyTorch, Playwright, etc.) con un solo comando:

```bash
uv sync
```

*(Opcional — solo si vas a usar la sincronización en vivo con el portal INSWEB)*: instala el navegador interno de Playwright ejecutando:
```bash
uv run playwright install chromium
```

Ahora inicia el servidor Backend:

```bash
uv run uvicorn backend.main:app --reload --port 8000
```

Si todo salió bien, verás un mensaje indicando:
`Uvicorn running on http://127.0.0.1:8000`

> **Deja esta primera terminal abierta** mientras uses la aplicación.

---

### Paso 4: Instalar dependencias y encender el Frontend (Terminal 2)

Abre una **segunda terminal** en la carpeta raíz del proyecto y ejecuta:

```bash
cd mi-app-svelte
npm install
npm run dev
```

Verás en pantalla:
`➜  Local:   http://localhost:5173/`

---

### Paso 5: ¡Listo! Abre la aplicación en tu navegador

- **Aplicación Web (Frontend):** [http://localhost:5173](http://localhost:5173)
- **Documentación interactiva de la API (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

#### ¿Cómo empezar a probarla?
1. En la pantalla inicial (`/`), puedes **Crear Cuenta** local, usar **Entrar como Invitado** para probar el modo demostración al instante, o vincular tu Cédula con INSWEB si deseas traer datos reales.
2. Navega al menú lateral hacia **Agente IA & Pronósticos** (`/agente-ia-pronosticos`) para mover los deslizadores de notas o chatear con el Copiloto (por ejemplo: *"Saqué 42 en el 1er parcial de Estática, ¿qué probabilidad tengo de aprobar?"*).

---

## 🌐 Despliegue en Producción (Vercel + Cloudflare Tunnel)

La arquitectura final separa la entrega estática/edge en la nube del motor pesado de cómputo y scraping:

- **Frontend en Vercel (`https://fiunai-helper.vercel.app/`):** desplegado directamente desde este repositorio con **Root Directory** en `mi-app-svelte` (`SvelteKit`).
- **Exposición segura del Backend local (Cloudflare Tunnel):** como el backend ejecuta **PyTorch CPU + scikit-learn + Playwright Chromium** de forma simultánea y los planes gratuitos estándar limitan la RAM a `512 MB` (además de que Hugging Face Spaces restringió los Spaces Docker a plan PRO), el backend corre localmente sin restricciones de memoria ni costos y se expone por HTTPS mediante `cloudflared`.
- **Arranque en un solo paso (`iniciar_servidor_nube.ps1`):**
  ```powershell
  .\iniciar_servidor_nube.ps1
  ```
  Verifica si el puerto `8000` ya está escuchando (si no, inicia `uvicorn backend.main:app --host 127.0.0.1 --port 8000`), abre el túnel HTTPS en `cloudflared` e imprime el enlace listo para la defensa.
- **Reconexión en caliente sin redeploy (`?api=`):** [api-base.ts](./mi-app-svelte/src/lib/services/api-base.ts) lee `VITE_API_URL` por defecto, pero permite cambiar la URL del backend al instante abriendo `https://fiunai-helper.vercel.app/?api=<NUEVA_URL_HTTPS>` (se guarda en `localStorage` bajo `fiunai_api_base_override`, o `?api=reset` para limpiar).
- **Portabilidad Docker lista:** el repositorio incluye [Dockerfile](./Dockerfile), [requirements-docker.txt](./requirements-docker.txt), [.dockerignore](./.dockerignore) y el dataset compacto [dataset_fiuna_compact.csv](./backend/services/ml/dataset_fiuna_compact.csv) (`29,687` registros deduplicados, `1.12 MB`) listos para desplegar en cualquier servidor Docker con `≥ 1 GB` de RAM (puerto `${PORT:-7860}`).

---

## 📁 Estructura Resumida del Repositorio

```text
proyectoIA2026/
├── Dockerfile                      # Imagen Python 3.14-slim + Torch CPU + Playwright Chromium (puerto 7860)
├── requirements-docker.txt         # Dependencias backend fijadas para contenedor (CPU-only PyTorch)
├── .dockerignore                   # Exclusión de .env, DB local y carpetas privadas de GitHub/defensa
├── iniciar_servidor_nube.ps1       # Script PowerShell: levanta Uvicorn (8000) + Cloudflare Tunnel HTTPS
├── DOCUMENTACION_IA_Y_LPV.md       # Implicaciones y aplicaciones detalladas por materia (IA + LPV)
├── data/horarios_oficiales/        # Horarios oficiales FIUNA en JSON (Res. CD Nº 1637/2026/006)
├── backend/
│   ├── main.py                     # API FastAPI, CORS (*.vercel.app), SSE y rutas REST
│   ├── database.py                 # Conexión SQLite y sesiones SQLAlchemy
│   ├── models.py                   # Tablas ORM (Chat, Estudiantes, Notas, Usuarios)
│   ├── schemas.py                  # Validación de entradas/salidas con Pydantic
│   ├── .env.example                # Plantilla de variables de entorno
│   └── services/
│       ├── llm.py                  # Cliente Gemini + Function Calling
│       ├── schedule.py             # Lector y filtro de horarios oficiales por carrera
│       ├── security.py             # Hashing PBKDF2-HMAC-SHA256
│       ├── scraper/                # Pipeline Playwright para INSWEB
│       └── ml/
│           ├── dataset_fiuna_compact.csv # Dataset compacto deduplicado (29,687 filas, 1.12 MB)
│           ├── predictor.py        # Inferencia de los 5 modelos y reentrenamiento por materia
│           ├── sequential_tracker.py # Ensamble Temporal Multi-Hito (Gradient Boosting)
│           ├── lstm_tracker.py     # Red Neuronal Recurrente LSTM (PyTorch)
│           ├── trainer.py          # Entrenamiento clásico y complementación de cohorte
│           └── saved_models/       # Pesos pre-entrenados (.joblib, .pt, .json)
├── mi-app-svelte/
│   ├── package.json                # Dependencias Node / SvelteKit
│   ├── .env.example                # Plantilla VITE_API_URL
│   └── src/
│       ├── routes/                 # Páginas: /, /dashboard, /agente-ia-pronosticos, /historial-malla-curricular
│       └── lib/
│           ├── components/         # Componentes Svelte 5 (Dashboard, Simulador, Historial)
│           └── services/           # api-base.ts (override ?api=), auth.ts, gemini.ts, scraper.ts, etc.
├── pyproject.toml                  # Dependencias Python y configuración uv/Pyright
├── uv.lock                         # Versiones exactas fijadas de Python
└── README.md                       # Esta guía
```

---

## 📡 Endpoints Principales de la API (`http://localhost:8000`)

| Categoría | Método y Ruta | Descripción |
| :--- | :--- | :--- |
| **Salud** | `GET /` | Verifica que el backend está activo. |
| **Chat IA** | `POST /api/chat` | Envía un mensaje al Copiloto Gemini con memoria SQLite y herramientas ML. |
| **Chat IA** | `GET /api/chat/sessions` | Lista las sesiones de chat guardadas. |
| **Chat IA** | `GET /api/chat/history/{session_id}` | Obtiene el historial de mensajes de una sesión. |
| **Chat IA** | `DELETE /api/chat/sessions/{session_id}` | Elimina una sesión de chat. |
| **Machine Learning** | `POST /api/ml/predict` | Evalúa los 5 modelos (Regresión Logística, Árbol, Random Forest, Ensamble Temporal y LSTM). |
| **Machine Learning** | `POST /api/ml/predict-sequential` | Predicción temporal progresiva desde el 1er parcial (Hitos 1, 2 o 3). |
| **Machine Learning** | `GET /api/ml/models` | Lista el catálogo de modelos entrenados disponibles. |
| **Machine Learning** | `POST /api/ml/retrain` | Reentrena bajo demanda los 5 modelos para una asignatura específica. |
| **Autenticación** | `POST /api/auth/register` | Crea una cuenta local segura. |
| **Autenticación** | `POST /api/auth/login-local` | Inicia sesión con usuario/cédula y contraseña local. |
| **Autenticación** | `POST /api/auth/login` | Login / sincronización con INSWEB. |
| **Autenticación** | `POST /api/auth/link-insweb` | Vincula y sincroniza materias desde INSWEB a una cuenta local. |
| **Autenticación / SSE** | `POST /api/auth/link-insweb/stream` | Vincula y sincroniza INSWEB transmitiendo telemetría en vivo vía SSE. |
| **Estudiantes / Scraper** | `GET /api/scraper/status` | Diagnóstico de salud de Playwright, conectividad INSWEB y estado SQLite. |
| **Estudiantes / Scraper** | `POST /api/scraper/sync` | Ejecuta el scraper de Playwright bajo demanda. |
| **Horarios** | `GET /api/horarios/examenes` | Lee el calendario oficial FIUNA desde `data/horarios_oficiales/` filtrado por carrera. |
| **Estudiantes / Scraper** | `GET /api/estudiantes/{cedula}` | Ficha académica completa (inscripciones, parciales y notas finales). |
| **Estudiantes / Scraper** | `GET /api/estudiantes/{cedula}/inscripciones` | Materias matriculadas del periodo. |
| **Estudiantes / Scraper** | `GET /api/estudiantes/{cedula}/parciales` | Evaluaciones parciales registradas. |
| **Estudiantes / Scraper** | `GET /api/estudiantes/{cedula}/notas` | Historial de notas finales. |

---

## 🛠️ Solución de Problemas Frecuentes

- **`uv` no se reconoce como comando en Windows:** Cierra y vuelve a abrir la terminal después de instalar `uv`. Si persiste, reinicia la sesión o usa el entorno virtual directamente (`.venv\Scripts\activate` y luego `uvicorn backend.main:app --reload --port 8000`).
- **El chat responde error 502 o dice que falta `GEMINI_API_KEY`:** Verifica que creaste el archivo `backend/.env` (no solo `.env.example`), que pegaste una clave válida sin comillas ni espacios extra, y reinicia la terminal del backend.
- **Error de conexión con `http://localhost:8000` en el navegador:** Asegúrate de que la **Terminal 1** (FastAPI) siga abierta y corriendo sin errores.
- **Puerto `8000` o `5173` ocupado:** Puedes iniciar el backend en otro puerto (`--port 8001`) y crear un archivo `mi-app-svelte/.env` con `VITE_API_URL=http://localhost:8001`.
- **Error de Playwright al sincronizar INSWEB:** Ejecuta `uv run playwright install chromium` para descargar el navegador requerido por el scraper.

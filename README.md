# MediaGroup LATAM - Pipeline de Análisis Inteligente

**Proyecto Final - Fundamentos de Arquitectura LLM (BSG Institute)**

Este proyecto implementa un pipeline automatizado para el análisis de artículos periodísticos para el cliente **MediaGroup LATAM**. El sistema ingiere textos vía Webhook, los procesa con un Agente Inteligente (usando Google ADK) y devuelve un análisis estructurado (Categoría, Sentimiento y Resumen SEO) en tiempo real a través de un Chat interactivo.

---

## Arquitectura y Stack Tecnológico

La solución está diseñada bajo una arquitectura serverless en Google Cloud Platform (GCP), separada en dos entornos:

*   **Backend (Python/FastAPI):** Desplegado en **Cloud Run**.
    *   **IA:** Google Agent Development Kit (ADK) + Vertex AI (Modelo Gemini 3.5 Flash en endpoint global).
    *   **Seguridad:** JWT (JSON Web Tokens) y Secret Manager.
    *   **Resiliencia:** Rate Limiting (SlowAPI) y Circuit Breaker (PyBreaker).
    *   **Base de Datos:** Firestore (persistencia de métricas y resultados).
    *   **Observabilidad:** Logging estructurado en JSON con trazabilidad de costos y latencia.
*   **Frontend (React/Vite):** Interfaz de usuario con Tailwind CSS. Incluye Dashboard de métricas reales y Chat con visualización del ciclo ReAct.

*(El diagrama detallado de la arquitectura C4 se encuentra en la carpeta `docs/`).*

---

## Estructura del Repositorio

```text
media-group-pipeline/
├── backend/
│   ├── app/
│   │   ├── agent/            # Configuración del Agente ADK y Tools
│   │   ├── api/              # Endpoints de la API (Auth, Webhook, Dashboard)
│   │   ├── core/             # Configuración, Seguridad JWT y Logging
│   │   ├── services/         # Pipeline asíncrono y conexión a Firestore
│   │   ├── __init__.py
│   │   └── main.py           # Punto de entrada de FastAPI
│   ├── __init__.py
│   ├── Dockerfile            # Imagen de Docker para Cloud Run
│   └── requirements.txt      # Dependencias de Python
├── docs/
│   └── arquitectura_c4.png   # Diagrama de Arquitectura (Entregable E1)
├── frontend/
│   ├── public/               # Archivos estáticos (favicon, icons)
│   ├── src/
│   │   ├── assets/
│   │   ├── components/       # Componentes reutilizables (Sidebar, Cards)
│   │   ├── pages/            # Vistas (Dashboard, Chat, Login)
│   │   ├── App.css
│   │   ├── App.jsx           # Enrutador principal
│   │   ├── api.js            # Configuración de Axios
│   │   ├── index.css
│   │   └── main.jsx
│   ├── eslint.config.js
│   ├── index.html
│   ├── package.json          # Dependencias de Node
│   └── vite.config.js
├── Makefile                  # Comandos de instalación y ejecución
├── README.md                 # Documentación del proyecto
└── requirements.txt          # (Opcional) Dependencias globales
```

## Instalación del entorno local

### Git y repositorio

```bash
sudo apt update
sudo apt install git -y

git clone <RL-DEL-REPOSITORIO>
cd pipeline-llm
```

### Python y Make (Setup y Backend)

Instala los requisitos:

```bash
sudo apt install python3 python3-venv make -y
```

Instala el entorno virtual con las dependencias:

```bash
make setup
```

Instala las dependencias del backend desde la raíz del proyecto:

```bash
make backend
```

Consulta los comandos disponibles:

```bash
make help
```

### Node.js y NPM (Frontend)

Instala NVM y Node.js 20:

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc

nvm install 20
nvm use 20
```

Instala las dependencias del frontend:

```bash
cd frontend
npm install
cd ..
```

### Google Cloud (Opcional)

Necesario para desplegar el backend en Cloud Run o utilizar servicios de Google Cloud.

**Instalar la CLI y autenticarte:**

```bash
sudo snap install google-cloud-cli --classic

gcloud auth login
gcloud auth application-default login
gcloud config set project TU_PROJECT_ID
```

**Crear los secretos:**

```bash
echo -n "TU_CLAVE_JWT" | gcloud secrets create JWT_SECRET_KEY --data-file=-
echo -n "TU_PROJECT_ID" | gcloud secrets create GCP_PROJECT_ID --data-file=-
```

**Crear la cuenta de servicio:**

```bash
gcloud iam service-accounts create media-group-sa \
  --display-name="MediaGroup Pipeline SA"
```

**Asignar permisos:**

```bash
gcloud projects add-iam-policy-binding TU_PROJECT_ID \
  --member="serviceAccount:media-group-sa@TU_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding TU_PROJECT_ID \
  --member="serviceAccount:media-group-sa@TU_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

gcloud projects add-iam-policy-binding TU_PROJECT_ID \
  --member="serviceAccount:media-group-sa@TU_PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/datastore.user"
```

**Desplegar en Cloud Run:**

```bash
cd backend

gcloud run deploy media-group-backend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --service-account media-group-sa@TU_PROJECT_ID.iam.gserviceaccount.com \
  --set-secrets="JWT_SECRET_KEY=JWT_SECRET_KEY:latest,GCP_PROJECT_ID=GCP_PROJECT_ID:latest" \
  --set-env-vars="GCP_REGION=global,JWT_ALGORITHM=HS256,ACCESS_TOKEN_EXPIRE_MINUTES=30"
```

Actualiza la URL del backend en `frontend/src/api.js`.

> Sustituye `TU_PROJECT_ID` y `TU_CLAVE_JWT` por los valores correspondientes. Habilita las API necesarias y concede a la cuenta de servicio acceso a los secretos. No subas credenciales al repositorio.

---

## Endpoints principales

Documentación interactiva: `http://localhost:8080/docs`

| Método | Endpoint | Descripción | Autenticación |
|---|---|---|---|
| POST | `/api/v1/auth/login` | Iniciar sesión y obtener JWT | Pública |
| POST | `/api/v1/webhook/ingest` | Enviar un artículo para procesar | Bearer JWT |
| GET | `/api/v1/webhook/result/{task_id}` | Consultar el resultado del procesamiento | Bearer JWT |
| GET | `/api/v1/dashboard/metrics` | Consultar métricas de Firestore | Bearer JWT |
| GET | `/health` | Verificar el estado del backend | Pública |

---

## Ejecución del proyecto

### Opción A. Backend en Cloud Run

Configura la URL desplegada en `frontend/src/api.js`.

```bash
make frontend
```

Abre `http://localhost:5173` en el navegador.

### Opción B. Ejecución local completa

**Terminal 1 — Backend** (desde la raíz):

```bash
make backend
```

**Terminal 2 — Frontend** (desde la raíz):

```bash
make frontend
```

Abre `http://localhost:5173`.

> Utiliza las credenciales de desarrollo configuradas en el backend. No uses credenciales de ejemplo en producción.

---

## Verificación de la instalación

1. Abre `http://localhost:5173` e inicia sesión.
2. En **Chat Agente**, envía un artículo periodístico.
3. Verifica que el agente finalice el procesamiento y devuelva un resultado.
4. En **Dashboard**, comprueba las métricas registradas.
5. Verifica el estado del backend:

```bash
curl http://localhost:8080/health
```
## Material Adicional
- Arquitectura C4: [docs/arquitectura_c4.png](docs/arquitectura_c4.png)
- RFC Tecnico: [docs/RFC_tecnico](docs/RFC_tecnico)
- Analisis de Costos: [docs/analisis_costos.xlsx](docs/analisis_costos.xlsx)

> para mas información en costos consulte las siguientes ligas:
- https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing
- https://cloud.google.com/products/gemini-enterprise-agent-platform/pricing#pipelines
- https://cloud.google.com/run/pricing
- https://cloud.google.com/firestore/pricing
- https://cloud.google.com/secret-manager/pricing

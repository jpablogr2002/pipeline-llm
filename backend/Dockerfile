# Usamos una imagen oficial ligera de Python
FROM python:3.12-slim

# Evita que Python escriba archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configuración para usar Vertex AI en lugar de la API de Google Generative AI
ENV GOOGLE_GENAI_USE_VERTEXAI=true

# Establecemos el directorio de trabajo
WORKDIR /app

# Instalamos dependencias del sistema necesarias (curl para healthchecks, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiamos e instalamos los requerimientos de Python primero (para aprovechar el cache de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código
COPY . .

# Exponemos el puerto que usa Cloud Run por defecto (8080)
EXPOSE 8080

# Comando para arrancar Uvicorn en producción (sin --reload)
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]
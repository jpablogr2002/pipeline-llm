# ==========================================
# Variables de Entorno y Rutas
# ==========================================
BACKEND_DIR = backend
FRONTEND_DIR = frontend
VENV_DIR = .venv
PYTHON = $(VENV_DIR)/bin/python
PIP = $(VENV_DIR)/bin/pip

.PHONY: help install run clean test freeze

# ==========================================
# Comandos Principales
# ==========================================
help:
	@echo "Comandos disponibles:"
	@echo "  make install   - Crea el entorno virtual e instala dependencias"
	@echo "  make backend       - Levanta el servidor FastAPI en modo desarrollo"
	@echo "  make frontend      - Levanta el servidor de React en modo desarrollo"
	@echo "  make freeze    - Actualiza requirements.txt con lo instalado"
	@echo "  make clean     - Elimina el entorno virtual y archivos temporales"

install:
	@echo "Creando entorno virtual..."
	python3 -m venv $(VENV_DIR)
	@echo "Actualizando pip..."
	$(PIP) install --upgrade pip
	@echo "Instalando dependencias..."
	$(PIP) install -r requirements.txt
	@echo "Instalación completada. Activa el entorno con: source $(VENV_DIR)/bin/activate"

backend:
	@echo "Iniciando servidor FastAPI..."
	# Se asume que tienes un archivo .env con tus variables (PROJECT_ID, etc.)
	cd $(BACKEND_DIR) && $(VENV_DIR)/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080

frontend:
	@echo "Iniciando servidor de React..."
	cd $(FRONTEND_DIR) && npm run dev

freeze:
	@echo "Actualizando requirements.txt..."
	$(PIP) freeze > requirements.txt

clean:
	@echo "Limpiando entorno..."
	rm -rf $(VENV_DIR)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "Limpieza completada."
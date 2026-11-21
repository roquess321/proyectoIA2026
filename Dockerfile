FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOME=/home/user \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    PYTHONPATH=/app:/app/backend

# Crear usuario no-root requerido por Hugging Face Spaces (UID 1000)
RUN useradd -m -u 1000 user

WORKDIR /app

# Instalar dependencias Python (CPU-only PyTorch) y Chromium con dependencias del sistema
COPY requirements-docker.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements-docker.txt \
    && mkdir -p /ms-playwright \
    && playwright install chromium --with-deps \
    && chmod -R a+rX /ms-playwright \
    && rm -rf /var/lib/apt/lists/*

# Copiar backend, dataset compacto, modelos entrenados y horarios oficiales
COPY --chown=user:user backend/ ./backend/
COPY --chown=user:user data/horarios_oficiales/ ./data/horarios_oficiales/
RUN mkdir -p /app/data && chown -R user:user /app/data

USER user

EXPOSE 7860

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-7860}"]

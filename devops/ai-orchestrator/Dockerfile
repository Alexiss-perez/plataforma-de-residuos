FROM python:3.12-slim

WORKDIR /app

# Instalar dependencias (cuando el Ing. de IA las defina)
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# Placeholder: el Ing. de IA llenará este contenido
COPY app/ ./app/

# Health check endpoint
HEALTHCHECK --interval=15s --timeout=5s --retries=3 \
  CMD curl -sf http://localhost:8000/health || exit 1

EXPOSE 8000

# Placeholder - el Ing. de IA reemplazará con el comando real
CMD ["echo", "ai-orchestrator: pendiente de implementacion por Ing. de IA"]

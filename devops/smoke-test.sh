#!/bin/bash
set -euo pipefail

# ============================================================
# EcoMatch - Smoke test del stack completo
# Verifica que BD + Backend + IA levanten y respondan.
# ============================================================

echo "=== EcoMatch - Smoke Test ==="
echo ""

# 1. Verificar .env
if [ ! -f .env ]; then
  echo "❌ No existe .env. Copia .env.example a .env y rellena los valores."
  exit 1
fi
echo "✅ .env existe"

# 2. Levantar stack
echo ""
echo ">>> Levantando stack..."
docker compose up --build -d

# 3. Esperar que los servicios estén healthy
echo ""
echo ">>> Esperando que los servicios estén healthy..."
echo "    (esto puede tomar 30-60 segundos)"

MAX_WAIT=90
WAITED=0

check_health() {
  local name=$1
  local url=$2
  if curl -sf "$url" > /dev/null 2>&1; then
    echo "✅ $name healthy"
    return 0
  else
    return 1
  fi
}

while [ $WAITED -lt $MAX_WAIT ]; do
  DB_OK=false; BACK_OK=false; AI_OK=false

  docker exec db-ecmatch pg_isready -U ecmatch > /dev/null 2>&1 && DB_OK=true
  curl -sf http://localhost:8000/health > /dev/null 2>&1 && BACK_OK=true
  curl -sf http://localhost:8001/health > /dev/null 2>&1 && AI_OK=true

  if $DB_OK && $BACK_OK && $AI_OK; then
    break
  fi

  sleep 3
  WAITED=$((WAITED + 3))
  echo "    ...esperando (${WAITED}s)"
done

echo ""
echo "=== Resultado ==="
docker exec db-ecmatch pg_isready -U ecmatch > /dev/null 2>&1 && echo "✅ PostgreSQL" || echo "❌ PostgreSQL"
curl -sf http://localhost:8000/health > /dev/null 2>&1 && echo "✅ Backend (FastAPI)" || echo "❌ Backend"
curl -sf http://localhost:8001/health > /dev/null 2>&1 && echo "✅ AI Orchestrator (GLM 5.2)" || echo "❌ AI Orchestrator"

# 4. Probar un chat básico
echo ""
echo "=== Probando chat con el agente ==="
CHAT_RESPONSE=$(curl -sf -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "hola"}' 2>/dev/null || echo "FAIL")

if [ "$CHAT_RESPONSE" != "FAIL" ]; then
  echo "✅ Agente responde:"
  echo "$CHAT_RESPONSE" | jq -r '.response' 2>/dev/null | head -3
else
  echo "❌ Agente no responde"
fi

echo ""
echo "=== Smoke test completado ==="

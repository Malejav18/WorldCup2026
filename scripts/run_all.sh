#!/bin/bash

set -e

# =========================
# CONFIGURACIÓN BASE
# =========================
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND="$ROOT/backend"

cd "$BACKEND"

# Detectar python
if [ -f "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="python3"
fi

echo "Usando Python: $PYTHON"
echo ""

# =========================
# FUNCIÓN PARA LEVANTAR SERVICIOS
# =========================
run_service () {
  NAME=$1
  MODULE=$2
  PORT=$3

  echo "Iniciando $NAME en puerto $PORT..."

  $PYTHON -m uvicorn "$MODULE" \
    --host 127.0.0.1 \
    --port "$PORT" \
    --reload \
    > "$ROOT/log_$NAME.log" 2>&1 &
}

# =========================
# LEVANTAR SERVICIOS
# =========================
run_service "api-gateway"        "api_gateway.main:app"             8000
run_service "auth-service"       "auth_service.app.main:app"        8001
run_service "user-service"       "user_service.app.main:app"        8002
run_service "tournament-service" "tournament_service.app.main:app"  8003
run_service "prediction-service" "prediction_service.app.main:app"  8004
run_service "scoring-service"    "scoring_service.app.main:app"     8005
run_service "ranking-service"    "ranking_service.app.main:app"     8006
run_service "league-service"     "league_service.app.main:app"      8007
run_service "notification-service" "notification_service.app.main:app" 8008

echo ""
echo "🚀 Servicios levantándose..."
echo ""

# =========================
# ENDPOINTS
# =========================
echo "Endpoints:"
echo "  api-gateway         : http://127.0.0.1:8000"
echo "  auth-service        : http://127.0.0.1:8001/docs"
echo "  user-service        : http://127.0.0.1:8002/docs"
echo "  tournament-service  : http://127.0.0.1:8003/docs"
echo "  prediction-service  : http://127.0.0.1:8004/docs"
echo "  scoring-service     : http://127.0.0.1:8005/docs"
echo "  ranking-service     : http://127.0.0.1:8006/docs"
echo "  league-service      : http://127.0.0.1:8007/docs"
echo "  notification-service: http://127.0.0.1:8008/docs"

echo ""
echo "📄 Logs disponibles en archivos log_*.log"
echo "⛔ Presiona CTRL+C para detener todo"

# =========================
# ESPERAR Y MATAR TODO
# =========================
trap "echo 'Deteniendo servicios...'; kill 0" SIGINT
wait
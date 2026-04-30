#!/usr/bin/env bash

set -euo pipefail

# ── Rutas ─────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND="$ROOT/backend"
FRONTEND="$ROOT/frontend"
PID_FILE="/tmp/worldcup2026_pids.txt"

# ── Colores ───────────────────────────────────────
GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; RESET='\033[0m'

info() { echo -e "${CYAN}[info]${RESET}  $*"; }
ok()   { echo -e "${GREEN}[ok]${RESET}    $*"; }
warn() { echo -e "${YELLOW}[warn]${RESET}  $*"; }

# ── Flags ─────────────────────────────────────────
DO_FRONTEND=false
DO_STOP=false

for arg in "$@"; do
  case "$arg" in
    --frontend) DO_FRONTEND=true ;;
    --stop)     DO_STOP=true ;;
  esac
done

# ── Stop ─────────────────────────────────────────
if $DO_STOP; then
  if [[ -f "$PID_FILE" ]]; then
    echo "🛑 Deteniendo servicios..."
    while read -r pid; do
      kill "$pid" 2>/dev/null || true
    done < "$PID_FILE"
    rm -f "$PID_FILE"
    ok "Servicios detenidos"
  fi
  exit 0
fi

# ── Verificar Python activo ───────────────────────
if ! command -v python &>/dev/null; then
  echo "❌ No hay entorno activo. Activa tu venv primero:"
  echo "   source .venv/bin/activate"
  exit 1
fi

ok "Usando Python: $(which python)"

# ── Arranque ──────────────────────────────────────
> "$PID_FILE"

start_service() {
  local name="$1"
  local module="$2"
  local port="$3"
  local log_file="/tmp/worldcup_${name}.log"

  info "Arrancando $name en puerto $port..."

  cd "$BACKEND"

  # Ejecuta servicio mostrando logs en terminal + guardando en archivo
  python -m uvicorn "$module" \
    --host 127.0.0.1 \
    --port "$port" \
    --reload \
    2>&1 | tee "$log_file" &

  echo $! >> "$PID_FILE"
  ok "$name corriendo en $port"
  sleep 0.3
}

echo "🚀 Iniciando microservicios..."

start_service "api-gateway"          "api_gateway.main:app"              8000
start_service "auth-service"         "auth_service.app.main:app"         8001
start_service "user-service"         "user_service.app.main:app"         8002
start_service "tournament-service"   "tournament_service.app.main:app"   8003
start_service "prediction-service"   "prediction_service.app.main:app"   8004
start_service "scoring-service"      "scoring_service.app.main:app"      8005
start_service "ranking-service"      "ranking_service.app.main:app"      8006
start_service "league-service"       "league_service.app.main:app"       8007
start_service "notification-service" "notification_service.app.main:app" 8008

# ── Frontend ─────────────────────────────────────
if $DO_FRONTEND; then
  info "Arrancando frontend..."
  cd "$FRONTEND"
  npm run dev >> "/tmp/worldcup_frontend.log" 2>&1 &
  echo $! >> "$PID_FILE"
  ok "Frontend en http://127.0.0.1:5173"
fi

echo ""
echo "✅ Todo corriendo"
echo "👉 Stop: ./run_all.sh --stop"

# ── Ctrl+C ───────────────────────────────────────
trap '
echo "🛑 Deteniendo..."
while read -r pid; do kill "$pid" 2>/dev/null; done < "$PID_FILE"
rm -f "$PID_FILE"
exit 0
' SIGINT

wait
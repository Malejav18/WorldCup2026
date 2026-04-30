#!/usr/bin/env bash

set -e

echo "🌱 Cargando datos del torneo (equipos, grupos y partidos)..."

# ── Obtener rutas ───────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND="$ROOT/backend"

# ── Detectar Python del venv ────────────────────
VENV_PYTHON="$ROOT/.venv/bin/python"

if [ -f "$VENV_PYTHON" ]; then
    PYTHON="$VENV_PYTHON"
else
    PYTHON="python3"
fi

echo "🐍 Usando: $PYTHON"

# ── Ir al backend ───────────────────────────────
cd "$BACKEND" || exit

# ── Ejecutar seed ───────────────────────────────
$PYTHON -m tournament_service.app.seed.seed_tournament

echo "✅ Datos cargados correctamente"
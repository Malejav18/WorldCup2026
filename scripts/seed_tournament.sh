#!/bin/bash

set -e

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

cd "$ROOT/backend"

# Detectar python del virtualenv o usar sistema
if [ -f "$ROOT/.venv/bin/python" ]; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="python3"
fi

# Ejecutar seed
$PYTHON -m tournament_service.app.seed.seed_tournament
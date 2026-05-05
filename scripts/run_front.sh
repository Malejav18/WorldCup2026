#!/bin/bash

# Detener si hay error
set -e

# Obtener ruta raíz del proyecto
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Ir a frontend
cd "$ROOT/frontend"

# Instalar dependencias si no existen
if [ ! -d "node_modules" ]; then
  echo "Instalando dependencias por primera vez..."
  npm install
fi

# Ejecutar servidor
npm run dev
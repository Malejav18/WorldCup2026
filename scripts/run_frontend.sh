#!/bin/bash

echo "🚀 Iniciando frontend (React)..."

BASE="/Users/maleja/Downloads/ARQUITECTURA_SOFT/corte2/worldcup2026/Worldcup2026"

# Ir a la carpeta frontend
cd "$BASE/frontend" || exit

# Verificar si existen node_modules
if [ ! -d "node_modules" ]; then
    echo "📦 Instalando dependencias por primera vez..."
    npm install
fi
# Ejecutar servidor de desarrollo
npm run dev
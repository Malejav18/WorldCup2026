# Arranca el dev server del frontend React en http://127.0.0.1:5173
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root "frontend")

if (-not (Test-Path "node_modules")) {
    Write-Host "Instalando dependencias por primera vez..."
    npm install
}

npm run dev

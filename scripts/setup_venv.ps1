# Crea .venv en la raiz del repo e instala dependencias.
# Ejecutar una sola vez tras clonar:  .\scripts\setup_venv.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path ".venv")) {
    Write-Host "Creando entorno virtual en .venv ..."
    python -m venv .venv
}

$venvPython = Join-Path $root ".venv\Scripts\python.exe"
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r (Join-Path $root "backend\requirements.txt")

Write-Host ""
Write-Host "Listo. Ahora:"
Write-Host "  1) Copia backend\.env.example -> backend\.env"
Write-Host "  2) Arranca auth-service:   .\scripts\run_auth_service.ps1"

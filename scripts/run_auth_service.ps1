# Arranca auth-service en el puerto 8001.
# Ejecutar desde la raiz del repo:  .\scripts\run_auth_service.ps1

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root "backend")

# Usa el .venv si existe; si no, usa el python del PATH.
$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$python = if (Test-Path $venvPython) { $venvPython } else { "python" }

& $python -m uvicorn auth_service.app.main:app --host 127.0.0.1 --port 8001 --reload

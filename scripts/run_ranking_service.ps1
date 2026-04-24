# Arranca ranking-service en el puerto 8006.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root "backend")

$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$python = if (Test-Path $venvPython) { $venvPython } else { "python" }

& $python -m uvicorn ranking_service.app.main:app --host 127.0.0.1 --port 8006 --reload

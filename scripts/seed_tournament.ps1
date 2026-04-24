# Carga los 48 equipos, 12 grupos y 72 partidos de fase de grupos en tournament.db.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location (Join-Path $root "backend")

$venvPython = Join-Path $root ".venv\Scripts\python.exe"
$python = if (Test-Path $venvPython) { $venvPython } else { "python" }

& $python -m tournament_service.app.seed.seed_tournament

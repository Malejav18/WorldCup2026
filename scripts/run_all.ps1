# Arranca todos los servicios implementados cada uno en una ventana de PowerShell aparte.
# A medida que se completen las fases, este script se ira ampliando.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$scripts = $PSScriptRoot

$services = @(
    @{ Name = "api-gateway";        Script = (Join-Path $scripts "run_api_gateway.ps1") }
    @{ Name = "auth-service";       Script = (Join-Path $scripts "run_auth_service.ps1") }
    @{ Name = "user-service";       Script = (Join-Path $scripts "run_user_service.ps1") }
    @{ Name = "tournament-service"; Script = (Join-Path $scripts "run_tournament_service.ps1") }
    @{ Name = "prediction-service"; Script = (Join-Path $scripts "run_prediction_service.ps1") }
    @{ Name = "scoring-service";    Script = (Join-Path $scripts "run_scoring_service.ps1") }
    @{ Name = "ranking-service";    Script = (Join-Path $scripts "run_ranking_service.ps1") }
    @{ Name = "league-service";     Script = (Join-Path $scripts "run_league_service.ps1") }
    @{ Name = "notification-service"; Script = (Join-Path $scripts "run_notification_service.ps1") }
)

foreach ($svc in $services) {
    Write-Host "Abriendo ventana para $($svc.Name)..."
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "`"$($svc.Script)`""
    Start-Sleep -Milliseconds 400
}

Write-Host ""
Write-Host "Servicios arrancando. Endpoints:"
Write-Host "  api-gateway        : http://127.0.0.1:8000"
Write-Host "  auth-service       : http://127.0.0.1:8001/docs"
Write-Host "  user-service       : http://127.0.0.1:8002/docs"
Write-Host "  tournament-service : http://127.0.0.1:8003/docs"
Write-Host "  prediction-service : http://127.0.0.1:8004/docs"
Write-Host "  scoring-service    : http://127.0.0.1:8005/docs"
Write-Host "  ranking-service    : http://127.0.0.1:8006/docs"
Write-Host "  league-service     : http://127.0.0.1:8007/docs"
Write-Host "  notification-service: http://127.0.0.1:8008/docs"

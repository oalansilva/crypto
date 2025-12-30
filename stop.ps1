# stop.ps1 - Script para parar todos os servidores

Write-Host "🛑 Parando servidores..." -ForegroundColor Cyan

# Parar processos Python (backend)
Write-Host "`nParando Backend..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Parar processos Node (frontend)
Write-Host "Parando Frontend..." -ForegroundColor Yellow
Get-Process node -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*npm*" -or $_.CommandLine -like "*vite*" } | Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host "`n✅ Servidores parados!" -ForegroundColor Green

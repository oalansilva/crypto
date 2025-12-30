# start.ps1 - Script to start the project correctly

Write-Host "Iniciando Crypto Backtester..." -ForegroundColor Cyan

# 1. Check if venv exists
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "Virtual environment nao encontrado!" -ForegroundColor Red
    Write-Host "Execute: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# 2. Init DB if needed
if (-not (Test-Path "backend\backtest.db")) {
    Write-Host "Inicializando banco de dados..." -ForegroundColor Yellow
    Set-Location backend
    ..\venv\Scripts\python init_db.py
    Set-Location ..
    Write-Host "Banco de dados criado!" -ForegroundColor Green
}

# 3. Start Backend
Write-Host "Iniciando Backend (porta 8000)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\backend'; ..\venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"
Start-Sleep -Seconds 3

# 4. Check Backend Health
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "Backend rodando em http://localhost:8000" -ForegroundColor Green
}
catch {
    Write-Host "Backend pode nao ter iniciado corretamente" -ForegroundColor Yellow
}

# 5. Start Frontend
Write-Host "Iniciando Frontend (porta 5173)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; npm run dev"
Start-Sleep -Seconds 3

Write-Host "Projeto iniciado!" -ForegroundColor Green
Write-Host "URLs:" -ForegroundColor Cyan
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Pressione Ctrl+C nas janelas abertas para parar os servidores" -ForegroundColor Gray

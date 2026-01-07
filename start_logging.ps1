# Stop everything first
.\stop.ps1

Write-Host "Iniciando Backend com logging..." -ForegroundColor Cyan

$backendDir = "$PWD\backend"
$logFile = "$backendDir\full_execution_log.txt"
$venvPython = "$PWD\.venv\Scripts\python.exe"

# Command to run: cd to backend, run uvicorn through python, redirect ALL output to file
# We use cmd /c for reliable redirection of both stdout and stderr
$command = "cd /d ""$backendDir"" && ""$venvPython"" -u -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload > ""$logFile"" 2>&1"

Write-Host "Comando Backend: $command" -ForegroundColor Gray

# Start backend process hidden or minimized, let it write to file
Start-Process cmd -ArgumentList "/c", "$command" -WindowStyle Minimized

Write-Host "Backend iniciado! Logs em: $logFile" -ForegroundColor Green

# Start Frontend
Write-Host "Iniciando Frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "Reinicialização completa. Aguardando serviços subirem..."
Start-Sleep -Seconds 5

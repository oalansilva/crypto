# cleanup.ps1 - Script para limpar processos duplicados

Write-Host "🧹 Limpando processos duplicados..." -ForegroundColor Cyan

# 1. Parar todos os processos Python (servidores backend)
Write-Host "`n1. Parando servidores backend antigos..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host "   Parando processo Python (PID: $($_.Id))" -ForegroundColor Gray
    Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
}

# 2. Aguardar um momento
Start-Sleep -Seconds 2

# 3. Verificar portas ocupadas
Write-Host "`n2. Verificando portas..." -ForegroundColor Yellow
$ports = @(8000, 8001, 8002, 8003)
foreach ($port in $ports) {
    $connection = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($connection) {
        $pid = $connection.OwningProcess
        Write-Host "   Porta $port ocupada por PID $pid - Matando processo..." -ForegroundColor Red
        Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    } else {
        Write-Host "   Porta $port livre ✓" -ForegroundColor Green
    }
}

# 4. Limpar banco de dados (opcional - resetar backtests travados)
Write-Host "`n3. Deseja limpar o banco de dados (resetar backtests)? (S/N)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq "S" -or $response -eq "s") {
    Write-Host "   Removendo backtest.db..." -ForegroundColor Gray
    Remove-Item "backend\backtest.db" -ErrorAction SilentlyContinue
    Write-Host "   Banco de dados removido. Será recriado ao iniciar o backend." -ForegroundColor Green
}

Write-Host "`n✅ Limpeza concluída!" -ForegroundColor Green
Write-Host "`nAgora execute: .\start.ps1" -ForegroundColor Cyan

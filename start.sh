#!/bin/bash
# start.sh - Iniciar backend + frontend

cd "$(dirname "$0")"

echo "🚀 Iniciando Backend (porta 8003)..."
export OPENCLAW_GATEWAY_TOKEN_FILE=/root/.openclaw/gateway.token
cd backend
nohup ./.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8003 > /tmp/uvicorn-8003.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

cd ..
echo ""
echo "🚀 Iniciando Frontend (porta 5173)..."
cd frontend
nohup npm run dev -- --host 0.0.0.0 --port 5173 > /tmp/vite-5173.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"

cd ..
sleep 3

echo ""
echo "✅ Servidores iniciados!"
echo ""
netstat -tlnp 2>/dev/null | grep -E ":8003|:5173"

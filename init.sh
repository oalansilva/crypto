#!/bin/bash
# init.sh — Verifica se o sistema está pronto para trabalho
# Uso: ./init.sh

echo "=== Crypto System Health Check ==="
echo ""

# Backend
echo "[1/3] Verificando backend (porta 8003)..."
BACKEND_OK=false
if curl -sf http://127.0.0.1:8003/api/health > /dev/null 2>&1; then
    echo "  ✅ Backend OK"
    BACKEND_OK=true
else
    echo "  ❌ Backend OFFLINE — iniciando..."
    cd /root/.openclaw/workspace/crypto
    ./start.sh > /dev/null 2>&1 &
    sleep 5
    if curl -sf http://127.0.0.1:8003/api/health > /dev/null 2>&1; then
        echo "  ✅ Backend iniciado"
        BACKEND_OK=true
    else
        echo "  ❌ Backend falhou ao iniciar"
    fi
fi

# Frontend
echo ""
echo "[2/3] Verificando frontend (porta 5173)..."
if curl -sf http://127.0.0.1:5173 > /dev/null 2>&1; then
    echo "  ✅ Frontend OK"
else
    echo "  ⚠️  Frontend não responde (verifique manualmente)"
fi

# OpenSpec - testa listando changes
echo ""
echo "[3/3] Verificando OpenSpec (porta 8003)..."
if curl -sf http://127.0.0.1:8003/api/openspec/specs > /dev/null 2>&1; then
    echo "  ✅ OpenSpec OK"
else
    echo "  ⚠️  OpenSpec API não responde"
fi

echo ""
if [ "$BACKEND_OK" = true ]; then
    echo "=== Pronto para trabalhar ==="
else
    echo "=== Atenção: backend offline ==="
fi

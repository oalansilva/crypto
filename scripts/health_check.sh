#!/bin/bash
# Health check script for backend and frontend services
# Sends Telegram notification to Alan on failure

BACKEND_URL="http://127.0.0.1:8003/api/health"
FRONTEND_URL="http://127.0.0.1:5173"
TIMEOUT=5
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID}"

send_telegram() {
    local message="$1"
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d "chat_id=${TELEGRAM_CHAT_ID}" \
            -d "text=${message}" \
            -d "parse_mode=HTML" > /dev/null 2>&1
    fi
}

check_service() {
    local name="$1"
    local url="$2"
    local response
    local http_code
    
    response=$(curl -s -o /dev/null -w "%{http_code}" --max-time "$TIMEOUT" "$url" 2>/dev/null)
    http_code=$?
    
    if [ $http_code -eq 0 ]; then
        if [ "$response" = "200" ]; then
            echo "✓ $name: OK"
            return 0
        else
            echo "✗ $name: HTTP $response"
            return 1
        fi
    else
        echo "✗ $name: TIMEOUT or CONNECTION ERROR"
        return 1
    fi
}

errors=0

echo "Running health check at $(date)"
echo "---"

# Check backend
if ! check_service "Backend" "$BACKEND_URL"; then
    errors=$((errors + 1))
fi

# Check frontend
if ! check_service "Frontend" "$FRONTEND_URL"; then
    errors=$((errors + 1))
fi

echo "---"

if [ $errors -gt 0 ]; then
    echo "Health check FAILED: $errors service(s) unavailable"
    send_telegram "⚠️ <b>Health Check Failed</b>%0A$errors service(s) unavailable at $(date)"
    exit 1
else
    echo "Health check PASSED: all services OK"
    exit 0
fi

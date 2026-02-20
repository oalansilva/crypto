#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_SERVICE="crypto-backend.service"
FRONTEND_SERVICE="crypto-frontend.service"
BACKEND_LOG="/tmp/uvicorn-8003.log"
FRONTEND_LOG="/tmp/vite-5173.log"
BACKEND_PID_FILE="/tmp/crypto-backend.pid"
FRONTEND_PID_FILE="/tmp/crypto-frontend.pid"
HEALTH_URL="http://127.0.0.1:8003/api/health"
VENV_PYTHON="$BACKEND_DIR/.venv/bin/python"

has_systemd_service() {
  local service_name="$1"
  command -v systemctl >/dev/null 2>&1 || return 1
  systemctl list-unit-files --type=service --no-legend 2>/dev/null | awk '{print $1}' | grep -Fxq "$service_name"
}

start_backend_with_nohup() {
  if pgrep -f "uvicorn app.main:app.*--port 8003" >/dev/null 2>&1; then
    echo "Backend already running on port 8003."
    return
  fi

  (
    cd "$BACKEND_DIR"
    nohup "$VENV_PYTHON" -m uvicorn app.main:app --host 0.0.0.0 --port 8003 >"$BACKEND_LOG" 2>&1 &
    echo "$!" >"$BACKEND_PID_FILE"
  )
  echo "Backend started with nohup (log: $BACKEND_LOG)."
}

start_frontend_with_nohup() {
  if pgrep -f "vite.*--port 5173" >/dev/null 2>&1; then
    echo "Frontend already running on port 5173."
    return
  fi

  (
    cd "$FRONTEND_DIR"
    nohup npm run dev -- --host 0.0.0.0 --port 5173 >"$FRONTEND_LOG" 2>&1 &
    echo "$!" >"$FRONTEND_PID_FILE"
  )
  echo "Frontend started with nohup (log: $FRONTEND_LOG)."
}

echo "Checking backend virtual environment..."
if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Missing virtual environment python: $VENV_PYTHON"
  echo "Create it first, e.g. from repo root:"
  echo "  python3 -m venv backend/.venv"
  exit 1
fi

echo "Running database initialization..."
(
  cd "$BACKEND_DIR"
  "$VENV_PYTHON" init_db.py
)

if has_systemd_service "$BACKEND_SERVICE"; then
  echo "Starting backend via systemd: $BACKEND_SERVICE"
  if ! systemctl start "$BACKEND_SERVICE"; then
    echo "systemd start failed for backend; falling back to nohup."
    start_backend_with_nohup
  fi
else
  start_backend_with_nohup
fi

if has_systemd_service "$FRONTEND_SERVICE"; then
  echo "Starting frontend via systemd: $FRONTEND_SERVICE"
  if ! systemctl start "$FRONTEND_SERVICE"; then
    echo "systemd start failed for frontend; falling back to nohup."
    start_frontend_with_nohup
  fi
else
  start_frontend_with_nohup
fi

if command -v curl >/dev/null 2>&1; then
  echo "Running backend health check: $HEALTH_URL"
  for _ in {1..10}; do
    if curl -fsS --max-time 2 "$HEALTH_URL" >/dev/null; then
      echo "Health check passed."
      echo "Backend:  http://127.0.0.1:8003"
      echo "Frontend: http://127.0.0.1:5173"
      exit 0
    fi
    sleep 1
  done
  echo "Health check failed. Check backend logs at $BACKEND_LOG."
  exit 1
fi

echo "curl not found; skipped health check."

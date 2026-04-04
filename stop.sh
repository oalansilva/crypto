#!/usr/bin/env bash
set -euo pipefail

BACKEND_SERVICE="crypto-backend.service"
FRONTEND_SERVICE="crypto-frontend.service"
BACKEND_PORT="${CRYPTO_BACKEND_PORT:-8003}"
FRONTEND_PORT="${CRYPTO_FRONTEND_PORT:-5173}"
BACKEND_PID_FILE="/tmp/crypto-backend.pid"
FRONTEND_PID_FILE="/tmp/crypto-frontend.pid"

has_systemd_service() {
  local service_name="$1"
  command -v systemctl >/dev/null 2>&1 || return 1
  systemctl list-unit-files --type=service --no-legend 2>/dev/null | awk '{print $1}' | grep -Fxq "$service_name"
}

kill_pid_file() {
  local pid_file="$1"
  if [[ ! -f "$pid_file" ]]; then
    return
  fi

  local pid
  pid="$(cat "$pid_file" 2>/dev/null || true)"
  if [[ -n "$pid" ]] && kill -0 "$pid" 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    sleep 1
    if kill -0 "$pid" 2>/dev/null; then
      kill -9 "$pid" 2>/dev/null || true
    fi
  fi
  rm -f "$pid_file"
}

kill_by_port() {
  local port="$1"
  local pids=""

  if command -v lsof >/dev/null 2>&1; then
    pids="$(lsof -ti "tcp:$port" 2>/dev/null || true)"
  elif command -v fuser >/dev/null 2>&1; then
    pids="$(fuser "${port}/tcp" 2>/dev/null || true)"
  fi

  if [[ -n "$pids" ]]; then
    echo "$pids" | xargs -r kill 2>/dev/null || true
    sleep 1
    echo "$pids" | xargs -r kill -9 2>/dev/null || true
  fi
}

kill_by_pattern() {
  local pattern="$1"
  if pgrep -f "$pattern" >/dev/null 2>&1; then
    pkill -f "$pattern" 2>/dev/null || true
    sleep 1
    pkill -9 -f "$pattern" 2>/dev/null || true
  fi
}

echo "Stopping crypto services..."

if has_systemd_service "$BACKEND_SERVICE"; then
  systemctl stop "$BACKEND_SERVICE" || true
fi
if has_systemd_service "$FRONTEND_SERVICE"; then
  systemctl stop "$FRONTEND_SERVICE" || true
fi

kill_pid_file "$BACKEND_PID_FILE"
kill_pid_file "$FRONTEND_PID_FILE"
kill_by_port "$BACKEND_PORT"
kill_by_port "$FRONTEND_PORT"
kill_by_pattern "uvicorn app.main:app.*--port ${BACKEND_PORT}"
kill_by_pattern "vite.*--port ${FRONTEND_PORT}"

echo "Done."

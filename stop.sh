#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_SERVICE="crypto-backend.service"
FRONTEND_SERVICE="crypto-frontend.service"
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

stop_backend_fallback() {
  echo "Stopping backend via process fallback..."
  kill_pid_file "$BACKEND_PID_FILE"
  kill_by_port 8000
  kill_by_pattern "uvicorn app.main:app.*--port 8000"
}

stop_frontend_fallback() {
  echo "Stopping frontend via process fallback..."
  kill_pid_file "$FRONTEND_PID_FILE"
  kill_by_port 5173
  kill_by_pattern "vite.*--port 5173"
  kill_by_pattern "npm run dev -- --host 127.0.0.1 --port 5173"
}

echo "Stopping services..."

if has_systemd_service "$BACKEND_SERVICE"; then
  echo "Stopping systemd service: $BACKEND_SERVICE"
  if ! systemctl stop "$BACKEND_SERVICE"; then
    echo "systemd stop failed for backend; falling back to process stop."
    stop_backend_fallback
  fi
else
  stop_backend_fallback
fi

if has_systemd_service "$FRONTEND_SERVICE"; then
  echo "Stopping systemd service: $FRONTEND_SERVICE"
  if ! systemctl stop "$FRONTEND_SERVICE"; then
    echo "systemd stop failed for frontend; falling back to process stop."
    stop_frontend_fallback
  fi
else
  stop_frontend_fallback
fi

echo "Done."

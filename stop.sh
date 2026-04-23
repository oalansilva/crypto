#!/usr/bin/env bash
set -euo pipefail

BACKEND_UNIT="crypto-backend"
FRONTEND_UNIT="crypto-frontend"
RUNTIME_WORKER_UNIT="crypto-runtime-worker"
CELERY_WORKER_UNIT="crypto-celery-worker"
BINANCE_WORKER_UNIT="crypto-binance-realtime-worker"
BACKEND_PORT="${CRYPTO_BACKEND_PORT:-8003}"
FRONTEND_PORT="${CRYPTO_FRONTEND_PORT:-5173}"
REDIS_CONTAINER_NAME="crypto-runtime-redis"
BACKEND_PID_FILE="/tmp/crypto-backend.pid"
FRONTEND_PID_FILE="/tmp/crypto-frontend.pid"
RUNTIME_WORKER_PID_FILE="/tmp/crypto-runtime-worker.pid"
CELERY_WORKER_PID_FILE="/tmp/crypto-celery-worker.pid"
BINANCE_WORKER_PID_FILE="/tmp/crypto-binance-realtime-worker.pid"

user_systemd_available() {
  command -v systemctl >/dev/null 2>&1 || return 1
  systemctl --user show-environment >/dev/null 2>&1
}

wait_for_unit_inactive() {
  local unit="$1"
  local attempts="${2:-20}"
  local sleep_s="${3:-1}"
  local state=""
  for _ in $(seq 1 "$attempts"); do
    state="$(systemctl --user show "${unit}.service" -p ActiveState --value 2>/dev/null || true)"
    if [[ -z "$state" || "$state" == "inactive" || "$state" == "failed" ]]; then
      return 0
    fi
    sleep "$sleep_s"
  done
  return 1
}

stop_user_unit() {
  local unit="$1"
  if ! user_systemd_available; then
    return 0
  fi
  systemctl --user stop "${unit}.service" >/dev/null 2>&1 || true
  wait_for_unit_inactive "$unit" 30 1 || true
  systemctl --user reset-failed "${unit}.service" >/dev/null 2>&1 || true
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

stop_user_unit "$BACKEND_UNIT"
stop_user_unit "$FRONTEND_UNIT"
stop_user_unit "$RUNTIME_WORKER_UNIT"
stop_user_unit "$CELERY_WORKER_UNIT"
stop_user_unit "$BINANCE_WORKER_UNIT"

kill_pid_file "$BACKEND_PID_FILE"
kill_pid_file "$FRONTEND_PID_FILE"
kill_pid_file "$RUNTIME_WORKER_PID_FILE"
kill_pid_file "$CELERY_WORKER_PID_FILE"
kill_pid_file "$BINANCE_WORKER_PID_FILE"
kill_by_port "$BACKEND_PORT"
kill_by_port "$FRONTEND_PORT"
kill_by_pattern "uvicorn app.main:app.*--port ${BACKEND_PORT}"
kill_by_pattern "vite.*--port ${FRONTEND_PORT}"
kill_by_pattern "python -m app.workers.runtime_worker"
kill_by_pattern "celery .*app.celery_app:celery_app worker"
kill_by_pattern "python -m app.binance_realtime_worker"

if command -v docker >/dev/null 2>&1 && docker inspect "$REDIS_CONTAINER_NAME" >/dev/null 2>&1; then
  docker rm -f "$REDIS_CONTAINER_NAME" >/dev/null 2>&1 || true
fi

echo "Done."

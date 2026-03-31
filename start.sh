#!/usr/bin/env bash
set -euo pipefail

# Load local environment variables (not committed)
if [ -f ".env" ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi


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
FRONTEND_URL="http://127.0.0.1:5173"
VENV_PYTHON="$BACKEND_DIR/.venv/bin/python"

has_systemd_service() {
  local service_name="$1"
  command -v systemctl >/dev/null 2>&1 || return 1
  systemctl list-unit-files --type=service --no-legend 2>/dev/null | awk '{print $1}' | grep -Fxq "$service_name"
}

pid_file_is_alive() {
  local pid_file="$1"
  if [[ ! -f "$pid_file" ]]; then
    return 1
  fi
  local pid
  pid="$(cat "$pid_file" 2>/dev/null || true)"
  [[ -n "$pid" ]] || return 1
  kill -0 "$pid" 2>/dev/null
}

find_backend_pid() {
  pgrep -fo "uvicorn app.main:app.*--port 8003|$BACKEND_DIR/.venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8003" 2>/dev/null || true
}

find_frontend_pid() {
  pgrep -fo "node .*vite.*--port 5173|vite.*--port 5173|npm run dev -- --host 0.0.0.0 --port 5173" 2>/dev/null || true
}

store_runtime_pid() {
  local pid_file="$1"
  local finder="$2"
  local pid=""
  for _ in $(seq 1 10); do
    pid="$($finder)"
    if [[ -n "$pid" ]]; then
      echo "$pid" >"$pid_file"
      return 0
    fi
    sleep 1
  done
  return 1
}

remove_stale_pid_file() {
  local pid_file="$1"
  if [[ -f "$pid_file" ]] && ! pid_file_is_alive "$pid_file"; then
    rm -f "$pid_file"
  fi
}

wait_for_http_ok() {
  local url="$1"
  local attempts="${2:-20}"
  local sleep_s="${3:-1}"
  for _ in $(seq 1 "$attempts"); do
    if curl -fsS --max-time 2 "$url" >/dev/null 2>&1; then
      return 0
    fi
    sleep "$sleep_s"
  done
  return 1
}

start_backend_with_nohup() {
  remove_stale_pid_file "$BACKEND_PID_FILE"

  if pid_file_is_alive "$BACKEND_PID_FILE" && wait_for_http_ok "$HEALTH_URL" 2 1; then
    echo "Backend already healthy."
    return
  fi

  if pgrep -f "uvicorn app.main:app.*--port 8003" >/dev/null 2>&1 && wait_for_http_ok "$HEALTH_URL" 2 1; then
    echo "Backend already healthy."
    return
  fi

  (
    cd "$BACKEND_DIR"
    if command -v setsid >/dev/null 2>&1; then
      setsid "$VENV_PYTHON" -m uvicorn app.main:app --host 0.0.0.0 --port 8003 >"$BACKEND_LOG" 2>&1 < /dev/null &
    else
      nohup "$VENV_PYTHON" -m uvicorn app.main:app --host 0.0.0.0 --port 8003 >"$BACKEND_LOG" 2>&1 < /dev/null &
    fi
  )
  store_runtime_pid "$BACKEND_PID_FILE" find_backend_pid || true
  echo "Backend started with nohup (log: $BACKEND_LOG)."
}

start_frontend_with_nohup() {
  remove_stale_pid_file "$FRONTEND_PID_FILE"

  if pid_file_is_alive "$FRONTEND_PID_FILE" && wait_for_http_ok "$FRONTEND_URL" 2 1; then
    echo "Frontend already healthy."
    return
  fi

  if pgrep -f "vite.*--port 5173" >/dev/null 2>&1 && wait_for_http_ok "$FRONTEND_URL" 2 1; then
    echo "Frontend already healthy."
    return
  fi

  (
    cd "$FRONTEND_DIR"
    if command -v setsid >/dev/null 2>&1; then
      setsid /bin/bash -lc 'exec npm run dev -- --host 0.0.0.0 --port 5173' >"$FRONTEND_LOG" 2>&1 < /dev/null &
    else
      nohup /bin/bash -lc 'exec npm run dev -- --host 0.0.0.0 --port 5173' >"$FRONTEND_LOG" 2>&1 < /dev/null &
    fi
    echo "$!" >"$FRONTEND_PID_FILE"
  )

  if ! wait_for_http_ok "$FRONTEND_URL" 30 1; then
    echo "Frontend failed to respond on $FRONTEND_URL. Check frontend logs at $FRONTEND_LOG."
    return 1
  fi

  sleep 2
  if ! wait_for_http_ok "$FRONTEND_URL" 3 1; then
    echo "Frontend responded once but did not stay up. Check frontend logs at $FRONTEND_LOG."
    return 1
  fi

  store_runtime_pid "$FRONTEND_PID_FILE" find_frontend_pid || true
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
  if wait_for_http_ok "$HEALTH_URL" 30 1; then
    echo "Backend health check passed."
    echo "Running frontend health check: $FRONTEND_URL"
    if wait_for_http_ok "$FRONTEND_URL" 30 1; then
      echo "Frontend health check passed."
      echo "Backend:  http://127.0.0.1:8003"
      echo "Frontend: http://127.0.0.1:5173"
      exit 0
    fi
    echo "Frontend health check failed. Check frontend logs at $FRONTEND_LOG."
    exit 1
  fi
  if pid_file_is_alive "$BACKEND_PID_FILE" && grep -q "Uvicorn running on http://0.0.0.0:8003" "$BACKEND_LOG" 2>/dev/null; then
    echo "Health check could not be confirmed from this environment, but backend process is alive and uvicorn reported successful startup."
    echo "Backend:  http://127.0.0.1:8003"
    echo "Frontend: http://127.0.0.1:5173"
    exit 0
  fi
  echo "Health check failed. Check backend logs at $BACKEND_LOG."
  exit 1
fi

echo "curl not found; skipped health check."

#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_SERVICE="crypto-backend.service"
FRONTEND_SERVICE="crypto-frontend.service"
BACKEND_PORT="${CRYPTO_BACKEND_PORT:-8003}"
FRONTEND_PORT="${CRYPTO_FRONTEND_PORT:-5173}"
BACKEND_LOG="/tmp/crypto-uvicorn-${BACKEND_PORT}.log"
FRONTEND_LOG="/tmp/crypto-vite-${FRONTEND_PORT}.log"
BACKEND_PID_FILE="/tmp/crypto-backend.pid"
FRONTEND_PID_FILE="/tmp/crypto-frontend.pid"
HEALTH_URL="http://127.0.0.1:${BACKEND_PORT}/api/health"
FRONTEND_URL="http://127.0.0.1:${FRONTEND_PORT}"
VENV_PYTHON="$BACKEND_DIR/.venv/bin/python"

for env_file in "$ROOT_DIR/backend/.env" "$ROOT_DIR/.env"; do
  if [ -f "$env_file" ]; then
    set -a
    # shellcheck disable=SC1090
    source "$env_file"
    set +a
  fi
done

# Accept project-scoped aliases when the generic runtime variables are absent.
export DATABASE_URL="${DATABASE_URL:-${CRYPTO_DATABASE_URL:-}}"
export WORKFLOW_DATABASE_URL="${WORKFLOW_DATABASE_URL:-${CRYPTO_WORKFLOW_DATABASE_URL:-}}"
export CRYPTO_DATABASE_URL="${CRYPTO_DATABASE_URL:-${DATABASE_URL:-}}"
export CRYPTO_WORKFLOW_DATABASE_URL="${CRYPTO_WORKFLOW_DATABASE_URL:-${WORKFLOW_DATABASE_URL:-}}"

require_env_var() {
  local var_name="$1"
  local value="${!var_name:-}"
  if [[ -z "$value" ]]; then
    echo "Missing required environment variable: $var_name"
    exit 1
  fi
}

require_postgres_url() {
  local var_name="$1"
  local value="${!var_name:-}"
  require_env_var "$var_name"
  if [[ "$value" != postgresql://* && "$value" != postgresql+psycopg2://* ]]; then
    echo "Environment variable $var_name must point to PostgreSQL."
    exit 1
  fi
}

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

store_runtime_pid() {
  local pid_file="$1"
  local pattern="$2"
  local pid=""
  for _ in $(seq 1 10); do
    pid="$(pgrep -fo "$pattern" 2>/dev/null || true)"
    if [[ -n "$pid" ]]; then
      echo "$pid" >"$pid_file"
      return 0
    fi
    sleep 1
  done
  return 1
}

echo "Checking crypto backend virtual environment..."
if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Missing virtual environment python: $VENV_PYTHON"
  exit 1
fi

require_postgres_url "DATABASE_URL"
require_postgres_url "WORKFLOW_DATABASE_URL"

echo "Running crypto database initialization..."
(
  cd "$BACKEND_DIR"
  "$VENV_PYTHON" init_db.py
)

remove_stale_pid_file "$BACKEND_PID_FILE"
remove_stale_pid_file "$FRONTEND_PID_FILE"

if has_systemd_service "$BACKEND_SERVICE"; then
  systemctl start "$BACKEND_SERVICE" || true
fi

if ! wait_for_http_ok "$HEALTH_URL" 2 1; then
  (
    cd "$BACKEND_DIR"
    nohup "$VENV_PYTHON" -m uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" >"$BACKEND_LOG" 2>&1 < /dev/null &
  )
  store_runtime_pid "$BACKEND_PID_FILE" "uvicorn app.main:app.*--port ${BACKEND_PORT}" || true
fi

if has_systemd_service "$FRONTEND_SERVICE"; then
  systemctl start "$FRONTEND_SERVICE" || true
fi

if ! wait_for_http_ok "$FRONTEND_URL" 2 1; then
  (
    cd "$FRONTEND_DIR"
    nohup env VITE_API_URL="/api" npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT" >"$FRONTEND_LOG" 2>&1 < /dev/null &
    echo "$!" >"$FRONTEND_PID_FILE"
  )
  store_runtime_pid "$FRONTEND_PID_FILE" "vite.*--port ${FRONTEND_PORT}" || true
fi

echo "Running crypto health checks..."
wait_for_http_ok "$HEALTH_URL" 30 1
wait_for_http_ok "$FRONTEND_URL" 30 1

echo "crypto backend:  ${CRYPTO_BACKEND_URL:-http://127.0.0.1:${BACKEND_PORT}}"
echo "crypto frontend: ${CRYPTO_FRONTEND_URL:-http://127.0.0.1:${FRONTEND_PORT}}"

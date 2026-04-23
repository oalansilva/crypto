#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
BACKEND_UNIT="crypto-backend"
FRONTEND_UNIT="crypto-frontend"
RUNTIME_WORKER_UNIT="crypto-runtime-worker"
CELERY_WORKER_UNIT="crypto-celery-worker"
BINANCE_WORKER_UNIT="crypto-binance-realtime-worker"
BACKEND_PORT="${CRYPTO_BACKEND_PORT:-8003}"
FRONTEND_PORT="${CRYPTO_FRONTEND_PORT:-5173}"
REDIS_HOST="${CRYPTO_REDIS_HOST:-127.0.0.1}"
REDIS_PORT="${CRYPTO_REDIS_PORT:-6379}"
BACKEND_LOG="/tmp/crypto-uvicorn-${BACKEND_PORT}.log"
FRONTEND_LOG="/tmp/crypto-vite-${FRONTEND_PORT}.log"
RUNTIME_WORKER_LOG="/tmp/crypto-runtime-worker.log"
CELERY_WORKER_LOG="/tmp/crypto-celery-worker.log"
BINANCE_WORKER_LOG="/tmp/crypto-binance-realtime-worker.log"
BACKEND_PID_FILE="/tmp/crypto-backend.pid"
FRONTEND_PID_FILE="/tmp/crypto-frontend.pid"
RUNTIME_WORKER_PID_FILE="/tmp/crypto-runtime-worker.pid"
CELERY_WORKER_PID_FILE="/tmp/crypto-celery-worker.pid"
BINANCE_WORKER_PID_FILE="/tmp/crypto-binance-realtime-worker.pid"
HEALTH_URL="http://127.0.0.1:${BACKEND_PORT}/api/health"
FRONTEND_URL="http://127.0.0.1:${FRONTEND_PORT}"
VENV_PYTHON="$BACKEND_DIR/.venv/bin/python"
VENV_ALEMBIC="$BACKEND_DIR/.venv/bin/alembic"
VENV_CELERY="$BACKEND_DIR/.venv/bin/celery"
REDIS_CONTAINER_NAME="crypto-runtime-redis"
REDIS_VOLUME_NAME="crypto-runtime-redis-data"

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
export REDIS_URL="${REDIS_URL:-redis://${REDIS_HOST}:${REDIS_PORT}/0}"
export CELERY_BROKER_URL="${CELERY_BROKER_URL:-redis://${REDIS_HOST}:${REDIS_PORT}/1}"
export CELERY_RESULT_BACKEND="${CELERY_RESULT_BACKEND:-redis://${REDIS_HOST}:${REDIS_PORT}/2}"
export CELERY_WORKER_CONCURRENCY="${CELERY_WORKER_CONCURRENCY:-1}"
export CELERY_WORKER_PREFETCH_MULTIPLIER="${CELERY_WORKER_PREFETCH_MULTIPLIER:-1}"
export CELERY_LOG_LEVEL="${CELERY_LOG_LEVEL:-INFO}"
export BINANCE_REALTIME_WORKER_ENABLED="${BINANCE_REALTIME_WORKER_ENABLED:-1}"

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

user_systemd_available() {
  command -v systemctl >/dev/null 2>&1 || return 1
  systemctl --user show-environment >/dev/null 2>&1
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

wait_for_tcp_open() {
  local host="$1"
  local port="$2"
  local attempts="${3:-20}"
  local sleep_s="${4:-1}"
  for _ in $(seq 1 "$attempts"); do
    if timeout 2 bash -lc ":</dev/tcp/${host}/${port}" >/dev/null 2>&1; then
      return 0
    fi
    sleep "$sleep_s"
  done
  return 1
}

flag_enabled() {
  local raw="${1:-}"
  raw="$(printf '%s' "$raw" | tr '[:upper:]' '[:lower:]')"
  [[ "$raw" != "0" && "$raw" != "false" && "$raw" != "no" && "$raw" != "off" ]]
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

ensure_process_running() {
  local pid_file="$1"
  local pattern="$2"
  local description="$3"
  if pid_file_is_alive "$pid_file"; then
    return 0
  fi
  store_runtime_pid "$pid_file" "$pattern" || true
  if ! pid_file_is_alive "$pid_file"; then
    echo "Failed to start ${description}" >&2
    exit 1
  fi
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

shell_escape() {
  printf '%q' "$1"
}

start_transient_unit() {
  local unit="$1"
  local working_dir="$2"
  local log_file="$3"
  local command="$4"

  stop_user_unit "$unit"
  : >"$log_file"
  systemd-run --user \
    --unit="$unit" \
    --collect \
    --property="WorkingDirectory=$working_dir" \
    --property="StandardOutput=append:$log_file" \
    --property="StandardError=append:$log_file" \
    /bin/bash -lc "$command" >/dev/null
}

run_alembic_migrations() {
  local output=""
  if output="$(
    cd "$BACKEND_DIR" && "$VENV_ALEMBIC" upgrade head 2>&1
  )"; then
    printf '%s\n' "$output"
    return 0
  fi

  printf '%s\n' "$output" >&2
  if grep -Eq 'Running upgrade  -> 20260419_0001' <<<"$output" \
    && grep -Eq 'DuplicateTable|already exists' <<<"$output"; then
    echo "Detected legacy PostgreSQL schema without Alembic stamp; stamping head..." >&2
    (
      cd "$BACKEND_DIR"
      "$VENV_ALEMBIC" stamp head
      "$VENV_ALEMBIC" upgrade head
    )
    return 0
  fi

  return 1
}

start_redis_runtime() {
  if wait_for_tcp_open "$REDIS_HOST" "$REDIS_PORT" 2 1; then
    return 0
  fi

  if command -v docker >/dev/null 2>&1; then
    if docker inspect "$REDIS_CONTAINER_NAME" >/dev/null 2>&1; then
      docker start "$REDIS_CONTAINER_NAME" >/dev/null
    else
      docker run -d \
        --name "$REDIS_CONTAINER_NAME" \
        -p "${REDIS_PORT}:6379" \
        -v "${REDIS_VOLUME_NAME}:/data" \
        redis:7-alpine \
        redis-server --appendonly yes --maxmemory-policy noeviction >/dev/null
    fi
  fi

  if ! wait_for_tcp_open "$REDIS_HOST" "$REDIS_PORT" 30 1; then
    echo "Redis runtime is unavailable on ${REDIS_HOST}:${REDIS_PORT}" >&2
    exit 1
  fi
}

echo "Checking crypto backend virtual environment..."
if [[ ! -x "$VENV_PYTHON" ]]; then
  echo "Missing virtual environment python: $VENV_PYTHON"
  exit 1
fi
if [[ ! -x "$VENV_ALEMBIC" ]]; then
  echo "Missing Alembic executable: $VENV_ALEMBIC"
  exit 1
fi
if [[ ! -x "$VENV_CELERY" ]]; then
  echo "Missing Celery executable: $VENV_CELERY"
  exit 1
fi

require_postgres_url "DATABASE_URL"
require_postgres_url "WORKFLOW_DATABASE_URL"

echo "Starting crypto Redis runtime..."
start_redis_runtime

echo "Running crypto database migrations..."
run_alembic_migrations

remove_stale_pid_file "$BACKEND_PID_FILE"
remove_stale_pid_file "$FRONTEND_PID_FILE"
remove_stale_pid_file "$RUNTIME_WORKER_PID_FILE"
remove_stale_pid_file "$CELERY_WORKER_PID_FILE"
remove_stale_pid_file "$BINANCE_WORKER_PID_FILE"

if ! wait_for_http_ok "$HEALTH_URL" 2 1; then
  if user_systemd_available; then
    start_transient_unit \
      "$BACKEND_UNIT" \
      "$BACKEND_DIR" \
      "$BACKEND_LOG" \
      "for env_file in $(shell_escape "$ROOT_DIR/backend/.env") $(shell_escape "$ROOT_DIR/.env"); do [ -f \"\$env_file\" ] && source \"\$env_file\"; done; export BINANCE_REALTIME_ENABLED=0; exec $(shell_escape "$VENV_PYTHON") -m uvicorn app.main:app --host 0.0.0.0 --port $(shell_escape "$BACKEND_PORT")"
  else
    (
      cd "$BACKEND_DIR"
      nohup env \
        BINANCE_REALTIME_ENABLED=0 \
        "$VENV_PYTHON" -m uvicorn app.main:app --host 0.0.0.0 --port "$BACKEND_PORT" >"$BACKEND_LOG" 2>&1 < /dev/null &
    )
  fi
  store_runtime_pid "$BACKEND_PID_FILE" "uvicorn app.main:app.*--port ${BACKEND_PORT}" || true
fi

if ! pgrep -f "python -m app.workers.runtime_worker" >/dev/null 2>&1; then
  if user_systemd_available; then
    start_transient_unit \
      "$RUNTIME_WORKER_UNIT" \
      "$BACKEND_DIR" \
      "$RUNTIME_WORKER_LOG" \
      "for env_file in $(shell_escape "$ROOT_DIR/backend/.env") $(shell_escape "$ROOT_DIR/.env"); do [ -f \"\$env_file\" ] && source \"\$env_file\"; done; export REDIS_URL=$(shell_escape "$REDIS_URL") CELERY_BROKER_URL=$(shell_escape "$CELERY_BROKER_URL") CELERY_RESULT_BACKEND=$(shell_escape "$CELERY_RESULT_BACKEND"); exec $(shell_escape "$VENV_PYTHON") -m app.workers.runtime_worker"
  else
    (
      cd "$BACKEND_DIR"
      nohup env \
        REDIS_URL="$REDIS_URL" \
        CELERY_BROKER_URL="$CELERY_BROKER_URL" \
        CELERY_RESULT_BACKEND="$CELERY_RESULT_BACKEND" \
        "$VENV_PYTHON" -m app.workers.runtime_worker >"$RUNTIME_WORKER_LOG" 2>&1 < /dev/null &
      echo "$!" >"$RUNTIME_WORKER_PID_FILE"
    )
  fi
fi
ensure_process_running \
  "$RUNTIME_WORKER_PID_FILE" \
  "python -m app.workers.runtime_worker" \
  "crypto runtime worker"

if ! pgrep -f "celery .*app.celery_app:celery_app worker" >/dev/null 2>&1; then
  if user_systemd_available; then
    start_transient_unit \
      "$CELERY_WORKER_UNIT" \
      "$BACKEND_DIR" \
      "$CELERY_WORKER_LOG" \
      "for env_file in $(shell_escape "$ROOT_DIR/backend/.env") $(shell_escape "$ROOT_DIR/.env"); do [ -f \"\$env_file\" ] && source \"\$env_file\"; done; export REDIS_URL=$(shell_escape "$REDIS_URL") CELERY_BROKER_URL=$(shell_escape "$CELERY_BROKER_URL") CELERY_RESULT_BACKEND=$(shell_escape "$CELERY_RESULT_BACKEND"); exec $(shell_escape "$VENV_CELERY") -A app.celery_app:celery_app worker --loglevel=$(shell_escape "$CELERY_LOG_LEVEL") --concurrency=$(shell_escape "$CELERY_WORKER_CONCURRENCY") --prefetch-multiplier=$(shell_escape "$CELERY_WORKER_PREFETCH_MULTIPLIER") -Q batch_backtest"
  else
    (
      cd "$BACKEND_DIR"
      nohup env \
        REDIS_URL="$REDIS_URL" \
        CELERY_BROKER_URL="$CELERY_BROKER_URL" \
        CELERY_RESULT_BACKEND="$CELERY_RESULT_BACKEND" \
        "$VENV_CELERY" -A app.celery_app:celery_app worker \
          --loglevel="$CELERY_LOG_LEVEL" \
          --concurrency="${CELERY_WORKER_CONCURRENCY}" \
          --prefetch-multiplier="${CELERY_WORKER_PREFETCH_MULTIPLIER}" \
          -Q batch_backtest >"$CELERY_WORKER_LOG" 2>&1 < /dev/null &
      echo "$!" >"$CELERY_WORKER_PID_FILE"
    )
  fi
fi
ensure_process_running \
  "$CELERY_WORKER_PID_FILE" \
  "celery .*app.celery_app:celery_app worker" \
  "crypto celery worker"

if flag_enabled "$BINANCE_REALTIME_WORKER_ENABLED"; then
  if ! pgrep -f "python -m app.binance_realtime_worker" >/dev/null 2>&1; then
    if user_systemd_available; then
      start_transient_unit \
        "$BINANCE_WORKER_UNIT" \
        "$BACKEND_DIR" \
        "$BINANCE_WORKER_LOG" \
        "for env_file in $(shell_escape "$ROOT_DIR/backend/.env") $(shell_escape "$ROOT_DIR/.env"); do [ -f \"\$env_file\" ] && source \"\$env_file\"; done; export BINANCE_REALTIME_ENABLED=1; exec $(shell_escape "$VENV_PYTHON") -m app.binance_realtime_worker"
    else
      (
        cd "$BACKEND_DIR"
        nohup env \
          BINANCE_REALTIME_ENABLED=1 \
          "$VENV_PYTHON" -m app.binance_realtime_worker >"$BINANCE_WORKER_LOG" 2>&1 < /dev/null &
        echo "$!" >"$BINANCE_WORKER_PID_FILE"
      )
    fi
  fi
  ensure_process_running \
    "$BINANCE_WORKER_PID_FILE" \
    "python -m app.binance_realtime_worker" \
    "crypto binance realtime worker"
fi

if ! wait_for_http_ok "$FRONTEND_URL" 2 1; then
  if user_systemd_available; then
    start_transient_unit \
      "$FRONTEND_UNIT" \
      "$FRONTEND_DIR" \
      "$FRONTEND_LOG" \
      "export VITE_API_URL=/api; exec npm run dev -- --host 0.0.0.0 --port $(shell_escape "$FRONTEND_PORT")"
  else
    (
      cd "$FRONTEND_DIR"
      nohup env VITE_API_URL="/api" npm run dev -- --host 0.0.0.0 --port "$FRONTEND_PORT" >"$FRONTEND_LOG" 2>&1 < /dev/null &
      echo "$!" >"$FRONTEND_PID_FILE"
    )
  fi
  store_runtime_pid "$FRONTEND_PID_FILE" "vite.*--port ${FRONTEND_PORT}" || true
fi

echo "Running crypto health checks..."
wait_for_http_ok "$HEALTH_URL" 30 1
wait_for_http_ok "$FRONTEND_URL" 30 1
wait_for_tcp_open "$REDIS_HOST" "$REDIS_PORT" 10 1
ensure_process_running \
  "$RUNTIME_WORKER_PID_FILE" \
  "python -m app.workers.runtime_worker" \
  "crypto runtime worker"
ensure_process_running \
  "$CELERY_WORKER_PID_FILE" \
  "celery .*app.celery_app:celery_app worker" \
  "crypto celery worker"
if flag_enabled "$BINANCE_REALTIME_WORKER_ENABLED"; then
  ensure_process_running \
    "$BINANCE_WORKER_PID_FILE" \
    "python -m app.binance_realtime_worker" \
    "crypto binance realtime worker"
fi

echo "crypto backend:  ${CRYPTO_BACKEND_URL:-http://127.0.0.1:${BACKEND_PORT}}"
echo "crypto frontend: ${CRYPTO_FRONTEND_URL:-http://127.0.0.1:${FRONTEND_PORT}}"
echo "crypto redis:    ${REDIS_HOST}:${REDIS_PORT}"

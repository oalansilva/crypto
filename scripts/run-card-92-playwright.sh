#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FRONTEND_DIR="$ROOT_DIR/frontend"
BASE_URL="${PLAYWRIGHT_BASE_URL:-http://127.0.0.1:5173}"
PORT="${PLAYWRIGHT_PORT:-5173}"

echo "[card-92] playwright sensor starting"
echo "[card-92] base url: $BASE_URL"

cleanup() {
  if [[ -n "${VITE_PID:-}" ]]; then
    kill "$VITE_PID" >/dev/null 2>&1 || true
    wait "$VITE_PID" >/dev/null 2>&1 || true
  fi
}

if ! curl -fsS "$BASE_URL" >/dev/null 2>&1; then
  echo "[card-92] starting vite on port $PORT"
  (
    cd "$FRONTEND_DIR"
    npm run dev -- --host 127.0.0.1 --port "$PORT"
  ) >/tmp/card-92-playwright-vite.log 2>&1 &
  VITE_PID=$!
  trap cleanup EXIT

  for _ in $(seq 1 60); do
    if curl -fsS "$BASE_URL" >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done

  if ! curl -fsS "$BASE_URL" >/dev/null 2>&1; then
    echo "Vite did not start for card #92 Playwright sensor" >&2
    exit 1
  fi
  echo "[card-92] vite ready"
else
  echo "[card-92] reusing existing server"
fi

cd "$FRONTEND_DIR"
echo "[card-92] running playwright spec"
PLAYWRIGHT_BASE_URL="$BASE_URL" \
PLAYWRIGHT_SKIP_WEBSERVER=1 \
CI=1 \
npx playwright test tests/e2e/card-92-unified-signal.spec.ts --reporter=list

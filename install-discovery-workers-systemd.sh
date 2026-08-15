#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CANONICAL_ROOT="/srv/apps/dev/criptofarol/source"
UNITS=(
  "criptofarol-dev-runtime-worker.service"
  "criptofarol-dev-discovery-worker.service"
)
BACKEND_DROPIN_DIR="/etc/systemd/system/criptofarol-dev-backend.service.d"
BACKEND_DROPIN_FILE="$BACKEND_DROPIN_DIR/discovery-workers.conf"

if [[ "$ROOT_DIR" != "$CANONICAL_ROOT" ]]; then
  echo "Refusing discovery worker install outside canonical DEV source: $ROOT_DIR" >&2
  exit 2
fi

if [[ "${EUID}" -ne 0 ]]; then
  if sudo -n true >/dev/null 2>&1; then
    exec sudo -n "$0" "$@"
  fi
  echo "Root privileges are required to install DEV discovery workers." >&2
  exit 1
fi

for unit in "${UNITS[@]}"; do
  template="$ROOT_DIR/ops/systemd/$unit"
  target="/etc/systemd/system/$unit"
  if [[ ! -f "$template" ]]; then
    echo "Missing systemd template: $template" >&2
    exit 1
  fi
  sed "s|__ROOT_DIR__|$ROOT_DIR|g" "$template" >"$target"
done

mkdir -p "$BACKEND_DROPIN_DIR"
cat >"$BACKEND_DROPIN_FILE" <<'EOF'
[Service]
Environment=CRYPTO_RUNTIME_WORKER_ENABLED=1
Environment=RUN_DISCOVERY_OUTBOX_DISPATCHER=1
Environment=CRYPTO_DISCOVERY_CELERY_WORKER_ENABLED=1
EOF

systemctl daemon-reload
systemctl enable --now "${UNITS[@]}"
systemctl is-active "${UNITS[@]}"

echo "Installed canonical DEV discovery dispatcher and Celery worker."

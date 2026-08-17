#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_ROOT="/srv/apps/dev/criptofarol/source"
PROD_ROOT="/srv/apps/prod/criptofarol/source"
DRY_RUN=0
ROOT_DIR="$SCRIPT_DIR"

usage() {
  echo "Usage: $0 [--dry-run] [--root $DEV_ROOT|$PROD_ROOT]" >&2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --root)
      ROOT_DIR="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

ROOT_DIR="$(cd "$ROOT_DIR" && pwd)"

case "$ROOT_DIR" in
  "$DEV_ROOT") TARGET="dev" ;;
  "$PROD_ROOT") TARGET="prod" ;;
  *)
    echo "Refusing discovery worker install outside canonical DEV or PROD source: $ROOT_DIR" >&2
    exit 2
    ;;
esac

if [[ "$TARGET" == "dev" ]]; then
  UNITS=(
    "criptofarol-dev-runtime-worker.service"
    "criptofarol-dev-discovery-worker.service"
  )
  BACKEND_DROPIN_DIR="/etc/systemd/system/criptofarol-dev-backend.service.d"
  BACKEND_DROPIN_FILE="$BACKEND_DROPIN_DIR/discovery-workers.conf"
else
  UNITS=(
    "criptofarol-prod-runtime-worker.service"
    "criptofarol-prod-discovery-worker.service"
  )
  BACKEND_DROPIN_DIR=""
  BACKEND_DROPIN_FILE=""
fi

template_dir="$SCRIPT_DIR/ops/systemd"

validate_templates() {
  for unit in "${UNITS[@]}"; do
    template="$template_dir/$unit"
    if [[ ! -f "$template" ]]; then
      echo "Missing systemd template: $template" >&2
      exit 1
    fi
    if [[ "$unit" == *runtime-worker.service ]] && ! grep -q 'RUN_DISCOVERY_OUTBOX_DISPATCHER=1' "$template"; then
      echo "Runtime worker template missing RUN_DISCOVERY_OUTBOX_DISPATCHER=1: $template" >&2
      exit 1
    fi
    if [[ "$TARGET" == "prod" && "$unit" == *runtime-worker.service ]]; then
      if ! grep -q 'RUN_FAVORITE_BACKTEST_REFRESH=1' "$template"; then
        echo "PROD runtime worker template would drop favorite refresh: $template" >&2
        exit 1
      fi
    fi
  done
}

validate_templates

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "target=$TARGET"
  echo "root=$ROOT_DIR"
  echo "templates=$template_dir"
  printf 'units=%s\n' "${UNITS[*]}"
  if [[ -n "$BACKEND_DROPIN_FILE" ]]; then
    echo "backend_dropin=$BACKEND_DROPIN_FILE"
  else
    echo "backend_dropin=none"
  fi
  echo "dry-run ok"
  exit 0
fi

if [[ "${EUID}" -ne 0 ]]; then
  if sudo -n true >/dev/null 2>&1; then
    extra=()
    if [[ "$ROOT_DIR" != "$SCRIPT_DIR" ]]; then
      extra=(--root "$ROOT_DIR")
    fi
    exec sudo -n "$0" "${extra[@]}"
  fi
  echo "Root privileges are required to install $TARGET discovery workers." >&2
  exit 1
fi

for unit in "${UNITS[@]}"; do
  template="$template_dir/$unit"
  target="/etc/systemd/system/$unit"
  sed "s|__ROOT_DIR__|$ROOT_DIR|g" "$template" >"$target"
done

if [[ -n "$BACKEND_DROPIN_DIR" ]]; then
  mkdir -p "$BACKEND_DROPIN_DIR"
  cat >"$BACKEND_DROPIN_FILE" <<'EOF'
[Service]
Environment=CRYPTO_RUNTIME_WORKER_ENABLED=1
Environment=RUN_DISCOVERY_OUTBOX_DISPATCHER=1
Environment=CRYPTO_DISCOVERY_CELERY_WORKER_ENABLED=1
EOF
fi

systemctl daemon-reload
systemctl enable --now "${UNITS[@]}"
systemctl is-active "${UNITS[@]}"

echo "Installed canonical $TARGET discovery dispatcher and Celery worker."

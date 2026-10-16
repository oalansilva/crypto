#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_ROOT="/srv/apps/dev/criptofarol/source"
PROD_ROOT="/srv/apps/prod/criptofarol/source"
DRY_RUN=0
DISCOVERY_ONLY=0
ROOT_DIR="$SCRIPT_DIR"

usage() {
  echo "Usage: $0 [--dry-run] [--discovery-only] [--root $DEV_ROOT|$PROD_ROOT]" >&2
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --discovery-only)
      DISCOVERY_ONLY=1
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

if [[ "$DISCOVERY_ONLY" -eq 1 ]]; then
  [[ "$TARGET" == "dev" ]] || { echo 'Discovery-only cutover is DEV-only.' >&2; exit 2; }
  UNITS=("criptofarol-dev-discovery-worker.service")
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
    if [[ "$DISCOVERY_ONLY" -eq 1 ]]; then extra+=(--discovery-only); fi
    exec sudo -n "$0" "${extra[@]}"
  fi
  echo "Root privileges are required to install $TARGET discovery workers." >&2
  exit 1
fi

# Applying a lower envelope to a running legacy tree may cause immediate OOM.
# The caller (./restart, or the operator during the manual cutover) stops
# Discovery first; this guard fails closed if it is still active or if any old
# descendant remains. It never kills anything.
if [[ "$TARGET" == "dev" ]]; then
  discovery_unit="criptofarol-dev-discovery-worker.service"
  if systemctl is-active --quiet "$discovery_unit"; then
    echo "DEV Discovery ($discovery_unit) is still active: memory limits were NOT applied (limites não aplicados). Stop/drain DEV Discovery and verify an empty cgroup before installing limits." >&2
    exit 1
  fi
  group="$(systemctl show "$discovery_unit" -p ControlGroup --value)"
  procs="/sys/fs/cgroup$group/cgroup.procs"
  if [[ -n "$group" && -r "$procs" ]] && [[ -s "$procs" ]]; then
    echo "Legacy Discovery descendants remain in cgroup $group: memory limits were NOT applied (limites não aplicados); refusing coexistence. Nothing was killed. Remaining processes:" >&2
    while IFS= read -r pid; do
      [[ -n "$pid" ]] || continue
      cmd="$(tr '\0' ' ' <"/proc/$pid/cmdline" 2>/dev/null | cut -c1-200 || true)"
      [[ -n "${cmd// /}" ]] || cmd="$(cat "/proc/$pid/comm" 2>/dev/null || true)"
      echo "  PID $pid: ${cmd:-?}" >&2
    done <"$procs"
    echo "Stop or drain these processes (see docs/discovery-memory-operations.md), then run again." >&2
    exit 1
  fi
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
if ! systemctl enable --now "${UNITS[@]}"; then
  echo "Failed to enable/start ${UNITS[*]}. The unit files were installed with the new limits, but the start was refused." >&2
  echo "If this is the 4th start within 15 minutes, systemd's start limit (StartLimitBurst=3/900s, #1093) refused it: wait and repeat. No automatic reset-failed is done." >&2
  exit 1
fi
if ! systemctl is-active "${UNITS[@]}"; then
  echo "Not every unit became active after enable --now: ${UNITS[*]}." >&2
  if [[ "$TARGET" == "dev" ]]; then
    for unit in "${UNITS[@]}"; do
      for hold in "/run/systemd/system/$unit.d/card-1093-hold.conf" "/etc/systemd/system/$unit.d/card-1093-hold.conf"; do
        if [[ -e "$hold" ]]; then
          echo "The #1093 containment drop-in is still present and prevents the start: $hold" >&2
        fi
      done
    done
  fi
  exit 1
fi

echo "Installed canonical $TARGET discovery dispatcher and Celery worker."

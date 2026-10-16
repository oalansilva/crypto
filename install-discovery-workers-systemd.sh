#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEV_ROOT="/srv/apps/dev/criptofarol/source"
PROD_ROOT="/srv/apps/prod/criptofarol/source"
DRY_RUN=0
DISCOVERY_ONLY=0
ROOT_DIR="$SCRIPT_DIR"
# PROD Discovery ceiling (#1110): wait for an idle ledger before touching the unit.
WAIT_IDLE_MIN=30
WAIT_INTERVAL="${DISCOVERY_WAIT_INTERVAL:-60}"

usage() {
  echo "Usage: $0 [--dry-run] [--discovery-only] [--wait-idle <minutes>] [--root $DEV_ROOT|$PROD_ROOT]" >&2
  echo "  --wait-idle <minutes>  PROD --discovery-only: how long to wait for no active search (default 30; 0 = do not wait)." >&2
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
    --wait-idle)
      WAIT_IDLE_MIN="${2:-}"
      if ! [[ "$WAIT_IDLE_MIN" =~ ^[0-9]+$ ]]; then
        echo "--wait-idle needs a whole number of minutes." >&2
        exit 2
      fi
      shift 2
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

DISCOVERY_UNIT="criptofarol-$TARGET-discovery-worker.service"
if [[ "$DISCOVERY_ONLY" -eq 1 ]]; then
  UNITS=("$DISCOVERY_UNIT")
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
    if [[ "$unit" == *discovery-worker.service ]] && ! grep -qx "Environment=DISCOVERY_RESOURCE_PROFILE=$TARGET" "$template"; then
      echo "Discovery template missing DISCOVERY_RESOURCE_PROFILE=$TARGET: $template" >&2
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
    if [[ "$DISCOVERY_ONLY" -eq 1 ]]; then extra+=(--discovery-only --wait-idle "$WAIT_IDLE_MIN"); fi
    exec sudo -n "$0" "${extra[@]}"
  fi
  echo "Root privileges are required to install $TARGET discovery workers." >&2
  exit 1
fi

# Applying a lower envelope to a running legacy tree may cause immediate OOM.
# DEV: the caller (./restart, or the operator during the manual cutover) stops
# Discovery first; this guard fails closed if it is still active or if any old
# descendant remains. It never kills anything.
# PROD (--discovery-only, #1110): this script waits for an idle ledger, stops
# only the Discovery unit and then runs the same guard.
guard_discovery_stopped() {
  local discovery_unit="$1" label="$2" group procs pid cmd
  if systemctl is-active --quiet "$discovery_unit"; then
    echo "$label Discovery ($discovery_unit) is still active: memory limits were NOT applied (limites não aplicados). Stop/drain $label Discovery and verify an empty cgroup before installing limits." >&2
    exit 1
  fi
  group="$(systemctl show "$discovery_unit" -p ControlGroup --value)"
  procs="/sys/fs/cgroup$group/cgroup.procs"
  # cgroup v2 (kernfs) reports size 0 even with PIDs listed: test the content, not -s.
  if [[ -n "$group" && -r "$procs" ]] && grep -q . "$procs"; then
    echo "Legacy Discovery descendants remain in cgroup $group: memory limits were NOT applied (limites não aplicados); refusing coexistence. Nothing was killed. Remaining processes:" >&2
    while IFS= read -r pid; do
      [[ -n "$pid" ]] || continue
      cmd="$({ tr '\0' ' ' <"/proc/$pid/cmdline" | cut -c1-200; } 2>/dev/null || true)"
      [[ -n "${cmd// /}" ]] || cmd="$(cat "/proc/$pid/comm" 2>/dev/null || true)"
      echo "  PID $pid: ${cmd:-?}" >&2
    done <"$procs"
    echo "Stop or drain these processes (see docs/discovery-memory-operations.md), then run again." >&2
    exit 1
  fi
}

# Read-only ledger probe (active_search_probe.py). Exit 0 = idle; anything else,
# including a failure to run it, counts as an active search (fail closed).
# DISCOVERY_ACTIVE_PROBE_CMD replaces the command (test seam).
PROBE_OUT=""
run_probe() {
  local rc=0
  if [[ -n "${DISCOVERY_ACTIVE_PROBE_CMD:-}" ]]; then
    PROBE_OUT="$(bash -c "$DISCOVERY_ACTIVE_PROBE_CMD" 2>&1)" || rc=$?
  else
    # errexit is ignored inside `|| rc=$?`, so the steps are chained with &&.
    PROBE_OUT="$(
      set -a
      source "$ROOT_DIR/backend/.env" &&
        set +a &&
        cd "$ROOT_DIR/backend" &&
        PYTHONPATH="$ROOT_DIR:$ROOT_DIR/backend" "$ROOT_DIR/backend/.venv/bin/python" scripts/discovery/active_search_probe.py 2>&1
    )" || rc=$?
  fi
  return "$rc"
}

if [[ "$TARGET" == "prod" && "$DISCOVERY_ONLY" -eq 1 ]]; then
  max_checks=$(( WAIT_IDLE_MIN * 60 / WAIT_INTERVAL + 1 ))
  check=0
  while true; do
    check=$((check + 1))
    probe_rc=0
    run_probe || probe_rc=$?
    [[ "$probe_rc" -ne 0 ]] || break
    if [[ "$check" -ge "$max_checks" ]]; then
      echo "adiado: busca ativa em PROD. O teto da Descoberta NÃO foi aplicado; nada foi parado, gravado nem reiniciado (a Descoberta PROD segue com a unit anterior). Repita depois." >&2
      echo "Sweeps encontrados (JSON da sonda): $PROBE_OUT" >&2
      exit 75
    fi
    echo "Busca ativa em PROD (consulta $check/$max_checks); nova consulta em ${WAIT_INTERVAL}s: $PROBE_OUT"
    sleep "$WAIT_INTERVAL"
  done
  echo "Sem busca ativa em PROD: $PROBE_OUT"
  echo "Stopping PROD Discovery only ($DISCOVERY_UNIT)..."
  if ! systemctl stop "$DISCOVERY_UNIT"; then
    echo "PROD Discovery did not stop ($DISCOVERY_UNIT): memory limits were NOT applied (limites não aplicados); nothing was installed." >&2
    exit 1
  fi
  guard_discovery_stopped "$DISCOVERY_UNIT" "PROD"
  probe_rc=0
  run_probe || probe_rc=$?
  if [[ "$probe_rc" -ne 0 ]]; then
    echo "aviso: a sonda voltou a indicar atividade entre a primeira consulta e a parada (a combinação retoma pela recuperação do #1093): $PROBE_OUT" >&2
  fi
elif [[ "$TARGET" == "dev" ]]; then
  guard_discovery_stopped "$DISCOVERY_UNIT" "DEV"
elif systemctl is-active --quiet "$DISCOVERY_UNIT"; then
  echo "PROD Discovery ($DISCOVERY_UNIT) is active: a full PROD install would rewrite its unit under a running tree. Use --discovery-only (waits for an idle ledger and stops only Discovery). Nothing was installed." >&2
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
if ! systemctl enable --now "${UNITS[@]}"; then
  if [[ "$TARGET" == "dev" || "$DISCOVERY_ONLY" -eq 1 ]]; then
    echo "Failed to enable/start ${UNITS[*]}. The unit files were installed with the new limits, but the start was refused." >&2
    echo "If this is the 4th start within 15 minutes, systemd's start limit (StartLimitBurst=3/900s, #1093) refused it: wait and repeat. No automatic reset-failed is done." >&2
  else
    echo "Failed to enable/start ${UNITS[*]}." >&2
  fi
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
if [[ "$TARGET" == "prod" && "$DISCOVERY_ONLY" -eq 1 ]]; then
  echo "Verificação ($DISCOVERY_UNIT):"
  systemctl show "$DISCOVERY_UNIT" -p MemoryHigh -p MemoryMax -p MemorySwapMax -p OOMPolicy -p KillMode -p Restart -p RestartUSec -p StartLimitBurst -p StartLimitIntervalUSec -p TimeoutStopUSec -p ActiveState -p NRestarts
fi

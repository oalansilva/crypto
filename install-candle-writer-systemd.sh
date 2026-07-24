#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_NAME=""
FORCE=0

usage() {
  cat >&2 <<'EOF'
Usage: ./install-candle-writer-systemd.sh --env <dev|prod> [--force]

Installs exactly one system candle-writer timer for the selected environment.
Does not enable candle writing inside the API process.
Also aligns backend runtime-status lock/state paths via a systemd drop-in.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --env)
      ENV_NAME="${2:-}"
      shift 2
      ;;
    --force)
      FORCE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$ENV_NAME" ]]; then
  case "$ROOT_DIR" in
    /srv/apps/dev/criptofarol/source) ENV_NAME="dev" ;;
    /srv/apps/prod/criptofarol/source) ENV_NAME="prod" ;;
    *)
      echo "Missing --env <dev|prod> (could not infer from $ROOT_DIR)." >&2
      usage
      exit 1
      ;;
  esac
fi

case "$ENV_NAME" in
  dev|prod) ;;
  *)
    echo "Invalid --env value: $ENV_NAME (expected dev|prod)." >&2
    exit 1
    ;;
esac

CANONICAL_ROOT=""
BACKEND_UNIT=""
LOCK_FILE=""
STATE_FILE=""
LOG_FILE=""
case "$ENV_NAME" in
  dev)
    CANONICAL_ROOT="/srv/apps/dev/criptofarol/source"
    BACKEND_UNIT="criptofarol-dev-backend.service"
    LOCK_FILE="/tmp/crypto-candle-writer-dev.lock"
    STATE_FILE="/tmp/crypto-candle-writer-dev-state.json"
    LOG_FILE="/tmp/crypto-candle-writer-dev.log"
    ;;
  prod)
    CANONICAL_ROOT="/srv/apps/prod/criptofarol/source"
    BACKEND_UNIT="criptofarol-prod-backend.service"
    LOCK_FILE="/tmp/crypto-candle-writer-prod.lock"
    STATE_FILE="/tmp/crypto-candle-writer-prod-state.json"
    LOG_FILE="/tmp/crypto-candle-writer-prod.log"
    ;;
esac

if [[ "$ROOT_DIR" != "$CANONICAL_ROOT" && "$FORCE" -ne 1 ]]; then
  echo "Refusing install from non-canonical root: $ROOT_DIR" >&2
  echo "Expected: $CANONICAL_ROOT (pass --force to override)." >&2
  exit 2
fi

UNIT_PREFIX="criptofarol-${ENV_NAME}-candle-writer"
SERVICE_TEMPLATE="$ROOT_DIR/ops/systemd/${UNIT_PREFIX}.service"
TIMER_TEMPLATE="$ROOT_DIR/ops/systemd/${UNIT_PREFIX}.timer"
SERVICE_TARGET="/etc/systemd/system/${UNIT_PREFIX}.service"
TIMER_TARGET="/etc/systemd/system/${UNIT_PREFIX}.timer"
BACKEND_DROPIN_DIR="/etc/systemd/system/${BACKEND_UNIT}.d"
BACKEND_DROPIN_FILE="${BACKEND_DROPIN_DIR}/candle-writer-paths.conf"

for template in "$SERVICE_TEMPLATE" "$TIMER_TEMPLATE"; do
  if [[ ! -f "$template" ]]; then
    echo "Missing systemd template: $template" >&2
    exit 1
  fi
done

if ! command -v systemctl >/dev/null 2>&1; then
  echo "systemctl is not available on this host." >&2
  exit 1
fi

if [[ "${EUID}" -ne 0 ]]; then
  if command -v sudo >/dev/null 2>&1 && sudo -n true >/dev/null 2>&1; then
    if [[ "$FORCE" -eq 1 ]]; then
      exec sudo -n "$0" --env "$ENV_NAME" --force
    fi
    exec sudo -n "$0" --env "$ENV_NAME"
  fi
  echo "Root privileges are required to install ${UNIT_PREFIX}." >&2
  exit 1
fi

sed "s|__ROOT_DIR__|$ROOT_DIR|g" "$SERVICE_TEMPLATE" >"$SERVICE_TARGET"
cp "$TIMER_TEMPLATE" "$TIMER_TARGET"

mkdir -p "$BACKEND_DROPIN_DIR"
cat >"$BACKEND_DROPIN_FILE" <<EOF
[Service]
Environment=CRYPTO_CANDLES_WRITER_LOCK_FILE=${LOCK_FILE}
Environment=CRYPTO_CANDLES_WRITER_STATE_FILE=${STATE_FILE}
EOF

systemctl daemon-reload
systemctl enable --now "${UNIT_PREFIX}.timer"
systemctl status "${UNIT_PREFIX}.timer" --no-pager

echo "Installed ${UNIT_PREFIX}.timer for env=${ENV_NAME} root=${ROOT_DIR}"
echo "Aligned ${BACKEND_UNIT} observability paths:"
echo "  lock=${LOCK_FILE}"
echo "  state=${STATE_FILE}"
echo "  log=${LOG_FILE}"
echo "Restart ${BACKEND_UNIT} to load the drop-in if it is already running."

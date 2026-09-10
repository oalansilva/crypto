#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_NAME=""
FORCE=0
DRY_RUN=0

usage() {
  cat >&2 <<'EOF'
Usage: ./install-telegram-alert-scan-systemd.sh --env <dev|prod> [--force] [--dry-run]

Installs exactly one system telegram-alert-scan timer for the selected environment.
Sources that environment's canonical backend/.env (DEV never uses the PROD bot).
After enable --now of the timer, starts the oneshot immediately.
Also writes a systemd drop-in for the per-environment flock lock path.
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
    --dry-run)
      DRY_RUN=1
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

# Exit 0 when DEV leftover tokens overlap PROD (dotenv + secrets JSON). Never prints values.
dev_prod_telegram_tokens_overlap() {
  python3 - "$1" "$2" "$3" "$4" <<'PY'
from pathlib import Path
import json
import sys

TOKEN_KEYS = ("MONITOR_TELEGRAM_BOT_TOKEN", "TELEGRAM_BOT_TOKEN")

def dotenv_tokens(path: Path) -> set[str]:
    found: set[str] = set()
    if not path.is_file():
        return found
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return found
    secrets_file = ""
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        value = value.strip().strip('"').strip("'")
        if name in TOKEN_KEYS and value:
            found.add(value)
        if name == "MONITOR_TELEGRAM_SECRETS_FILE":
            secrets_file = value
    if secrets_file:
        found.update(json_tokens(Path(secrets_file)))
    return found

def json_tokens(path: Path) -> set[str]:
    found: set[str] = set()
    if not path.is_file():
        return found
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return found
    env_payload = payload.get("env", payload)
    if not isinstance(env_payload, dict):
        return found
    for key in TOKEN_KEYS:
        value = str(env_payload.get(key) or "").strip()
        if value:
            found.add(value)
    return found

dev_dotenv = Path(sys.argv[1])
dev_json = Path(sys.argv[2])
prod_dotenv = Path(sys.argv[3])
prod_json = Path(sys.argv[4])
dev = dotenv_tokens(dev_dotenv) | json_tokens(dev_json)
prod = dotenv_tokens(prod_dotenv) | json_tokens(prod_json)
sys.exit(0 if (dev and prod and dev & prod) else 1)
PY
}

CANONICAL_ROOT=""
LOCK_FILE=""
BLOCK_PROD_BOT=0
case "$ENV_NAME" in
  dev)
    CANONICAL_ROOT="/srv/apps/dev/criptofarol/source"
    LOCK_FILE="/tmp/crypto-telegram-alert-scan-dev.lock"
    ;;
  prod)
    CANONICAL_ROOT="/srv/apps/prod/criptofarol/source"
    LOCK_FILE="/tmp/crypto-telegram-alert-scan-prod.lock"
    ;;
esac

if [[ "$ROOT_DIR" != "$CANONICAL_ROOT" && "$FORCE" -ne 1 ]]; then
  echo "Refusing install from non-canonical root: $ROOT_DIR" >&2
  echo "Expected: $CANONICAL_ROOT (pass --force to override)." >&2
  exit 2
fi

UNIT_PREFIX="criptofarol-${ENV_NAME}-telegram-alert-scan"
SERVICE_TEMPLATE="$ROOT_DIR/ops/systemd/${UNIT_PREFIX}.service"
TIMER_TEMPLATE="$ROOT_DIR/ops/systemd/${UNIT_PREFIX}.timer"
SERVICE_TARGET="/etc/systemd/system/${UNIT_PREFIX}.service"
TIMER_TARGET="/etc/systemd/system/${UNIT_PREFIX}.timer"
DROPIN_DIR="/etc/systemd/system/${UNIT_PREFIX}.service.d"
DROPIN_FILE="${DROPIN_DIR}/lock-path.conf"

for template in "$SERVICE_TEMPLATE" "$TIMER_TEMPLATE"; do
  if [[ ! -f "$template" ]]; then
    echo "Missing systemd template: $template" >&2
    exit 1
  fi
done

if ! grep -q '^OnCalendar=\*\-\*\-\* 11:05:00 UTC$' "$TIMER_TEMPLATE"; then
  echo "Timer template missing OnCalendar=*-*-* 11:05:00 UTC: $TIMER_TEMPLATE" >&2
  exit 1
fi
if grep -qE '^(OnBootSec|OnUnitInactiveSec)=' "$TIMER_TEMPLATE"; then
  echo "Timer template must not inherit candle-writer OnBootSec/OnUnitInactiveSec: $TIMER_TEMPLATE" >&2
  exit 1
fi

DEV_DOTENV="/srv/apps/dev/criptofarol/source/backend/.env"
PROD_DOTENV="/srv/apps/prod/criptofarol/source/backend/.env"
DEV_SECRETS="/srv/apps/dev/criptofarol/source/backend/.monitor-telegram-secrets.json"
PROD_SECRETS="/srv/apps/prod/criptofarol/source/backend/.monitor-telegram-secrets.json"
if [[ "$ENV_NAME" == "dev" ]]; then
  if dev_prod_telegram_tokens_overlap "$DEV_DOTENV" "$DEV_SECRETS" "$PROD_DOTENV" "$PROD_SECRETS"; then
    BLOCK_PROD_BOT=1
  fi
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "target=$ENV_NAME"
  echo "installer_root=$ROOT_DIR"
  echo "canonical_root=$CANONICAL_ROOT"
  echo "lock=$LOCK_FILE"
  echo "dropin=$DROPIN_FILE"
  echo "service_target=$SERVICE_TARGET"
  echo "timer_target=$TIMER_TARGET"
  echo "start_oneshot=yes"
  echo "block_prod_bot=$BLOCK_PROD_BOT"
  echo "dry-run ok"
  exit 0
fi

if ! command -v systemctl >/dev/null 2>&1; then
  echo "systemctl is not available on this host." >&2
  exit 1
fi

if [[ "${EUID}" -ne 0 ]]; then
  if command -v sudo >/dev/null 2>&1 && sudo -n true >/dev/null 2>&1; then
    extra=(--env "$ENV_NAME")
    if [[ "$FORCE" -eq 1 ]]; then
      extra+=(--force)
    fi
    exec sudo -n "$0" "${extra[@]}"
  fi
  echo "Root privileges are required to install ${UNIT_PREFIX}." >&2
  exit 1
fi

# Units always bind ExecStart to the canonical env root, even when --force
# installs templates from a card worktree.
sed "s|__ROOT_DIR__|$CANONICAL_ROOT|g" "$SERVICE_TEMPLATE" >"$SERVICE_TARGET"
cp "$TIMER_TEMPLATE" "$TIMER_TARGET"

mkdir -p "$DROPIN_DIR"
{
  echo "[Service]"
  echo "Environment=CRYPTO_TELEGRAM_ALERT_SCAN_LOCK_FILE=${LOCK_FILE}"
  if [[ "$BLOCK_PROD_BOT" -eq 1 ]]; then
    echo "Environment=CRYPTO_TELEGRAM_ALERT_SCAN_BLOCK_PROD_BOT=1"
  fi
} >"$DROPIN_FILE"

systemctl daemon-reload
systemctl enable --now "${UNIT_PREFIX}.timer"
oneshot_rc=0
systemctl start "${UNIT_PREFIX}.service" || oneshot_rc=$?
systemctl status "${UNIT_PREFIX}.timer" --no-pager

echo "Installed ${UNIT_PREFIX}.timer for env=${ENV_NAME} canonical_root=${CANONICAL_ROOT}"
echo "Started ${UNIT_PREFIX}.service immediately oneshot_exit=${oneshot_rc}"
echo "Aligned lock drop-in:"
echo "  lock=${LOCK_FILE}"
if [[ "$BLOCK_PROD_BOT" -eq 1 ]]; then
  echo "  block_prod_bot=1"
fi

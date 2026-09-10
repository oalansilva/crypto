#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALLER="$REPO/install-telegram-alert-scan-systemd.sh"
PASS=0
FAIL=0
OUT=/tmp/telegram-alert-scan-installer-test.out
ERR=/tmp/telegram-alert-scan-installer-test.err

assert_exit() {
  local want="$1"
  local label="$2"
  shift 2
  local rc=0
  "$@" >"$OUT" 2>"$ERR" || rc=$?
  if [[ "$rc" -eq "$want" ]]; then
    echo "PASS $label"
    PASS=$((PASS + 1))
  else
    echo "FAIL $label (exit $rc, expected $want)"
    cat "$ERR"
    cat "$OUT"
    FAIL=$((FAIL + 1))
  fi
}

assert_grep() {
  local file="$1"
  local pattern="$2"
  local label="$3"
  if grep -qE "$pattern" "$file"; then
    echo "PASS $label"
    PASS=$((PASS + 1))
  else
    echo "FAIL $label"
    echo "missing /$pattern/ in $file"
    FAIL=$((FAIL + 1))
  fi
}

assert_not_grep() {
  local file="$1"
  local pattern="$2"
  local label="$3"
  if grep -qE "$pattern" "$file"; then
    echo "FAIL $label"
    echo "unexpected /$pattern/ in $file"
    FAIL=$((FAIL + 1))
  else
    echo "PASS $label"
    PASS=$((PASS + 1))
  fi
}

# These two cases MUST NOT depend on whether $REPO is the canonical DEV checkout.
# Copy only the installer into a throwaway root so inference/canonical checks
# see a non-canonical path even when the suite runs from /srv/apps/dev/criptofarol/source.
ISOLATED_ROOT="$(mktemp -d /tmp/telegram-alert-scan-installer-isolated.XXXXXX)"
trap 'rm -rf "$ISOLATED_ROOT"' EXIT
cp "$INSTALLER" "$ISOLATED_ROOT/install-telegram-alert-scan-systemd.sh"
ISOLATED_INSTALLER="$ISOLATED_ROOT/install-telegram-alert-scan-systemd.sh"

assert_exit 1 "missing env refused" bash "$ISOLATED_INSTALLER" --dry-run
assert_exit 1 "invalid env refused" bash "$INSTALLER" --dry-run --env staging
assert_exit 2 "non-canonical root refused" bash "$ISOLATED_INSTALLER" --dry-run --env dev
assert_exit 0 "DEV dry-run with --force" bash "$INSTALLER" --dry-run --env dev --force
if grep -q 'canonical_root=/srv/apps/dev/criptofarol/source' "$OUT" \
  && grep -q 'lock=/tmp/crypto-telegram-alert-scan-dev.lock' "$OUT" \
  && grep -q 'start_oneshot=yes' "$OUT" \
  && grep -q 'dropin=/etc/systemd/system/criptofarol-dev-telegram-alert-scan.service.d/lock-path.conf' "$OUT"; then
  echo "PASS DEV dry-run binds canonical DEV root + lock drop-in"
  PASS=$((PASS + 1))
else
  echo "FAIL DEV dry-run should bind canonical DEV root and lock drop-in"
  cat "$OUT"
  FAIL=$((FAIL + 1))
fi

assert_exit 0 "PROD dry-run with --force" bash "$INSTALLER" --dry-run --env prod --force
if grep -q 'canonical_root=/srv/apps/prod/criptofarol/source' "$OUT" \
  && grep -q 'lock=/tmp/crypto-telegram-alert-scan-prod.lock' "$OUT"; then
  echo "PASS PROD dry-run binds canonical PROD root"
  PASS=$((PASS + 1))
else
  echo "FAIL PROD dry-run should bind canonical PROD root"
  cat "$OUT"
  FAIL=$((FAIL + 1))
fi

for env_name in dev prod; do
  timer="$REPO/ops/systemd/criptofarol-${env_name}-telegram-alert-scan.timer"
  service="$REPO/ops/systemd/criptofarol-${env_name}-telegram-alert-scan.service"
  assert_grep "$timer" '^OnCalendar=\*\-\*\-\* 11:05:00 UTC$' "$env_name timer OnCalendar 11:05 UTC"
  assert_not_grep "$timer" '^(OnBootSec|OnUnitInactiveSec)=' "$env_name timer has no candle-writer interval"
  assert_grep "$service" '^Type=oneshot$' "$env_name service is oneshot"
  assert_grep "$service" '^TimeoutStartSec=1800$' "$env_name service timeout 1800s"
  assert_grep "$service" 'ops/run_monitor_telegram_alert_scan.py' "$env_name service reuses scan script"
  assert_grep "$service" 'flock -n 9' "$env_name service skip-lock via flock -n"
  assert_grep "$service" '^StandardOutput=journal$' "$env_name service logs to journal"
done
assert_grep "$REPO/ops/systemd/criptofarol-dev-telegram-alert-scan.service" 'CRYPTO_TELEGRAM_ALERT_SCAN_BLOCK_PROD_BOT' "DEV service can isolate PROD bot"
assert_grep "$REPO/ops/systemd/criptofarol-dev-telegram-alert-scan.service" 'MONITOR_TELEGRAM_SECRETS_FILE=' "DEV isolation also clears secrets JSON path"
assert_grep "$REPO/ops/run_monitor_telegram_alert_scan.py" '_block_prod_bot' "scanner honors BLOCK_PROD_BOT before loading leftovers"

echo "installer tests: $PASS passed, $FAIL failed"
test "$FAIL" -eq 0

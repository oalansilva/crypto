#!/usr/bin/env bash
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INSTALLER="$REPO/install-discovery-workers-systemd.sh"
PASS=0
FAIL=0
OUT=/tmp/discovery-installer-test.out
ERR=/tmp/discovery-installer-test.err

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

assert_exit 2 "invalid path refused" bash "$INSTALLER" --dry-run --root /tmp
assert_exit 0 "DEV dry-run" bash "$INSTALLER" --dry-run --root /srv/apps/dev/criptofarol/source
if grep -q 'backend_dropin=/etc/systemd/system/criptofarol-dev-backend.service.d/discovery-workers.conf' "$OUT"; then
  echo "PASS DEV keeps backend drop-in"
  PASS=$((PASS + 1))
else
  echo "FAIL DEV should keep backend drop-in"
  cat "$OUT"
  FAIL=$((FAIL + 1))
fi

assert_exit 0 "PROD dry-run" bash "$INSTALLER" --dry-run --root /srv/apps/prod/criptofarol/source
if grep -q 'backend_dropin=none' "$OUT"; then
  echo "PASS PROD has no backend drop-in"
  PASS=$((PASS + 1))
else
  echo "FAIL PROD should not write backend drop-in"
  cat "$OUT"
  FAIL=$((FAIL + 1))
fi
if grep -q 'RUN_FAVORITE_BACKTEST_REFRESH=1' "$REPO/ops/systemd/criptofarol-prod-runtime-worker.service" \
  && grep -q 'RUN_DISCOVERY_OUTBOX_DISPATCHER=1' "$REPO/ops/systemd/criptofarol-prod-runtime-worker.service"; then
  echo "PASS PROD runtime worker keeps refresh + dispatcher"
  PASS=$((PASS + 1))
else
  echo "FAIL PROD runtime worker flags"
  FAIL=$((FAIL + 1))
fi

echo "installer tests: $PASS passed, $FAIL failed"
test "$FAIL" -eq 0

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

# --- #1106: guard with leftover process, isolated from real systemd -------
# Run a rewritten copy of the installer (root check, canonical root,
# /etc/systemd/system and /sys/fs/cgroup pointing to a temp dir) with a fake
# systemctl. The fake cgroup.procs lists a real `sleep` PID.
TMP="$(mktemp -d)"
SLEEP_PID=""
cleanup() {
  [[ -z "$SLEEP_PID" ]] || kill "$SLEEP_PID" 2>/dev/null || true
  rm -rf "$TMP"
}
trap cleanup EXIT

FAKE_ROOT="$TMP/canonical"
mkdir -p "$FAKE_ROOT/ops" "$TMP/etc" "$TMP/stubs" "$TMP/cgroup/system.slice/criptofarol-dev-discovery-worker.service"
cp -r "$REPO/ops/systemd" "$FAKE_ROOT/ops/systemd"
sed \
  -e "s|/srv/apps/dev/criptofarol/source|$FAKE_ROOT|g" \
  -e 's|\[\[ "${EUID}" -ne 0 \]\]|[[ 0 -ne 0 ]]|' \
  -e "s|/etc/systemd/system|$TMP/etc|g" \
  -e "s|/run/systemd/system|$TMP/run|g" \
  -e "s|/sys/fs/cgroup|$TMP/cgroup|g" \
  "$INSTALLER" >"$FAKE_ROOT/install-discovery-workers-systemd.sh"
chmod +x "$FAKE_ROOT/install-discovery-workers-systemd.sh"
cat >"$TMP/stubs/systemctl" <<'STUB'
#!/usr/bin/env bash
echo "$*" >>"$FAKE_CALLS"
case "$1" in
  is-active) [[ -e "$FAKE_ACTIVE" ]] && exit 0 || exit 3 ;;
  show) echo "/system.slice/criptofarol-dev-discovery-worker.service" ;;
  *) ;;
esac
exit 0
STUB
chmod +x "$TMP/stubs/systemctl"
export FAKE_CALLS="$TMP/calls.log"
export FAKE_ACTIVE="$TMP/active"
UNIT_FILE="$TMP/etc/criptofarol-dev-discovery-worker.service"
printf 'OLD-UNIT-SENTINEL' >"$UNIT_FILE"
: >"$FAKE_CALLS"

sleep 300 &
SLEEP_PID=$!
echo "$SLEEP_PID" >"$TMP/cgroup/system.slice/criptofarol-dev-discovery-worker.service/cgroup.procs"

assert_exit 1 "DEV guard refuses leftover process in cgroup" \
  env PATH="$TMP/stubs:$PATH" bash "$FAKE_ROOT/install-discovery-workers-systemd.sh" --discovery-only
check_err() {
  local label="$1" pattern="$2"
  if grep -q -- "$pattern" "$ERR"; then
    echo "PASS $label"
    PASS=$((PASS + 1))
  else
    echo "FAIL $label (missing: $pattern)"
    cat "$ERR"
    FAIL=$((FAIL + 1))
  fi
}
check_err "guard message names the cgroup" "/system.slice/criptofarol-dev-discovery-worker.service"
check_err "guard message lists PID" "PID $SLEEP_PID"
check_err "guard message lists command" "sleep 300"
check_err "guard message says limits not applied" "não aplicados"
if [[ "$(cat "$UNIT_FILE")" == "OLD-UNIT-SENTINEL" ]] \
  && ! grep -qE '^(daemon-reload|enable)' "$FAKE_CALLS" \
  && kill -0 "$SLEEP_PID" 2>/dev/null; then
  echo "PASS guard leaves unit untouched, no reload/enable, kills nothing"
  PASS=$((PASS + 1))
else
  echo "FAIL guard must not install, reload, enable or kill"
  cat "$FAKE_CALLS"
  FAIL=$((FAIL + 1))
fi

: >"$TMP/cgroup/system.slice/criptofarol-dev-discovery-worker.service/cgroup.procs"
touch "$FAKE_ACTIVE"
assert_exit 1 "DEV guard refuses active Discovery unit" \
  env PATH="$TMP/stubs:$PATH" bash "$FAKE_ROOT/install-discovery-workers-systemd.sh" --discovery-only
check_err "active guard says limits not applied" "não aplicados"
rm -f "$FAKE_ACTIVE"

echo "installer tests: $PASS passed, $FAIL failed"
test "$FAIL" -eq 0

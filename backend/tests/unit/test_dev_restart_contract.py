from pathlib import Path
import os
import subprocess


def test_canonical_dev_restart_is_scoped_away_from_prod_runtime():
    restart_source = (Path(__file__).resolve().parents[3] / "restart").read_text()
    dev_block = restart_source.split("# BEGIN CANONICAL DEV RESTART", 1)[1].split(
        "# END CANONICAL DEV RESTART", 1
    )[0]

    assert "criptofarol-dev-backend.service" in dev_block
    assert "criptofarol-dev-frontend.service" in dev_block
    assert 'DEV_BACKEND_PORT="8004"' in dev_block
    assert 'DEV_FRONTEND_PORT="5175"' in dev_block
    assert "criptofarol-prod" not in dev_block
    assert 'DEV_BACKEND_PORT="8003"' not in dev_block
    assert 'DEV_FRONTEND_PORT="5173"' not in dev_block


def test_discovery_worker_uses_solo_pool_for_nested_optimizer_workers():
    repo_root = Path(__file__).resolve().parents[3]
    unit_source = (repo_root / "ops/systemd/criptofarol-dev-discovery-worker.service").read_text()

    assert "--pool=solo" in unit_source
    assert "-Q discovery" in unit_source


def test_dev_discovery_unit_carries_the_1110_ceiling():
    repo_root = Path(__file__).resolve().parents[3]
    lines = (repo_root / "ops/systemd/criptofarol-dev-discovery-worker.service").read_text().splitlines()

    # #1110: DEV warns at 3 GiB and cuts at 4 GiB (was 5/6 GiB in #1093).
    assert "MemoryHigh=3G" in lines and "MemoryMax=4G" in lines
    assert "MemorySwapMax=512M" in lines
    assert "Environment=DISCOVERY_RESOURCE_PROFILE=dev" in lines
    assert not any(line in ("MemoryHigh=5G", "MemoryMax=6G") for line in lines)


def test_dev_worktree_restart_fails_closed_before_legacy_runtime(tmp_path):
    repo_root = Path(__file__).resolve().parents[3]
    simulated_worktree = repo_root / ".restart-contract-test"
    simulated_worktree.mkdir(exist_ok=True)
    restart_copy = simulated_worktree / "restart"
    try:
        restart_source = (repo_root / "restart").read_text()
        restart_copy.write_text(
            restart_source.replace(
                "/srv/apps/dev/criptofarol/*",
                f"{repo_root}/*",
            )
        )
        restart_copy.chmod(0o755)
        result = subprocess.run(
            [str(restart_copy)],
            cwd=simulated_worktree,
            env={**os.environ, "PATH": os.environ.get("PATH", "")},
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    finally:
        restart_copy.unlink(missing_ok=True)
        simulated_worktree.rmdir()

    assert result.returncode == 2
    assert "Refusing restart outside the canonical DEV source." in result.stderr
    assert "Stopping crypto services" not in result.stdout
    assert "Starting crypto" not in result.stdout


# ---------------------------------------------------------------------------
# #1106: DEV restart stops Discovery before installing the #1093 limits.
#
# The real `restart` and `install-discovery-workers-systemd.sh` are copied to a
# temporary canonical root with the root check, /etc/systemd/system,
# /run/systemd/system and /sys/fs/cgroup rewritten to test paths. systemctl,
# curl, npm, alembic and the candle writer installer are stubs, so no real
# service is ever touched.
# ---------------------------------------------------------------------------

import shutil
import signal

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
DISCOVERY_UNIT = "criptofarol-dev-discovery-worker.service"
RUNTIME_UNIT = "criptofarol-dev-runtime-worker.service"
BACKEND_UNIT = "criptofarol-dev-backend.service"
FRONTEND_UNIT = "criptofarol-dev-frontend.service"
OLD_UNIT_CONTENT = "OLD-UNIT-SENTINEL"

SYSTEMCTL_STUB = r"""#!/usr/bin/env bash
# Fake systemctl. State lives in $FAKE/active/<unit>; every call is appended to
# $FAKE/calls.log. Behaviour switches are plain files under $FAKE.
FAKE="${FAKE_SYSTEMD}"
ETC="${FAKE_ETC}"
mkdir -p "$FAKE/active"
args=("$@")
quiet=0
clean=()
for a in "${args[@]}"; do
  [[ "$a" == "--quiet" ]] && { quiet=1; continue; }
  [[ "$a" == "--no-pager" || "$a" == --lines=* ]] && continue
  clean+=("$a")
done
cmd="${clean[0]:-}"
rest=("${clean[@]:1}")
unit_head() { head -c 40 "$ETC/$1" 2>/dev/null | head -n1; }
case "$cmd" in
  cat)
    [[ -e "$FAKE/missing/${rest[0]}" ]] && exit 1
    exit 0 ;;
  stop)
    echo "stop ${rest[*]} unit_head=$(unit_head "$DISCOVERY")" >>"$FAKE/calls.log"
    if [[ -e "$FAKE/stop_fails/${rest[0]}" ]]; then
      echo "Failed to stop ${rest[0]}: simulated" >&2
      exit 1
    fi
    rm -f "$FAKE/active/${rest[0]}"
    exit 0 ;;
  start)
    echo "start ${rest[*]}" >>"$FAKE/calls.log"
    touch "$FAKE/active/${rest[0]}"
    exit 0 ;;
  restart)
    echo "restart ${rest[*]}" >>"$FAKE/calls.log"
    for u in "${rest[@]}"; do touch "$FAKE/active/$u"; done
    exit 0 ;;
  daemon-reload)
    echo "daemon-reload unit_head=$(unit_head "$DISCOVERY")" >>"$FAKE/calls.log"
    exit 0 ;;
  enable)
    echo "enable ${rest[*]}" >>"$FAKE/calls.log"
    if [[ -e "$FAKE/enable_fails" ]]; then
      echo "Job for ${rest[1]} failed: start-limit-hit (simulated)" >&2
      exit 1
    fi
    for u in "${rest[@]}"; do
      [[ "$u" == --now ]] && continue
      [[ "$u" == "$DISCOVERY" && -e "$FAKE/hold_dropin" ]] && continue
      touch "$FAKE/active/$u"
      [[ "$u" == "$DISCOVERY" ]] && echo "start-discovery" >>"$FAKE/calls.log"
    done
    exit 0 ;;
  is-active)
    rc=0
    for u in "${rest[@]}"; do
      if [[ -e "$FAKE/active/$u" ]]; then
        [[ "$quiet" -eq 1 ]] || echo active
      else
        [[ "$quiet" -eq 1 ]] || echo inactive
        rc=3
      fi
    done
    exit "$rc" ;;
  show)
    unit="${rest[0]}"
    if [[ " ${rest[*]} " == *" ControlGroup "* ]]; then
      echo "/system.slice/$unit"
    else
      echo "MemoryHigh=3221225472"
    fi
    exit 0 ;;
  status)
    echo "status ${rest[*]}" >>"$FAKE/calls.log"
    exit 0 ;;
  *)
    echo "unexpected systemctl call: ${args[*]}" >>"$FAKE/calls.log"
    exit 0 ;;
esac
"""


def _rewrite(source: str, root: Path, fake: Path) -> str:
    return (
        source.replace("/srv/apps/dev/criptofarol/source", str(root))
        .replace('[[ "${EUID}" -ne 0 ]]', "[[ 0 -ne 0 ]]")
        .replace("/etc/systemd/system", str(fake / "etc"))
        .replace("/run/systemd/system", str(fake / "run"))
        .replace("/sys/fs/cgroup", str(fake / "cgroup"))
    )


class RestartHarness:
    def __init__(self, tmp_path: Path):
        self.root = (tmp_path / "canonical").resolve()
        self.fake = (tmp_path / "fake").resolve()
        self.etc = self.fake / "etc"
        self.calls_log = self.fake / "calls.log"
        self.procs_file = self.fake / "cgroup" / "system.slice" / DISCOVERY_UNIT / "cgroup.procs"
        stubs = tmp_path / "stubs"
        for d in (self.root, self.fake, self.etc, stubs, self.procs_file.parent):
            d.mkdir(parents=True, exist_ok=True)
        (self.fake / "run").mkdir(exist_ok=True)
        for sub in ("active", "missing", "stop_fails"):
            (self.fake / sub).mkdir(exist_ok=True)
        self.calls_log.touch()
        self.procs_file.touch()

        for name in ("restart", "install-discovery-workers-systemd.sh"):
            copy = self.root / name
            copy.write_text(_rewrite((REPO_ROOT / name).read_text(), self.root, self.fake))
            copy.chmod(0o755)
        shutil.copytree(REPO_ROOT / "ops" / "systemd", self.root / "ops" / "systemd")

        (self.root / "backend" / ".venv" / "bin").mkdir(parents=True)
        (self.root / "backend" / ".env").write_text("")
        (self.root / "frontend").mkdir()
        self._exe(self.root / "backend" / ".venv" / "bin" / "alembic", "#!/bin/sh\nexit 0\n")
        self._exe(self.root / "install-candle-writer-systemd.sh", "#!/bin/sh\nexit 0\n")
        self._exe(stubs / "curl", "#!/bin/sh\nexit 0\n")
        self._exe(stubs / "npm", "#!/bin/sh\nexit 0\n")
        self._exe(stubs / "sleep", "#!/bin/sh\nexit 0\n")
        self._exe(stubs / "sudo", "#!/bin/sh\necho 'sudo must not be called' >&2\nexit 99\n")
        self._exe(stubs / "systemctl", SYSTEMCTL_STUB)
        self.stubs = stubs

        for unit in (BACKEND_UNIT, FRONTEND_UNIT, RUNTIME_UNIT, DISCOVERY_UNIT):
            (self.etc / unit).write_text(OLD_UNIT_CONTENT)

    @staticmethod
    def _exe(path: Path, content: str) -> None:
        path.write_text(content)
        path.chmod(0o755)

    def set_active(self, *units: str) -> None:
        for unit in units:
            (self.fake / "active" / unit).touch()

    def flag(self, relative: str) -> None:
        target = self.fake / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.touch()

    def run(self) -> subprocess.CompletedProcess:
        env = {
            **os.environ,
            "PATH": f"{self.stubs}:{os.environ.get('PATH', '')}",
            "FAKE_SYSTEMD": str(self.fake),
            "FAKE_ETC": str(self.etc),
            "DISCOVERY": DISCOVERY_UNIT,
        }
        return subprocess.run(
            [str(self.root / "restart")],
            cwd=self.root,
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    @property
    def calls(self) -> list[str]:
        return self.calls_log.read_text().splitlines()

    def unit_text(self, unit: str = DISCOVERY_UNIT) -> str:
        return (self.etc / unit).read_text()


@pytest.fixture()
def harness(tmp_path):
    return RestartHarness(tmp_path)


def _index(calls: list[str], prefix: str) -> int:
    for i, line in enumerate(calls):
        if line.startswith(prefix):
            return i
    raise AssertionError(f"no call starting with {prefix!r} in {calls}")


def _assert_stop_install_start_order(h: RestartHarness) -> None:
    calls = h.calls
    stop = _index(calls, f"stop {DISCOVERY_UNIT}")
    reload_ = _index(calls, "daemon-reload")
    enable = _index(calls, "enable --now")
    assert stop < reload_ < enable
    # Unit file still old when stopped, already the rendered template at reload.
    assert f"unit_head={OLD_UNIT_CONTENT}" in calls[stop]
    assert "unit_head=[Unit]" in calls[reload_]
    assert DISCOVERY_UNIT in calls[enable] and RUNTIME_UNIT in calls[enable]
    # Exactly one Discovery start, and never a `restart` of it.
    assert calls.count("start-discovery") == 1
    assert not any(c.startswith("restart") and DISCOVERY_UNIT in c for c in calls), calls
    # No plain `start <discovery>` besides the installer's `enable --now`.
    assert not any(c.startswith(f"start {DISCOVERY_UNIT}") for c in calls), calls
    assert sum(DISCOVERY_UNIT in c for c in calls if c.startswith("enable")) == 1
    # backend/frontend are still restarted.
    restart_line = calls[_index(calls, "restart ")]
    assert BACKEND_UNIT in restart_line and FRONTEND_UNIT in restart_line
    assert any(c.startswith(f"stop {RUNTIME_UNIT}") for c in calls)


def test_restart_stops_active_discovery_then_installs_and_starts_once(harness):
    harness.set_active(DISCOVERY_UNIT, RUNTIME_UNIT, BACKEND_UNIT, FRONTEND_UNIT)

    result = harness.run()

    assert result.returncode == 0, result.stderr
    _assert_stop_install_start_order(harness)
    assert "crypto DEV discovery workers: active" in result.stdout
    assert "__ROOT_DIR__" not in harness.unit_text()
    assert str(harness.root) in harness.unit_text()


def test_restart_with_discovery_already_stopped_still_succeeds(harness):
    harness.set_active(RUNTIME_UNIT, BACKEND_UNIT, FRONTEND_UNIT)

    result = harness.run()

    assert result.returncode == 0, result.stderr
    _assert_stop_install_start_order(harness)


def test_restart_stops_discovery_even_when_installed_unit_equals_template(harness):
    template = (REPO_ROOT / "ops/systemd" / DISCOVERY_UNIT).read_text()
    (harness.etc / DISCOVERY_UNIT).write_text(template.replace("__ROOT_DIR__", str(harness.root)))
    harness.set_active(DISCOVERY_UNIT, RUNTIME_UNIT, BACKEND_UNIT, FRONTEND_UNIT)

    result = harness.run()

    assert result.returncode == 0, result.stderr
    calls = harness.calls
    stop = _index(calls, f"stop {DISCOVERY_UNIT}")
    assert stop < _index(calls, "daemon-reload") < _index(calls, "enable --now")
    assert calls.count("start-discovery") == 1


def test_restart_skips_stop_when_discovery_unit_not_installed_yet(harness):
    (harness.fake / "missing" / DISCOVERY_UNIT).touch()
    harness.set_active(RUNTIME_UNIT, BACKEND_UNIT, FRONTEND_UNIT)

    result = harness.run()

    assert result.returncode == 0, result.stderr
    assert not any(c.startswith(f"stop {DISCOVERY_UNIT}") for c in harness.calls)
    assert harness.calls.count("start-discovery") == 1


def test_restart_leftover_process_fails_without_installing_or_killing(harness):
    victim = subprocess.Popen(["sleep", "300"])
    try:
        harness.procs_file.write_text(f"{victim.pid}\n")
        harness.set_active(RUNTIME_UNIT, BACKEND_UNIT, FRONTEND_UNIT)

        result = harness.run()

        assert result.returncode != 0
        assert f"/system.slice/{DISCOVERY_UNIT}" in result.stderr
        assert f"PID {victim.pid}" in result.stderr
        assert "sleep 300" in result.stderr
        assert "NOT applied" in result.stderr and "não aplicados" in result.stderr
        # Nothing installed, reloaded, enabled or restarted; unit file intact.
        assert harness.unit_text() == OLD_UNIT_CONTENT
        calls = harness.calls
        assert not any(c.startswith(("daemon-reload", "enable", "restart")) for c in calls)
        assert calls.count("start-discovery") == 0
        # Nothing was killed by the restart.
        assert victim.poll() is None
    finally:
        victim.send_signal(signal.SIGKILL)
        victim.wait()


def test_restart_leftover_process_that_vanished_is_listed_with_placeholder(harness):
    harness.procs_file.write_text("2147483000\n")
    harness.set_active(RUNTIME_UNIT, BACKEND_UNIT, FRONTEND_UNIT)

    result = harness.run()

    assert result.returncode != 0
    assert "PID 2147483000: ?" in result.stderr
    assert "No such file" not in result.stderr
    assert harness.unit_text() == OLD_UNIT_CONTENT


def test_restart_missing_installer_fails_before_stopping_discovery(harness):
    (harness.root / "install-discovery-workers-systemd.sh").unlink()
    harness.set_active(DISCOVERY_UNIT, RUNTIME_UNIT, BACKEND_UNIT, FRONTEND_UNIT)

    result = harness.run()

    assert result.returncode != 0
    assert "install-discovery-workers-systemd.sh" in result.stderr
    assert "nothing was stopped" in result.stderr
    assert not any(
        c.startswith(("stop", "daemon-reload", "enable", "restart")) for c in harness.calls
    )
    assert (harness.fake / "active" / DISCOVERY_UNIT).exists()
    assert harness.unit_text() == OLD_UNIT_CONTENT


def test_restart_stop_failure_exits_nonzero_and_installs_nothing(harness):
    harness.flag(f"stop_fails/{DISCOVERY_UNIT}")
    harness.set_active(DISCOVERY_UNIT, RUNTIME_UNIT, BACKEND_UNIT, FRONTEND_UNIT)

    result = harness.run()

    assert result.returncode != 0
    assert "did not stop" in result.stderr
    assert "NOT applied" in result.stderr
    assert harness.unit_text() == OLD_UNIT_CONTENT
    assert not any(c.startswith(("daemon-reload", "enable", "restart")) for c in harness.calls)


def test_restart_start_limit_refusal_fails_with_clear_message_and_no_reset_failed(harness):
    harness.flag("enable_fails")
    harness.set_active(DISCOVERY_UNIT, RUNTIME_UNIT, BACKEND_UNIT, FRONTEND_UNIT)

    result = harness.run()

    assert result.returncode != 0
    assert "StartLimitBurst" in result.stderr
    assert "wait and repeat" in result.stderr
    assert "stopped" in result.stderr
    assert not any("reset-failed" in c for c in harness.calls)
    assert not any(c.startswith("restart") for c in harness.calls)


def test_restart_containment_dropin_is_reported_when_discovery_does_not_start(harness):
    hold = harness.fake / "run" / f"{DISCOVERY_UNIT}.d" / "card-1093-hold.conf"
    hold.parent.mkdir(parents=True)
    hold.touch()
    harness.flag("hold_dropin")
    harness.set_active(DISCOVERY_UNIT, RUNTIME_UNIT, BACKEND_UNIT, FRONTEND_UNIT)

    result = harness.run()

    assert result.returncode != 0
    assert "card-1093-hold.conf" in result.stderr
    assert "prevents the start" in result.stderr


def test_restart_source_does_not_restart_discovery_in_final_restart_call():
    source = (REPO_ROOT / "restart").read_text()
    dev_block = source.split("# BEGIN CANONICAL DEV RESTART", 1)[1].split(
        "# END CANONICAL DEV RESTART", 1
    )[0]
    restart_call = dev_block.rsplit("systemctl restart", 1)[1].split("\n\n", 1)[0]
    assert "DEV_DISCOVERY_WORKER_UNIT" not in restart_call
    code = "\n".join(line for line in dev_block.splitlines() if not line.lstrip().startswith("#"))
    assert "reset-failed" not in code

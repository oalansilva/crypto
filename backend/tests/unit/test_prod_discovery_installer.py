"""Installer contract for the PROD Discovery ceiling (#1110).

The real installer is copied to temporary canonical roots with the root check,
/etc/systemd/system and /sys/fs/cgroup rewritten to test paths. systemctl and
sleep are stubs and the active-search probe is replaced through
DISCOVERY_ACTIVE_PROBE_CMD, so no real service, database or sudo is touched.
"""

from pathlib import Path
import os
import shutil
import signal
import subprocess

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
DEV_ROOT = "/srv/apps/dev/criptofarol/source"
PROD_ROOT = "/srv/apps/prod/criptofarol/source"
PROD_DISCOVERY = "criptofarol-prod-discovery-worker.service"
PROD_RUNTIME = "criptofarol-prod-runtime-worker.service"
PROD_BACKEND = "criptofarol-prod-backend.service"
DEV_DISCOVERY = "criptofarol-dev-discovery-worker.service"
SENTINEL = "OLD-UNIT-SENTINEL"
PENDING_ONLY = (
    '{"active": false, "error": null, "sweeps": '
    '[{"id": "s1", "state": "pending", "active": false, "reasons": []}]}'
)
ACTIVE = (
    '{"active": true, "error": null, "sweeps": '
    '[{"id": "busca-cliente", "state": "running", "active": true, "reasons": ["sweep_state"]}]}'
)

SYSTEMCTL = r"""#!/usr/bin/env bash
FAKE="${FAKE_SYSTEMD}"
args=("$@")
clean=()
quiet=0
for a in "${args[@]}"; do
  [[ "$a" == "--quiet" ]] && { quiet=1; continue; }
  clean+=("$a")
done
cmd="${clean[0]:-}"
rest=("${clean[@]:1}")
echo "$cmd ${rest[*]}" >>"$FAKE/calls.log"
case "$cmd" in
  stop)
    [[ -e "$FAKE/stop_fails" ]] && { echo "Failed to stop: simulated" >&2; exit 1; }
    [[ -e "$FAKE/stop_leaves_active" ]] || rm -f "$FAKE/active/${rest[0]}"
    exit 0 ;;
  enable)
    [[ -e "$FAKE/enable_fails" ]] && { echo "start-limit-hit (simulated)" >&2; exit 1; }
    for u in "${rest[@]}"; do
      [[ "$u" == --now ]] && continue
      touch "$FAKE/active/$u"
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
    if [[ " ${rest[*]} " == *" ControlGroup "* ]]; then
      echo "/system.slice/${rest[0]}"
    else
      echo "MemoryHigh=4294967296"
      echo "MemoryMax=5368709120"
    fi
    exit 0 ;;
  *) exit 0 ;;
esac
"""

PROBE = r"""#!/usr/bin/env bash
# Pops one exit code per call from $FAKE/probe_rc (the last one repeats) and
# prints the matching JSON payload.
FAKE="${FAKE_SYSTEMD}"
echo probe >>"$FAKE/probe.log"
mapfile -t codes <"$FAKE/probe_rc"
rc="${codes[0]:-0}"
if [[ "${#codes[@]}" -gt 1 ]]; then printf '%s\n' "${codes[@]:1}" >"$FAKE/probe_rc"; fi
cat "$FAKE/probe_json"
exit "$rc"
"""


class Harness:
    def __init__(self, tmp_path: Path):
        self.fake = (tmp_path / "fake").resolve()
        self.etc = self.fake / "etc"
        self.cgroup = self.fake / "cgroup"
        self.stubs = tmp_path / "stubs"
        self.roots = {
            "dev": (tmp_path / "dev-root").resolve(),
            "prod": (tmp_path / "prod-root").resolve(),
        }
        for d in (self.fake / "active", self.etc, self.stubs, *self.roots.values()):
            d.mkdir(parents=True, exist_ok=True)
        (self.fake / "calls.log").touch()
        for unit in (DEV_DISCOVERY, PROD_DISCOVERY, PROD_RUNTIME, PROD_BACKEND):
            (self.etc / unit).write_text(SENTINEL)
        self.procs = self.cgroup / "system.slice" / PROD_DISCOVERY / "cgroup.procs"
        self.procs.parent.mkdir(parents=True)
        self.procs.touch()
        self.set_probe(PENDING_ONLY, 0)
        source = (REPO_ROOT / "install-discovery-workers-systemd.sh").read_text()
        rewritten = (
            source.replace(DEV_ROOT, str(self.roots["dev"]))
            .replace(PROD_ROOT, str(self.roots["prod"]))
            .replace('[[ "${EUID}" -ne 0 ]]', "[[ 0 -ne 0 ]]")
            .replace("/etc/systemd/system", str(self.etc))
            .replace("/run/systemd/system", str(self.fake / "run"))
            .replace("/sys/fs/cgroup", str(self.cgroup))
        )
        for root in self.roots.values():
            installer = root / "install-discovery-workers-systemd.sh"
            installer.write_text(rewritten)
            installer.chmod(0o755)
            shutil.copytree(REPO_ROOT / "ops" / "systemd", root / "ops" / "systemd")
        self._exe(self.stubs / "systemctl", SYSTEMCTL)
        self._exe(self.stubs / "sleep", '#!/bin/sh\necho "sleep $*" >>"$FAKE_SYSTEMD/calls.log"\n')
        self._exe(self.stubs / "sudo", "#!/bin/sh\necho 'sudo must not be called' >&2\nexit 99\n")
        self._exe(self.fake / "probe.sh", PROBE)

    @staticmethod
    def _exe(path: Path, content: str):
        path.write_text(content)
        path.chmod(0o755)

    def set_probe(self, payload: str, *codes: int):
        (self.fake / "probe_json").write_text(payload)
        (self.fake / "probe_rc").write_text("\n".join(str(c) for c in codes) + "\n")

    def set_active(self, *units: str):
        for unit in units:
            (self.fake / "active" / unit).touch()

    def flag(self, name: str):
        (self.fake / name).touch()

    def run(self, target="prod", *args: str, probe_cmd=None):
        root = self.roots[target]
        env = {
            **os.environ,
            "PATH": f"{self.stubs}:{os.environ.get('PATH', '')}",
            "FAKE_SYSTEMD": str(self.fake),
            "DISCOVERY_ACTIVE_PROBE_CMD": (
                f"bash {self.fake / 'probe.sh'}" if probe_cmd is None else probe_cmd
            ),
        }
        return subprocess.run(
            [
                "bash",
                str(root / "install-discovery-workers-systemd.sh"),
                "--root",
                str(root),
                *args,
            ],
            env=env,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    @property
    def calls(self):
        return (self.fake / "calls.log").read_text().splitlines()

    @property
    def probes(self):
        path = self.fake / "probe.log"
        return len(path.read_text().splitlines()) if path.exists() else 0

    def unit_text(self, unit):
        return (self.etc / unit).read_text()

    def mutated(self):
        return [
            c
            for c in self.calls
            if c.startswith(("stop", "daemon-reload", "enable", "restart", "start"))
        ]


@pytest.fixture()
def h(tmp_path):
    return Harness(tmp_path)


def test_prod_discovery_only_dry_run_lists_only_the_discovery_unit(h):
    result = h.run("prod", "--dry-run", "--discovery-only")
    assert result.returncode == 0, result.stderr
    assert f"units={PROD_DISCOVERY}\n" in result.stdout
    assert PROD_RUNTIME not in result.stdout
    assert "backend_dropin=none" in result.stdout
    assert h.probes == 0 and h.mutated() == []


def test_prod_full_dry_run_still_lists_runtime_and_discovery(h):
    result = h.run("prod", "--dry-run")
    assert result.returncode == 0, result.stderr
    assert f"units={PROD_RUNTIME} {PROD_DISCOVERY}\n" in result.stdout


def test_idle_prod_stops_only_discovery_installs_only_its_unit_and_starts_once(h):
    h.set_active(PROD_DISCOVERY, PROD_RUNTIME, PROD_BACKEND)

    result = h.run("prod", "--discovery-only")

    assert result.returncode == 0, result.stderr
    calls = h.calls
    stop = calls.index(f"stop {PROD_DISCOVERY}")
    reload_ = calls.index("daemon-reload ")
    enable = calls.index(f"enable --now {PROD_DISCOVERY}")
    assert stop < reload_ < enable
    assert [c for c in calls if c.startswith(("stop", "enable", "restart", "start"))] == [
        f"stop {PROD_DISCOVERY}",
        f"enable --now {PROD_DISCOVERY}",
    ]
    # Only the Discovery unit file was rewritten; runtime and backend are untouched.
    assert "__ROOT_DIR__" not in h.unit_text(PROD_DISCOVERY)
    assert str(h.roots["prod"]) in h.unit_text(PROD_DISCOVERY)
    assert h.unit_text(PROD_RUNTIME) == SENTINEL and h.unit_text(PROD_BACKEND) == SENTINEL
    assert not any(
        PROD_RUNTIME in c or PROD_BACKEND in c for c in calls if not c.startswith("is-active")
    )
    # D8 verification is printed with the properties the card demands.
    shown = [c for c in calls if c.startswith("show") and "MemoryHigh" in c][0]
    for prop in (
        "MemoryHigh MemoryMax MemorySwapMax OOMPolicy KillMode Restart RestartUSec "
        "StartLimitBurst StartLimitIntervalUSec TimeoutStopUSec ActiveState NRestarts"
    ).split():
        assert f"-p {prop}" in shown
    assert "Verificação" in result.stdout and "MemoryMax=5368709120" in result.stdout


def test_queued_pending_sweep_does_not_block_applying_the_ceiling(h):
    h.set_active(PROD_DISCOVERY)
    h.set_probe(PENDING_ONLY, 0)

    result = h.run("prod", "--discovery-only")

    assert result.returncode == 0, result.stderr
    assert "s1" in result.stdout  # the pending sweep is listed
    assert f"stop {PROD_DISCOVERY}" in h.calls and h.probes == 2  # before and after the stop
    assert not any(c.startswith("sleep") for c in h.calls)


def test_active_search_past_the_deadline_defers_and_touches_nothing(h):
    h.set_active(PROD_DISCOVERY)
    h.set_probe(ACTIVE, 3)

    result = h.run("prod", "--discovery-only", "--wait-idle", "2")

    assert result.returncode == 75
    assert "adiado: busca ativa" in result.stderr
    assert "busca-cliente" in result.stderr  # the sweeps found
    assert h.probes == 3  # t=0, 60 s, 120 s
    assert [c for c in h.calls if c.startswith("sleep")] == ["sleep 60", "sleep 60"]
    assert h.mutated() == []
    assert h.unit_text(PROD_DISCOVERY) == SENTINEL
    assert (h.fake / "active" / PROD_DISCOVERY).exists()


def test_wait_idle_zero_defers_immediately_without_sleeping(h):
    h.set_active(PROD_DISCOVERY)
    h.set_probe(ACTIVE, 3)

    result = h.run("prod", "--discovery-only", "--wait-idle", "0")

    assert result.returncode == 75 and "adiado: busca ativa" in result.stderr
    assert h.probes == 1
    assert not any(c.startswith("sleep") for c in h.calls)
    assert h.mutated() == []


def test_default_wait_is_thirty_minutes_of_sixty_second_checks(h):
    h.set_active(PROD_DISCOVERY)
    h.set_probe(ACTIVE, 3)

    result = h.run("prod", "--discovery-only")

    assert result.returncode == 75
    assert h.probes == 31 and len([c for c in h.calls if c == "sleep 60"]) == 30
    assert h.mutated() == []


def test_search_that_finishes_while_waiting_lets_the_ceiling_proceed(h):
    h.set_active(PROD_DISCOVERY)
    h.set_probe(ACTIVE, 3, 3, 0)

    result = h.run("prod", "--discovery-only", "--wait-idle", "5")

    assert result.returncode == 0, result.stderr
    assert len([c for c in h.calls if c.startswith("sleep")]) == 2
    assert h.calls.index(f"stop {PROD_DISCOVERY}") > h.calls.index("sleep 60")


def test_probe_that_cannot_run_counts_as_active(h):
    h.set_active(PROD_DISCOVERY)

    result = h.run("prod", "--discovery-only", "--wait-idle", "0", probe_cmd="exit 127")

    assert result.returncode == 75 and "adiado: busca ativa" in result.stderr
    assert h.mutated() == []


def _default_probe_env(h, with_env_file=True):
    """No DISCOVERY_ACTIVE_PROBE_CMD: the installer runs the real script path."""
    backend = h.roots["prod"] / "backend"
    (backend / ".venv" / "bin").mkdir(parents=True)
    h._exe(
        backend / ".venv" / "bin" / "python",
        '#!/bin/sh\necho "python $* env=$LEDGER_DB cwd=$(pwd)" >>"$FAKE_SYSTEMD/probe.log"\n'
        'echo \'{"active": false, "sweeps": []}\'\n',
    )
    if with_env_file:
        (backend / ".env").write_text("LEDGER_DB=prod-ledger\n")


def test_default_probe_runs_the_script_with_the_prod_env_file(h):
    _default_probe_env(h)
    h.set_active(PROD_DISCOVERY)

    result = h.run("prod", "--discovery-only", probe_cmd="")

    assert result.returncode == 0, result.stderr
    line = (h.fake / "probe.log").read_text().splitlines()[0]
    assert "scripts/discovery/active_search_probe.py" in line
    assert "env=prod-ledger" in line and f"cwd={h.roots['prod']}/backend" in line


def test_default_probe_without_env_file_fails_closed(h):
    _default_probe_env(h, with_env_file=False)
    h.set_active(PROD_DISCOVERY)

    result = h.run("prod", "--discovery-only", "--wait-idle", "0", probe_cmd="")

    assert result.returncode == 75 and "adiado: busca ativa" in result.stderr
    assert h.mutated() == []


def test_lease_appearing_between_probe_and_stop_is_reported_not_fatal(h):
    h.set_active(PROD_DISCOVERY)
    h.set_probe(ACTIVE, 0, 3)

    result = h.run("prod", "--discovery-only")

    assert result.returncode == 0, result.stderr
    assert "aviso" in result.stderr and "busca-cliente" in result.stderr


def test_leftover_process_after_stop_refuses_listing_pids_without_killing(h):
    victim = subprocess.Popen(["sleep", "300"])
    try:
        h.procs.write_text(f"{victim.pid}\n")
        h.set_active(PROD_DISCOVERY)

        result = h.run("prod", "--discovery-only")

        assert result.returncode == 1
        assert f"stop {PROD_DISCOVERY}" in h.calls
        assert f"PID {victim.pid}" in result.stderr and "sleep 300" in result.stderr
        assert "não aplicados" in result.stderr
        assert h.unit_text(PROD_DISCOVERY) == SENTINEL
        assert not any(c.startswith(("daemon-reload", "enable")) for c in h.calls)
        assert victim.poll() is None
    finally:
        victim.send_signal(signal.SIGKILL)
        victim.wait()


def test_cgroup_procs_is_judged_by_content_not_by_file_size(h):
    # cgroup v2 reports size 0 even when PIDs are listed, so the guard reads the
    # content: a blank file is empty, a file with a PID is not (see the test above).
    h.procs.write_text("\n")
    h.set_active(PROD_DISCOVERY)

    result = h.run("prod", "--discovery-only")

    assert result.returncode == 0, result.stderr
    assert "Legacy Discovery descendants" not in result.stderr


def test_unit_still_active_after_stop_refuses(h):
    h.set_active(PROD_DISCOVERY)
    h.flag("stop_leaves_active")

    result = h.run("prod", "--discovery-only")

    assert result.returncode == 1 and "still active" in result.stderr
    assert h.unit_text(PROD_DISCOVERY) == SENTINEL
    assert not any(c.startswith(("daemon-reload", "enable")) for c in h.calls)


def test_stop_failure_installs_nothing(h):
    h.set_active(PROD_DISCOVERY)
    h.flag("stop_fails")

    result = h.run("prod", "--discovery-only")

    assert result.returncode == 1 and "did not stop" in result.stderr
    assert h.unit_text(PROD_DISCOVERY) == SENTINEL
    assert not any(c.startswith(("daemon-reload", "enable")) for c in h.calls)


def test_start_limit_refusal_is_explained_and_never_reset(h):
    h.set_active(PROD_DISCOVERY)
    h.flag("enable_fails")

    result = h.run("prod", "--discovery-only")

    assert result.returncode == 1
    assert "StartLimitBurst" in result.stderr and "wait and repeat" in result.stderr
    assert not any("reset-failed" in c for c in h.calls)


def test_full_prod_install_refuses_to_rewrite_a_running_discovery_unit(h):
    h.set_active(PROD_DISCOVERY)

    result = h.run("prod")

    assert result.returncode == 1 and "--discovery-only" in result.stderr
    assert h.unit_text(PROD_DISCOVERY) == SENTINEL and h.unit_text(PROD_RUNTIME) == SENTINEL
    assert h.mutated() == []


def test_full_prod_install_with_discovery_stopped_installs_both(h):
    result = h.run("prod")

    assert result.returncode == 0, result.stderr
    assert "__ROOT_DIR__" not in h.unit_text(PROD_RUNTIME)
    assert "__ROOT_DIR__" not in h.unit_text(PROD_DISCOVERY)
    assert h.probes == 0


def test_dev_discovery_only_keeps_its_guard_and_never_probes_or_stops(h):
    h.set_active(DEV_DISCOVERY)

    result = h.run("dev", "--discovery-only")

    assert result.returncode == 1 and "still active" in result.stderr
    assert "DEV Discovery" in result.stderr
    assert h.probes == 0
    assert not any(c.startswith("stop") for c in h.calls)
    assert h.unit_text(DEV_DISCOVERY) == SENTINEL


def test_invalid_wait_idle_is_rejected(h):
    result = h.run("prod", "--discovery-only", "--wait-idle", "abc")
    assert result.returncode == 2 and h.mutated() == []


def test_unit_templates_carry_the_approved_ceilings():
    prod = (REPO_ROOT / "ops/systemd" / PROD_DISCOVERY).read_text()
    dev = (REPO_ROOT / "ops/systemd" / DEV_DISCOVERY).read_text()
    for text, high, maximum, profile in ((prod, "4G", "5G", "prod"), (dev, "3G", "4G", "dev")):
        lines = text.splitlines()
        for expected in (
            f"MemoryHigh={high}",
            f"MemoryMax={maximum}",
            "MemorySwapMax=512M",
            "MemoryAccounting=yes",
            "OOMPolicy=kill",
            "KillMode=control-group",
            "TimeoutStopSec=30s",
            "SendSIGKILL=yes",
            "Restart=on-failure",
            "RestartSec=60",
            "StartLimitIntervalSec=900",
            "StartLimitBurst=3",
            f"Environment=DISCOVERY_RESOURCE_PROFILE={profile}",
            "Environment=DISCOVERY_INTERNAL_WORKERS=1",
            f"Environment=DISCOVERY_SPOOL_DIR=/var/tmp/criptofarol-{profile}-discovery",
            f"StateDirectory=criptofarol-{profile}-discovery",
        ):
            assert expected in lines, (profile, expected)
        assert "--hostname=discovery-" + profile in text and "--pool=solo" in text

"""Operator scripts for the per-environment Discovery ceiling (#1110)."""

import importlib.util
import json
import os
from pathlib import Path

import pytest

from app.services import discovery_recovery
from app.services import discovery_resources as resources
from app.services.discovery_resources import GiB, OperationalFailure, ResourceProfile

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts" / "discovery"
HOST = {"MemTotal": 23 * GiB, "MemAvailable": 9 * GiB, "SwapFree": 2 * GiB}


def load(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_limits(group, profile):
    group.mkdir(parents=True, exist_ok=True)
    for key, value in {
        "memory.high": profile.memory_high,
        "memory.max": profile.memory_max,
        "memory.swap.max": profile.swap_max,
        "memory.oom.group": 1,
    }.items():
        (group / key).write_text(str(value))


def test_unit_and_cgroup_are_derived_from_the_environment():
    assert resources.discovery_unit("dev") == "criptofarol-dev-discovery-worker.service"
    assert resources.discovery_unit("prod") == "criptofarol-prod-discovery-worker.service"
    assert resources.unit_cgroup("prod") == Path(
        "/sys/fs/cgroup/system.slice/criptofarol-prod-discovery-worker.service"
    )
    with pytest.raises(OperationalFailure):
        resources.discovery_unit("staging")


@pytest.mark.parametrize("env", ["dev", "prod"])
def test_admission_probe_passes_against_the_unit_cgroup_with_the_environment_profile(
    tmp_path, env
):
    probe = load("admission_probe")
    write_limits(tmp_path, ResourceProfile.named(env))
    result = probe.probe(env, group=tmp_path, spool_root=tmp_path, memory=HOST)
    assert result["name"] == env


def test_admission_probe_refuses_unit_with_the_other_environments_limits(tmp_path, capsys):
    probe = load("admission_probe")
    write_limits(tmp_path, ResourceProfile.named("dev"))
    with pytest.raises(OperationalFailure):
        probe.probe("prod", group=tmp_path, spool_root=tmp_path, memory=HOST)
    # Missing cgroup (unit not running) is refused too, never assumed healthy.
    assert probe.main(["--env", "prod", "--group", str(tmp_path / "absent")]) == 1
    assert json.loads(capsys.readouterr().out) == {
        "admitted": False,
        "code": "resource_budget_unavailable",
        "env": "prod",
    }


def test_acknowledge_targets_the_prod_unit_without_touching_circuit_rules():
    ack = load("acknowledge_circuit")
    profile, unit, group = ack.derive_target("prod")
    assert profile == ResourceProfile.named("prod")
    assert unit == "criptofarol-prod-discovery-worker.service"
    assert group == Path("/sys/fs/cgroup/system.slice/criptofarol-prod-discovery-worker.service")
    assert ack.derive_target("dev")[1] == "criptofarol-dev-discovery-worker.service"
    assert ack.derive_target("dev", "/x")[2] == Path("/x")


def test_acknowledge_empty_check_queries_the_environment_unit(tmp_path, monkeypatch):
    ack = load("acknowledge_circuit")
    calls = []

    def fake_show(command, text):
        calls.append(command)
        return "MainPID=0\nActiveState=inactive\nControlGroup=\n"

    monkeypatch.setattr(ack.subprocess, "check_output", fake_show)
    unit = resources.discovery_unit("prod")
    assert ack.groups_are_empty(unit, tmp_path / "absent") is True
    assert calls[0][:3] == ["systemctl", "show", "criptofarol-prod-discovery-worker.service"]
    (tmp_path / "cgroup.procs").write_text("123\n")
    assert ack.groups_are_empty(unit, tmp_path) is False
    (tmp_path / "cgroup.procs").write_text("")
    assert ack.groups_are_empty(unit, tmp_path) is True


def run_acknowledge(ack, monkeypatch, argv, cgroup=None):
    seen = {}
    monkeypatch.setattr(ack.os, "geteuid", lambda: 0)
    monkeypatch.setattr(ack, "admission", lambda profile: seen.setdefault("profile", profile))
    monkeypatch.setattr(ack, "groups_are_empty", lambda unit, group: seen.update(unit=unit) or True)
    # main() assigns os.environ directly; setenv first so monkeypatch restores
    # (removes) the variable at teardown instead of leaking it to later tests.
    monkeypatch.setenv("DISCOVERY_RESOURCE_PROFILE", "x")
    monkeypatch.delenv("DISCOVERY_RESOURCE_PROFILE")
    monkeypatch.setenv("APP_ENV", "x")
    monkeypatch.delenv("APP_ENV")
    if cgroup:
        monkeypatch.setattr(resources, "cgroup_path", lambda: Path("/s/system.slice") / cgroup)

    class Session:
        def __enter__(self):
            return "db"

        def __exit__(self, *_):
            return False

    def fake_acknowledge(db, actor, reason, healthy, groups_empty):
        seen.update(
            circuit_env=discovery_recovery.environment(),
            reason=reason,
            healthy=healthy,
            groups_empty=groups_empty,
        )

    import app.database as database

    monkeypatch.setattr(database, "SessionLocal", Session)
    monkeypatch.setattr(discovery_recovery, "acknowledge", fake_acknowledge)
    ack.main(argv)
    return seen


def test_acknowledge_prod_uses_prod_profile_unit_and_circuit_key(monkeypatch):
    ack = load("acknowledge_circuit")
    seen = run_acknowledge(ack, monkeypatch, ["--reason", "teste", "--env", "prod"])
    assert seen["profile"] == ResourceProfile.named("prod")
    assert seen["unit"] == "criptofarol-prod-discovery-worker.service"
    assert seen["circuit_env"] == "prod"
    assert (seen["healthy"], seen["groups_empty"], seen["reason"]) == (True, True, "teste")


def test_acknowledge_does_not_leak_profile_to_later_tests(monkeypatch):
    ack = load("acknowledge_circuit")
    before = os.environ.get("DISCOVERY_RESOURCE_PROFILE")
    with monkeypatch.context() as scoped:
        run_acknowledge(ack, scoped, ["--reason", "teste", "--env", "prod"])
        assert os.environ["DISCOVERY_RESOURCE_PROFILE"] == "prod"
    assert os.environ.get("DISCOVERY_RESOURCE_PROFILE") == before


def test_acknowledge_default_stays_dev(monkeypatch):
    ack = load("acknowledge_circuit")
    seen = run_acknowledge(ack, monkeypatch, ["--reason", "teste"])
    assert seen["profile"] == ResourceProfile.named("dev")
    assert seen["unit"] == "criptofarol-dev-discovery-worker.service"
    assert seen["circuit_env"] == "dev"


def test_acknowledge_refuses_when_unit_cgroup_overrides_the_environment(monkeypatch):
    ack = load("acknowledge_circuit")
    with pytest.raises(SystemExit):
        run_acknowledge(
            ack,
            monkeypatch,
            ["--reason", "x", "--env", "prod"],
            cgroup="criptofarol-dev-backend.service",
        )

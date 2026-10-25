"""Every Celery queue the app publishes to must have a worker that consumes it (#1120).

The batch backtest (``batch_backtest`` queue) sat unconsumed in DEV and PROD
because only the Discovery worker (``-Q discovery``) existed. This contract reads
``celery_app.conf.task_routes`` and the systemd templates under ``ops/systemd`` and
fails when a routed queue has no worker template that consumes it with ``-Q`` for
DEV and for PROD, or when that worker would not be installed, restarted and
evidenced by the release flow.
"""

from __future__ import annotations

import importlib
import re
import sys
from pathlib import Path

import pytest
import yaml

from app.celery_app import celery_app

REPO_ROOT = Path(__file__).resolve().parents[3]
SYSTEMD_DIR = REPO_ROOT / "ops" / "systemd"
ENVIRONMENTS = ("dev", "prod")
_QUEUE_FLAG = re.compile(r"(?:^|\s)-Q\s+([A-Za-z0-9_.,-]+)")


def _import_task_modules() -> None:
    # The systemd units run with PYTHONPATH=<root>:<root>/backend; the Discovery task needs ``src``.
    if str(REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(REPO_ROOT))
    for module in celery_app.conf.include or ():
        importlib.import_module(module)


def _routed_queues() -> dict[str, str]:
    routes = celery_app.conf.task_routes or {}
    queues: dict[str, str] = {}
    for task_name, route in routes.items():
        queue = route["queue"] if isinstance(route, dict) else str(route)
        queues[task_name] = queue
    return queues


def _consumers(environment: str) -> dict[str, list[str]]:
    """queue -> worker units of the environment that consume it with ``-Q``."""

    consumers: dict[str, list[str]] = {}
    for template in sorted(SYSTEMD_DIR.glob(f"criptofarol-{environment}-*.service")):
        exec_start = next(
            (
                line
                for line in template.read_text().splitlines()
                if line.startswith("ExecStart=") and "celery" in line and " worker " in line
            ),
            None,
        )
        if exec_start is None:
            continue
        match = _QUEUE_FLAG.search(exec_start)
        assert match, f"Celery worker template without -Q consumes every queue: {template.name}"
        for queue in match.group(1).split(","):
            consumers.setdefault(queue, []).append(template.name)
    return consumers


def test_task_routes_are_present_and_name_a_queue():
    routed = _routed_queues()
    assert routed, "celery_app.task_routes is empty; the contract would pass vacuously"
    assert all(routed.values())


def test_every_registered_app_task_is_routed_to_a_queue_that_exists():
    _import_task_modules()
    routed = _routed_queues()
    default_queue = celery_app.conf.task_default_queue
    app_tasks = sorted(name for name in celery_app.tasks if name.startswith("app."))
    assert app_tasks
    for name in app_tasks:
        queue = routed.get(name, default_queue)
        assert queue != default_queue, (
            f"{name} falls on the default queue {default_queue!r}, which no worker consumes: "
            "add it to celery_app.task_routes and give that queue a worker template"
        )


@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_every_routed_queue_has_exactly_one_worker_template_per_environment(environment):
    consumers = _consumers(environment)
    for task_name, queue in _routed_queues().items():
        units = consumers.get(queue, [])
        assert units, (
            f"queue {queue!r} (task {task_name}) has no {environment.upper()} worker template "
            f"under ops/systemd consuming it with -Q: the job would sit in the broker forever"
        )
        assert (
            len(units) == 1
        ), f"queue {queue!r} is consumed by several {environment} units: {units}"


@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_worker_templates_consume_only_routed_queues(environment):
    routed = set(_routed_queues().values())
    for queue, units in _consumers(environment).items():
        assert queue in routed, f"{units} consume {queue!r}, which no task is routed to"


@pytest.mark.parametrize("environment", ENVIRONMENTS)
def test_each_queue_consumer_is_installed_by_the_installer_and_listed_in_the_overlay(environment):
    installer = (REPO_ROOT / "install-discovery-workers-systemd.sh").read_text()
    overlay = yaml.safe_load((REPO_ROOT / ".covenant-flow" / "overlay.yaml").read_text())
    services = overlay["environments"][environment]["services"]
    oneshot = overlay["environments"][environment].get("oneshot_services") or []
    consumers = _consumers(environment)
    for queue in sorted(set(_routed_queues().values())):
        for unit in consumers.get(queue, []):
            assert f'"{unit}"' in installer, f"installer does not install {unit} ({queue})"
            assert unit in services, (
                f"overlay environments.{environment}.services omits {unit}: the release "
                "guard would not require it in PROD_DEPLOY_EVIDENCE"
            )
            assert unit not in oneshot, f"{unit} is a long-running consumer, not a oneshot"

from __future__ import annotations

from app.main import app


def test_admin_backfill_api_routes_are_not_registered():
    paths = {getattr(route, "path", "") or "" for route in app.routes}
    assert not any("/admin/backfill" in path for path in paths)


def test_admin_backfill_modules_are_gone():
    import importlib

    for module_name in ("app.routes.admin_backfill", "app.schemas.backfill"):
        try:
            importlib.import_module(module_name)
        except ModuleNotFoundError:
            continue
        raise AssertionError(f"{module_name} should not exist after surface removal")

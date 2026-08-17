#!/usr/bin/env python3
"""Fail-closed check: new App.tsx product routes need Playwright coverage."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROUTE_RE = re.compile(r"<Route\b([^>]*)>", re.DOTALL)
PATH_RE = re.compile(r'\bpath="([^"]+)"')
NAVIGATE_RE = re.compile(r"<Navigate\b[^>]*\bto=\"([^\"]+)\"")
IGNORE_PREFIXES = ("/prototypes/",)
DEFAULT_INVENTORY = Path("frontend/tests/e2e/route-coverage-inventory.json")
DEFAULT_APP = Path("frontend/src/App.tsx")
DEFAULT_E2E = Path("frontend/tests/e2e")


def repo_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "frontend" / "src" / "App.tsx").exists():
            return parent
    return Path.cwd()


def parse_app_routes(app_source: str) -> list[dict[str, str]]:
    routes: list[dict[str, str]] = []
    for match in ROUTE_RE.finditer(app_source):
        attrs = match.group(1)
        path_match = PATH_RE.search(attrs)
        if not path_match:
            continue
        path = path_match.group(1)
        if path.startswith(IGNORE_PREFIXES) or "PrototypeRedirect" in attrs:
            continue
        navigate = NAVIGATE_RE.search(attrs)
        if navigate:
            routes.append(
                {"path": path, "kind": "alias", "covered_by": navigate.group(1)}
            )
            continue
        routes.append({"path": path, "kind": "page"})
    return routes


def load_inventory(path: Path) -> dict[str, dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return {item["path"]: item for item in payload.get("routes", [])}


def spec_mentions_path(spec_path: Path, route_path: str) -> bool:
    if not spec_path.exists():
        return False
    text = spec_path.read_text(encoding="utf-8")
    return route_path in text


def expected_spec_hint(route_path: str) -> str:
    slug = route_path.strip("/").replace("/", "-").replace(":", "") or "index"
    return f"frontend/tests/e2e/{slug}-visual-critical.spec.ts"


def check_coverage(
    *,
    app_text: str,
    inventory: dict[str, dict],
    e2e_dir: Path,
    allow_visual_skip: bool = False,
) -> list[str]:
    errors: list[str] = []
    for route in parse_app_routes(app_text):
        path = route["path"]
        entry = inventory.get(path)
        if route["kind"] == "alias":
            if entry and entry.get("status") in {"alias", "covered", "grandfathered"}:
                continue
            dest = route.get("covered_by")
            dest_entry = inventory.get(dest or "")
            if dest_entry:
                continue
            errors.append(
                f"Alias route {path} -> {dest} is not inventoried. "
                f"Add it as status=alias covered_by={dest}."
            )
            continue
        if entry is None:
            hint = expected_spec_hint(path)
            if allow_visual_skip:
                continue
            errors.append(
                f"New product route {path} is missing from {DEFAULT_INVENTORY}. "
                f"Add a functional+visual Playwright spec (expected {hint}) "
                f"and an inventory entry in the same diff."
            )
            continue
        status = entry.get("status")
        if status == "grandfathered":
            continue
        if status == "alias":
            continue
        if status == "dispensed" and allow_visual_skip:
            continue
        specs = [entry.get("functional"), entry.get("visual")]
        named = [Path(spec) for spec in specs if spec]
        if not named:
            if allow_visual_skip:
                continue
            errors.append(
                f"Route {path} is inventoried without functional/visual specs. "
                f"Expected {expected_spec_hint(path)}."
            )
            continue
        root = repo_root(e2e_dir)
        for spec in named:
            resolved = spec if spec.is_absolute() else root / spec
            if not resolved.exists():
                errors.append(f"Route {path} inventory points to missing spec {spec}.")
                continue
            if not spec_mentions_path(resolved, path):
                errors.append(
                    f"Route {path} inventory points to {spec}, but that file does not mention the path."
                )
        visual = entry.get("visual")
        if not visual and not allow_visual_skip:
            errors.append(
                f"Route {path} has no visual spec in the inventory. "
                f"Add desktop/mobile snapshots or an authorized qa-visual-skip dispensation."
            )
    return errors


def run_self_test() -> int:
    fixture_app = """
      <Routes>
        <Route path="/prototypes/demo" element={<PrototypeRedirect to="/prototypes/demo/" />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/kanban" element={<Navigate to="/monitor" replace />} />
        <Route path="/combo/new-lab" element={<NewLabPage />} />
      </Routes>
    """
    inventory = {
        "/login": {
            "path": "/login",
            "status": "covered",
            "functional": "frontend/tests/e2e/login-closed-beta.spec.ts",
            "visual": "frontend/tests/e2e/visual-critical.spec.ts",
        },
        "/kanban": {"path": "/kanban", "status": "alias", "covered_by": "/monitor"},
        "/monitor": {"path": "/monitor", "status": "grandfathered"},
    }
    errors = check_coverage(
        app_text=fixture_app,
        inventory=inventory,
        e2e_dir=DEFAULT_E2E,
        allow_visual_skip=False,
    )
    if not any("/combo/new-lab" in err for err in errors):
        print(
            "SELF-TEST FAIL: expected new route /combo/new-lab to fail", file=sys.stderr
        )
        print("\n".join(errors), file=sys.stderr)
        return 1
    skipped = check_coverage(
        app_text=fixture_app,
        inventory=inventory,
        e2e_dir=DEFAULT_E2E,
        allow_visual_skip=True,
    )
    if any("/combo/new-lab" in err for err in skipped):
        print(
            "SELF-TEST FAIL: authorized skip should not fail solely for missing visual spec",
            file=sys.stderr,
        )
        return 1
    aliases = parse_app_routes(fixture_app)
    kinds = {item["path"]: item["kind"] for item in aliases}
    if kinds.get("/prototypes/demo"):
        print("SELF-TEST FAIL: prototype redirect should be ignored", file=sys.stderr)
        return 1
    if kinds.get("/kanban") != "alias":
        print(
            "SELF-TEST FAIL: Navigate alias should be classified as alias",
            file=sys.stderr,
        )
        return 1
    print("SELF-TEST PASS")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--app", type=Path, default=DEFAULT_APP)
    parser.add_argument("--inventory", type=Path, default=DEFAULT_INVENTORY)
    parser.add_argument("--e2e-dir", type=Path, default=DEFAULT_E2E)
    parser.add_argument("--allow-visual-skip", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_test()
    app_text = args.app.read_text(encoding="utf-8")
    inventory = load_inventory(args.inventory)
    errors = check_coverage(
        app_text=app_text,
        inventory=inventory,
        e2e_dir=args.e2e_dir if args.e2e_dir.exists() else args.inventory.parent,
        allow_visual_skip=args.allow_visual_skip,
    )
    if errors:
        print("New-route Playwright coverage check failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1
    print("New-route Playwright coverage check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

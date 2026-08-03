#!/usr/bin/env python3
"""Validate the backend unit-test portfolio inventory.

The validator intentionally compares paths on disk with the JSON inventory so
that adding, renaming, or deleting a ``test_*.py`` file cannot silently leave
the audit stale.  It is usable from CI and from focused contract tests.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

DECISIONS = {"keep", "refactor/consolidate", "remove"}
PERSISTENCE_NEEDS = {"pure", "postgres"}
REQUIRED_FIELDS = {
    "file",
    "protected_behavior",
    "production_reachability",
    "persistence_need",
    "regression_risk",
    "decision",
    "evidence",
}

_MODULE_POSTGRES_MARKER_RE = re.compile(
    r"^\s*pytestmark\s*=\s*pytest\.mark\.postgres\b", re.MULTILINE
)
_EXPLICIT_POSTGRES_FIXTURE_RE = re.compile(
    r"\b(?:postgres_isolation|unit_database_url|unit_workflow_database_url|"
    r"opportunity_postgres)\b"
)
_REAL_PERSISTENCE_RE = re.compile(
    r"\b(?:SessionLocal|create_engine|sessionmaker)\s*\(|"
    r"\b(?:Base|WorkflowBase)\.metadata\.create_all\s*\(|"
    r"\b(?:init_workflow_schema_for_url|get_workflow_engine_for_url|"
    r"get_workflow_sessionmaker_for_url)\s*\("
)
_UNSAFE_DB_LITERAL_RE = re.compile(
    r"postgresql(?:\+[^:/\"']+)?://[^\"'\n]*?/postgres(?:[\"']|$)",
    re.IGNORECASE,
)


class InventoryValidationError(ValueError):
    """Raised when the inventory does not exactly match discovered tests."""


def discovered_unit_test_files(root: Path) -> list[str]:
    unit_dir = root / "backend" / "tests" / "unit"
    return sorted(path.relative_to(root).as_posix() for path in unit_dir.glob("test_*.py"))


def load_inventory(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    entries = payload.get("entries") if isinstance(payload, dict) else payload
    if not isinstance(entries, list):
        raise InventoryValidationError("inventory must contain an 'entries' array")
    if not all(isinstance(entry, dict) for entry in entries):
        raise InventoryValidationError("every inventory entry must be an object")
    return entries


def _source_without_imports(source: str) -> str:
    """Remove import lines before looking for executable DB calls."""

    return "\n".join(
        line for line in source.splitlines() if not line.lstrip().startswith(("import ", "from "))
    )


def _semantic_issues(root: Path, entries: list[dict[str, Any]]) -> list[str]:
    """Catch obvious inventory/fixture mismatches before a suite run.

    This is intentionally a conservative static check.  It does not attempt
    to infer every indirect database call, but it rejects the classes of
    regressions that previously bypassed the safe unit fixtures: broad module
    markers, pure files with real persistence calls, PostgreSQL files with no
    explicit isolation request, and hard-coded shared ``/postgres`` URLs in
    connection paths.  Parser and mock URL strings without a connection call
    remain valid.
    """

    issues: list[str] = []
    for entry in entries:
        file_name = str(entry.get("file", ""))
        if not file_name:
            continue
        path = root / file_name
        if not path.is_file():
            continue
        source = path.read_text(encoding="utf-8")
        executable_source = _source_without_imports(source)
        module_marker = bool(_MODULE_POSTGRES_MARKER_RE.search(source))
        explicit_fixture = bool(_EXPLICIT_POSTGRES_FIXTURE_RE.search(source))
        real_persistence = bool(_REAL_PERSISTENCE_RE.search(executable_source))

        unsafe_shared_url = False
        for match in _UNSAFE_DB_LITERAL_RE.finditer(source):
            context_start = max(0, match.start() - 180)
            context_end = min(len(source), match.end() + 180)
            context = source[context_start:context_end]
            if re.search(r"\b(?:DB_URL|DATABASE_URL|ComboService|create_engine)\b", context):
                unsafe_shared_url = True
                break

        if module_marker:
            issues.append(f"{file_name}: module-level postgres marker is too broad")
        persistence_need = entry.get("persistence_need")
        if persistence_need == "pure":
            if explicit_fixture:
                issues.append(f"{file_name}: pure inventory entry requests PostgreSQL isolation")
            if real_persistence:
                issues.append(f"{file_name}: pure inventory entry contains a real DB call")
            if unsafe_shared_url:
                issues.append(f"{file_name}: pure inventory entry contains a shared /postgres URL")
        elif persistence_need == "postgres":
            if not explicit_fixture:
                issues.append(f"{file_name}: postgres inventory entry lacks explicit isolation")
            if unsafe_shared_url:
                issues.append(f"{file_name}: shared /postgres URL bypasses safe test DB")

    return sorted(issues)


def validate_inventory(root: Path, inventory_path: Path) -> dict[str, Any]:
    entries = load_inventory(inventory_path)
    discovered = discovered_unit_test_files(root)
    paths = [str(entry.get("file", "")) for entry in entries]
    duplicate_paths = sorted({path for path in paths if paths.count(path) > 1 and path})
    stale_paths = sorted(path for path in paths if path not in discovered)
    missing_paths = sorted(path for path in discovered if path not in paths)
    malformed: list[str] = []
    for entry in entries:
        file_name = str(entry.get("file", "<missing file>"))
        missing_fields = sorted(REQUIRED_FIELDS - set(entry))
        invalid_decision = entry.get("decision") not in DECISIONS
        invalid_persistence = entry.get("persistence_need") not in PERSISTENCE_NEEDS
        empty_evidence = not str(entry.get("evidence", "")).strip()
        if missing_fields or invalid_decision or invalid_persistence or empty_evidence:
            details: list[str] = []
            if missing_fields:
                details.append("missing=" + ",".join(missing_fields))
            if invalid_decision:
                details.append(f"decision={entry.get('decision')!r}")
            if invalid_persistence:
                details.append(f"persistence_need={entry.get('persistence_need')!r}")
            if empty_evidence:
                details.append("evidence is empty")
            malformed.append(f"{file_name}: " + "; ".join(details))

    semantic_issues = _semantic_issues(root, entries)

    errors: list[str] = []
    if missing_paths:
        errors.append("missing inventory entries: " + ", ".join(missing_paths))
    if stale_paths:
        errors.append("stale inventory entries: " + ", ".join(stale_paths))
    if duplicate_paths:
        errors.append("duplicate inventory entries: " + ", ".join(duplicate_paths))
    errors.extend(malformed)
    errors.extend(semantic_issues)
    result = {
        "inventory": (
            inventory_path.relative_to(root).as_posix()
            if inventory_path.is_relative_to(root)
            else str(inventory_path)
        ),
        "discovered_files": len(discovered),
        "inventory_entries": len(entries),
        "missing": missing_paths,
        "stale": stale_paths,
        "duplicates": duplicate_paths,
        "malformed": malformed,
        "semantic_issues": semantic_issues,
        "valid": not errors,
    }
    if errors:
        raise InventoryValidationError("; ".join(errors))
    return result


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--inventory",
        type=Path,
        default=Path("backend/tests/unit/test_inventory.json"),
    )
    parser.add_argument("--json", action="store_true", help="emit the validation result as JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    root = args.root.resolve()
    inventory_path = args.inventory
    if not inventory_path.is_absolute():
        inventory_path = root / inventory_path
    try:
        result = validate_inventory(root, inventory_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        if args.json:
            print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True))
        else:
            print(f"backend unit inventory invalid: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            f"backend unit inventory valid: {result['inventory_entries']} entries "
            f"for {result['discovered_files']} discovered files"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

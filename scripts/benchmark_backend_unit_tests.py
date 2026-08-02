#!/usr/bin/env python3
"""Summarize a pytest JUnit report for the backend unit-test audit.

The command intentionally has no pytest-specific reporting dependency.  Pytest
emits the JUnit XML, while this small parser produces deterministic JSON and
Markdown suitable for CI artifacts and the versioned audit document.

Example (after the consolidated runner finishes)::

    python scripts/benchmark_backend_unit_tests.py \
      --junit-xml artifacts/backend-unit.junit.xml \
      --pytest-log artifacts/backend-unit.pytest.log \
      --output artifacts/backend-unit-timing.json \
      --markdown-output artifacts/backend-unit-timing.md
"""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import re
import subprocess
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

_WARNING_TOTAL_RE = re.compile(r"(?P<count>\d+)\s+warnings?\s+in\s+", re.IGNORECASE)
_SKIP_TOTAL_RE = re.compile(r"(?P<count>\d+)\s+skips?\s+in\s+", re.IGNORECASE)


def _float(value: str | None) -> float:
    try:
        return max(0.0, float(value or 0.0))
    except (TypeError, ValueError):
        return 0.0


def _nearest_rank(values: Iterable[float], percentile: float) -> float:
    ordered = sorted(float(value) for value in values)
    if not ordered:
        return 0.0
    rank = max(1, math.ceil(percentile * len(ordered)))
    return ordered[rank - 1]


def _testcase_file(testcase: ET.Element) -> str:
    file_name = (testcase.attrib.get("file") or "").strip()
    if file_name:
        return file_name.replace("\\", "/")
    classname = (testcase.attrib.get("classname") or "unknown").strip()
    # JUnit producers differ on whether ``classname`` is a Python module,
    # dotted node id, or a free-form suite name.  Pytest's default xunit2
    # output omits ``file`` but uses a dotted module classname; recover the
    # real test path for that common shape.
    if classname.startswith("backend.tests.unit."):
        return classname.replace(".", "/") + ".py"
    # Keep other fallbacks stable and recognizable rather than pretending they
    # map to a source file.
    return f"<junit:{classname}>"


def parse_junit_report(path: Path) -> dict[str, Any]:
    """Parse pytest's JUnit XML into deterministic timing primitives."""

    root = ET.parse(path).getroot()
    testcases = list(root.iter("testcase"))
    per_file: dict[str, float] = defaultdict(float)
    case_durations: list[float] = []
    skipped = 0
    failures = 0
    errors = 0

    for testcase in testcases:
        duration = _float(testcase.attrib.get("time"))
        file_name = _testcase_file(testcase)
        per_file[file_name] += duration
        case_durations.append(duration)
        skipped += int(testcase.find("skipped") is not None)
        failures += int(testcase.find("failure") is not None)
        errors += int(testcase.find("error") is not None)

    suites = list(root.iter("testsuite"))
    suite_times = [_float(suite.attrib.get("time")) for suite in suites]
    total_duration = _float(root.attrib.get("time"))
    if total_duration <= 0.0:
        total_duration = sum(suite_times)
    if total_duration <= 0.0:
        total_duration = sum(case_durations)

    return {
        "collected_cases": len(testcases),
        "total_duration_seconds": round(total_duration, 6),
        "case_duration_p95_seconds": round(_nearest_rank(case_durations, 0.95), 6),
        "file_duration_p95_seconds": round(_nearest_rank(per_file.values(), 0.95), 6),
        "per_file_seconds": {
            file_name: round(duration, 6) for file_name, duration in sorted(per_file.items())
        },
        "slowest_files": [
            {"file": file_name, "seconds": round(duration, 6)}
            for file_name, duration in sorted(
                per_file.items(), key=lambda item: (-item[1], item[0])
            )[:10]
        ],
        "skips": skipped,
        "failures": failures,
        "errors": errors,
    }


def _log_total(path: Path | None, pattern: re.Pattern[str]) -> int | None:
    if path is None or not path.exists():
        return None
    content = path.read_text(encoding="utf-8", errors="replace")
    matches = list(pattern.finditer(content))
    if not matches:
        return None
    return int(matches[-1].group("count"))


def _revision() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return os.getenv("GITHUB_SHA", "unknown")


def build_summary(
    junit_xml: Path,
    *,
    pytest_log: Path | None = None,
    revision: str | None = None,
    environment: str | None = None,
    started_at: float | None = None,
    finished_at: float | None = None,
) -> dict[str, Any]:
    report = parse_junit_report(junit_xml)
    warning_total = _log_total(pytest_log, _WARNING_TOTAL_RE)
    skip_total = _log_total(pytest_log, _SKIP_TOTAL_RE)
    if warning_total is None:
        warning_total = 0
    if skip_total is not None:
        # JUnit is the source of truth for per-case skips; the log count is a
        # useful cross-check and may include collection-level skips.
        report["log_skips"] = skip_total

    if started_at is not None and finished_at is not None:
        wall_duration = max(0.0, finished_at - started_at)
    else:
        wall_duration = report["total_duration_seconds"]

    database_url = os.getenv("DATABASE_URL", "")
    database_backend = database_url.split(":", 1)[0] if ":" in database_url else "unknown"
    report.update(
        {
            "schema_version": 1,
            "revision": revision or _revision(),
            "environment": environment or os.getenv("CI", "local"),
            "python": platform.python_version(),
            "platform": platform.platform(aliased=True),
            "database_backend": database_backend or "unknown",
            "warnings": warning_total,
            "wall_duration_seconds": round(wall_duration, 6),
            "source_junit_xml": str(junit_xml),
            "source_pytest_log": str(pytest_log) if pytest_log else None,
        }
    )
    return report


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Backend unit-test timing",
        "",
        f"- Revision: `{summary['revision']}`",
        f"- Environment: `{summary['environment']}`",
        f"- Database backend: `{summary['database_backend']}`",
        f"- Collected cases: **{summary['collected_cases']}**",
        f"- Total JUnit duration: **{summary['total_duration_seconds']:.3f}s**",
        f"- Wall duration: **{summary['wall_duration_seconds']:.3f}s**",
        f"- File-duration p95: **{summary['file_duration_p95_seconds']:.3f}s**",
        f"- Skips: **{summary['skips']}**",
        f"- Warnings: **{summary['warnings']}**",
        "",
        "## Ten slowest files",
        "",
        "| File | Seconds |",
        "| --- | ---: |",
    ]
    lines.extend(
        f"| `{item['file']}` | {item['seconds']:.3f} |" for item in summary["slowest_files"]
    )
    lines.append("")
    return "\n".join(lines)


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--junit-xml", type=Path, required=True)
    parser.add_argument("--pytest-log", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--revision")
    parser.add_argument("--environment")
    parser.add_argument("--started-at", type=float)
    parser.add_argument("--finished-at", type=float)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    if not args.junit_xml.exists():
        raise SystemExit(f"JUnit report not found: {args.junit_xml}")
    summary = build_summary(
        args.junit_xml,
        pytest_log=args.pytest_log,
        revision=args.revision,
        environment=args.environment,
        started_at=args.started_at,
        finished_at=args.finished_at,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(render_markdown(summary), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

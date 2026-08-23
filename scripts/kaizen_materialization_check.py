#!/usr/bin/env python3
"""Validate Kaizen materialization evidence in docs/kaizen-log.md (card #661).

Exit 0 on PASS (prints one success line to stdout).
Exit 1 on FAIL (prints blocker lines to stdout, one per issue).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from typing import Iterable

TERMINAL_STATUSES = frozenset({"Pronto", "Cancelado"})
HEADING_RE = re.compile(
    r"^##\s+(\d{4}-\d{2}-\d{2})[^#\n]*(?:Kaizen release|/kaizen release)",
    re.IGNORECASE,
)
TABLE_HEADING_RE = re.compile(r"^###\s+Cards kaizen criados\b", re.IGNORECASE)
CREATED_RE = re.compile(r"^\s*#(\d+)\b")
NAO_CRIADO_RE = re.compile(r"\(\s*não\s+criado\s*\)", re.IGNORECASE)
COBERTO_POR_RE = re.compile(r"coberto\s+por\b(.*)$", re.IGNORECASE)
HASH_RE = re.compile(r"#(\d+)\b")
NO_ACTIONABLE_RE = re.compile(r"Sem\s+achados\s+acion[aá]veis", re.IGNORECASE)
SEP_RE = re.compile(r"^\|\s*[-:]+")


def _cells(line: str) -> list[str]:
    raw = line.strip()
    if not raw.startswith("|"):
        return []
    parts = [p.strip() for p in raw.strip("|").split("|")]
    return parts


def _is_separator(line: str) -> bool:
    return bool(SEP_RE.match(line.strip()))


def _section_bodies(text: str, release_date: str) -> list[str]:
    lines = text.splitlines()
    bodies: list[str] = []
    i = 0
    while i < len(lines):
        m = HEADING_RE.match(lines[i])
        if m and m.group(1) == release_date:
            i += 1
            chunk: list[str] = []
            while i < len(lines) and not lines[i].startswith("## "):
                chunk.append(lines[i])
                i += 1
            bodies.append("\n".join(chunk))
            continue
        i += 1
    return bodies


def _table_rows(section: str) -> list[str]:
    lines = section.splitlines()
    rows: list[str] = []
    i = 0
    while i < len(lines):
        if TABLE_HEADING_RE.match(lines[i].strip()):
            i += 1
            while i < len(lines) and not lines[i].startswith("###") and not lines[i].startswith("## "):
                line = lines[i]
                if line.strip().startswith("|") and not _is_separator(line):
                    cells = _cells(line)
                    # skip header row (Card | Prioridade | ...)
                    if cells and cells[0].lower() == "card":
                        i += 1
                        continue
                    if cells:
                        rows.append(line)
                i += 1
            continue
        i += 1
    return rows


def _board_status(board: dict | None, number: int) -> str | None:
    if board is None:
        return None
    for item in board.get("items") or []:
        content = item.get("content") or {}
        if content.get("number") != number:
            continue
        if (content.get("repository") or "") != "oalansilva/crypto":
            continue
        status = item.get("status")
        if isinstance(status, str) and status.strip():
            return status.strip()
    return None


def evaluate(
    log_text: str,
    release_date: str,
    *,
    board_state: str,
    board: dict | None,
) -> tuple[bool, list[str], str]:
    """Return (ok, blocker_messages, success_message)."""
    bodies = _section_bodies(log_text, release_date)
    if not bodies:
        return False, [
            f"kaizen-log has no canonical Kaizen release entry for {release_date}"
        ], ""

    union_body = "\n".join(bodies)
    rows: list[str] = []
    for body in bodies:
        rows.extend(_table_rows(body))

    created: set[int] = set()
    dedupe_ids: set[int] = set()
    invalid_rows: list[str] = []

    for row in rows:
        cells = _cells(row)
        first = cells[0] if cells else ""
        created_m = CREATED_RE.match(first)
        if created_m:
            created.add(int(created_m.group(1)))
            continue
        if NAO_CRIADO_RE.search(first) or NAO_CRIADO_RE.search(row):
            cob = COBERTO_POR_RE.search(row)
            if not cob:
                invalid_rows.append(row.strip())
                continue
            ids = [int(x) for x in HASH_RE.findall(cob.group(1))]
            if not ids:
                invalid_rows.append(row.strip())
                continue
            dedupe_ids.update(ids)
            continue
        # data row that is neither created nor valid dedupe
        invalid_rows.append(row.strip())

    blockers: list[str] = []

    if invalid_rows:
        blockers.append(
            "kaizen materialization: invalid Cards kaizen criados row(s) "
            "(require '#N …' or '(não criado) … coberto por #N'): "
            + " | ".join(invalid_rows[:3])
        )

    needs_board = bool(dedupe_ids)
    if needs_board and board_state != "ok":
        blockers.append(
            "kaizen materialization: board snapshot unavailable (fail-closed) "
            "while dedupe coverage check is required"
        )
    else:
        for num in sorted(dedupe_ids):
            status = _board_status(board, num)
            if status is None:
                blockers.append(
                    f"kaizen materialization: coverage #{num} absent on Project 1 board"
                )
            elif status in TERMINAL_STATUSES:
                blockers.append(
                    f"kaizen materialization: coverage #{num} has terminal Status={status} "
                    "(dedupe requires in-flow card, not Pronto/Cancelado)"
                )

    created_count = len(created)
    if created_count > 3:
        blockers.append(
            f"kaizen materialization: {created_count} distinct created cards for {release_date} "
            "(max 3/release)"
        )

    if blockers:
        return False, blockers, ""

    no_actionable = bool(NO_ACTIONABLE_RE.search(union_body))
    if created_count >= 1:
        return (
            True,
            [],
            f"Kaizen materialization OK for {release_date}: {created_count} created card(s).",
        )
    if dedupe_ids:
        return (
            True,
            [],
            f"Kaizen materialization OK for {release_date}: 0 created; "
            f"dedupe coverage in flow ({', '.join(f'#{n}' for n in sorted(dedupe_ids))}).",
        )
    if no_actionable and not rows:
        return (
            True,
            [],
            f"Kaizen materialization OK for {release_date}: Sem achados acionáveis.",
        )
    return (
        False,
        [
            f"kaizen materialization missing for {release_date}: need 1–3 created cards, "
            "valid '(não criado) coberto por #N' with in-flow coverage, "
            "or marker 'Sem achados acionáveis' with no data rows"
        ],
        "",
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log_path")
    parser.add_argument("release_date")
    parser.add_argument(
        "--board-state",
        default=os.environ.get("BOARD_STATE", "unloaded"),
    )
    parser.add_argument(
        "--board-json",
        default="",
        help="Project board snapshot JSON (prefer --board-json-file; env BOARD_JSON is not used)",
    )
    parser.add_argument(
        "--board-json-file",
        default=os.environ.get("BOARD_JSON_FILE", ""),
        help="Path to Project board snapshot JSON (avoids ARG_MAX vs env/argv)",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        text = open(args.log_path, encoding="utf-8").read()
    except OSError as exc:
        print(f"kaizen-log unreadable: {exc}")
        return 1

    board = None
    raw_json = args.board_json
    if args.board_json_file.strip():
        try:
            raw_json = open(args.board_json_file, encoding="utf-8").read()
        except OSError as exc:
            print(f"kaizen materialization: board JSON file unreadable: {exc}")
            return 1
    if raw_json.strip():
        try:
            board = json.loads(raw_json)
        except json.JSONDecodeError:
            print("kaizen materialization: BOARD_JSON is not valid JSON")
            return 1

    ok, blockers, success = evaluate(
        text,
        args.release_date,
        board_state=args.board_state,
        board=board,
    )
    if ok:
        print(success)
        return 0
    for msg in blockers:
        print(msg)
    return 1


if __name__ == "__main__":
    sys.exit(main())

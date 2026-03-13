#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REQ_RE = re.compile(r"^###\s*Requirement:\s*(.+?)\s*$")
SCENARIO_RE = re.compile(r"^####\s*Scenario:\s*(.+?)\s*$")
SECTION_RE = re.compile(r"^##\s+(ADDED|MODIFIED|REMOVED|RENAMED) Requirements\s*$")
RENAMED_LINE_RE = re.compile(r"^\s*-\s*(FROM|TO):\s*`?###\s*Requirement:\s*(.+?)`?\s*$")
TOKEN_RE = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "the", "a", "an", "and", "or", "to", "of", "from", "for", "must", "include", "system",
    "kanban", "column", "columns", "requirement", "board", "provide", "support", "derive", "status",
}


@dataclass
class RequirementBlock:
    name: str
    lines: list[str]

    @property
    def text(self) -> str:
        return "\n".join(self.lines)

    @property
    def scenarios(self) -> set[str]:
        out: set[str] = set()
        for line in self.lines:
            m = SCENARIO_RE.match(line)
            if m:
                out.add(m.group(1).strip().lower())
        return out

    @property
    def body_tokens(self) -> set[str]:
        tokens: set[str] = set()
        for line in self.lines[1:]:
            for token in TOKEN_RE.findall(line.lower()):
                if token not in STOPWORDS:
                    tokens.add(token)
        return tokens


def split_sections(lines: list[str]) -> list[tuple[str | None, list[str]]]:
    sections: list[tuple[str | None, list[str]]] = []
    current_name: str | None = None
    current_lines: list[str] = []
    for line in lines:
        m = SECTION_RE.match(line)
        if m:
            sections.append((current_name, current_lines))
            current_name = m.group(1)
            current_lines = [line]
        else:
            current_lines.append(line)
    sections.append((current_name, current_lines))
    return sections


def parse_requirement_blocks(lines: list[str]) -> list[RequirementBlock]:
    blocks: list[RequirementBlock] = []
    current_name: str | None = None
    current_lines: list[str] = []
    for line in lines:
        m = REQ_RE.match(line)
        if m:
            if current_name is not None:
                blocks.append(RequirementBlock(current_name, current_lines))
            current_name = m.group(1).strip()
            current_lines = [line]
        elif current_name is not None:
            current_lines.append(line)
    if current_name is not None:
        blocks.append(RequirementBlock(current_name, current_lines))
    return blocks


def parse_canonical_requirements(spec_path: Path) -> dict[str, RequirementBlock]:
    lines = spec_path.read_text(encoding="utf-8").splitlines()
    return {block.name: block for block in parse_requirement_blocks(lines)}


def score_candidate(mod_block: RequirementBlock, target_block: RequirementBlock) -> tuple[int, int, int]:
    scenario_overlap = len(mod_block.scenarios & target_block.scenarios)
    token_overlap = len(mod_block.body_tokens & target_block.body_tokens)
    title_overlap = len((set(TOKEN_RE.findall(mod_block.name.lower())) - STOPWORDS) & (set(TOKEN_RE.findall(target_block.name.lower())) - STOPWORDS))
    return (scenario_overlap, token_overlap, title_overlap)


def choose_target(mod_block: RequirementBlock, canonical: dict[str, RequirementBlock]) -> str | None:
    scored: list[tuple[tuple[int, int, int], str]] = []
    for name, target in canonical.items():
        score = score_candidate(mod_block, target)
        scenario_overlap, token_overlap, title_overlap = score
        if scenario_overlap <= 0:
            continue
        if token_overlap <= 0 and title_overlap <= 0:
            continue
        scored.append((score, name))
    if not scored:
        return None
    scored.sort(reverse=True)
    best_score, best_name = scored[0]
    tied = [name for score, name in scored if score == best_score]
    if len(tied) != 1:
        raise RuntimeError(
            f"Ambiguous canonical requirement match for '{mod_block.name}': candidates={tied} score={best_score}"
        )
    return best_name


def reconcile_file(change_spec_path: Path, canonical_spec_path: Path) -> list[tuple[str, str]]:
    lines = change_spec_path.read_text(encoding="utf-8").splitlines()
    sections = split_sections(lines)
    canonical = parse_canonical_requirements(canonical_spec_path)
    retargeted: list[tuple[str, str]] = []
    out_sections: list[list[str]] = []

    for section_name, section_lines in sections:
        if section_name == "RENAMED":
            # Drop stale rename metadata during archive reconciliation.
            # Archive must target the canonical header that exists *now*.
            continue
        if section_name != "MODIFIED":
            out_sections.append(section_lines)
            continue

        rebuilt: list[str] = []
        i = 0
        while i < len(section_lines):
            line = section_lines[i]
            m = REQ_RE.match(line)
            if not m:
                rebuilt.append(line)
                i += 1
                continue

            start = i
            i += 1
            while i < len(section_lines) and not REQ_RE.match(section_lines[i]):
                i += 1
            block_lines = section_lines[start:i]
            block = RequirementBlock(m.group(1).strip(), block_lines)
            if block.name in canonical:
                rebuilt.extend(block_lines)
                continue

            target_name = choose_target(block, canonical)
            if target_name is None:
                rebuilt.extend(block_lines)
                continue

            new_block_lines = block_lines[:]
            new_block_lines[0] = f"### Requirement: {target_name}"
            rebuilt.extend(new_block_lines)
            retargeted.append((block.name, target_name))

        out_sections.append(rebuilt)

    if not retargeted:
        return []

    merged_lines: list[str] = []
    for section in out_sections:
        merged_lines.extend(section)

    change_spec_path.write_text("\n".join(merged_lines).rstrip() + "\n", encoding="utf-8")
    return retargeted


def iter_change_spec_files(change_dir: Path) -> Iterable[tuple[Path, Path]]:
    specs_root = change_dir / "specs"
    if not specs_root.is_dir():
        return []
    pairs: list[tuple[Path, Path]] = []
    for spec_file in specs_root.glob("*/spec.md"):
        spec_name = spec_file.parent.name
        canonical = change_dir.parent.parent / "specs" / spec_name / "spec.md"
        if canonical.is_file():
            pairs.append((spec_file, canonical))
    return pairs


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("change_id")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent
    change_dir = repo_root / "openspec" / "changes" / args.change_id
    if not change_dir.is_dir():
        raise SystemExit(f"change not found: {change_dir}")

    any_changes = False
    for change_spec, canonical_spec in iter_change_spec_files(change_dir):
        renames = reconcile_file(change_spec, canonical_spec)
        if renames:
            any_changes = True
            for old, new in renames:
                print(f"reconciled {change_spec.relative_to(repo_root)}: '{old}' -> '{new}'")
    if not any_changes:
        print(f"no header reconciliation needed for {args.change_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

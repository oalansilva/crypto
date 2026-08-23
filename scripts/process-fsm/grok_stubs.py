"""Generate and check Grok skill stubs that point at .cursor/skills (not a second runbook)."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
CURSOR_SKILLS = REPO_ROOT / ".cursor" / "skills"
GROK_SKILLS = REPO_ROOT / ".grok" / "skills"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)


def _description_raw(text: str) -> str:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return '"Delegate to the canonical SKILL.md"'
    block = match.group(1)
    found = re.search(r"^description:\s*(.*)$", block, re.MULTILINE)
    if not found:
        return '"Delegate to the canonical SKILL.md"'
    return found.group(1).strip()


def stub_body(name: str) -> str:
    return (
        f"# {name}\n"
        "\n"
        f"Cliente: Grok Build. MUST Read `.cursor/skills/{name}/SKILL.md` and follow it as the runbook.\n"
        "Map Cursor Task `inherit` to `spawn_subagent` inherit. Do not copy the runbook here.\n"
    )


def render_stub(name: str, description_raw: str) -> str:
    return f"---\nname: {name}\ndescription: {description_raw}\n---\n\n{stub_body(name)}"


def canonical_skills() -> list[Path]:
    return sorted(path for path in CURSOR_SKILLS.glob("*/SKILL.md") if path.is_file())


def expected_stubs() -> dict[str, str]:
    out: dict[str, str] = {}
    for skill_md in canonical_skills():
        name = skill_md.parent.name
        text = skill_md.read_text(encoding="utf-8")
        out[name] = render_stub(name, _description_raw(text))
    return out


def write_stubs() -> None:
    for name, content in expected_stubs().items():
        dest = GROK_SKILLS / name / "SKILL.md"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")


def stub_errors() -> list[str]:
    errors: list[str] = []
    expected = expected_stubs()
    for name, content in expected.items():
        dest = GROK_SKILLS / name / "SKILL.md"
        if not dest.is_file():
            errors.append(f"missing {dest.relative_to(REPO_ROOT)}")
            continue
        actual = dest.read_text(encoding="utf-8")
        if actual != content:
            errors.append(f"stale {dest.relative_to(REPO_ROOT)}")
        nonempty = [ln for ln in actual.splitlines() if ln.strip()]
        try:
            body = actual.split("---", 2)[2]
        except IndexError:
            body = actual
        body_lines = [ln for ln in body.splitlines() if ln.strip()]
        if len(body_lines) > 8:
            errors.append(f"body too long {dest.relative_to(REPO_ROOT)}")
        if f".cursor/skills/{name}/SKILL.md" not in actual:
            errors.append(f"missing pointer {dest.relative_to(REPO_ROOT)}")
        if "Em Refinamento → Todo → Design" in actual:
            errors.append(f"runbook copy {dest.relative_to(REPO_ROOT)}")
        del nonempty
    return errors


if __name__ == "__main__":
    write_stubs()
    problems = stub_errors()
    if problems:
        raise SystemExit("\n".join(problems))

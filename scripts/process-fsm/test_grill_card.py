from __future__ import annotations

import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fsm import load_fsm  # noqa: E402
from paging import page  # noqa: E402

TODO_STUB = "Próximo evento = iniciar_design. Não apply. Não /opsx:new ainda."
GRILL_CARD = REPO / ".cursor" / "skills" / "grill-card" / "SKILL.md"
GRILLING = REPO / ".cursor" / "skills" / "grilling" / "SKILL.md"
HERMES = Path("/srv/knowledge/hermes-second-brain/skills")
CODEX = Path.home() / ".codex" / "skills"
DOD_NEEDLES = (
    "CONTEXT.md",
    "docs/adr",
    "process_event priorizar",
    "/opsx:",
    "disable-model-invocation: false",
    "grill-card: fronteira vazia; história no body; à espera de T1 (Alan).",
)


def _regular_skill(path: Path) -> None:
    assert path.is_file(), path
    assert not path.is_symlink(), path
    assert not stat.S_ISLNK(path.stat().st_mode), path


def _resolve(bound: str, git: str) -> object:
    def inner(cwd, path, issue_id=None, status=None):
        return {"q": None, "bound_card": bound, "q_git": git}

    return inner


def _provider(status: str | None):
    def inner(bound: str | None) -> str | None:
        assert bound == "613"
        return status

    return inner


def test_grill_skills_are_regular_files() -> None:
    _regular_skill(GRILL_CARD)
    _regular_skill(GRILLING)
    skills = REPO / ".cursor" / "skills"
    assert not (skills / "grill-with-docs").exists()


def test_grill_card_text_has_prohibitions() -> None:
    text = GRILL_CARD.read_text(encoding="utf-8")
    for needle in DOD_NEEDLES:
        assert needle in text, needle
    assert "bound_card" in text
    assert "Em Refinamento" in text
    assert "Não exige branch `card-<id>-*`" in text
    assert "sessão bound a `card-<id>-*`" not in text


def test_grill_skills_not_dual_written() -> None:
    for name in ("grill-card", "grilling"):
        assert not (HERMES / name).exists()
        assert not (CODEX / name).exists()


def test_em_refinamento_stub_names_grill() -> None:
    fsm = load_fsm()
    stub = str(fsm["context_file"]["Em Refinamento"])
    assert "grill-card" in stub
    assert "T1" in stub
    assert "CONTEXT.md" in stub
    todo = str(fsm["context_file"]["Todo"])
    assert TODO_STUB in todo
    design = str(fsm["context_file"]["Design"])
    assert "sintetizar" in design
    assert "reentrevistar" in design
    tools = fsm["enabled_tools"]["Em Refinamento"]
    assert list(tools) == ["issue_edit", "comment"]
    assert "write_openspec" not in tools
    transitions = {row["id"]: row for row in fsm["transitions"]}
    assert transitions["T0"]["to"] == "Em Refinamento"
    assert transitions["T1"]["actor"] == "Alan"
    assert transitions["T1"]["from"] == "Em Refinamento"
    assert transitions["T1"]["to"] == "Todo"


def test_em_refinamento_page_stays_short() -> None:
    result = page(
        cwd=".",
        resolve_fn=_resolve("613", "card-613-process-fsm-paging"),
        status_provider=_provider("Em Refinamento"),
    )
    ctx = result["additional_context"]
    assert "grill-card" in ctx
    assert "Chat" in ctx
    assert len(ctx.splitlines()) <= 20

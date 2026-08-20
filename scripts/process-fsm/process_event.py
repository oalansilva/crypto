"""SMAG process_event: validate δ then move Project 1 Status. No GitHub in unit tests."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable, Protocol

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from board_status import STATUS_FIELD_ID, STATUS_OPTIONS  # noqa: E402
from fsm import (  # noqa: E402
    CARD_GIT_RE,
    EvalContext,
    enabled_events,
    evaluate,
    load_fsm,
)
from guard import github_status_provider  # noqa: E402
from resolve import UNBOUND, resolve  # noqa: E402

REPO_ROOT = ROOT.parents[1]
AMBIENTES = "alan-workflow-ambientes"
RELEASE_GUARD = "release-guard"
HUMAN_EVENTS = frozenset({"priorizar", "aprovar_design", "homologar", "fechar_release", "devolver_design", "cancelar"})
I4_EVENTS = frozenset({"iniciar_apply", "pedir_review", "invalidar_aprovacao"})
EVENT_GUARDS = {
    "achar_bloqueante": {"open_p0_p1": True, "reviewers_ok": False},
    "aceitar_sha": {"reviewers_ok": True, "open_p0_p1": False},
    "rerun_infra": {"flaky_infra": True, "source_failure": False, "checks_green": False},
    "falha_codigo": {"source_failure": True, "flaky_infra": False, "checks_green": False},
}


class BoardMover(Protocol):
    def set_status(self, issue_number: int, to: str) -> None: ...


class FakeMover:
    def __init__(self) -> None:
        self.calls: list[tuple[int, str]] = []

    def set_status(self, issue_number: int, to: str) -> None:
        self.calls.append((issue_number, to))


class GhBoardMover:
    """Live Project 1 Status edit. Tests MUST inject FakeMover instead."""

    def set_status(self, issue_number: int, to: str) -> None:
        import subprocess

        option = STATUS_OPTIONS.get(to)
        if option is None:
            raise ValueError(f"unknown Status {to!r}")
        item_id = _item_id_for_issue(issue_number)
        proc = subprocess.run(
            [
                "gh",
                "project",
                "item-edit",
                "--id",
                item_id,
                "--project-id",
                "PVT_kwHOAAHtBM4BV8b2",
                "--field-id",
                STATUS_FIELD_ID,
                "--single-select-option-id",
                option,
            ],
            capture_output=True,
            text=True,
            check=False,
            timeout=20,
        )
        if proc.returncode != 0:
            raise RuntimeError((proc.stderr or proc.stdout or "item-edit failed").strip())


def _item_id_for_issue(issue_number: int) -> str:
    import json as json_mod
    import subprocess

    query = (
        "query($n:Int!){repository(owner:\"oalansilva\",name:\"crypto\")"
        "{issue(number:$n){projectItems(first:20){nodes{id project{number owner{...on User{login}}}}}}}}"
    )
    proc = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={query}", "-F", f"n={issue_number}"],
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    if proc.returncode != 0:
        raise RuntimeError((proc.stderr or "graphql failed").strip())
    data = json_mod.loads(proc.stdout or "{}")
    nodes = (
        (((data.get("data") or {}).get("repository") or {}).get("issue") or {}).get("projectItems") or {}
    ).get("nodes") or []
    for node in nodes:
        project = (node or {}).get("project") or {}
        owner = (project.get("owner") or {}).get("login")
        if project.get("number") == 1 and owner in (None, "oalansilva"):
            item_id = node.get("id")
            if isinstance(item_id, str) and item_id:
                return item_id
    raise RuntimeError(f"issue {issue_number} not on Project 1")


def _unbound(bound: Any) -> bool:
    return bound in (None, "", UNBOUND)


def files_g_design(change_dir: Path) -> bool:
    needed = [change_dir / "proposal.md", change_dir / "design.md", change_dir / "tasks.md"]
    if not all(path.is_file() for path in needed):
        return False
    specs = change_dir / "specs"
    return bool(specs.is_dir() and any(specs.rglob("*.md")))


def compute_digest(change_dir: Path, prototype_dir: Path | None) -> str:
    digest = hashlib.sha256()
    design = change_dir / "design.md"
    if design.is_file():
        digest.update(design.read_bytes())
    if prototype_dir is not None and prototype_dir.is_dir():
        for path in sorted(p for p in prototype_dir.rglob("*") if p.is_file()):
            digest.update(path.relative_to(prototype_dir).as_posix().encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()


def sidecar_path(change_dir: Path) -> Path:
    return change_dir / ".design-digest"


def measure_digest_changed(change_dir: Path | None, prototype_dir: Path | None, state: str | None) -> bool:
    if change_dir is None:
        return state in {"Pronto para Dev", "Em desenvolvimento"}
    sidecar = sidecar_path(change_dir)
    if not sidecar.is_file():
        return True
    current = compute_digest(change_dir, prototype_dir)
    stored = sidecar.read_text(encoding="utf-8").strip()
    return current != stored


def write_sidecar(change_dir: Path, prototype_dir: Path | None) -> None:
    sidecar_path(change_dir).write_text(
        compute_digest(change_dir, prototype_dir) + "\n",
        encoding="utf-8",
    )


def _payload(
    *,
    result: str,
    state: str | None,
    to: str | None,
    reason: str | None,
    enabled: list[str] | None = None,
    message: str | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {"result": result, "state": state, "to": to, "reason": reason}
    if enabled is not None:
        out["enabled_events"] = enabled
    if message:
        out["message"] = message
    return out


def _fechar_message(base: str | None) -> str:
    text = base or "reject"
    if AMBIENTES not in text:
        text = f"{text}; see {AMBIENTES} and {RELEASE_GUARD}"
    elif RELEASE_GUARD not in text:
        text = f"{text}; {RELEASE_GUARD}"
    return text


def process_event(
    event: str,
    *,
    cwd: Path | None = None,
    card: str | int | None = None,
    change: str | None = None,
    dry_run: bool = False,
    mover: BoardMover | None = None,
    status: str | None = None,
    q_git: str | None = None,
    bound_card: str | None = None,
    digest_changed: bool | None = None,
    g_design: bool | None = None,
    m_lote: bool | None = None,
    checks_green: bool | None = None,
    fsm: dict[str, Any] | None = None,
    resolve_fn: Callable[..., dict[str, str | None]] = resolve,
    change_dir: Path | None = None,
    prototype_dir: Path | None = None,
) -> dict[str, Any]:
    if event == "criar_card":
        return _payload(
            result="reject",
            state=status,
            to=None,
            reason="not_implemented",
            message="criar_card is out of scope for process_event; create the issue/card first.",
        )
    table = fsm if fsm is not None else load_fsm()
    workdir = Path(cwd) if cwd is not None else Path.cwd()
    resolved = resolve_fn(workdir, workdir, issue_id=card, status=status)
    q = status if status is not None else resolved.get("q")
    git = q_git if q_git is not None else resolved.get("q_git")
    bound = bound_card if bound_card is not None else resolved.get("bound_card")
    if q is None:
        q = github_status_provider(None if _unbound(bound) else str(bound))
    match = CARD_GIT_RE.match(str(git or ""))
    if card is not None and match is not None and str(card) != match.group(1):
        return _payload(result="reject", state=q, to=None, reason="card_mismatch")
    if event != "criar_card" and _unbound(bound):
        return _payload(result="reject", state=q, to=None, reason="unbound")

    issue_number: int | None = None
    try:
        issue_number = int(str(bound if bound not in (None, UNBOUND) else card))
    except (TypeError, ValueError):
        issue_number = None

    inferred_change = change
    if inferred_change is None and match is not None:
        inferred_change = str(git)
    resolved_change_dir = change_dir
    if resolved_change_dir is None and inferred_change:
        candidate = REPO_ROOT / "openspec" / "changes" / inferred_change
        if candidate.is_dir():
            resolved_change_dir = candidate
    resolved_proto = prototype_dir
    if resolved_proto is None and inferred_change:
        proto = REPO_ROOT / "frontend" / "public" / "prototypes" / inferred_change
        resolved_proto = proto if proto.is_dir() else None

    if g_design is None:
        g_design = files_g_design(resolved_change_dir) if resolved_change_dir else False
    if digest_changed is None:
        digest_changed = measure_digest_changed(resolved_change_dir, resolved_proto, q)
    if m_lote is None:
        m_lote = False

    exclusive = EVENT_GUARDS.get(event, {})
    ctx_kwargs: dict[str, Any] = {
        "state": q,
        "event": event,
        "actor": "Agent",
        "q_git": git,
        "bound_card": bound if not _unbound(bound) else None,
        "g_design": g_design,
        "digest_changed": digest_changed,
        "m_lote": m_lote,
        "checks_green": checks_green,
        "open_p0_p1": exclusive.get("open_p0_p1"),
        "reviewers_ok": exclusive.get("reviewers_ok"),
        "flaky_infra": exclusive.get("flaky_infra"),
        "source_failure": exclusive.get("source_failure"),
    }
    ctx_kwargs.update(exclusive)

    if event in I4_EVENTS and digest_changed is True:
        compiled = evaluate(
            table,
            EvalContext(
                state=q,
                event="invalidar_aprovacao",
                actor="Guard",
                q_git=git,
                bound_card=bound if not _unbound(bound) else None,
                digest_changed=True,
            ),
        )
        if compiled.result == "transition":
            if not dry_run and mover is not None and issue_number is not None:
                mover.set_status(issue_number, compiled.to or "Design")
            return _payload(
                result="transition",
                state=q,
                to=compiled.to,
                reason="I4" if event != "invalidar_aprovacao" else compiled.reason,
            )
        return _payload(result="reject", state=q, to=None, reason=compiled.reason)

    result = evaluate(table, EvalContext(**ctx_kwargs))
    enabled = enabled_events(table, q)
    message = None
    if event == "fechar_release":
        message = _fechar_message(result.reason)
    if result.result != "transition":
        extra = enabled if event in {"request_implement", "pular_coluna", "Agent.aprovar_design"} or result.reason in {
            "illegal_event",
            "no_edge",
        } else None
        if event == "request_implement":
            extra = enabled
        return _payload(
            result="reject",
            state=q,
            to=None,
            reason=result.reason,
            enabled=extra,
            message=message,
        )
    if dry_run or mover is None or issue_number is None:
        return _payload(result="transition", state=q, to=result.to, reason=result.reason, message=message)
    mover.set_status(issue_number, result.to or "")
    if event == "submeter_design" and resolved_change_dir is not None:
        write_sidecar(resolved_change_dir, resolved_proto)
    return _payload(result="transition", state=q, to=result.to, reason=result.reason, message=message)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="process_event")
    parser.add_argument("event")
    parser.add_argument("--card")
    parser.add_argument("--change")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    payload = process_event(
        args.event,
        card=args.card,
        change=args.change,
        dry_run=args.dry_run,
        mover=None if args.dry_run else GhBoardMover(),
    )
    json.dump(payload, sys.stdout, ensure_ascii=True)
    sys.stdout.write("\n")
    return 0 if payload.get("result") == "transition" else 1


if __name__ == "__main__":
    raise SystemExit(main())

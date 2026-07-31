from __future__ import annotations

import hashlib
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.workflow_models import (
    ApprovalScope,
    ApprovalState,
    Change,
    WorkItem,
    WorkItemState,
    WorkItemType,
    WorkflowApproval,
)
from app.services.upstream_guard import (
    UpstreamGuardError,
    current_commit_sha,
    require_card_main_publication,
)

if TYPE_CHECKING:
    from app.services.workflow_auth import WorkflowActor


KANBAN_COLUMNS = [
    "Todo",
    "Design",
    "Aprovação de Design",
    "Pronto para Dev",
    "Em desenvolvimento",
    "Code Review",
    "QA",
    "Done",
    "Homologado",
    "Pronto",
    "Cancelado",
]

LEGACY_STATUS_ALIASES = {
    "Pending": "Todo",
    "PO": "Todo",
    "DESIGN": "Design",
    "Approval": "Aprovação de Design",
    "Aprovacao de Design": "Aprovação de Design",
    "DEV": "Em desenvolvimento",
    "In Progress": "Em desenvolvimento",
    "in_progress": "Em desenvolvimento",
    "Homologation": "Done",
    "Alan homologation": "Done",
    # OpenSpec archival does not prove publication in main. Keep the card at
    # the last human-approved checkpoint until release evidence moves it on.
    "Archived": "Homologado",
    "archived": "Homologado",
    "Canceled": "Cancelado",
    "canceled": "Cancelado",
}

CANONICAL_STATUS_SET = frozenset(KANBAN_COLUMNS)
TERMINAL_STATUSES = frozenset({"Pronto", "Cancelado"})
NON_REGRESSING_STATUSES = frozenset({"Done", "Homologado", "Pronto"})

_FORWARD_TARGET = {
    "Todo": "Design",
    "Design": "Aprovação de Design",
    "Aprovação de Design": "Pronto para Dev",
    "Pronto para Dev": "Em desenvolvimento",
    "Em desenvolvimento": "Code Review",
    "Code Review": "QA",
    "QA": "Done",
    "Done": "Homologado",
    "Homologado": "Pronto",
}
_REWORK_TARGETS = {
    "Aprovação de Design": {"Design"},
    "Code Review": {"Em desenvolvimento"},
    "QA": {"Em desenvolvimento"},
}
_CANCELABLE_STATUSES = frozenset(KANBAN_COLUMNS[:7])
_DIGEST_RE = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class TransitionResult:
    previous_status: str
    status: str
    approval_created: bool = False
    approval_invalidated: bool = False


def canonicalize_status(status: str | None, *, allow_legacy: bool = False) -> str:
    value = (status or "").strip()
    if value in CANONICAL_STATUS_SET:
        return value
    if allow_legacy and value in LEGACY_STATUS_ALIASES:
        return LEGACY_STATUS_ALIASES[value]
    raise HTTPException(
        status_code=422,
        detail={
            "code": "unknown_workflow_status",
            "message": f"Unknown workflow status: {value or '<empty>'}",
            "status": value,
            "canonical_statuses": KANBAN_COLUMNS,
        },
    )


def allowed_targets(current_status: str) -> list[str]:
    current = canonicalize_status(current_status)
    if current in TERMINAL_STATUSES:
        return []
    targets: set[str] = set(_REWORK_TARGETS.get(current, set()))
    forward = _FORWARD_TARGET.get(current)
    if forward:
        targets.add(forward)
    if current in _CANCELABLE_STATUSES:
        targets.add("Cancelado")
    # Explicit non-UI bypass. Its evidence is validated separately.
    if current == "Todo":
        targets.add("Pronto para Dev")
    return [status for status in KANBAN_COLUMNS if status in targets]


def validate_kanban_transition(
    *, current_column: str | None, target_column: str | None
) -> tuple[str, str]:
    current = canonicalize_status(current_column)
    target = canonicalize_status(target_column)
    if current == target:
        return current, target
    targets = allowed_targets(current)
    if target not in targets:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "invalid_kanban_transition",
                "message": f"Cannot move card directly from {current} to {target}.",
                "current": current,
                "target": target,
                "allowed_targets": targets,
            },
        )
    return current, target


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_repo_file(repo_root: Path, reference: str) -> Path | None:
    value = (reference or "").strip()
    if not value or value.startswith(("http://", "https://")):
        return None
    candidate = Path(value)
    if not candidate.is_absolute():
        candidate = repo_root / candidate
    candidate = candidate.resolve()
    root = repo_root.resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail={"code": "invalid_design_reference", "message": "Evidence path is outside the repository."},
        ) from exc
    return candidate


def refresh_design_evidence(
    change: Change,
    repo_root: Path,
    *,
    record_delivery: bool = False,
) -> tuple[str, str]:
    design_ref = (change.design_ref or "").strip() or f"openspec/changes/{change.change_id}/design.md"
    design_path = _resolve_repo_file(repo_root, design_ref)
    if not design_path or not design_path.is_file():
        raise HTTPException(
            status_code=409,
            detail={
                "code": "incomplete_design_delivery",
                "message": "Design delivery is missing design.md.",
                "missing_items": ["design.md"],
            },
        )
    design_text = design_path.read_text(encoding="utf-8")
    missing_sections = []
    if not re.search(r"^##+\s+Prototype\s*$", design_text, flags=re.IGNORECASE | re.MULTILINE):
        missing_sections.append("Prototype section")
    if not re.search(r"^##+\s+Design Critique\s*$", design_text, flags=re.IGNORECASE | re.MULTILINE):
        missing_sections.append("Design Critique section")
    if missing_sections:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "incomplete_design_delivery",
                "message": "Design delivery is missing required sections.",
                "missing_items": missing_sections,
            },
        )

    prototype_ref = (change.prototype_ref or "").strip()
    if not prototype_ref:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "incomplete_design_delivery",
                "message": "Design delivery is missing versioned prototype evidence.",
                "missing_items": ["prototype_ref"],
            },
        )
    prototype_path = _resolve_repo_file(repo_root, prototype_ref)
    if prototype_path is not None:
        if not prototype_path.is_file():
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "incomplete_design_delivery",
                    "message": "Prototype evidence file does not exist.",
                    "missing_items": ["prototype_ref"],
                },
            )
        prototype_digest = _sha256_file(prototype_path)
    else:
        prototype_digest = (change.prototype_digest or "").strip().lower()
        if not _DIGEST_RE.fullmatch(prototype_digest):
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "incomplete_design_delivery",
                    "message": "Remote prototype evidence requires a SHA-256 digest.",
                    "missing_items": ["prototype_digest"],
                },
            )

    verdict = (change.design_critique_verdict or "").strip().upper()
    if verdict != "PASS":
        raise HTTPException(
            status_code=409,
            detail={
                "code": "incomplete_design_delivery",
                "message": "Designer Agent critique must have verdict PASS.",
                "missing_items": ["design_critique_verdict=PASS"],
            },
        )

    change.design_ref = design_ref
    change.design_digest = _sha256_file(design_path)
    change.prototype_digest = prototype_digest
    if record_delivery:
        change.design_delivered_at = datetime.now(timezone.utc)
    return change.design_digest, prototype_digest


def approval_matches_current_evidence(change: Change, repo_root: Path) -> bool:
    if not change.design_approval_valid:
        return False
    try:
        design_digest, prototype_digest = refresh_design_evidence(change, repo_root)
    except HTTPException:
        return False
    return bool(
        change.approved_design_digest == design_digest
        and change.approved_prototype_digest == prototype_digest
    )


def invalidate_design_approval(change: Change) -> bool:
    if not change.design_approval_valid:
        return False
    change.design_approval_valid = False
    return True


def _is_non_ui_bypass(change: Change) -> bool:
    return change.ui_impact == "none" and bool(
        (change.ui_impact_justification or "").strip()
    )


def _require_current_design_approval(
    change: Change,
    repo_root: Path,
    *,
    regress_on_obsolete: bool,
) -> None:
    if _is_non_ui_bypass(change):
        return
    if change.ui_impact == "affected" and approval_matches_current_evidence(change, repo_root):
        return
    invalidate_design_approval(change)
    if regress_on_obsolete:
        change.status = "Aprovação de Design"
    raise HTTPException(
        status_code=409,
        detail={
            "code": "design_approval_obsolete",
            "message": "Design evidence is missing, changed, or no longer approved for this stage.",
            "regressed_to": "Aprovação de Design" if regress_on_obsolete else None,
        },
    )


def _current_repo_sha(repo_root: Path) -> str:
    try:
        return current_commit_sha(repo_root)
    except UpstreamGuardError as exc:
        raise HTTPException(
            status_code=409,
            detail={"code": "qa_commit_unavailable", "message": str(exc)},
        ) from exc


def start_qa_round(db: Session, change: Change, repo_root: Path) -> None:
    qa_round_id = str(uuid.uuid4())
    commit_sha = _current_repo_sha(repo_root)
    started_at = datetime.now(timezone.utc)
    change.qa_round_id = qa_round_id
    change.qa_commit_sha = commit_sha
    change.qa_round_started_at = started_at
    change.qa_approved_round_id = None
    change.qa_approved_commit_sha = None
    change.qa_approved_at = None
    db.add(
        WorkflowApproval(
            scope=ApprovalScope.change,
            gate="QA",
            state=ApprovalState.pending,
            change_pk=change.id,
            work_item_id=None,
            actor="workflow",
            note=f"round={qa_round_id}; commit={commit_sha}; started_at={started_at.isoformat()}",
        )
    )


def invalidate_qa_round(db: Session, change: Change, *, actor: str, reason: str) -> bool:
    if not change.qa_round_id:
        return False
    db.add(
        WorkflowApproval(
            scope=ApprovalScope.change,
            gate="QA",
            state=ApprovalState.rejected,
            change_pk=change.id,
            work_item_id=None,
            actor=actor,
            note=(
                f"round={change.qa_round_id}; commit={change.qa_commit_sha or ''}; "
                f"invalidated={reason}"
            ),
        )
    )
    change.qa_round_id = None
    change.qa_commit_sha = None
    change.qa_round_started_at = None
    change.qa_approved_round_id = None
    change.qa_approved_commit_sha = None
    change.qa_approved_at = None
    return True


def approve_current_qa_round(
    db: Session,
    *,
    change: Change,
    actor: "WorkflowActor",
    round_id: str,
    commit_sha: str,
    note: str,
    repo_root: Path,
) -> WorkflowApproval:
    if canonicalize_status(change.status) != "QA":
        raise HTTPException(
            status_code=409,
            detail={"code": "qa_round_not_active", "message": "The card is not in QA."},
        )
    supplied_round = (round_id or "").strip()
    supplied_sha = (commit_sha or "").strip()
    if supplied_round != change.qa_round_id or supplied_sha != change.qa_commit_sha:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "qa_round_mismatch",
                "message": "QA approval does not match the active server-created round and commit.",
            },
        )
    current_sha = _current_repo_sha(repo_root)
    if current_sha != change.qa_commit_sha:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "qa_commit_obsolete",
                "message": "Repository HEAD changed after this QA round started.",
                "round_commit": change.qa_commit_sha,
                "current_commit": current_sha,
            },
        )
    approved_at = datetime.now(timezone.utc)
    change.qa_approved_round_id = change.qa_round_id
    change.qa_approved_commit_sha = change.qa_commit_sha
    change.qa_approved_at = approved_at
    approval = WorkflowApproval(
        scope=ApprovalScope.change,
        gate="QA",
        state=ApprovalState.approved,
        change_pk=change.id,
        work_item_id=None,
        actor=actor.email,
        note=(
            f"round={change.qa_round_id}; commit={change.qa_commit_sha}; "
            f"approved_at={approved_at.isoformat()}; evidence={(note or '').strip()}"
        ),
    )
    db.add(approval)
    return approval


def _validate_qa_done_gate(db: Session, change: Change, repo_root: Path) -> None:
    current_sha = _current_repo_sha(repo_root)
    if not (
        change.qa_round_id
        and change.qa_commit_sha
        and change.qa_approved_round_id == change.qa_round_id
        and change.qa_approved_commit_sha == change.qa_commit_sha
        and current_sha == change.qa_commit_sha
    ):
        raise HTTPException(
            status_code=409,
            detail={
                "code": "qa_gate_not_approved",
                "message": "The active QA round and commit must have trusted approval before Done.",
                "qa_round_id": change.qa_round_id,
                "qa_commit_sha": change.qa_commit_sha,
                "current_commit_sha": current_sha,
            },
        )
    blocking_bugs = (
        db.query(WorkItem)
        .filter(
            WorkItem.change_pk == change.id,
            WorkItem.type == WorkItemType.bug,
            WorkItem.state.notin_([WorkItemState.done, WorkItemState.canceled]),
        )
        .all()
    )
    if blocking_bugs:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "blocking_child_bugs",
                "message": f"Cannot move to Done while {len(blocking_bugs)} bug(s) remain open.",
                "blocking_bugs": [bug.title for bug in blocking_bugs[:10]],
            },
        )


def transition_change(
    db: Session,
    *,
    change: Change,
    target_status: str,
    actor: "WorkflowActor",
    repo_root: Path,
    design_approver_emails: set[str],
    homologation_approver_emails: set[str] | None = None,
    release_approver_emails: set[str] | None = None,
) -> TransitionResult:
    current, target = validate_kanban_transition(
        current_column=change.status, target_column=target_status
    )
    if current == target:
        return TransitionResult(previous_status=current, status=target)

    if current in {
        "Pronto para Dev",
        "Em desenvolvimento",
        "Code Review",
        "QA",
    } and target != "Cancelado":
        try:
            _require_current_design_approval(
                change,
                repo_root,
                regress_on_obsolete=True,
            )
        except HTTPException:
            if current == "QA":
                invalidate_qa_round(
                    db,
                    change,
                    actor=actor.email,
                    reason="design approval became obsolete",
                )
            raise

    if current == "Todo" and target == "Pronto para Dev":
        if change.ui_impact != "none" or not (change.ui_impact_justification or "").strip():
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "ui_bypass_requires_justification",
                    "message": "Non-UI bypass requires UI impact none and a non-empty justification.",
                    "current": current,
                    "target": target,
                },
            )

    if current == "Design" and target == "Aprovação de Design":
        if change.ui_impact != "affected":
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "ui_impact_required",
                    "message": "Design delivery requires ui_impact=affected.",
                },
            )
        refresh_design_evidence(change, repo_root, record_delivery=True)

    approval_created = False
    if current == "Aprovação de Design" and target == "Pronto para Dev":
        normalized_email = actor.email.strip().lower()
        if normalized_email not in design_approver_emails:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "design_approver_required",
                    "message": "Only a configured design approver can approve this delivery.",
                },
            )
        design_digest, prototype_digest = refresh_design_evidence(change, repo_root)
        approved_at = datetime.now(timezone.utc)
        change.design_approved_by_user_id = actor.user_id
        change.design_approved_by = actor.email
        change.design_approved_at = approved_at
        change.approved_design_digest = design_digest
        change.approved_prototype_digest = prototype_digest
        change.design_approval_valid = True
        db.add(
            WorkflowApproval(
                scope=ApprovalScope.change,
                gate="Design Approval",
                state=ApprovalState.approved,
                change_pk=change.id,
                work_item_id=None,
                actor=actor.email,
                note=(
                    f"design_digest={design_digest}; "
                    f"prototype_digest={prototype_digest}; approved_at={approved_at.isoformat()}"
                ),
            )
        )
        approval_created = True

    if current == "Code Review" and target == "QA":
        start_qa_round(db, change, repo_root)

    if current == "QA" and target == "Em desenvolvimento":
        invalidate_qa_round(db, change, actor=actor.email, reason="QA rework")

    if current == "QA" and target == "Done":
        _validate_qa_done_gate(db, change, repo_root)

    if current == "Done" and target == "Homologado":
        allowed_homologators = homologation_approver_emails or design_approver_emails
        if actor.email.strip().lower() not in allowed_homologators:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "homologation_approver_required",
                    "message": "Only the configured human homologation approver can homologate this card.",
                },
            )
        db.add(
            WorkflowApproval(
                scope=ApprovalScope.change,
                gate="Homologation",
                state=ApprovalState.approved,
                change_pk=change.id,
                work_item_id=None,
                actor=actor.email,
                note=f"Homologated by authenticated user {actor.email}.",
            )
        )

    if current == "Homologado" and target == "Pronto":
        allowed_releasers = release_approver_emails or (
            homologation_approver_emails or design_approver_emails
        )
        if actor.email.strip().lower() not in allowed_releasers:
            raise HTTPException(
                status_code=403,
                detail={
                    "code": "release_approver_required",
                    "message": "Only Alan or a configured release approver can publish this card.",
                },
            )
        try:
            publication = require_card_main_publication(
                repo_root,
                change_id=change.change_id,
                card_number=change.card_number,
            )
        except UpstreamGuardError as exc:
            raise HTTPException(
                status_code=409,
                detail={
                    "code": "publication_not_verified",
                    "message": str(exc),
                    "target": target,
                },
            ) from exc
        change.publication_commit_sha = publication.head_sha
        db.add(
            WorkflowApproval(
                scope=ApprovalScope.change,
                gate="Publication",
                state=ApprovalState.approved,
                change_pk=change.id,
                work_item_id=None,
                actor=actor.email,
                note=(
                    f"Published in {publication.main_ref}; head={publication.head_sha}; "
                    f"main={publication.main_sha}."
                ),
            )
        )

    change.status = target
    return TransitionResult(
        previous_status=current,
        status=target,
        approval_created=approval_created,
    )


# Compatibility wrappers kept for internal callers while all decisions use the
# canonical service above.
def sync_change_gates_for_column(
    db: Session, *, change: Change, target_column: str, actor: str = "kanban"
) -> bool:
    current, target = validate_kanban_transition(
        current_column=change.status, target_column=target_column
    )
    if current == target:
        return False
    if (current, target) == ("Aprovação de Design", "Pronto para Dev"):
        raise HTTPException(
            status_code=409,
            detail={
                "code": "design_approval_requires_authenticated_transition",
                "message": "Use transition_change with a server-derived workflow actor.",
            },
        )
    change.status = target
    return True


def validate_transition_hooks(db: Session, change: Change, target_column: str) -> None:
    validate_kanban_transition(current_column=change.status, target_column=target_column)


def validate_work_item_transition(
    db: Session, work_item: WorkItem, target_state: WorkItemState
) -> None:
    if work_item.type != WorkItemType.story or target_state != WorkItemState.done:
        return
    open_bugs = (
        db.query(WorkItem)
        .filter(
            WorkItem.parent_id == work_item.id,
            WorkItem.type == WorkItemType.bug,
            WorkItem.state.notin_([WorkItemState.done, WorkItemState.canceled]),
        )
        .all()
    )
    if open_bugs:
        raise HTTPException(
            status_code=409,
            detail={
                "code": "blocking_child_bugs",
                "message": f"Cannot close story. {len(open_bugs)} child bug(s) are still open.",
                "story_id": work_item.id,
                "blocking_bugs": [item.id for item in open_bugs],
            },
        )

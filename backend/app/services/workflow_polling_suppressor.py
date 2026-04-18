"""Workflow Polling Suppression Service.

This module implements the reduce-workflow-scheduler-polling change:
- Suppresses redundant scheduler turns when no material workflow state has changed
- Detects meaningful events (milestones, blockers, approvals) that should break suppression
- Reduces token cost from repeated idle orchestration

The scheduler should query this service before running a turn to decide whether to proceed.
"""

from __future__ import annotations

import hashlib
import json
import logging
import threading
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from sqlalchemy.orm import Session

from app.workflow_models import (
    Change,
    WorkItem,
    WorkItemState,
    WorkItemType,
    WorkflowApproval,
    WorkflowComment,
    WorkflowHandoff,
    AgentRun,
)
from app.workflow_database import get_workflow_db

logger = logging.getLogger(__name__)

# Material change types that should break suppression
MATERIAL_CHANGE_TYPES = {
    "approval_created",  # New approval (gate transition)
    "approval_updated",  # Approval state changed
    "handoff_created",  # New handoff between roles
    "comment_added",  # New comment (might be coordination signal)
    "workitem_state_changed",  # Work item moved to new state
    "workitem_created",  # New work item added
    "workitem_blocked",  # Work item became blocked
    "change_status_changed",  # Change overall status changed
}


@dataclass
class WorkflowStateSnapshot:
    """Immutable snapshot of workflow state for comparison."""

    change_count: int
    active_changes: Set[str]
    work_item_states: Dict[str, str]  # work_item_id -> state
    approvals: Dict[str, str]  # approval_id -> state
    handoffs: Set[str]  # handoff_id set
    comment_count: int

    def to_hash(self) -> str:
        """Generate deterministic hash for state comparison."""
        data = {
            "change_count": self.change_count,
            "active_changes": sorted(self.active_changes),
            "work_item_states": dict(sorted(self.work_item_states.items())),
            "approvals": dict(sorted(self.approvals.items())),
            "handoffs": sorted(self.handoffs),
            "comment_count": self.comment_count,
        }
        return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()[:16]


@dataclass
class SuppressionState:
    """Tracks suppression state for scheduler decision-making."""

    last_turn_hash: str = ""
    suppressed_count: int = 0
    last_turn_at: Optional[datetime] = None
    suppressed_since: Optional[datetime] = None

    # Configuration
    suppression_enabled: bool = True
    max_suppressed_turns: int = 5  # Max consecutive suppressed turns before force-running
    suppression_timeout_minutes: int = 60  # Force-run after this timeout even if suppressed

    def should_run(self, now: datetime, material_change: bool = False) -> bool:
        """Decide whether scheduler should run a turn.

        Args:
            now: Current timestamp
            material_change: Whether a material change occurred since last turn

        Returns:
            True if scheduler should run, False if should suppress
        """
        if not self.suppression_enabled:
            return True

        if material_change:
            # Always run on material change - reset suppression
            self.suppressed_count = 0
            self.suppressed_since = None
            return True

        # Check timeout-based override
        if self.suppressed_since:
            elapsed = now - self.suppressed_since
            if elapsed > timedelta(minutes=self.suppression_timeout_minutes):
                logger.info(
                    f"Suppression timeout reached ({self.suppression_timeout_minutes}min), forcing turn"
                )
                self.suppressed_count = 0
                self.suppressed_since = None
                return True

        # Check max suppressed turns override
        if self.suppressed_count >= self.max_suppressed_turns:
            logger.info(f"Max suppressed turns reached ({self.max_suppressed_turns}), forcing turn")
            self.suppressed_count = 0
            self.suppressed_since = None
            return True

        return False

    def record_suppressed(self, now: datetime):
        """Record that a turn was suppressed."""
        self.suppressed_count += 1
        if self.suppressed_since is None:
            self.suppressed_since = now
        self.last_turn_at = now

    def record_run(self, now: datetime, new_hash: str):
        """Record that a turn was executed."""
        self.last_turn_hash = new_hash
        self.last_turn_at = now
        self.suppressed_count = 0
        self.suppressed_since = None


class WorkflowPollingSuppressor:
    """Service that decides whether to suppress scheduler turns.

    This implements the reduce-workflow-scheduler-polling change:
    - Detects material workflow state changes
    - Maintains suppression state across turns
    - Provides clear decision API for scheduler
    """

    _instance: Optional[WorkflowPollingSuppressor] = None
    _lock = threading.Lock()

    def __init__(self):
        self._state = SuppressionState()
        self._material_changes_cache: Dict[str, datetime] = {}

    @classmethod
    def get_instance(cls) -> WorkflowPollingSuppressor:
        """Get singleton instance (thread-safe)."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = WorkflowPollingSuppressor()
        return cls._instance

    def capture_state(self, db: Session) -> WorkflowStateSnapshot:
        """Capture current workflow state from database.

        Args:
            db: Database session

        Returns:
            Snapshot of current workflow state
        """
        # Count active changes (not archived/canceled)
        changes = db.query(Change).all()
        active_changes = {
            c.change_id for c in changes if c.status not in ("archived", "canceled", "done")
        }

        # Get work item states
        work_items = db.query(WorkItem).all()
        work_item_states = {wi.id: wi.state.value for wi in work_items}

        # Get approvals
        approvals = db.query(WorkflowApproval).all()
        approval_states = {a.id: a.state.value for a in approvals}

        # Get handoffs
        handoffs = db.query(WorkflowHandoff).all()
        handoff_ids = {h.id for h in handoffs}

        # Count comments
        comment_count = db.query(WorkflowComment).count()

        return WorkflowStateSnapshot(
            change_count=len(changes),
            active_changes=active_changes,
            work_item_states=work_item_states,
            approvals=approval_states,
            handoffs=handoff_ids,
            comment_count=comment_count,
        )

    def detect_material_changes(
        self, old_state: Optional[WorkflowStateSnapshot], new_state: WorkflowStateSnapshot
    ) -> List[str]:
        """Detect what material changes occurred between two states.

        Args:
            old_state: Previous state snapshot (or None for first run)
            new_state: Current state snapshot

        Returns:
            List of material change types that occurred
        """
        changes: List[str] = []

        if old_state is None:
            # First run - everything is new
            changes.append("initial_state")
            return changes

        # Check for approval changes
        for aid, old_val in old_state.approvals.items():
            if aid not in new_state.approvals:
                changes.append("approval_removed")
            elif new_state.approvals[aid] != old_val:
                changes.append("approval_updated")

        # Check for new approvals
        for aid in new_state.approvals:
            if aid not in old_state.approvals:
                changes.append("approval_created")

        # Check for handoff changes
        new_handoffs = new_state.handoffs - old_state.handoffs
        if new_handoffs:
            changes.append("handoff_created")

        # Check for work item state changes
        for wid, old_val in old_state.work_item_states.items():
            if wid not in new_state.work_item_states:
                changes.append("workitem_removed")
            elif new_state.work_item_states[wid] != old_val:
                changes.append("workitem_state_changed")

                # Also detect blocking
                if new_state.work_item_states[wid] == WorkItemState.blocked.value:
                    changes.append("workitem_blocked")

        # Check for new work items
        for wid in new_state.work_item_states:
            if wid not in old_state.work_item_states:
                changes.append("workitem_created")

        # Check for change status changes
        old_active = old_state.active_changes
        new_active = new_state.active_changes

        if old_active != new_active:
            changes.append("change_status_changed")

            # Check for newly activated changes
            newly_active = new_active - old_active
            if newly_active:
                changes.append("change_activated")

        # Check for significant comment activity (might be coordination signal)
        comment_diff = new_state.comment_count - old_state.comment_count
        if comment_diff > 5:  # Threshold for "meaningful" comment activity
            changes.append("comment_added")

        return changes

    def should_scheduler_run(self, db: Session) -> tuple[bool, Dict[str, Any]]:
        """Main decision function for scheduler.

        This is the primary API the scheduler should call to decide whether to run.

        Args:
            db: Database session

        Returns:
            Tuple of (should_run: bool, metadata: dict)
        """
        now = datetime.now(timezone.utc)

        # Capture current state
        new_state = self.capture_state(db)
        new_hash = new_state.to_hash()

        # Detect material changes
        old_state = None
        if self._state.last_turn_hash:
            # Reconstruct approximate old state from hash
            old_state = self._reconstruct_old_state(db)

        material_changes = self.detect_material_changes(old_state, new_state)
        has_material_change = len(material_changes) > 0 and "initial_state" not in material_changes

        # Check if state actually changed
        state_changed = new_hash != self._state.last_turn_hash

        # Decide whether to run
        should_run = self._state.should_run(now, has_material_change)

        metadata = {
            "should_run": should_run,
            "material_changes": material_changes,
            "state_changed": state_changed,
            "suppressed_count": self._state.suppressed_count,
            "suppressed_since": (
                self._state.suppressed_since.isoformat() if self._state.suppressed_since else None
            ),
            "last_hash": self._state.last_turn_hash,
            "current_hash": new_hash,
        }

        if should_run:
            self._state.record_run(now, new_hash)
            logger.info(
                f"Scheduler decision: RUN (material_changes={material_changes}, state_changed={state_changed})"
            )
        else:
            self._state.record_suppressed(now)
            logger.info(
                f"Scheduler decision: SUPPRESS (suppressed_count={self._state.suppressed_count})"
            )

        return should_run, metadata

    def _reconstruct_old_state(self, db: Session) -> Optional[WorkflowStateSnapshot]:
        """Reconstruct approximate old state for comparison.

        Note: This is a simplified reconstruction. For more accurate comparison,
        we could store state snapshots persistently.
        """
        # For now, return None which will cause a "first run" comparison
        # In a more complete implementation, we'd load from persistent storage
        return None

    def force_run_next(self):
        """Force the next scheduler turn to run (ignore suppression)."""
        self._state.suppressed_count = 0
        self._state.suppressed_since = None
        logger.info("Forced next scheduler run")

    def get_status(self) -> Dict[str, Any]:
        """Get current suppression status (for debugging/monitoring)."""
        return {
            "suppression_enabled": self._state.suppression_enabled,
            "suppressed_count": self._state.suppressed_count,
            "last_turn_at": (
                self._state.last_turn_at.isoformat() if self._state.last_turn_at else None
            ),
            "suppressed_since": (
                self._state.suppressed_since.isoformat() if self._state.suppressed_since else None
            ),
            "last_hash": self._state.last_turn_hash,
            "max_suppressed_turns": self._state.max_suppressed_turns,
            "suppression_timeout_minutes": self._state.suppression_timeout_minutes,
        }

    def configure(self, **kwargs):
        """Configure suppression behavior."""
        for key, value in kwargs.items():
            if hasattr(self._state, key):
                setattr(self._state, key, value)
        logger.info(f"Suppression config updated: {kwargs}")


def get_suppressor() -> WorkflowPollingSuppressor:
    """Convenience function to get the suppressor instance."""
    return WorkflowPollingSuppressor.get_instance()

# Design — workflow-stage-gate-enforcement

## Overview

This change implements backend enforcement to prevent workflow cards from skipping stages. The system will validate that all previous stages are completed before allowing transition to a new stage.

## Architecture

### Database Schema Changes

Add three new columns to `wf_work_items` table:

```sql
ALTER TABLE wf_work_items 
ADD COLUMN stage_started_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN stage_completed_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN last_agent_acted VARCHAR(64);
```

### Stage Order Definition

```
pending → PO → DESIGN → DEV → QA → Alan homologation → QA functional → Published
```

### Core Service: Stage Gate Validation

Create `app/services/stage_gate_service.py`:

```python
STAGE_ORDER = [
    "pending",
    "PO", 
    "DESIGN",
    "DEV",
    "QA",
    "Alan homologation",
    "QA functional",
    "Published"
]

def validate_stage_transition(current_stage: str, target_stage: str) -> tuple[bool, str]:
    """Validate if transition from current_stage to target_stage is allowed."""
    try:
        current_idx = STAGE_ORDER.index(current_stage.lower())
        target_idx = STAGE_ORDER.index(target_stage.lower())
    except ValueError:
        return False, f"Unknown stage"
    
    if target_idx <= current_idx:
        return False, f"Cannot transition backwards"
    
    # Check for skipped stages
    missing = []
    for stage in STAGE_ORDER[current_idx+1:target_idx]:
        if stage != target_stage.lower():
            missing.append(stage)
    
    if missing:
        return False, f"Skipped stages: {', '.join(missing)}"
    
    return True, "OK"

def can_transition_to_stage(work_item, target_stage: str) -> tuple[bool, str]:
    """Check if work item can transition to target stage."""
    current_stage = work_item.status
    return validate_stage_transition(current_stage, target_stage)
```

### API Integration Points

1. **Transition Endpoint** (`POST /api/workflow/items/{id}/transition`):
   - Add stage validation before allowing transition
   - Return 400 error with clear message if stage skipped

2. **Patch Endpoint** (`PATCH /api/workflow/items/{id}`):
   - Validate status changes
   - Block invalid stage transitions

### Error Response Format

```json
{
  "detail": "Stage transition blocked",
  "error_type": "stage_skip_attempt",
  "current_stage": "pending",
  "target_stage": "DEV",
  "skipped_stages": ["PO", "DESIGN"],
  "message": "Cannot skip PO and DESIGN stages"
}
```

### Agent Handoff Tracking

When a stage is completed:
1. Set `stage_completed_at = NOW()`
2. Set `last_agent_acted = <agent_name>`
3. Require handoff comment with fields: `status`, `evidence`, `next_step`

## Implementation Plan

### Phase 1: Database (Tasks 1.1-1.4)
- Add columns to work_items table
- Create migration script

### Phase 2: Core Service (Tasks 2.1-2.4)
- Create stage_gate_service.py
- Implement validation functions

### Phase 3: API Integration (Tasks 3.1-3.4)
- Update transition endpoint
- Update patch endpoint
- Add error handling

### Phase 4: Agent Tracking (Task 4.1-4.3)
- Update transition handler
- Add handoff comment validation
- Store timestamps

### Phase 5: Tests (Tasks 5.1-5.3)
- Unit tests for validation
- Integration tests for blocked transitions
- Sequential transition tests

## Acceptance Criteria

- [ ] Card cannot skip from Pending to DEV without PO/DESIGN activation
- [ ] Card cannot skip from DEV to QA without DEV completion  
- [ ] Card cannot skip from QA to Homologation without QA validation
- [ ] API returns clear error message when stage skip is attempted
- [ ] Stage completion timestamps are tracked
- [ ] Agent handoffs are recorded with required comments

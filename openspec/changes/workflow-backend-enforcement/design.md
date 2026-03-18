# Design: Workflow Backend Enforcement

## Architecture

### New Files
- `app/services/workflow_validation_service.py` - Core validation logic
- `app/routes/workflow_validation.py` - API endpoints
- Modify `app/services/workflow_transition_service.py` - Add validation hooks

### Data Models
- Add `ValidationError` exception class
- Reuse existing `WorkflowComment`, `WorkItem`, `Change` models

## Implementation Details

### R1: Approval Gate Validation
```python
async def validate_approval_gate(change_id: str, approval_type: str) -> list[str]:
    """Return list of missing required links."""
    # Check change artifacts exist
    # Return missing paths
```

### R2: Story-Bug Closure
```python
async def validate_story_closure(story_id: str, db: Session) -> bool:
    """Return True if story can be closed."""
    # Query all child bugs
    # Return False if any bug.state not in [done, canceled]
```

### R3: Handoff Comment
```python
def validate_handoff_comment(comment: str) -> bool:
    """Validate comment has required fields."""
    required = ['status:', 'evidence:', 'next_step:']
    return all(field in comment.lower() for field in required)
```

### R4: Sync Verification
- Compare `wf_changes.status` with `openspec/changes/{change_id}/meta.yaml`
- Compare `wf_work_items` with `openspec/changes/{change_id}/tasks.md`

## Testing
- Add integration tests for each validation rule
- Mock external calls to OpenSpec file system

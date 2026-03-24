# Tasks — workflow-stage-gate-enforcement

## 1. Backend Schema Updates

- [ ] 1.1 Add `stage_started_at` timestamp field to work_items table
- [ ] 1.2 Add `stage_completed_at` timestamp field to work_items table  
- [ ] 1.3 Add `last_agent_acted` VARCHAR field to work_items table
- [ ] 1.4 Create migration for new fields

## 2. Stage Gate Validation Service

- [ ] 2.1 Create `app/services/stage_gate_service.py`
- [ ] 2.2 Implement `validate_stage_transition(current_stage, target_stage)` function
- [ ] 2.3 Define stage order: pending → po → design → dev → qa → homologation → archived
- [ ] 2.4 Implement `can_transition_to_stage(work_item_id, target_stage)` function

## 3. API Integration

- [ ] 3.1 Add stage validation to `POST /api/workflow/items/{id}/transition`
- [ ] 3.2 Add validation to `PATCH /api/workflow/items/{id}`
- [ ] 3.3 Return 400 with clear error message on stage skip attempt
- [ ] 3.4 Include "skipped_stage" in error response

## 4. Agent Handoff Tracking

- [ ] 4.1 Update transition handler to set `last_agent_acted` on stage completion
- [ ] 4.2 Require handoff comment with "status", "evidence", "next_step" fields
- [ ] 4.3 Store stage completion timestamp

## 5. Tests

- [ ] 5.1 Write unit tests for stage gate validation
- [ ] 5.2 Write integration tests for blocked stage skips
- [ ] 5.3 Write tests for valid sequential transitions

## 6. Documentation

- [ ] 6.1 Update workflow documentation with stage gate rules
- [ ] 6.2 Document API error responses for stage validation

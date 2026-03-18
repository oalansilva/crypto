## 1. Validation Service Foundation

- [ ] 1.1 Create `app/services/workflow_validation_service.py`
- [ ] 1.2 Add `ValidationError` exception class
- [ ] 1.3 Add validation hooks to `workflow_transition_service.py`

## 2. Approval Gate Validation

- [ ] 2.1 Implement `validate_approval_gate()` function
- [ ] 2.2 Check for proposal.md existence
- [ ] 2.3 Check for review-ptbr.md existence (PO approval)
- [ ] 2.4 Check for tasks.md existence
- [ ] 2.5 Integrate with approval endpoint

## 3. Story-Bug Closure Validation

- [ ] 3.1 Implement `validate_story_closure()` function
- [ ] 3.2 Query child bugs for a story
- [ ] 3.3 Check bug states before story closure
- [ ] 3.4 Integrate with work item transition

## 4. Handoff Comment Validation

- [ ] 4.1 Implement `validate_handoff_comment()` function
- [ ] 4.2 Require status, evidence, next_step fields
- [ ] 4.3 Integrate with comment creation endpoint

## 5. Sync Verification Endpoint

- [ ] 5.1 Create GET `/api/workflow/verify-sync/{change_id}`
- [ ] 5.2 Compare DB status with OpenSpec meta.yaml
- [ ] 5.3 Compare work items with tasks.md
- [ ] 5.4 Return discrepancies list

## 6. Auto-Update DB on Homologation

- [ ] 6.1 Add webhook handler for Alan approval
- [ ] 6.2 Auto-update change status to homologated
- [ ] 6.3 Trigger archive workflow after approval

## 7. Sequence Enforcement

- [ ] 7.1 Add DEV→QA transition validation
- [ ] 7.2 Add QA→Homologation validation  
- [ ] 7.3 Add Homologation→Archived validation
- [ ] 7.4 Return clear error messages for blocked transitions

## 8. Testing

- [ ] 8.1 Add integration tests for approval validation
- [ ] 8.2 Add integration tests for story-bug closure
- [ ] 8.3 Add integration tests for comment validation
- [ ] 8.4 Add integration tests for sync verification
- [ ] 8.5 Run all tests and fix failures

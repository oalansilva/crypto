## ADDED Requirements

### Requirement: Functional QA result MUST be distinguished from publish/runtime readiness
The workflow runtime MUST distinguish a functionally validated change from a change that is fully ready to move to Alan homologation.

#### Scenario: QA is functionally green but publish is still pending
- **WHEN** QA confirms the feature behavior is correct
- **AND** publish/reconcile requirements are still pending or blocked
- **THEN** the workflow MUST preserve that QA functional result explicitly
- **AND** MUST report the missing publish/reconcile step without implying Alan homologation readiness

### Requirement: Runtime-affecting changes MUST include live reconciliation before QA handoff completion
For changes that affect runtime, API, or UI behavior, the workflow MUST require a live reconciliation/smoke step before the DEV handoff is considered operationally complete.

#### Scenario: Runtime stale after local success
- **WHEN** local tests pass but the live runtime still serves stale behavior
- **THEN** the workflow MUST treat the DEV handoff as incomplete
- **AND** MUST direct the next step to reconcile/restart/publish the runtime before final QA advancement

### Requirement: Homologation readiness announcements MUST require full consistency
A change MUST only be announced as ready for Alan homologation after functional QA, publish/reconcile status, and runtime stage status are all aligned.

#### Scenario: Avoid premature homologation signal
- **WHEN** one of QA functional result, publish/reconcile state, or runtime stage transition is still incomplete
- **THEN** the workflow MUST NOT announce the change as ready for Alan homologation
- **AND** MUST instead state exactly which alignment step is missing

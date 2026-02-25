# Spec: Lab Run Manual Upstream Approval

**Capability:** lab-run-upstream  
**Change:** auto-upstream-completion

## ADDED Requirements

### Requirement: Continue Conversation After Draft

**Description:** The system SHALL allow the user to continue the conversation with the Trader even after `ready_for_user_review: true`, enabling iterative refinement of the strategy draft before final approval.

#### Scenario: User requests adjustment after draft is generated

**Given** a Lab run where Trader has set `ready_for_user_review: true`  
**And** a `strategy_draft` has been generated  
**And** the "Approve Upstream" button is visible  
**When** the user sends a new message to the Trader (e.g., "ajusta o RSI pra 35/65")  
**Then** the system SHALL process the message as a normal upstream message  
**And** the Trader SHALL respond with an updated draft or clarification  
**And** the "Approve Upstream" button SHALL remain visible (user can approve later)  
**And** `ready_for_user_review` MAY remain `true` or be updated by the Trader

#### Scenario: Multiple iterations before approval

**Given** the user is in an upstream conversation  
**When** the user sends multiple refinement messages (e.g., "adiciona ATR", "muda stop pra 2%")  
**Then** each message SHALL be processed by the Trader  
**And** the `strategy_draft` SHALL be updated incrementally  
**And** the user can approve at any point when satisfied

---

### Requirement: Manual Upstream Approval Button

**Description:** The system SHALL display an "Approve Upstream" button in the UI when the Trader persona has marked `ready_for_user_review: true` and the user has not yet approved (`user_approved: false`).

#### Scenario: Button appears when strategy draft is ready

**Given** a Lab run in the `upstream` phase  
**And** the Trader persona has set `ready_for_user_review: true`  
**And** the upstream contract has `approved: true`  
**And** `upstream.user_approved` is `false`  
**When** the user views the run detail page  
**Then** the system SHALL display an "Approve Upstream" button  
**And** the button SHALL be enabled and clickable  
**And** the `strategy_draft` content SHALL be visible above the button

#### Scenario: Button does not appear when already approved

**Given** a Lab run where `upstream.user_approved` is already `true`  
**When** the user views the run detail page  
**Then** the system SHALL NOT display the "Approve Upstream" button  
**And** SHALL display a message indicating upstream was approved

### Requirement: Upstream Approval Endpoint

**Description:** The system MUST provide a REST endpoint to process manual upstream approval from the user.

#### Scenario: User clicks approve button

**Given** a Lab run with `ready_for_user_review: true` and `user_approved: false`  
**When** the user clicks the "Approve Upstream" button  
**Then** the frontend SHALL send a POST request to `/api/lab/runs/{run_id}/upstream/approve`  
**And** the backend SHALL set `upstream.user_approved = true`  
**And** SHALL emit an `upstream_approved` event with the validated inputs  
**And** SHALL return the updated run with `status: ready_for_execution`  
**And** the button SHALL be disabled during the request (loading state)

#### Scenario: Prevent duplicate approval

**Given** a Lab run where `user_approved` is already `true`  
**When** a POST request is sent to `/upstream/approve`  
**Then** the backend SHALL return HTTP 400 with error "Already approved"  
**And** SHALL NOT re-emit the `upstream_approved` event

### Requirement: Upstream Approved Event Emission

**Description:** The system MUST emit an `upstream_approved` event containing the finalized inputs when the user manually approves the upstream.

#### Scenario: Emit event with correct inputs

**Given** the user is approving the upstream  
**When** the backend processes the `/upstream/approve` request  
**Then** the system SHALL emit an event with type `upstream_approved`  
**And** the event payload SHALL include the `inputs` dict from `upstream_contract`  
**And** the event timestamp SHALL be recorded in UTC milliseconds

### Requirement: Persona Execution Trigger After Approval

**Description:** The system SHALL automatically trigger the decision phase (coordinator → dev → validator → trader personas) when a run transitions to `ready_for_execution` status after manual approval.

#### Scenario: Trigger personas after manual approval

**Given** a Lab run that just transitioned to `ready_for_execution` via manual approval  
**When** the next API request polls the run state (e.g., GET `/api/lab/runs/{run_id}`)  
**Then** the system SHALL initiate the persona execution sequence  
**And** SHALL update the run phase to `decision`  
**And** SHALL start with the `coordinator` persona  
**And** SHALL log a `persona_started` event with `persona: coordinator`

## MODIFIED Requirements

### Requirement: Status Transition Logic

**Description:** The system SHALL determine run status based on manual user approval state, NOT automatically when `ready_for_user_review: true`.

#### Scenario: Status remains ready_for_review until manual approval

**Given** `upstream_contract.approved: true`  
**And** `upstream.ready_for_user_review: true`  
**And** `upstream.user_approved: false`  
**When** calculating the run status  
**Then** the system SHALL return `ready_for_review` (waiting for user action)  
**And** SHALL NOT automatically progress to `ready_for_execution`

#### Scenario: Status changes after manual approval

**Given** `upstream_contract.approved: true`  
**And** `upstream.ready_for_user_review: true`  
**And** `upstream.user_approved: true`  
**When** calculating the run status  
**Then** the system SHALL return `ready_for_execution`  
**And** SHALL trigger persona execution on next poll

## REMOVED Requirements

None.

## Constraints

- **Manual approval only:** No automatic approval logic — user MUST explicitly click the button
- **UI dependency:** Requires frontend implementation (button + API integration)
- **Backward compatibility:** Existing runs in `ready_for_review` state must show the approval button retroactively
- **Event ordering:** `upstream_approved` event MUST be emitted BEFORE status changes to `ready_for_execution`
- **Idempotency:** Approval endpoint must be idempotent (reject duplicate approvals with clear error)

## Acceptance Criteria

1. **UI:** "Approve Upstream" button appears when `ready_for_user_review: true` and `user_approved: false`
2. **API:** POST `/upstream/approve` successfully marks `user_approved: true` and emits event
3. **Progression:** Run transitions from `ready_for_review` → `ready_for_execution` after approval
4. **Personas:** Coordinator persona starts within 2 seconds of approval
5. **Idempotency:** Clicking "Approve" multiple times does not cause duplicate events or errors
6. **Retroactive:** Old runs stuck in `ready_for_review` can be approved via the new button

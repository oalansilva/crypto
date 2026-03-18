# Workflow Validation Service

## Purpose
Backend service to enforce workflow rules programmatically, preventing runtime violations defined in MEMORY.md and playbooks.

## ADDED Requirements

### Requirement: R1 - Approval Gate Validation
**Description:** Before accepting an approval (PO or Alan), the API SHALL validate that required review links exist.

#### Scenario: Approver sends approval without required links
- Given a change without proposal.md or review-ptbr.md
- When someone tries to approve via API
- Then API returns 400 with list of missing links

#### Scenario: Approver sends approval with all required links
- Given a change with all required artifacts
- When someone approves via API
- Then approval is accepted

### Requirement: R2 - Story-Bug Closure Rule
**Description:** When attempting to mark a story as done, the API SHALL validate all child bugs are done or canceled.

#### Scenario: Attempting to close story with active bugs
- Given a story with one or more child bugs in "active" state
- When someone tries to mark story as done
- Then API returns 400 blocking the transition

#### Scenario: Attempting to close story with all bugs resolved
- Given a story with all child bugs in "done" or "canceled" state
- When someone marks story as done
- Then transition succeeds

### Requirement: R3 - Handoff Comment Validation
**Description:** When transitioning a work item to a new stage, the API SHALL require a comment with status, evidence, and next_step.

#### Scenario: Transition without required comment fields
- Given a work item transition request
- When comment is missing status/evidence/next_step
- Then API returns 400

#### Scenario: Transition with valid comment
- Given a work item transition request
- When comment contains all required fields
- Then transition succeeds

### Requirement: R4 - Sync Verification Endpoint
**Description:** The system SHALL provide a GET endpoint to compare runtime DB state with OpenSpec artifacts.

#### Scenario: DB and OpenSpec are in sync
- Given a change with matching DB and file state
- When calling GET /api/workflow/verify-sync/{change_id}
- Then returns { "synced": true, "discrepancies": [] }

#### Scenario: DB and OpenSpec are out of sync
- Given a change with mismatched state
- When calling verify-sync endpoint
- Then returns { "synced": false, "discrepancies": [...] }

### Requirement: R5 - Auto-Update DB on Homologation
**Description:** When Alan approves via chat, the backend SHALL auto-update the workflow DB.

#### Scenario: Alan approves via chat
- Given Alan's approval message in chat
- When system processes the approval
- Then DB status updates to homologated automatically

### Requirement: R6 - DEV→QA→Publish Sequence
**Description:** The transition service SHALL enforce proper sequence: DEV → QA → Homologation → Archived.

#### Scenario: Trying to skip QA and go directly to homologation
- Given a change in DEV stage
- When someone tries to move to Homologation
- Then API returns 400 requiring QA validation first

#### Scenario: Valid transition from QA to Homologation
- Given QA validation is complete
- When moving to Homologation
- Then transition succeeds

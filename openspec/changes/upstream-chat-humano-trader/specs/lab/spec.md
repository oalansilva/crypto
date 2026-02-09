# Δ lab Specification — Upstream chat Humano↔Trader

## ADDED Requirements

### Requirement: Upstream MUST be a chat with Trader

When a Lab run is in `phase=upstream`, the system MUST support a conversational flow between the user and the **Trader** persona to clarify inputs/constraints and produce an `upstream_contract`.

The system MUST:
- Persist upstream chat history per run (messages with role + text + timestamp).
- Provide an API to append a user upstream message and receive an updated `upstream_contract` and (if not approved) the next Trader question.
- Only proceed to execution when `upstream_contract.approved == true` and the user confirms.

#### Scenario:

User starts a run with ambiguous constraints. The Trader asks clarifying questions; after the user answers, the contract becomes approved and the UI offers a CTA to start execution.

### Requirement: UI MUST rename validator to Trader

The UI MUST display the persona label **Trader** wherever it previously showed `validator`.

#### Scenario:

User views the upstream conversation and sees messages attributed to “Trader”, not “validator”.

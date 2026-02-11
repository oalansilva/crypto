# Spec: Trader Conversa Fluida (Backend)

**Capability:** backend  
**Type:** enhancement  
**Change:** trader-conversation-flow

---

## ADDED Requirements

### Requirement: Trader controls when draft is ready

**Description:** The system SHALL allow the Trader to decide when `ready_for_user_review=true`, regardless of whether symbol/timeframe is already provided.

#### Scenario: Trader keeps asking questions
- **Given** symbol/timeframe already provided
- **When** Trader still needs more context
- **Then** system MUST keep upstream in chat mode
- **And** MUST NOT force draft generation

---

### Requirement: Upstream chat remains open

**Description:** The system SHALL keep upstream conversation open until Trader signals readiness.

#### Scenario: Additional questions after contract approved
- **Given** contract is technically approved
- **When** Trader asks an additional question
- **Then** system MUST accept and persist that question
- **And** status remains `needs_user_input` until Trader sets ready_for_user_review

---

## MODIFIED Requirements

### Requirement: Draft gating logic

**Description:** The system SHALL only move to `ready_for_review` when Trader explicitly sets `ready_for_user_review=true`.

#### Scenario: Contract approved but draft not ready
- **Given** contract approved but no draft
- **When** upstream is updated
- **Then** status MUST remain `needs_user_input`
- **And** Trader can continue asking questions

---

### Requirement: UI prompt handling

**Description:** The system SHALL treat Trader follow-up questions as normal chat prompts, not as errors.

#### Scenario: Extra question
- **Given** Trader asks “qual risco máximo você aceita?”
- **When** user replies
- **Then** message is appended to upstream messages
- **And** upstream question updates normally

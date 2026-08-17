# hermes-agent-runtime Specification

## Purpose
Agent chat e runtime ativo usam Hermes HTTP; OpenClaw Gateway não é dependência viva.

## Requirements
### Requirement: Agent chat uses Hermes HTTP runtime
The backend SHALL send agent-chat turns to Hermes `POST /v1/responses` (default `http://127.0.0.1:8642`) with a 180s timeout, request idempotency, response sanitization, and optional authentication. The public `POST /api/agent/chat` contract SHALL remain: favorite context, `conversation_id`, `thinking` (off|minimal|low|medium|high mapped into Hermes), and non-empty reply. Errors SHALL use the existing `detail` JSON field the chat modal already displays. Runtime code SHALL NOT call OpenClaw Gateway WebSocket, `OPENCLAW_GATEWAY_*`, or port `18789`.

#### Scenario: Chat turn succeeds via Hermes
- **WHEN** agent chat is enabled and Hermes returns a non-empty response
- **THEN** `POST /api/agent/chat` returns that reply with a stable `conversation_id`
- **AND** the request `thinking` value is forwarded to Hermes
- **AND** no OpenClaw gateway WebSocket connection is opened

#### Scenario: Hermes timeout or empty reply
- **WHEN** Hermes times out or returns an empty/unsafe payload
- **THEN** the API returns a controlled error without leaking secrets
- **AND** it SHALL NOT fall back to OpenClaw

### Requirement: No active runtime depends on OpenClaw gateway
Active Cripto Farol runtime (API, workers, systemd templates used in DEV/PROD) SHALL NOT require `OPENCLAW_GATEWAY_URL`, `OPENCLAW_GATEWAY_TOKEN`, or port `18789`. OpenClaw MAY remain only as classified historical documentation.

#### Scenario: Runtime inventory has no gateway env
- **WHEN** an operator inspects active service templates and agent-chat code
- **THEN** none of them export or read `OPENCLAW_GATEWAY_*` as a live dependency


---
spec: openspec.v1
id: crypto.agent-chat.favorites
title: Agent chat for Favorite strategies (Favorites screen)
status: implemented
owner: Alan
created_at: 2026-02-04
updated_at: 2026-02-04
---

# 0) One-liner

Add an "agent chat" option on the Favorites screen so users can chat about a saved FavoriteStrategy, using Hermes `POST /v1/responses` (no new provider tokens in the product UI).

# 1) Context

- We have saved Favorite strategies with params + metrics.
- We want to ask natural-language questions about a specific favorite.
- Initial implementation using a CLI subprocess was unreliable (timeouts, empty replies). The stable solution is calling Hermes `POST /v1/responses`.

# 2) Goal

## In scope
- UI button on each favorite row to open a chat modal.
- Backend endpoint that builds a compact prompt with favorite JSON context.
- Run agent turns through Hermes HTTP (`POST /v1/responses`) and return reply text.
- Keep stable conversation per favorite via `conversation_id`.

## Out of scope
- Multi-tenant auth hardening.
- Persisting chat transcripts in DB.

# 3) User stories

- As a user, I want to ask "why did this strategy work?" and get hypotheses + next tests.
- As a user, I want conversation context to persist while the modal is open.

# 4) UX / UI

- Entry point: Favorites list → row action "Chat com o agente".
- Modal:
  - Message input + send
  - Busy indicator
  - Error display
  - Thinking selector (off|minimal|low|medium|high)

# 5) API / Contracts

## Backend endpoints

### POST /api/agent/chat
- Request:
  - favorite_id: int
  - message: string
  - conversation_id?: string (defaults to fav-<id>)
  - thinking?: string (default low)
- Response:
  - conversation_id: string
  - reply: string
  - model?: string
  - provider?: string
  - usage?: object
  - duration_ms?: int

## Security
- Single-tenant; endpoint gated by AGENT_CHAT_ENABLED.

# 6) Acceptance criteria (Definition of Done)

- [x] Favorites UI has an Agent chat option.
- [x] Backend returns non-empty replies reliably.
- [x] Uses Hermes HTTP `/v1/responses` (no CLI subprocess, no OpenClaw Gateway).

# 7) Test plan

## Automated
- `crypto/scripts/agent_chat_smoketest.sh`

## Manual smoke
1. Open /favorites
2. Click "Chat com o agente"
3. Ask: "Responda apenas com ok" → see "ok"

# 8) Implementation notes

- Backend uses `HERMES_API_BASE_URL` (default `http://127.0.0.1:8642`) and optional `HERMES_API_TOKEN` / `HERMES_API_KEY`.
- Hermes session key format: `agent:main:agentchat:<conversation_id>`
